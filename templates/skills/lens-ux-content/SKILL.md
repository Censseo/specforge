---
name: lens-ux-content
description: |
  Adversarial UX and content lens - finds flows that dead-end, states nobody designed and messages
  that leave users stuck. Activate when: reviewing user flows, error messages, empty states,
  destructive actions, onboarding or any user-facing copy.
triggers: ["ux review", "user flow", "error message", "empty state", "copy review", "microcopy", "usability", "destructive action"]
lens:
  id: ux-content
  prefix: UX
  domain: User experience and content
  applies_to: [idea, spec, code, docs]
  phases: [design, qa]
  blocking_severity: medium
---

# UX and Content Lens

**Failure this lens prevents**: a feature that technically works and practically strands the user.

## Load First

The user scenarios in `spec.md`, the actual strings in the diff, and the screens or responses the
change produces.

## The Five States

Every surface that loads or submits data has five states. Missing states are the most common finding.

| State | Question |
| ----- | -------- |
| Empty | First use, no data yet - is there guidance, or a blank void? |
| Loading | Is progress shown, and is the wait bounded? |
| Partial | Some data, some failed - is the failure visible without hiding what worked? |
| Error | What went wrong, whose fault, what to do now? |
| Ideal | The designed case |

## Probes

| # | Probe | Failure signature | Evidence |
| - | ----- | ----------------- | -------- |
| X1 | Are all five states designed for each new surface? | Only the ideal state exists | Surface + missing states |
| X2 | Does every error message say what to do next? | "An error occurred", "Invalid input", error codes with no remedy | Message |
| X3 | Does the message blame the system, not the user? | "You entered an invalid value" for a format the field never explained | Message |
| X4 | Are validation rules stated before submission? | Requirements revealed only by failing | Form |
| X5 | Is destructive action confirmed, reversible, or both? | Immediate irreversible delete with no undo and no confirmation | Action |
| X6 | Does the user know what happened after an action? | Silent success; no feedback on save | Action |
| X7 | Is a long operation given progress and an exit? | Spinner with no timeout, no cancel, no expectation | Operation |
| X8 | Is jargon avoided or explained? | Internal entity names, HTTP codes, stack terms shown to users | String |
| X9 | Is the user's work preserved on failure? | Form clears on validation error; navigation loses input | Flow |
| X10 | Is the flow completable without prior knowledge? | Step requiring information the user was never asked for or shown | Step |
| X11 | Are defaults the safe and common choice? | Destructive or expensive option pre-selected; opt-out by default | Default |
| X12 | Is terminology consistent across the UI? | Same concept called three things in three screens | Term map |
| X13 | Does the copy avoid promising what the system does not do? | "Instantly", "always", "never" contradicting the actual behavior | String |
| X14 | Is the tone consistent and non-alarming for recoverable problems? | Red alerts for routine states | Message |
| X15 | Is there a path back from every screen? | Dead-end page with no navigation, no back, no retry | Screen |

## Attack Moves

- **The stranger walkthrough**: complete the flow as someone who has never seen the product, in a
  hurry, on a phone, with a flaky connection.
- **State enumeration**: for every surface, list the five states and find the code that renders each.
- **Message audit**: collect every user-facing string in the diff into one list and read it as a
  whole. Inconsistency and jargon become obvious.
- **Failure tour**: force each failure the system can produce and read what the user sees.
- **Undo test**: for every action, ask how the user reverses it. No answer means the confirmation
  must carry the weight.

## Severity Calibration

| Severity | UX-specific |
| -------- | ----------- |
| Critical | A destructive irreversible action with no confirmation and no undo; a flow with no exit that loses user data |
| High | A primary flow dead-ends; errors give no path forward; user input lost on failure; missing empty state on the first-run surface |
| Medium | Missing loading or partial states; jargon in user-facing copy; inconsistent terminology |
| Low | Tone, wording polish, minor inconsistency |

## Common False Positives

- Missing states on internal admin tools where the standard is deliberately lower - check the audience.
- "Jargon" that is the user's own domain vocabulary. Developers' jargon and users' jargon are not
  the same thing.
- Confirmation dialogs missing on actions that are trivially reversible - confirmation fatigue is
  itself a UX defect.

## Output

Findings with prefix `UX`. For copy findings, propose the replacement string, not just the objection.
