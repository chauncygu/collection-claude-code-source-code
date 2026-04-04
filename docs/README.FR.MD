Français | [中文](https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/README.CN.MD) | [한국어](https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/README.KO.MD) | [日本語](https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/README.JP.MD) | [Deutsch](https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/README.DE.MD) | [Español](https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/README.ES.MD)

<div align="center">
  <a href="[https://github.com/SafeRL-Lab/Robust-Gymnasium](https://github.com/SafeRL-Lab/nano-claude-code)">
    <img src="https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/logo-v1.png" alt="Logo" width="280"> 
  </a>

<h1 align="center" style="font-size: 30px;"><strong><em>Nano Claude Code</em></strong> : une réimplémentation Python rapide et facile à utiliser de Claude Code, compatible avec n’importe quel modèle</h1>
<p align="center">
    <a href="https://github.com/chauncygu/collection-claude-code-source-code">La source la plus récente de Claude Code</a>
    ·
    <a href="https://github.com/SafeRL-Lab/nano-claude-code/issues">Issue</a>
  ·
    <a href="https://deepwiki.com/SafeRL-Lab/nano-claude-code">Brève introduction</a>
</p>
</div>

<div align=center>
 <img src="https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/demo.gif" width="850"/> 
</div>
<div align=center>
<center style="color:#000000;text-decoration:underline"> </center>
</div>

---

## 🔥🔥🔥 Actualités (heure du Pacifique)
- 00:41, 04 avr. 2026 : **v3.05** — Saisie vocale (package `voice/`) : backends d’enregistrement `sounddevice` → `arecord` → SoX, backends STT `faster-whisper` → `openai-whisper` → API OpenAI. Extraction intelligente de termes clés à partir de la branche git + du nom du projet + des fichiers récents, injectés dans `initial_prompt` de Whisper pour améliorer la précision sur le domaine du code. Commandes REPL `/voice`, `/voice status`, `/voice lang <code>`. Fonctionne entièrement hors ligne, sans clé API. 29 nouveaux tests (**~11.6K** lignes de Python).
- 22:29, 03 avr. 2026 : **v3.04** — Couverture des outils étendue : `NotebookEdit` (édition des cellules Jupyter `.ipynb` — remplacer/insérer/supprimer avec aller-retour JSON complet) et `GetDiagnostics` (diagnostics de style LSP via pyright/mypy/flake8/tsc/shellcheck). Correction également d’un ancien bug d’index de schéma dans `_register_builtins` en passant à une recherche par nom (**~10.5K** lignes de Python).
- 18:00, 03 avr. 2026 : **v3.03** — Système de gestion de tâches (package `task/`) : outils `TaskCreate` / `TaskUpdate` / `TaskGet` / `TaskList` avec identifiants séquentiels, arêtes de dépendance (`blocks`/`blocked_by`), métadonnées, persistance vers `.nano_claude/tasks.json`, stockage thread-safe, commande REPL `/tasks`, 37 nouveaux tests (**~9500** lignes de Python).
- 14:50, 03 avr. 2026 : **v3.02** — Système de plugins (package `plugin/`) : installation/désinstallation/activation/désactivation/mise à jour via la CLI `/plugin`, moteur de recommandation (correspondance mots-clés + tags), multi-portée (utilisateur/projet), marketplace basée sur git. Outil `AskUserQuestion` : invites interactives à l’utilisateur en cours de tâche, avec options numérotées et saisie libre (**~8500** lignes de Python).
- 10:00, 03 avr. 2026 : **v3.01** — Support MCP (Model Context Protocol) : package `mcp/`, transports stdio + SSE + HTTP, découverte automatique d’outils, commande `/mcp`, 34 nouveaux tests (**~7000** lignes de Python).
- 12:20, 02 avr. 2026 : **v3.0** — Packages multi-agent (`multi_agent/`), mémoire (`memory/`), compétences (`skill/`) avec compétences intégrées, substitution d’arguments, exécution fork/inline, recherche mémoire par IA, isolation via git worktree, définitions de types d’agents (**~5000** lignes de Python), voir la [mise à jour](https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/update_readme_v3.0.md).
- 10:00, 02 avr. 2026 : **v2.0** — Compression de contexte, mémoire, sous-agents, compétences, vue diff, système de plugins d’outils (**~3400** lignes de code Python).
- 13:47, 01 avr. 2026 : prise en charge de l’inférence VLLM (**~2000** lignes de code Python).
- 11:30, 01 avr. 2026 : prise en charge de davantage de modèles **propriétaires** et **open source** : Claude, GPT, Gemini, Kimi, Qwen, Zhipu, DeepSeek, ainsi que des modèles open source locaux via Ollama ou tout endpoint compatible OpenAI. (**~1700** lignes de code Python).
- 09:50, 01 avr. 2026 : prise en charge de davantage de modèles **propriétaires** : Claude, GPT, Gemini. (**~1300** lignes de code Python).
- 08:23, 01 avr. 2026 : publication de la version initiale de Nano Claude Code (**~900 lignes** de code Python).

---

# Nano Claude Code

Nano Claude Code : **une réimplémentation Python légère** et **facile à utiliser** de Claude Code **compatible avec n’importe quel modèle**, comme Claude, GPT, Gemini, Kimi, Qwen, Zhipu, DeepSeek, ainsi que des modèles open source locaux via Ollama ou tout endpoint compatible OpenAI.

---

## Sommaire
  * [Pourquoi Nano Claude Code](#pourquoi-nano-claude-code)
  * [Fonctionnalités](#fonctionnalités)
  * [Modèles pris en charge](#modèles-pris-en-charge)
  * [Installation](#installation)
  * [Utilisation : modèles API propriétaires](#utilisation--modèles-api-propriétaires)
  * [Utilisation : modèles open source (local)](#utilisation--modèles-open-source-local)
  * [Format du nom de modèle](#format-du-nom-de-modèle)
  * [Référence CLI](#référence-cli)
  * [Commandes slash (REPL)](#commandes-slash-repl)
  * [Configuration des clés API](#configuration-des-clés-api)
  * [Système d’autorisations](#système-dautorisations)
  * [Outils intégrés](#outils-intégrés)
  * [Mémoire](#mémoire)
  * [Compétences](#compétences)
  * [Sous-agents](#sous-agents)
  * [MCP (Model Context Protocol)](#mcp-model-context-protocol)
  * [Système de plugins](#système-de-plugins)
  * [Outil AskUserQuestion](#outil-askuserquestion)
  * [Gestion des tâches](#gestion-des-tâches)
  * [Saisie vocale](#saisie-vocale)
  * [Compression de contexte](#compression-de-contexte)
  * [Vue diff](#vue-diff)
  * [Prise en charge de CLAUDE.md](#prise-en-charge-de-claudemd)
  * [Gestion des sessions](#gestion-des-sessions)
  * [Structure du projet](#structure-du-projet)
  * [FAQ](#faq)

## Pourquoi Nano Claude Code

Claude Code est un assistant de codage IA puissant, prêt pour la production — mais son code source est un bundle TypeScript/Node.js compilé de 12 Mo (~1 300 fichiers, ~283K lignes). Il est étroitement couplé à l’API Anthropic, difficile à modifier, et impossible à exécuter sur un modèle local ou alternatif.

**Nano Claude Code** réimplémente la même boucle centrale en ~10K lignes de Python lisible, en conservant tout ce dont vous avez besoin et en supprimant le reste. Voir ici une analyse plus détaillée (Nano Claude Code v3.03), [version anglaise](https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/comparison_claude_code_vs_nano_v3.03_en.md) et [version chinoise](https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/comparison_claude_code_vs_nano_v3.03_cn.md)

### En un coup d’œil

| Dimension | Claude Code (TypeScript) | Nano Claude Code (Python) |
|-----------|--------------------------|---------------------------|
| Langage | TypeScript + React/Ink | Python 3.8+ |
| Fichiers source | ~1 332 fichiers TS/TSX | 51 fichiers Python |
| Lignes de code | ~283K | ~11.6K |
| Outils intégrés | 44+ | 23 |
| Commandes slash | 88 | 18 |
| Saisie vocale | WebSocket Anthropic propriétaire (OAuth requis) | Whisper local / API OpenAI — fonctionne hors ligne, sans abonnement |
| Fournisseurs de modèles | Anthropic uniquement | 7+ (Anthropic · OpenAI · Gemini · Kimi · Qwen · DeepSeek · Ollama · …) |
| Modèles locaux | Non | Oui — Ollama, LM Studio, vLLM, tout endpoint compatible OpenAI |
| Étape de build requise | Oui (Bun + esbuild) | Non — exécution directe avec `python nano_claude.py` |
| Extensibilité à l’exécution | Fermée (à la compilation) | Ouverte — `register_tool()` à l’exécution, compétences Markdown, plugins git |
| Graphe de dépendances de tâches | Non | Oui — arêtes `blocks` / `blocked_by` dans le package `task/` |

### Là où Claude Code l’emporte

- **Qualité de l’interface** — arbre de composants React/Ink avec rendu en streaming, visualisation diff fine et systèmes de dialogue.
- **Richesse des outils** — 44 outils, dont `RemoteTrigger`, `EnterWorktree` et davantage d’outils intégrés à l’UI.
- **Fonctionnalités entreprise** — config gérée par MDM, synchronisation des permissions d’équipe, OAuth, stockage keychain, feature flags GrowthBook.
- **Extraction de mémoire pilotée par IA** — le service `extractMemories` extrait proactivement des connaissances à partir des conversations sans appels d’outils explicites.
- **Fiabilité en production** — un unique exécutable `cli.js`, couverture de tests complète, versions figées.

### Là où Nano Claude Code l’emporte

- **Multi-fournisseur** — basculez entre Claude, GPT-4o, Gemini 2.5 Pro, DeepSeek, Qwen ou un modèle Llama local avec `--model` ou `/model`, sans recompilation.
- **Prise en charge des modèles locaux** — fonctionne entièrement hors ligne avec Ollama, LM Studio ou tout modèle servi via vLLM.
- **Code lisible** — la boucle complète de l’agent fait 174 lignes (`agent.py`). Tout développeur Python peut la lire, la forker et l’étendre en quelques minutes.
- **Zéro build** — `pip install -r requirements.txt` et c’est prêt. Les modifications prennent effet immédiatement.
- **Extensibilité dynamique** — enregistrez de nouveaux outils à l’exécution avec `register_tool(ToolDef(...))`, installez des packs de compétences depuis des URL git, ou branchez n’importe quel serveur MCP.
- **Graphe de dépendances de tâches** — `TaskCreate` / `TaskUpdate` prennent en charge les arêtes `blocks` / `blocked_by` pour une planification structurée en plusieurs étapes (indisponible dans Claude Code).
- **Compression de contexte à deux couches** — découpe basée sur des règles + résumé par IA, configurable via `preserve_last_n_turns`.
- **Édition de notebooks** — `NotebookEdit` manipule directement le JSON `.ipynb` (remplacer/insérer/supprimer des cellules) sans noyau requis.
- **Diagnostics sans serveur LSP** — `GetDiagnostics` enchaîne pyright → mypy → flake8 → py_compile pour Python, et tsc/shellcheck pour les autres langages, sans configuration.
- **Saisie vocale hors ligne** — `/voice` enregistre via `sounddevice`/`arecord`/SoX, transcrit avec `faster-whisper` local (sans clé API ni abonnement), puis soumet automatiquement. Les termes clés provenant de votre branche git et des fichiers du projet améliorent la précision sur le vocabulaire du code.

### Différences de conception clés

**Boucle agent** — Nano utilise un générateur Python qui `yield` des événements typés (`TextChunk`, `ToolStart`, `ToolEnd`, `TurnDone`). Toute la boucle est visible dans un seul fichier, ce qui facilite l’ajout de hooks, de rendus personnalisés ou de logs.

**Enregistrement des outils** — chaque outil est une dataclass `ToolDef(name, schema, func, read_only, concurrent_safe)`. N’importe quel module peut appeler `register_tool()` à l’import ; les serveurs MCP, plugins et compétences utilisent tous le même mécanisme.

**Compression de contexte**

| | Claude Code | Nano Claude Code |
|-|-------------|-----------------|
| Déclenchement | Compte exact de tokens | estimation `len / 3.5`, déclenchement à 70 % |
| Couche 1 | — | Snip : tronque les anciennes sorties d’outils (sans coût API) |
| Couche 2 | Résumé par IA | Résumé par IA des anciens tours |
| Contrôle | Géré par le système | paramètre `preserve_last_n_turns` |

**Mémoire** — le service `extractMemories` de Claude Code fait remonter proactivement des faits par le modèle. Le package `memory/` de Nano est piloté par des outils : le modèle appelle explicitement `MemorySave`, ce qui est plus prévisible et plus auditable.

### Qui devrait utiliser Nano Claude Code

- Les développeurs qui veulent **utiliser un modèle local ou non-Anthropic** comme assistant de codage.
- Les chercheurs qui étudient **le fonctionnement des assistants de codage agentiques** — tout le système tient sur un écran.
- Les équipes qui ont besoin d’**une base hackable** pour ajouter des outils propriétaires, des politiques d’autorisation personnalisées ou des types d’agents spécialisés.
- Toute personne qui veut la productivité de Claude Code **sans chaîne de build Node.js**.

---

## Fonctionnalités

| Fonctionnalité | Détails |
|---|---|
| Multi-fournisseur | Anthropic · OpenAI · Gemini · Kimi · Qwen · Zhipu · DeepSeek · Ollama · LM Studio · endpoint personnalisé |
| REPL interactive | historique readline, auto-complétion Tab pour les slash commands |
| Boucle agent | API en streaming + boucle automatique d’utilisation des outils |
| 23 outils intégrés | Read · Write · Edit · Bash · Glob · Grep · WebFetch · WebSearch · **NotebookEdit** · **GetDiagnostics** · MemorySave · MemoryDelete · MemorySearch · MemoryList · Agent · SendMessage · CheckAgentResult · ListAgentTasks · ListAgentTypes · Skill · SkillList · AskUserQuestion · TaskCreate/Update/Get/List · *(outils MCP + plugins ajoutés automatiquement au démarrage)* |
| Intégration MCP | Connecte n’importe quel serveur MCP (stdio/SSE/HTTP), outils auto-enregistrés et appelables par Claude |
| Système de plugins | Installer/désinstaller/activer/désactiver/mettre à jour des plugins depuis des URL git ou des chemins locaux ; multi-portée (utilisateur/projet) ; moteur de recommandation |
| AskUserQuestion | Claude peut s’arrêter et poser une question de clarification à l’utilisateur en cours de tâche, avec options numérotées facultatives |
| Gestion des tâches | Outils TaskCreate/Update/Get/List ; IDs séquentiels ; arêtes de dépendance ; métadonnées ; persistance vers `.nano_claude/tasks.json` ; commande REPL `/tasks` |
| Vue diff | Affichage diff rouge/vert de style git pour Edit et Write |
| Compression de contexte | Compactage automatique des longues conversations pour rester dans les limites du modèle |
| Mémoire persistante | Mémoire à double portée (utilisateur + projet) avec 4 types, recherche par IA, avertissements d’obsolescence |
| Multi-agent | Lance des sous-agents typés (coder/reviewer/researcher/…), isolation git worktree, mode arrière-plan |
| Compétences | `/commit` · `/review` intégrées + compétences Markdown personnalisées avec substitution d’arguments et exécution fork/inline |
| Outils plugin | Enregistrement d’outils personnalisés via `tool_registry.py` |
| Système d’autorisations | modes `auto` / `accept-all` / `manual` |
| 18 commandes slash | `/model` · `/config` · `/save` · `/cost` · `/memory` · `/skills` · `/agents` · `/voice` · … |
| Saisie vocale | Enregistrer → transcrire → soumettre automatiquement. Backends : `sounddevice` / `arecord` / SoX + `faster-whisper` / `openai-whisper` / API OpenAI. Fonctionne entièrement hors ligne. |
| Injection de contexte | Charge automatiquement `CLAUDE.md`, l’état git, le répertoire courant, la mémoire persistante |
| Persistance des sessions | Sauvegarde / chargement des conversations dans `~/.nano_claude/sessions/` |
| Extended Thinking | Activable/désactivable (modèles Claude uniquement) |
| Suivi des coûts | Utilisation des tokens + coût estimé en USD |
| Mode non interactif | drapeau `--print` pour scripts / CI |

---

## Modèles pris en charge

### Propriétaires (API)

| Fournisseur | Modèle | Contexte | Points forts | Variable d’environnement pour clé API |
|---|---|---|---|---|
| **Anthropic** | `claude-opus-4-6` | 200k | Le plus capable, excellent pour le raisonnement complexe | `ANTHROPIC_API_KEY` |
| **Anthropic** | `claude-sonnet-4-6` | 200k | Bon équilibre vitesse / qualité | `ANTHROPIC_API_KEY` |
| **Anthropic** | `claude-haiku-4-5-20251001` | 200k | Rapide, économique | `ANTHROPIC_API_KEY` |
| **OpenAI** | `gpt-4o` | 128k | Multimodal fort et performant en code | `OPENAI_API_KEY` |
| **OpenAI** | `gpt-4o-mini` | 128k | Rapide, peu coûteux | `OPENAI_API_KEY` |
| **OpenAI** | `o3-mini` | 200k | Raisonnement solide | `OPENAI_API_KEY` |
| **OpenAI** | `o1` | 200k | Raisonnement avancé | `OPENAI_API_KEY` |
| **Google** | `gemini-2.5-pro-preview-03-25` | 1M | Long contexte, multimodal | `GEMINI_API_KEY` |
| **Google** | `gemini-2.0-flash` | 1M | Rapide, grand contexte | `GEMINI_API_KEY` |
| **Google** | `gemini-1.5-pro` | 2M | Plus grande fenêtre de contexte | `GEMINI_API_KEY` |
| **Moonshot (Kimi)** | `moonshot-v1-8k` | 8k | Chinois & anglais | `MOONSHOT_API_KEY` |
| **Moonshot (Kimi)** | `moonshot-v1-32k` | 32k | Chinois & anglais | `MOONSHOT_API_KEY` |
| **Moonshot (Kimi)** | `moonshot-v1-128k` | 128k | Long contexte | `MOONSHOT_API_KEY` |
| **Alibaba (Qwen)** | `qwen-max` | 32k | Meilleure qualité Qwen | `DASHSCOPE_API_KEY` |
| **Alibaba (Qwen)** | `qwen-plus` | 128k | Équilibré | `DASHSCOPE_API_KEY` |
| **Alibaba (Qwen)** | `qwen-turbo` | 1M | Rapide, économique | `DASHSCOPE_API_KEY` |
| **Alibaba (Qwen)** | `qwq-32b` | 32k | Raisonnement solide | `DASHSCOPE_API_KEY` |
| **Zhipu (GLM)** | `glm-4-plus` | 128k | Meilleure qualité GLM | `ZHIPU_API_KEY` |
| **Zhipu (GLM)** | `glm-4` | 128k | Usage général | `ZHIPU_API_KEY` |
| **Zhipu (GLM)** | `glm-4-flash` | 128k | Niveau gratuit disponible | `ZHIPU_API_KEY` |
| **DeepSeek** | `deepseek-chat` | 64k | Solide en code | `DEEPSEEK_API_KEY` |
| **DeepSeek** | `deepseek-reasoner` | 64k | Raisonnement avec chaîne de pensée | `DEEPSEEK_API_KEY` |

### Open source (local via Ollama)

| Modèle | Taille | Points forts | Commande de téléchargement |
|---|---|---|---|
| `llama3.3` | 70B | Usage général, bon raisonnement | `ollama pull llama3.3` |
| `llama3.2` | 3B / 11B | Léger | `ollama pull llama3.2` |
| `qwen2.5-coder` | 7B / 32B | **Meilleur pour les tâches de code** | `ollama pull qwen2.5-coder` |
| `qwen2.5` | 7B / 72B | Chinois & anglais | `ollama pull qwen2.5` |
| `deepseek-r1` | 7B–70B | Raisonnement, mathématiques | `ollama pull deepseek-r1` |
| `deepseek-coder-v2` | 16B | Code | `ollama pull deepseek-coder-v2` |
| `mistral` | 7B | Rapide, efficace | `ollama pull mistral` |
| `mixtral` | 8x7B | Modèle MoE performant | `ollama pull mixtral` |
| `phi4` | 14B | Microsoft, bon raisonnement | `ollama pull phi4` |
| `gemma3` | 4B / 12B / 27B | Modèle ouvert de Google | `ollama pull gemma3` |
| `codellama` | 7B / 34B | Génération de code | `ollama pull codellama` |

> **Remarque :** l’appel d’outils nécessite un modèle prenant en charge le function calling. Modèles locaux recommandés : `qwen2.5-coder`, `llama3.3`, `mistral`, `phi4`.

---

## Installation

```bash
git clone <repo-url>
cd nano_claude_code

pip install -r requirements.txt
# ou manuellement :
pip install anthropic openai httpx rich sounddevice
```

---

## Utilisation : modèles API propriétaires

### Anthropic Claude

Obtenez votre clé API sur [console.anthropic.com](https://console.anthropic.com).

```bash
export ANTHROPIC_API_KEY=sk-ant-api03-...

# Modèle par défaut (claude-opus-4-6)
python nano_claude.py

# Choisir un modèle spécifique
python nano_claude.py --model claude-sonnet-4-6
python nano_claude.py --model claude-haiku-4-5-20251001

# Activer Extended Thinking
python nano_claude.py --model claude-opus-4-6 --thinking --verbose
```

### OpenAI GPT

Obtenez votre clé API sur [platform.openai.com](https://platform.openai.com).

```bash
export OPENAI_API_KEY=sk-...

python nano_claude.py --model gpt-4o
python nano_claude.py --model gpt-4o-mini
python nano_claude.py --model gpt-4.1-mini
python nano_claude.py --model o3-mini
```

### Google Gemini

Obtenez votre clé API sur [aistudio.google.com](https://aistudio.google.com).

```bash
export GEMINI_API_KEY=AIza...

python nano_claude.py --model gemini/gemini-2.0-flash
python nano_claude.py --model gemini/gemini-1.5-pro
python nano_claude.py --model gemini/gemini-2.5-pro-preview-03-25
```

### Kimi (Moonshot AI)

Obtenez votre clé API sur [platform.moonshot.cn](https://platform.moonshot.cn).

```bash
export MOONSHOT_API_KEY=sk-...

python nano_claude.py --model kimi/moonshot-v1-32k
python nano_claude.py --model kimi/moonshot-v1-128k
```

### Qwen (Alibaba DashScope)

Obtenez votre clé API sur [dashscope.aliyun.com](https://dashscope.aliyun.com).

```bash
export DASHSCOPE_API_KEY=sk-...

python nano_claude.py --model qwen/Qwen3.5-Plus
python nano_claude.py --model qwen/Qwen3-MAX
python nano_claude.py --model qwen/Qwen3.5-Flash
```

### Zhipu GLM

Obtenez votre clé API sur [open.bigmodel.cn](https://open.bigmodel.cn).

```bash
export ZHIPU_API_KEY=...

python nano_claude.py --model zhipu/glm-4-plus
python nano_claude.py --model zhipu/glm-4-flash   # niveau gratuit
```

### DeepSeek

Obtenez votre clé API sur [platform.deepseek.com](https://platform.deepseek.com).

```bash
export DEEPSEEK_API_KEY=sk-...

python nano_claude.py --model deepseek/deepseek-chat
python nano_claude.py --model deepseek/deepseek-reasoner
```

---

## Utilisation : modèles open source (local)

### Option A — Ollama (recommandé)

Ollama exécute les modèles localement sans configuration. Aucune clé API requise.

**Étape 1 : installer Ollama**

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Ou télécharger depuis https://ollama.com/download
```

**Étape 2 : télécharger un modèle**

```bash
# Meilleur pour le code (recommandé)
ollama pull qwen2.5-coder          # 4.7 GB (7B)
ollama pull qwen2.5-coder:32b      # 19 GB (32B)

# Usage général
ollama pull llama3.3               # 42 GB (70B)
ollama pull llama3.2               # 2.0 GB (3B)

# Raisonnement
ollama pull deepseek-r1            # 4.7 GB (7B)
ollama pull deepseek-r1:32b        # 19 GB (32B)

# Autres
ollama pull phi4                   # 9.1 GB (14B)
ollama pull mistral                # 4.1 GB (7B)
```

**Étape 3 : démarrer le serveur Ollama** (automatique sur macOS ; sur Linux, lancez-le manuellement)

```bash
ollama serve     # démarre sur http://localhost:11434
```

**Étape 4 : lancer nano claude**

```bash
python nano_claude.py --model ollama/qwen2.5-coder
python nano_claude.py --model ollama/llama3.3
python nano_claude.py --model ollama/deepseek-r1
```

**Lister les modèles disponibles localement :**

```bash
ollama list
```

Puis utilisez n’importe quel modèle de la liste :

```bash
python nano_claude.py --model ollama/<nom-du-modèle>
```

---

### Option B — LM Studio

LM Studio fournit une interface graphique pour télécharger et exécuter des modèles, avec un serveur intégré compatible OpenAI.

**Étape 1 :** Téléchargez [LM Studio](https://lmstudio.ai) et installez-le.

**Étape 2 :** Recherchez et téléchargez un modèle dans LM Studio (format GGUF).

**Étape 3 :** Allez dans l’onglet **Local Server** → cliquez sur **Start Server** (port par défaut : 1234).

**Étape 4 :**

```bash
python nano_claude.py --model lmstudio/<nom-du-modèle>
# par ex. :
python nano_claude.py --model lmstudio/phi-4-GGUF
python nano_claude.py --model lmstudio/qwen2.5-coder-7b
```

Le nom du modèle doit correspondre à celui affiché par LM Studio dans la barre d’état du serveur.

---

### Option C — vLLM / serveur auto-hébergé compatible OpenAI

Pour les serveurs d’inférence auto-hébergés (vLLM, TGI, serveur llama.cpp, etc.) exposant une API compatible OpenAI :

Démarrage rapide pour l’option C :  
Étape 1 : démarrer vllm :
```bash
CUDA_VISIBLE_DEVICES=7 python -m vllm.entrypoints.openai.api_server \
      --model Qwen/Qwen2.5-Coder-7B-Instruct \
      --host 0.0.0.0 \
      --port 8000 \
      --enable-auto-tool-choice \
      --tool-call-parser hermes
```

Étape 2 : démarrer nano claude :
```bash
export CUSTOM_BASE_URL=http://localhost:8000/v1
export CUSTOM_API_KEY=none
python nano_claude.py --model custom/Qwen/Qwen2.5-Coder-7B-Instruct
```

```bash
# Exemple : vLLM sert Qwen2.5-Coder-32B
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-Coder-32B-Instruct \
    --port 8000

# Puis lancez nano claude pointant vers votre serveur :
python nano_claude.py
```

Dans le REPL :

```text
/config custom_base_url=http://localhost:8000/v1
/config custom_api_key=token-abc123    # ignorer si pas d’auth
/model custom/Qwen2.5-Coder-32B-Instruct
```

Ou via des variables d’environnement :

```bash
export CUSTOM_BASE_URL=http://localhost:8000/v1
export CUSTOM_API_KEY=token-abc123

python nano_claude.py --model custom/Qwen2.5-Coder-32B-Instruct
```

Pour un serveur GPU distant :

```bash
/config custom_base_url=http://192.168.1.100:8000/v1
/model custom/your-model-name
```

---

## Format du nom de modèle

Trois formats équivalents sont pris en charge :

```bash
# 1. Détection automatique par préfixe (fonctionne pour les modèles connus)
python nano_claude.py --model gpt-4o
python nano_claude.py --model gemini-2.0-flash
python nano_claude.py --model deepseek-chat

# 2. Préfixe explicite de fournisseur avec slash
python nano_claude.py --model ollama/qwen2.5-coder
python nano_claude.py --model kimi/moonshot-v1-128k

# 3. Préfixe explicite de fournisseur avec deux-points (fonctionne aussi)
python nano_claude.py --model kimi:moonshot-v1-32k
python nano_claude.py --model qwen:qwen-max
```

**Règles de détection automatique :**

| Préfixe du modèle | Fournisseur détecté |
|---|---|
| `claude-` | anthropic |
| `gpt-`, `o1`, `o3` | openai |
| `gemini-` | gemini |
| `moonshot-`, `kimi-` | kimi |
| `qwen`, `qwq-` | qwen |
| `glm-` | zhipu |
| `deepseek-` | deepseek |
| `llama`, `mistral`, `phi`, `gemma`, `mixtral`, `codellama` | ollama |

---

## Référence CLI

```text
python nano_claude.py [OPTIONS] [PROMPT]

Options :
  -p, --print          Mode non interactif : exécute le prompt puis quitte
  -m, --model MODEL    Remplace le modèle (ex. gpt-4o, ollama/llama3.3)
  --accept-all         Approuve automatiquement toutes les opérations (sans demande d’autorisation)
  --verbose            Affiche les blocs de raisonnement et le nombre de tokens par tour
  --thinking           Active Extended Thinking (Claude uniquement)
  --version            Affiche la version puis quitte
  -h, --help           Affiche l’aide
```

**Exemples :**

```bash
# REPL interactive avec le modèle par défaut
python nano_claude.py

# Changer de modèle au démarrage
python nano_claude.py --model gpt-4o
python nano_claude.py -m ollama/deepseek-r1:32b

# Mode non interactif / scripting
python nano_claude.py --print "Write a Python fibonacci function"
python nano_claude.py -p "Explain the Rust borrow checker in 3 sentences" -m gemini/gemini-2.0-flash

# CI / automatisation (sans demande d’autorisation)
python nano_claude.py --accept-all --print "Initialize a Python project with pyproject.toml"

# Mode debug (voir tokens + raisonnement)
python nano_claude.py --thinking --verbose
```

---

## Commandes slash (REPL)

Tapez `/` puis appuyez sur **Tab** pour l’auto-complétion.

| Commande | Description |
|---|---|
| `/help` | Afficher toutes les commandes |
| `/clear` | Effacer l’historique de conversation |
| `/model` | Afficher le modèle courant + lister tous les modèles disponibles |
| `/model <name>` | Changer de modèle (prend effet immédiatement) |
| `/config` | Afficher toutes les valeurs de configuration actuelles |
| `/config key=value` | Définir une valeur de configuration (persistée sur disque) |
| `/save` | Sauvegarder la session (nom automatique horodaté) |
| `/save <filename>` | Sauvegarder la session sous un nom donné |
| `/load` | Lister toutes les sessions sauvegardées |
| `/load <filename>` | Charger une session sauvegardée |
| `/history` | Afficher l’historique complet de conversation |
| `/context` | Afficher le nombre de messages et l’estimation de tokens |
| `/cost` | Afficher l’usage des tokens et le coût estimé en USD |
| `/verbose` | Basculer le mode verbose (tokens + raisonnement) |
| `/thinking` | Basculer Extended Thinking (Claude uniquement) |
| `/permissions` | Afficher le mode d’autorisation courant |
| `/permissions <mode>` | Définir le mode d’autorisation : `auto` / `accept-all` / `manual` |
| `/cwd` | Afficher le répertoire courant |
| `/cwd <path>` | Changer de répertoire courant |
| `/memory` | Lister toutes les mémoires persistantes |
| `/memory <query>` | Rechercher des mémoires par mot-clé |
| `/skills` | Lister les compétences disponibles |
| `/agents` | Afficher l’état des tâches des sous-agents |
| `/mcp` | Lister les serveurs MCP configurés et leurs outils |
| `/mcp reload` | Reconnecter tous les serveurs MCP et rafraîchir les outils |
| `/mcp reload <name>` | Reconnecter un seul serveur MCP |
| `/mcp add <name> <cmd> [args]` | Ajouter un serveur MCP stdio à la config utilisateur |
| `/mcp remove <name>` | Supprimer un serveur de la config utilisateur |
| `/voice` | Enregistrer la voix, transcrire avec Whisper, soumettre automatiquement comme prompt |
| `/voice status` | Afficher la disponibilité des backends d’enregistrement et STT |
| `/voice lang <code>` | Définir la langue STT (ex. `zh`, `en`, `ja`; `auto` pour détection) |
| `/exit` / `/quit` | Quitter |

**Changer de modèle dans une session :**

```text
[myproject] ❯ /model
  Modèle courant : claude-opus-4-6  (fournisseur : anthropic)

  Modèles disponibles par fournisseur :
    anthropic     claude-opus-4-6, claude-sonnet-4-6, ...
    openai        gpt-4o, gpt-4o-mini, o3-mini, ...
    ollama        llama3.3, llama3.2, phi4, mistral, ...
    ...

[myproject] ❯ /model gpt-4o
  Modèle défini sur gpt-4o  (fournisseur : openai)

[myproject] ❯ /model ollama/qwen2.5-coder
  Modèle défini sur ollama/qwen2.5-coder  (fournisseur : ollama)
```

---

## Configuration des clés API

### Méthode 1 : variables d’environnement (recommandé)

```bash
# Ajouter à ~/.bashrc ou ~/.zshrc
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export GEMINI_API_KEY=AIza...
export MOONSHOT_API_KEY=sk-...       # Kimi
export DASHSCOPE_API_KEY=sk-...      # Qwen
export ZHIPU_API_KEY=...             # Zhipu GLM
export DEEPSEEK_API_KEY=sk-...       # DeepSeek
```

### Méthode 2 : définir dans le REPL (persisté)

```text
/config anthropic_api_key=sk-ant-...
/config openai_api_key=sk-...
/config gemini_api_key=AIza...
/config kimi_api_key=sk-...
/config qwen_api_key=sk-...
/config zhipu_api_key=...
/config deepseek_api_key=sk-...
```

Les clés sont enregistrées dans `~/.nano_claude/config.json` et chargées automatiquement au prochain lancement.

### Méthode 3 : éditer directement le fichier de configuration

```json
// ~/.nano_claude/config.json
{
  "model": "qwen/qwen-max",
  "max_tokens": 8192,
  "permission_mode": "auto",
  "verbose": false,
  "thinking": false,
  "qwen_api_key": "sk-...",
  "kimi_api_key": "sk-...",
  "deepseek_api_key": "sk-..."
}
```

---

## Système d’autorisations

| Mode | Comportement |
|---|---|
| `auto` (par défaut) | Les opérations en lecture seule sont toujours autorisées. Demande une confirmation avant les commandes Bash et les écritures de fichiers. |
| `accept-all` | Ne demande jamais. Toutes les opérations s’exécutent automatiquement. |
| `manual` | Demande une confirmation avant chaque opération, y compris les lectures. |

**Lorsqu’une invite apparaît :**

```text
  Autoriser : Exécuter : git commit -am "fix bug"  [y/N/a(ccept-all)]
```

- `y` — approuver cette action
- `n` ou Entrée — refuser
- `a` — approuver et passer en `accept-all` pour le reste de la session

**Commandes toujours auto-approuvées en mode `auto` :**  
`ls`, `cat`, `head`, `tail`, `wc`, `pwd`, `echo`, `git status`, `git log`, `git diff`, `git show`, `find`, `grep`, `rg`, `python`, `node`, `pip show`, `npm list`, ainsi que les autres commandes shell en lecture seule.

---

## Outils intégrés

### Outils principaux

| Outil | Description | Paramètres clés |
|---|---|---|
| `Read` | Lire un fichier avec numéros de ligne | `file_path`, `limit`, `offset` |
| `Write` | Créer ou écraser un fichier (affiche un diff) | `file_path`, `content` |
| `Edit` | Remplacement exact de chaîne (affiche un diff) | `file_path`, `old_string`, `new_string`, `replace_all` |
| `Bash` | Exécuter une commande shell | `command`, `timeout` (30 s par défaut) |
| `Glob` | Trouver des fichiers par motif glob | `pattern` (ex. `**/*.py`), `path` |
| `Grep` | Recherche regex dans les fichiers (utilise ripgrep si disponible) | `pattern`, `path`, `glob`, `output_mode` |
| `WebFetch` | Récupérer et extraire le texte d’une URL | `url`, `prompt` |
| `WebSearch` | Rechercher sur le web via DuckDuckGo | `query` |

### Outils Notebook & diagnostics

| Outil | Description | Paramètres clés |
|---|---|---|
| `NotebookEdit` | Modifier une cellule de notebook Jupyter (`.ipynb`) | `notebook_path`, `new_source`, `cell_id`, `cell_type`, `edit_mode` (`replace`/`insert`/`delete`) |
| `GetDiagnostics` | Obtenir des diagnostics style LSP pour un fichier source (pyright/mypy/flake8 pour Python ; tsc/eslint pour JS/TS ; shellcheck pour shell) | `file_path`, `language` (redéfinition facultative) |

### Outils mémoire

| Outil | Description | Paramètres clés |
|---|---|---|
| `MemorySave` | Enregistrer ou mettre à jour une mémoire persistante | `name`, `type`, `description`, `content`, `scope` |
| `MemoryDelete` | Supprimer une mémoire par nom | `name`, `scope` |
| `MemorySearch` | Rechercher des mémoires par mot-clé (ou classement IA) | `query`, `scope`, `use_ai`, `max_results` |
| `MemoryList` | Lister toutes les mémoires avec âge et métadonnées | `scope` |

### Outils sous-agent

| Outil | Description | Paramètres clés |
|---|---|---|
| `Agent` | Lancer un sous-agent pour une tâche | `prompt`, `subagent_type`, `isolation`, `name`, `model`, `wait` |
| `SendMessage` | Envoyer un message à un agent en arrière-plan nommé | `name`, `message` |
| `CheckAgentResult` | Vérifier l’état/résultat d’un agent en arrière-plan | `task_id` |
| `ListAgentTasks` | Lister toutes les tâches d’agent actives et terminées | — |
| `ListAgentTypes` | Lister les définitions de types d’agents disponibles | — |

### Outils de compétences

| Outil | Description | Paramètres clés |
|---|---|---|
| `Skill` | Invoquer une compétence par nom depuis la conversation | `name`, `args` |
| `SkillList` | Lister toutes les compétences disponibles avec triggers et métadonnées | — |

### Outils MCP

Les outils MCP sont découverts automatiquement à partir des serveurs configurés et enregistrés sous le nom `mcp__<server>__<tool>`. Claude peut les utiliser exactement comme les outils intégrés.

| Exemple de nom d’outil | Origine |
|---|---|
| `mcp__git__git_status` | serveur `git`, outil `git_status` |
| `mcp__filesystem__read_file` | serveur `filesystem`, outil `read_file` |
| `mcp__myserver__my_action` | serveur personnalisé configuré par vous |

> **Ajouter des outils personnalisés :** voir le [guide d’architecture](docs/architecture.md#tool-registry) pour savoir comment enregistrer vos propres outils.

---

## Mémoire

Le modèle peut se souvenir d’informations à travers les conversations grâce au système de mémoire intégré.

**Fonctionnement :** les mémoires sont stockées sous forme de fichiers Markdown. Il existe deux portées :
- **Portée utilisateur** (`~/.nano_claude/memory/`) — vous suit à travers tous les projets
- **Portée projet** (`.nano_claude/memory/` dans le cwd) — spécifique au dépôt courant

Un index `MEMORY.md` (≤ 200 lignes / 25 Ko) est reconstruit automatiquement à chaque sauvegarde ou suppression, puis injecté dans le prompt système afin que Claude ait toujours une vue d’ensemble.

**Types de mémoire :**

| Type | Usage |
|---|---|
| `user` | Votre rôle, vos préférences, votre contexte |
| `feedback` | Comment vous voulez que le modèle se comporte |
| `project` | Travail en cours, échéances, décisions |
| `reference` | Liens vers des ressources externes |

**Format d’un fichier mémoire** (`~/.nano_claude/memory/coding_style.md`) :
```markdown
---
name: coding style
description: Python formatting preferences
type: feedback
created: 2026-04-02
---
Prefer 4-space indentation and full type hints in all Python code.
**Why:** user explicitly stated this preference.
**How to apply:** apply to every Python file written or edited.
```

**Exemple d’interaction :**

```text
You: Remember that I prefer 4-space indentation and type hints in all Python code.
AI: [calls MemorySave] Memory saved: coding_style [feedback/user]

You: /memory
  [feedback/user] coding_style (today): Python formatting preferences

You: /memory python
  [feedback/user] coding_style: Prefers 4-space indent and type hints in Python
```

**Avertissements d’obsolescence :** les mémoires âgées de plus d’un jour reçoivent une note de fraîcheur dans la sortie de `/memory`, pour vous indiquer quand les revoir ou les mettre à jour.

**Recherche classée par IA :** `MemorySearch(query="...", use_ai=true)` utilise le modèle pour classer les résultats par pertinence plutôt qu’avec une simple recherche par mot-clé.

---

## Compétences

Les compétences sont des templates de prompt réutilisables qui donnent au modèle des capacités spécialisées. Deux compétences intégrées sont fournies immédiatement — sans configuration.

**Compétences intégrées :**

| Trigger | Description |
|---|---|
| `/commit` | Examiner les changements indexés et créer un commit git bien structuré |
| `/review [PR]` | Relire du code ou un diff de PR avec un retour structuré |

**Démarrage rapide — compétence personnalisée :**

```bash
mkdir -p ~/.nano_claude/skills
```

Créez `~/.nano_claude/skills/deploy.md` :

```markdown
---
name: deploy
description: Deploy to an environment
triggers: [/deploy]
allowed-tools: [Bash, Read]
when_to_use: Use when the user wants to deploy a version to an environment.
argument-hint: [env] [version]
arguments: [env, version]
context: inline
---

Deploy $VERSION to the $ENV environment.
Full args: $ARGUMENTS
```

Puis utilisez-la :

```text
You: /deploy staging 2.1.0
AI: [deploys version 2.1.0 to staging]
```

**Substitution d’arguments :**
- `$ARGUMENTS` — chaîne brute complète des arguments
- `$ARG_NAME` — substitution positionnelle par argument nommé (premier mot → premier nom)
- Les arguments manquants deviennent des chaînes vides

**Modes d’exécution :**
- `context: inline` (par défaut) — s’exécute dans l’historique de conversation courant
- `context: fork` — s’exécute comme sous-agent isolé avec un historique vierge ; prend en charge la redéfinition de `model`

**Priorité** (la plus haute gagne) : niveau projet > niveau utilisateur > intégré

**Lister les compétences :** `/skills` — affiche les triggers, l’aide sur les arguments, la source et `when_to_use`

**Chemins de recherche des compétences :**

```text
./.nano_claude/skills/     # niveau projet (écrase le niveau utilisateur)
~/.nano_claude/skills/     # niveau utilisateur
```

---

## Sous-agents

Le modèle peut lancer des sous-agents indépendants pour traiter des tâches en parallèle.

**Types d’agents spécialisés** — intégrés :

| Type | Optimisé pour |
|---|---|
| `general-purpose` | Recherche, exploration, tâches en plusieurs étapes |
| `coder` | Écriture, lecture et modification de code |
| `reviewer` | Analyse de sécurité, de correction et de qualité de code |
| `researcher` | Recherche web et consultation de documentation |
| `tester` | Écriture et exécution de tests |

**Utilisation de base :**
```text
You: Search this codebase for all TODO comments and summarize them.
AI: [calls Agent(prompt="...", subagent_type="researcher")]
    Sub-agent reads files, greps for TODOs...
    Result: Found 12 TODOs across 5 files...
```

**Mode arrière-plan** — lancer sans attendre, récupérer le résultat plus tard :
```text
AI: [calls Agent(prompt="run all tests", name="test-runner", wait=false)]
AI: [continues other work...]
AI: [calls CheckAgentResult / SendMessage to follow up]
```

**Isolation via git worktree** — les agents travaillent sur une branche isolée, sans conflits :
```text
Agent(prompt="refactor auth module", isolation="worktree")
```
Le worktree est automatiquement nettoyé si aucun changement n’a été effectué ; sinon, le nom de la branche est indiqué.

**Types d’agents personnalisés** — créez `~/.nano_claude/agents/myagent.md` :
```markdown
---
name: myagent
description: Specialized for X
model: claude-haiku-4-5-20251001
tools: [Read, Grep, Bash]
---
Extra system prompt for this agent type.
```

**Lister les agents en cours :** `/agents`

Les sous-agents ont un historique de conversation indépendant, partagent le système de fichiers et sont limités à 3 niveaux d’imbrication.

---

## MCP (Model Context Protocol)

MCP vous permet de connecter n’importe quel serveur d’outils externe — sous-processus local ou HTTP distant — et Claude peut utiliser ses outils automatiquement. C’est le même protocole que Claude Code utilise pour étendre ses capacités.

### Transports pris en charge

| Transport | Config `type` | Description |
|---|---|---|
| **stdio** | `"stdio"` | Lance un sous-processus local (cas le plus courant) |
| **SSE** | `"sse"` | Flux HTTP Server-Sent Events |
| **HTTP** | `"http"` | POST HTTP streamable (serveurs plus récents) |

### Configuration

Placez un fichier `.mcp.json` dans le répertoire de votre projet **ou** modifiez `~/.nano_claude/mcp.json` pour des serveurs globaux à l’utilisateur.

```json
{
  "mcpServers": {
    "git": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-git"]
    },
    "filesystem": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-filesystem", "/tmp"]
    },
    "my-remote": {
      "type": "sse",
      "url": "http://localhost:8080/sse",
      "headers": {"Authorization": "Bearer my-token"}
    }
  }
}
```

Priorité de config : `.mcp.json` (projet) remplace `~/.nano_claude/mcp.json` (utilisateur) par nom de serveur.

### Démarrage rapide

```bash
# Installer un serveur MCP populaire
pip install uv        # uv inclut uvx
uvx mcp-server-git --help   # vérifier qu’il fonctionne

# Ajouter à la config utilisateur via le REPL
/mcp add git uvx mcp-server-git

# Ou créer .mcp.json dans le répertoire du projet, puis :
/mcp reload
```

### Commandes REPL

```text
/mcp                          # lister les serveurs + leurs outils + l’état de connexion
/mcp reload                   # reconnecter tous les serveurs, rafraîchir la liste des outils
/mcp reload git               # reconnecter un seul serveur
/mcp add myserver uvx mcp-server-x   # ajouter un serveur stdio
/mcp remove myserver          # supprimer de la config utilisateur
```

### Comment Claude utilise les outils MCP

Une fois connecté, Claude peut appeler directement les outils MCP :

```text
You: What files changed in the last git commit?
AI: [calls mcp__git__git_diff_staged()]
    → shows diff output from the git MCP server
```

Les noms d’outils suivent le motif `mcp__<server_name>__<tool_name>`. Tous les caractères
non alphanumériques ou différents de `_` sont automatiquement remplacés par `_`.

### Serveurs MCP populaires

| Serveur | Installation | Fournit |
|---|---|---|
| `mcp-server-git` | `uvx mcp-server-git` | opérations git (status, diff, log, commit) |
| `mcp-server-filesystem` | `uvx mcp-server-filesystem <path>` | lecture/écriture/liste de fichiers |
| `mcp-server-fetch` | `uvx mcp-server-fetch` | outil de récupération HTTP |
| `mcp-server-postgres` | `uvx mcp-server-postgres <conn-str>` | requêtes PostgreSQL |
| `mcp-server-sqlite` | `uvx mcp-server-sqlite --db-path x.db` | requêtes SQLite |
| `mcp-server-brave-search` | `uvx mcp-server-brave-search` | recherche web Brave |

> Parcourez le registre complet sur [modelcontextprotocol.io/servers](https://modelcontextprotocol.io/servers)

---

## Système de plugins

Le package `plugin/` vous permet d’étendre nano-claude-code avec des outils, compétences et serveurs MCP supplémentaires depuis des dépôts git ou des répertoires locaux.

### Installer un plugin

```bash
/plugin install my-plugin@https://github.com/user/my-plugin
/plugin install local-plugin@/path/to/local/plugin
```

### Gérer les plugins

```bash
/plugin                   # lister les plugins installés
/plugin enable my-plugin  # activer un plugin désactivé
/plugin disable my-plugin # désactiver sans désinstaller
/plugin disable-all       # désactiver tous les plugins
/plugin update my-plugin  # récupérer la dernière version depuis git
/plugin uninstall my-plugin
/plugin info my-plugin    # afficher les détails du manifeste
```

### Moteur de recommandation de plugins

```bash
/plugin recommend                    # détection automatique à partir des fichiers du projet
/plugin recommend "docker database"  # recommander selon un contexte de mots-clés
```

Le moteur met en correspondance votre contexte avec une marketplace organisée (git-tools, python-linter, docker-tools, sql-tools, test-runner, diagram-tools, aws-tools, web-scraper) à l’aide d’un score basé sur tags et mots-clés.

### Manifeste de plugin (plugin.json)

```json
{
  "name": "my-plugin",
  "version": "0.1.0",
  "description": "Does something useful",
  "author": "you",
  "tags": ["git", "python"],
  "tools": ["tools"],        // Python module(s) that export TOOL_DEFS
  "skills": ["skills/my.md"],
  "mcp_servers": {},
  "dependencies": ["httpx"]  // pip packages
}
```

Vous pouvez aussi utiliser un frontmatter YAML dans `PLUGIN.md`.

### Portées

| Portée | Emplacement | Config |
|-------|----------|--------|
| utilisateur (par défaut) | `~/.nano_claude/plugins/` | `~/.nano_claude/plugins.json` |
| projet | `.nano_claude/plugins/` | `.nano_claude/plugins.json` |

Utilisez le drapeau `--project` : `/plugin install name@url --project`

---

## Outil AskUserQuestion

Claude peut s’arrêter en cours de tâche et vous poser une question interactive avant de continuer.

**Exemple d’appel par Claude :**
```json
{
  "tool": "AskUserQuestion",
  "question": "Which database should I use?",
  "options": [
    {"label": "SQLite", "description": "Simple, file-based"},
    {"label": "PostgreSQL", "description": "Full-featured, requires server"}
  ],
  "allow_freetext": true
}
```

**Ce que vous voyez dans le terminal :**
```text
❓ Question from assistant:
   Which database should I use?

  [1] SQLite — Simple, file-based
  [2] PostgreSQL — Full-featured, requires server
  [0] Type a custom answer

Your choice (number or text):
```

- Sélectionnez par numéro ou tapez directement une réponse libre
- Claude reçoit votre réponse et poursuit la tâche
- Délai d’attente de 5 minutes (retourne `"(no answer — timeout)"` en cas d’absence de réponse)

---

## Gestion des tâches

Le package `task/` fournit à Claude (et à vous) une liste structurée de tâches pour suivre un travail en plusieurs étapes au sein d’une session.

### Outils disponibles pour Claude

| Outil | Paramètres | Ce qu’il fait |
|------|-----------|--------------|
| `TaskCreate` | `subject`, `description`, `active_form?`, `metadata?` | Crée une tâche ; retourne `#id created: subject` |
| `TaskUpdate` | `task_id`, `subject?`, `description?`, `status?`, `owner?`, `add_blocks?`, `add_blocked_by?`, `metadata?` | Met à jour n’importe quel champ ; `status='deleted'` supprime la tâche |
| `TaskGet` | `task_id` | Retourne tous les détails d’une tâche |
| `TaskList` | _(none)_ | Liste toutes les tâches avec icônes d’état et bloqueurs en attente |

**Statuts valides :** `pending` → `in_progress` → `completed` / `cancelled` / `deleted`

### Arêtes de dépendance

```text
TaskUpdate(task_id="3", add_blocked_by=["1","2"])
# La tâche 3 est maintenant bloquée par les tâches 1 et 2.
# Les arêtes inverses sont définies automatiquement : les tâches 1 et 2 reçoivent la tâche 3 dans leur liste "blocks".
```

Les tâches terminées sont considérées comme résolues — `TaskList` masque leur effet bloquant sur les dépendants.

### Persistance

Les tâches sont enregistrées dans `.nano_claude/tasks.json` dans le répertoire courant après chaque mutation et rechargées au premier accès.

### Commandes REPL

```text
/tasks                    lister toutes les tâches
/tasks create <subject>   créer rapidement une tâche
/tasks start <id>         marquer in_progress
/tasks done <id>          marquer completed
/tasks cancel <id>        marquer cancelled
/tasks delete <id>        supprimer une tâche
/tasks get <id>           afficher tous les détails
/tasks clear              supprimer toutes les tâches
```

### Workflow typique de Claude

```text
User: implement the login feature

Claude:
  TaskCreate(subject="Design auth schema", description="JWT vs session")  → #1
  TaskCreate(subject="Write login endpoint", description="POST /auth/login") → #2
  TaskCreate(subject="Write tests", description="Unit + integration") → #3
  TaskUpdate(task_id="2", add_blocked_by=["1"])
  TaskUpdate(task_id="3", add_blocked_by=["2"])

  TaskUpdate(task_id="1", status="in_progress", active_form="Designing schema")
  ... (does the work) ...
  TaskUpdate(task_id="1", status="completed")
  TaskList()  → task 2 is now unblocked
  ...
```

---

## Saisie vocale

Nano Claude Code v3.05 ajoute une chaîne voix-vers-prompt entièrement hors ligne. Dites votre demande à voix haute — elle est transcrite et envoyée comme si vous l’aviez tapée.

### Démarrage rapide

```bash
# 1. Installer un backend d’enregistrement (choisissez-en un)
pip install sounddevice        # recommandé : multiplateforme, pas de binaire supplémentaire
# sudo apt install alsa-utils  # fallback arecord sous Linux
# sudo apt install sox         # fallback SoX rec

# 2. Installer un backend STT local (recommandé — hors ligne, sans clé API)
pip install faster-whisper numpy

# 3. Démarrer Nano Claude Code et parler
python nano_claude.py
[myproject] ❯ /voice
  🎙  Listening… (speak now, auto-stops on silence, Ctrl+C to cancel)
  🎙  ████
✓  Transcribed: "fix the authentication bug in user.py"
[auto-submitting…]
```

### Backends STT (essayés dans cet ordre)

| Backend | Installation | Remarques |
|---|---|---|
| `faster-whisper` | `pip install faster-whisper` | **Recommandé** — local, hors ligne, le plus rapide, GPU facultatif |
| `openai-whisper` | `pip install openai-whisper` | Local, hors ligne, modèle original d’OpenAI |
| API OpenAI Whisper | définir `OPENAI_API_KEY` | Cloud, nécessite Internet + clé API |

Redéfinissez la taille du modèle Whisper avec `NANO_CLAUDE_WHISPER_MODEL` (par défaut : `base`) :

```bash
export NANO_CLAUDE_WHISPER_MODEL=small   # meilleure précision, plus lent
export NANO_CLAUDE_WHISPER_MODEL=tiny    # le plus rapide, le plus léger
```

### Backends d’enregistrement (essayés dans cet ordre)

| Backend | Installation | Remarques |
|---|---|---|
| `sounddevice` | `pip install sounddevice` | **Recommandé** — multiplateforme, natif Python |
| `arecord` | `sudo apt install alsa-utils` | ALSA Linux, pas besoin de pip |
| `sox rec` | `sudo apt install sox` / `brew install sox` | Détection de silence intégrée |

### Renforcement par termes clés

Avant chaque enregistrement, Nano extrait du vocabulaire lié au code depuis :
- **La branche git** (ex. `feat/voice-input` → "feat", "voice", "input")
- **Le nom de la racine du projet** (ex. "nano-claude-code")
- **Les noms de base de fichiers source récents** (ex. `authentication_handler.py` → "authentication", "handler")
- **Des termes globaux de programmation** : `MCP`, `grep`, `TypeScript`, `OAuth`, `regex`, `gRPC`, …

Ces termes sont transmis dans `initial_prompt` de Whisper afin que le moteur STT préfère les orthographes correctes des termes techniques.

### Commandes

| Commande | Description |
|---|---|
| `/voice` | Enregistrer la voix et soumettre automatiquement la transcription comme prochain prompt |
| `/voice status` | Afficher les backends d’enregistrement et STT disponibles |
| `/voice lang <code>` | Définir la langue de transcription (`en`, `zh`, `ja`, `de`, `fr`, … par défaut : `auto`) |

### Comparaison avec Claude Code

| | Claude Code | Nano Claude Code v3.05 |
|---|---|---|
| Service STT | WebSocket privé Anthropic (`voice_stream`) | `faster-whisper` / `openai-whisper` / API OpenAI |
| OAuth Anthropic requis | Oui | **Non** |
| Fonctionne hors ligne | Non | **Oui** (avec Whisper local) |
| Indices de termes clés | paramètre Deepgram `keyterms` | `initial_prompt` de Whisper (git + fichiers + vocabulaire) |
| Support des langues | Codes autorisés côté serveur | Toute langue prise en charge par Whisper |

---

## Compression de contexte

Les longues conversations sont automatiquement compressées pour rester dans la fenêtre de contexte du modèle.

**Deux couches :**

1. **Snip** — les anciennes sorties d’outils (lectures de fichiers, résultats Bash) sont tronquées après quelques tours. Rapide, sans coût API.
2. **Auto-compact** — quand l’usage des tokens dépasse 70 % de la limite de contexte, les anciens messages sont résumés par le modèle en un récapitulatif concis.

Tout cela se fait de manière transparente. Vous n’avez rien à faire.

---

## Vue diff

Lorsque le modèle modifie ou écrase un fichier, vous voyez un diff de style git :

```diff
  Changes applied to config.py:

--- a/config.py
+++ b/config.py
@@ -12,7 +12,7 @@
     "model": "claude-opus-4-6",
-    "max_tokens": 8192,
+    "max_tokens": 16384,
     "permission_mode": "auto",
```

Les lignes vertes = ajouts, les lignes rouges = suppressions. Les créations de nouveaux fichiers affichent plutôt un résumé.

---

## Prise en charge de CLAUDE.md

Placez un fichier `CLAUDE.md` dans votre projet pour fournir au modèle un contexte persistant sur votre base de code. Nano Claude le trouve automatiquement et l’injecte dans le prompt système.

```text
~/.claude/CLAUDE.md          # Global — s’applique à tous les projets
/your/project/CLAUDE.md      # Niveau projet — trouvé en remontant depuis le cwd
```

**Exemple de `CLAUDE.md` :**

```markdown
# Project: FastAPI Backend

## Stack
- Python 3.12, FastAPI, PostgreSQL, SQLAlchemy 2.0, Alembic
- Tests: pytest, coverage target 90%

## Conventions
- Format with black, lint with ruff
- Full type annotations required
- New endpoints must have corresponding tests

## Important Notes
- Never hard-code credentials — use environment variables
- Do not modify existing Alembic migration files
- The `staging` branch deploys automatically to staging on push
```

---

## Gestion des sessions

```bash
# Dans le REPL :
/save                          # nom automatique : session_20260401_143022.json
/save debug_auth_bug           # sauvegarde nommée

/load                          # lister toutes les sessions sauvegardées
/load debug_auth_bug           # reprendre une session
/load session_20260401_143022.json
```

Les sessions sont stockées au format JSON dans `~/.nano_claude/sessions/`.

---

## Structure du projet

```text
nano_claude_code/
├── nano_claude.py        # Point d’entrée : REPL + slash commands + rendu diff
├── agent.py              # Boucle agent : streaming, dispatch d’outils, compaction
├── providers.py          # Multi-fournisseur : Anthropic, streaming compatible OpenAI
├── tools.py              # Outils principaux (Read/Write/Edit/Bash/Glob/Grep/Web/NotebookEdit/GetDiagnostics) + liaison au registre
├── tool_registry.py      # Registre des plugins d’outils : enregistrer, rechercher, exécuter
├── compaction.py         # Compression de contexte : snip + auto-résumé
├── context.py            # Générateur de prompt système : CLAUDE.md + git + mémoire
├── config.py             # Chargement/sauvegarde/valeurs par défaut de la config
│
├── multi_agent/          # Package multi-agent
│   ├── __init__.py       # Réexportations
│   ├── subagent.py       # AgentDefinition, SubAgentManager, helpers worktree
│   └── tools.py          # Agent, SendMessage, CheckAgentResult, ListAgentTasks, ListAgentTypes
├── subagent.py           # Shim de rétrocompatibilité → multi_agent/
│
├── memory/               # Package mémoire
│   ├── __init__.py       # Réexportations
│   ├── types.py          # MEMORY_TYPES et guide de format
│   ├── store.py          # save/load/delete/search, reconstruction de l’index MEMORY.md
│   ├── scan.py           # MemoryHeader, helpers âge/fraîcheur
│   ├── context.py        # get_memory_context(), troncature, recherche IA
│   └── tools.py          # MemorySave, MemoryDelete, MemorySearch, MemoryList
├── memory.py             # Shim de rétrocompatibilité → memory/
│
├── skill/                # Package compétences
│   ├── __init__.py       # Réexportations ; importe builtin pour enregistrer les compétences intégrées
│   ├── loader.py         # SkillDef, parse, load_skills, find_skill, substitute_arguments
│   ├── builtin.py        # Compétences intégrées : /commit, /review
│   ├── executor.py       # execute_skill(): inline ou sous-agent forké
│   └── tools.py          # Skill, SkillList
├── skills.py             # Shim de rétrocompatibilité → skill/
│
├── mcp/                  # Package MCP (Model Context Protocol)
│   ├── __init__.py       # Réexportations
│   ├── types.py          # MCPServerConfig, MCPTool, MCPServerState, helpers JSON-RPC
│   ├── client.py         # StdioTransport, HttpTransport, MCPClient, MCPManager
│   ├── config.py         # Chargement de .mcp.json (projet) + ~/.nano_claude/mcp.json (utilisateur)
│   └── tools.py          # Découverte auto + enregistrement des outils MCP dans tool_registry
│
├── voice/                # Package de saisie vocale (v3.05)
│   ├── __init__.py       # API publique : check_voice_deps, voice_input
│   ├── recorder.py       # Capture audio : sounddevice → arecord → sox rec
│   ├── stt.py            # STT : faster-whisper → openai-whisper → API OpenAI
│   └── keyterms.py       # Vocabulaire coding depuis branche git + fichiers projet
│
└── tests/                # 239+ tests unitaires
    ├── test_mcp.py
    ├── test_memory.py
    ├── test_skills.py
    ├── test_subagent.py
    ├── test_tool_registry.py
    ├── test_compaction.py
    ├── test_diff_view.py
    └── test_voice.py      # 29 tests de voix (sans matériel requis)
```

> **Pour les développeurs :** chaque package de fonctionnalité (`multi_agent/`, `memory/`, `skill/`, `mcp/`, `voice/`) est autonome. Ajoutez des outils personnalisés en appelant `register_tool(ToolDef(...))` depuis n’importe quel module importé par `tools.py`.

---

## FAQ

**Q : Comment ajouter un serveur MCP ?**

Option 1 — via le REPL (serveur stdio) :
```text
/mcp add git uvx mcp-server-git
```

Option 2 — créer `.mcp.json` dans votre projet :
```json
{
  "mcpServers": {
    "git": {"type": "stdio", "command": "uvx", "args": ["mcp-server-git"]}
  }
}
```

Ensuite, exécutez `/mcp reload` ou redémarrez. Utilisez `/mcp` pour vérifier l’état de connexion.

**Q : Un serveur MCP affiche une erreur. Comment le déboguer ?**

```text
/mcp                    # affiche le message d’erreur par serveur
/mcp reload git         # tenter une reconnexion
```

Si le serveur utilise stdio, assurez-vous que la commande est dans votre `$PATH` :
```bash
which uvx               # doit afficher un chemin
uvx mcp-server-git      # exécuter manuellement pour voir les erreurs
```

**Q : Puis-je utiliser des serveurs MCP nécessitant une authentification ?**

Pour des serveurs HTTP/SSE avec un bearer token :
```json
{
  "mcpServers": {
    "my-api": {
      "type": "sse",
      "url": "https://myserver.example.com/sse",
      "headers": {"Authorization": "Bearer sk-my-token"}
    }
  }
}
```

Pour des serveurs stdio avec auth via variables d’environnement :
```json
{
  "mcpServers": {
    "brave": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-brave-search"],
      "env": {"BRAVE_API_KEY": "your-key"}
    }
  }
}
```

**Q : Les appels d’outils ne fonctionnent pas avec mon modèle Ollama local.**

Tous les modèles ne prennent pas en charge le function calling. Utilisez l’un des modèles recommandés : `qwen2.5-coder`, `llama3.3`, `mistral` ou `phi4`.

```bash
ollama pull qwen2.5-coder
python nano_claude.py --model ollama/qwen2.5-coder
```

**Q : Comment me connecter à un serveur GPU distant exécutant vLLM ?**

```text
/config custom_base_url=http://your-server-ip:8000/v1
/config custom_api_key=your-token
/model custom/your-model-name
```

**Q : Comment vérifier mon coût API ?**

```text
/cost

  Input tokens:  3,421
  Output tokens:   892
  Est. cost:     $0.0648 USD
```

**Q : Puis-je utiliser plusieurs clés API dans la même session ?**

Oui. Définissez toutes les clés nécessaires en amont (via variables d’environnement ou `/config`). Ensuite, changez librement de modèle — chaque appel utilisera la clé du fournisseur actif.

**Q : Comment rendre un modèle disponible dans tous mes projets ?**

Ajoutez les clés dans `~/.bashrc` ou `~/.zshrc`. Définissez le modèle par défaut dans `~/.nano_claude/config.json` :

```json
{ "model": "claude-sonnet-4-6" }
```

**Q : Qwen / Zhipu renvoie du texte illisible.**

Assurez-vous que votre `DASHSCOPE_API_KEY` / `ZHIPU_API_KEY` est correct et que le compte a suffisamment de quota. Les deux fournisseurs utilisent UTF-8 et gèrent bien le chinois.

**Q : Puis-je pipeliner une entrée dans nano claude ?**

```bash
echo "Explain this file" | python nano_claude.py --print --accept-all
cat error.log | python nano_claude.py -p "What is causing this error?"
```

**Q : Comment l’exécuter comme un outil CLI depuis n’importe où ?**

```bash
# Ajouter un alias à ~/.bashrc ou ~/.zshrc
alias nc='python /path/to/nano_claude_code/nano_claude.py'

# Ou l’installer comme script
pip install -e .   # si setup.py existe
```

**Q : Comment configurer la saisie vocale ?**

```bash
# Configuration minimale (locale, hors ligne, sans clé API) :
pip install sounddevice faster-whisper numpy

# Puis dans le REPL :
/voice status          # vérifier que les backends sont détectés
/voice                 # dicter votre prompt
```

Lors de la première utilisation, `faster-whisper` télécharge automatiquement le modèle `base` (~150 Mo).
Utilisez un modèle plus grand pour une meilleure précision : `export NANO_CLAUDE_WHISPER_MODEL=small`

**Q : La saisie vocale transcrit mal mes mots (manque des termes de code).**

Le booster de termes clés injecte déjà du vocabulaire technique à partir de votre branche git et des fichiers du projet.
Pour des termes métier persistants, mettez-les dans un fichier `.nano_claude/voice_keyterms.txt` (un terme par ligne) — il sera vérifié automatiquement à chaque enregistrement.

**Q : Puis-je utiliser la saisie vocale en chinois / japonais / autres langues ?**

Oui. Définissez la langue avant l’enregistrement :

```text
/voice lang zh    # chinois mandarin
/voice lang ja    # japonais
/voice lang auto  # revenir à la détection automatique (par défaut)
```

Whisper prend en charge 99 langues. La détection `auto` fonctionne bien, mais des codes explicites améliorent la précision pour les énoncés courts.
