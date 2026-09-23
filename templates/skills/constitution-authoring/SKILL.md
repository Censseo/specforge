---
name: constitution-authoring
description: |
  Write or amend the project constitution - the non-negotiable principles that outrank every spec,
  plan and review. Activate when: creating /memory/constitution.md, amending a principle, or deciding
  whether something belongs in the constitution.
triggers: ["constitution", "project principles", "governing rules", "non-negotiables", "amend the constitution", "setup constitution"]
phase: design
---

# Constitution Authoring

> The constitution is the only document that outranks a specification. Everything in it must be worth
> blocking a release for. Everything else belongs somewhere else.

## The Admission Test

A principle belongs in the constitution only if all four hold:

1. It applies to **every** feature, not to one domain.
2. Violating it is a defect, not a preference.
3. It can be **checked** - by a person or a tool - against a real artifact.
4. The team is willing to **block a release** on it.

If a candidate fails any test, it belongs in the architecture registry, a checklist, or a lint rule.

## Structure

```markdown
# {Project} Constitution

**Version**: {n} | **Ratified**: {date} | **Last amended**: {date}

## Principle {n}: {Short name}

**Statement**: {One sentence, MUST or SHOULD, unambiguous}

**Rationale**: {Why this is worth blocking on}

**Applies to**: {Specs | Plans | Code | Operations - be specific}

**How it is checked**: {The artifact and the observation that proves compliance}

**Exceptions**: {The narrow, named cases - or "None"}
```

## Writing Principles

- Use **MUST** for blocking rules and **SHOULD** for strong defaults. Never use "consider" - a
  principle that suggests is not a principle.
- One rule per principle. A principle with three clauses will be half-enforced.
- State the check. "Code must be secure" is unenforceable; "no endpoint may be deployed without an
  authorization check verifiable in its handler or middleware" is.
- Name the exceptions up front. Undocumented exceptions become precedent.

## Typical Categories

| Category | Example principle |
| -------- | ----------------- |
| Quality | Every bug fix ships with a regression test that fails without the fix |
| Security | Secrets never appear in the repository, the logs or an error response |
| Privacy | Personal data is collected only with a recorded purpose and a retention rule |
| Accessibility | User-facing surfaces meet WCAG 2.2 AA on primary flows |
| Architecture | Domain logic depends on no infrastructure package |
| Testing | No test is skipped or deleted to make a build pass |
| Operations | Every schema change is deployable and reversible without downtime |
| Documentation | A merged feature updates its domain documentation in the same change |

Adopt only what the team will actually enforce. A constitution with ten ignored principles is worse
than one with three enforced ones - it teaches everyone that the document does not mean anything.

## Amending

Amendments are versioned, dated, and carry the reason. When a principle is removed, record why: a
future reader will otherwise re-propose it.

Increment the version on every amendment. Record the migration expectation - does the change apply to
new work only, or must existing code be brought into line, and by when?

## Downstream Effects

Once written, the constitution is loaded by `spec-authoring`, `technical-planning`,
`quality-checklists`, `artifact-analysis` and every gate. A conflict with a MUST is CRITICAL and
blocking, without exception and regardless of which lens found it.

Changing a principle is therefore a change to every future review. Treat it accordingly.
