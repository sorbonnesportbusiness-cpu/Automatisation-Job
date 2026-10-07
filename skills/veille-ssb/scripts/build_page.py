#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère la page web de la veille emploi (Sorbonne Sport Business) : tableau des
offres trié de la plus récente à la plus ancienne, recherche, filtres, tri par
colonne, lien écrit en entier, sélection d'offres et message WhatsApp prêt à
envoyer aux adhérents.

Usage :
    python3 build_page.py offres.json --date 2026-10-07 --out ./out/veille-ssb.html \
        [--standalone] [--downloads] [--schedule "le lundi et le jeudi à 8 h"] \
        [--sheet-url https://docs.google.com/spreadsheets/d/...] [--site-url https://...]

Le fichier d'entrée est le même que pour build_outputs.py (ou data/offres.json).
Champs utilisés par offre : titre, entreprise, categorie, secteur, localisation,
contrat, date_iso, ajoutee_le, date_pub (ou infos), lien, source.

Sans --standalone, la page est un fragment HTML prêt à publier comme Artifact Claude.
--downloads ajoute les boutons Excel / Google Sheets / CSV (page hébergée avec
veille-ssb.xlsx et offres.csv à côté).
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
/* Layout : outil de travail. En-tête et actions, filtres collants, tableau dense, barre de sélection en bas. */
:root {
  --bg: #ffffff;
  --surface: #f3f5f8;
  --ink: #041a35;
  --muted: #566173;
  --line: rgba(4, 26, 53, 0.12);
  --accent: #2660a5;
  --accent-ink: #ffffff;
  --accent-soft: rgba(38, 96, 165, 0.10);
  --row-sel: rgba(38, 96, 165, 0.07);
  --stage: #2e7d32;
  --alternance: #1565c0;
  --cdi: #c75400;
  --cdd: #5f6368;
  --freelance: #6a1b9a;
  --warn: #b3261e;
  --warn-soft: rgba(179, 38, 30, 0.09);
  --wa: #128c4b;
  --font: "Hanken Grotesk", "Segoe UI", Helvetica, Arial, sans-serif;
  --mono: "Geist Mono", ui-monospace, "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #02101f; --surface: #062750; --ink: #eef4fb; --muted: #a9bdd3;
    --line: rgba(197, 219, 242, 0.16); --accent: #7ab1e8; --accent-ink: #02101f; --accent-soft: rgba(122, 177, 232, 0.14);
    --row-sel: rgba(122, 177, 232, 0.10);
    --stage: #7cc97f; --alternance: #7ab1e8; --cdi: #ffa45c; --cdd: #b5bcc6; --freelance: #c79be0;
    --warn: #ff8a80; --warn-soft: rgba(255, 138, 128, 0.12); --wa: #4fd18b;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #02101f; --surface: #062750; --ink: #eef4fb; --muted: #a9bdd3;
  --line: rgba(197, 219, 242, 0.16); --accent: #7ab1e8; --accent-ink: #02101f; --accent-soft: rgba(122, 177, 232, 0.14);
  --row-sel: rgba(122, 177, 232, 0.10);
  --stage: #7cc97f; --alternance: #7ab1e8; --cdi: #ffa45c; --cdd: #b5bcc6; --freelance: #c79be0;
  --warn: #ff8a80; --warn-soft: rgba(255, 138, 128, 0.12); --wa: #4fd18b;
  color-scheme: dark;
}
* { box-sizing: border-box; }
[hidden] { display: none !important; }
body { background: var(--bg); color: var(--ink); font: 400 14.5px/1.45 var(--font); }
.wrap { max-width: 1480px; margin: 0 auto; padding-inline: 16px; padding-block: 24px 120px; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 4px; }
button { font: inherit; }

header.top { display: grid; gap: 8px; padding-bottom: 16px; }
.org { font: 500 12px/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--accent); }
.headrow { display: flex; flex-wrap: wrap; gap: 12px 24px; align-items: flex-end; justify-content: space-between; }
h1 { margin: 0; font-size: clamp(26px, 4vw, 36px); line-height: 1.1; font-weight: 700; letter-spacing: -0.02em; text-wrap: balance; }
.figures { display: flex; flex-wrap: wrap; gap: 6px 20px; font-variant-numeric: tabular-nums; color: var(--muted); }
.figures b { color: var(--ink); font-weight: 600; }
.actions { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.btn { font: 600 14px/1 var(--font); text-decoration: none; color: var(--ink); background: transparent; border: 1px solid var(--line);
  border-radius: 10px; padding: 10px 13px; cursor: pointer; display: inline-flex; gap: 8px; align-items: center; white-space: nowrap; }
.btn:hover { border-color: var(--ink); }
.btn.primary { color: var(--accent-ink); background: var(--accent); border-color: var(--accent); }
.btn.primary:hover { filter: brightness(1.08); }
.btn.wa { color: #ffffff; background: var(--wa); border-color: var(--wa); }
.btn[disabled] { opacity: .45; cursor: not-allowed; }
.count-pill { font: 600 12px/1 var(--font); background: rgba(255,255,255,.22); border-radius: 999px; padding: 3px 7px; }
.gs { display: grid; gap: 8px; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 14px; max-width: 80ch; }
.gs ol { margin: 0; padding-left: 20px; display: grid; gap: 6px; }
.gs code { font: 500 12.5px/1.4 var(--mono); overflow-wrap: anywhere; background: var(--bg); border: 1px solid var(--line); border-radius: 6px; padding: 2px 6px; }

.filters { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--bg);
  display: grid; gap: 8px; padding-block: 12px; border-block: 1px solid var(--line); }
.row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
#q { flex: 1 1 280px; min-width: 0; font: inherit; color: var(--ink); background: var(--surface);
  border: 1px solid var(--line); border-radius: 10px; padding: 9px 12px; }
select { font: inherit; color: var(--ink); background: var(--surface); border: 1px solid var(--line);
  border-radius: 10px; padding: 9px 12px; max-width: 100%; }
.chip { font: 500 13px/1 var(--font); color: var(--muted); background: transparent; border: 1px solid var(--line);
  border-radius: 999px; padding: 7px 11px; cursor: pointer; }
.chip[aria-pressed="true"] { color: var(--bg); background: var(--ink); border-color: var(--ink); }
.chip:hover { border-color: var(--ink); }
.status { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px; color: var(--muted); font-size: 13px; }
.linkbtn { background: none; border: 0; padding: 0; font: inherit; color: var(--accent); cursor: pointer; text-decoration: underline; }

.tablewrap { overflow-x: auto; margin-top: 4px; }
table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
thead th { position: sticky; top: 0; text-align: left; font: 600 12px/1.2 var(--font); letter-spacing: .02em; color: var(--muted);
  padding: 10px 10px; border-bottom: 1px solid var(--line); background: var(--bg); white-space: nowrap; }
th button.sort { all: unset; cursor: pointer; display: inline-flex; gap: 4px; align-items: center; }
th button.sort:focus-visible { outline: 2px solid var(--accent); }
th button.sort[data-dir]::after { content: attr(data-arrow); color: var(--accent); }
tbody td { padding: 10px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
tbody tr:hover { background: var(--surface); }
tbody tr.sel { background: var(--row-sel); }
td.ck, th.ck { width: 34px; padding-right: 0; }
input[type="checkbox"] { width: 17px; height: 17px; accent-color: var(--accent); cursor: pointer; margin: 2px 0 0; }
td.date { white-space: nowrap; color: var(--muted); }
.ct { font: 600 12.5px/1.3 var(--font); white-space: nowrap; }
.ct::before { content: ""; display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: currentColor; margin-right: 6px; vertical-align: 1px; }
.ct[data-c="Stage"] { color: var(--stage); }
.ct[data-c="Alternance"] { color: var(--alternance); }
.ct[data-c="CDI"] { color: var(--cdi); }
.ct[data-c="CDD"] { color: var(--cdd); }
.ct[data-c="Freelance"] { color: var(--freelance); }
td.poste { min-width: 240px; max-width: 360px; }
.title { font-weight: 600; text-decoration: none; }
.title:hover { color: var(--accent); text-decoration: underline; }
.new { display: inline-block; margin-left: 6px; font: 600 11px/1 var(--font); color: var(--accent); background: var(--accent-soft); border-radius: 5px; padding: 3px 6px; vertical-align: 1px; }
td.emp { min-width: 150px; max-width: 220px; }
td.cat { color: var(--muted); min-width: 120px; }
td.lieu { min-width: 120px; }
td.infos { color: var(--muted); min-width: 150px; max-width: 220px; }
.flag { display: inline-block; margin-top: 4px; font: 600 11.5px/1 var(--font); color: var(--warn); background: var(--warn-soft); border-radius: 5px; padding: 4px 6px; }
td.url { min-width: 220px; max-width: 300px; }
.url a { font: 500 11.5px/1.45 var(--mono); color: var(--accent); overflow-wrap: anywhere; word-break: break-all; }
.copy { margin-top: 4px; background: none; border: 0; padding: 0; color: var(--muted); font: 500 12px/1 var(--font); cursor: pointer; text-decoration: underline; }
.copy:hover { color: var(--ink); }
.empty { padding: 40px 0; color: var(--muted); }

.selbar { position: fixed; left: 0; right: 0; bottom: 0; z-index: 10; background: var(--ink); color: var(--bg);
  padding: 12px 16px calc(12px + env(safe-area-inset-bottom, 0px)); display: flex; flex-wrap: wrap; gap: 10px 16px; align-items: center; justify-content: center; }
.selbar .btn { color: var(--bg); border-color: rgba(255,255,255,.35); }
.selbar .btn.wa { border-color: var(--wa); color: #ffffff; }
.selbar .linkbtn { color: var(--bg); }

dialog { width: min(760px, calc(100vw - 32px)); max-height: calc(100vh - 48px); border: 1px solid var(--line); border-radius: 16px;
  padding: 0; background: var(--bg); color: var(--ink); }
dialog::backdrop { background: rgba(2, 16, 31, .55); }
.dlg { display: grid; gap: 12px; padding: 20px; }
.dlg h2 { margin: 0; font-size: 20px; }
.dlg p { margin: 0; color: var(--muted); }
.dlg label { font-weight: 600; font-size: 13px; }
.dlg textarea { width: 100%; min-height: 46vh; resize: vertical; font: 400 14px/1.5 var(--font); color: var(--ink); background: var(--surface);
  border: 1px solid var(--line); border-radius: 10px; padding: 12px; }
.dlg input[type="text"] { width: 100%; font: inherit; color: var(--ink); background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 9px 12px; }
.dlg .opts { display: flex; flex-wrap: wrap; gap: 8px 18px; align-items: center; color: var(--muted); font-size: 13.5px; }
.dlg .opts label { font-weight: 500; display: inline-flex; gap: 6px; align-items: center; }
.dlg .foot { display: flex; flex-wrap: wrap; gap: 8px; justify-content: space-between; align-items: center; }
.dlg .foot .actions { justify-content: flex-end; }
.hint { color: var(--muted); font-size: 12.5px; }

footer { margin-top: 32px; padding-top: 16px; border-top: 1px solid var(--line); color: var(--muted); font-size: 13.5px; display: grid; gap: 8px; max-width: 80ch; }

/* Téléphone : chaque ligne devient une fiche. */
@media (max-width: 860px) {
  .filters { position: static; }
  thead { display: none; }
  table, tbody, tr, td { display: block; width: 100%; }
  tbody tr { position: relative; padding: 12px 0 12px 34px; border-bottom: 1px solid var(--line); }
  tbody td { border: 0; padding: 2px 0; max-width: none; min-width: 0; }
  td.ck { position: absolute; left: 0; top: 12px; width: auto; }
  td.date::before { content: "Publiée le "; }
  td.cat { display: none; }
  td.url { padding-top: 6px; }
}
@media (prefers-reduced-motion: no-preference) { .chip, .title, .btn { transition: color .14s, background-color .14s, border-color .14s; } }
</style>

<div class="wrap">
  <header class="top">
    <div class="org">Sorbonne Sport Business · Veille emploi</div>
    <div class="headrow">
      <div style="display:grid;gap:8px;min-width:0">
        <h1>Offres sport business</h1>
        <div class="figures" id="figures"></div>
      </div>
      <div class="actions">
__DOWNLOADS__
        <button class="btn primary" id="msg-open" type="button" disabled>Message adhérents <span class="count-pill" id="msg-count">0</span></button>
      </div>
    </div>
__GSHELP__
  </header>

  <section class="filters" aria-label="Filtres">
    <div class="row">
      <label for="q" hidden>Rechercher</label>
      <input id="q" type="search" placeholder="Rechercher un poste, un employeur, une ville…" autocomplete="off">
      <label for="cat" hidden>Catégorie</label>
      <select id="cat"><option value="">Toutes les catégories</option></select>
    </div>
    <div class="row" role="group" aria-label="Filtres rapides">
      <span id="contracts" class="row"></span>
      <button class="chip" id="idf" aria-pressed="false" type="button">Île-de-France</button>
      <button class="chip" id="fresh" aria-pressed="false" type="button" hidden>Nouvelles</button>
      <button class="chip" id="week" aria-pressed="false" type="button">Publiées ces 7 derniers jours</button>
      <button class="chip" id="soon" aria-pressed="false" type="button">Clôture dans les 10 jours</button>
    </div>
    <div class="status"><span id="count" aria-live="polite"></span><button class="linkbtn" id="reset" type="button">Effacer les filtres</button></div>
  </section>

  <div class="tablewrap">
    <table>
      <thead><tr>
        <th class="ck"><input type="checkbox" id="all" aria-label="Sélectionner les offres affichées"></th>
        <th><button class="sort" data-key="date" type="button">Publiée le</button></th>
        <th><button class="sort" data-key="contrat" type="button">Contrat</button></th>
        <th><button class="sort" data-key="titre" type="button">Poste</button></th>
        <th><button class="sort" data-key="entreprise" type="button">Employeur</button></th>
        <th><button class="sort" data-key="categorie" type="button">Catégorie</button></th>
        <th><button class="sort" data-key="localisation" type="button">Lieu</button></th>
        <th>Début / clôture</th>
        <th>Lien de l'offre</th>
      </tr></thead>
      <tbody id="rows"></tbody>
    </table>
  </div>
  <p class="empty" id="empty" hidden>Aucune offre ne correspond à ces filtres. Cliquez sur « Effacer les filtres ».</p>

  <footer>
    <p>Règles de la veille : offres non expirées, vérifiées sur leur page individuelle, publiées depuis moins de deux mois, cinq offres au maximum par employeur, lien vers le site de l'employeur dès qu'il existe.</p>
    <p id="meta"></p>
  </footer>
</div>

<div class="selbar" id="selbar" hidden>
  <span id="sel-text"></span>
  <button class="btn wa" id="msg-open-2" type="button">Préparer le message WhatsApp</button>
  <button class="linkbtn" id="sel-clear" type="button">Tout désélectionner</button>
</div>

<dialog id="msg" aria-labelledby="msg-title">
  <div class="dlg">
    <h2 id="msg-title">Message pour les adhérents</h2>
    <p>Le message reprend les offres cochées. Relisez-le, modifiez-le si besoin, puis copiez-le ou ouvrez WhatsApp pour choisir le groupe.</p>
    <div>
      <label for="msg-intro">Phrase d'introduction</label>
      <input type="text" id="msg-intro">
    </div>
    <div class="opts">
      <label><input type="checkbox" id="msg-link" checked> Ajouter le lien vers toutes les offres</label>
      <label><input type="checkbox" id="msg-infos" checked> Afficher début et clôture</label>
    </div>
    <label for="msg-text">Message</label>
    <textarea id="msg-text"></textarea>
    <div class="foot">
      <span class="hint" id="msg-len"></span>
      <div class="actions">
        <button class="btn" id="msg-close" type="button">Fermer</button>
        <button class="btn" id="msg-copy" type="button">Copier le message</button>
        <a class="btn wa" id="msg-wa" href="#" target="_blank" rel="noopener">Ouvrir dans WhatsApp</a>
      </div>
    </div>
  </div>
</dialog>

<script type="application/json" id="data">__DATA__</script>
<script>
(function () {
  const RUN = "__RUN__";
  const SCHEDULE = "__SCHEDULE__";
  const SITE = "__SITE__" || (location.protocol.startsWith("http") ? location.origin + location.pathname.replace(/[^/]*$/, "") : "");
  const offers = JSON.parse(document.getElementById("data").textContent);
  const runDate = new Date(RUN + "T12:00:00");
  const IDF = /\((75|77|78|91|92|93|94|95)\)|Paris|Île-de-France/i;
  const MONTHS = ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"];
  const DAYS = ["dimanche","lundi","mardi","mercredi","jeudi","vendredi","samedi"];
  const CONTRACTS = ["Stage", "Alternance", "CDI", "CDD", "Freelance"];
  const state = { q: "", cat: "", contracts: new Set(), idf: false, week: false, soon: false, fresh: false, sort: "date", dir: -1 };
  const $ = id => document.getElementById(id);

  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const norm = s => String(s ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const daysBetween = (a, b) => Math.round((b - a) / 86400000);
  const fmt = d => d ? `${String(d.getDate()).padStart(2, "0")}/${String(d.getMonth() + 1).padStart(2, "0")}/${d.getFullYear()}` : "n.c.";

  function closing(o) {
    const m = /(cl[ôo]ture|jusqu'au)\s*(?:le\s*)?(\d{2})\/(\d{2})(?:\/(\d{4}))?/i.exec(o.infos || "");
    if (!m) return null;
    const d = new Date(Number(m[4] || runDate.getFullYear()), Number(m[3]) - 1, Number(m[2]), 12);
    return isNaN(d) ? null : d;
  }
  offers.forEach((o, i) => {
    o._i = i;
    o._pub = o.date_iso ? new Date(o.date_iso + "T12:00:00") : null;
    o._close = closing(o);
    o._hay = norm([o.titre, o.entreprise, o.categorie, o.secteur, o.localisation, o.contrat, o.source, o.infos].join(" "));
  });
  const isNew = o => o.ajoutee_le === RUN;
  const nNew = offers.filter(isNew).length;
  const showNew = nNew > 0 && nNew < offers.length;
  const soonDays = o => o._close ? daysBetween(runDate, o._close) : null;

  // Sélection, gardée dans ce navigateur d'une visite à l'autre.
  const KEY = "ssb-veille-selection";
  let selected = new Set();
  try { selected = new Set(JSON.parse(localStorage.getItem(KEY) || "[]").filter(l => offers.some(o => o.lien === l))); } catch {}
  const saveSel = () => { try { localStorage.setItem(KEY, JSON.stringify([...selected])); } catch {} };

  // Filtres
  const cats = [...new Set(offers.map(o => o.categorie).filter(Boolean))].sort((a, b) => a.localeCompare(b, "fr"));
  cats.forEach(c => $("cat").insertAdjacentHTML("beforeend", `<option value="${esc(c)}">${esc(c)} (${offers.filter(o => o.categorie === c).length})</option>`));
  CONTRACTS.filter(c => offers.some(o => o.contrat === c)).forEach(c => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip"; b.setAttribute("aria-pressed", "false");
    b.textContent = `${c} · ${offers.filter(o => o.contrat === c).length}`;
    b.addEventListener("click", () => { state.contracts.has(c) ? state.contracts.delete(c) : state.contracts.add(c); b.setAttribute("aria-pressed", state.contracts.has(c)); render(); });
    $("contracts").appendChild(b);
  });
  const toggle = (id, key) => $(id).addEventListener("click", e => { state[key] = !state[key]; e.currentTarget.setAttribute("aria-pressed", state[key]); render(); });
  ["idf", "week", "soon", "fresh"].forEach(k => toggle(k, k));
  if (showNew) { $("fresh").hidden = false; $("fresh").textContent = `Nouvelles depuis la dernière veille · ${nNew}`; }
  $("q").addEventListener("input", e => { state.q = norm(e.target.value.trim()); render(); });
  $("cat").addEventListener("change", e => { state.cat = e.target.value; render(); });
  $("reset").addEventListener("click", () => {
    Object.assign(state, { q: "", cat: "", idf: false, week: false, soon: false, fresh: false }); state.contracts.clear();
    $("q").value = ""; $("cat").value = "";
    document.querySelectorAll(".chip").forEach(b => b.setAttribute("aria-pressed", "false"));
    render();
  });

  function match(o) {
    if (state.q && !state.q.split(/\s+/).every(t => o._hay.includes(t))) return false;
    if (state.cat && o.categorie !== state.cat) return false;
    if (state.contracts.size && !state.contracts.has(o.contrat)) return false;
    if (state.idf && !IDF.test(o.localisation || "")) return false;
    if (state.fresh && !isNew(o)) return false;
    if (state.week && !(o._pub && daysBetween(o._pub, runDate) <= 7)) return false;
    if (state.soon) { const d = soonDays(o); if (d === null || d < 0 || d > 10) return false; }
    return true;
  }

  // Tri par colonne
  const sorters = {
    date: (a, b) => (a.date_iso || "").localeCompare(b.date_iso || ""),
    contrat: (a, b) => CONTRACTS.indexOf(a.contrat) - CONTRACTS.indexOf(b.contrat),
  };
  document.querySelectorAll("button.sort").forEach(b => b.addEventListener("click", () => {
    const k = b.dataset.key;
    state.dir = state.sort === k ? -state.dir : (k === "date" ? -1 : 1);
    state.sort = k; render();
  }));
  function sorted(list) {
    const k = state.sort;
    const cmp = sorters[k] || ((a, b) => String(a[k] || "").localeCompare(String(b[k] || ""), "fr", { sensitivity: "base" }));
    return list.slice().sort((a, b) => (cmp(a, b) * state.dir) || (b.date_iso || "").localeCompare(a.date_iso || "") || a._i - b._i);
  }

  let shown = [];
  function render() {
    shown = sorted(offers.filter(match));
    $("rows").innerHTML = shown.map(o => {
      const d = soonDays(o);
      const flag = d !== null && d >= 0 && d <= 10 ? `<div><span class="flag">${d === 0 ? "Clôture aujourd'hui" : `Clôture dans ${d} j`}</span></div>` : "";
      const on = selected.has(o.lien);
      return `<tr class="${on ? "sel" : ""}" data-i="${o._i}">
        <td class="ck"><input type="checkbox" class="pick" ${on ? "checked" : ""} aria-label="Sélectionner : ${esc(o.titre)}"></td>
        <td class="date">${fmt(o._pub)}</td>
        <td><span class="ct" data-c="${esc(o.contrat)}">${esc(o.contrat)}</span></td>
        <td class="poste"><a class="title" href="${esc(o.lien)}" target="_blank" rel="noopener">${esc(o.titre)}</a>${showNew && isNew(o) ? `<span class="new">Nouvelle</span>` : ""}</td>
        <td class="emp">${esc(o.entreprise)}</td>
        <td class="cat">${esc(o.categorie)}</td>
        <td class="lieu">${esc(o.localisation)}</td>
        <td class="infos">${esc(o.infos)}${flag}</td>
        <td class="url"><a href="${esc(o.lien)}" target="_blank" rel="noopener">${esc(o.lien)}</a><div><button class="copy" type="button">Copier le lien</button></div></td>
      </tr>`;
    }).join("");
    $("empty").hidden = shown.length > 0;
    $("count").textContent = `${shown.length} offre${shown.length > 1 ? "s" : ""} sur ${offers.length}`;
    document.querySelectorAll("button.sort").forEach(b => {
      if (b.dataset.key === state.sort) { b.dataset.dir = state.dir; b.dataset.arrow = state.dir < 0 ? "↓" : "↑"; } else { delete b.dataset.dir; }
    });
    syncSel();
  }

  function syncSel() {
    const n = selected.size;
    $("msg-count").textContent = n;
    $("msg-open").disabled = n === 0;
    $("selbar").hidden = n === 0;
    $("sel-text").textContent = `${n} offre${n > 1 ? "s" : ""} sélectionnée${n > 1 ? "s" : ""}`;
    const vis = shown.filter(o => selected.has(o.lien)).length;
    $("all").checked = shown.length > 0 && vis === shown.length;
    $("all").indeterminate = vis > 0 && vis < shown.length;
  }
  $("rows").addEventListener("change", e => {
    if (!e.target.classList.contains("pick")) return;
    const tr = e.target.closest("tr"); const o = offers[Number(tr.dataset.i)];
    e.target.checked ? selected.add(o.lien) : selected.delete(o.lien);
    tr.classList.toggle("sel", e.target.checked); saveSel(); syncSel();
  });
  $("rows").addEventListener("click", async e => {
    if (!e.target.classList.contains("copy")) return;
    const o = offers[Number(e.target.closest("tr").dataset.i)];
    try { await navigator.clipboard.writeText(o.lien); e.target.textContent = "Lien copié"; }
    catch { const r = document.createRange(); r.selectNodeContents(e.target.closest("td").querySelector("a")); const s = getSelection(); s.removeAllRanges(); s.addRange(r); e.target.textContent = "Lien sélectionné"; }
    setTimeout(() => { e.target.textContent = "Copier le lien"; }, 1800);
  });
  $("all").addEventListener("change", e => { shown.forEach(o => e.target.checked ? selected.add(o.lien) : selected.delete(o.lien)); saveSel(); render(); });
  $("sel-clear").addEventListener("click", () => { selected.clear(); saveSel(); render(); });

  // Message WhatsApp
  const weekStart = (() => { const d = new Date(runDate); d.setDate(d.getDate() - ((d.getDay() + 6) % 7)); return d; })();
  $("msg-intro").value = `Voici les offres de la semaine du ${weekStart.getDate()} ${MONTHS[weekStart.getMonth()]}, sélectionnées pour vous.`;
  function buildMessage() {
    const picks = offers.filter(o => selected.has(o.lien)).sort((a, b) => (b.date_iso || "").localeCompare(a.date_iso || ""));
    const lines = ["*Offres sport business | Sorbonne Sport Business*", $("msg-intro").value.trim(), ""];
    picks.forEach((o, i) => {
      lines.push(`*${i + 1}. ${o.titre.replace(/\*/g, "")}*`);
      lines.push([o.entreprise, o.contrat, o.localisation].filter(Boolean).join(" · "));
      if ($("msg-infos").checked && o.infos) lines.push(o.infos.charAt(0).toUpperCase() + o.infos.slice(1));
      lines.push(o.lien, "");
    });
    if ($("msg-link").checked && SITE) lines.push(`Toutes les offres${SCHEDULE ? `, mises à jour ${SCHEDULE.replace(/ à .*$/, "")}` : ""} :`, SITE, "");
    lines.push("Bonne chance à toutes et à tous !");
    return lines.filter((l, i, a) => !(l === "" && a[i - 1] === "")).join("\n");
  }
  function refreshMsg(regen) {
    if (regen) $("msg-text").value = buildMessage();
    const t = $("msg-text").value;
    $("msg-wa").href = "https://wa.me/?text=" + encodeURIComponent(t);
    $("msg-len").textContent = `${t.length} caractères`;
  }
  const openMsg = () => { refreshMsg(true); $("msg").showModal(); $("msg-text").focus(); $("msg-text").setSelectionRange(0, 0); $("msg-text").scrollTop = 0; };
  $("msg-open").addEventListener("click", openMsg);
  $("msg-open-2").addEventListener("click", openMsg);
  ["msg-intro", "msg-link", "msg-infos"].forEach(id => $(id).addEventListener("input", () => refreshMsg(true)));
  $("msg-text").addEventListener("input", () => refreshMsg(false));
  $("msg-close").addEventListener("click", () => $("msg").close());
  $("msg-copy").addEventListener("click", async e => {
    try { await navigator.clipboard.writeText($("msg-text").value); e.currentTarget.textContent = "Message copié"; }
    catch { $("msg-text").select(); e.currentTarget.textContent = "Texte sélectionné : Cmd+C"; }
  });

  // Google Sheets (formule de secours quand aucune feuille n'est configurée)
  const gsBtn = $("gs");
  if (gsBtn && $("gs-help")) {
    const formula = `=IMPORTDATA("${SITE}offres.csv")`;
    $("gs-formula").textContent = formula;
    gsBtn.addEventListener("click", () => { const h = $("gs-help"); h.hidden = !h.hidden; gsBtn.setAttribute("aria-expanded", !h.hidden); });
    $("gs-copy").addEventListener("click", async e => {
      try { await navigator.clipboard.writeText(formula); e.target.textContent = "Formule copiée"; }
      catch { const r = document.createRange(); r.selectNodeContents($("gs-formula")); const s = getSelection(); s.removeAllRanges(); s.addRange(r); e.target.textContent = "Formule sélectionnée : Cmd+C"; }
    });
  }

  const employers = new Set(offers.map(o => o.entreprise)).size;
  const week = offers.filter(o => o._pub && daysBetween(o._pub, runDate) <= 7).length;
  $("figures").innerHTML = `<span><b>${offers.length}</b> offres</span><span><b>${employers}</b> employeurs</span><span><b>${week}</b> publiées ces 7 derniers jours</span><span>Mise à jour le <b>${DAYS[runDate.getDay()]} ${runDate.getDate()} ${MONTHS[runDate.getMonth()]}</b></span>`;
  $("meta").textContent = `${SCHEDULE ? `Veille relancée automatiquement ${SCHEDULE}. ` : ""}Les offres changent vite : vérifiez la date limite sur la page de l'employeur avant de postuler.`;
  render();
})();
</script>
"""

DOWNLOADS = """        <a class="btn" href="veille-ssb.xlsx" download="veille-ssb-__RUN__.xlsx">Télécharger l'Excel</a>
        __GSBUTTON__
        <a class="btn" href="offres.csv" download="offres-ssb-__RUN__.csv">CSV</a>"""

GS_LINK = """<a class="btn" href="__SHEET__" target="_blank" rel="noopener">Ouvrir le Google Sheet</a>"""
GS_FALLBACK_BUTTON = """<button class="btn" id="gs" type="button" aria-expanded="false" aria-controls="gs-help">Google Sheets</button>"""
GS_FALLBACK_HELP = """    <div class="gs" id="gs-help" hidden>
      <ol>
        <li>Créez une feuille vide : <a href="https://sheets.new" target="_blank" rel="noopener">sheets.new</a>.</li>
        <li>Collez cette formule dans la case A1 : <code id="gs-formula"></code> <button class="linkbtn" id="gs-copy" type="button">Copier la formule</button></li>
      </ol>
    </div>"""

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
    parser.add_argument("--downloads", action="store_true",
                        help="Boutons Excel / Google Sheets / CSV (page hébergée avec veille-ssb.xlsx et offres.csv à côté)")
    parser.add_argument("--schedule", help="Rythme affiché en pied de page, ex. « le lundi et le jeudi à 8 h »")
    parser.add_argument("--sheet-url", help="Google Sheet partagé (sinon le bouton explique la formule IMPORTDATA)")
    parser.add_argument("--site-url", help="Adresse publique de la page, reprise dans le message WhatsApp")
    args = parser.parse_args()

    data = json.load(open(args.input_json, encoding="utf-8"))
    run = args.date or data.get("date_maj") or data.get("date_execution") or datetime.date.today().isoformat()
    keep = ("titre", "entreprise", "categorie", "secteur", "localisation", "contrat", "date_iso", "ajoutee_le", "lien", "source")
    offers = [{**{k: o.get(k, "") for k in keep}, "infos": infos(o)} for o in data.get("offres", [])]
    offers.sort(key=lambda o: o.get("date_iso") or "", reverse=True)

    downloads, gshelp = "", ""
    if args.downloads:
        if args.sheet_url:
            gs_button = GS_LINK.replace("__SHEET__", html.escape(args.sheet_url))
        else:
            gs_button, gshelp = GS_FALLBACK_BUTTON, GS_FALLBACK_HELP
        downloads = DOWNLOADS.replace("__GSBUTTON__", gs_button).replace("__RUN__", html.escape(run))

    payload = json.dumps(offers, ensure_ascii=False).replace("</", "<\\/")
    page = (PAGE.replace("__DOWNLOADS__", downloads).replace("__GSHELP__", gshelp)
            .replace("__DATA__", payload).replace("__RUN__", html.escape(run))
            .replace("__SCHEDULE__", html.escape(args.schedule or ""))
            .replace("__SITE__", html.escape(args.site_url or "")))
    if args.standalone:
        head_end = page.index("</style>") + len("</style>")
        page = STANDALONE.format(page_head=page[:head_end], page_body=page[head_end:])

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"Page générée : {out} ({len(offers)} offres)")


if __name__ == "__main__":
    main()
