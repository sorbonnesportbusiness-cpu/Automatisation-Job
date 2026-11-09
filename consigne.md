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
- droit : droit du sport junior (stages, élèves-avocats, alternance, juriste et collaborateur jusqu'à 3 ans), en Île-de-France d'abord. Village de la Justice : parcourir `https://www.village-justice.com/annonces/browse.php?cat=20&offset=0` à `offset=1940` (20 annonces par page) et garder celles qui disent « sport » dans l'intitulé, le recruteur ou le résumé. Law Profiler `?page=offres&keyword=` sport, football, rugby, fédération, ligue. HelloWork `k=stage+juridique+sport` et `k=juriste+sport` triés par date. choisirleservicepublic mot-clé « chargé d'affaires juridiques » (Direction des sports). Pages des cabinets à pratique sport (Racine, Joffe & Associés, LPA-CGR, SAJET, August Debouzy). LinkedIn sans connexion : « juriste sport », « droit du sport », « élève avocat sport », « juriste paris sportifs ». Écarter les stages juridiques de diffuseurs dont les missions ne parlent pas de sport, et les republications déjà refusées dans `ecartees.txt`.
- finance : finance du sport (contrôle de gestion, audit, M&A et conseil sport chez les clubs, ligues, opérateurs de paris, fonds et cabinets à pratique sport), sur LinkedIn sans connexion et les sites carrières.
- alternance : alternances sport business (apprentissage, contrat pro) en France, Île-de-France d'abord. La Bonne Alternance (fiches /emploi/..., recherches partenariats, événementiel sportif, marketing sportif, communication sport ; vérifier la date d'origine chez l'employeur, car la date est remise à zéro à chaque import), HelloWork `c=Alternance&st=date` par métier et par nom de club, LinkedIn sans connexion « alternance » + métier, Sport Stratégies (type de contrat Alternance). Écarter les offres d'écoles pour une « entreprise partenaire » anonyme et la vente en magasin ou en salle.
- cdi-idf : premiers emplois (CDI, CDD de 6 mois et plus, 0 à 3 ans d'expérience lus sur la fiche) en Île-de-France. join.com/companies/parisladefense-arena (Plenitude Arena, Racing 92) ; GL events `https://www.gl-events.com/fr/webgl_gl/get_hr_data` (lignes Paris et Saint-Denis, champ years_of_experience) ; GlobalSportsJobs `api.globalsportsjobs.com/api/jobs?location=France&careerStage=1` puis `=2` (lien employeur via applicationUrl du détail) ; LinkedIn sans connexion `linkedin.com/jobs/search?keywords=<mot>&location=Île-de-France&f_TPR=r1209600` (5 à 9 s entre deux requêtes) avec les noms d'employeurs (PSG, Paris FC, Racing 92, Stade Français, Paris Basketball, FFF, FFR, LNR, SPORTFIVE, KENEO, Havas Play, FDJ United, Betclic, Winamax, adidas, Nike, Lacoste) et les métiers (billetterie, hospitalités, partenariats sport, sponsoring, marketing sportif, commercial sport) ; f_E ne filtre pas, lire l'expérience sur `linkedin.com/jobs-guest/jobs/api/jobPosting/<id>`. HelloWork `l=Île-de-France&c=CDI&st=date`. Contrôler la date d'origine chez l'employeur, car LinkedIn affiche les republications. Écarter la vente en magasin et en salle, le coaching et l'IT.
- annonceurs : sponsoring chez les grands annonceurs (banques, assurances, énergie, télécoms, automobile, distribution ; ex. Crédit Agricole « Stage - Chargé(e) de communication sponsoring »). Sites carrières des groupes + LinkedIn sans connexion (« stage sponsoring », « chargé de sponsoring », « partenariats sportifs », « parrainage sportif »).
- etranger : sources HTML de `portails.md` (Eintracht Frankfurt, Atlético, Club Brugge, Everton, UK Sport, adidas Herzogenaurach...), LinkedIn sans connexion par pays européen avec f_E=1 (« sports marketing intern », « football club internship », « sponsorship internship », « Praktikum Sportmarketing », « prácticas marketing deportivo »), et 5 grands clubs ou instances européens pas encore couverts (identifier leur ATS).

## Passe LinkedIn connectée (Mac)

En plus des familles ci-dessus, et sans les remplacer. Après la veille, le job `linkedin` du
workflow tourne sur le Mac de Tom (runner auto-hébergé, étiquette `ego`), dans le navigateur
Ego Lite où son compte LinkedIn est ouvert. Si le Mac est éteint, GitHub garde le job en
attente (24 h au plus) et il part dès que le Mac se rallume.

1. `skills/veille-ssb/scripts/ego_linkedin.py` fait les recherches, seul, en lecture seule :
   les requêtes larges (« sports industry », « sport business », « industrie du sport »), puis
   celles des familles linkedin, cdi-idf, alternance, annonceurs, finance, droit, etranger,
   agences, federations et startups à tour de rôle, et des recherches de posts
   (`skills/veille-ssb/references/ego-requetes.json`). Budget par passage : 25 recherches
   d'offres et 15 de posts, une page de résultats chacune, 5 à 9 s d'écart. Il lit ensuite
   chaque fiche par la version publique de LinkedIn, sans le compte, et écrit
   `out/candidats/AAAA-MM-JJ-ego.json` (`_famille`, `_type` offre ou post, `_extrait`,
   `_criteres`, `_lien_employeur`). Sur une vérification, un CAPTCHA ou une déconnexion, il
   s'arrête et le note dans `bloque`.
2. Relecture (une session Claude) : applique les règles communes et la cible à chaque
   candidate, comme la famille api, puis écris un lot par famille,
   `out/lots/AAAA-MM-JJ/ego-<famille>.json` (`ego-posts.json` pour les posts), même vide.
   - Offre : lis `_extrait` et `_criteres`. Écarte ce qui demande plus de 3 ans d'expérience
     ou n'est pas du sport business. Lien livré : `_lien_employeur` ou l'offre retrouvée chez
     l'employeur quand elle existe (vérifie-la), sinon `https://www.linkedin.com/jobs/view/<id>`.
     LinkedIn affiche les republications : quand l'offre existe chez l'employeur, prends sa
     date d'origine.
   - Post : garde seulement un vrai poste proposé par l'auteur ou sa structure (pas un
     étudiant qui cherche un stage, pas une formation, pas une école pour une « entreprise
     partenaire » anonyme). Si le post renvoie vers une offre (`_liens`), vérifie cette offre
     et livre son lien. Si le post est lui-même l'annonce, livre le lien du post
     (`linkedin.com/posts/...` dans `_liens`) ; sans lien vérifiable, écarte. `date_iso` = date
     du post ou de l'offre.
   - N'utilise jamais ego-browser ni le compte LinkedIn : lis les pages avec WebFetch ou curl.
   - Ajoute les candidates refusées à `skills/veille-ssb/references/ecartees.txt`, comme la
     famille api.
3. Le job fusionne les lots `ego-*`, lance `site/publish.sh`, ajoute une section « Passe
   LinkedIn connectée » au récapitulatif `veille/AAAA-MM-JJ.md` et pousse sur main.

Le compte est le vrai profil de Tom : lecture seule (jamais de candidature, de message,
d'alerte ni de réglage), budget fixe, arrêt sur toute vérification. Ne relève pas le budget
sans son accord.

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
