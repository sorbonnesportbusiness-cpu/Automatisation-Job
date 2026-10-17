# Consigne de la veille

Veille des offres de stage, d'alternance et de premier emploi dans l'industrie du sport
pour Sorbonne Sport Business (SSB). Elle tourne sur GitHub Actions le lundi et le jeudi
à 3 h (heure de Paris), alimente https://veille.sorbonnesportbusiness.com et écrit un
récapitulatif dans `veille/`.

Ce fichier est relu à chaque lancement : modifier la cible ou une famille de recherche
suffit, sans toucher au workflow.

## Cible

SPORT BUSINESS uniquement : marketing, partenariats et sponsoring, commercial,
communication, contenus, événementiel, billetterie et hospitalités, fan experience,
merchandising, juridique, finance, stratégie. Stages, alternances et premiers emplois
jusqu'à 3 ans d'expérience.

En France, et à l'étranger en Europe (grands clubs, UEFA, FIFA, CIO, ligues, marques,
agences) pour les stages, graduate programmes et postes juniors. Hors d'Europe : écarter,
sauf programme ouvert aux étudiants étrangers.

Langue : l'intitulé ET le contenu de l'offre doivent être en français ou en anglais,
sinon l'offre est écartée (une annonce en allemand, espagnol, néerlandais... n'est pas
accessible aux étudiants).

## Règles communes à toutes les recherches

- Lis d'abord `skills/veille-ssb/SKILL.md` (règles, filtres, méthode, format d'une offre)
  et `skills/veille-ssb/references/portails.md` (où chercher, portails stériles).
  `skills/veille-ssb/references/sources.json` liste les sources déjà moissonnées par
  script : inutile de les refaire à la main.
- Une offre retenue a une page individuelle que tu as ouverte, elle est encore ouverte,
  publiée depuis moins de 2 mois, avec une `date_iso` précise. Lien employeur de préférence
  à un agrégateur. N'invente jamais d'offre.
- Aucun lien déjà présent dans `data/offres.json`, `skills/veille-ssb/references/historique.md`
  ou `out/candidats/AAAA-MM-JJ-api.json`. Ces fichiers sont gros : cherche-y le lien avec
  Grep, ne les lis pas en entier. Pas de plafond par employeur.
- Format de chaque offre : `titre`, `entreprise`, `categorie`, `secteur`, `localisation`
  (à l'étranger « Ville (Pays) »), `pays` (« France » ou le pays en français), `contrat`,
  `date_iso`, `date_pub` (avec « clôture JJ/MM/AAAA » quand elle est connue), `infos`
  (langue, droit de travail exigé), `lien`, `source`. Plus un `bilan` avec
  `detail_ecartees`, `portails_steriles` et `nouveaux_portails`.
- Écris tes offres dans `out/lots/AAAA-MM-JJ/<famille>.json` (même vide :
  `{"offres": [], "bilan": {...}}`), puis valide-le avec
  `python3 -c "import json;json.load(open('out/lots/AAAA-MM-JJ/<famille>.json'))"`.
- Toute nouvelle source qui répond en JSON ou en RSS avec des offres (types gérés par
  `skills/veille-ssb/scripts/harvest.py`, voir son en-tête) est à proposer dans
  `out/sources-proposees/AAAA-MM-JJ-<famille>.json`, au format de `sources.json`.
- N'écris aucun autre fichier.
- Personne n'est là pour approuver une commande : une commande refusée ne sera jamais
  acceptée. Avec Bash, une seule commande simple par appel : pas de `&` (arrière-plan),
  pas de chaînes avec `;`, `&&`, `|` ni de `$(...)`, pas de `cd`. Pour espacer deux
  requêtes, un appel `sleep 7` à part. Pour lire une page, WebFetch ; pour écrire un
  fichier, Write plutôt que `echo >` ou `cat <<`. Si une commande est refusée, passe par
  un autre outil plutôt que d'abandonner la famille.

## Familles de recherche

Chaque ligne lance une recherche séparée, en parallèle des autres. Le nom avant « : »
sert de nom de fichier.

- api : relecture des candidates du moissonneur (`out/candidats/AAAA-MM-JJ-api.json`). Garder seulement le sport business junior (intitulé + champ `_extrait`), écarter vente en magasin, logistique, IT, RH, santé, encadrement sportif, postes senior, début ou clôture déjà passés, hors Europe ; relever la date sur la fiche quand `date_iso` est vide (Pinpoint : JSON-LD datePosted), sinon écarter ; corriger `contrat` et `categorie` ; écrire `out/lots/AAAA-MM-JJ/api.json` sans les champs commençant par « _ ». Ajouter chaque candidate refusée en fin de `skills/veille-ssb/references/ecartees.txt` (une ligne « - AAAA-MM-JJ | employeur | intitulé | lien ») pour que le moissonneur ne la repropose plus (seule famille autorisée à écrire ce fichier).
- employeurs : portails employeurs de `portails.md` qui ne sont PAS dans `sources.json` (FFR Flatchr, Taleez CNOSF/FFF/OM, DigitalRecruiters Decathlon/Lacoste, Welcome Kit, softy.pro, GL events, careers.ol.fr, FDJ United, lemans.org...).
- linkedin : recherche LinkedIn sans connexion en France (25 requêtes et plus, 14 derniers jours, 5 à 9 s entre deux requêtes avec `sleep`), retracée vers la source employeur quand elle existe.
- agregateurs : HelloWork trié par date, et HelloWork par NOM DE CLUB seul (les clubs de Ligue 1, Ligue 2 et Top 14 y publient par lots), Sport Stratégies, Ecofoot, La Bonne Alternance, Meent, Wizbii, lesportrecrute.fr, talent.com.
- startups : startups, sportstech, esport, fitness, outdoor : nouveaux slugs d'ATS à tester (ceux de `sources.json` sont déjà moissonnés).
- federations : fédérations, ligues régionales, CROS.
- public : choisirleservicepublic.gouv.fr, emploi-territorial.fr, Ville de Paris.
- agences : agences, médias, sponsors, stades et événements en France.
- droit-finance : droit et finance du sport (Village de la Justice, Law Profiler, opérateurs de paris).
- annonceurs : sponsoring chez les grands annonceurs (banques, assurances, énergie, télécoms, automobile, distribution ; ex. Crédit Agricole « Stage - Chargé(e) de communication sponsoring »). Sites carrières des groupes + LinkedIn sans connexion (« stage sponsoring », « chargé de sponsoring », « partenariats sportifs », « parrainage sportif »).
- etranger : sources HTML de `portails.md` (Eintracht Frankfurt, Atlético, Club Brugge, Everton, UK Sport, adidas Herzogenaurach...), LinkedIn sans connexion par pays européen avec f_E=1 (« sports marketing intern », « football club internship », « sponsorship internship », « Praktikum Sportmarketing », « prácticas marketing deportivo »), et 5 grands clubs ou instances européens pas encore couverts (identifier leur ATS).

## Après les recherches

Le workflow fusionne les fichiers des familles dans `out/nouvelles.json` (doublons et
liens déjà livrés retirés par `merge_lots.py`). Ensuite :

1. Ajoute à `skills/veille-ssb/references/sources.json` les sources proposées dans
   `out/sources-proposees/` qui marchent vraiment : teste chacune avec
   `python3 skills/veille-ssb/scripts/harvest.py --sources skills/veille-ssb/references/sources.json --board data/offres.json --date AAAA-MM-JJ --out /tmp/test.json --only "<nom>"`.
2. Mets à jour `skills/veille-ssb/references/portails.md` : nouveaux portails, sources
   devenues stériles (voir les `bilan` des fichiers de `out/lots/AAAA-MM-JJ/`).
3. Écris le récapitulatif `veille/AAAA-MM-JJ.md` à partir de `out/nouvelles.json` :
   les 15 offres les plus intéressantes pour des étudiants de Master en sport business,
   classées par pertinence (Paris et Île-de-France d'abord). Format ci-dessous.

## Format du récapitulatif

```markdown
# Veille sport business du AAAA-MM-JJ

N nouvelles offres sur le site ce jour, dont les 15 plus pertinentes ci-dessous.
Toutes les offres : https://veille.sorbonnesportbusiness.com

## 1. Intitulé du poste, Entreprise

- **Contrat** : stage / alternance / CDI / CDD
- **Lieu** : ville (ou télétravail)
- **Publiée le** : JJ/MM/AAAA
- **Lien** : https://...
- **Pourquoi** : une phrase sur ce qui la rend intéressante.

## Sources

Une ligne par famille de recherche, avec le nombre d'offres retenues (0 compris) et les
sources bloquées.
```
