# Journal des portails carrières — Veille SSB

Ce fichier est la mémoire collective de la veille : chaque semaine, la personne qui lance
le skill met à jour cette liste (portails qui ont donné des offres, portails devenus
stériles, nouveaux portails découverts). Le skill `veille-ssb` lit ce fichier comme
référence avant de choisir où chercher.

Dernière mise à jour : 2026-10-07 (veille élargie : 106 offres, 85 employeurs).

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

## À tester

FFBB (portail en 403 au fetch), Golazo (cookies à accepter), Karmine Corp et Solary (hors WTTJ),
Mouratoglou Academy (Taleez en JS), Compagnie des Alpes, Sodexo Live!, Weezevent.
