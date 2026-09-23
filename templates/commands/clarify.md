---
description: Identify underspecified areas in the current feature spec by asking highly targeted clarification questions and encoding answers back into the spec.
skills:
  - requirements-clarification
  - lens-requirements
semantic_anchors:
  - Socratic Method       # Guided questioning to uncover assumptions and gaps
  - Requirements Elicitation  # Structured discovery techniques, stakeholder interviews
  - INVEST Criteria       # Validate story quality through targeted questions
  - Cynefin Framework     # Match question depth to problem complexity
  - Active Listening      # Capture intent, not just words
handoffs:
  - label: Build Technical Plan
    agent: specforge.plan
    prompt: Create a plan for the spec. I am building with...
scripts:
   sh: scripts/bash/check-prerequisites.sh --json --paths-only
   ps: scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly
---

## User Input

```text
$ARGUMENTS
```

Use the input to bias prioritisation (a named area, a risk, a depth).

## Method

Apply the **`requirements-clarification`** skill: the coverage taxonomy, the impact-times-uncertainty
ranking, the one-question-at-a-time loop with a leading recommendation, and the rule that every answer
is integrated into the spec immediately.

Run this before `/specforge.plan`. If the user is deliberately skipping it for a spike, proceed but
say that downstream rework risk rises.

## Operational Steps

1. Run `{SCRIPT}` once and parse `FEATURE_DIR` and `FEATURE_SPEC` (optionally `IMPL_PLAN`, `TASKS`).
   If JSON parsing fails, stop and tell the user to run `/specforge.specify` or check the branch.
   For single quotes in arguments use `'I'\''m Groot'`.

2. If the spec file is missing, stop and tell the user to run `/specforge.specify`. Do not create one here.

3. Load the spec and run the coverage scan from the skill. Build the question queue.

4. Run the questioning loop. Ask one question at a time, always leading with your recommendation so
   the user can answer "yes".

5. After **each** accepted answer: append the bullet under `## Clarifications` / `### Session
   YYYY-MM-DD`, apply the answer to the affected section, replace any now-invalid text, and save.

6. Validate after each write and once at the end, per the skill's validation list.

7. Optionally run `lens-requirements` over the updated spec to catch what the questions did not.

## Non-Interactive Mode

When the input says non-interactive (as `/specforge.design` does), the questioning loop still runs -
the questions are what find the ambiguity - but you answer them yourself:

- For each question, apply your own **Recommended** or **Suggested** answer. Never wait for input.
- Record it identically: `- Q: <question> -> A: <answer>` under `## Clarifications`, and integrate it
  into the affected section.
- Mark each auto-applied answer as an assumption in the spec's Assumptions section. An assumption that
  is written down can be attacked by the design review; one that stays in your head cannot.
- Report the count of auto-applied answers separately from user-supplied ones. A design where twelve
  decisions were made for the user is a different artifact from one where two were.

## Report

Questions asked and answered, spec path, sections touched, and the coverage table marking each
category Resolved / Deferred / Clear / Outstanding. Flag any high-impact category left deferred and
recommend whether to proceed to `/specforge.plan`.

If nothing meaningful was found: "No critical ambiguities detected worth formal clarification", plus
the compact coverage summary, then suggest advancing.
