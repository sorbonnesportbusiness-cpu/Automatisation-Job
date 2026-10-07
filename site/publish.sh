#!/usr/bin/env bash
# Met en ligne une veille : tableau des offres, Excel, CSV, page web, commit + push.
# Usage : site/publish.sh <nouvelles.json> [AAAA-MM-JJ]
# Machine de Tom : wrangler connecté au compte Cloudflare perso, gh connecté à tpetitvallois-web.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NEW="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
DATE="${2:-$(date +%F)}"
SK="$ROOT/skills/veille-ssb"
cd "$ROOT"

[ -x .venv/bin/python ] || { python3 -m venv .venv && .venv/bin/pip install -q -r "$SK/requirements.txt"; }
PY=.venv/bin/python

$PY "$SK/scripts/update_board.py" "$NEW" --date "$DATE" --board data/offres.json --history "$SK/references/historique.md"
$PY "$SK/scripts/build_outputs.py" data/offres.json --date "$DATE" --out-dir out
$PY "$SK/scripts/build_page.py" data/offres.json --date "$DATE" --out site/public/index.html \
    --standalone --downloads --schedule "le lundi et le jeudi à 8 h"
cp "out/veille-ssb-$DATE.xlsx" site/public/veille-ssb.xlsx
cp "out/offres-$DATE.csv" site/public/offres.csv
cp data/offres.json site/public/offres.json

(cd site && npx --yes wrangler@4 deploy)

git add data "$SK/references"
git commit -q -m "Veille du $DATE" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || echo "Rien à committer"
TOKEN="$(gh auth token --user tpetitvallois-web)"
git -c http.extraheader="Authorization: Basic $(printf 'x-access-token:%s' "$TOKEN" | base64)" push -q origin HEAD:main
echo "En ligne : https://veille-ssb.gererseul-avis-worker.workers.dev"
