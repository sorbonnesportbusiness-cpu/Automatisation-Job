#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fusionne les fichiers d'offres produits par plusieurs sous-agents en un seul
fichier de nouvelles offres, prêt pour site/publish.sh.

- supprime les doublons (même lien, ou même employeur + même intitulé) ;
- écarte les liens déjà au tableau (data/offres.json) ou déjà livrés (historique.md) ;
- applique le plafond d'offres par employeur, en comptant celles déjà au tableau ;
- fusionne les bilans.

Usage :
    python3 merge_lots.py out/lots/*.json --board data/offres.json \
        --history skills/veille-ssb/references/historique.md --cap 5 --out out/nouvelles-2026-10-08.json
"""

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


def key(text):
    text = unicodedata.normalize("NFD", text or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def employer(o):
    """Nom d'employeur comparable : sans parenthèses ni forme juridique."""
    return key(re.sub(r"\(.*?\)", "", o.get("entreprise", "")))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("lots", nargs="+", help="Fichiers JSON des sous-agents")
    p.add_argument("--board", required=True)
    p.add_argument("--history")
    p.add_argument("--cap", type=int, default=5)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    board = json.load(open(args.board, encoding="utf-8")) if Path(args.board).exists() else {"offres": []}
    seen_links = {o["lien"] for o in board["offres"]}
    if args.history and Path(args.history).exists():
        seen_links |= set(re.findall(r"https?://\S+", Path(args.history).read_text(encoding="utf-8")))
    seen_pairs = {(employer(o), key(o["titre"])) for o in board["offres"]}
    per_employer = Counter(employer(o) for o in board["offres"])

    offers, bilan, dropped = [], {"total_testees_ecartees": 0, "detail_ecartees": [], "portails_steriles": [], "nouveaux_portails": []}, []
    lots = []
    for f in args.lots:
        try:
            lots.append((f, json.load(open(f, encoding="utf-8"))))
        except Exception as exc:  # noqa: BLE001 - un lot cassé ne doit pas bloquer les autres
            print(f"Lot ignoré (JSON illisible) : {f} : {exc}")
    # Offres les plus récentes d'abord, pour que le plafond garde les plus fraîches.
    candidates = [o for _, lot in lots for o in lot.get("offres", [])]
    candidates.sort(key=lambda o: o.get("date_iso") or "", reverse=True)
    for o in candidates:
        if not o.get("lien") or not o.get("titre"):
            continue
        pair = (employer(o), key(o["titre"]))
        if o["lien"] in seen_links or pair in seen_pairs:
            dropped.append(f"Doublon : {o['titre']} - {o.get('entreprise')}")
            continue
        if per_employer[pair[0]] >= args.cap:
            dropped.append(f"Plafond de {args.cap} atteint : {o['titre']} - {o.get('entreprise')}")
            continue
        seen_links.add(o["lien"]); seen_pairs.add(pair); per_employer[pair[0]] += 1
        offers.append(o)
    for _, lot in lots:
        b = {"ecartees": lot.get("ecartees", []), "portails_steriles": lot.get("portails_steriles", []),
             "nouveaux_portails": lot.get("nouveaux_portails", [])}
        b.update(lot.get("bilan", {}))
        bilan["detail_ecartees"] += b.get("detail_ecartees", b["ecartees"])
        bilan["portails_steriles"] += b["portails_steriles"]
        bilan["nouveaux_portails"] += b["nouveaux_portails"]
    bilan["detail_ecartees"] += dropped
    bilan["total_testees_ecartees"] = len(bilan["detail_ecartees"])

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"offres": offers, "bilan": bilan}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(offers)} nouvelles offres retenues ({len(dropped)} doublons ou hors plafond) -> {args.out}")
    print("Par employeur :", ", ".join(f"{k} {v}" for k, v in Counter(o['entreprise'] for o in offers).most_common(8)))


if __name__ == "__main__":
    main()
