#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moissonne les API publiques des sites carrières listés dans references/sources.json
(Workday, SmartRecruiters, Lever, Greenhouse, Ashby, Teamtailor, Workable, Breezy,
Recruitee, Personio, Pinpoint, Jobylon, flux schema.org de softgarden, DigitalRecruiters, Taleez, Flatchr, WordPress, flux RSS, agrégateur GlobalSportsJobs) et écrit les offres candidates au format du skill.

Le script ne fait que le gros du tri : offres de moins de 60 jours, niveau junior,
métiers sport business, intitulé et extrait en français ou en anglais, pas déjà au
tableau ni déjà livrées. Un sous-agent relit
ensuite les candidates (champ `_extrait`) avant qu'elles n'entrent au tableau.

Une source d'actualités (blog, flux RSS d'une fac) porte "junior_obligatoire": true : seuls
les intitulés de stage, d'alternance ou de poste junior sont gardés.

Chaque source peut porter "exclure" : une expression régulière appliquée à l'intitulé
normalisé (minuscules, sans accents) pour écarter le bruit propre à cet employeur.

Usage :
    python3 harvest.py --sources references/sources.json --board data/offres.json \
        --history references/historique.md --date 2026-10-19 --out out/candidats/2026-10-19-api.json
    python3 harvest.py ... --only "Manchester United"   # tester une source
"""

import argparse
import html
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from langue import offre_ok  # noqa: E402

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0 Safari/537.36")
MAX_JOBS = 600  # par source, pour ne pas paginer sans fin un ATS mondial

# --- Filtres -----------------------------------------------------------------

def norm(text):
    text = unicodedata.normalize("NFD", text or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", text)

# Postes juniors explicites (seuls acceptés hors de France).
JUNIOR = re.compile(r"\b(stage|stagiaire|intern|interns|internship|placement|alternan\w*|apprenti\w*|"
                    r"graduate|trainee|junior|working student|werkstudent\w*|praktik\w*|practicas|"
                    r"becari\w*|stagista|tirocin\w*|entry[- ]level|v\.?i\.?e\.?|work[- ]study|"
                    r"contrat pro\w*|year in industry)\b")
SENIOR = re.compile(r"\b(head|director|directeu\w*|directrice|direction|vp|vice[- ]president|chief|cfo|cmo|"
                    r"ceo|coo|senior|sr|lead|principal|responsable|manager|managing|expert|confirme|"
                    r"experimente|partner|associate director)\b")
# Métiers hors cible, sur l'intitulé.
OFF_TARGET = re.compile(
    r"\b(coach\w*|entraineu\w*|educateur|educatrice|kine\w*|physio\w*|medecin|doctor|nurse|infirmi\w*|"
    r"osteo\w*|scout\w*|video analyst|analyste video|performance analyst|sport scien\w*|sports scien\w*|"
    r"preparat\w*|strength|groundsman|grounds\w*|pitch|jardinier|greenkeeper|cuisin\w*|chef de partie|"
    r"commis|serveu\w*|barista|waiter|waitress|kitchen|bartender|steward\w*|securite|security|"
    r"maintenance|technicien\w*|technician|electric\w*|plomb\w*|engineer\w*|ingenieu\w*|developer|"
    r"developpeu\w*|devops|software|fullstack|full stack|frontend|backend|sre|helpdesk|it support|"
    r"warehouse|entrepot|magasinier|driver|chauffeur|cashier|caissi\w*|vendeu\w*|sales associate|"
    r"store|magasin|boutique|retail assistant|conseiller de vente|cleaner|nettoy\w*|entretien|lifeguard|"
    r"maitre[- ]nageur|animat\w*|instructor|instructeur|moniteu\w*|personal trainer|coach sportif|"
    r"hote\w* de caisse|picker|packer|forklift|mechanic|mecanicien|kit man|kitman|physiotherap\w*|"
    r"soigneu\w*|dietet\w*|nutritionist|psycholog\w*|referee|arbitre|joueu\w*|stock\w*|shop|"
    r"conseill\w* de vente\w*|data scien\w*|research|r ?& ?d|genai|nlp|machine learning|quantitative|"
    r"analyse video|espaces verts|referent sportif|casino|product owner|it|si|informatique|"
    r"systemes? d.information|design\w*|architecte|ux|ui|education|cyber\w*|cloud|sysadmin|qa|"
    r"acheteu\w*|achats?|logisti\w*|supply chain|transport\w*|ambassador|ambassadeu\w*|"
    r"fraud\w*|releaser|nutrition\w*|hris|payroll|paie|recrut\w*|recruit\w*|people ops|ressources humaines|"
    r"rh|hr|office management|empfang|reception\w*|plm|planner|planning|merchandiser|equipment|construction|"
    r"knowledge management|accountant|comptable|schulerpraktikum|fachlager\w*|schuhfertig\w*|"
    r"(footwear|apparel|material) development|product testing|quality|workplace management|trainer\w*|"
    r"sicherheit|anwendersupport|information technology|customer service|allocator|music|marketeer|"
    r"barman|barmaid|sous chef|veiligheid|poker|journalism\w*|visual merchandis\w*)\b")
# Pour un employeur hors sport, l'offre doit parler explicitement de sport ou de sponsoring.
SPORT = re.compile(r"(\bsports?\b|sportif|sportive|sponsor|parrainage|athlet|olymp|paralymp|football|rugby|"
                   r"tennis|basket|cyclisme|e-?sport|stadium)")

MONTHS_FR_EN = {"jan": 1, "fev": 2, "feb": 2, "mar": 3, "avr": 4, "apr": 4, "mai": 5, "may": 5, "juin": 6,
                "june": 6, "juil": 7, "july": 7, "aou": 8, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}


def month_num(word):
    return next(v for k, v in MONTHS_FR_EN.items() if word.startswith(k))
START = re.compile(r"\b(janv\w*|janu\w*|fevr\w*|febr\w*|mars|march|avril|april|mai|may|juin|june|juil\w*|july|"
                   r"aout|august|sept\w*|octo\w*|nove\w*|dece\w*) (20\d\d)\b")
run_month = None  # (année, mois) de la veille, fixé dans main()

COUNTRIES = {
    "france": "France", "fr": "France", "fra": "France",
    "united kingdom": "Royaume-Uni", "uk": "Royaume-Uni", "gb": "Royaume-Uni", "gbr": "Royaume-Uni",
    "england": "Royaume-Uni", "scotland": "Royaume-Uni", "wales": "Royaume-Uni", "great britain": "Royaume-Uni",
    "spain": "Espagne", "es": "Espagne", "espana": "Espagne", "esp": "Espagne",
    "italy": "Italie", "it": "Italie", "italia": "Italie", "ita": "Italie",
    "germany": "Allemagne", "de": "Allemagne", "deutschland": "Allemagne", "deu": "Allemagne",
    "switzerland": "Suisse", "ch": "Suisse", "schweiz": "Suisse", "suisse": "Suisse", "che": "Suisse",
    "netherlands": "Pays-Bas", "nl": "Pays-Bas", "nld": "Pays-Bas", "the netherlands": "Pays-Bas",
    "belgium": "Belgique", "be": "Belgique", "belgique": "Belgique", "bel": "Belgique",
    "portugal": "Portugal", "pt": "Portugal", "prt": "Portugal",
    "monaco": "Monaco", "mc": "Monaco", "mco": "Monaco",
    "ireland": "Irlande", "ie": "Irlande", "irl": "Irlande",
    "austria": "Autriche", "at": "Autriche", "aut": "Autriche", "osterreich": "Autriche",
    "luxembourg": "Luxembourg", "lu": "Luxembourg", "lux": "Luxembourg",
    "united states": "États-Unis", "us": "États-Unis", "usa": "États-Unis",
    "united states of america": "États-Unis", "canada": "Canada", "ca": "Canada",
    "united arab emirates": "Émirats arabes unis", "ae": "Émirats arabes unis", "uae": "Émirats arabes unis",
    "denmark": "Danemark", "dk": "Danemark", "sweden": "Suède", "se": "Suède", "norway": "Norvège",
    "poland": "Pologne", "pl": "Pologne", "australia": "Australie", "au": "Australie",
    "singapore": "Singapour", "sg": "Singapour", "qatar": "Qatar", "qa": "Qatar",
    "saudi arabia": "Arabie saoudite", "sa": "Arabie saoudite", "morocco": "Maroc", "ma": "Maroc",
}
# Hors de France, on ne garde que l'Europe (droit de travail accessible ou presque aux étudiants
# français), sauf si la source porte "hors_europe": true.
EUROPE = {"Royaume-Uni", "Espagne", "Italie", "Allemagne", "Suisse", "Pays-Bas", "Belgique", "Portugal",
          "Monaco", "Irlande", "Autriche", "Luxembourg", "Danemark", "Suède", "Norvège", "Pologne"}
FR_HINT = re.compile(r"\b(paris|lyon|marseille|lille|bordeaux|toulouse|nantes|nice|rennes|montpellier|"
                     r"strasbourg|grenoble|annecy|boulogne|levallois|saint-denis|issy|courbevoie|"
                     r"la defense|villeneuve|ile-de-france|\(\d{2}\))")


def country_of(text, default=None):
    t = norm(text)
    for part in reversed([p.strip() for p in re.split(r"[,/|;\-–()]", t) if p.strip()]):
        if part in COUNTRIES:
            return COUNTRIES[part]
    for name, fr in COUNTRIES.items():
        if len(name) > 3 and re.search(rf"\b{re.escape(name)}\b", t):
            return fr
    if FR_HINT.search(t):
        return "France"
    return default


def contract_of(title, hint=""):
    t = norm(f"{title} {hint}")
    if re.search(r"alternan|apprenti|work[- ]study|contrat pro", t):
        return "Alternance"
    if re.search(r"\b(stage|stagiaire|intern|interns|internship|placement|praktik\w*|practicas|becari\w*|"
                 r"stagista|tirocin\w*|working student|werkstudent\w*|year in industry)\b", t):
        return "Stage"
    if re.search(r"\b(cdd|fixed[- ]term|temporary|temporaire|seasonal|saisonnier|contract role|interim)\b", t):
        return "CDD"
    if re.search(r"\b(freelance|independant)\b", t):
        return "Freelance"
    return "CDI"


def keep(job, src):
    """Renvoie (garder, raison)."""
    t = norm(job["titre"])
    if OFF_TARGET.search(t):
        return False, "métier hors cible"
    ok, why = offre_ok(job["titre"], job.get("_extrait", ""))
    if not ok:
        return False, why
    if src.get("exclure") and re.search(src["exclure"], t):
        return False, "exclu pour cette source"
    junior = bool(JUNIOR.search(t)) or job.get("_niveau") in ("internship", "intern")
    if src.get("junior_obligatoire") and not junior:
        return False, "pas un stage ni un poste junior (source d'actualités)"
    if job["pays"] != "France" and not junior:
        return False, "étranger : pas un poste junior"
    if job["pays"] not in ("France", "?") and job["pays"] not in EUROPE and not src.get("hors_europe"):
        return False, f"hors Europe ({job['pays']})"
    if SENIOR.search(t) and not JUNIOR.search(t):
        return False, "poste senior"
    if job.get("_niveau") in ("mid_senior_level", "director", "executive"):
        return False, "poste senior (niveau ATS)"
    if job["pays"] == "?" and src.get("pays") == "Monde":
        return False, "pays inconnu (ATS mondial)"
    m = START.search(t)
    if m and run_month and (int(m.group(2)), month_num(m.group(1))) < run_month:
        return False, "date de début passée"
    if src.get("filtre") == "sport" and not SPORT.search(norm(job["titre"] + " " + job.get("_extrait", ""))):
        return False, "employeur hors sport, offre sans lien avec le sport"
    return True, ""

# --- HTTP ----------------------------------------------------------------------

def fetch(url, data=None, headers=None, timeout=25):
    h = {"User-Agent": UA, "Accept": "application/json, application/xml, text/xml, */*",
         "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"}
    h.update(headers or {})
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=h, method="POST" if body else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def get_json(url, data=None, headers=None):
    return json.loads(fetch(url, data, headers))


def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"(?s)<[^>]+>", " ", s or ""))).strip()


def iso(value):
    """Date ISO (AAAA-MM-JJ) depuis un timestamp ms, une date ISO ou une date RSS."""
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).date().isoformat()
    s = str(value).strip()
    m = re.match(r"(\d{4}-\d{2}-\d{2})", s)
    if m:
        return m.group(1)
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z", "%d/%m/%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def job(titre, lien, date_iso=None, localisation="", pays=None, contrat_hint="", extrait="", niveau=None):
    return {"titre": strip_tags(titre), "lien": lien, "date_iso": date_iso, "localisation": localisation.strip(),
            "pays": pays, "_contrat": contrat_hint, "_extrait": strip_tags(extrait)[:400], "_niveau": niveau}

# --- Lecteurs par ATS ----------------------------------------------------------

def read_workday(s, run):
    base = f"https://{s['host']}/wday/cxs/{s['tenant']}/{s['site']}"
    public = f"https://{s['host']}/{s['site']}"
    out, searches = [], s.get("recherche") or [""]
    for q in searches:
        offset = 0
        while offset < MAX_JOBS:
            d = get_json(f"{base}/jobs", {"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": q})
            posts = d.get("jobPostings", [])
            for p in posts:
                posted = (p.get("postedOn") or "").lower()
                age = 0 if "today" in posted or "aujourd" in posted else 1 if "yesterday" in posted or "hier" in posted else None
                m = re.search(r"(\d+)\+?", posted)
                if age is None and m:
                    age = int(m.group(1)) + (1 if "+" in posted else 0)
                out.append(job(p.get("title", ""), public + p.get("externalPath", ""),
                               (run - timedelta(days=age)).isoformat() if age is not None and "+" not in posted else None,
                               p.get("locationsText", ""), contrat_hint=p.get("timeType", "")) | {"_path": p.get("externalPath")})
            offset += 20
            if len(posts) < 20 or offset >= d.get("total", 0):
                break
    seen, uniq = set(), []
    for j in out:
        if j["lien"] not in seen:
            seen.add(j["lien"]); uniq.append(j)
    return uniq


def detail_workday(s, j):
    """Date exacte, pays et extrait pour une offre Workday qui a passé les filtres d'intitulé."""
    d = get_json(f"https://{s['host']}/wday/cxs/{s['tenant']}/{s['site']}{j['_path']}").get("jobPostingInfo", {})
    j["date_iso"] = iso(d.get("startDate")) or j["date_iso"]
    j["localisation"] = d.get("location") or j["localisation"]
    j["pays"] = country_of((d.get("country") or {}).get("descriptor", "")) or j["pays"]
    j["_extrait"] = strip_tags(d.get("jobDescription", ""))[:400]
    j["lien"] = d.get("externalUrl") or j["lien"]


def read_smartrecruiters(s, run):
    out, offset = [], 0
    qs = {"limit": 100}
    if s.get("pays_filtre") == "France":
        qs["country"] = "fr"
    while offset < MAX_JOBS:
        qs["offset"] = offset
        d = get_json(f"https://api.smartrecruiters.com/v1/companies/{s['company']}/postings?{urllib.parse.urlencode(qs)}")
        for p in d.get("content", []):
            loc = p.get("location") or {}
            out.append(job(p.get("name", ""), f"https://jobs.smartrecruiters.com/{s['company']}/{p.get('id')}",
                           iso(p.get("releasedDate")), ", ".join(x for x in (loc.get("city"), loc.get("country", "").upper()) if x),
                           country_of(loc.get("country", "")) or (loc.get("country") or "?").upper(),
                           (p.get("typeOfEmployment") or {}).get("label", ""),
                           niveau=(p.get("experienceLevel") or {}).get("id")))
        offset += 100
        if offset >= d.get("totalFound", 0):
            break
    return out


def read_lever(s, run):
    host = "api.eu.lever.co" if s.get("region") == "eu" else "api.lever.co"
    d = get_json(f"https://{host}/v0/postings/{s['slug']}?mode=json")
    out = []
    for p in d:
        c = p.get("categories") or {}
        out.append(job(p.get("text", ""), p.get("hostedUrl", ""), iso(p.get("createdAt")), c.get("location", ""),
                       country_of(p.get("country", "") or c.get("location", "")), c.get("commitment", ""),
                       p.get("descriptionPlain", "")))
    return out


def read_greenhouse(s, run):
    d = get_json(f"https://boards-api.greenhouse.io/v1/boards/{s['board']}/jobs")
    return [job(p.get("title", ""), p.get("absolute_url", ""), iso(p.get("first_published") or p.get("updated_at")),
                (p.get("location") or {}).get("name", ""), country_of((p.get("location") or {}).get("name", "")))
            for p in d.get("jobs", [])]


def read_ashby(s, run):
    d = get_json(f"https://api.ashbyhq.com/posting-api/job-board/{s['org']}")
    out = []
    for p in d.get("jobs", []):
        if p.get("isListed") is False:
            continue
        addr = ((p.get("address") or {}).get("postalAddress") or {})
        out.append(job(p.get("title", ""), p.get("jobUrl", ""), iso(p.get("publishedAt")), p.get("location", ""),
                       country_of(addr.get("addressCountry", "") or p.get("location", "")), p.get("employmentType", ""),
                       p.get("descriptionPlain", "")))
    return out


def read_rss(s, run):
    url = s["url"].rstrip("/") + "/jobs.rss" if s["ats"] == "teamtailor" else s["url"]
    root = ET.fromstring(fetch(url))
    out = []
    for it in root.iter():
        if it.tag.split("}")[-1] not in ("item", "entry"):
            continue
        fields = {c.tag.split("}")[-1].lower(): (c.text or c.get("href") or "").strip() for c in it}
        locs = " ".join((c.text or "") for c in it.iter() if c.tag.split("}")[-1].lower() in ("city", "country", "location", "name"))
        out.append(job(fields.get("title", ""), fields.get("link", ""),
                       iso(fields.get("pubdate") or fields.get("published") or fields.get("updated")),
                       locs, country_of(locs), extrait=fields.get("description", "") or fields.get("summary", "")))
    return out


def read_workable(s, run):
    d = get_json(f"https://apply.workable.com/api/v1/widget/accounts/{s['slug']}")
    return [job(p.get("title", ""), p.get("url") or p.get("application_url", ""), iso(p.get("published_on") or p.get("created_at")),
                ", ".join(x for x in (p.get("city"), p.get("country")) if x), country_of(p.get("country", "")),
                p.get("employment_type", "")) for p in d.get("jobs", [])]


def read_breezy(s, run):
    d = get_json(f"https://{s['slug']}.breezy.hr/json")
    out = []
    for p in d:
        loc = p.get("location") or {}
        country = (loc.get("country") or {}).get("name", "") if isinstance(loc.get("country"), dict) else loc.get("country", "")
        out.append(job(p.get("name", ""), p.get("url", ""), iso(p.get("published_date")),
                       ", ".join(x for x in (loc.get("city"), country) if x), country_of(country),
                       (p.get("type") or {}).get("name", "")))
    return out


def read_recruitee(s, run):
    d = get_json(f"https://{s['slug']}.recruitee.com/api/offers/")
    return [job(p.get("title", ""), p.get("careers_url", ""), iso(p.get("published_at") or p.get("created_at")),
                ", ".join(x for x in (p.get("city"), p.get("country")) if x), country_of(p.get("country", "") or p.get("country_code", "")),
                p.get("employment_type_code", ""), p.get("description", ""), p.get("experience_code"))
            for p in d.get("offers", [])]


def read_personio(s, run):
    dom = s.get("domain", "jobs.personio.de")
    root = ET.fromstring(fetch(f"https://{s['slug']}.{dom}/xml"))
    out = []
    for p in root.iter("position"):
        g = lambda k: (p.findtext(k) or "").strip()
        out.append(job(g("name"), f"https://{s['slug']}.{dom}/job/{g('id')}", iso(g("createdAt")), g("office"),
                       country_of(g("office")), f"{g('employmentType')} {g('seniority')}"))
    return out


def read_pinpoint(s, run):
    """Pinpoint ne donne pas de date de publication : le relecteur la relève sur la fiche."""
    d = get_json(s.get("url") or f"https://{s['slug']}.pinpointhq.com/postings.json")
    out = []
    for p in d.get("data", []):
        loc = p.get("location") or {}
        j = job(p.get("title", ""), p.get("url", ""), None, loc.get("name", ""),
                country_of(loc.get("name", "")), p.get("employment_type_text", ""), p.get("description", ""))
        if p.get("deadline_at"):
            j["_extrait"] = f"clôture {iso(p['deadline_at'])} · " + j["_extrait"]
        out.append(j)
    return out


def _js_str(block, key):
    m = re.search(rf"\b{key}: '((?:[^'\\]|\\.)*)'", block)
    return json.loads('"' + m.group(1).replace('"', '\\"') + '"') if m else ""


def _en_date(text):
    m = re.match(r"([A-Za-z]+)\.? (\d{1,2}), (\d{4})", text or "")
    if not m:
        return None
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    mon = m.group(1)[:3].lower()
    return date(int(m.group(3)), months.index(mon) + 1, int(m.group(2))).isoformat() if mon in months else None


def read_jobylon(s, run):
    """Widget Jobylon (UEFA = société 2972) : les offres sont des objets JS dans la page."""
    page = fetch(f"https://cdn.jobylon.com/jobs/companies/{s['company_id']}/embed/v2/?target=jobylon-jobs-widget&page_size=100")
    out = []
    for block in re.split(r"\n\s*\{\s*\n\s*id: '", page)[1:]:
        url = _js_str(block, "url")
        if not url.startswith("/jobs/"):
            continue
        j = job(_js_str(block, "title"), "https://emp.jobylon.com" + url, _en_date(_js_str(block, "published_date")),
                _js_str(block, "locations_text"), s.get("pays") if s.get("pays") != "Monde" else None,
                _js_str(block, "employment_type"), niveau="internship" if "Trainee" in block else None)
        j["_entreprise"] = _js_str(block, "company") or None
        close = _en_date(_js_str(block, "to_date"))
        if close:
            j["_extrait"] = f"clôture {close} · expérience : {_js_str(block, 'experience')}"
        out.append(j)
    return out


def read_schema_feed(s, run):
    """Flux schema.org DataFeed de JobPosting (softgarden : <site>/jobs.feed.json)."""
    d = get_json(s["url"])
    out = []
    for el in d.get("dataFeedElement", []):
        p = el.get("item") or {}
        locs = p.get("jobLocation") or []
        locs = locs if isinstance(locs, list) else [locs]
        addr = " ".join(f"{(l.get('address') or {}).get('addressLocality', '')} {(l.get('address') or {}).get('addressCountry', '')}"
                        for l in locs if isinstance(l, dict))
        j = job(p.get("title", ""), p.get("url", ""), iso(p.get("datePosted")), addr.strip(), country_of(addr),
                str(p.get("employmentType", "")), p.get("description", ""))
        if p.get("validThrough"):
            j["_extrait"] = f"clôture {iso(p['validThrough'])} · " + j["_extrait"]
        out.append(j)
    return out


def read_wordpress(s, run):
    """API REST WordPress d'un site carrières (posts ou type d'offre daté), 60 derniers jours."""
    after = (run - timedelta(days=62)).isoformat() + "T00:00:00"
    out, page = [], 1
    while page <= 15:
        sep = "&" if "?" in s["url"] else "?"
        try:
            d = get_json(f"{s['url']}{sep}per_page=100&page={page}&after={after}&_fields=title,link,date,excerpt,content")
        except urllib.error.HTTPError as exc:
            if exc.code == 400:  # au-delà de la dernière page
                break
            raise
        for p in d:
            body = (p.get("content") or {}).get("rendered", "") or (p.get("excerpt") or {}).get("rendered", "")
            out.append(job((p.get("title") or {}).get("rendered", ""), p.get("link", ""), iso(p.get("date")),
                           s.get("ville", ""), s.get("pays") if s.get("pays") != "Monde" else None, extrait=body))
        if len(d) < 100:
            break
        page += 1
    return out


DR = "https://api.digitalrecruiters.com/public/v1/careers-site/job-ads"


def read_digitalrecruiters(s, run):
    """DigitalRecruiters (Decathlon, Lacoste) : liste sans date, la date est lue au détail."""
    out, page = [], 1
    while len(out) < s.get("max", 1500):
        qs = urllib.parse.urlencode({"domainName": s["domain"], "limit": 100, "page": page, "locale": "fr_FR"})
        d = get_json(f"{DR}?{qs}", {"filters": {}})
        for p in d.get("items", []):
            j = job(p.get("title", ""), f"https://{s['domain']}/fr/annonce/{p.get('url', '')}", None,
                    p.get("location", ""), "France", p.get("contract", ""))
            j["_dr_id"] = p.get("job_ad_id")
            out.append(j)
        if page * 100 >= d.get("count", 0) or not d.get("items"):
            break
        page += 1
    return out


def detail_digitalrecruiters(s, j):
    qs = urllib.parse.urlencode({"domainName": s["domain"], "locale": "fr_FR", "withJsonld": 1})
    d = get_json(f"{DR}/{j['_dr_id']}?{qs}")
    j["date_iso"] = iso((d.get("jsonld") or {}).get("datePosted")) or iso(d.get("republished_at"))
    j["_extrait"] = strip_tags(d.get("description", ""))[:400]


def read_taleez(s, run):
    d = get_json(f"https://{s['slug']}.taleez.com/api/careez")
    out = []
    for p in d.get("jobs", []):
        loc = p.get("location") or {}
        out.append(job(p.get("label", ""), f"https://{s['slug']}.taleez.com/jobs/{p.get('slug', '')}",
                       iso(p.get("publishDate") or p.get("creationDate")),
                       f"{loc.get('city', '')} ({loc.get('departmentCode', '')})" if loc.get("city") else p.get("officeName", ""),
                       country_of(loc.get("country", "")) or "France", p.get("contract", "")))
    return out


def read_flatchr(s, run):
    """Flatchr : les offres sont dans le __NEXT_DATA__ de la page entreprise."""
    page = fetch(f"https://careers.flatchr.io/fr/company/{s['slug']}/")
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', page, re.S)
    out, seen = [], set()

    def walk(o):
        if isinstance(o, dict):
            v = o.get("vacancy")
            if isinstance(v, dict) and v.get("slug") and v.get("title") and v["slug"] not in seen:
                seen.add(v["slug"])
                addr = (v.get("company") or {}).get("address") or v.get("address") or {}
                out.append(job(v["title"], f"https://careers.flatchr.io/fr/company/{s['slug']}/vacancy/{v['slug']}/",
                               iso(o.get("publish_date") or o.get("created_at")),
                               addr.get("locality", "") if isinstance(addr, dict) else "", "France",
                               str(v.get("contract_type", "")), v.get("description", "")))
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    if m:
        walk(json.loads(m.group(1)))
    return out


GSJ = "https://api.globalsportsjobs.com/api/jobs"
GSJ_SECTORS = {"clubs": "Club", "leagues": "Ligue / Fédération", "federations": "Ligue / Fédération",
               "governing_bodies": "Ligue / Fédération", "agencies": "Agence", "media": "Média",
               "broadcasters": "Média", "brands": "Marque / Sponsor", "betting": "Paris sportifs",
               "events": "Organisateur / Événement", "venues": "Stade / Arène", "technology": "Sportstech"}
GSJ_OFF = {"people", "coaching", "medical", "engineering", "technology", "performance"}


def read_globalsportsjobs(s, run):
    """Agrégateur : une page par pays (`pays_liste`, noms anglais), stages et jobs étudiants (careerStage=0)."""
    out = []
    for country in s.get("pays_liste", []):
        cursor, n = None, 0
        while n < 300:
            qs = {"location": country, "careerStage": s.get("careerStage", 0), "limit": 50}
            if cursor:
                qs["cursor"] = cursor
            d = get_json(f"{GSJ}?{urllib.parse.urlencode(qs)}")
            for p in d.get("items", []):
                if p.get("occupation") in GSJ_OFF:
                    continue
                j = job(p.get("title", ""), f"gsj:{p['id']}", iso(p.get("postedAt")), p.get("location", ""),
                        country_of(p.get("location", "")), p.get("employmentType", ""), niveau="internship")
                j["_entreprise"] = p.get("companyName")
                j["_categorie"] = GSJ_SECTORS.get(p.get("sectorType"), "")
                out.append(j)
            n += len(d.get("items", []))
            cursor = d.get("nextCursor")
            if not cursor or not d.get("items"):
                break
    return out


def detail_gsj(j):
    """Lien de l'employeur (la fiche GSJ est réservée aux membres) et contrôle d'ouverture."""
    d = get_json(f"{GSJ}/{j['lien'][4:]}").get("job", {})
    if d.get("status") != "active" or d.get("isExpired") or not d.get("applicationUrl"):
        return False
    j["lien"] = re.sub(r"/apply/?$", "", d["applicationUrl"])
    j["_extrait"] = strip_tags(d.get("description", ""))[:400]
    if d.get("expiresOn"):
        j["_extrait"] = f"clôture {iso(d['expiresOn'])} · " + j["_extrait"]
    return True


READERS = {"workday": read_workday, "smartrecruiters": read_smartrecruiters, "lever": read_lever,
           "greenhouse": read_greenhouse, "ashby": read_ashby, "teamtailor": read_rss, "rss": read_rss,
           "successfactors_rss": read_rss, "workable": read_workable, "breezy": read_breezy,
           "recruitee": read_recruitee, "personio": read_personio, "pinpoint": read_pinpoint, "jobylon": read_jobylon, "schema_feed": read_schema_feed,
           "digitalrecruiters": read_digitalrecruiters, "wordpress": read_wordpress, "taleez": read_taleez, "flatchr": read_flatchr,
           "globalsportsjobs": read_globalsportsjobs}

# --- Programme ----------------------------------------------------------------

def run_source(s, run, max_age, seen_links):
    kept, dropped = [], []
    try:
        jobs = READERS[s["ats"]](s, run)
    except Exception as exc:  # noqa: BLE001 - une source en panne ne bloque pas les autres
        return s, [], [], f"{type(exc).__name__}: {exc}"[:160], 0
    oldest = (run - timedelta(days=max_age)).isoformat()
    for j in jobs:
        if not j["titre"] or not j["lien"] or j["lien"] in seen_links:
            continue
        j["pays"] = j["pays"] or s.get("pays") if s.get("pays") not in (None, "Monde") else j["pays"]
        if j["pays"] is None:
            j["pays"] = country_of(j["localisation"], None)
        if s.get("pays_filtre") and j["pays"] and j["pays"] != s["pays_filtre"]:
            continue
        if j["pays"] is None:
            j["pays"] = s.get("pays_filtre") or "?"
        ok, why = keep(j, s)
        if ok and s["ats"] == "globalsportsjobs":
            try:
                ok, why = (True, "") if detail_gsj(j) else (False, "GSJ : offre fermée ou sans lien employeur")
            except Exception:  # noqa: BLE001
                ok, why = False, "GSJ : détail illisible"
            if ok and j["lien"] in seen_links:
                continue
        if ok and s["ats"] == "digitalrecruiters":
            try:
                detail_digitalrecruiters(s, j)
                ok, why = keep(j, s)
            except Exception:  # noqa: BLE001
                pass
        if ok and s["ats"] == "workday":
            try:
                detail_workday(s, j)
                if s.get("pays_filtre") and j["pays"] != s["pays_filtre"]:
                    continue
                ok, why = keep(j, s)
            except Exception:  # noqa: BLE001
                pass
        close = re.match(r"clôture (\d{4}-\d{2}-\d{2})", j["_extrait"])
        if ok and close and close.group(1) <= (run + timedelta(days=1)).isoformat():
            ok, why = False, f"clôture le {close.group(1)}"
        if ok and j["date_iso"] and j["date_iso"] < oldest:
            ok, why = False, f"publiée le {j['date_iso']}"
        (kept if ok else dropped).append((j, why))
    return s, kept, dropped, None, len(jobs)


def to_offer(j, s):
    loc = j["localisation"] or s.get("ville", "")
    if j["pays"] not in ("France", "?") and j["pays"] and j["pays"] not in loc and country_of(loc) != j["pays"]:
        loc = f"{loc} ({j['pays']})" if loc else j["pays"]
    o = {"titre": j["titre"], "entreprise": j.get("_entreprise") or s["nom"],
         "categorie": j.get("_categorie") or s.get("categorie", ""), "secteur": s.get("secteur", ""),
         "localisation": loc, "pays": j["pays"] if j["pays"] != "?" else "", "contrat": contract_of(j["titre"], j["_contrat"]),
         "date_iso": j["date_iso"],
         "date_pub": datetime.strptime(j["date_iso"], "%Y-%m-%d").strftime("%d/%m/%Y") if j["date_iso"] else "",
         "lien": j["lien"], "source": f"API {s['ats']} ({s['nom']})", "_extrait": j["_extrait"]}
    if j["_extrait"].startswith("clôture "):
        o["date_pub"] += f" (clôture {datetime.strptime(j['_extrait'][8:18], '%Y-%m-%d'):%d/%m/%Y})"
    return o


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--sources", required=True)
    p.add_argument("--board", required=True)
    p.add_argument("--history")
    p.add_argument("--rejected", help="Liens refusés aux relectures précédentes (défaut : ecartees.txt à côté de --history)")
    p.add_argument("--date", default=date.today().isoformat())
    p.add_argument("--max-age", type=int, default=60)
    p.add_argument("--only", help="Nom d'une source à tester seule")
    p.add_argument("--out", required=True)
    a = p.parse_args()

    run = date.fromisoformat(a.date)
    global run_month
    run_month = (run.year, run.month)
    sources = json.load(open(a.sources, encoding="utf-8"))["sources"]
    if a.only:
        sources = [s for s in sources if norm(a.only) in norm(s["nom"])]
    seen = {o["lien"] for o in json.load(open(a.board, encoding="utf-8"))["offres"]}
    if a.history and Path(a.history).exists():
        seen |= set(re.findall(r"https?://\S+", Path(a.history).read_text(encoding="utf-8")))
    rejected = Path(a.rejected) if a.rejected else (Path(a.history).with_name("ecartees.txt") if a.history else None)
    if rejected and rejected.exists():
        seen |= set(re.findall(r"https?://\S+", rejected.read_text(encoding="utf-8")))

    offers, bilan = [], {"detail_ecartees": [], "portails_steriles": [], "nouveaux_portails": [], "sources": []}
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda s: run_source(s, run, a.max_age, seen), sources))
    for s, kept, dropped, err, total in results:
        if err:
            bilan["portails_steriles"].append(f"{s['nom']} ({s['ats']}) : {err}")
            print(f"  ERREUR  {s['nom']:<38} {err}", file=sys.stderr)
            continue
        offers += [to_offer(j, s) for j, _ in kept]
        bilan["detail_ecartees"] += [f"{j['titre']} - {s['nom']} : {why}" for j, why in dropped]
        bilan["sources"].append({"nom": s["nom"], "offres_lues": total, "retenues": len(kept)})
        print(f"  {len(kept):>3} / {total:<4} {s['nom']}", file=sys.stderr)

    uniq, links, pairs = [], set(), set()
    for o in sorted(offers, key=lambda o: o["date_iso"] or "", reverse=True):
        pair = (o["entreprise"], norm(o["titre"]), o["pays"])
        if o["lien"] not in links and pair not in pairs:
            links.add(o["lien"]); pairs.add(pair); uniq.append(o)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps({"offres": uniq, "bilan": bilan}, ensure_ascii=False, indent=2), encoding="utf-8")
    errors = len(bilan["portails_steriles"])
    print(f"{len(uniq)} offres candidates de {len(sources) - errors} sources ({errors} en erreur) -> {a.out}")


if __name__ == "__main__":
    main()
