# troy-pain-hunter

Claude Code skill — scanne Reddit et Google pour détecter des frustrations publiques, puis applique la **méthode Troy** (serial founder, >$1bn exits) en 5 étapes pour évaluer chaque opportunité business.

## Ce que ça fait

1. **Scrape** Reddit (JSON public) + Google + Twitter/X + Facebook pour des pain points réels
2. **Déduplique** par URL et trie par score
3. **Guide** l'utilisateur à travers la méthode Troy :
   - Pré-étape : clarifier objectifs (temps, ambition, budget)
   - Étape 1 : scorer chaque pain (Intensité / Fréquence / Niche, /15)
   - Étape 2 : filtrer par compétences (Venn diagram)
   - Étape 3 : recherche prospective (concurrence + trouvabilité clients)
   - Étape 4 : TAM / SAM / SOM
   - Étape 5 : crash-test lean (objectif 10 clients payants, sans MVP)
4. **Mémorise** les analyses entre sessions via [troy-memory-engine](https://github.com/MaelCP/troy-memory-engine)

## Installation

```bash
# 1. Cloner dans le dossier plugins Claude Code
git clone https://github.com/MaelCP/troy-pain-hunter ~/.claude/plugins/troy-pain-hunter

# 2. Installer les dépendances
cd ~/.claude/plugins/troy-pain-hunter
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. (Optionnel) Configurer les tokens pour Twitter/Facebook
cp scripts/.env.example scripts/.env
# Éditer scripts/.env avec TWITTER_BEARER_TOKEN et FACEBOOK_ACCESS_TOKEN

# 4. Installer le moteur mémoire
git clone https://github.com/MaelCP/troy-memory-engine ~/mchanpeng/git/sl
```

Reddit et Google fonctionnent **sans aucune clé API**.

## Utilisation

Dans Claude Code, lancer le skill :

```
/troy-pain-hunter
```

Ou avec un scope précis :

```bash
python3 ~/.claude/plugins/troy-pain-hunter/scripts/main.py --scope annoying
python3 ~/.claude/plugins/troy-pain-hunter/scripts/main.py --scope saas freelance
python3 ~/.claude/plugins/troy-pain-hunter/scripts/main.py --scope all
```

## Scopes disponibles

| Scope | Cible |
|-------|-------|
| `annoying` | Frustrations quotidiennes (tâches manuelles, pertes de temps) |
| `saas` | Opportunités logicielles (manque d'outils, API absentes) |
| `physical` | Business physiques / services locaux |
| `freelance` | Douleurs freelance et agence (clients, facturation, scope creep) |

## Structure

```
troy-pain-hunter/
├── SKILL.md              # Instructions du skill Claude Code
├── requirements.txt
└── scripts/
    ├── main.py           # Orchestrateur : scraping + dédup + mémoire
    ├── keywords.py       # Keywords globaux (legacy)
    ├── sources/
    │   ├── reddit.py     # Reddit JSON API (sans clé)
    │   ├── google.py     # googlesearch-python (sans clé)
    │   ├── twitter.py    # Tweepy (Bearer Token requis)
    │   └── facebook.py   # Facebook Graph API (Access Token requis)
    └── tests/            # pytest — 25 tests
```

## Mémoire persistante

Les analyses Troy sont sauvegardées dans [troy-memory-engine](https://github.com/MaelCP/troy-memory-engine) (SQLite). Au prochain lancement, le skill charge les analyses précédentes et **ne re-analyse pas** les idées déjà traitées.

```bash
# Voir les analyses sauvegardées
python3 ~/mchanpeng/git/sl/memory/troy_memory.py --list-analyses

# Marquer une idée comme validée
python3 ~/mchanpeng/git/sl/memory/troy_memory.py --update-status --id 1 --status commit

# Marquer une idée comme abandonnée
python3 ~/mchanpeng/git/sl/memory/troy_memory.py --update-status --id 1 --status fold
```

## Tests

```bash
cd ~/.claude/plugins/troy-pain-hunter/scripts
pytest tests/ -v
# 25 passed
```
