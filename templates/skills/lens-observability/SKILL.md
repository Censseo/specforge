---
name: lens-observability
description: |
  Adversarial observability lens - checks whether a failure would be noticed, diagnosed and attributed
  without adding code. Activate when: reviewing new failure modes, background work, SLO claims,
  logging, metrics, tracing or alerting.
triggers: ["observability review", "logging review", "metrics", "tracing", "alerting", "how would we know", "debuggability", "slo"]
lens:
  id: observability
  prefix: OBS
  domain: Observability and operations signal
  applies_to: [plan, code, config]
  phases: [design, build, qa]
  blocking_severity: medium
---

# Observability Lens

**Failure this lens prevents**: an outage nobody notices, or one nobody can explain at 3am.

## The Governing Question

For each failure mode the change introduces: **how would we know, how fast, and what would we look at
next?** Three unanswerable questions are three findings.

## Load First

The failure inventory from `lens-reliability` if it exists, log and metric emission in the diff,
dashboards and alerts touching this area, and the stated SLO if any.

## Probes

| # | Probe | Failure signature | Evidence to capture |
| - | ----- | ----------------- | ------------------- |
| O1 | Is each new failure mode detectable? | Failure produces no log, no metric, no alert | Failure mode |
| O2 | Do errors carry the context needed to act? | "Error occurred" with no id, input, or cause chain | Log line |
| O3 | Is the correlation id propagated end to end? | Cannot follow one request across services or into jobs | Hop where it drops |
| O4 | Is background work visible? | Job success, failure, duration and backlog unmeasured | Job |
| O5 | Are the four golden signals available for this path? | No rate, errors, duration or saturation measurement | Path |
| O6 | Do alerts fire on symptoms users feel, not on causes? | Alert on CPU, none on error rate or latency | Alert config |
| O7 | Is the alert actionable? | No runbook link, no owner, no clear first step | Alert |
| O8 | Is log volume and cardinality sane? | Per-item logging on a hot loop; user id as a metric label | Emission site |
| O9 | Do logs avoid secrets and personal data? | Tokens, bodies, emails in log lines | Log line |
| O10 | Are log levels meaningful? | Everything at info; handled cases at error; real failures at debug | Emission sites |
| O11 | Can a specific user's problem be investigated? | No way to find the request for a reported failure | Missing dimension |
| O12 | Is the deployment visible in the signals? | No version or release marker on metrics; cannot attribute a regression | Config |
| O13 | Are timeouts and retries observable? | Retry storms invisible; slow dependency indistinguishable from slow service | Instrumentation gap |
| O14 | Is a claimed SLO measurable with what exists? | SLO stated with no corresponding measurement | Claim + gap |

## Attack Moves

- **3am drill**: an alert fires. Write the first five steps of the investigation using only the
  signals that exist today. Where the trail goes cold is a finding.
- **Silent failure test**: for each failure mode, ask what page or dashboard changes. If none changes,
  it is silent.
- **Attribution test**: latency doubles after a deploy. Can the signals attribute it to a component,
  a version and a query?
- **Cardinality audit**: list the labels on new metrics. Any unbounded value (id, path, email) is a
  finding before it is a cost incident.
- **Noise audit**: would this alert have fired ten times last month for something nobody acted on?

## Severity Calibration

| Severity | Observability-specific |
| -------- | ---------------------- |
| Critical | Personal data or secrets written to logs |
| High | A primary-flow failure mode is entirely silent; correlation is impossible across the main request path; unbounded metric cardinality |
| Medium | Background job unmeasured; alert on cause rather than symptom; error logs lacking context |
| Low | Log level tuning; message wording; dashboard layout |

## Common False Positives

- "No metric" where the platform emits it automatically (service mesh, APM agent, framework
  middleware). Verify what the platform already provides.
- Missing tracing in a single-process application where logs carry the same correlation.
- Alert noise concerns for an alert that is deliberately informational and routed to a low-priority
  channel.

## Output

Findings with prefix `OBS`, plus a detection table:

```markdown
| Failure mode | Signal today | Time to detect | First diagnostic step | Gap |
| ------------ | ------------ | -------------- | --------------------- | --- |
```
