# Veille emploi Sport Business — Sorbonne Sport Business (SSB)

Ce repo contient un **skill Claude** réutilisable qui refait, à la demande ou sur une
planification hebdomadaire, la veille d'offres d'emploi/stage/alternance sport business
pour l'association. Chaque membre du bureau peut l'installer dans son propre Claude et
l'exécuter — pas besoin de centraliser l'exécution sur une seule personne.

Le skill produit chaque semaine :
- un fichier Excel coloré et prêt à diffuser (`veille-ssb-<date>.xlsx`),
- un export JSON brut des mêmes offres (`offres-<date>.json`), pensé pour être repris plus
  tard par le CRM de l'association dès qu'il existera.

## Ce qu'il y a dans ce repo

```
.claude/skills/veille-ssb/
├── SKILL.md                  → les instructions complètes de la veille (règles, portails, format)
├── scripts/build_outputs.py  → génère le .xlsx + le .json à partir d'une liste d'offres
└── references/portails.md    → mémoire collective : portails qui marchent / stériles / à tester
```

## Installer le skill dans son propre Claude

### Option A — Claude Code (ou Cowork avec accès à un dépôt de code)

1. Clone ce repo (ou copie juste le dossier `.claude/skills/veille-ssb/`) à la racine du
   projet sur lequel tu ouvres Claude Code :
   ```bash
   git clone <URL_DE_CE_REPO> veille-ssb-automation
   # ou, si tu as déjà un projet Claude Code :
   cp -r veille-ssb-automation/.claude/skills/veille-ssb mon-projet/.claude/skills/
   ```
2. Ouvre Claude Code dans ce dossier. Le skill apparaît automatiquement dans la liste des
   skills disponibles (`veille-ssb`).
3. Installe les dépendances Python une fois (`pip install openpyxl`), si ton
   environnement ne les a pas déjà.
4. Lance-le en tapant simplement, par exemple : *"Lance la veille SSB"* ou invoque le skill
   explicitement si ton interface le permet.

### Option B — Cowork (claude.ai, sans repo de code)

1. Télécharge le fichier `SKILL.md` (et le dossier `scripts/`) depuis GitHub.
2. Dans Cowork, ajoute-le comme skill personnalisé (selon les réglages autorisés par ton
   organisation — upload du fichier depuis l'interface).
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
1. Modifier les fichiers dans `.claude/skills/veille-ssb/`.
2. Ouvrir une Pull Request et la faire relire par un autre membre du bureau.
3. Une fois mergée, chaque membre doit retélécharger/re-copier le dossier mis à jour dans
   son propre Claude (il n'y a pas de synchronisation automatique entre ce repo et
   l'installation de chacun).

## Et le CRM ?

Le CRM de l'association n'existe pas encore. Le script `build_outputs.py` est déjà prêt à
s'y brancher : il lit une variable d'environnement `SSB_CRM_WEBHOOK_URL` et, si elle est
renseignée, envoie automatiquement le JSON des offres à cette URL en plus d'écrire les
fichiers locaux. Tant que cette variable n'est pas définie, rien ne change par rapport à
aujourd'hui. Quand le CRM existera, il suffira :
1. de créer un endpoint qui accepte un POST JSON de la forme `{"date_execution": "...",
   "nombre_offres": N, "offres": [...]}`,
2. de renseigner `SSB_CRM_WEBHOOK_URL` avec l'URL de cet endpoint avant de lancer le
   script (ou de demander à Claude de le faire).

## Historique

- 2026-10-04 : premier export du skill depuis une session Cowork, après plusieurs semaines
  d'exécution manuelle via une tâche planifiée Claude. Portails validés et stériles au
  2026-09-28 consignés dans `references/portails.md`.
