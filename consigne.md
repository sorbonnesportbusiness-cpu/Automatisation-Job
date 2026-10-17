# Consigne de la veille hebdomadaire

Tu fais la veille des offres d'emploi et de stage dans le sport business pour
Sorbonne Sport Business (association d'étudiants en Master). Modifie ce fichier pour
changer les critères : le workflow le relit à chaque lancement.

## Critères de recherche

- **Secteur** : sport business (clubs, ligues, fédérations, équipementiers,
  agences de marketing sportif, organisateurs d'événements, médias sportifs).
- **Types de contrat** : stage, alternance, CDI junior, VIE.
- **Métiers** : marketing, partenariats, communication, événementiel, développement
  commercial.
- **Localisation** : Paris et Île-de-France en priorité, puis France entière.
  Le télétravail complet est accepté.
- **Niveau** : Bac+5, jeune diplômé.
- **Sources à privilégier** : Welcome to the Jungle, JobTeaser, Sport Stratégies,
  sites carrières des clubs et des fédérations, France Travail.

## Ce qui est déjà connu (à ne pas reprendre)

Une offre est déjà connue si son lien, ou le même intitulé chez la même entreprise,
figure dans l'un de ces fichiers :
- les fichiers du dossier `veille/` (les semaines précédentes) ;
- `data/offres.json` (les offres déjà sur le site veille.sorbonnesportbusiness.com) ;
- `skills/veille-ssb/references/historique.md` (les liens déjà livrés).

Ces fichiers sont gros : ne les lis pas en entier, cherche-y le lien ou le nom de
l'entreprise avec Grep avant de retenir une offre.

## Comment chercher

Prends le temps : une veille sérieuse dure 15 à 30 minutes. Ne t'arrête pas après
deux ou trois sources.

1. **Pars de `out/candidats.json`.** Le workflow vient d'interroger directement les
   sites carrières de plus de 80 employeurs du sport. Ce fichier contient les offres
   récentes qui ne sont pas encore sur le site. Relis chacune (champ `_extrait`, et
   ouvre le lien en cas de doute) et garde celles qui correspondent aux critères.
2. **Complète par la recherche web**, en couvrant au minimum :
   - Welcome to the Jungle, JobTeaser, HelloWork, Indeed, France Travail, LinkedIn
     (recherches du type « stage marketing sport Paris », « alternance partenariats
     club », « VIE sport marketing ») ;
   - Sport Stratégies (offres d'emploi) et les job boards sport (Jobs in Sports,
     GlobalSportsJobs) ;
   - les sites carrières des grands acteurs : LFP, FFF, FFR, FFT, PSG, OM, OL,
     Stade Toulousain, Paris 2024 / Alpes 2030, ASO, Decathlon, adidas, Nike,
     Puma, beIN Sports, Canal+, L'Équipe, Sportfive, Infront, Havas Sport,
     Lagardère Sports.
   Le fichier `skills/veille-ssb/references/portails.md` liste les portails qui ont
   déjà donné des résultats et ceux qui ne marchent pas : lis-le d'abord.
3. Continue jusqu'à avoir 15 offres retenues ou avoir couvert toutes ces sources.

## Règles

- N'invente jamais d'offre. Garde uniquement les annonces trouvées en ligne, avec
  un lien direct vers l'annonce que tu as ouvert et qui fonctionne.
- Écarte les offres expirées ou pourvues.
- Classe les offres de la plus pertinente à la moins pertinente.
- **15 offres au maximum.** S'il y en a moins, n'en mets pas plus pour remplir.
- S'il n'y a aucune nouvelle offre, écris-le simplement dans le fichier.

## Format du fichier

```markdown
# Veille sport business, semaine du AAAA-MM-JJ

N nouvelles offres, classées par pertinence.

## 1. Intitulé du poste, Entreprise

- **Contrat** : stage / alternance / CDI junior / VIE
- **Lieu** : ville (ou télétravail)
- **Publiée le** : JJ/MM/AAAA (ou « non indiquée »)
- **Lien** : https://...
- **Pourquoi** : une phrase sur ce qui correspond aux critères.

(... les autres offres ...)

## Sources consultées

Une ligne par source, avec le nombre d'offres retenues (0 compris).
```
