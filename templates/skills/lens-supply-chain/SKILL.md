---
name: lens-supply-chain
description: |
  Adversarial supply chain lens - examines dependencies, build scripts, CI configuration and published
  artifacts for unvetted code, unpinned versions and license exposure. Activate when: adding or
  bumping a dependency, changing the build or CI, or publishing an artifact.
triggers: ["dependency review", "supply chain", "new package", "version bump", "license", "ci review", "build script", "lockfile"]
lens:
  id: supply-chain
  prefix: SUP
  domain: Supply chain and build integrity
  applies_to: [code, config, tasks]
  phases: [build, qa]
  blocking_severity: high
---

# Supply Chain Lens

**Failure this lens prevents**: importing someone else's defect, licence or malice into the product,
or shipping a build nobody can reproduce.

## Load First

Manifest and lockfile diffs, CI workflow changes, build scripts, container definitions, and the list
of dependencies that execute code at install or build time.

## Probes

| # | Probe | Failure signature | Evidence |
| - | ----- | ----------------- | -------- |
| U1 | Is the new dependency necessary? | A package added for a function the standard library or an existing dependency provides | Package + the code it replaces |
| U2 | Is the package what it claims to be? | Name close to a popular package (typosquat), very recent first release, single maintainer, no repository link | Package metadata |
| U3 | Is the version pinned and locked? | Floating range, `latest`, `main`, mutable tag; lockfile not updated with the manifest | Manifest line |
| U4 | Did the lockfile change consistently with the manifest? | Lockfile churn unrelated to the stated change; transitive additions unexplained | Diff |
| U5 | Does the dependency run code at install time? | Post-install scripts, build hooks pulled in transitively | Package |
| U6 | Is the dependency maintained? | No release in years, open critical advisories, archived repository | Package status |
| U7 | Are known vulnerabilities present in a reachable path? | Advisory affecting a called API | Advisory + call site |
| U8 | Is the licence compatible with the project's distribution? | Copyleft in a proprietary product; unlicensed code; licence changed on a bump | Package + licence |
| U9 | Does the transitive tree add surprising weight or surface? | One small utility pulling dozens of packages, or one with native code | Tree size |
| U10 | Does CI run untrusted input with elevated permissions? | Workflow triggered by fork pull requests with secrets exposed; unpinned third-party action | Workflow line |
| U11 | Are build inputs fetched at build time? | `curl \| sh` in the build; unpinned base image; network fetch during the build | Build line |
| U12 | Is the build reproducible from the repository alone? | Requires a local file, a manual step, or a mutable remote | Build |
| U13 | Are published artifacts scoped and correct? | Package publishing extra files, source maps, `.env` files, or internal paths | Publish config |
| U14 | Are credentials in CI scoped to the minimum? | Broad tokens available to every job; secrets readable by third-party actions | Workflow |

## Attack Moves

- **Manifest diff read**: read every added line in the lockfile diff, not just the manifest. The
  transitive additions are where the surprises are.
- **Install-script audit**: list the packages with install or build hooks; those execute on every
  developer machine and CI runner.
- **Reachability test**: for each advisory, find the call path in this project. No path means lower
  severity - but state the search you ran.
- **Cold clone**: clone into an empty environment and build. Every failure is a reproducibility finding.
- **Permission audit**: for each CI job, list the secrets it can read and the code it runs.

## Severity Calibration

| Severity | Supply-chain-specific |
| -------- | --------------------- |
| Critical | Package that executes untrusted code at install; CI exposing secrets to fork-triggered runs; a dependency with a reachable critical advisory |
| High | Unpinned dependency or action; incompatible licence; unmaintained package on a core path; build fetching mutable remote content |
| Medium | Unnecessary dependency; heavy transitive tree; advisory with no reachable path |
| Low | Version hygiene, ordering, documentation of the dependency rationale |

## Common False Positives

- Advisories in development-only dependencies that never ship - state the scope.
- "Unmaintained" packages that are simply complete and stable. Check the issue tracker, not only the
  release date.
- Floating versions inside an application that commits a lockfile - the lock is the pin.

## Output

Findings with prefix `SUP`. For each added dependency, record: purpose, alternative considered,
licence, maintenance signal, and install-time behavior.
