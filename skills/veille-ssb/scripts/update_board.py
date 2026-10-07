#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Met à jour le tableau en ligne des offres (data/offres.json) après une veille.

Le tableau garde les offres des veilles précédentes tant qu'elles sont ouvertes,
et y ajoute les nouvelles. À chaque passage :
  - une offre déjà au tableau est retirée si sa date de clôture est passée, si elle
    a été publiée il y a plus de --max-age jours, ou si son lien est mort (404/410
    ou page « offre expirée / plus disponible ») ;
  - les nouvelles offres sont ajoutées avec ajoutee_le = date de la veille ;
  - leurs liens sont ajoutés en tête de references/historique.md.

Usage :
    python3 update_board.py nouvelles.json --date 2026-10-12 \
        --board ../../../data/offres.json --history ../references/historique.md

nouvelles.json a le même format que l'entrée de build_outputs.py.
Le tableau écrit garde ce format (offres + bilan), il sert d'entrée aux scripts
build_outputs.py et build_page.py.
"""

import argparse
import concurrent.futures as cf
import datetime
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
CLOSED_MARKERS = (
    "n'est plus disponible", "n’est plus disponible", "offre expirée", "offre a expiré",
    "n'est plus en ligne", "n’est plus en ligne", "recrutement est fermé", "poste pourvu",
    "no longer accepting applications", "n'accepte plus de candidatures",
    "n’accepte plus de candidatures", "this job is no longer available",
)
CLOSING_RE = re.compile(r"(cl[ôo]ture|jusqu'au)\s*(?:le\s*)?(\d{2})/(\d{2})(?:/(\d{4}))?", re.I)


def closing_date(offer, year):
    m = CLOSING_RE.search(offer.get("infos") or offer.get("date_pub", ""))
    if not m:
        return None
    try:
        return datetime.date(int(m.group(4) or year), int(m.group(3)), int(m.group(2)))
    except ValueError:
        return None


def link_status(url):
    """'ok', 'mort' ou 'inconnu' (erreur réseau, 403, 429 : on garde l'offre)."""
    safe = urllib.parse.quote(url, safe=":/?=&%#~-_.()+,")
    req = urllib.request.Request(safe, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = resp.read(400_000).decode("utf-8", "ignore").lower()
    except urllib.error.HTTPError as exc:
        return "mort" if exc.code in (404, 410) else "inconnu"
    except Exception:  # noqa: BLE001 - réseau capricieux : ne pas retirer l'offre pour ça
        return "inconnu"
    return "mort" if any(m in visible_text(body) for m in CLOSED_MARKERS) else "ok"


def visible_text(html):
    """Texte affiché de la page : sans scripts, styles ni balises. Les messages d'erreur
    rangés dans les bundles JS (« l'offre n'est plus en ligne ») ne doivent pas compter."""
    html = re.sub(r"(?is)<(script|style|noscript|template)\b.*?</\1>", " ", html)
    return re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", html))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("nouvelles", help="JSON des offres trouvées par cette veille")
    p.add_argument("--date", required=True, help="Date de la veille AAAA-MM-JJ")
    p.add_argument("--board", required=True, help="Tableau des offres (créé s'il n'existe pas)")
    p.add_argument("--history", help="references/historique.md à compléter")
    p.add_argument("--max-age", type=int, default=60, help="Âge max d'une offre en jours (défaut 60)")
    p.add_argument("--no-check", action="store_true", help="Ne pas revérifier les liens existants")
    args = p.parse_args()

    run = datetime.date.fromisoformat(args.date)
    new = json.load(open(args.nouvelles, encoding="utf-8"))
    board_path = Path(args.board)
    board = json.load(open(board_path, encoding="utf-8")) if board_path.exists() else {"offres": []}

    new_offers = new.get("offres", [])
    new_links = {o["lien"] for o in new_offers}
    for o in new_offers:
        o.setdefault("ajoutee_le", args.date)

    kept, removed = [], []
    candidates = [o for o in board.get("offres", []) if o["lien"] not in new_links]
    to_check = []
    for o in candidates:
        close = closing_date(o, run.year)
        pub = o.get("date_iso")
        if close and close < run:
            removed.append((o, f"clôture passée ({close:%d/%m})"))
        elif pub and (run - datetime.date.fromisoformat(pub)).days > args.max_age:
            removed.append((o, f"publiée il y a plus de {args.max_age} jours"))
        else:
            to_check.append(o)

    if args.no_check:
        kept = to_check
    else:
        with cf.ThreadPoolExecutor(8) as ex:
            for o, status in zip(to_check, ex.map(lambda o: link_status(o["lien"]), to_check)):
                (removed.append((o, "lien mort ou offre fermée")) if status == "mort" else kept.append(o))

    offers = new_offers + kept
    offers.sort(key=lambda o: o.get("date_iso") or "", reverse=True)

    bilan = new.get("bilan", {})
    bilan.setdefault("detail_ecartees", [])
    bilan["detail_ecartees"] = [
        f"Retirée du tableau : {o['titre']} - {o['entreprise']} ({why})" for o, why in removed
    ] + bilan["detail_ecartees"]
    board = {"date_maj": args.date, "offres": offers, "bilan": bilan}
    board_path.parent.mkdir(parents=True, exist_ok=True)
    board_path.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.history and new_offers:
        hist = Path(args.history)
        text = hist.read_text(encoding="utf-8") if hist.exists() else "# Historique des offres livrées\n"
        block = [f"## Veille du {args.date} ({len(new_offers)} offres)", ""] + [
            f"- {o.get('date_iso') or 'n.c.'} | {o['contrat']} | {o['entreprise']} | {o['titre']} | {o['lien']}"
            for o in new_offers
        ]
        marker = text.find("\n## ")
        text = (text + "\n" + "\n".join(block) + "\n") if marker < 0 else (
            text[:marker + 1] + "\n".join(block) + "\n\n" + text[marker + 1:])
        hist.write_text(text, encoding="utf-8")

    print(f"Tableau : {len(offers)} offres ({len(new_offers)} nouvelles, {len(kept)} conservées, {len(removed)} retirées)")
    for o, why in removed:
        print(f"  retirée : {o['entreprise']} | {o['titre']} | {why}")


if __name__ == "__main__":
    main()
