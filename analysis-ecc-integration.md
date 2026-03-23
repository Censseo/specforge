# Analyse d'intégration : Everything Claude Code → SpecForge

> Source : [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) (50K+ stars, 28 agents, 119 skills, 60 commands)
>
> Cible : SpecForge v0.0.25 (24 commandes, 5 skills, 7 scripts)

---

## Synthèse exécutive

Everything Claude Code (ECC) est un plugin d'optimisation de performance pour agents IA avec un focus sur la **granularité par langage**, l'**apprentissage continu**, les **hooks événementiels**, et la **parallélisation**. SpecForge est un framework de développement spec-first avec un focus sur la **méthodologie** (spec → plan → tasks → implement → validate).

Les deux projets sont complémentaires : SpecForge excelle en gouvernance et workflow méthodologique, ECC excelle en outillage opérationnel et optimisation runtime. Voici ce qui pourrait enrichir SpecForge.

---

## 1. HOOKS ÉVÉNEMENTIELS (Priorité : HAUTE)

### Ce qu'ECC fait

ECC implémente un système de hooks à 3 niveaux :
- **PreToolUse** : intercepte avant exécution (peut bloquer avec exit code 2)
- **PostToolUse** : analyse après exécution (quality gates, formatage, détection console.log)
- **Lifecycle** : SessionStart, PreCompact, Stop, SessionEnd

Exemples concrets :
- Bloqueur de `npm run dev` hors tmux (préservation des logs)
- Rappel de review avant `git push`
- Suggestion automatique de `/compact` tous les ~50 appels d'outils
- Sauvegarde de contexte avant compaction
- Détection automatique du package manager

### Ce que SpecForge a actuellement

- `setup-hooks.sh` : détecte le type de projet et génère des configs de hooks basiques
- Pas de hooks runtime actifs pendant les sessions

### Recommandations d'intégration

| Hook à ajouter | Type | Impact |
|---|---|---|
| **Pre-push review gate** | PreToolUse/Bash | Empêche le push sans validation spec → implémentation |
| **Spec drift detector** | PostToolUse/Edit | Détecte quand du code modifié diverge de sa spec source |
| **Checklist enforcer** | PreToolUse/Bash | Bloque `/specforge.implement` si checklists incomplètes |
| **Context persistence** | Lifecycle/Stop | Sauvegarde l'état du workflow (tâches en cours, phase actuelle) |
| **Session resume** | Lifecycle/SessionStart | Restaure le contexte de la session précédente |
| **Auto-compact advisor** | PreToolUse | Suggère compaction quand le contexte est trop chargé |
| **Architecture guard** | PostToolUse/Edit | Vérifie que les modifications respectent `architecture-registry.md` |

### Effort estimé

- Créer un répertoire `templates/hooks/` avec des hooks Node.js cross-platform
- Ajouter une commande `/specforge.setup-hooks` (existe déjà en script, à enrichir)
- Modifier `forge init` pour installer les hooks automatiquement

---

## 2. SYSTÈME DE RULES STRATIFIÉES (Priorité : HAUTE)

### Ce qu'ECC fait

Architecture en couches :
```
rules/
├── common/           # 8 fichiers universels
│   ├── coding-style.md
│   ├── git-workflow.md
│   ├── testing.md
│   ├── performance.md
│   ├── patterns.md
│   ├── hooks.md
│   ├── agents.md
│   └── security.md
└── {language}/       # Extensions par langage (12 langages)
```

Les rules sont des instructions **toujours actives** (copiées dans `~/.claude/rules/`) qui guident le comportement de l'agent à chaque interaction.

### Ce que SpecForge a actuellement

- `memory/constitution.md` : principes du projet (similaire mais plus abstrait)
- `memory/architecture-registry.md` : patterns architecturaux
- Module CLAUDE.md par dossier (conventions locales)
- Pas de rules par langage, pas de couche commune standardisée

### Recommandations d'intégration

| Rule à ajouter | Couche | Bénéfice pour SpecForge |
|---|---|---|
| **spec-compliance.md** | common | Toujours vérifier la cohérence code ↔ spec |
| **git-workflow.md** | common | Conventions de branches, commits, PR liées aux features |
| **testing-from-specs.md** | common | Générer les tests depuis les scénarios d'acceptance |
| **security.md** | common | OWASP checks intégrés au workflow validate |
| **Rules par langage** | language | Conventions spécifiques (naming, patterns, frameworks) |

### Implémentation suggérée

```
templates/rules/
├── common/
│   ├── spec-compliance.md      # Règles spec-first
│   ├── git-workflow.md         # Conventions git
│   ├── testing.md              # Tests depuis specs
│   ├── security.md             # OWASP + secure coding
│   └── quality.md              # SOLID, DRY, complexity
└── languages/
    ├── typescript.md
    ├── python.md
    ├── go.md
    └── ...
```

- `/specforge.setup` copie les rules appropriées dans le dossier agent
- Les rules complètent la constitution (constitution = principes projet, rules = standards techniques)

---

## 3. AGENTS SPÉCIALISÉS PAR DOMAINE (Priorité : HAUTE)

### Ce qu'ECC fait

28 agents organisés en 4 catégories :
- **Orchestration** : planner, chief-of-staff, loop-operator, architect
- **Review par langage** : python-reviewer, typescript-reviewer, go-reviewer, etc.
- **Build resolution** : python-build-resolver, java-build-resolver, etc.
- **Spécialistes** : e2e-runner, tdd-guide, doc-updater, security-reviewer, refactor-cleaner

### Ce que SpecForge a actuellement

- `/specforge.setup-agents` génère des fichiers de subagents
- Pas de catalogue d'agents prédéfinis par domaine
- Les commandes SpecForge elles-mêmes font office d'agents (analyze, review, validate)

### Recommandations d'intégration

| Agent à ajouter | Rôle dans le workflow SpecForge |
|---|---|
| **security-reviewer** | Intégré à `/specforge.review` pour audit sécurité dédié |
| **build-error-resolver** | Intégré à `/specforge.fix` pour résolution d'erreurs de build |
| **e2e-runner** | Intégré à `/specforge.validate` pour tests end-to-end |
| **tdd-guide** | Intégré à `/specforge.implement` pour approche TDD |
| **doc-updater** | Intégré à `/specforge.merge` pour mise à jour docs auto |
| **refactor-cleaner** | Nouveau `/specforge.refactor` ou mode de review |
| **{language}-reviewer** | Sous-agents spécialisés invoqués par review selon le stack |

### Implémentation suggérée

- Ajouter un répertoire `templates/agents/` avec des définitions d'agents .md
- `/specforge.setup-agents` utilise la détection de stack pour générer les agents pertinents
- Les commandes existantes délèguent aux sous-agents automatiquement

---

## 4. APPRENTISSAGE CONTINU (Priorité : MOYENNE-HAUTE)

### Ce qu'ECC fait

Système complet de continuous learning :
- `/learn` : extrait des patterns en cours de session
- `/learn-eval` : évalue la qualité des patterns extraits
- `/evolve` : clusterise les patterns en skills réutilisables
- `/instinct-import` / `/instinct-export` : partage de patterns entre projets
- Scoring de confiance sur chaque pattern
- Pruning automatique des patterns périmés

### Ce que SpecForge a actuellement

- `/specforge.learn` : analyse le code pour mettre à jour `architecture-registry.md` et les fichiers CLAUDE.md par module
- Pattern Mining, Code Archaeology (frameworks activés)
- Pas de scoring, pas d'évolution, pas d'export/import

### Recommandations d'intégration

| Fonctionnalité | Impact |
|---|---|
| **Scoring de confiance** | Chaque pattern dans architecture-registry a un score (0-1) basé sur la fréquence d'usage |
| **Pruning automatique** | Suppression des patterns non utilisés depuis N sessions |
| **Pattern evolution** | `/specforge.learn --evolve` regroupe les patterns similaires |
| **Cross-project export** | `/specforge.learn --export` génère un fichier de patterns portable |
| **Cross-project import** | `/specforge.learn --import <file>` intègre des patterns externes |
| **Session tracking** | Suivi des patterns utilisés pour mesurer leur ROI |

### Implémentation suggérée

- Enrichir `learn.md` avec des phases d'évaluation et scoring
- Ajouter un champ `confidence` et `last_used` dans architecture-registry.md
- Nouvelle commande `/specforge.evolve` ou flag `--evolve` sur learn

---

## 5. GESTION DE SESSIONS (Priorité : MOYENNE)

### Ce qu'ECC fait

- `/save-session` : persiste l'état complet de la session
- `/resume-session` : restaure une session précédente
- `/sessions` : liste les sessions disponibles
- `/checkpoint` : snapshot à un milestone
- Hooks automatiques de sauvegarde au Stop/PreCompact
- Session identifiers pour tracking des dépendances

### Ce que SpecForge a actuellement

- Pas de gestion de session
- L'état est implicitement dans les fichiers (tasks.md, plan.md)
- Perte de contexte entre sessions

### Recommandations d'intégration

| Fonctionnalité | Bénéfice |
|---|---|
| **Auto-save on stop** | Hook qui sauvegarde la phase en cours, les tâches restantes, les blockers |
| **Resume context** | Au démarrage, charge automatiquement l'état de la dernière session |
| **Checkpoint par phase** | Snapshot à chaque transition (spec→plan, plan→tasks, etc.) |
| **Session log** | Journal des décisions prises pendant la session |

### Implémentation suggérée

- Fichier `.specforge/session-state.json` avec : phase courante, feature active, tâches en cours, dernière action
- Hook SessionStart qui affiche un résumé et propose de reprendre
- Hook Stop qui persiste l'état

---

## 6. COMMANDES TDD ET QUALITY GATES (Priorité : MOYENNE)

### Ce qu'ECC fait

- `/tdd` : workflow TDD complet (red-green-refactor)
- `/e2e` : tests end-to-end avec orchestration
- `/test-coverage` : analyse de couverture
- `/quality-gate` : validation automatique avant merge
- `/code-review` dédié avec checklist
- Vérification loops : checkpoint vs continuous
- Grader types : binary, rubric scoring, pass@k

### Ce que SpecForge a actuellement

- `/specforge.validate` : BDD/ATDD depuis les specs (scénarios Gherkin)
- `/specforge.review` : code quality + tech debt
- `/specforge.checklist` : compliance manuelle
- Pas de TDD workflow dédié
- Pas de quality gates automatiques
- Pas de métriques de couverture

### Recommandations d'intégration

| Commande/Feature | Description |
|---|---|
| **`/specforge.tdd`** | Workflow TDD intégré : génère les tests depuis spec.md, cycle red-green-refactor |
| **`/specforge.coverage`** | Analyse de couverture mappée aux scénarios d'acceptance |
| **Quality gate dans implement** | Vérification automatique avant de marquer une tâche "done" |
| **Grading system** | Score de qualité par feature (tests pass, coverage, lint, security) |
| **Pre-merge gate** | `/specforge.merge` vérifie tous les quality gates avant fusion |

---

## 7. PARALLÉLISATION ET ORCHESTRATION (Priorité : MOYENNE)

### Ce qu'ECC fait

- `/multi-plan` : planification parallèle de plusieurs features
- `/multi-execute` : exécution parallèle avec git worktrees
- `/orchestrate` : coordination de tâches interdépendantes
- `/pm2` : gestion de processus pour services
- Cascade method (séquentiel) vs parallel (indépendant)
- Progressive context refinement pour les subagents

### Ce que SpecForge a actuellement

- `/specforge.breakdown` : planification détaillée par phases
- Exécution séquentielle des tâches
- Pas de parallélisation native
- Pas de gestion multi-feature

### Recommandations d'intégration

| Fonctionnalité | Description |
|---|---|
| **Multi-feature planning** | `/specforge.specify --batch` pour spécifier plusieurs features en parallèle |
| **Parallel implementation** | Détection des tâches indépendantes dans tasks.md, exécution en worktrees |
| **Progressive context** | Chaque subagent reçoit uniquement le contexte pertinent à sa tâche |
| **Dependency graph** | Visualisation des dépendances entre tâches pour optimiser l'ordonnancement |

---

## 8. OPTIMISATION DE TOKENS ET CONTEXTE (Priorité : MOYENNE)

### Ce qu'ECC fait

- Model routing par complexité de tâche
- System prompt slimming (nettoyage de contexte en arrière-plan)
- Chargement sélectif des skills/instincts
- Suggestion automatique de compaction

### Ce que SpecForge a actuellement

- "Minimal context loading" dans implement.md (les agents chargent leur propre contexte)
- Pas de routing de modèle
- Pas de gestion active du contexte

### Recommandations d'intégration

| Fonctionnalité | Description |
|---|---|
| **Lazy context loading** | Ne charger que la spec/plan/tasks de la feature active |
| **Context budget** | Indicateur de taille du contexte dans les commandes |
| **Compaction advisor** | Hook qui suggère `/compact` quand le contexte dépasse un seuil |
| **Spec summarization** | Résumés automatiques pour les specs longues |

---

## 9. SÉCURITÉ INTÉGRÉE (Priorité : MOYENNE)

### Ce qu'ECC fait

- `/security-scan` : scan de sécurité dédié (1282 tests, 102 rules)
- `security-reviewer` agent spécialisé
- Rules de sécurité par langage
- AgentShield integration

### Ce que SpecForge a actuellement

- OWASP Top 10 référencé dans `review.md` comme semantic anchor
- Security mentionnée dans constitution.md
- Pas de scan dédié, pas de rules de sécurité actives

### Recommandations d'intégration

| Fonctionnalité | Description |
|---|---|
| **`/specforge.security`** | Commande dédiée de scan sécurité |
| **Security skill** | Nouveau skill `templates/skills/security/` avec patterns OWASP |
| **Pre-implement security check** | Vérification des risques de sécurité identifiés dans la spec avant implémentation |
| **Security dans validate** | Ajout d'un mode "security" à `/specforge.validate` |

---

## 10. SKILLS ENRICHIS (Priorité : BASSE-MOYENNE)

### Ce qu'ECC fait

119 skills organisés par domaine :
- Language patterns (12 langages)
- Testing & verification
- Architecture (backend, frontend, API, deployment)
- Data & analytics (ClickHouse, PostgreSQL, migrations)
- Content & business (articles, slides, market research)

### Ce que SpecForge a actuellement

5 catégories de skills :
- Architecture decision records
- Architecture patterns
- Code review
- Microservices patterns
- Tech debt

### Recommandations d'intégration

| Skill à ajouter | Catégorie |
|---|---|
| **testing-patterns/** | TDD, BDD, property-based testing, mutation testing |
| **security-patterns/** | OWASP, auth patterns, data protection |
| **api-design/** | REST, GraphQL, gRPC patterns |
| **deployment-patterns/** | CI/CD, containerization, IaC |
| **database-patterns/** | Migrations, query optimization, schema design |
| **frontend-patterns/** | State management, component design, accessibility |
| **performance-patterns/** | Caching, lazy loading, optimization |

---

## Tableau récapitulatif par priorité

| # | Domaine | Priorité | Effort | Impact |
|---|---|---|---|---|
| 1 | Hooks événementiels | HAUTE | Moyen | Automatisation du workflow, prévention d'erreurs |
| 2 | Rules stratifiées | HAUTE | Moyen | Standards de qualité constants |
| 3 | Agents spécialisés | HAUTE | Élevé | Expertise ciblée par domaine |
| 4 | Apprentissage continu | MOYENNE-HAUTE | Moyen | Amélioration progressive du framework |
| 5 | Gestion de sessions | MOYENNE | Faible | Continuité entre sessions |
| 6 | TDD & Quality Gates | MOYENNE | Moyen | Qualité du code produit |
| 7 | Parallélisation | MOYENNE | Élevé | Vitesse d'exécution |
| 8 | Optimisation tokens | MOYENNE | Faible | Efficacité des sessions |
| 9 | Sécurité intégrée | MOYENNE | Moyen | Réduction des vulnérabilités |
| 10 | Skills enrichis | BASSE-MOYENNE | Faible | Couverture des patterns |

---

## Plan d'implémentation suggéré

### Phase 1 — Fondations (quick wins)
1. Système de rules stratifiées (`templates/rules/`)
2. Hooks de base (pre-push gate, context persistence, session resume)
3. Gestion de session (`.specforge/session-state.json`)

### Phase 2 — Qualité
4. Quality gates dans `/specforge.implement` et `/specforge.merge`
5. Commande `/specforge.tdd` ou mode TDD dans implement
6. Enrichissement de `/specforge.learn` (scoring, pruning)

### Phase 3 — Spécialisation
7. Agents spécialisés (security-reviewer, e2e-runner, build-resolver)
8. Skills additionnels (security, testing, api-design, deployment)
9. Commande `/specforge.security`

### Phase 4 — Performance
10. Parallélisation avec worktrees
11. Optimisation de contexte (lazy loading, compaction advisor)
12. Multi-feature planning

---

## Conclusion

SpecForge a une **fondation méthodologique solide** que ECC n'a pas (spec-first, constitution, architecture registry). ECC apporte un **outillage runtime riche** que SpecForge n'a pas (hooks actifs, rules par langage, agents spécialisés, apprentissage continu).

L'intégration optimale consisterait à **garder le workflow spec-first de SpecForge comme colonne vertébrale** et y greffer les mécanismes opérationnels d'ECC pour renforcer chaque phase du cycle :

```
Spec → [rules + security check] →
Plan → [architect agent] →
Tasks → [dependency graph + parallelization] →
Implement → [TDD guide + quality gates + hooks] →
Validate → [e2e-runner + security scan + coverage] →
Learn → [scoring + evolution + export] →
Merge → [pre-merge gate + doc-updater]
```
