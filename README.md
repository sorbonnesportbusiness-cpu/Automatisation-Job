# Veille emploi Sport Business — Sorbonne Sport Business (SSB)

Ce repo contient un **skill Claude** réutilisable qui refait, à la demande ou sur une
planification hebdomadaire, la veille d'offres d'emploi/stage/alternance sport business
pour l'association. Chaque membre du bureau peut l'installer dans son propre Claude et
l'exécuter — pas besoin de centraliser l'exécution sur une seule personne.

Le skill produit chaque semaine :
- un fichier Excel coloré et prêt à diffuser (`veille-ssb-<date>.xlsx`), trié de l'offre la
  plus récente à la plus ancienne,
- une page web filtrable des mêmes offres (`veille-ssb-<date>.html`),
- un export JSON brut des mêmes offres (`offres-<date>.json`), pensé pour être repris plus
  tard par le CRM de l'association dès qu'il existera.

## La page en ligne

**https://veille-ssb.gererseul-avis-worker.workers.dev** : toutes les offres ouvertes, triées
de la plus récente à la plus ancienne, avec recherche et filtres. Depuis la page, on peut
télécharger l'Excel ou le CSV, ou ouvrir une feuille Google Sheets qui se met à jour toute
seule (formule `IMPORTDATA`).

La veille est relancée automatiquement le lundi et le jeudi à 8 h par une tâche planifiée
Claude sur le Mac de Tom (qui doit être allumé, avec l'app Claude ouverte). Chaque passage
retire les offres closes, ajoute les nouvelles, remet la page en ligne et pousse les données
dans `data/offres.json`.

## Ce qu'il y a dans ce repo

```
skills/veille-ssb/
├── SKILL.md                  → les instructions complètes de la veille (règles, portails, format)
├── scripts/build_outputs.py  → génère le .xlsx + le .json à partir d'une liste d'offres
├── scripts/build_page.py     → génère la page web filtrable à partir de la même liste
├── scripts/update_board.py   → tient le tableau des offres d'une veille à l'autre
├── references/portails.md    → mémoire collective : portails qui marchent / stériles / à tester
└── references/historique.md  → liens déjà livrés, à ne pas reproposer
data/offres.json              → le tableau en ligne (offres ouvertes)
site/                         → hébergement Cloudflare (wrangler.toml) et publish.sh
```

Le dossier est rangé sous `skills/` (sans point devant) à la racine du repo, et pas
directement sous `.claude/skills/`. Chaque personne le copie ensuite là où son Claude
l'attend (voir ci-dessous).

## Installer le skill dans son propre Claude

### Option A — Claude Code

1. Clone ce repo (ou télécharge-le en zip depuis GitHub : bouton vert "Code" → "Download
   ZIP") :
```bash
   git clone https://github.com/sorbonnesportbusiness-cpu/Automatisation-Job.git
```
2. Dans le projet où tu ouvres Claude Code, copie le dossier du skill sous `.claude/skills/` :
```bash
   mkdir -p mon-projet/.claude/skills
   cp -r Automatisation-Job/skills/veille-ssb mon-projet/.claude/skills/
```
3. Ouvre Claude Code dans `mon-projet`. Le skill apparaît automatiquement dans la liste des
   skills disponibles (`veille-ssb`).
4. Installe les dépendances Python une fois (`pip install openpyxl`), si ton
   environnement ne les a pas déjà.
5. Lance-le en tapant simplement, par exemple : *"Lance la veille SSB"* ou invoque le skill
   explicitement si ton interface le permet.

### Option B — Cowork (claude.ai, sans repo de code)

1. Sur la page du repo GitHub, ouvre `skills/veille-ssb/SKILL.md`, clique sur le bouton
   "Raw" puis enregistre la page (Ctrl/Cmd+S) sous le nom `SKILL.md` — ou télécharge tout
   le dossier `skills/veille-ssb/` via "Download ZIP" et dézippe-le.
2. Dans Cowork, ajoute-le comme skill personnalisé si ton organisation autorise les
   skills personnalisés (upload du fichier depuis l'interface des paramètres).
3. Demande à Claude : *"Lance la veille SSB"*.

Dans les deux cas, Claude a besoin d'un accès à la **recherche web** (WebSearch/WebFetch)
pour que la veille fonctionne — sans ça, il te le dira plutôt que d'inventer des offres.

## Automatiser l'exécution chaque semaine

Chaque membre qui installe le skill peut lui-même programmer un run hebdomadaire **dans
son propre Claude** :
- Sur Cowork/claude.ai : utiliser la fonctionnalité de tâches planifiées ("scheduled
  tasks") et donner comme instruction *"Lance le skill veille-ssb et envoie-moi le
  résultat"*, avec une fréquence hebdomadaire.
- Sur Claude Code : selon l'environnement, via un scheduler externe (cron) qui invoque
  Claude Code avec le prompt du skill, ou via la fonctionnalité de tâches planifiées si
  elle est disponible dans ton environnement.

Il n'y a pas de serveur central à maintenir : c'est volontairement décentralisé, pour que
n'importe qui du bureau puisse le faire tourner avec son propre accès Claude, sans
dépendre d'une infrastructure partagée.

## Mettre à jour le skill pour tout le monde

Le skill est versionné ici. Quand quelqu'un améliore les règles, ajoute un portail fiable
ou corrige un bug du script :
1. Modifier les fichiers dans `skills/veille-ssb/`.
2. Ouvrir une Pull Request et la faire relire par un autre membre du bureau.
3. Une fois mergée, chaque membre doit retélécharger/re-copier le dossier mis à jour dans
   son propre Claude (il n'y a pas de synchronisation automatique entre ce repo et
   l'installation de chacun).

## Historique

- 2026-10-04 : premier export du skill depuis une session Cowork, après plusieurs semaines
  d'exécution manuelle via une tâche planifiée Claude. Portails validés et stériles au
  2026-09-28 consignés dans `skills/veille-ssb/references/portails.md`.
- 2026-10-07 : veille élargie à toute l'industrie du sport (institutions, droit, finance,
  marques, sportstech) : 106 offres chez 85 employeurs. Excel trié par date avec colonnes
  Catégorie et Début / clôture, nouvelle page web, historique des liens livrés, liste des
  portails refaite.

Important : il faut utiliser la recherche internet avec Claude, sinon la veille ne
fonctionne pas.
