---
name: lens-operations
description: |
  Adversarial operations lens - checks that the change can be deployed, configured, rolled back,
  operated and afforded. Activate when: reviewing deployment, config, feature flags, migrations
  ordering, infrastructure, runbooks or anything that costs money to run.
triggers: ["operations review", "deployment review", "rollback", "feature flag", "config", "runbook", "infrastructure review", "cost"]
lens:
  id: operations
  prefix: OPS
  domain: Deployability and operations
  applies_to: [plan, config, code, docs]
  phases: [design, qa]
  blocking_severity: high
---

# Operations Lens

**Failure this lens prevents**: a change that is correct in the repository and unshippable in reality.

## Load First

Deployment configuration, environment variables and secrets wiring, migration ordering relative to
the deploy, feature flag usage, infrastructure definitions, and the runbook if one exists.

## Probes

| # | Probe | Failure signature | Evidence |
| - | ----- | ----------------- | -------- |
| G1 | Can this be deployed without downtime? | Schema and code must change simultaneously; no expand-contract path | Sequence |
| G2 | Can it be rolled back after traffic has flowed? | Migration that the previous release cannot read; irreversible data change | Change |
| G3 | Is the deploy order stated and safe in both directions? | Assumes migration-then-code, but the pipeline does the reverse | Pipeline |
| G4 | Is new configuration documented, defaulted and validated at startup? | Undocumented env var; missing value fails at first request, not at boot | Config |
| G5 | Are secrets delivered by the secret mechanism, not the repo or the image? | Secret in the manifest, in an env file, or baked into a layer | Location |
| G6 | Do all environments have what this needs? | Works locally; staging lacks the queue, the bucket or the permission | Environment |
| G7 | Is the feature flag path complete? | Flag with no default, no cleanup plan, or code that breaks when it is off | Flag |
| G8 | Is the change observable at deploy time? | No way to tell whether the new code is serving | Signal |
| G9 | Is there a rollback runbook for the known failure modes? | "Roll back" with no steps for the data left behind | Runbook |
| G10 | Does anything new cost money, and is that bounded? | New managed service, per-request external call, unbounded storage or egress | Resource |
| G11 | Are resource limits and requests set? | No memory limit; container OOM-killed under load; no autoscaling bound | Manifest |
| G12 | Are one-off operations repeatable and recorded? | Manual production step described in a chat message | Step |
| G13 | Does the build produce a reproducible artifact? | Unpinned base image, `latest` tag, build-time network fetch | Build file |
| G14 | Is scheduled or background work owned? | New cron with no owner, no alert, no runbook | Job |
| G15 | Are there new operational dependencies on a person? | Only one person can perform the rollback or read the dashboard | Process |

## Attack Moves

- **Deploy simulation**: write the exact sequence for shipping this to production, then the exact
  sequence for undoing it 30 minutes later with traffic served. Gaps are findings.
- **Fresh environment test**: could a new environment be stood up from the repository alone? List
  every manual step.
- **Config diff**: compare configuration across environments. Anything present in one and absent in
  another is a candidate finding.
- **Bill projection**: multiply the new per-request cost by expected volume. Then by 10x for an
  incident.
- **Bus test**: which steps here require one specific person's knowledge?

## Severity Calibration

| Severity | Operations-specific |
| -------- | ------------------- |
| Critical | The change cannot be rolled back once traffic flows, and no forward fix is prepared; secrets exposed in the image or repo |
| High | Deploy requires downtime that was not agreed; missing configuration fails at runtime rather than at boot; unbounded cost; manual production step with no record |
| Medium | Missing runbook for a known failure; feature flag with no cleanup; missing resource limits |
| Low | Documentation of an otherwise sound process |

## Common False Positives

- "No rollback" for a change that is additive and inert until enabled by a flag.
- Manual steps that are deliberate one-time bootstrap actions, recorded as such.
- Cost concerns for resources within an existing committed budget - check before flagging.

## Output

Findings with prefix `OPS`, plus the deploy and rollback sequences written out explicitly.
