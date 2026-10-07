#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère une page web consultable de la veille emploi (Sorbonne Sport Business) :
offres triées de la plus récente à la plus ancienne, groupées par jour de
publication, avec recherche et filtres (contrat, catégorie, Île-de-France).

Usage :
    python3 build_page.py offres.json --date 2026-10-07 --out ./out/veille-ssb-2026-10-07.html

Le fichier d'entrée est le même que pour build_outputs.py (ou l'export
offres-<date>.json qu'il produit). Champs utilisés par offre : titre, entreprise,
categorie, secteur, localisation, contrat, date_iso, date_pub (ou infos), lien, source.

Par défaut la page est un fragment HTML (title + style + contenu + script), prêt
à publier comme Artifact Claude. --standalone l'enveloppe dans un document HTML
complet, à ouvrir directement dans un navigateur ou à héberger.
"""

import argparse
import datetime
import html
import json
import re
from pathlib import Path

PAGE = r"""<title>Veille emploi SSB</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&family=Geist+Mono:wght@500&display=swap">
<style>
/* Layout : une colonne de lecture, filtres collants en tête, offres groupées par jour de publication. */
:root {
  --bg: #ffffff;
  --surface: #f4f6f9;
  --ink: #041a35;
  --muted: #566173;
  --line: rgba(4, 26, 53, 0.12);
  --accent: #2660a5;
  --accent-soft: rgba(38, 96, 165, 0.10);
  --stage: #2e7d32;
  --alternance: #1565c0;
  --cdi: #c75400;
  --cdd: #5f6368;
  --freelance: #6a1b9a;
  --warn: #b3261e;
  --warn-soft: rgba(179, 38, 30, 0.09);
  --font: "Hanken Grotesk", "Segoe UI", Helvetica, Arial, sans-serif;
  --mono: "Geist Mono", ui-monospace, "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #02101f; --surface: #062750; --ink: #eef4fb; --muted: #a9bdd3;
    --line: rgba(197, 219, 242, 0.16); --accent: #7ab1e8; --accent-soft: rgba(122, 177, 232, 0.14);
    --stage: #7cc97f; --alternance: #7ab1e8; --cdi: #ffa45c; --cdd: #b5bcc6; --freelance: #c79be0;
    --warn: #ff8a80; --warn-soft: rgba(255, 138, 128, 0.12);
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #02101f; --surface: #062750; --ink: #eef4fb; --muted: #a9bdd3;
  --line: rgba(197, 219, 242, 0.16); --accent: #7ab1e8; --accent-soft: rgba(122, 177, 232, 0.14);
  --stage: #7cc97f; --alternance: #7ab1e8; --cdi: #ffa45c; --cdd: #b5bcc6; --freelance: #c79be0;
  --warn: #ff8a80; --warn-soft: rgba(255, 138, 128, 0.12);
  color-scheme: dark;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font: 400 15px/1.5 var(--font); }
.wrap { max-width: 1080px; margin: 0 auto; padding-inline: 16px; padding-block: 28px 64px; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 4px; }

header.top { display: grid; gap: 10px; padding-bottom: 20px; border-bottom: 1px solid var(--line); }
.org { font: 500 12px/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--accent); }
h1 { margin: 0; font-size: clamp(28px, 5vw, 40px); line-height: 1.1; font-weight: 700; letter-spacing: -0.02em; text-wrap: balance; }
.lede { margin: 0; color: var(--muted); max-width: 62ch; }
.figures { display: flex; flex-wrap: wrap; gap: 8px 22px; margin-top: 4px; font-variant-numeric: tabular-nums; }
.figures span { color: var(--muted); }
.figures b { color: var(--ink); font-weight: 600; }

.filters { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--bg);
  display: grid; gap: 10px; padding-block: 14px; border-bottom: 1px solid var(--line); }
.row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
#q { flex: 1 1 260px; min-width: 0; font: inherit; color: var(--ink); background: var(--surface);
  border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; }
select { font: inherit; color: var(--ink); background: var(--surface); border: 1px solid var(--line);
  border-radius: 10px; padding: 10px 12px; max-width: 100%; }
.chip { font: 500 13px/1 var(--font); color: var(--muted); background: transparent; border: 1px solid var(--line);
  border-radius: 999px; padding: 8px 12px; cursor: pointer; }
.chip[aria-pressed="true"] { color: var(--bg); background: var(--ink); border-color: var(--ink); }
.chip:hover { border-color: var(--ink); }
.status { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px; color: var(--muted); font-size: 13px; }
.linkbtn { background: none; border: 0; padding: 0; font: inherit; color: var(--accent); cursor: pointer; text-decoration: underline; }

.day { margin-top: 26px; }
.day h2 { margin: 0 0 6px; font: 500 12px/1 var(--mono); letter-spacing: .06em; text-transform: uppercase; color: var(--muted);
  display: flex; gap: 10px; align-items: baseline; }
.day h2 .n { color: var(--accent); }
ol.offers { list-style: none; margin: 0; padding: 0; }
.offer { display: grid; grid-template-columns: 96px minmax(0, 1fr) 190px; gap: 6px 18px; align-items: start;
  padding: 14px 0; border-top: 1px solid var(--line); }
.offer:first-child { border-top: 0; }
.ct { font: 600 12px/1 var(--font); letter-spacing: .02em; padding: 6px 0 0; }
.ct::before { content: ""; display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: currentColor; margin-right: 7px; vertical-align: 1px; }
.ct[data-c="Stage"] { color: var(--stage); }
.ct[data-c="Alternance"] { color: var(--alternance); }
.ct[data-c="CDI"] { color: var(--cdi); }
.ct[data-c="CDD"] { color: var(--cdd); }
.ct[data-c="Freelance"] { color: var(--freelance); }
.main { min-width: 0; display: grid; gap: 3px; }
.title { font-weight: 600; font-size: 16px; line-height: 1.35; text-decoration: none; }
.title:hover { color: var(--accent); text-decoration: underline; }
.who { color: var(--ink); }
.who .cat { color: var(--muted); }
.infos { color: var(--muted); font-size: 13.5px; }
.side { display: grid; gap: 4px; justify-items: start; font-size: 13.5px; color: var(--muted); min-width: 0; }
.side .src { font: 500 11.5px/1.3 var(--mono); overflow-wrap: anywhere; }
.flag { font: 600 11.5px/1 var(--font); color: var(--warn); background: var(--warn-soft); border-radius: 6px; padding: 5px 7px; }
.empty { padding: 40px 0; color: var(--muted); }

footer { margin-top: 40px; padding-top: 18px; border-top: 1px solid var(--line); color: var(--muted); font-size: 13.5px; display: grid; gap: 8px; max-width: 75ch; }

@media (max-width: 720px) {
  .offer { grid-template-columns: minmax(0, 1fr); gap: 4px; }
  .ct { padding: 0; }
  .side { display: flex; flex-wrap: wrap; gap: 4px 12px; align-items: center; }
}
@media (prefers-reduced-motion: no-preference) { .chip, .title { transition: color .14s, background-color .14s, border-color .14s; } }
</style>

<div class="wrap">
  <header class="top">
    <div class="org">Sorbonne Sport Business · Veille emploi</div>
    <h1>Offres sport business</h1>
    <p class="lede">Stages, alternances et premiers postes dans l'industrie du sport en France : clubs, ligues, fédérations, marques, agences, médias, institutions, droit et finance. Chaque lien a été ouvert et vérifié le jour de la veille.</p>
    <div class="figures" id="figures"></div>
  </header>

  <section class="filters" aria-label="Filtres">
    <div class="row">
      <label for="q" hidden>Rechercher</label>
      <input id="q" type="search" placeholder="Rechercher un poste, un employeur, une ville…" autocomplete="off">
      <label for="cat" hidden>Catégorie</label>
      <select id="cat"><option value="">Toutes les catégories</option></select>
    </div>
    <div class="row" role="group" aria-label="Type de contrat" id="contracts"></div>
    <div class="row" role="group" aria-label="Zone et fraîcheur">
      <button class="chip" id="idf" aria-pressed="false" type="button">Île-de-France</button>
      <button class="chip" id="week" aria-pressed="false" type="button">Publiées ces 7 derniers jours</button>
      <button class="chip" id="soon" aria-pressed="false" type="button">Clôture dans les 10 jours</button>
    </div>
    <div class="status"><span id="count" aria-live="polite"></span><button class="linkbtn" id="reset" type="button">Tout afficher</button></div>
  </section>

  <main id="list"></main>

  <footer>
    <p>Règles de la veille : offres non expirées, vérifiées sur leur page individuelle, publiées depuis moins de deux mois, deux offres au maximum par employeur, lien vers le site de l'employeur dès qu'il existe.</p>
    <p id="meta"></p>
  </footer>
</div>

<script type="application/json" id="data">__DATA__</script>
<script>
(function () {
  const RUN = "__RUN__";
  const offers = JSON.parse(document.getElementById("data").textContent);
  const runDate = new Date(RUN + "T12:00:00");
  const IDF = /\((75|77|78|91|92|93|94|95)\)|Paris|Île-de-France/i;
  const MONTHS = ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"];
  const DAYS = ["dimanche","lundi","mardi","mercredi","jeudi","vendredi","samedi"];
  const CONTRACTS = ["Stage", "Alternance", "CDI", "CDD", "Freelance"];
  const state = { q: "", cat: "", contracts: new Set(), idf: false, week: false, soon: false };

  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const norm = s => String(s ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const daysBetween = (a, b) => Math.round((b - a) / 86400000);

  // Date de clôture lue dans le texte libre ("clôture 30/11/2026", "jusqu'au 09/10").
  function closing(o) {
    const m = /(cl[ôo]ture|jusqu'au|valable jusqu'au)\s*(?:le\s*)?(\d{2})\/(\d{2})(?:\/(\d{4}))?/i.exec(o.infos || "");
    if (!m) return null;
    const d = new Date(Number(m[4] || runDate.getFullYear()), Number(m[3]) - 1, Number(m[2]), 12);
    return isNaN(d) ? null : d;
  }
  offers.forEach(o => {
    o._pub = o.date_iso ? new Date(o.date_iso + "T12:00:00") : null;
    o._close = closing(o);
    o._hay = norm([o.titre, o.entreprise, o.categorie, o.secteur, o.localisation, o.contrat, o.source].join(" "));
  });

  // Filtres
  const cats = [...new Set(offers.map(o => o.categorie).filter(Boolean))].sort((a, b) => a.localeCompare(b, "fr"));
  const catSel = document.getElementById("cat");
  cats.forEach(c => catSel.insertAdjacentHTML("beforeend", `<option value="${esc(c)}">${esc(c)} (${offers.filter(o => o.categorie === c).length})</option>`));
  const cBox = document.getElementById("contracts");
  CONTRACTS.filter(c => offers.some(o => o.contrat === c)).forEach(c => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip"; b.setAttribute("aria-pressed", "false");
    b.textContent = `${c} · ${offers.filter(o => o.contrat === c).length}`;
    b.addEventListener("click", () => { state.contracts.has(c) ? state.contracts.delete(c) : state.contracts.add(c); b.setAttribute("aria-pressed", state.contracts.has(c)); render(); });
    cBox.appendChild(b);
  });
  const toggle = (id, key) => { const b = document.getElementById(id); b.addEventListener("click", () => { state[key] = !state[key]; b.setAttribute("aria-pressed", state[key]); render(); }); };
  toggle("idf", "idf"); toggle("week", "week"); toggle("soon", "soon");
  document.getElementById("q").addEventListener("input", e => { state.q = norm(e.target.value.trim()); render(); });
  catSel.addEventListener("change", e => { state.cat = e.target.value; render(); });
  document.getElementById("reset").addEventListener("click", () => {
    Object.assign(state, { q: "", cat: "", idf: false, week: false, soon: false }); state.contracts.clear();
    document.getElementById("q").value = ""; catSel.value = "";
    document.querySelectorAll(".chip").forEach(b => b.setAttribute("aria-pressed", "false"));
    render();
  });

  const soonDays = o => o._close ? daysBetween(runDate, o._close) : null;
  function match(o) {
    if (state.q && !state.q.split(/\s+/).every(t => o._hay.includes(t))) return false;
    if (state.cat && o.categorie !== state.cat) return false;
    if (state.contracts.size && !state.contracts.has(o.contrat)) return false;
    if (state.idf && !IDF.test(o.localisation || "")) return false;
    if (state.week && !(o._pub && daysBetween(o._pub, runDate) <= 7)) return false;
    if (state.soon) { const d = soonDays(o); if (d === null || d < 0 || d > 10) return false; }
    return true;
  }
  const dayLabel = d => {
    if (!d) return "Date de publication non communiquée";
    const ago = daysBetween(d, runDate);
    const base = `${DAYS[d.getDay()]} ${d.getDate()} ${MONTHS[d.getMonth()]}`;
    return ago === 0 ? `Aujourd'hui · ${base}` : ago === 1 ? `Hier · ${base}` : base;
  };

  function render() {
    const shown = offers.filter(match);
    const groups = new Map();
    shown.forEach(o => { const k = o.date_iso || "zzz"; if (!groups.has(k)) groups.set(k, []); groups.get(k).push(o); });
    const keys = [...groups.keys()].sort().reverse().sort((a, b) => (a === "zzz") - (b === "zzz"));
    const list = document.getElementById("list");
    if (!shown.length) { list.innerHTML = `<p class="empty">Aucune offre ne correspond à ces filtres. Retirez-en un ou cliquez sur « Tout afficher ».</p>`; }
    else list.innerHTML = keys.map(k => {
      const items = groups.get(k);
      return `<section class="day"><h2><span>${esc(dayLabel(items[0]._pub))}</span><span class="n">${items.length}</span></h2><ol class="offers">${items.map(o => {
        const d = soonDays(o);
        const flag = d !== null && d >= 0 && d <= 10 ? `<span class="flag">${d === 0 ? "Clôture aujourd'hui" : `Clôture dans ${d} j`}</span>` : "";
        return `<li class="offer">
          <span class="ct" data-c="${esc(o.contrat)}">${esc(o.contrat)}</span>
          <div class="main">
            <a class="title" href="${esc(o.lien)}" target="_blank" rel="noopener">${esc(o.titre)}</a>
            <div class="who">${esc(o.entreprise)}${o.categorie ? ` <span class="cat">· ${esc(o.categorie)}</span>` : ""}</div>
            ${o.infos ? `<div class="infos">${esc(o.infos)}</div>` : ""}
          </div>
          <div class="side"><span>${esc(o.localisation)}</span>${flag}<span class="src">${esc(o.source)}</span></div>
        </li>`; }).join("")}</ol></section>`;
    }).join("");
    document.getElementById("count").textContent = `${shown.length} offre${shown.length > 1 ? "s" : ""} sur ${offers.length}`;
  }

  const employers = new Set(offers.map(o => o.entreprise)).size;
  const week = offers.filter(o => o._pub && daysBetween(o._pub, runDate) <= 7).length;
  const stages = offers.filter(o => o.contrat === "Stage").length;
  document.getElementById("figures").innerHTML =
    `<span><b>${offers.length}</b> offres</span><span><b>${employers}</b> employeurs</span><span><b>${stages}</b> stages</span><span><b>${week}</b> publiées ces 7 derniers jours</span>`;
  document.getElementById("meta").textContent = `Veille du ${runDate.getDate()} ${MONTHS[runDate.getMonth()]} ${runDate.getFullYear()}. Les offres changent vite : vérifiez la date limite sur la page de l'employeur avant de postuler.`;
  render();
})();
</script>
"""

STANDALONE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{page_head}
</head>
<body>
{page_body}
</body>
</html>
"""


def infos(offer):
    """Début / clôture : champ `infos`, sinon le contenu entre parenthèses de date_pub."""
    if offer.get("infos"):
        return offer["infos"]
    m = re.search(r"\((.*)\)", offer.get("date_pub", ""))
    return m.group(1) if m else ""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", help="offres.json (même format que build_outputs.py)")
    parser.add_argument("--date", help="Date de la veille AAAA-MM-JJ (défaut : aujourd'hui)")
    parser.add_argument("--out", required=True, help="Fichier HTML à écrire")
    parser.add_argument("--standalone", action="store_true", help="Document HTML complet")
    args = parser.parse_args()

    data = json.load(open(args.input_json, encoding="utf-8"))
    run = args.date or data.get("date_execution") or datetime.date.today().isoformat()
    keep = ("titre", "entreprise", "categorie", "secteur", "localisation", "contrat", "date_iso", "lien", "source")
    offers = [{**{k: o.get(k, "") for k in keep}, "infos": infos(o)} for o in data.get("offres", [])]
    offers.sort(key=lambda o: o.get("date_iso") or "", reverse=True)

    payload = json.dumps(offers, ensure_ascii=False).replace("</", "<\\/")
    page = PAGE.replace("__DATA__", payload).replace("__RUN__", html.escape(run))
    if args.standalone:
        head_end = page.index("</style>") + len("</style>")
        page = STANDALONE.format(page_head=page[:head_end], page_body=page[head_end:])

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"Page générée : {out} ({len(offers)} offres)")


if __name__ == "__main__":
    main()
