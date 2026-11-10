#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bibliothèque de logos des employeurs, pour le visuel Insta de la page des offres.

Pour chaque employeur du tableau qui n'a pas encore de logo (references/logos.json), cherche
un logo, dans cet ordre :
  1. Wikimedia Commons : recherche dans les fichiers « <nom> logo », SVG de préférence ;
  2. Wikipédia en anglais, puis en français : page de l'employeur, image dont le nom contient
     « logo » (les anciens logos en dernier) ;
  3. le site de l'employeur (domaine d'un lien d'offre qui n'est pas un ATS ni un agrégateur) :
     première image de la page d'accueil marquée « logo ».
Le fichier va dans site/static/logos/, la table est mise à jour. Un logo introuvable n'est pas
bloquant : il est noté dans « introuvables » et réessayé après 30 jours. Les logos clairs
(faits pour un fond sombre) sont recolorés par la page au moment du dessin.

La page cherche un employeur avec les mêmes variantes de nom que variantes() (visuel-insta
dans build_page.py) : nom complet, contenu des parenthèses, nom sans parenthèses, sans
« groupe », « France »..., puis ses premiers mots.

Usage :
    python3 logos.py --board data/offres.json --table references/logos.json --dir site/static/logos
"""

import argparse
import datetime as dt
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

UA = "SSB-veille-logos/1.0 (https://veille.sorbonnesportbusiness.com; Sorbonne Sport Business)"
STOP = {"groupe", "group", "sa", "sas", "france", "fr", "the", "inc", "ltd", "gmbh", "se", "holding"}
FAIBLES = {"de", "du", "des", "la", "le", "les", "et", "of", "and", "the", "l", "d", "club", "sport",
           "sports", "group", "groupe", "france", "fc", "sa", "sas"}
PAS_EMPLOYEUR = re.compile(
    r"linkedin|hellowork|indeed|welcometothejungle|jobteaser|myworkday|smartrecruiters|teamtailor|"
    r"greenhouse|lever\.co|breezy|jobylon|pinpoint|taleez|flatchr|digitalrecruiters|successfactors|"
    r"talent-soft|join\.com|recruitee|personio|workable|ashby|softy|globalsportsjobs|sportstrategies|"
    r"wizbii|meteojob|talent\.com|labonnealternance|choisirleservicepublic|emploi-territorial|"
    r"village-justice|lawprofiler|jobs\.|careers\.|recrutement\.|carrieres\.|emploi\.|career", re.I)
MAX_RECHERCHES = 15        # nouveaux employeurs par passage, pour garder la publication rapide
RETRY_DAYS = 30


def cle(texte):
    t = unicodedata.normalize("NFD", texte or "").encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", t).split())


def variantes(nom):
    """Noms normalisés à essayer, du plus précis au plus large."""
    entre = re.findall(r"\(([^)]*)\)", nom or "")
    base = [cle(nom), *[cle(x) for x in entre], cle(re.sub(r"\([^)]*\)", " ", nom or ""))]
    out = []
    for v in base:
        for w in (v, " ".join(x for x in v.split() if x not in STOP)):
            if w and w not in out:
                out.append(w)
    for v in list(out):
        mots = v.split()
        for k in range(len(mots) - 1, 0, -1):
            p = " ".join(mots[:k])
            if (k > 1 or len(mots[0]) >= 4) and p not in out and p not in STOP:
                out.append(p)
    return out


def trouve(table, nom):
    for v in variantes(nom):
        if v in table["logos"]:
            return v
        if v in table["alias"]:
            return table["alias"][v]
    return None


# --- Recherche ------------------------------------------------------------------------

def get(url, timeout=20, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read(4_000_000)
        return (data, r.headers.get("Content-Type", "")) if binary else data.decode("utf-8", "replace")


def api(host, **params):
    params.update(format="json", formatversion="2")
    return json.loads(get(f"https://{host}/w/api.php?" + urllib.parse.urlencode(params)))


def mots_forts(nom):
    return [w for w in cle(nom).split() if w not in FAIBLES and len(w) >= 2]


def colle(titre_fichier, nom):
    """Le titre du fichier ou de la page reprend tous les mots forts du nom. Seul un sigle formé
    des initiales du nom peut manquer (« LFP - Ligue de Football Professionnel » / « Ligue de
    Football Professionnel logo »)."""
    t = cle(titre_fichier)
    forts = mots_forts(nom)
    initiales = "".join(w[0] for w in cle(nom).split() if w not in {"de", "du", "des", "la", "le", "les", "l", "d", "et"})
    if len(forts) == 1:   # « Paris FC » : « paris » seul désignerait la ville
        forts = [w for w in cle(nom).split() if w not in {"de", "du", "des", "la", "le", "les", "l", "d", "et"}]
    manquants = [w for w in forts if not re.search(rf"\b{re.escape(w)}\b", t)]
    if not forts or len(manquants) == len(forts) or not all(len(w) >= 2 and w in initiales for w in manquants):
        return False
    if len(forts) - len(manquants) <= 1:
        # Un seul mot en commun (« CIO », « Boost », « Wimbledon ») : le titre ne doit rien dire
        # d'autre, sinon c'est un homonyme (« CIO (company) logo », « Boost Mobile USA logo »).
        neutres = {"file", "fichier", "logo", "logotype", "svg", "png", "jpg", "gif", "webp", "text", "wordmark",
                   "official", "new", "of", "the", "de", "du", "la", "le", "l", "d"}
        autres = [w for w in t.split() if w not in neutres and w not in cle(nom).split()
                  and not re.fullmatch(r"(19|20)\d\d", w)]
        return not autres
    return True


def noms_a_chercher(nom):
    """Nom sans parenthèses, puis le contenu des parenthèses (« CNOSF (Comité National Olympique...) »)."""
    out = [re.sub(r"\s+", " ", re.sub(r"\([^)]*\)", " ", nom)).strip(" -")]
    out += [x.strip() for x in re.findall(r"\(([^)]*)\)", nom) if len(x.strip()) > 3]
    return [x for x in out if x]


# Ancien logo (« (1990-2024) », « old », « former ») : en dernier recours seulement.
ANCIEN = re.compile(r"\b(19|20)\d\d\s*[-–]\s*(19|20)\d\d\b|\b19\d\d\b|\bold\b|former|ancien|historique|provisoire", re.I)
# Icônes de Wikipédia, jamais le logo de l'employeur.
ICONE = re.compile(r"disambig|commons-logo|wiki|question_book|edit-clear|symbol|flag|icon", re.I)


def ordre(titre, nom):
    return (bool(ANCIEN.search(titre)), not titre.lower().endswith(".svg"), not colle(titre, nom), len(titre))


def info_fichier(host, titre):
    pages = api(host, action="query", titles=titre, prop="imageinfo", iiprop="url|mime|size",
                iiurlwidth=800)["query"]["pages"]
    ii = (pages[0].get("imageinfo") or [None])[0]
    if not ii:
        return None
    if ii.get("mime") == "image/svg+xml":
        return ii["url"], "svg"
    return ii.get("thumburl") or ii["url"], "png"


def commons(nom):
    for n in noms_a_chercher(nom):
        res = api("commons.wikimedia.org", action="query", list="search", srnamespace=6,
                  srsearch=f"{n} logo", srlimit=15)["query"]["search"]
        titres = [r["title"] for r in res if "logo" in r["title"].lower() and not ICONE.search(r["title"])
                  and colle(r["title"], n)]
        titres.sort(key=lambda t: ordre(t, n))
        for t in titres[:3]:
            info = info_fichier("commons.wikimedia.org", t)
            if info:
                return (*info, f"Wikimedia Commons, {t}")
    return None


def wikipedia(nom, host="en.wikipedia.org", libelle="Wikipédia en anglais"):
    for n in noms_a_chercher(nom):
        res = api(host, action="query", list="search", srsearch=n, srlimit=3)["query"]["search"]
        for r in res:
            if not colle(r["title"], n):
                continue
            pages = api(host, action="query", titles=r["title"], prop="pageimages|images",
                        piprop="name", imlimit=50)["query"]["pages"]
            page = pages[0]
            noms = ([page["pageimage"]] if page.get("pageimage") else []) + [i["title"] for i in page.get("images", [])]
            noms = [x if ":" in x else "File:" + x for x in noms]
            # L'image principale de la page si c'est un logo, sinon une image qui porte le nom :
            # les autres images de la page sont souvent d'autres logos (partenaires, transports).
            principale = noms[:1] if page.get("pageimage") else []
            logos = [x for x in noms if "logo" in x.lower() and not ICONE.search(x)
                     and (x in principale or colle(x, n))]
            logos.sort(key=lambda t: ordre(t, n))
            for t in logos[:2]:
                info = info_fichier(host, t)
                if info:
                    return (*info, f"{libelle}, page {r['title']}, {t}")
    return None


def site(nom, liens):
    domaines = []
    for lien in liens:
        host = urllib.parse.urlsplit(lien).netloc.lower()
        if host and not PAS_EMPLOYEUR.search(host):
            dom = ".".join(host.split(".")[-2:])
            if dom not in domaines:
                domaines.append(dom)
    for dom in domaines[:2]:
        try:
            page = get(f"https://www.{dom}/", timeout=15)
        except Exception:  # noqa: BLE001
            continue
        for tag in re.findall(r"<img\b[^>]*>", page, re.I):
            if "logo" not in tag.lower():
                continue
            m = re.search(r'\bsrc="([^"]+)"', tag) or re.search(r"\bsrc='([^']+)'", tag)
            if not m or m.group(1).startswith("data:"):
                continue
            url = urllib.parse.urljoin(f"https://www.{dom}/", m.group(1))
            ext = "svg" if ".svg" in url.lower() else "png"
            return url, ext, f"site de l'employeur ({dom})"
    return None


def telecharge(url, ext, dest):
    data, ctype = get(url, binary=True)
    if ext == "svg" and b"<svg" not in data[:5000]:
        raise ValueError("pas un SVG")
    if ext != "svg":
        ext = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp", "image/gif": "gif"}.get(
            ctype.split(";")[0].strip(), None)
        if not ext:
            raise ValueError(f"type inattendu {ctype}")
    path = dest.with_suffix("." + ext)
    path.write_bytes(data)
    return path.name


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", required=True)
    ap.add_argument("--table", required=True)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--max", type=int, default=MAX_RECHERCHES)
    args = ap.parse_args()

    table = json.load(open(args.table, encoding="utf-8"))
    for k in ("logos", "alias", "introuvables"):
        table.setdefault(k, {})
    board = json.load(open(args.board, encoding="utf-8"))["offres"]
    dossier = Path(args.dir)
    dossier.mkdir(parents=True, exist_ok=True)
    today = dt.date.today()

    liens = {}
    for o in board:
        liens.setdefault(o["entreprise"], []).append(o.get("lien", ""))
    a_chercher = []
    for nom in liens:
        if trouve(table, nom):
            continue
        k = cle(nom)
        vu = table["introuvables"].get(k)
        if vu and (today - dt.date.fromisoformat(vu)).days < RETRY_DAYS:
            continue
        a_chercher.append(nom)

    trouves, rates = [], []
    for nom in a_chercher[: args.max]:
        k = cle(nom)
        res = None
        for chercheur in (lambda: commons(nom), lambda: wikipedia(nom),
                          lambda: wikipedia(nom, "fr.wikipedia.org", "Wikipédia en français"),
                          lambda: site(nom, liens[nom])):
            try:
                res = chercheur()
            except Exception as exc:  # noqa: BLE001 - une source en panne n'arrête pas les autres
                print(f"  {nom} : {type(exc).__name__} {exc}", file=sys.stderr)
                res = None
            if res:
                break
            time.sleep(0.5)
        if not res:
            table["introuvables"][k] = today.isoformat()
            rates.append(nom)
            continue
        url, ext, source = res
        deja = next((kk for kk, v in table["logos"].items() if v.get("url") == url), None)
        if deja:
            table["alias"][k] = deja
            table["introuvables"].pop(k, None)
            trouves.append(f"{nom} -> même logo que « {deja} »")
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", k).strip("-")[:60] or "logo"
        try:
            fichier = telecharge(url, ext, dossier / slug)
        except Exception as exc:  # noqa: BLE001
            table["introuvables"][k] = today.isoformat()
            rates.append(f"{nom} (téléchargement : {exc})")
            continue
        table["logos"][k] = {"fichier": fichier, "source": f"{source}, {today.isoformat()}", "url": url}
        table["introuvables"].pop(k, None)
        trouves.append(f"{nom} -> {fichier} ({source})")
        time.sleep(0.5)

    Path(args.table).write_text(json.dumps(table, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    reste = max(0, len(a_chercher) - args.max)
    print(f"Logos : {len(trouves)} trouvés, {len(rates)} introuvables"
          + (f", {reste} employeurs remis au prochain passage" if reste else ""))
    for t in trouves:
        print("  + " + t)
    for r in rates:
        print("  - " + r)


if __name__ == "__main__":
    main()
