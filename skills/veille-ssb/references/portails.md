# Journal des portails carrières — Veille SSB

Ce fichier est la mémoire collective de la veille : chaque semaine, la personne qui lance
le skill met à jour cette liste (portails qui ont donné des offres, portails devenus
stériles, nouveaux portails découverts). Le skill `veille-ssb` lit ce fichier comme
référence avant de choisir où chercher.

Dernière mise à jour : 2026-10-15 au soir (moissonneur d'API et offres à l'étranger, voir plus bas).

## Portails employeurs validés (accès libre, fiables)

| Portail | Employeur | Dernière offre trouvée | Notes |
|---|---|---|---|
| jobs.fft.fr | FFT / Roland-Garros | 2026-10-07 | Très fourni, plafonner à 2 offres. Seules les 20 dernières offres s'affichent sans JS |
| carrieres.lfp.fr | LFP / LFP Media | 2026-10-07 | Teamtailor, uniquement des stages en ce moment |
| carrieres.alpes2030.org | COJOP Alpes 2030 | 2026-10-07 | Teamtailor, plus de 60 offres dont une vingtaine de stages début 2027. Flux `/jobs.rss` |
| parissaintgermain.wd3.myworkdayjobs.com/fr-FR/rejoigneznous | PSG | 2026-10-07 | Pages en JS mais fiches lisibles via l'API publique Workday (`/wday/cxs/parissaintgermain/rejoigneznous/jobs`) |
| jobs.world.luccasoftware.com/rejoignez-le-paris-basketball-et-participez-a-son-developpement-ambitieux | Paris Basketball | 2026-10-07 | La racine du domaine redirige vers lucca.fr : utiliser cette URL |
| federation-francaise-de-cyclisme.welcomekit.co | FFC | 2026-10-07 | |
| join.com/companies/parisladefense-arena | Paris La Défense Arena (Plenitude Arena) | 2026-10-07 | Dates et début visibles sur chaque fiche |
| careers.ol.fr/search | Olympique Lyonnais / Eagle Football Group | 2026-10-07 | SuccessFactors, date affichée par offre |
| careers.flatchr.io/fr/company/ffr | FFR | 2026-10-07 | Le site ffr.fr est 100 % JS, passer par Flatchr. 404 passagers possibles |
| cnosf.taleez.com | CNOSF | 2026-10-07 | API `https://<slug>.taleez.com/api/careez` (publishDate) |
| olympique-de-marseille.taleez.com | OM | 2026-10-07 | Fiches taleez.com/apply/... lisibles, indiquent si le recrutement est fermé |
| recrutement.lemans.org/search | ACO (24 Heures du Mans) | 2026-10-07 | « Publiée le » sur chaque fiche |
| carrieres.aso.fr | A.S.O. (Tour de France, Marathon de Paris) | 2026-10-07 | Flux `/jobs.rss`, souvent de la finance/comptabilité |
| carrieres.amaury.com | L'Équipe (groupe Amaury) | 2026-10-07 | Flux `/jobs.rss` |
| careers.wbd.com | Eurosport | 2026-10-07 | Chercher « France » |
| betclic-group.breezy.hr | Betclic | 2026-10-07 | `/json` liste tout |
| careers.fdjunited.com | FDJ United | 2026-10-07 | datePosted en JSON-LD |
| api.lever.co/v0/postings/winamax?mode=json | Winamax | 2026-10-07 | Surtout poker et tech, filtrer |
| api.smartrecruiters.com/v1/companies/<société>/postings?country=fr | Red Bull, Ubisoft, Salomon, Continental, Courir, JDE Peet's | 2026-10-07 | API publique, releasedDate |
| careers.essilorluxottica.com | EssilorLuxottica (partenariat LFP) | 2026-10-07 | |
| jobs.adidas-group.com | adidas France | 2026-10-07 | Trier par date, beaucoup de retail à filtrer |
| careers.lacoste.com/sitemap.xml, joinus.decathlon.fr/sitemap.xml | Lacoste, Decathlon | 2026-10-07 | Listes en JS ; API DigitalRecruiters `api.digitalrecruiters.com/public/v1/careers-site/job-ads` |
| inrecruitingfr.intervieweb.it/glevents | GL events (Stade de France, LOU Rugby) | 2026-10-07 | Flux JSON gl-events.com/fr/webgl_gl/get_hr_data |
| carrieres.lefebvre-dalloz.fr | Lefebvre Dalloz | 2026-10-07 | Stages PPI droit du sport |
| emplois.parisentertainmentcompany.com | Accor Arena / adidas arena | 2026-09-28 | Stérile le 2026-10-07 (postes techniques uniquement) |

## Agrégateurs et plateformes qui fonctionnent

- **HelloWork** : `hellowork.com/fr-fr/emploi/recherche.html?k=<mots>&st=date`. Chaque fiche
  `/fr-fr/emplois/<id>.html` contient un JSON-LD avec datePosted et validThrough. Meilleur
  agrégateur de la veille. Chercher par nom d'employeur seul, pas « employeur + mot-clé ».
- **La Bonne Alternance** : fiches `/emploi/<sub_type>/<id>/<slug>` avec « Publiée depuis X jours ».
  Garder seulement offres_emploi_lba et offres_emploi_partenaires.
- **Meent** (cabinet sport et entertainment) : wearemeent.com/nos-offres.
- **Sport Stratégies** : `sportstrategies.com/wp-json/wp/v2/offre-emploi?per_page=100&after=<date>`
  donne la liste datée ; le statut « Recrutement en cours » est sur la fiche.
- **GlobalSportsJobs** : API `hub.globalsportsjobs.com/api/vacancy` filtrable sur la France.
  Utile pour Sportfive, dont le site carrières bloque l'accès.
- **choisirleservicepublic.gouv.fr** : `/nos-offres/filtres/domaine/3507/date-de-publication/14_derniers_jours/`
  (jeunesse et sports). Ajouter `/experience/1835/` pour les débutants.
- **emploi-territorial.fr** : `/emploi-mobilite/?search-fam-metier=C5` (famille Sport des collectivités).
  User-Agent de navigateur obligatoire.
- **travaillerpourparis.offres.paris.fr** : offres de la Ville de Paris.
- **Village de la Justice** : `browse.php?cat=174` (stages), `cat=175` (alternance). Chercher
  « sport » dans les extraits. **Law Profiler** : `?page=offres&keyword=sport`.
- **Ecofoot** (ecofoot.fr/offres-emploi-sport) : relaie les posts LinkedIn des clubs.
- **LinkedIn sans connexion** : les fiches `/jobs/view/<id>` se lisent sans compte. Recherche :
  `linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=<mots>&location=France&f_TPR=r1209600`.
  Espacer les appels de 5 secondes ou plus (429 sinon). Ne livrer le lien LinkedIn que si
  l'employeur n'a pas de fiche ailleurs. Les petits clubs ne publient souvent que là.

## Ajouts du 2026-10-08 (veille élargie, 212 offres)

- **Sitemaps des sites carrières Teamtailor** (jobs.fft.fr, carrieres.lfp.fr, carrieres.alpes2030.org) :
  ils listent toutes les offres, la page d'accueil n'en montre que 9. Flux `/jobs.rss` aussi.
- **API publiques à interroger à chaque veille** : Workday PSG et Havas (`/wday/cxs/.../jobs`),
  DigitalRecruiters (Decathlon, Lacoste), Breezy Betclic (`/json`), Ashby EGYM et ScorePlay,
  Lever Trainsweateat et Winamax, SmartRecruiters (Salomon, Courir, Red Bull, Continental),
  Flatchr FFR, Welcome Kit (`<slug>.welcomekit.co` : Nutripure, Team Vitality, EBRA).
- **GlobalSportsJobs** (`hub.globalsportsjobs.com/api/vacancy`, filtre France) : seule porte
  d'entrée lisible vers Sportfive (Groupama Stadium, clubs commercialisés par Sportfive).
- **Crédit Agricole** : `groupecreditagricole.jobs/fr/nos-offres/mot-cles/<mot>/` (couvre LCL,
  CA Assurances, Amundi, caisses régionales). Seul grand annonceur avec un stage sponsoring sport ouvert.
- **LinkedIn sans connexion** : 10 cartes par page (paginer start=0, 10, 20). Requêtes les plus
  productives : partenariats, marketing sportif, événementiel sportif, communication club, club
  football, juriste sport. Bruit : billetterie, hospitalités, paris sportifs, golf, cyclisme.
- **Fédérations** : l'API WordPress media (`/wp-json/wp/v2/media?search=offre`) repère les fiches
  de poste PDF datées (FFHG, CPSF). careers.fia.com/rss.php pour la FIA.
- **Stériles ce jour** : Taleez (CNOSF, FFF, OM) refuse les connexions ; Jooble, TeamWork Online,
  Work In Sports (403) ; Hitmarker, Jobijoba, Meteojob (JS) ; ligues régionales *.fff.fr (403) ;
  sites carrières de SG, BPCE, EDF, Orange, TotalEnergies, SNCF (aucun poste sponsoring).

## Ajouts du 2026-10-09

- **Nouveaux portails productifs** : campsider.welcomekit.co (marketplace sport d'occasion, 4 stages) ;
  lawprofiler.com (et non .fr) `?page=offres&keyword=sport`, offres droit du sport datées (LFP, FFF) ;
  recrutement.angers.fr `/wp-json/wp/v2/job?per_page=100` ; fftri.com/nosoffres/bourse-a-lemploi (PDF datés) ;
  ffvolley.org/la-ffvb/emploi (PDF, dater par Last-Modified) ; ffs.fr/carrieres ; urbansoccer.softy.pro/offres.
- **group.bnpparibas** : 403 pour curl et WebFetch, mais les fiches se lisent dans le navigateur intégré
  (stage sponsoring tennis trouvé ainsi). L'API Workday BNP répond 422.
- **Accès précisés** :
  - GlobalSportsJobs : `api/vacancy?search=*&filter={"country":"France"}` (URL-encodé), ou la page
    `hub.globalsportsjobs.com/company/sportfive` pour Sportfive.
  - La Bonne Alternance : API publique `/api/v1/search?q=<mots>&hitsPerPage=100`.
  - emploi-territorial : `&page=N` renvoie N×20 offres d'un coup (familles C5, A6).
  - choisirleservicepublic : le filtre débutant ne marche que dans l'ordre
    `/domaine/3507/experience/1835/date-de-publication/14_derniers_jours/`.
  - CANAL+ : jobs.canalplus.com en 403, les stages se lisent sur HelloWork (« Canal Plus »).
  - Eurosport : POST `careers.wbd.com/widgets` avec le pays France.
  - FDJ United : `careers.fdjunited.com/fr/search-jobs/results?RecordsPerPage=300` (en-tête X-Requested-With).
  - fff.taleez.com/api/careez répond de nouveau.
- **ATS testés sans offre utile** : Infront (Teamtailor), Wasserman et Dentsu/MKTG (Workday), Fever et
  Genius Sports (Greenhouse), DAZN (RSS, rien en France), UTMB (Flatchr), Lagardère (RSS), France
  Télévisions, Basic-Fit (Workday, postes en club), Petzl (Flatchr), alltricks et webedia (Welcome Kit).
- **Bloqués ce jour** : sofoot.com, seetickets.com, jobs.layan.eu (Rossignol), ekoi.fr, unibet.fr, AXA,
  Allianz, RATP, Back Market (403) ; welcomekit.co en 429 après quelques appels ; HelloWork en 403
  au-delà de 8 requêtes parallèles (0,7 s entre fiches passe).
- **Stériles** : Village de la Justice (466 fiches, rien en sport), cabinets avec pratique sport, PMU
  (0 offre, passe par JobTeaser), ligues LNR/LNB/LNH/LNV, FFBB, Agence nationale du Sport, CDOS, INSEP,
  Ville de Paris (576 offres lues), annonceurs hors Crédit Agricole et BNP Paribas.

## Ajouts du 2026-10-12

- **HelloWork** : le JSON-LD est écrit `type="application/ld&#x2B;json"` (adapter les regex). `datePosted` est
  rafraîchi à chaque republication : l'identifiant donne l'ancienneté réelle (~84,3 M au 12/10, ~82,2 M vers le 12/08).
- **Accès corrigés** :
  - Havas : `wd3.myworkdaysite.com/wday/cxs/havas/GroupExternalCareerSite/jobs` (l'ancienne adresse répond 404).
  - DigitalRecruiters (Decathlon, Lacoste) : POST `api.digitalrecruiters.com/public/v1/careers-site/job-ads?domainName=<domaine>&limit=100&page=N&locale=fr_FR`
    corps `{"filters":{}}` ; fiche datée par GET `/job-ads/<id>?...&withJsonld=1`.
  - FDJ United : `/search-jobs/results` vide ; utiliser `careers.fdjunited.com/en/sitemap.xml` (fiche FR en remplaçant
    `/en/job/` par `/fr/emploi/`) ou paginer `/fr/search-jobs?p=N`.
  - ACO (recrutement.lemans.org) : rendu JS, lire au navigateur intégré.
  - GlobalSportsJobs : date et lien d'origine seulement sur `/vacancy/<slug>` (l'id UUIDv7 encode aussi la date).
  - La Bonne Alternance : ajouter `type_filter_label=Offres d'emploi partenaires` (sinon candidatures spontanées).
  - Meent : offres et publishDate embarquées dans le HTML de `/nos-offres`.
  - choisirleservicepublic : recherche `/nos-offres/filtres/mot-cles/<mot>/date-de-publication/14_derniers_jours/page/N/`.
  - emploi-territorial : `?search-type-contrat=06` (stages), `05` (apprentissage), combinable avec `&page=N`.
  - Village de la Justice : `browse.php?cat=20&offset=N` liste toutes les annonces.
- **Nouveaux portails** : compagniedesalpes.softy.pro/offers?page=N (domaines skiables, JSON dans `data-page`) ;
  SmartRecruiters `Ubisoft2` (et non `Ubisoft`) ; fftir.org `/wp-json/wp/v2/posts?search=offre` (PDF image) ;
  ffhandball.fr `/wp-json/wp/v2/internal-ad` et `external-ad` ; Fever Greenhouse `feverup` ; Workable
  (`apply.workable.com/api/v3/accounts/<slug>/jobs`, Two Circles) ; FFA Recruitee ; PMU `pmu-recrute.talent-soft.com`
  (0 offre) ; ANJ `choisirleservicepublic.gouv.fr/employeurs/330_autorite-nationale-des-jeux-anj_1/` ; TotalEnergies
  RSS `jobs.totalenergies.com/fr_FR/careers/SearchJobs/<mot>/feed/` ; Allianz, Orange et Société Générale lisibles au navigateur intégré.
- **LinkedIn** : « stage agence événementielle sport » fait remonter les petites agences (Eventeam, Ball'N Connect) ;
  les employeurs relayés par Profession Sport & Loisirs (ex. OSARC) ne publient que là.
- **Stériles ou bloqués ce jour** : Taleez CNOSF/OM/Mouratoglou (connexion refusée ; fff.taleez.com répond), Welcome
  to the Jungle (403), recrutement.fff.fr et ligues *.fff.fr (403), recrutement.ffe.com (Cloudflare), Macif (403),
  21 pages Welcome Kit de startups vides (Karmine Corp, Gymlib, Kiplin, Weezevent, Onefootball...), Eurosport via WBD,
  Sodexo Live!, Golazo (rien en France), Compagnie des Alpes sur JobTeaser (403, mais softy.pro marche), sites emploi
  des grandes villes (404 ou sans liste), Village de la Justice et Law Profiler (rien de nouveau en sport).
- **FFBB** : descriptions en image de PDF, missions et expérience invérifiables : offres écartées.

## Ajouts du 2026-10-15

- **GlobalSportsJobs a migré** : `hub.globalsportsjobs.com/vacancy/...` et `/api/vacancy` sont morts (redirection 200
  vers la liste `www.globalsportsjobs.com/jobs`, que la revérification de `publish.sh` prend pour une page vivante).
  Nouvelle API : `api.globalsportsjobs.com/api/jobs?location=France&limit=50` (max 50, paginer avec `nextCursor`),
  détail `api.globalsportsjobs.com/api/jobs/<id>` (status, isExpired, postedAt, applicationUrl). Les fiches
  `www.globalsportsjobs.com/jobs/<id>` sont en JS et `isGated` : livrer l'`applicationUrl` de l'employeur.
  Les 6 offres Sportfive encore ouvertes du tableau ont été repointées vers jobs.sportfive.com (403 en curl, lisible
  au navigateur intégré) ; le stage ADV Billetterie CSE, absent de l'API, a été retiré.
- **Nouveaux portails productifs** : hopscotch-recrute.talent-soft.com (Hopscotch Sport, Sport & Co, Le Public Système) ;
  careers.aroma-zone.com (Teamtailor, `/jobs.rss`, stage événementiel sportif) ; careers.danone.com (sitemap, équipe
  Sponsorship) ; FFBaD `frontwebservice.ffbad.org/api/career` (API datée) ; FFVoile `ffvoile_recrute.asp` (offres du
  siège, certains PDF morts) ; jobs.fft.fr héberge aussi les ligues et comités de tennis ; Accor Arena sur Teamtailor
  (`/jobs.rss`).
- **Accès précisés** :
  - softy.pro : offres dans `<script data-page="app">`, lien public par `softy_id` (pas `id`).
  - Workable : `GET apply.workable.com/api/v1/widget/accounts/<slug>` donne tout sans 429 (Two Circles = `twocircles`).
  - Welcome Kit : `datePosted` dans le code de la fiche ; le slug d'URL peut mentir sur l'intitulé (Campsider).
  - DigitalRecruiters : la fiche détaillée se lit avec `job_ad_id` seul.
  - emploi-territorial : `?adv-search=<mot>&page=N` trouve des postes sport hors famille C5 ; la référence
    `O<dép><AAMMJJ>` donne la date de première publication (repère les republications).
  - choisirleservicepublic : filtre ministère des Sports `/nos-offres/filtres/organisme/44/`.
  - LinkedIn : l'ID d'un post donne sa date (`id >> 22` = millisecondes). 105 requêtes à 5-9 s passent sans 429 bloquant.
  - Ecofoot : les boutons « Voir l'offre » mènent directement chez l'employeur (Workday PSG, careers.ol.fr, jobs.fft.fr).
  - orange.jobs : POST `/widgets` ; API Workday publiques de Coca-Cola, Renault et Pernod Ricard ; SmartRecruiters Accor.
- **Employeurs qui ne publient que sur LinkedIn** : GiG (stages paris sportifs à Labège), KENEO/Eventeam, Spartner,
  STRADA Marketing (commerciaux teamwear adidas), Aono (présentation sportive), Potel et Chabot (Roland-Garros, Hosco refuse).
- **Slugs ATS valides mais sans offre utile** : Ashby fnatic ; Lever teamsnap ; Greenhouse catapultsports, riotgames,
  kambi, betsson ; Teamtailor shotgun, teamliquid, endeavor ; Breezy img ; Recruitee ticketswap.
- **Stériles ou bloqués ce jour** : Village de la Justice (fiches « rubrique Emploi désactivée » après une attaque,
  retour annoncé le 16/10) ; Law Profiler (31 mots-clés, rien) ; Meent, La Bonne Alternance (bruit) ; Ville de Paris
  (584 offres) ; Agence nationale du Sport (page emploi 404) ; France Télévisions, JobTeaser, Ironman, Le Public
  Système, Auditoire, Uniteam (403 ou connexion refusée) ; lesportrecrute.fr, recrutement.ffe.com, *.fff.fr ; Taleez
  Mouratoglou ; Société Générale (JS) ; BNP Paribas (403) ; CANAL+ (aucun stage sport).

## Ajouts du 2026-10-15 (soir) : moissonneur d'API et étranger

- **Moissonneur** : `scripts/harvest.py` lit toutes les sources de `references/sources.json` (55 au 15/10) en une
  minute et écrit les candidates dans `out/candidats/<date>-api.json`. Types gérés : workday, smartrecruiters, lever,
  greenhouse, ashby, teamtailor, workable, breezy, recruitee, personio, pinpoint, jobylon, schema_feed (softgarden),
  rss / successfactors_rss, globalsportsjobs. Ne plus interroger ces sources à la main : chercher ailleurs et ajouter
  toute nouvelle source à API dans `sources.json`.
- **GlobalSportsJobs** : branché dans le moissonneur, 12 pays européens, `careerStage=0` (stages et jobs étudiants) ;
  `q=intern` filtre par mot-clé. Le lien livré est l'`applicationUrl` de l'employeur (fiche GSJ réservée aux membres).
- **Étranger, sources validées (API)** : UEFA et EFC (Jobylon 2972 et 3210), FIFA (`jobs.fifa.com/jobs.rss`), CIO
  (RSS SuccessFactors `ioc.jobs.hr.cloud.sap`), OBS, Formula E, Premier League et Manchester United (Pinpoint, sans date :
  la relever sur la fiche), Borussia Dortmund (`karriere.bvb.de/jobs.feed.json`), PSV (Recruitee `psv`), Arsenal et
  Juventus (Teamtailor), City Football Group (RSS), DFB (Personio), Infront (Teamtailor), Red Bull (SmartRecruiters
  mondial, très bruyant : regex `exclure`), Sportradar, Entain, PUMA, Nike, The North Face, CAA, IMG, Wasserman,
  Two Circles, Riot, ESL FACEIT, Genius Sports, On, Strava, WHOOP, Amer Sports, DAZN.
- **Étranger, HTML ou navigateur seulement** : Eintracht Frankfurt `klub.eintracht.de/jobs/ag/` (dates de clôture,
  pas de publication) ; Atlético de Madrid `/ofertas` (date en clair) ; Club Brugge `jobs.clubbrugge.be/en` ; Everton
  (sitemap + JSON-LD) ; Ajax (AFAS, JS) ; Tottenham (iTrent) ; West Ham (inRecruiting, jeton CSRF) ; Chelsea (API UKG
  Ready sans date) ; World Rugby / RWC 2027 (XML SuccessFactors sans date) ; WADA (BambooHR `wada.bamboohr.com/careers/list`) ;
  World Aquatics (Lucca) ; UK Sport `uksport.gov.uk/jobs-in-sport/search-all-vacancies?pg=N` (34 pages, agrégateur
  britannique lisible) ; adidas `jobs.adidas-group.com/search/?q=intern&locationsearch=Herzogenaurach&sortColumn=referencedate&sortDirection=desc`.
- **LinkedIn à l'étranger** : même recherche sans connexion avec `location=<pays en anglais>&f_E=1` (stages). La date
  exacte est dans `<time datetime>` des cartes de recherche ; `id >> 22` ne marche pas sur les ID `/jobs/view`.
  Employeurs trouvés ainsi : FC Bayern, Werder Brême, 1. FC Köln, Lidl-Trek, Würth, HYROX, Wimbledon, NAC Breda,
  Albert Heijn (stage sponsoring), Sportium.
- **Règle de langue (2026-10-16)** : intitulé et contenu en français ou en anglais, sinon l'offre est écartée.
  Conséquence : la plupart des clubs et fédérations allemands, néerlandais et espagnols (DFB, DFL, Bayern, BVB,
  PSV, LaLiga, Infront Allemagne) ne donnent rien ; les sources utiles à l'étranger sont celles qui recrutent en
  anglais (UEFA, FIFA, CIO, Premier League, clubs anglais, Red Bull graduate programmes, adidas, PUMA, agences).
- **Règle étranger** : Europe seulement (France, Royaume-Uni, Espagne, Italie, Allemagne, Suisse, Benelux, Portugal,
  Monaco, Irlande, Autriche, pays nordiques, Pologne), postes juniors explicites. Les stages américains (PGA Tour, MLB,
  ESPN, Nike Beaverton, LA28) exigent le droit de travailler aux États-Unis : écartés.
- **France, nouveaux** : BOOST (cabinet de recrutement 100 % sport, Teamtailor, mandats AJ Auxerre, ESTAC, Winamax,
  Asics), TOCA Social (Workable), Sorare (Ashby, tech seulement).
- **Bloqués ou stériles** : jobsinfootball, sportbusiness.com, teamworkonline, workinsports (403) ; Formula 1 (Workday 422) ;
  ATP, DP World Tour, America's Cup (403) ; Bayern et Feyenoord (timeout) ; Real Madrid et AC Milan (pas de portail) ;
  LaLiga, WADA, World Athletics (aucune offre ouverte hors candidature spontanée) ; clubs de Ligue 1 et Top 14 toujours
  sans ATS (LinkedIn seulement) ; stades français sans site carrières.

## Ajouts du 2026-10-16 : France

- **Moissonneur** : 84 sources. Nouveaux lecteurs : DigitalRecruiters (Decathlon, Lacoste), Taleez (FFF, OM, CNOSF ;
  refuse parfois les connexions), Flatchr (FFR), WordPress (Intersport, VMATCH, CVsportsjob). Mémoire des refus :
  `references/ecartees.txt` (le moissonneur ne repropose pas une offre déjà refusée à la relecture).
- **Nouvelles sources France** : Intersport France (WordPress, 885 offres, regex `exclure` pour le magasin) ; Eventeam
  Group / KENEO (Teamtailor `recrutement.eventeam-group.com`) ; JD Sports France (Greenhouse `jdsportsfr`) ; Basic-Fit
  (Workday, surtout clubs) ; annonceurs en filtre « sport » : Pernod Ricard, Mondelez, Coca-Cola (Workday), ENGIE,
  TotalEnergies (flux « sponsoring »), MAIF, Groupama Gan, Matmut, Air France (RSS Talentsoft, 20 dernières offres) ;
  conseil : Roland Berger (SmartRecruiters), PwC (Workday), BearingPoint, Comexposium, RELX/LexisNexis.
- **Agrégateurs** : Wizbii (page entreprise + offre en JSON sans compte), Talentview (groupe SSM : Spartner, RnK,
  Novabox ; JSON avec en-tête Origin), talent.com (date sur la fiche, lien employeur derrière un anti-robot : retrouver
  l'offre par son intitulé), lesportrecrute.fr de nouveau lisible en curl, France Travail (liste en curl, détail au
  navigateur), fac de sport de Strasbourg (RSS F3S).
- **Clubs pros (sondage de 78 entités le 16/10)** : aucun ATS public avec des offres. Ils publient sur HelloWork par lots
  (multidiffuseur) : chercher le NOM DU CLUB seul sur HelloWork (Stade Rennais, FC Lorient, FC Metz, Stade Toulousain,
  Stade Rochelais...) et sur LinkedIn. Taleez coupe l'IP une quinzaine de minutes après une dizaine de requêtes.
  Bourse de l'emploi FFGolf : HTML, 77 offres, filtres marketing et stage. Racing 92 : join.com vide.
- **Bloqués ou stériles** : optioncarriere, jobted (anti-robot JS) ; cadremploi, keljob, emploi.lefigaro, monster, AXA,
  intersport.fr, Fidal, Fieldfisher, Kearney (403) ; iquesta (connexion) ; Village de la Justice encore en 403 le 16/10 ;
  Workday 422 pour Live Nation/Ticketmaster, Renault, L'Oréal ; écoles (AMOS, ISC, ESSCA, ESSEC) via JobTeaser seulement.

## Portails stériles ou bloqués (à retester occasionnellement)

- **Bloqués** : welcometothejungle.com (403, ce qui cache l'esport, la sportstech et les petites
  agences), jobteaser.com (403), jobs.sportfive.com (403), group.bnpparibas (403), apec.fr et
  indeed.fr (403), lesportrecrute.fr (Cloudflare).
- **Payant** : app.lecafedusportbiz.fr (employeurs réservés aux membres Premium).
- **Jamais fiable** : sportjobshunter.com (affiche des offres closes comme ouvertes).
- **Sans offre utile au 2026-10-07** : Team Vitality, FFVoile, Agence nationale du Sport, AFLD, ANJ,
  ligues LNR/LNB/LNH/LNV (LinkedIn seulement), clubs sans portail (OGC Nice, Strasbourg, Brest,
  TFC, Auxerre, Angers, ASSE, Metz, Racing 92, Stade Français, ASM, UBB, Castres, Bayonne, USAP,
  Stade Toulousain, ASVEL, LOSC, RC Lens, FC Nantes), équipes cyclistes, Big Four (aucun poste
  sport), cabinets d'avocats (Racine, De Gaulle Fleurance, Joffe, Delsol), Riot, DAZN, Octagon,
  Two Circles, Puma, Nike France (retail seulement), PASS (stages de la fonction publique).

## Mise à jour du 2026-10-17

- **Nouveaux portails** : Wellhub (Greenhouse gympass, ajouté à sources.json) ; Paris La Défense Arena (join.com, createdAt dans
  __NEXT_DATA__) ; careers.lagardere.com/jobs.rss (Teamtailor) ; jobs.makesense.org (JSON-LD, relaye KCO et agences événementielles) ;
  Hopscotch (talent-soft, flux offerRss.ashx?LCID=1036) ; FFC et FF Cyclisme Welcome Kit (datePosted en JSON-LD) ;
  FFBaD frontwebservice.ffbad.org/api/career (JSON daté, pas de type harvest.py) ; GL events get_hr_data (JSON, peu de sport) ;
  careers.ol.fr (/search/?q=&sortColumn=referencedate&sortDirection=desc) ; Ville de Paris : travaillerpourparis.rec.paris.fr/search.
- **Stériles ou bloqués ce jour** : ecofoot.fr (connexion en échec), talent.com (anti-robot), lesportrecrute.fr (SPA illisible en curl),
  Village de la Justice (404), ffgolf.org (404), fftri, ffvoile, ffbb, ffjudo, ffhandball, cnosf, cros-idf, ffs.fr (JS), Club Brugge,
  Atlético (espagnol), Everton, UK Sport, adidas Herzogenaurach, Paris Entertainment Company, Lefebvre Dalloz, recrutement.lemans.org (JS),
  Paris Basketball (Lucca, JS), Octagon (postes Asie-Pacifique), Law Profiler (rien de nouveau), emploi-territorial et choisirleservicepublic
  (encadrement seulement).
- **Clubs anglais sans ATS public** (Leeds, Newcastle, Tottenham, Norwich) : LinkedIn sans connexion avec « partnerships assistant »,
  « fan engagement intern ».

## À tester

Mouratoglou Academy (Taleez refuse encore les connexions le 2026-10-15), Village de la Justice (retour annoncé le 16/10),
Alltricks (republications en masse : 3 stages retenus le 2026-10-15 avec début au 01/11).
Testés le 2026-10-12 : Sodexo Live! et Golazo (rien en France), Compagnie des Alpes (validé via softy.pro).
Testés le 2026-10-09 sans portail lisible : FFBB, Karmine Corp, Solary, Weezevent.

## Mise à jour du 2026-10-17 (relecture)

- **Nouveaux portails** : Ecofoot de nouveau lisible (59 offres, liens employeurs) ; HelloWork par nom de club (Eagle Football Group/OL
  publie par lots) ; HelloWork k=fédération française&st=date (158 offres, relais FFVolley, FFR, FFHG, FFT) ; LinkedIn
  jobs-guest/jobs/api/seeMoreJobPostings/search (HTML) et jobPosting/<id> via WebFetch, sans connexion (429 si requêtes enchaînées).
- **Stériles ou bloqués ce jour** : carrieres.amaury.com, sportstrategies.com, joinus.canalplus.com (WebFetch refusé) ; indeed (403) ;
  wearemeent.com ; careers.accorarena.com/jobs.rss ; fff.taleez.com (vide) ; ffvolley.org/la-ffvb/emploi ; LinkedIn Suisse (429) ;
  FFBaD career API (encadrement seulement) ; Lawprofiler et Lefebvre Dalloz (seniors ou hors sport) ; Greenhouse gymshark, zwift,
  peloton, hudl, twitch (sans offre utile) ; choisirleservicepublic et emploi-territorial (rien de junior).

## Ajouts du 2026-10-19
- **Nouveaux portails** : aucun ; aucune source proposée en JSON ou RSS ce jour.
- **Stériles ou bloqués ce jour** : careers.accorarena.com (domaine introuvable), careers.lagardere.com/jobs.rss (pas de sport),
  careers.fdjunited.com (déjà connus), softy.pro Compagnie des Alpes ; sportbuzzbusiness.fr (annonces de 2013-2015), jobteaser (403),
  WTTJ (recherche illisible) ; sportstrategies.com et joinus.canalplus.com (WebFetch refusé) ; talent.com (États-Unis seulement),
  lesportrecrute.fr et wearemeent.com (pas de lien individuel), La Bonne Alternance API (404) ; ffbad.org, fftt.com, ffhandball.fr (404),
  ffa.fr, cnosf.org (DNS), franceolympique.com (certificat) ; choisirleservicepublic, emploi-territorial, Ville de Paris (rien de sport) ;
  Village de la Justice (404) ; UK Sport (coaching) ; Greenhouse/Lever/Ashby/Recruitee des startups testées (404 ou vides ; SmartRecruiters
  répond 200 vide pour tout slug inconnu) ; LinkedIn guest : 429 sous 6 s entre deux requêtes, les mots-clés avec OR donnent du bruit.

## Ajouts du 2026-10-20
- **Nouveaux portails** : aucun ; aucune source proposée en JSON ou RSS ce jour.
- **Stériles ou bloqués ce jour** : OM Taleez (liste vide), GL events get_hr_data (rien de junior sport), Club Brugge (aucune offre),
  Celtic FC (JS), Liverpool FC et Newcastle United (404), UK Sport (Head of Commercial senior), careers.havas.com et beIN (DNS),
  sportfive.com/careers (403), aso.fr et lequipe.fr (WebFetch refusé), sportstrategies.com, Meent (pas de lien individuel),
  La Bonne Alternance API (404), recrutement.credit-agricole.com (DNS), Village de la Justice (404), ffbad.org et ffgolf.org (404),
  jobteaser FFBaD (403), ffnatation.fr (encadrement), emploi-territorial, choisirleservicepublic, Ville de Paris (rien de sport) ;
  Greenhouse, Ashby, Lever, Recruitee, Personio, Workable des startups sportstech testées (404) ; career.hyrox.com (DNS) ;
  LinkedIn guest : 429 après environ 8 requêtes (pause de 20 s nécessaire), Pays-Bas en 429.

## Ajouts du 2026-10-22
- **Nouveaux portails** : aucun en JSON ou RSS ; pages HelloWork `/stage/mot-cle_<mot>.html` et `/alternance/mot-cle_<mot>.html`
  (evenementiel-sportif, marketing-sportif) lisibles avec date relative ; LinkedIn par nom d'agence (« Publicis Sport stage »,
  « Havas Play stage ») productif pour les agences sport des grands groupes.
- **Stériles ou bloqués ce jour** : LinkedIn jobs-guest API (404, utiliser linkedin.com/jobs/search?...&f_E=1&f_TPR=r1209600),
  sportbuzzbusiness.fr/emploi (404), join.com Paris La Défense Arena (404), careers.lagardere.com RSS (édition seulement),
  sportstrategies.com et joinus.canalplus.com (WebFetch refusé), welcometothejungle LFP (403), PSG Workday fiche 014988 (page vide),
  group.bnpparibas (403), careers.fdjunited.com (rien de sport junior), careers.ol.fr, lemans.org, softy.pro, Welcome Kit (déjà vus),
  Eintracht Frankfurt (allemand seul), ffr.fr/emploi (vide), cros-idf.fr (DNS), ffgolf.org (404), Law Profiler, Village de la Justice (404),
  choisirleservicepublic, emploi-territorial, Ville de Paris (rien de sport), Greenhouse, Lever, Ashby, Recruitee des startups (404).
- **Non consultés ce jour** : Wizbii, La Bonne Alternance, Meent, lesportrecrute.fr, talent.com.

## Ajouts du 2026-10-23
- **Nouveaux portails** : aucun en JSON ou RSS ; frontwebservice.ffbad.org/api/career?page=2 (86 offres, dernières en page 2) et
  ffnatation.fr/la-ffn/on-recrute (HTML, surtout encadrement) à examiner ; Personio sportec-solutions valide mais sans offre utile ;
  LinkedIn jobs-guest seeMoreJobPostings répond de nouveau via WebFetch (28 requêtes sans 429, 6 à 8 s d'écart).
- **Stériles ou bloqués ce jour** : sportstrategies.com et joinus.canalplus.com (WebFetch refusé), welcometothejungle (403),
  careers.fdjunited.com, ffr Flatchr, GL events get_hr_data, careers.danone.com (sitemap trop gros), Club Brugge (aucune offre),
  UK Sport (postes seniors), LinkedIn Allemagne (429), ffgolf.org (404), ffvoile.fr (erreur serveur), fftt.com (404),
  Village de la Justice (404), Law Profiler (rien de junior), choisirleservicepublic, emploi-territorial, Ville de Paris (rien de sport),
  Greenhouse, Ashby, Lever, Recruitee, Personio, Teamtailor des startups sportstech (404 ou sans offre), career.zwift.com et
  karriere.rb-leipzig.com (DNS), recherches annonceurs (banques, assureurs) sans résultat exploitable.

## Ajouts du 2026-10-23 : alternance, droit du sport, CDI en Île-de-France

Ajoutées au moissonneur (sources.json) :
- Olympique Lyonnais / Eagle Football Group (careers.ol.fr, RSS SuccessFactors), Hopscotch Groupe (RSS Talentsoft, filtre sport), adidas France (RSS SuccessFactors `locale=fr_FR&keywords=France`), Sport Stratégies (WordPress `offre-emploi`, l'employeur et le contrat sont sur la fiche, « Recrutement terminé » = close).
- Paris Entertainment Company (Accor Arena, adidas arena, Teamtailor), On Air Fitness siège (WordPress).
- Droit : Groupe TF1 (RSS `keywords=sport`), Lefebvre Dalloz (Teamtailor, stage « droit du sport » chaque semestre), De Gaulle Fleurance et Bignon Lebray (cabinets à pratique sport, filtre sport), AFLD (PDF d'offres via WordPress media).

Portails à lire à la main (pas d'API exploitable) :
- Droit : Village de la Justice `browse.php?cat=20&offset=0..1940`, pas de recherche par mot-clé, filtrer « sport » soi-même ; Law Profiler `?page=offres&keyword=sport` ; cabinets Racine, Joffe & Associés, LPA-CGR (simply-jobs), SAJET Avocats (pratique Sports et Médias). August Debouzy et FTPA en 403 le 23/10. TAS : aucun poste. Carrières-Juridiques : 0 offre en droit du sport.
- CDI Île-de-France : join.com/companies/parisladefense-arena (Plenitude Arena, Racing 92, datePosted sur la fiche) ; GL events `webgl_gl/get_hr_data` (JSON de 69 offres avec years_of_experience, dont la société d'exploitation du Stade de France) ; Paris FC renvoie vers LinkedIn ; Paris Basketball (Lucca, JavaScript) ; Viparis sur WTTJ (bloqué) ; Fitness Park et Neoness hébergés par HelloWork.
- Alternance : La Bonne Alternance, fiches lisibles sans compte, mais l'API officielle demande une clé et l'API du site refuse la pagination (pas de lecteur) ; la date de publication est remise à zéro à chaque import. HelloWork `c=Alternance` : environ 75 % d'offres d'écoles.

Règles apprises :
- Une offre d'école (WIN Sport School, School of Sports, ECS...) pour une « entreprise partenaire » anonyme est écartée : postuler revient à s'inscrire dans l'école.
- LinkedIn affiche les republications avec une date récente : contrôler la date d'origine chez l'employeur. Le filtre f_E (niveau d'expérience) ne filtre pas.
- Le moissonneur garde désormais les « Account / Community / Event / Brand... Manager » et « Business Developer » en France (premiers CDI fréquents), et les intitulés juridiques qui contiennent IT, RH, construction, fraude. La relecture lit l'expérience demandée.
- Faux homonymes d'ATS : Greenhouse `psg` (société indienne), Breezy `hopscotch` (Afrique du Sud), SmartRecruiters `asics` (Australie), Teamtailor `fitnesspark` (Espagne), Recruitee `lecoq` (garage).

## Ajouts du 2026-10-26

Aucune source JSON ou RSS proposée ce jour : `sources.json` inchangé.

- **Utiles** : Ecofoot lisible en WebFetch (liens employeurs et LinkedIn, déjà couvert en majorité) ; HelloWork en requêtes thématiques (stage hospitalités, stage rugby, stage football) pour ACO, Canal+, TF1 ; ffhockey.org `emploi-formation/bourse-a-l-emploi.html` (10 offres lisibles, sans date de publication) ; ffnatation.fr `la-ffn/on-recrute` (daté, surtout encadrement).
- **Stériles ou bloqués ce jour** : La Bonne Alternance (API 404, page vide sans JavaScript), lesportrecrute.fr (aucun lien individuel), talent.com (éducateurs et écoles), Wizbii (404), sportstrategies.com (WebFetch bloqué), HelloWork par nom de club (Stade Français, Stade Toulousain, LOSC, Reims, Strasbourg, Racing 92, Pau, UBB, USAP, Bayonne : 0 offre), careers.flatchr.io FFR (308), OM Taleez (vide), fff.taleez.com (2 offres seniors), Club Brugge (aucune offre), ffgolf.org, fftt.com, ffjudo.com, sports.gouv.fr (404), ffhockey.org (403 en curl), choisirleservicepublic.gouv.fr (listes vides au fetch), Lever (sorare, spartner, gotenna, sportsmanagement), Greenhouse (ticketmaster, dazn, matchroomsport, sportsbet), Ashby (sportradar, hudl, onefootball), SmartRecruiters Decathlon1 : 404 ou vides. LinkedIn : recherches sponsoring, finance, fan expérience et UK « sports marketing intern » très bruyantes.

## Ajouts du 2026-10-29

Aucune source JSON ou RSS proposée ce jour : `sources.json` inchangé.

- **Utiles** : Ecofoot lisible en WebFetch (59 offres avec liens employeurs, déjà couvertes en grande partie) ; Greenhouse `hudl` (valide, 1 poste borderline à Londres sans date), `peloton`, `twitch`, `fanduel` (valides, rien de junior sport business en Europe).
- **Stériles ou bloqués ce jour** : sportstrategies.com (WebFetch refusé), La Bonne Alternance (résultats en JavaScript, API 401), Wizbii (404), lesportrecrute.fr, Meent, talent.com, OM Taleez (liste vide), FFR Flatchr (encadrement seulement), choisirleservicepublic.gouv.fr (résultats non rendus), Village de la Justice cat=20 (aucune annonce sport), racine.eu/fr/carrieres (404), ffgolf.org, ffjudo.com, fftt.com, ffessm.fr (404), ffbb.com/emploi (403), cros-idf.fr (DNS), ffvoile.fr (erreur), UK Sport (aucun junior). Greenhouse statsperform, onefootball, sportsengine, underarmour, blast, dazn ; Lever sportradar, kinexon, vitality, sorare, spartner, sportmonks ; Ashby sportsbet, oura, kickoff, vitality, sportable : 404. Recruitee vitality, karminecorp, blast : 401. LinkedIn guest : 429 après environ 22 requêtes à 6 s (pause de 20 s suffisante), 502 fréquents sur les fiches ; mots-clés avec OR bruyants.
