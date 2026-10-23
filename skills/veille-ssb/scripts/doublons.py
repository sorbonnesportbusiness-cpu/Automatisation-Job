# -*- coding: utf-8 -*-
"""
Repérage des doublons du tableau. Une même offre arrive souvent deux fois : par le
site de l'employeur et par LinkedIn ou HelloWork, ou par deux variantes d'un même
lien (/fr-FR/ dans Workday, slug -f-h / -f-m chez Breezy, / final chez Flatchr...).

Deux offres sont le même poste si :
  - leurs liens donnent la même clé (hôte + identifiant de l'offre), ou
  - même employeur, même intitulé une fois retirés « Stage », H/F, (e), .e...,
    et pas deux villes différentes.
Les précisions entre parenthèses restent dans l'intitulé : « (Wittenheim) » et
« (Puilboreau) », ou « (mars-juillet 2027) » et « (avril-septembre 2027) », sont
bien deux offres.

On garde le lien employeur plutôt qu'un agrégateur, puis l'offre la plus ancienne.
"""

import re
import unicodedata
from urllib.parse import urlsplit

AGGREGATORS = re.compile(
    r"linkedin\.|hellowork\.|indeed\.|welcometothejungle\.|jobteaser\.|talent\.com|meteojob\.|"
    r"labonnealternance\.|wizbii\.|sportbuzzbusiness\.|cvsportsjob\.|vmatch\.|globalsportsjobs\.|"
    r"sportstrategies\.|ecofoot\.|lesportrecrute\.|meent\.", re.I)
# Mots d'intitulé sans valeur pour comparer : marques de genre et « stage ».
NOISE = {"h", "f", "x", "d", "m", "w", "e", "fe", "ffe", "hf", "fh", "hfx", "fhx", "hfd", "fhd",
         "stage", "stagiaire"}


def _ascii(text):
    return unicodedata.normalize("NFD", text or "").encode("ascii", "ignore").decode().lower()


def _words(text):
    return re.sub(r"[^a-z0-9]+", " ", _ascii(text)).split()


def link_key(url):
    """Hôte + identifiant de l'offre, pour reconnaître deux variantes d'un même lien."""
    parts = urlsplit(url or "")
    host = parts.netloc.lower().removeprefix("www.")
    host = re.sub(r"^[a-z]{2}\.linkedin\.com$", "linkedin.com", host)
    path = parts.path.rstrip("/")
    for pattern in (
        r"linkedin\.com/jobs/view/(?:.*-)?(\d{8,})",
        r"myworkday(?:site|jobs)\.com/.*_([A-Z]*\d[\w-]*)$",
        r"smartrecruiters\.com/[^/]+/(\d{6,})",
        r"breezy\.hr/p/([0-9a-f]{8,})",
        r"hellowork\.com/.*/(\d{6,})\.html",
    ):
        m = re.search(pattern, host + path)
        if m:
            return f"{host}#{m.group(1)}"
    path = re.sub(r"/[a-z]{2}-[A-Z]{2}(?=/)", "", path)  # segment de langue /fr-FR/
    return f"{host}{path}"


def title_key(title):
    return " ".join(w for w in _words(title) if w not in NOISE)


def employer_words(o):
    """(mots du nom sans parenthèses, mots du nom complet)."""
    name = o.get("entreprise", "")
    return set(_words(re.sub(r"\(.*?\)", "", name))), set(_words(name))


def same_employer(a, b):
    (short_a, full_a), (short_b, full_b) = employer_words(a), employer_words(b)
    return bool(short_a and short_b) and (short_a <= full_b or short_b <= full_a)


def same_city(a, b):
    city_a, city_b = _words(a.get("localisation", ""))[:1], _words(b.get("localisation", ""))[:1]
    return not (city_a and city_b) or city_a == city_b


def is_aggregator(o):
    return bool(AGGREGATORS.search(urlsplit(o.get("lien", "")).netloc))


def same_offer(a, b):
    if link_key(a["lien"]) == link_key(b["lien"]):
        return True
    return title_key(a["titre"]) == title_key(b["titre"]) and same_employer(a, b) and same_city(a, b)


def _rank(o):
    return (is_aggregator(o), o.get("ajoutee_le") or "9999", o.get("date_iso") or "9999")


def dedupe(offers):
    """Renvoie (offres gardées, [(offre retirée, offre gardée)]), ordre d'origine conservé."""
    by_title, by_link, groups = {}, {}, []
    for o in offers:
        group = by_link.get(link_key(o["lien"]))
        if group is None:
            group = next((g for g in by_title.get(title_key(o["titre"]), []) if any(same_offer(o, x) for x in g)), None)
        if group is None:
            group = []
            groups.append(group)
            by_title.setdefault(title_key(o["titre"]), []).append(group)
        group.append(o)
        by_link[link_key(o["lien"])] = group
    keep_ids, removed = set(), []
    for group in groups:
        best = min(group, key=_rank)
        for other in group:
            if other is best:
                continue
            removed.append((other, best))
            # Le poste n'est pas nouveau parce qu'on a trouvé un meilleur lien.
            for field in ("ajoutee_le", "date_iso"):
                dates = [d for d in (best.get(field), other.get(field)) if d]
                if dates:
                    best[field] = min(dates)
        keep_ids.add(id(best))
    return [o for o in offers if id(o) in keep_ids], removed
