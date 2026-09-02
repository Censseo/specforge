---
description: Run the adversarial review harness on any target - a diff, a file, a spec, a PR, a directory - through selected domain lenses, with falsification before reporting.
skills:
  - adversarial-review
  - finding-verification
  - quality-gates
semantic_anchors:
  - Red Team / Blue Team
  - Falsification
  - STRIDE
  - FMEA
  - Mutation Testing
  - Blast Radius
handoffs:
  - label: Fix the Findings
    agent: specforge.fix
    prompt: Fix the confirmed blocking findings from the review
  - label: Add Correction Tasks
    agent: specforge.tasks
    prompt: Add correction tasks for the review findings
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --paths-only
  ps: scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly
---

## User Input

```text
$ARGUMENTS
```

# Adversarial Review Harness

Runs a red-team pass over any target and falsifies its own findings before reporting. Load the
`adversarial-review` skill and follow its protocol.

## Invocation

```text
/specforge.harness                              # the current diff vs the base branch
/specforge.harness src/api/                     # a path
/specforge.harness spec.md                      # an artifact
/specforge.harness --lens security,data         # explicit lens selection
/specforge.harness --phase design               # the design-phase default lens set
/specforge.harness --depth deep                 # every triggered lens, no cap
```

Parse the arguments for: a target (path, glob, artifact or diff range), `--lens` (comma-separated lens
ids), `--phase` (`design` | `build` | `qa`), and `--depth` (`quick` | `standard` | `deep`).

Defaults: target is the diff against the base branch; lenses come from the routing table; depth is
`standard` (up to 8 lenses).

## Step 1 - Frame

Run `{SCRIPT}` for repository context, then state in five lines: target, intent, invariants, blast
radius, reversibility. This sets the rigor for everything that follows.

## Step 2 - Select Lenses

If `--lens` was given, use exactly those. Otherwise consult
`adversarial-review/references/lens-registry.md`:

1. Every lens marked mandatory for the artifact types in the target.
2. Every lens whose risk trigger appears in the target.
3. Cap at 8 unless `--depth deep`; split into waves by blast radius if more trigger.

Record the selection and every skip with its reason.

## Step 3 - Red Pass

Run each selected lens's probes against the actual content. Read the source, not a summary. Assume the
target is wrong and look for where. Record candidates in the finding schema - do not filter yet.

## Step 4 - Falsify

Apply `finding-verification` to every candidate: trace the path end to end, run the refutation
checklist, attempt the cheapest empirical proof. Drop everything refuted. Mark surviving findings
`confirmed` or `plausible`, and name the unverified link on every `plausible` one.

## Step 5 - Triage

Dedupe by root cause across lenses. Assign severity by the harness rubric. Mark blocking per
`quality-gates`. Rank by severity, then confidence, then fix cost.

## Step 6 - Report

Use the report format from the `adversarial-review` skill: blocking findings, advisory findings,
coverage table, conditions to clear.

Then offer, without doing any of it unasked:

- Fix the confirmed blocking findings.
- Add correction tasks to `tasks.md`.
- Deep-dive one finding.
- Re-run with different lenses.

## Rules

- No failure path, no finding.
- No evidence anchored to a location, no finding.
- Refuted findings are dropped, not demoted.
- Zero findings is a legitimate result when the coverage table shows the probes ran against real
  content. Say what was checked and found sound.
- A target that cannot be evaluated is BLOCK with reason `not-evaluable`, never PASS.
