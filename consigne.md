# Consigne de la veille hebdomadaire

Tu fais la veille des offres d'emploi et de stage dans le sport business pour
Sorbonne Sport Business (association d'étudiants en Master). Modifie ce fichier pour
changer les critères ou les sources : le workflow le relit à chaque lancement.

## Critères de recherche

- **Secteur** : sport business (clubs, ligues, fédérations, équipementiers,
  agences de marketing sportif, organisateurs d'événements, médias sportifs).
- **Types de contrat** : stage, alternance, CDI junior, VIE.
- **Métiers** : marketing, partenariats, communication, événementiel, développement
  commercial.
- **Localisation** : Paris et Île-de-France en priorité, puis France entière.
  Le télétravail complet est accepté.
- **Niveau** : Bac+5, jeune diplômé.

## Sources à couvrir

Chaque ligne ci-dessous donne lieu à une recherche séparée. Ajouter ou retirer une
ligne suffit (garder le tiret en début de ligne).

- Welcome to the Jungle
- JobTeaser (offres publiques)
- HelloWork
- Indeed France
- France Travail
- LinkedIn (offres publiques)
- Sport Stratégies, Jobs in Sports, GlobalSportsJobs
- Sites carrières des ligues et fédérations : LFP, FFF, FFR, FFT, FFBB, FFHandball, CNOSF
- Sites carrières des clubs : PSG, OM, OL, LOSC, Paris FC, Stade Toulousain, Racing 92
- Équipementiers et marques : Decathlon, adidas, Nike, Puma, Lacoste, Salomon
- Médias et agences : beIN Sports, Canal+, L'Équipe, Sportfive, Infront, Havas Play, Lagardère
- Événements : ASO, Alpes 2030, Roland-Garros, Paris La Défense Arena, GL events

Le fichier `skills/veille-ssb/references/portails.md` dit quels portails ont déjà
donné des résultats et lesquels ne marchent pas : consulte-le pour ta source.

## Ce qui est déjà connu (à ne pas reprendre)

Une offre est déjà connue si son lien figure dans l'un de ces fichiers, ou si le
**même intitulé chez la même entreprise** y figure :
- les fichiers du dossier `veille/` (les semaines précédentes) ;
- `data/offres.json` (les offres déjà sur le site veille.sorbonnesportbusiness.com) ;
- `skills/veille-ssb/references/historique.md` (les liens déjà livrés).

Ces fichiers sont gros : ne les lis pas en entier, cherche-y le lien (ou un morceau
de l'intitulé) avec Grep. Une entreprise déjà présente pour **une autre** offre ne
rend pas l'offre connue.

## Règles

- N'invente jamais d'offre. Garde uniquement les annonces trouvées en ligne, avec
  un lien direct vers l'annonce que tu as ouvert et qui fonctionne.
- Écarte les offres expirées ou pourvues.
- Classe les offres de la plus pertinente à la moins pertinente.
- **15 offres au maximum.** S'il y en a moins, n'en mets pas plus pour remplir.
- S'il n'y a aucune nouvelle offre, écris-le simplement dans le fichier.

## Format d'une offre

```markdown
## 1. Intitulé du poste, Entreprise

- **Contrat** : stage / alternance / CDI junior / VIE
- **Lieu** : ville (ou télétravail)
- **Publiée le** : JJ/MM/AAAA (ou « non indiquée »)
- **Lien** : https://...
- **Pourquoi** : une phrase sur ce qui correspond aux critères.
```

## Format du fichier de la semaine

```markdown
# Veille sport business, semaine du AAAA-MM-JJ

N nouvelles offres, classées par pertinence.

(les offres, au format ci-dessus)

## Sources consultées

Une ligne par source, avec le nombre d'offres retenues (0 compris).
```
