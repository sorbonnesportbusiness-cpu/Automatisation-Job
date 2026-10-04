---
name: veille-ssb
description: "Veille hebdomadaire des offres d'emploi/stage/alternance en sport business pour Sorbonne Sport Business (SSB). Utiliser quand on demande de lancer/relancer la veille emploi SSB, de chercher des offres sport business (marketing sportif, événementiel, sponsoring, droit du sport, esport, billetterie...), ou d'exécuter le skill veille-ssb. Produit un fichier Excel coloré + un export JSON brut prêt pour un futur CRM."
license: Interne association SSB
---

# Veille emploi Sport Business — Sorbonne Sport Business (SSB)

Ce skill reproduit la veille hebdomadaire d'offres d'emploi/stage/alternance sport business
de l'association. Il fonctionne dans n'importe quelle session Claude qui a accès à la
recherche web (WebSearch/WebFetch ou équivalent) et à un terminal (Bash) pour lancer le
script Python de mise en forme — Claude Code, Cowork, ou un Claude personnel avec les
outils web activés.

Toute personne du bureau peut l'utiliser : installez ce dossier comme skill (voir
`../../README.md` à la racine du repo pour la procédure d'installation Cowork / Claude Code),
puis invoquez-le (`/veille-ssb` ou "lance la veille SSB").

## Avant de commencer

1. Détermine la date du jour avec `date +%F` (ne jamais la deviner).
2. Vérifie que tu as accès à une recherche web et à un fetch de pages. Si aucun outil web
   n'est disponible dans cette session, dis-le clairement et arrête-toi : ce skill ne doit
   jamais inventer des offres à partir de connaissances générales.

## Objectif

Livrer AU MINIMUM 7 offres NON EXPIRÉES et VÉRIFIÉES dans le sport business : marketing
sportif, management du sport, événementiel sportif, communication sport, sponsoring,
partenariats, droit du sport, fan experience, billetterie/hospitalités, merchandising,
esport.

**Priorité absolue : l'offre ne doit pas être expirée.** C'est plus important que sa
fraîcheur exacte.

## Règle de diversité

Maximum 2 offres par employeur, et au moins 4 employeurs différents dans la liste finale.
Si un portail est très fourni, on n'en prend que les 2 meilleures offres et on va chercher
ailleurs.

## Règle de lien — la plus importante

Chaque lien livré doit être LIBREMENT ACCESSIBLE et pointer vers la source de l'employeur
quand c'est possible.
- Ne jamais livrer un lien derrière un paywall ou une inscription obligatoire.
- Les boards payants/masqués servent uniquement de DÉTECTION : on y repère qu'un poste
  existe, puis on fait une recherche web sur l'intitulé exact (+ secteur, ville, employeur
  si devinable) pour retrouver l'offre d'origine sur le site carrières de l'employeur, et
  c'est CE lien-là qu'on livre.
- Si on ne parvient pas à retrouver la source libre d'une offre, on ne la livre pas.

## Portails carrières directs connus (accès libre, fiables — à enrichir au fil des semaines)

Tenir cette liste à jour dans `references/portails.md` (voir plus bas) :
- jobs.fft.fr (FFT/Roland-Garros) — très fourni, plafonner à 2 offres
- carrieres.lfp.fr (LFP / LFP Media)
- team-vitality.welcomekit.co (Team Vitality, esport)
- federation-francaise-de-cyclisme.welcomekit.co (FFC)
- ffvoile.fr/ffv/web/services/emploi/annonces/ffvoile_recrute.asp (annonces PDF — vérifier
  la date de début, souvent dépassée)
- recrutement.fff.fr et fff.taleez.com (FFF) — le rendu JS bloque souvent la vérification
  automatique, à tester manuellement si besoin
- parissaintgermain.wd3.myworkdayjobs.com (PSG, souvent JS-bloqué) et en alternative
  jobteaser.com/companies/psg/job-offers (fiches individuelles lisibles)
- emplois.parisentertainmentcompany.com (Accor Arena / adidas arena / Bataclan) — bon
  gisement, offres fraîches
- jobs.world.luccasoftware.com (Paris Basketball)

Portails à éviter ou peu productifs : jobs.sportfive.com, jobs.smartrecruiters.com (JS),
Havas Play / Infront (pages invérifiables), sportjobshunter.com (NE JAMAIS s'y fier seul —
affiche des offres closes comme ouvertes), welcometothejungle.com (contenu JS vide côté
fetch).

À tester régulièrement pour élargir la diversité : Paris FC, Racing 92, Stade Français,
Paris Basketball, FFR, FFBB, FFHandball, France Judo, FF Natation, CNOSF, ASO/Amaury,
Paris La Défense Arena, beIN Sports, Hopscotch Sport, Publicis Sport, Fuse, Karmine Corp,
Decathlon, Nike/Adidas/Asics France, OL, OM, AS Monaco, LOSC, RC Lens, Stade Rennais,
FC Nantes, Stade Toulousain, LOU Rugby, Section Paloise, Clermont Foot, Limoges CSP, ASVEL.

## Filtres

1. Fraîcheur : publication dans les 2 derniers mois maximum de préférence (priorité
   absolue reste la non-expiration). Une prise de poste future est valable ; une offre
   dont la date de DÉBUT est déjà passée est à écarter.
2. Localisation : France entière.
3. Offre réellement ouverte, vérifiée sur la page individuelle (jamais sur une page de
   liste/recherche).

## Leçon critique — taux d'erreur des agrégateurs

Les jobboards sport gardent en ligne des offres closes et affichent parfois "publié il y a
X jours" pour un poste déjà fermé. sportjobshunter.com est le pire cas. Éliminer
systématiquement : 404/410, "offre expirée"/"poste pourvu"/"clôturée"/"n'est plus
disponible", page qui se charge vide, date limite/début passée, publication de plus de 2
mois, et toute page de recherche/catégorie qui n'est pas une offre individuelle.

## Sources de détection (repérer, puis retracer vers la source libre)

app.lecafedusportbiz.fr/emploi?sort=date, hellowork.com (fiches /emplois/ID),
jobteaser.com (fiches /job-offers/ et pages /companies/<nom>/job-offers), wearemeent.com.
Rendement faible, ne pas y perdre de temps : indeed.fr, apec.fr, glassdoor.fr, monster.fr,
sport-job.fr, sportyjob.com, sportsmarketing.fr, sportbuzzbusiness.fr, sporsora.com,
myjobsports.com.

## Méthode

1. Balayer les portails carrières directs validés (plafond 2 offres/employeur).
2. Ouvrir 2-3 nouveaux employeurs de la liste "à tester" pour élargir la diversité, et
   consigner le résultat (positif ou négatif) dans `references/portails.md`.
3. Compléter par les sources de détection, puis retracer chaque offre intéressante vers sa
   source libre par recherche web sur l'intitulé exact.
4. Vérifier CHAQUE offre par fetch de sa page individuelle avant de la retenir.

Ne jamais tenter de se connecter à un site ni de contourner une protection anti-scraping :
recherche web + fetch de pages publiques uniquement. Ne pas répéter les liens déjà
partagés les semaines précédentes (voir `references/historique.md` si présent dans le
repo de l'association).

Pour une session avec plusieurs agents/sous-agents disponibles, répartir la recherche par
portail/famille de sources en parallèle accélère beaucoup la veille (voir l'exemple de
run dans `references/exemple-execution.md`).

## Livrables

Une fois les offres réunies et vérifiées (minimum 7, diversité respectée), générer les
sorties avec le script fourni :

```bash
python3 scripts/build_outputs.py offres.json --date YYYY-MM-DD --out-dir ./out
```

où `offres.json` est un fichier que tu écris toi-même, de la forme :

```json
{
  "offres": [
    {
      "titre": "Stage - Gestion Billetterie - Janvier 2027",
      "entreprise": "Fédération Française de Tennis (Roland-Garros)",
      "secteur": "Billetterie",
      "localisation": "Paris 16e (75016)",
      "contrat": "Stage",
      "date_pub": "15/09/2026 (début janv. 2027)",
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

Le script produit, dans `--out-dir` :
- `veille-ssb-YYYY-MM-DD.xlsx` — le fichier Excel pour l'association (voir format ci-dessous).
- `offres-YYYY-MM-DD.json` — export brut des mêmes offres, pensé pour être repris plus
  tard par le CRM de l'association (voir section CRM ci-dessous). Toujours générer ce
  fichier même si le CRM n'existe pas encore.

Livre ensuite le `.xlsx` à l'utilisateur (SendUserFile ou équivalent selon la session), et
mentionne que l'export JSON est disponible dans le même dossier pour une intégration
future.

### Format du fichier Excel

Un onglet principal "Offres Sport Business" avec les colonnes N°, Intitulé du poste,
Entreprise/Organisation, Secteur, Localisation, Type de contrat, Date de publication,
Lien vers l'offre, Source, Vérifié le — mise en forme Arial 11, en-tête bleu foncé
(#1B3A5C) en blanc gras, lignes alternées blanc/bleu très clair (#E8F0FE), type de contrat
coloré (Stage #2E7D32, Alternance #1565C0, CDI #E65100, CDD #616161), liens cliquables,
filtre auto, première ligne figée, bordures fines (#D0D0D0). Largeurs : A=5, B=45, C=30,
D=18, E=25, F=18, G=18, H=55, I=25, J=15.

Un onglet "Bilan" avec le nombre total d'offres retenues, le nombre de candidates
testées/écartées, les employeurs/portails stériles de la semaine, les nouveaux portails
découverts, et la date d'exécution.

(Le script `scripts/build_outputs.py` implémente déjà tout ce formatage — ne pas le
réécrire à la main, juste lui fournir le JSON des offres.)

## Point d'intégration CRM (à venir)

Le CRM de l'association n'existe pas encore. Le script accepte dès maintenant une variable
d'environnement `SSB_CRM_WEBHOOK_URL` : si elle est définie, il envoie un POST du JSON des
offres vers cette URL en plus d'écrire les fichiers locaux ; si elle est absente (cas
normal aujourd'hui), il ne fait rien de plus. Quand le CRM sera prêt, il suffira de
renseigner cette variable d'environnement (ou de demander à Claude de la définir avant de
lancer le script) — aucune autre modification du skill ne sera nécessaire.

## Nom du fichier

`veille-ssb-YYYY-MM-DD.xlsx` (date du jour d'exécution), `offres-YYYY-MM-DD.json`.

## Important

Ne publie rien d'autre, ne modifie aucun site web, ne touche à aucun dépôt git sans qu'on
te le demande explicitement. Les seuls livrables sont le fichier Excel et le JSON.
