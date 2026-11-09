#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Passe LinkedIn connectée de la veille : offres (rubrique Emplois) et posts, lus dans le
navigateur Ego Lite du Mac de Tom, où son compte LinkedIn est ouvert.

Le compte est le vrai profil de Tom, d'où des garde-fous écrits dans le code :
  - lecture seule : le navigateur ne fait qu'ouvrir une page, la faire défiler et la lire.
    Aucun clic, donc ni candidature, ni message, ni alerte, ni réglage ;
  - budget par passage (références ego-requetes.json) : 25 recherches d'offres et 15 de
    posts au plus, une page de résultats par recherche, 5 à 9 s entre deux recherches ;
  - une seule TaskSpace (« veille-ssb-linkedin ») et sa page p1 ;
  - arrêt immédiat sur une vérification, un CAPTCHA ou une déconnexion : le fichier de
    sortie porte alors "bloque" et ce qui a été lu avant.
Les fiches des offres sont lues ensuite par la version publique de LinkedIn
(jobs-guest/jobs/api/jobPosting/<id>), sans le compte.

Sortie : candidates au format du skill, avec `_famille`, `_type` (offre ou post) et
`_extrait`, relues ensuite par un agent comme celles du moissonneur.

Usage :
    python3 ego_linkedin.py --requetes ../references/ego-requetes.json --board data/offres.json \
        --history ../references/historique.md --date 2026-11-09 --out out/candidats/2026-11-09-ego.json
    python3 ego_linkedin.py ... --offres 3 --posts 0     # petit essai
"""

import argparse
import datetime as dt
import html
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from doublons import same_offer, title_key  # noqa: E402
from harvest import contract_of, country_of, keep  # noqa: E402

EGO = "/Users/tom/.local/bin/ego-browser"
SPACE = "veille-ssb-linkedin"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0 Safari/537.36")
BLOCKED_URL = re.compile(r"checkpoint|authwall|/login|/uas/|captcha|challenge|signup", re.I)
BLOCKED_TEXT = re.compile(r"vérification de sécurité|security check|let's do a quick|confirmez que vous|"
                          r"connectez-vous pour|sign in to|rejoignez linkedin", re.I)

# Page de résultats : chargement, contrôle de blocage, défilement à la molette au-dessus de la
# liste, puis lecture. Les fonctions de lecture tournent dans la page (page.evaluate).
JS = r"""
const MODE = __MODE__, URL = __URL__;
const task = await taskSpace("__SPACE__");
const p = task.page("p1");
await p.goto(URL, { timeout: 45000 });
await p.waitForTimeout(3500);
const state = await p.evaluate(() => ({ url: location.href, text: (document.body.innerText || "").slice(0, 3000) }));
let items = [];
const isBlocked = __BLOCKED_URL__.test(state.url) || __BLOCKED_TEXT__.test(state.text.slice(0, 600));
if (!isBlocked) {
  for (let i = 0; i < 5; i++) {
    const box = await p.evaluate((mode) => {
      const sel = mode === "offres" ? '[componentkey^="job-card-component-ref-"]' : 'main [role="listitem"]';
      const all = document.querySelectorAll(sel);
      const last = all[all.length - 1];
      if (!last) return null;
      const r = last.getBoundingClientRect();
      return { x: Math.max(10, r.left + r.width / 2), y: Math.min(window.innerHeight - 20, Math.max(20, r.top + 10)) };
    }, MODE);
    if (!box) break;
    await p.mouse.move(box.x, box.y);
    await p.mouse.wheel(0, 1400, { label: "faire défiler les résultats" });
    await p.waitForTimeout(1100);
  }
  items = await p.evaluate((mode) => {
    if (mode === "offres") {
      const seen = new Map();
      for (const el of document.querySelectorAll('[componentkey^="job-card-component-ref-"]')) {
        const id = el.getAttribute("componentkey").replace("job-card-component-ref-", "");
        if (seen.has(id)) continue;
        const ps = [...el.querySelectorAll("p")].map((x) => x.innerText.trim()).filter(Boolean);
        seen.set(id, { id, ps: ps.slice(0, 8), text: el.innerText.trim().slice(0, 600) });
      }
      return [...seen.values()];
    }
    const out = [];
    for (const it of document.querySelectorAll('main [role="listitem"]')) {
      const t = it.innerText || "";
      if (t.length < 80) continue;
      const author = [...it.querySelectorAll('a[href*="/in/"], a[href*="/company/"]')].map((a) => a.href.split("?")[0])[0] || "";
      const links = [...new Set([...it.querySelectorAll("a[href]")].map((a) => a.href)
        .filter((h) => !/linkedin\.com\/(in|company|school|feed\/hashtag|search|signup|legal)\b|linkedin\.com\/?$/.test(h)))];
      out.push({ author, links: links.slice(0, 8), text: t.slice(0, 2500) });
    }
    return out;
  }, MODE);
}
const fs = await import("node:fs/promises");
await fs.writeFile(__OUT__, JSON.stringify({ url: state.url, blocked: isBlocked, head: state.text.slice(0, 200), items }));
console.log("ok");
"""


def run_page(mode, url):
    script = (JS.replace("__MODE__", json.dumps(mode)).replace("__URL__", json.dumps(url))
              .replace("__SPACE__", SPACE)
              .replace("__BLOCKED_URL__", "/" + BLOCKED_URL.pattern.replace("/", "\\/") + "/i")
              .replace("__BLOCKED_TEXT__", "/" + BLOCKED_TEXT.pattern.replace("/", "\\/") + "/i"))
    # La sortie standard d'ego-browser coupe les longues lignes : le résultat passe par un fichier.
    out = Path(tempfile.gettempdir()) / f"ego-linkedin-{os.getpid()}.json"
    out.unlink(missing_ok=True)
    res = subprocess.run([EGO, "nodejs"], input=script.replace("__OUT__", json.dumps(str(out))),
                         capture_output=True, text=True, timeout=180)
    if not out.exists():
        raise RuntimeError(f"ego-browser sans résultat : {(res.stderr or res.stdout)[-400:]}")
    data = json.loads(out.read_text(encoding="utf-8"))
    out.unlink(missing_ok=True)
    return data


def finish_space():
    subprocess.run([EGO, "nodejs"], input=f'const t = await taskSpace("{SPACE}"); await t.finish({{ keep: [] }});',
                   capture_output=True, text=True, timeout=60)


def jobs_url(keywords, fam):
    q = {"keywords": keywords, "f_TPR": "r1209600"}
    if fam.get("geoId"):
        q["geoId"] = fam["geoId"]
    if fam.get("location"):
        q["location"] = fam["location"]
    return "https://www.linkedin.com/jobs/search-results/?" + urllib.parse.urlencode(q)


def posts_url(keywords):
    return ("https://www.linkedin.com/search/results/content/?" +
            urllib.parse.urlencode({"keywords": keywords, "datePosted": '"past-week"', "sortBy": '"date_posted"'}))


def plan(conf, run, n_offres, n_posts):
    """Recherches du passage : les larges, puis les familles à tour de rôle (rotation par passage)."""
    passage = run.isocalendar()[1] * 2 + (run.weekday() >= 3) + run.year * 200
    jobs = [("larges", q) for q in conf["larges"]]
    fams = list(conf["familles"].items())
    reste = max(0, n_offres - len(jobs))
    par_famille = {name: reste // len(fams) for name, _ in fams}
    for name, _ in fams[: reste % len(fams)]:
        par_famille[name] += 1
    for name, fam in fams:
        reqs, k = fam["requetes"], par_famille[name]
        start = (passage * k) % len(reqs) if reqs else 0
        jobs += [(name, reqs[(start + i) % len(reqs)]) for i in range(min(k, len(reqs)))]
    posts = conf["posts"]
    start = (passage * n_posts) % len(posts) if posts else 0
    return jobs[:n_offres], [posts[(start + i) % len(posts)] for i in range(min(n_posts, len(posts)))]


# --- Fiches publiques -----------------------------------------------------------

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.geturl(), r.read(1_500_000).decode("utf-8", "replace")


def text_of(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"(?s)<[^>]+>", " ", fragment or ""))).strip()


def ago_to_date(text, run):
    """« il y a 3 jours », « 2 weeks ago », « 1 j », « 12 h », « 1 sem. » -> date ISO."""
    t = text.lower()
    m = re.search(r"(\d+)\s*(minute|min|heure|hour|h\b|jour|day|j\b|semaine|week|sem|mois|month|an\b|year)", t)
    if not m:
        return None
    n, unit = int(m.group(1)), m.group(2)
    days = (0 if unit.startswith(("min", "heure", "hour", "h")) else n if unit.startswith(("jour", "day", "j"))
            else 7 * n if unit.startswith(("sem", "week")) else 30 * n if unit.startswith(("mois", "month")) else 365 * n)
    return (run - dt.timedelta(days=days)).isoformat()


def job_detail(job_id, run):
    _, page = fetch(f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}")
    pick = lambda pat: (re.search(pat, page, re.S) or [None, ""])[1]  # noqa: E731
    criteria = dict(zip([text_of(x) for x in re.findall(r'job-criteria-subheader[^>]*>(.*?)</h3>', page, re.S)],
                        [text_of(x) for x in re.findall(r'job-criteria-text[^>]*>(.*?)</span>', page, re.S)]))
    apply = pick(r'<code id="applyUrl"[^>]*><!--"(.*?)"-->')
    if apply:
        apply = urllib.parse.parse_qs(urllib.parse.urlsplit(html.unescape(apply)).query).get("url", [""])[0]
    closed = bool(re.search(r"n.accepte plus de candidatures|no longer accepting applications", page, re.I))
    posted = text_of(pick(r'posted-time-ago__text[^>]*>(.*?)</span>'))
    return {
        "titre": text_of(pick(r'top-card-layout__title[^>]*>(.*?)</h2>')),
        "entreprise": text_of(pick(r'topcard__org-name-link[^>]*>(.*?)</a>')) or text_of(pick(r'topcard__flavor">(.*?)</span>')),
        "localisation": text_of(pick(r'topcard__flavor topcard__flavor--bullet[^>]*>(.*?)</span>')),
        "date_iso": ago_to_date(posted, run), "publie": posted, "criteres": criteria,
        "lien_employeur": apply, "fermee": closed,
        "description": text_of(pick(r'show-more-less-html__markup[^>]*>(.*?)</div>'))[:3500],
    }


def resolve(url):
    """Lien d'un post : décode la redirection de sécurité LinkedIn et les liens courts lnkd.in."""
    if "linkedin.com/safety/go" in url:
        url = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query).get("url", [url])[0]
    if "lnkd.in/" in url:
        try:
            final, page = fetch(url, timeout=15)
            m = re.search(r'data-tracking-control-name="external_url_click"[^>]*href="([^"]+)"', page)
            url = html.unescape(m.group(1)) if m else final
        except Exception:  # noqa: BLE001 - lien court illisible : on le garde tel quel
            pass
    return url


# --- Main ---------------------------------------------------------------------------

def known_ids(paths):
    ids = set()
    for p in paths:
        if p and Path(p).exists():
            ids |= set(re.findall(r"linkedin\.com/jobs/view/(?:[^\s|]*?-)?(\d{8,})", Path(p).read_text(encoding="utf-8")))
    return ids


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--requetes", required=True)
    ap.add_argument("--board", required=True)
    ap.add_argument("--history", required=True)
    ap.add_argument("--rejected", help="ecartees.txt (défaut : à côté de --history)")
    ap.add_argument("--date", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--offres", type=int, help="Nombre de recherches d'offres (défaut : budget du fichier)")
    ap.add_argument("--posts", type=int, help="Nombre de recherches de posts (défaut : budget du fichier)")
    args = ap.parse_args()

    run = dt.date.fromisoformat(args.date)
    conf = json.load(open(args.requetes, encoding="utf-8"))
    n_offres = min(args.offres if args.offres is not None else conf["budget_offres"], conf["budget_offres"])
    n_posts = min(args.posts if args.posts is not None else conf["budget_posts"], conf["budget_posts"])
    jobs_plan, posts_plan = plan(conf, run, n_offres, n_posts)
    rejected = args.rejected or str(Path(args.history).with_name("ecartees.txt"))
    board = json.load(open(args.board, encoding="utf-8"))["offres"]
    seen = known_ids([args.board, args.history, rejected])
    by_title = {}
    for o in board:
        by_title.setdefault(title_key(o["titre"]), []).append(o)

    cards, posts, journal, bloque = {}, [], [], None
    searches = [("offres", fam, q) for fam, q in jobs_plan] + [("posts", "posts", q) for q in posts_plan]
    for i, (mode, fam, q) in enumerate(searches):
        if i:
            time.sleep(random.uniform(5, 9))
        famconf = conf["familles"].get(fam, {})
        url = jobs_url(q, famconf) if mode == "offres" else posts_url(q)
        try:
            res = run_page(mode, url)
        except Exception as exc:  # noqa: BLE001 - une recherche ratée n'arrête pas les autres
            journal.append(f"{mode} | {fam} | {q} | erreur : {exc}")
            continue
        if res["blocked"]:
            bloque = f"LinkedIn a affiché une vérification ou une déconnexion ({res['url']}) à la recherche « {q} »"
            journal.append(bloque)
            break
        journal.append(f"{mode} | {fam} | {q} | {len(res['items'])} résultats")
        for it in res["items"]:
            if mode == "offres":
                c = cards.setdefault(it["id"], {**it, "_familles": []})
                c["_familles"].append(fam)
            else:
                posts.append({**it, "_requete": q})
    finish_space()

    offres, ecartees = [], []
    for job_id, c in cards.items():
        if job_id in seen:
            continue
        ps = c["ps"]
        titre0 = (ps[0].split("\n")[-1] if ps else "").strip()
        try:
            d = job_detail(job_id, run)
            time.sleep(random.uniform(1.0, 2.0))
        except Exception as exc:  # noqa: BLE001
            ecartees.append(f"{titre0} | fiche publique illisible ({exc})")
            continue
        fam = c["_familles"][0]
        pays_force = conf["familles"].get(fam, {}).get("geoId")
        o = {
            "titre": d["titre"] or titre0, "entreprise": d["entreprise"] or (ps[1] if len(ps) > 1 else ""),
            "localisation": d["localisation"] or (ps[2] if len(ps) > 2 else ""),
            "date_iso": d["date_iso"], "lien": f"https://www.linkedin.com/jobs/view/{job_id}",
            "source": "LinkedIn connecté (Ego Lite)",
        }
        o["pays"] = country_of(o["localisation"], None if pays_force else "France") or "?"
        o["contrat"] = contract_of(o["titre"], " ".join(d["criteres"].values()))
        o.update({"_famille": fam, "_type": "offre", "_lien_employeur": d["lien_employeur"],
                  "_criteres": d["criteres"], "_publie": d["publie"], "_extrait": d["description"]})
        if d["fermee"]:
            ecartees.append(f"{o['titre']} - {o['entreprise']} | n'accepte plus de candidatures")
            continue
        if o["date_iso"] and (run - dt.date.fromisoformat(o["date_iso"])).days > 60:
            ecartees.append(f"{o['titre']} - {o['entreprise']} | publiée il y a plus de 60 jours")
            continue
        ok, why = keep({**o, "_niveau": None}, {"filtre": "tout"})
        if not ok:
            ecartees.append(f"{o['titre']} - {o['entreprise']} | {why}")
            continue
        if any(same_offer(o, x) for x in by_title.get(title_key(o["titre"]), [])):
            ecartees.append(f"{o['titre']} - {o['entreprise']} | déjà au tableau")
            continue
        offres.append(o)

    for p in posts:
        t = p["text"]
        when = re.search(r"\n\s*(\d+\s?(?:min|h|j|sem\.?|mois|an))\b", t)
        p["date_iso"] = ago_to_date(when.group(1), run) if when else None
        p["liens"] = [resolve(u) for u in p.pop("links")]
    # Un même post remonte sur plusieurs requêtes.
    uniques = {}
    for p in posts:
        uniques.setdefault((p["author"], p["text"][:200]), p)
    for p in uniques.values():
        offres.append({"titre": "", "entreprise": "", "localisation": "", "pays": "", "contrat": "",
                       "date_iso": p["date_iso"], "lien": "", "source": "Post LinkedIn (Ego Lite)",
                       "_famille": "posts", "_type": "post", "_auteur": p["author"], "_liens": p["liens"],
                       "_requete": p["_requete"], "_extrait": p["text"]})

    out = {"date": args.date, "bloque": bloque, "recherches": journal, "ecartees_auto": ecartees,
           "offres": offres}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    n_off = sum(1 for o in offres if o["_type"] == "offre")
    print(f"{len(journal)} recherches, {len(cards)} offres vues, {n_off} candidates, "
          f"{len(uniques)} posts -> {args.out}" + (f"\nBLOQUÉ : {bloque}" if bloque else ""))
    for line in journal:
        print("  " + line)


if __name__ == "__main__":
    main()
