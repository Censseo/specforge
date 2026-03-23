# Analyse ECC (Everything Claude Code) — Recommandations pour SpecForge

> Analyse croisée du repo [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) avec le workflow SpecForge actuel.
> Objectif : identifier les améliorations concrètes applicables à SpecForge.

---

## Sommaire

1. [Setup & Installation](#1-setup--installation)
2. [Hooks & Automatisation](#2-hooks--automatisation)
3. [Quality Gates & Vérification](#3-quality-gates--vérification)
4. [Gestion du Contexte & Mémoire](#4-gestion-du-contexte--mémoire)
5. [Commandes & Skills](#5-commandes--skills)
6. [Sécurité](#6-sécurité)
7. [MCP Servers](#7-mcp-servers)
8. [Multi-Agent & Orchestration](#8-multi-agent--orchestration)
9. [CI/CD & DevOps](#9-cicd--devops)
10. [Apprentissage Continu](#10-apprentissage-continu)
11. [Synthèse des Priorités](#11-synthèse-des-priorités)

---

## 1. Setup & Installation

### Ce que fait SpecForge actuellement
- Installation via `uv tool install` ou `uvx` (one-shot)
- `forge init` avec sélection de l'agent AI et du type de script
- Devcontainer pré-configuré
- Script `check-prerequisites.sh` pour vérifier les outils installés

### Ce qu'ECC apporte

**a) Détection automatique du package manager**
ECC implémente une chaîne de détection à 6 niveaux :
1. Variable d'environnement `CLAUDE_PACKAGE_MANAGER`
2. Config projet `.claude/package-manager.json`
3. Champ `packageManager` dans `package.json`
4. Détection par lock file (package-lock.json, yarn.lock, etc.)
5. Config globale `~/.claude/package-manager.json`
6. Premier package manager disponible

**Recommandation pour SpecForge** : Implémenter une détection similaire pour les outils Python (uv, pip, pipx, conda) dans `forge init` et `forge check`. Actuellement `forge check` vérifie la présence des outils mais ne détecte pas le gestionnaire préféré de l'utilisateur.

**b) Installation sélective par stack**
ECC permet d'installer uniquement les règles/skills pour son stack :
```bash
./install.sh typescript python golang
```

**Recommandation pour SpecForge** : Ajouter une option `--stack` à `forge init` pour pré-charger les skills pertinentes selon la stack technique :
```bash
forge init my-project --ai claude --stack python-django
forge init my-project --ai claude --stack typescript-nextjs
```

**c) Optimisation des tokens dès le setup**
ECC recommande de configurer dès le départ :
```json
{
  "env": {
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50",
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"
  }
}
```

**Recommandation pour SpecForge** : Inclure une étape optionnelle dans `forge init` ou `/specforge.setup` qui propose de configurer ces paramètres de performance dans le settings.json du projet.

---

## 2. Hooks & Automatisation

### Ce que fait SpecForge actuellement
- Script `setup-hooks.sh` pour les git hooks (pré-commit, etc.)
- Pas de hooks Claude Code natifs

### Ce qu'ECC apporte

**a) Architecture de hooks Claude Code complète**
ECC définit 8 types d'événements avec des patterns critiques :

| Pattern | Fonction | Impact |
|---------|----------|--------|
| Secret Detection | Bloque les commits avec AKIA, ghp_, sk_ | Sécurité |
| Console.log Warning | Avertit sur les debug logs | Qualité |
| TypeScript Type Checking | Vérifie les types à chaque édition | Qualité |
| Test Coverage Check | Vérifie 80%+ à la fin de session | Qualité |

**Conventions de codes de sortie** :
- Exit 0 = Autorisé (silencieux)
- Exit 1 = Avertissement (continue)
- Exit 2 = Bloqué (opération annulée)

**Recommandation pour SpecForge** : Créer un template de hooks Claude Code dans `/specforge.setup` :
- **PreToolUse** : Détection de secrets avant chaque `Edit`
- **PostToolUse** : Linting/typecheck après édition
- **Stop** : Validation de couverture de tests en fin de session
- **SessionStart** : Chargement du contexte projet (constitution, architecture)

**b) Hook runtime controls**
```bash
export ECC_HOOK_PROFILE=standard  # minimal|standard|strict
export ECC_DISABLED_HOOKS="pre:bash:tmux-reminder"
```

**Recommandation pour SpecForge** : Ajouter des profils de hooks dans la constitution projet (permissif pour le prototypage, strict pour la production).

---

## 3. Quality Gates & Vérification

### Ce que fait SpecForge actuellement
- `/specforge.validate` : validation par scénarios d'acceptation
- `/specforge.review` : revue de qualité
- `/specforge.analyze` : analyse de cohérence cross-artifacts
- `/specforge.checklist` : génération de checklists

### Ce qu'ECC apporte

**a) Boucle de vérification séquentielle complète**
ECC propose une commande `/verify` qui exécute séquentiellement :
1. Build (compilation sans erreur)
2. Tests (tous passants)
3. Lint (aucune violation de style)
4. Type Check (TypeScript/mypy clean)
5. Security (aucune vulnérabilité connue)
6. Coverage (80%+ de couverture)

Arrêt au premier échec avec rapport.

**Recommandation pour SpecForge** : Enrichir `/specforge.validate` pour inclure cette boucle de vérification technique en plus de la validation fonctionnelle par scénarios. Ajouter une commande `/specforge.verify` dédiée aux quality gates techniques.

**b) Système de checkpoints**
```bash
/checkpoint "OAuth implementation complete"
# ... session se termine ...
/checkpoint restore "OAuth implementation complete"
```

Sauvegarde : état des fichiers, résultats de tests, métriques de couverture, statut de vérification.

**Recommandation pour SpecForge** : Intégrer un mécanisme de checkpoint dans le workflow, lié aux étapes du workflow SDD (après specify, après plan, après tasks, après implement). Cela permettrait de reprendre un workflow interrompu.

---

## 4. Gestion du Contexte & Mémoire

### Ce que fait SpecForge actuellement
- Constitution projet (`.specforge/memory/constitution.md`)
- Architecture Registry (`memory/architecture-registry.md`)
- `/specforge.learn` pour analyser le codebase et mettre à jour l'architecture
- Contexte agent synchronisé via `forge update`

### Ce qu'ECC apporte

**a) Points de compaction stratégiques**
ECC définit quand et quand NE PAS compacter :

**Compacter** :
- Après la phase de recherche (avant d'implémenter)
- Après un milestone majeur
- Après une session de debug
- Après une approche échouée
- À 60-70% du contexte (proactif)

**Ne PAS compacter** :
- En pleine implémentation
- Pendant un debug actif
- Entre des éditions rapides liées
- Avant un run de vérification

**Recommandation pour SpecForge** : Ajouter des instructions de compaction stratégique dans le CLAUDE.md généré, alignées avec les étapes du workflow SDD :
- Compacter entre `specify` et `plan` (changement de mode)
- Compacter entre `plan` et `tasks` (recherche → structuration)
- NE PAS compacter entre `tasks` et `implement` (besoin du contexte complet)

**b) Limite de contexte MCP**
ECC recommande :
- Maximum 10 MCP actifs par projet
- Cible sous 80 outils concurrents
- Chaque description d'outil MCP consomme 50-100 tokens
- Contexte réaliste après MCPs : ~70k sur 200k de fenêtre

**Recommandation pour SpecForge** : Documenter ces limites dans `/specforge.setup-mcp` et recommander de désactiver les serveurs inutilisés. Ajouter un avertissement si plus de 10 MCPs sont configurés.

---

## 5. Commandes & Skills

### Ce que fait SpecForge actuellement
- 24 commandes slash couvrant le workflow SDD complet
- Templates de skills par domaine (architecture, ADR, microservices)
- Setup modulaire (constitution, docs, skills, agents, mcp)

### Ce qu'ECC apporte

**a) Commandes manquantes potentielles**

| Commande ECC | Équivalent SpecForge | Gap |
|-------------|---------------------|-----|
| `/verify` | `/specforge.validate` | Manque la vérification technique (build, lint, types) |
| `/build-fix` | `/specforge.fix` | SpecForge est plus spec-oriented, pas build-oriented |
| `/security-scan` | Aucun | Pas de commande de scan sécurité dédiée |
| `/test-coverage` | Aucun | Pas de commande de couverture de tests |
| `/checkpoint` | Aucun | Pas de système de points de sauvegarde |
| `/loop-start` | Aucun | Pas de boucle autonome |
| `/cost` | Aucun | Pas de suivi de consommation tokens |
| `/model-route` | Aucun | Pas de routage par complexité |
| `/e2e` | Aucun | Pas de génération de tests E2E |
| `/update-codemaps` | `/specforge.learn` | Similaire mais learn est plus orienté architecture |

**Recommandation pour SpecForge** : Considérer l'ajout de ces commandes complémentaires :
1. **`/specforge.verify`** — Quality gates techniques (build + test + lint + types + security + coverage)
2. **`/specforge.security`** — Audit de sécurité (OWASP, secrets, injections)
3. **`/specforge.coverage`** — Analyse de couverture de tests
4. **`/specforge.checkpoint`** — Sauvegarde d'état à chaque étape SDD
5. **`/specforge.e2e`** — Génération de tests end-to-end depuis les scénarios de spec

**b) Skills par écosystème linguistique**
ECC offre 40+ skills par langage avec des patterns très spécifiques :
- Django : models, views, managers, signals, security, TDD
- Spring Boot : DI, REST, JPA, security, TDD
- Go : interfaces, error handling, goroutines, table-driven tests
- React/Next.js : hooks, layouts, SWR/Zustand

**Recommandation pour SpecForge** : Les skills SpecForge actuelles sont orientées architecture (ADR, microservices, DDD). Ajouter des skills orientées **implémentation** par framework pour guider `/specforge.implement` :
- `skills/python-django.md`
- `skills/typescript-nextjs.md`
- `skills/golang-api.md`
- `skills/java-springboot.md`

Ces skills donneraient des conventions de code concrètes à l'agent pendant l'implémentation.

---

## 6. Sécurité

### Ce que fait SpecForge actuellement
- La constitution inclut des principes de sécurité
- Pas de commande ou hook de sécurité dédié

### Ce qu'ECC apporte

**a) Checklist de sécurité systématique**
ECC impose avant chaque merge :
- [ ] Aucun secret hardcodé (AKIA, ghp_, sk_, pk_live_)
- [ ] Requêtes SQL paramétrées
- [ ] Tokens CSRF sur les endpoints modifiant l'état
- [ ] Guards d'authentification sur les routes sensibles
- [ ] Validation d'input (whitelist)
- [ ] Messages d'erreur sans détails internes
- [ ] Données sensibles chiffrées
- [ ] Rate limiting sur les APIs publiques
- [ ] Scan de vulnérabilités des dépendances
- [ ] Logs sans PII

**Recommandation pour SpecForge** : Intégrer cette checklist dans `/specforge.checklist` avec un mode `--security` et dans `/specforge.merge` comme pré-condition.

**b) Hooks de détection de secrets**
```json
{
  "matcher": "tool == \"Edit\"",
  "hooks": [{
    "type": "command",
    "command": "#!/bin/bash\ngrep -E '(AKIA|ghp_|sk_)' \"$file_path\" && exit 2"
  }]
}
```

**Recommandation pour SpecForge** : Inclure ce hook dans le template de setup. C'est une protection zero-cost qui bloque immédiatement la fuite de secrets.

---

## 7. MCP Servers

### Ce que fait SpecForge actuellement
- `/specforge.setup-mcp` pour configurer les serveurs MCP
- Templates de configuration MCP

### Ce qu'ECC apporte

**Stack MCP recommandée avec coûts en tokens** :

| Serveur | Coût tokens | Usage |
|---------|------------|-------|
| GitHub | 60-100 | Issues, PRs, search |
| Playwright | 100-150 | Tests E2E |
| Sequential Thinking | 10-20 | Décisions complexes |
| Memory | 30-50 | Apprentissage cross-session |
| Context | 50-80 | Recherche sémantique |

**Recommandation pour SpecForge** :
1. Documenter le coût en tokens de chaque MCP dans `/specforge.setup-mcp`
2. Recommander le serveur **Sequential Thinking** pour les phases `plan` et `architect` (faible coût, haute valeur pour les décisions complexes)
3. Recommander le serveur **Memory** pour la persistance de la constitution et de l'architecture registry entre sessions
4. Limiter à 5-7 MCPs actifs par défaut

---

## 8. Multi-Agent & Orchestration

### Ce que fait SpecForge actuellement
- `/specforge.setup-agents` pour générer des subagents spécialisés
- Support de 17 agents AI différents

### Ce qu'ECC apporte

**a) Subagents spécialisés par rôle**
ECC définit 28 agents avec des rôles précis :

| Catégorie | Agents | Rôle |
|-----------|--------|------|
| Planning | planner, architect, tdd-guide | Conception |
| Quality | code-reviewer, security-reviewer, refactor-cleaner | Revue |
| Language | typescript-reviewer, python-reviewer, go-reviewer... | Spécialisation |
| Build | go-build-resolver, java-build-resolver... | Résolution d'erreurs |
| Ops | doc-updater, loop-operator, harness-optimizer | Opérationnel |

**Recommandation pour SpecForge** : Enrichir `/specforge.setup-agents` avec des templates de subagents alignés sur le workflow SDD :
- **spec-reviewer** : Revue de spécification (cohérence, complétude, testabilité)
- **plan-reviewer** : Revue de plan technique (faisabilité, risques, alternatives)
- **implementation-reviewer** : Revue de code post-implémentation
- **security-reviewer** : Revue de sécurité avant merge
- **build-resolver** : Résolution d'erreurs de build par langage

**b) Orchestration multi-agent parallèle**
ECC permet l'exécution parallèle de subagents pour des features complexes :
```
/multi-plan → décompose en sous-tâches
/multi-execute --parallel → lance 4 subagents
/orchestrate → synchronise les résultats
```

**Recommandation pour SpecForge** : Pour les features complexes dans `/specforge.implement`, permettre la décomposition en sous-implémentations parallèles quand les tâches sont indépendantes (ex: backend + frontend + tests en parallèle).

---

## 9. CI/CD & DevOps

### Ce que fait SpecForge actuellement
- GitHub Actions pour release, lint, docs
- Release automatique avec semantic versioning
- Génération de packages par agent/script

### Ce qu'ECC apporte

**a) GitHub Actions de qualité intégrées**
```yaml
# Scan sécurité sur PR
- name: Security Audit
  run: npx ecc-agentshield scan --fail-on-critical

# Gate de couverture
- name: Coverage Check
  run: npm test -- --coverage && npx nyc check-coverage --lines 80

# Conventional commits
- name: Commit Lint
  run: npx commitlint --from origin/main
```

**Recommandation pour SpecForge** : Fournir des templates de GitHub Actions dans `/specforge.setup` que les utilisateurs peuvent adopter :
- Workflow de vérification sur PR (build + test + lint + security)
- Validation des conventional commits
- Scan de secrets dans le CI
- Publication automatique de documentation

**b) Conventional Commits enforced**
ECC impose : `feat:`, `fix:`, `refactor:`, `security:`, `docs:`, `test:`, `perf:`

**Recommandation pour SpecForge** : Le hook git de SpecForge (`setup-hooks.sh`) pourrait imposer les conventional commits, alignés avec les étapes SDD :
- `spec:` pour les changements de spécification
- `plan:` pour les changements de plan
- `impl:` pour l'implémentation
- `validate:` pour les corrections de validation

---

## 10. Apprentissage Continu

### Ce que fait SpecForge actuellement
- `/specforge.learn` : analyse le codebase pour mettre à jour l'architecture registry
- Constitution comme mémoire de gouvernance

### Ce qu'ECC apporte

**a) Système d'instincts avec scoring de confiance**
```
/learn-eval → extraire + valider les patterns
/instinct-status → voir avec scores de confiance
/evolve → regrouper en skills réutilisables
```

Scoring :
- **HIGH (0.8+)** — Vu 3+ fois, fiable
- **MEDIUM (0.5-0.8)** — Vu 1-2 fois, à valider
- **LOW (<0.5)** — Expérimental

**Recommandation pour SpecForge** : Enrichir `/specforge.learn` avec :
1. Un scoring de confiance sur les patterns architecturaux détectés
2. Un mécanisme d'export/import des patterns entre projets
3. Une promotion automatique des patterns fréquents en skills

**b) Pipeline Instinct → Skill**
```
learn-eval → instinct-status → evolve → Create SKILL.md → Reference in CLAUDE.md
```

**Recommandation pour SpecForge** : Créer un pipeline similaire :
```
/specforge.learn → patterns détectés → /specforge.evolve (nouveau) → skill formalisée → ajoutée au setup
```

---

## 11. Synthèse des Priorités

### Impact fort / Effort faible (Quick Wins)

| Amélioration | Commande concernée | Effort |
|-------------|-------------------|--------|
| Template de hooks Claude Code (secret detection) | `/specforge.setup` | 1-2h |
| Instructions de compaction stratégique dans CLAUDE.md | `forge init` | 1h |
| Checklist sécurité dans `/specforge.checklist --security` | `/specforge.checklist` | 2-3h |
| Limites MCP documentées dans setup-mcp | `/specforge.setup-mcp` | 1h |
| Configuration tokens/performance dans setup | `/specforge.setup` | 1-2h |

### Impact fort / Effort moyen

| Amélioration | Commande concernée | Effort |
|-------------|-------------------|--------|
| `/specforge.verify` (quality gates techniques) | Nouvelle commande | 1-2j |
| `/specforge.security` (audit dédié) | Nouvelle commande | 1-2j |
| Skills par framework (Django, Next.js, Spring Boot, Go) | Templates | 2-3j |
| Subagents spécialisés (spec-reviewer, security-reviewer) | `/specforge.setup-agents` | 1-2j |
| Checkpoints par étape SDD | Nouvelle commande | 2-3j |

### Impact moyen / Effort élevé

| Amélioration | Commande concernée | Effort |
|-------------|-------------------|--------|
| Orchestration multi-agent parallèle | `/specforge.implement` | 1-2 sem |
| Système d'instincts avec scoring | `/specforge.learn` | 1-2 sem |
| Détection automatique stack/package manager | `forge init` | 3-5j |
| Templates GitHub Actions pour utilisateurs | `/specforge.setup` | 3-5j |
| Boucle autonome (loop) | Nouvelle commande | 1-2 sem |

---

## Conclusion

Le repo ECC est un **catalogue de bonnes pratiques opérationnelles** (hooks, security, CI/CD, token optimization) là où SpecForge est un **framework méthodologique** (spec-driven development, workflows structurés).

Les deux approches sont **complémentaires** :
- **SpecForge excelle** dans la structuration du workflow de développement (spec → plan → tasks → implement → validate)
- **ECC excelle** dans l'outillage opérationnel (hooks, quality gates, sécurité, gestion de contexte)

L'intégration des patterns ECC dans SpecForge renforcerait le framework sur les aspects opérationnels sans compromettre sa méthodologie SDD. Les quick wins (hooks de sécurité, instructions de compaction, configuration de performance) offrent un ROI immédiat.
