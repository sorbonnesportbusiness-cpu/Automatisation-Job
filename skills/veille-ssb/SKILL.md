---
name: veille-ssb
description: "Veille hebdomadaire des offres d'emploi/stage/alternance dans l'industrie du sport pour Sorbonne Sport Business (SSB). Utiliser quand on demande de lancer/relancer la veille emploi SSB, de chercher des offres sport business (marketing sportif, événementiel, sponsoring, droit du sport, finance du sport, institutions sportives, esport, billetterie...), ou d'exécuter le skill veille-ssb. Produit un fichier Excel coloré trié par date, une page web filtrable et un export JSON brut prêt pour un futur CRM."
license: Interne association SSB
---

# Veille emploi Sport Business — Sorbonne Sport Business (SSB)

Ce skill reproduit la veille hebdomadaire d'offres d'emploi/stage/alternance sport business
de l'association. Il fonctionne dans n'importe quelle session Claude qui a accès à la
recherche web (WebSearch/WebFetch ou équivalent) et à un terminal (Bash) pour lancer les
scripts Python de mise en forme — Claude Code, Cowork, ou un Claude personnel avec les
outils web activés.

Toute personne du bureau peut l'utiliser : installez ce dossier comme skill (voir
`../../README.md` à la racine du repo pour la procédure d'installation Cowork / Claude Code),
puis invoquez-le (`/veille-ssb` ou "lance la veille SSB").

## Avant de commencer

1. Détermine la date du jour avec `date +%F` (ne jamais la deviner).
2. Vérifie que tu as accès à une recherche web et à un fetch de pages. Si aucun outil web
   n'est disponible dans cette session, dis-le clairement et arrête-toi : ce skill ne doit
   jamais inventer des offres à partir de connaissances générales.
3. Lis `references/portails.md` (où chercher) et `references/historique.md` (liens déjà
   livrés, à ne pas reproposer).

## Objectif

Livrer AU MINIMUM 7 offres NON EXPIRÉES et VÉRIFIÉES dans l'industrie du sport, pour des
étudiants et jeunes diplômés (stage, alternance, premier emploi jusqu'à 3 ans
d'expérience). Périmètre : marketing sportif, management du sport, événementiel sportif,
communication sport, sponsoring, partenariats, fan experience, billetterie/hospitalités,
merchandising, esport, médias sport, paris sportifs, droit du sport (juristes, élèves-avocats,
cabinets avec une pratique sport), finance du sport, politiques sportives (État,
collectivités). Une veille complète en donne facilement 50 à 100.

Écarter : encadrement sportif (coach, éducateur, MNS, CTS), postes techniques, IT,
entretien, sécurité, vente en magasin, postes demandant 4-5 ans d'expérience ou plus,
annonces d'écoles sans employeur nommé, services civiques, bénévolat.

**Priorité absolue : l'offre ne doit pas être expirée.** C'est plus important que sa
fraîcheur exacte.

## Règle de diversité

Pas de plafond par employeur (levé le 2026-10-09 à la demande de Tom) : toutes les offres
valides d'un portail très fourni (Alpes 2030, FFT, LFP, Sportfive, CANAL+...) entrent au
tableau. Balayer quand même toutes les familles de sources : un gros portail ne dispense
pas de chercher ailleurs.

## Règle de lien — la plus importante

Chaque lien livré doit être LIBREMENT ACCESSIBLE et pointer vers la source de l'employeur
quand c'est possible.
- Ne jamais livrer un lien derrière un paywall ou une inscription obligatoire.
- Les boards payants/masqués servent uniquement de DÉTECTION : on y repère qu'un poste
  existe, puis on fait une recherche web sur l'intitulé exact (+ secteur, ville, employeur
  si devinable) pour retrouver l'offre d'origine sur le site carrières de l'employeur, et
  c'est CE lien-là qu'on livre.
- Ordre de préférence : site carrières / ATS de l'employeur, puis fiche d'un agrégateur
  lisible sans connexion (HelloWork, La Bonne Alternance, choisirleservicepublic.gouv.fr...),
  puis fiche LinkedIn `/jobs/view/<id>` en dernier recours (beaucoup de clubs ne publient
  que là).
- Si on ne parvient pas à retrouver une source libre d'une offre, on ne la livre pas.

## Où chercher

La liste à jour des portails qui marchent, des agrégateurs utiles et des sources stériles
est dans `references/portails.md`. La mettre à jour à chaque veille.

Les API JSON publiques qu'une page carrières appelle elle-même sans authentification
(Workday, SmartRecruiters, Teamtailor, Welcome Kit, Taleez, Flatchr, Lever, Ashby, Breezy,
DigitalRecruiters...) sont autorisées : elles donnent souvent la date exacte de publication.

Familles de sources à couvrir, en parallèle (un sous-agent par famille) :
1. Portails validés de `references/portails.md` (clubs, ligues, fédérations, organisateurs).
2. Marques, équipementiers et sponsors (activation, partenariats, marketing sport), y compris
   les équipes sponsoring des grands annonceurs hors sport : banques, assurances, énergie,
   télécoms, automobile, distribution (ex. Crédit Agricole, « Stage - Chargé(e) de
   communication sponsoring »).
3. Agences, médias sport, paris sportifs, sportstech.
4. Institutions publiques : choisirleservicepublic.gouv.fr, emploi-territorial.fr, Ville de Paris.
5. Droit et finance du sport : Village de la Justice, Law Profiler, sites carrières des
   éditeurs juridiques et des opérateurs de paris.
6. Agrégateurs : HelloWork trié par date, La Bonne Alternance, Meent, Sport Stratégies,
   GlobalSportsJobs.
7. Recherche LinkedIn sans connexion, balayée systématiquement (25 requêtes et plus :
   stage sponsoring, stage marketing sportif, alternance événementiel sport, stage club
   football/rugby/basket, stage esport, stage juriste sport...). C'est là que publient les
   clubs, ligues et petites agences. Retracer vers la source employeur quand elle existe.
8. Startups, sportstech, esport, fitness et outdoor via les API publiques de leurs ATS
   (Ashby, Lever, Greenhouse, Teamtailor, Recruitee, Breezy, Personio, SmartRecruiters).

## Filtres

1. Fraîcheur : publication dans les 2 derniers mois maximum (priorité absolue reste la
   non-expiration). Une prise de poste future est valable ; une offre dont la date de
   DÉBUT ou la date limite est déjà passée est à écarter.
2. Localisation : France entière.
3. Offre réellement ouverte, vérifiée sur la page individuelle (jamais sur une page de
   liste/recherche).
4. Date de publication relevée précisément (JSON-LD `datePosted`, date affichée, champ de
   l'API, « il y a X jours » converti). Elle sert au tri des livrables.

## Leçon critique — taux d'erreur des agrégateurs

Les jobboards sport gardent en ligne des offres closes et affichent parfois "publié il y a
X jours" pour un poste déjà fermé, ou une date de republication. sportjobshunter.com est le
pire cas. Éliminer systématiquement : 404/410, "offre expirée"/"poste pourvu"/"clôturée"/
"n'est plus disponible"/"recrutement fermé", page qui se charge vide, date limite/début
passée, publication de plus de 2 mois, et toute page de recherche/catégorie qui n'est pas
une offre individuelle. Quand une API donne une première date de publication plus ancienne
que celle affichée (republication), garder la plus ancienne.

## Méthode

1. Balayer les familles de sources ci-dessus (pas de plafond par employeur).
2. Ouvrir 2-3 nouveaux employeurs de la liste "À tester" de `references/portails.md` et
   consigner le résultat (positif ou négatif).
3. Retracer chaque offre trouvée sur un agrégateur vers la source de l'employeur.
4. Vérifier CHAQUE offre par fetch de sa page individuelle avant de la retenir.
5. Exclure les liens déjà présents dans `references/historique.md`.
6. Juste avant de générer les livrables, revérifier que chaque lien répond encore
   (un 429 de LinkedIn signifie seulement qu'il faut espacer les requêtes).

Ne jamais tenter de se connecter à un site ni de contourner une protection anti-scraping
(403, Cloudflare, paywall = on abandonne cette source).

## Livrables

Une fois les offres réunies et vérifiées, générer les sorties avec les scripts fournis :

```bash
python3 scripts/build_outputs.py offres.json --date YYYY-MM-DD --out-dir ./out
python3 scripts/build_page.py offres.json --date YYYY-MM-DD --out ./out/veille-ssb-YYYY-MM-DD.html --standalone
```

où `offres.json` est un fichier que tu écris toi-même, de la forme :

```json
{
  "offres": [
    {
      "titre": "Stage - Gestion Billetterie - Janvier 2027",
      "entreprise": "Fédération Française de Tennis (Roland-Garros)",
      "categorie": "Ligue / Fédération",
      "secteur": "Billetterie",
      "localisation": "Paris 16e (75)",
      "contrat": "Stage",
      "date_iso": "2026-09-15",
      "date_pub": "15/09/2026 (début janv. 2027, clôture 30/11/2026)",
      "lien": "https://jobs.fft.fr/jobs/8380861-...",
      "source": "jobs.fft.fr"
    }
  ],
  "bilan": {
    "total_testees_ecartees": 32,
    "detail_ecartees": ["..."],
    "portails_steriles": ["..."],
    "nouveaux_portails": ["..."]
  }
}
```

- `date_iso` (AAAA-MM-JJ) : date de publication, utilisée pour trier les offres de la plus
  récente à la plus ancienne. `null` si introuvable (l'offre est alors classée en bas).
- `categorie` : type d'employeur, pour filtrer. Valeurs utilisées : Club, Ligue / Fédération,
  Institution, Organisateur / Événement, Stade / Arène, Agence, Média, Paris sportifs,
  Marque / Sponsor, Retail sport, Sportstech, Loisirs sportifs, Droit.
- `date_pub` : texte libre. Ce qui est entre parenthèses (début, clôture, durée) est repris
  dans la colonne « Début / clôture ». Écrire « clôture JJ/MM/AAAA » quand la date limite
  est connue : la page web signale alors les offres qui ferment dans les 10 jours.
- `contrat` : Stage, Alternance, CDI, CDD ou Freelance (contractuel de la fonction publique = CDD).

Les scripts produisent, dans `out/` :
- `veille-ssb-YYYY-MM-DD.xlsx` — le fichier Excel pour l'association (voir format ci-dessous).
- `offres-YYYY-MM-DD.json` — export brut des mêmes offres, pensé pour être repris plus
  tard par le CRM de l'association (voir section CRM ci-dessous). Toujours générer ce
  fichier même si le CRM n'existe pas encore.
- `veille-ssb-YYYY-MM-DD.html` — page web autonome : offres groupées par jour de
  publication, recherche, filtres par contrat, catégorie, Île-de-France, publiées ces
  7 derniers jours, clôture proche. Sans `--standalone`, le script produit un fragment prêt
  à publier comme Artifact Claude.

Livre ensuite le `.xlsx` et la page à l'utilisateur (SendUserFile ou équivalent selon la
session), et mentionne que l'export JSON est disponible dans le même dossier.

Enfin, ajoute les liens livrés en tête de `references/historique.md` et mets à jour
`references/portails.md`.

### Format du fichier Excel

Un onglet principal "Offres Sport Business", trié de la plus récente à la plus ancienne,
avec les colonnes N°, Publiée le (vraie date Excel, triable), Intitulé du poste,
Entreprise / Organisation, Catégorie, Secteur, Localisation, Type de contrat,
Début / clôture, Lien vers l'offre, Source, Vérifié le — mise en forme Arial 11, en-tête
bleu foncé (#1B3A5C) en blanc gras, lignes alternées blanc/bleu très clair (#E8F0FE), type
de contrat coloré (Stage #2E7D32, Alternance #1565C0, CDI #E65100, CDD #616161), liens
cliquables, filtre auto, première ligne figée, bordures fines (#D0D0D0).

Un onglet "Bilan" avec le nombre total d'offres retenues, le nombre de candidates
testées/écartées, les employeurs/portails stériles de la semaine, les nouveaux portails
découverts, et la date d'exécution.

(Le script `scripts/build_outputs.py` implémente déjà tout ce formatage — ne pas le
réécrire à la main, juste lui fournir le JSON des offres.)

## Mode automatique : le tableau en ligne

La veille alimente une page publique : https://veille-ssb.gererseul-avis-worker.workers.dev
(boutons Excel, CSV et Google Sheets inclus). Elle est relancée par une tâche planifiée
Claude sur le Mac de Tom, le lundi et le jeudi à 8 h, depuis le clone `~/Automatisation-Job`.

Le tableau (`data/offres.json`) garde les offres des veilles précédentes tant qu'elles
sont ouvertes. Une veille automatique se déroule ainsi :
1. `site/pull.sh` dans `~/Automatisation-Job` (pull + date du jour).
2. Chercher de NOUVELLES offres avec la méthode ci-dessus. Exclure tout lien déjà présent
   dans `data/offres.json` ou dans `references/historique.md`. Pas de plafond par
   employeur.
3. Chaque sous-agent écrit ses offres dans `out/lots/AAAA-MM-JJ/<famille>.json` (format
   ci-dessus, avec `date_iso` et `categorie`). Les fusionner avec
   `scripts/merge_lots.py out/lots/AAAA-MM-JJ/*.json --board data/offres.json --history references/historique.md --out out/nouvelles-AAAA-MM-JJ.json`
   (doublons et liens déjà livrés traités par le script).
4. Lancer `site/publish.sh out/nouvelles-AAAA-MM-JJ.json AAAA-MM-JJ`. Le script revérifie
   les offres déjà au tableau (retire celles qui sont closes, mortes ou publiées il y a
   plus de 60 jours), ajoute les nouvelles, régénère l'Excel, le CSV et la page, met en
   ligne, puis commit et pousse `data/` et `references/` sur `main`.
5. Mettre à jour `references/portails.md` si de nouveaux portails ont été trouvés, puis
   commit et push.

Zéro nouvelle offre est un résultat valable : lancer quand même `publish.sh` avec un
fichier `{"offres": [], "bilan": {...}}` pour que les offres closes soient retirées.

## Point d'intégration CRM (à venir)

Le CRM de l'association n'existe pas encore. Le script accepte dès maintenant une variable
d'environnement `SSB_CRM_WEBHOOK_URL` : si elle est définie, il envoie un POST du JSON des
offres vers cette URL en plus d'écrire les fichiers locaux ; si elle est absente (cas
normal aujourd'hui), il ne fait rien de plus. Quand le CRM sera prêt, il suffira de
renseigner cette variable d'environnement (ou de demander à Claude de la définir avant de
lancer le script) — aucune autre modification du skill ne sera nécessaire.

## Nom des fichiers

`veille-ssb-YYYY-MM-DD.xlsx`, `veille-ssb-YYYY-MM-DD.html` et `offres-YYYY-MM-DD.json`
(date du jour d'exécution).

## Important

Ne publie rien d'autre, ne modifie aucun site web, ne touche à aucun dépôt git sans qu'on
te le demande explicitement. Les seuls livrables sont le fichier Excel, la page web et le
JSON (plus la mise à jour de `references/` si on te demande de pousser sur le repo).
