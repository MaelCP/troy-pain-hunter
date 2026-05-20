---
name: troy-pain-hunter
description: Scanne Reddit, Twitter, Facebook, Google et offres de stages AI/LLM (Indeed, Welcome to the Jungle, LinkedIn) pour détecter les frustrations exprimées publiquement, puis applique la méthode Troy (serial founder, portefeuille >$1bn) pour évaluer chaque pain point comme opportunité business en 6 étapes. Étape 1.5 OBLIGATOIRE de deep-dive avant tout crash-test pour éviter de construire sur un pain culturellement résolu ou un faux signal. Si l'opportunité est validée, enchaîne automatiquement sur la spec produit (via superpowers:brainstorming) et le plan d'implémentation (via superpowers:writing-plans).
---

# Troy Pain Hunter

Dès que ce skill est activé, exécute le script de scraping, puis guide l'utilisateur à travers chaque étape de la méthode Troy. **Attends la validation de l'utilisateur après chaque étape avant de continuer.**

## 0. Lancement du scraping

**Avant de scraper**, charge les analyses déjà effectuées :

```bash
/Users/satoshi/Projets/bizness/.venv/bin/python /Users/satoshi/Projets/bizness/troy-memory-engine/memory/troy_memory.py --list-analyses
```

Si des idées ont `status=commit` ou `status=fold`, affiche-les à l'utilisateur et **ne les ré-analyse pas** dans les étapes suivantes.

Puis lance le scraping (par défaut tous les scopes) :

```bash
/Users/satoshi/Projets/bizness/.venv/bin/python ~/.claude/plugins/troy-pain-hunter/scripts/main.py --scope all
```

**Scopes disponibles** : `annoying`, `saas`, `physical`, `freelance`, `internships`, `all`.

- `internships` : scrape les offres de stages IA/LLM/RAG/MLOps. Hypothèse : ce qu'une boîte ouvre comme stage à 6 mois sur l'IA est un proxy du SaaS qu'elle aimerait acheter mais qui n'existe pas. Très utile pour les opportunités B2B sous-explorées.
  
  **Sources qui marchent direct** (testées 2026-05-20) :
  - **LinkedIn Jobs guest** : ✅ ~16 résultats / keyword / géo (FR + US)
  - **Free-Work** (FR tech) : ✅ HTML SSR scrapable, filtre internship + apprenticeship natif
  
  **Sources stubbed (anti-scrape)** :
  - **Indeed** : 404 RSS + 403 Cloudflare. Activer via `INDEED_API_KEY` (Publisher API)
  - **Welcome to the Jungle** : SPA, clé Algolia non exposée. Activer via `WTTJ_ALGOLIA_KEY`
  - **HelloWork** : SPA depuis 2026. Nécessite Playwright headless
  - **Wellfound / Google site: search** : DDG et Bing bloquent les requêtes non-browser. À recoder via SerpAPI (clé `SERPAPI_KEY`)
  
  Le scope reste utile même avec seulement LinkedIn + Free-Work : ~25-40 offres / keyword.

Affiche à l'utilisateur :
- Le nombre de résultats nouveaux par scope (`by_scope`)
- Le nombre d'URLs déjà vues (`already_seen`)
- Les éventuelles sources skippées (`errors`)

---

## Pré-étape — Clarifier les objectifs personnels

Avant d'analyser quoi que ce soit, pose ces 3 questions à l'utilisateur :

1. **Contraintes de temps :** Combien d'heures par semaine peux-tu consacrer à ce projet ?
2. **Ambition :** Tu cherches un micro-SaaS passif (quelques k€/mois, side project) ou un business venture scale (>$10m ARR, levée de fonds possible) ?
3. **Budget :** Bootstrap uniquement ou tu peux investir du capital de départ ?

Ces réponses servent de filtre pour toutes les étapes suivantes. Une opportunité venture est à éliminer si l'utilisateur a 5h/semaine. Note les réponses et rappelle-les si besoin dans les étapes suivantes.

---

## Étape 1 — Pain vs Enjoyment + Scoring

À partir des résultats du scraping :

1. **Élimine immédiatement** tout ce qui relève du divertissement pur (jeux vidéo, restaurants, films, sport loisir, réseaux sociaux de divertissement). Ces marchés sont "enjoyment businesses" — plus difficiles à construire, pas de douleur régulière qui force le paiement.

2. Pour chaque pain restant, attribue une note de **1 à 5** sur 3 axes :
   - **Intensité** : 1 = léger inconfort → 5 = bloque un business / gâche une journée entière / coûte de l'argent
   - **Fréquence** : 1 = une fois par an → 5 = quotidien ou plusieurs fois par semaine
   - **Niche** : 1 = touche tout le monde de façon générique → 5 = groupe ultra-spécifique, sous-desservi, prêt à payer plus cher pour une solution sur mesure

3. **Élimine tout ce qui a un score combiné < 8/15.**

**Persistance obligatoire** : pour chaque URL traitée, appelle :

```bash
/Users/satoshi/Projets/bizness/.venv/bin/python /Users/satoshi/Projets/bizness/troy-memory-engine/memory/troy_memory.py \
  --rate-url "<url>" \
  --label "<noise|qualified>" \
  --pain-score <0 si noise, sinon /15> \
  --reason "<raison courte>"
```

Avant de re-scorer dans un futur run, charge les déjà-classés :

```bash
# Lister les pains déjà qualifiés (à recharger pour analyse continue)
/Users/satoshi/Projets/bizness/.venv/bin/python /Users/satoshi/Projets/bizness/troy-memory-engine/memory/troy_memory.py --list-results --label qualified --min-pain 8

# Stats globales
/Users/satoshi/Projets/bizness/.venv/bin/python /Users/satoshi/Projets/bizness/troy-memory-engine/memory/troy_memory.py --stats
```

Les URLs étiquetées `noise` ne seront pas re-présentées à l'utilisateur dans les runs suivants (filtrer côté skill via `--label unrated` au démarrage).

Présente le tableau des pains retenus à l'utilisateur et demande validation avant de continuer.

---

---

## Étape 1.5 — Deep-dive OBLIGATOIRE (anti-crash-test inutile)

🚨 **Cette étape est non-skippable.** Un score 1-15 sur un titre de post ne suffit PAS pour engager un crash-test. La méthode Troy demande de vérifier **avant de construire** que :

1. Le pain est **volumétriquement** validé (pas un seul post isolé)
2. La communauté n'a **pas déjà répondu culturellement** ("don't chase", "force users to ticket", "client's responsibility") — pattern qui tue l'opportunité SaaS
3. Les concurrents revendiqués sont **vraiment** mentionnés par les utilisateurs (sinon ils sont fantômes = mauvais marketing OU pas vrai marché)
4. **Si des concurrents existent : ont-ils des FAILLES** ? Des rage posts ("switched away from X", "I hate X"), des bugs récurrents, des features manquantes ? → opportunité de faire **mieux avec des specs en plus**

### Lancer le deep-dive

Pour chaque pain qualifié à l'Étape 1 (score ≥ 8/15), lancer :

```bash
/Users/satoshi/Projets/bizness/.venv/bin/python \
  /Users/satoshi/Projets/bizness/troy-memory-engine/memory/deep_dive.py \
  --url "<URL du post Reddit qualifié>" \
  --competitors "Concurrent1" "Concurrent2" "Concurrent3" \
  --search-terms "expression du pain 1" "expression du pain 2" \
  --subs sub1 sub2 sub3
```

Le script retourne un JSON avec :
- `thread` : top commentaires + cultural_dismissals détectés + tool_mentions
- `related` : autres threads à fort engagement sur le même pain (>20 upvotes)
- `competitor_complaints` : par concurrent, threads de plainte/rage trouvés
- `competitor_snippets` : phrases extraites où un user décrit ce qu'il déteste dans un concurrent
- `verdict` : `GO` | `WEAK_GO_DEEPER` | `KILL_OR_PIVOT` avec raisons

### Règles d'interprétation

- **Verdict `KILL_OR_PIVOT`** : éliminer le pain ou trouver un angle radicalement différent. Ne **jamais** passer à l'Étape 2/3 sur un pain KILL.
- **Verdict `WEAK_GO_DEEPER`** : faire un 2ème deep-dive avec d'autres search-terms et subs, OU traiter comme WEAK_GO (proceed avec scepticisme).
- **Verdict `GO`** : passer à l'Étape 2.
- **Cultural dismissals ≥ 3** : drapeau rouge. La communauté gère le pain par la discipline, pas par un outil → marché culturellement résolu, l'outil n'aura pas de traction même s'il est bon.
- **Competitor complaints non vides** : 💡 trésor pour le pitch. Lister chaque faille relevée → ce sont les **specs en plus** que ton produit doit avoir d'office.

### Sortie attendue dans la conversation

Présenter à l'utilisateur :
1. Tableau pain × `verdict` × raisons clés
2. Pour chaque concurrent ayant des plaintes : 2-3 quotes verbatim de users qui le critiquent → ce sont les **features différenciantes** à construire
3. Décision : continuer / pivoter / kill

**Persistance** : sauvegarder le verdict dans Troy memory via `--rate-url` (label `qualified_deep` ou `cultural_kill`).

---

## Étape 2 — Filtre compétences (Venn Diagram)

Demande à l'utilisateur sa **Skill Tier List** :

> "Liste tes compétences en étant brutalement honnête et range-les en 3 catégories :
> - **Good** : quelqu'un te paierait pour ça aujourd'hui (même à niveau junior)
> - **Acceptable** : tu peux le faire, avec pratique tu deviendrais pro
> - **Bad** : tu détestes ou tu n'as jamais vraiment pratiqué"
>
> Compétences à évaluer : Sales, Design graphique, Product Design, Création de contenu, Marketing digital (SEO/ads), Prise de parole, Outils no-code (Zapier, Webflow...), Programmation, Finance, Ops/Processus, Leadership.

Pour chaque pain retenu à l'étape 1 :
1. Identifie les **3-4 compétences clés** indispensables pour ce business spécifique
2. Calcule le % de ces compétences dans le "Good" ou "Acceptable" de l'utilisateur
3. Si la majorité des compétences clés sont en "Bad" → **🚩 RED FLAG** : propose soit de trouver un co-fondateur, soit un pivot vers une solution 100% no-code/manuelle, soit l'élimination de cette idée

---

## Étape 3 — Recherche prospective (timebox : 10h max)

Pour chaque pain qui a passé les étapes 1 et 2 :

**A) Concurrence**
- Identifie les acteurs existants qui adressent ce pain. **0 concurrent = alerte marché mort** (sauf si l'utilisateur peut prouver que c'est une technologie de rupture récente ou un espace ultra-niche jamais exploré).
- Pour chaque concurrent : pricing (abonnement vs one-time), taille estimée (nb employés), bootstrapped vs VC.

**B) Trouvabilité des clients**
- Pose cette question exacte à l'utilisateur : *"Si je te demandais de trouver UN client potentiel pour ce produit en ligne, maintenant, combien de temps ça prendrait ?"*
- Si la réponse est "je ne sais pas" ou "plus d'une heure" → Red Flag fort.
- Nomme les canaux précis : sous-reddits spécifiques, hashtags, forums, Slack communities, annuaires professionnels.

**C) Marketing Company ou Sales Company ?**
- *Marketing Company* : produit peu cher, onboarding automatisé, vendu à des individus ou petites structures, pas de contrat, audience facilement ciblable en ligne → budget marketing prioritaire
- *Sales Company* : produit cher (high deal size), setup complexe, vendu à des entreprises (B2B), contrats ou engagements volume → équipe commerciale prioritaire

---

## Étape 4 — Dimensionnement financier (TAM / SAM / SOM)

Applique ces formules en **ancrant toujours sur les hypothèses les plus basses** :

```
TAM = nb total de personnes dans l'espace global × prix estimé × fréquence d'achat/an
SAM = nb de personnes souffrant réellement de ce pain × prix estimé × fréquence d'achat/an
SOM = SAM × 0.10  (capture réaliste de 10% du SAM)
```

Documente chaque hypothèse et son raisonnement. Classe l'opportunité :
- **Low** : SOM < $500k
- **Mid** : SOM < $1m
- **Large** : SOM < $10m
- **Venture** : SOM > $10m

Compare la classification avec les objectifs de la pré-étape. Si l'utilisateur veut un side project mais que le SOM est "Low" → c'est parfaitement aligné. Si le SOM est "Venture" mais l'utilisateur veut bootstrapper avec 5h/semaine → incompatibilité à signaler.

**Après avoir présenté le classement à l'utilisateur et reçu sa validation**, sauvegarde l'analyse :

```bash
/Users/satoshi/Projets/bizness/.venv/bin/python /Users/satoshi/Projets/bizness/troy-memory-engine/memory/troy_memory.py \
  --save-analysis \
  --title "<titre de l'opportunité>" \
  --scope "<annoying|saas|physical|freelance>" \
  --pain-score <total /15 de l'étape 1> \
  --skill-match <% compétences matchées de l'étape 2> \
  --som-class "<Low|Mid|Large|Venture>" \
  --status pending \
  --notes "<observations clés>"
```

Confirme à l'utilisateur que l'analyse a été sauvegardée (affiche l'`id` retourné).

---

## Étape 5 — Plan crash-test lean (objectif : 10 clients payants)

**Règle absolue : ce n'est PAS un MVP.** Pas de landing page pro, pas de business cards, pas de logo soigné. L'objectif est de valider l'intention d'achat avec le minimum absolu.

Propose la solution la plus dépouillée possible (Google Form + traitement manuel en coulisses, tableur partagé, simple email).

**L'approche fondateur :** L'utilisateur doit approcher les prospects directement et avec humilité. Les gens aiment soutenir un entrepreneur qui leur parle en face-à-face. Ne pas simuler une "grande boîte".

**3 leviers d'acquisition à choisir selon le contexte :**

1. **Advisor Shares** : offrir 0.1–0.5% d'equity (présenté en nombre de parts, pas en %) à des early users prestige (médecins, avocats, executives). Ikea Effect : ils s'investissent dans le succès du produit.

2. **Godfather Offer** : prix de lancement imbattable à vie pour les 10 premiers. Teste l'intention d'achat réelle sans donner gratuitement.

3. **Free Trial avec empreinte bancaire** : zéro paiement maintenant, mais carte enregistrée et date de facturation future annoncée clairement. Le prospect s'engage moralement et financièrement.

**Signaux d'alarme :**
- Tu dois contacter plus de 100 personnes dans ta cible avant que quelqu'un soit vaguement intéressé → l'opportunité est mauvaise ou ton approche est complètement fausse. Ne t'acharne pas.
- Les gens sont intéressés mais ne veulent pas payer → ce n'est pas un pain business, c'est un "nice to have".

---

---

## Étape 6 — Spec produit & Plan d'implémentation (automatique)

**Déclenche cette étape UNIQUEMENT si** l'utilisateur valide une opportunité à l'Étape 5 (statut `committed` après crash-test réussi, OU s'il demande explicitement à passer à l'implémentation avant le crash-test).

### 6.1 Brainstorming de la spec produit

Invoque le skill `superpowers:brainstorming` via le tool `Skill`. Brief à passer :

> "On a validé une opportunité business : `<titre opportunité>`. Pain : `<résumé Étape 1>`. Cible : `<persona Étape 2-3>`. Distribution : `<canaux Étape 3>`. Prix : `<modèle Étape 4>`. Crash-test : `<résumé Étape 5>`.
>
> Objectif du brainstorm : définir la spec produit MVP minimale qui permet de passer du Wizard of Oz manuel à un vrai produit auto-servi. Explorer features core vs nice-to-have, choix techniques (stack, hosting), modèle de données, parcours utilisateur principal."

Récupère la sortie du brainstorming. Sauvegarde-la dans :
```
/Users/satoshi/Projets/bizness/troy-pain-hunter/crash-tests/<slug-opportunité>/06-spec.md
```

### 6.2 Plan d'implémentation

Invoque le skill `superpowers:writing-plans` via le tool `Skill`. Passe-lui la spec produite en 6.1 comme entrée.

Récupère le plan généré. Sauvegarde-le dans :
```
/Users/satoshi/Projets/bizness/troy-pain-hunter/crash-tests/<slug-opportunité>/07-plan.md
```

### 6.3 Mise à jour de la mémoire Troy

Une fois spec + plan sauvegardés, mets à jour l'analyse en base :

```bash
/Users/satoshi/Projets/bizness/.venv/bin/python /Users/satoshi/Projets/bizness/troy-memory-engine/memory/troy_memory.py \
  --update-status \
  --id <id_analyse> \
  --status implementing
```

Et confirme à l'utilisateur :
- Spec écrite dans `06-spec.md`
- Plan écrit dans `07-plan.md`
- Statut Troy passé à `implementing`
- Propose d'enchaîner avec `superpowers:executing-plans` si l'utilisateur veut démarrer l'implémentation tout de suite.

---

## Conclusion

Si le marché résiste après le crash-test :

> **PLEASE GIVE UP WHEN SHIT ISN'T WORKING.**
>
> Tu es encore très tôt dans le processus. Ne reste pas bloqué à essayer de forcer quelque chose que le marché n'accepte pas. Retourne à l'étape 1 avec de nouveaux pain points. L'entrepreneuriat, c'est ne jamais abandonner le rêve — mais abandonner très vite les idées spécifiques qui ne fonctionnent pas.
