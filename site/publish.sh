#!/usr/bin/env bash
# Met en ligne une veille : tableau des offres, Excel, CSV, page web, commit + push.
# Usage : site/publish.sh <nouvelles.json> [AAAA-MM-JJ]
# Machine de Tom : compte Cloudflare de SSB via site/.env (CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN), gh connecté à tpetitvallois-web.
# GitHub Actions (workflow veille-hebdo) : mêmes variables lues dans les secrets du dépôt, et c'est le workflow qui pousse.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NEW="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
DATE="${2:-$(date +%F)}"
SK="$ROOT/skills/veille-ssb"
cd "$ROOT"
if [ -f site/.env ]; then set -a; . site/.env; set +a; fi

[ -x .venv/bin/python ] || { python3 -m venv .venv && .venv/bin/pip install -q -r "$SK/requirements.txt"; }
PY=.venv/bin/python

# Le Mac (lundi et jeudi) et GitHub Actions (lundi) alimentent le même tableau : on part de la
# dernière version poussée, sinon le dernier qui publie efface les offres de l'autre.
if [ "${GITHUB_ACTIONS:-}" = true ]; then
  GIT=(git)
else
  TOKEN="$(gh auth token --user tpetitvallois-web)"
  GIT=(git -c http.extraheader="Authorization: Basic $(printf 'x-access-token:%s' "$TOKEN" | base64)")
fi
"${GIT[@]}" pull -q --rebase --autostash origin main

$PY "$SK/scripts/update_board.py" "$NEW" --date "$DATE" --board data/offres.json --history "$SK/references/historique.md"
$PY "$SK/scripts/build_outputs.py" data/offres.json --date "$DATE" --out-dir out
$PY "$SK/scripts/build_page.py" data/offres.json --date "$DATE" --out site/public/index.html \
    --standalone --downloads --schedule "le lundi et le jeudi à 3 h" \
    --site-url "https://veille.sorbonnesportbusiness.com/" \
    --sheet-url "https://docs.google.com/spreadsheets/d/1dq0GyY7BNuiMfmkkJChm4dLw6iJzSyfR4Q6hkTm0GmU/edit"
cp "out/veille-ssb-$DATE.xlsx" site/public/veille-ssb.xlsx
cp "out/offres-$DATE.csv" site/public/offres.csv
cp data/offres.json site/public/offres.json

(cd site && npx --yes wrangler@4 deploy)

git add data "$SK/references"
git commit -q -m "Veille du $DATE" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || echo "Rien à committer"
if [ "${GITHUB_ACTIONS:-}" != true ]; then
  "${GIT[@]}" pull -q --rebase --autostash origin main
  "${GIT[@]}" push -q origin HEAD:main
fi
echo "En ligne : https://veille.sorbonnesportbusiness.com"
