#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère les livrables de la veille emploi Sport Business (Sorbonne Sport Business) :
  - veille-ssb-<date>.xlsx : fichier Excel coloré pour l'association
  - offres-<date>.json     : export brut, pensé pour un futur CRM

Usage :
    python3 build_outputs.py offres.json --date 2026-09-28 --out-dir ./out

Le fichier d'entrée (offres.json) doit avoir la forme :
{
  "offres": [
    {
      "titre": "...", "entreprise": "...", "secteur": "...",
      "localisation": "...", "contrat": "Stage|Alternance|CDI|CDD|Freelance",
      "date_pub": "...", "lien": "https://...", "source": "..."
    }, ...
  ],
  "bilan": {
    "total_testees_ecartees": 0,
    "detail_ecartees": ["..."],
    "portails_steriles": ["..."],
    "nouveaux_portails": ["..."]
  }
}

Point d'intégration CRM : si la variable d'environnement SSB_CRM_WEBHOOK_URL est définie,
le JSON des offres lui est envoyé en POST en plus d'être écrit sur disque. Tant que le CRM
de l'association n'existe pas, laisser cette variable non définie : le script fonctionne
alors exactement comme avant, sans rien envoyer.
"""

import argparse
import csv
import datetime
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

FONT_NAME = "Arial"

HEADER_FILL = PatternFill(start_color="1B3A5C", end_color="1B3A5C", fill_type="solid")
HEADER_FONT = Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")
HEADER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)

EVEN_FILL = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
ODD_FILL = PatternFill(start_color="E8F0FE", end_color="E8F0FE", fill_type="solid")

THIN_BORDER = Border(
    left=Side(style="thin", color="D0D0D0"),
    right=Side(style="thin", color="D0D0D0"),
    top=Side(style="thin", color="D0D0D0"),
    bottom=Side(style="thin", color="D0D0D0"),
)

CONTRACT_COLORS = {
    "Stage": "2E7D32",
    "Alternance": "1565C0",
    "CDI": "E65100",
    "CDD": "616161",
    "Freelance": "6A1B9A",
}

COLUMN_WIDTHS = {
    "A": 5, "B": 13, "C": 45, "D": 30, "E": 16, "F": 22,
    "G": 24, "H": 13, "I": 30, "J": 50, "K": 24, "L": 12,
}

HEADERS = [
    "N°", "Publiée le", "Intitulé du poste", "Entreprise / Organisation", "Catégorie",
    "Secteur", "Localisation", "Type de contrat", "Début / clôture", "Lien vers l'offre",
    "Source", "Vérifié le",
]
COL_CONTRACT, COL_LINK = 8, 10


def _infos(offer):
    """Début / clôture : champ `infos`, sinon le contenu entre parenthèses de date_pub."""
    if offer.get("infos"):
        return offer["infos"]
    m = re.search(r"\((.*)\)", offer.get("date_pub", ""))
    return m.group(1) if m else ""


def build_workbook(offers, bilan, run_date_fr, run_date_iso):
    wb = Workbook()
    ws = wb.active
    ws.title = "Offres Sport Business"

    for col_idx, header in enumerate(HEADERS, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = HEADER_ALIGN
        cell.border = THIN_BORDER
    ws.row_dimensions[1].height = 30

    for i, offer in enumerate(offers, start=1):
        row = i + 1
        fill = EVEN_FILL if i % 2 == 0 else ODD_FILL
        pub = offer.get("date_iso")
        values = [
            i, datetime.date.fromisoformat(pub) if pub else "n.c.",
            offer.get("titre", ""), offer.get("entreprise", ""), offer.get("categorie", ""),
            offer.get("secteur", ""), offer.get("localisation", ""), offer.get("contrat", ""),
            _infos(offer), offer.get("lien", ""), offer.get("source", ""), run_date_fr,
        ]
        for col_idx, value in enumerate(values, start=1):
            cell = ws.cell(row=row, column=col_idx, value=value)
            cell.font = Font(name=FONT_NAME, size=11)
            cell.fill = fill
            cell.border = THIN_BORDER
            cell.alignment = Alignment(vertical="center", wrap_text=(col_idx in (3, 4, 9, 10)))
        ws.cell(row=row, column=2).number_format = "DD/MM/YYYY"

        contract_cell = ws.cell(row=row, column=COL_CONTRACT)
        color = CONTRACT_COLORS.get(offer.get("contrat", ""), "000000")
        contract_cell.font = Font(name=FONT_NAME, size=11, bold=True, color=color)

        link_cell = ws.cell(row=row, column=COL_LINK)
        if offer.get("lien"):
            link_cell.hyperlink = offer["lien"]
            link_cell.font = Font(name=FONT_NAME, size=11, color="1155CC", underline="single")

    for col, width in COLUMN_WIDTHS.items():
        ws.column_dimensions[col].width = width

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:L{len(offers) + 1}"

    # Onglet Bilan
    bilan_ws = wb.create_sheet("Bilan")
    TITLE_FONT = Font(name=FONT_NAME, size=14, bold=True, color="1B3A5C")
    SUBTITLE_FONT = Font(name=FONT_NAME, size=12, bold=True, color="FFFFFF")
    SUBTITLE_FILL = PatternFill(start_color="1B3A5C", end_color="1B3A5C", fill_type="solid")
    LABEL_FONT = Font(name=FONT_NAME, size=11, bold=True)
    NORMAL_FONT = Font(name=FONT_NAME, size=11)
    ITEM_FONT = Font(name=FONT_NAME, size=10)

    bilan_ws.column_dimensions["A"].width = 100
    for col in ["B", "C", "D"]:
        bilan_ws.column_dimensions[col].width = 20

    r = 1
    bilan_ws.cell(row=r, column=1, value="Bilan de la veille emploi - Sorbonne Sport Business").font = TITLE_FONT
    r += 1
    bilan_ws.cell(row=r, column=1, value=f"Date d'exécution : {run_date_fr}").font = NORMAL_FONT
    r += 2

    def section_title(row, text):
        cell = bilan_ws.cell(row=row, column=1, value=text)
        cell.font = SUBTITLE_FONT
        cell.fill = SUBTITLE_FILL
        cell.alignment = Alignment(vertical="center")
        bilan_ws.row_dimensions[row].height = 22
        return row + 1

    r = section_title(r, "Chiffres clés")
    bilan_ws.cell(row=r, column=1, value="Nombre total d'offres retenues (vérifiées, non expirées)").font = LABEL_FONT
    bilan_ws.cell(row=r, column=2, value=len(offers)).font = NORMAL_FONT
    r += 1
    bilan_ws.cell(row=r, column=1, value="Nombre d'employeurs distincts dans la sélection finale").font = LABEL_FONT
    bilan_ws.cell(row=r, column=2, value=len(set(o.get("entreprise", "") for o in offers))).font = NORMAL_FONT
    r += 1
    bilan_ws.cell(row=r, column=1, value="Nombre de candidates testées et écartées").font = LABEL_FONT
    bilan_ws.cell(row=r, column=2, value=bilan.get("total_testees_ecartees", 0)).font = NORMAL_FONT
    r += 2

    sections = [
        ("Détail des candidates écartées", bilan.get("detail_ecartees", [])),
        ("Employeurs / portails stériles cette semaine", bilan.get("portails_steriles", [])),
        ("Nouveaux portails découverts (à ajouter à la liste des sources validées)", bilan.get("nouveaux_portails", [])),
    ]
    for title, items in sections:
        r = section_title(r, title)
        for item in items:
            cell = bilan_ws.cell(row=r, column=1, value=f"• {item}")
            cell.font = ITEM_FONT
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            r += 1
        r += 1

    r = section_title(r, "Traçabilité")
    bilan_ws.cell(row=r, column=1, value=f"Date d'exécution de la veille : {run_date_fr}").font = NORMAL_FONT
    r += 1
    note = bilan_ws.cell(
        row=r, column=1,
        value="Méthode : recherche web + fetch direct de la page individuelle de chaque "
              "offre retenue (jamais de page de liste/recherche). Aucun lien derrière un "
              "mur d'inscription obligatoire livré.",
    )
    note.font = NORMAL_FONT
    note.alignment = Alignment(wrap_text=True, vertical="top")
    bilan_ws.row_dimensions[r].height = 30

    return wb


def write_csv(offers, path):
    """CSV UTF-8 des offres (mêmes colonnes que l'Excel), lisible par IMPORTDATA de Google Sheets."""
    fr = lambda iso: datetime.date.fromisoformat(iso).strftime("%d/%m/%Y") if iso else ""
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Publiée le", "Ajoutée le", "Intitulé du poste", "Entreprise / Organisation",
                    "Catégorie", "Secteur", "Localisation", "Type de contrat", "Début / clôture",
                    "Lien vers l'offre", "Source"])
        for o in offers:
            w.writerow([fr(o.get("date_iso")), fr(o.get("ajoutee_le")), o.get("titre", ""),
                        o.get("entreprise", ""), o.get("categorie", ""), o.get("secteur", ""),
                        o.get("localisation", ""), o.get("contrat", ""), _infos(o),
                        o.get("lien", ""), o.get("source", "")])


def maybe_push_to_crm(payload):
    """Envoie le JSON au CRM si SSB_CRM_WEBHOOK_URL est défini. No-op sinon."""
    url = os.environ.get("SSB_CRM_WEBHOOK_URL", "").strip()
    if not url:
        return "SSB_CRM_WEBHOOK_URL non définie — étape CRM ignorée (normal tant que le CRM n'existe pas)."
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return f"Envoyé au CRM ({url}) — statut HTTP {resp.status}."
    except Exception as exc:  # noqa: BLE001 - on veut juste logguer, jamais faire planter le run
        return f"Échec de l'envoi au CRM ({url}) : {exc}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", help="Fichier JSON des offres (voir docstring)")
    parser.add_argument("--date", help="Date d'exécution AAAA-MM-JJ (défaut : aujourd'hui)")
    parser.add_argument("--out-dir", default="./out", help="Répertoire de sortie")
    args = parser.parse_args()

    with open(args.input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    offers = data.get("offres", [])
    # Plus récentes d'abord (date_iso = AAAA-MM-JJ de publication), offres sans date en bas.
    offers.sort(key=lambda o: o.get("date_iso") or "", reverse=True)
    bilan = data.get("bilan", {})

    if len(offers) < 7:
        print(
            f"ATTENTION : seulement {len(offers)} offre(s) fournie(s), "
            "objectif minimum = 7. Le fichier sera quand même généré.",
            file=sys.stderr,
        )

    run_date_iso = args.date or datetime.date.today().isoformat()
    run_date_fr = datetime.date.fromisoformat(run_date_iso).strftime("%d/%m/%Y")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    xlsx_path = out_dir / f"veille-ssb-{run_date_iso}.xlsx"
    json_path = out_dir / f"offres-{run_date_iso}.json"
    csv_path = out_dir / f"offres-{run_date_iso}.csv"

    wb = build_workbook(offers, bilan, run_date_fr, run_date_iso)
    wb.save(xlsx_path)

    export_payload = {
        "date_execution": run_date_iso,
        "nombre_offres": len(offers),
        "offres": offers,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(export_payload, f, ensure_ascii=False, indent=2)

    write_csv(offers, csv_path)

    crm_status = maybe_push_to_crm(export_payload)

    print(f"Excel généré : {xlsx_path}")
    print(f"JSON généré  : {json_path}")
    print(f"CSV généré   : {csv_path}")
    print(f"CRM          : {crm_status}")


if __name__ == "__main__":
    main()
