#!/usr/bin/env bash
# Met le clone à jour avant une veille, crée le dossier des lots du jour et affiche la date.
# Usage : site/pull.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
TOKEN="$(gh auth token --user tpetitvallois-web)"
git -c http.extraheader="Authorization: Basic $(printf 'x-access-token:%s' "$TOKEN" | base64)" pull -q --ff-only origin main
DATE="$(date +%F)"
mkdir -p "out/lots/$DATE"
echo "$DATE"
