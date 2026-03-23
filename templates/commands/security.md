---
description: Run a comprehensive security audit covering OWASP Top 10, secrets, dependencies, and auth
semantic_anchors:
  - OWASP Top 10              # Web application security risks classification
  - Defense in Depth           # Multiple security layers, no single point of failure
  - Principle of Least Privilege  # Minimum permissions needed for each component
  - Zero Trust                 # Never trust, always verify — validate every request
handoffs:
  - label: Fix Security Issues
    agent: specforge.fix
    prompt: Fix the critical and high severity security vulnerabilities found in the audit
  - label: Full Review
    agent: specforge.review
    prompt: Run a full code review incorporating the security findings
  - label: Verify Fixes
    agent: specforge.verify
    prompt: Run quality gates to verify security fixes don't break anything
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

# Security Audit

> **Activated Frameworks**: OWASP Top 10, Defense in Depth, Principle of Least Privilege, Zero Trust.

You are a Security Auditor. Systematically analyze the codebase for vulnerabilities using the OWASP Top 10 framework, detect hardcoded secrets, audit dependencies, and verify authentication/authorization coverage.

## User Input

```text
$ARGUMENTS
```

**Options**:
- `--scope path/` — Limit scan to a specific directory
- `--severity critical|high|medium|all` — Minimum severity to report (default: `high`)
- `--fix` — Auto-fix safe issues (remove exposed secrets, update vulnerable deps)
- `--deps-only` — Only run dependency vulnerability audit
- `--secrets-only` — Only run secret detection scan

---

## Phase 1: Scope & Context

### 1.1: Load Context

Run `{SCRIPT}` to get project paths and context.

### 1.2: Determine Scan Scope

<scope-rules>

- **Feature branch**: If on a feature branch, diff against base branch to focus on changed/added files
- **Full codebase**: If `--scope` not specified and on main/master, scan entire source tree
- **Directory**: If `--scope path/` specified, limit to that directory
- **Exclusions**: Always skip `node_modules/`, `.venv/`, `vendor/`, `target/`, `build/`, `dist/`, `__pycache__/`, `.git/`

</scope-rules>

### 1.3: Identify Technology Stack

From project context, determine applicable checks:
- Web framework → OWASP web-specific checks
- API framework → Auth, input validation, rate limiting
- Database → SQL injection, connection string exposure
- Frontend → XSS, CSRF, CSP headers

---

## Phase 2: Secret Detection

Scan all source files in scope for hardcoded secrets.

### Secret Patterns

| Pattern | Type | Severity |
|---------|------|----------|
| `AKIA[A-Z0-9]{16}` | AWS Access Key ID | Critical |
| `ghp_[a-zA-Z0-9]{36}` | GitHub Personal Access Token | Critical |
| `gho_[a-zA-Z0-9]{36}` | GitHub OAuth Token | Critical |
| `sk-[a-zA-Z0-9]{20,}` | OpenAI / Stripe Secret Key | Critical |
| `sk_live_[a-zA-Z0-9]+` | Stripe Live Secret Key | Critical |
| `pk_live_[a-zA-Z0-9]+` | Stripe Live Publishable Key | High |
| `-----BEGIN.*PRIVATE KEY-----` | Private Key (RSA/EC/etc.) | Critical |
| `password\s*=\s*["'][^"']+["']` | Hardcoded Password | Critical |
| `mongodb(\+srv)?://[^/\s]+` | MongoDB Connection String | High |
| `postgres(ql)?://[^/\s]+` | PostgreSQL Connection String | High |
| `mysql://[^/\s]+` | MySQL Connection String | High |
| `redis://[^/\s]+` | Redis Connection String | High |
| `eyJ[A-Za-z0-9-_]+\.eyJ` | JWT Token | High |
| `xox[bpas]-[a-zA-Z0-9-]+` | Slack Token | Critical |
| `SG\.[a-zA-Z0-9_-]+` | SendGrid API Key | Critical |
| `AIza[0-9A-Za-z_-]{35}` | Google API Key | High |
| `[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com` | Google OAuth Client ID | Medium |

### Additional Checks

- `.env` files committed to git (check `.gitignore`)
- Secrets in test fixtures or seed data
- Credentials in configuration files (not using env vars)
- API keys in frontend/client-side code
- Private keys in repository

### For Each Finding

Report: file path, line number, secret type, severity, masked preview (show first/last 4 chars only).

---

## Phase 3: OWASP Top 10 Analysis

For each applicable category, scan the codebase systematically.

### A01: Broken Access Control

- [ ] Missing auth middleware on protected routes
- [ ] Direct object references without ownership verification
- [ ] CORS misconfiguration (wildcard origins on authenticated endpoints)
- [ ] Missing CSRF tokens on state-changing POST/PUT/DELETE endpoints
- [ ] Privilege escalation paths (user accessing admin functions)
- [ ] Missing rate limiting on sensitive endpoints

### A02: Cryptographic Failures

- [ ] Weak hashing for passwords (MD5, SHA1 — should use bcrypt/scrypt/argon2)
- [ ] Missing encryption for sensitive data at rest
- [ ] Hardcoded encryption keys or IVs
- [ ] HTTP used for sensitive data transmission
- [ ] Weak TLS configuration

### A03: Injection

- [ ] SQL string concatenation instead of parameterized queries
- [ ] Template injection (unescaped user input in HTML templates)
- [ ] OS command injection (unsanitized input in shell commands)
- [ ] NoSQL injection (unsanitized queries in MongoDB/etc.)
- [ ] LDAP injection
- [ ] Log injection (unsanitized input in log messages)

### A04: Insecure Design

- [ ] Missing rate limiting on authentication endpoints
- [ ] No account lockout after failed attempts
- [ ] Sensitive operations without re-authentication
- [ ] Missing audit logging for security-relevant actions
- [ ] Business logic flaws (e.g., negative quantities, price manipulation)

### A05: Security Misconfiguration

- [ ] Debug mode enabled in production config
- [ ] Default credentials in configuration
- [ ] Verbose error messages exposing stack traces or internal paths
- [ ] Unnecessary features/endpoints enabled
- [ ] Missing security headers (CSP, X-Frame-Options, HSTS, X-Content-Type-Options)
- [ ] Directory listing enabled

### A06: Vulnerable and Outdated Components

Run dependency audit using the appropriate tool:

| Project Type | Command |
|---|---|
| Node.js (npm) | `npm audit --json` |
| Node.js (pnpm) | `pnpm audit --json` |
| Node.js (yarn) | `yarn audit --json` |
| Python | `pip-audit --format json` or `safety check --json` |
| Rust | `cargo audit --json` |
| Go | `govulncheck -json ./...` |
| Java (Maven) | `mvn dependency-check:check` |
| Ruby | `bundle-audit check` |
| .NET | `dotnet list package --vulnerable --format json` |

Parse output and list: package, current version, CVE, severity, fixed version.

### A07: Identification and Authentication Failures

- [ ] Weak password policy (no minimum length/complexity)
- [ ] Missing multi-factor authentication option
- [ ] Session fixation vulnerabilities
- [ ] Insecure token storage (localStorage for sensitive tokens)
- [ ] Missing session expiration/timeout
- [ ] Credentials sent over unencrypted channels

### A08: Software and Data Integrity Failures

- [ ] Missing input validation on all endpoints
- [ ] Unverified deserialization of user input
- [ ] Missing integrity checks on file uploads
- [ ] Unsigned or unverified data from external sources
- [ ] Unsafe CI/CD pipeline patterns (secrets in logs, untrusted actions)

### A09: Security Logging and Monitoring Failures

- [ ] PII in application logs (emails, passwords, tokens, SSN)
- [ ] Missing logging for authentication events (login, logout, failed attempts)
- [ ] Missing logging for authorization failures
- [ ] Log injection vulnerabilities
- [ ] No alerting mechanism for suspicious activity

### A10: Server-Side Request Forgery (SSRF)

- [ ] Unvalidated URL inputs used in server-side requests
- [ ] Internal network access from user-controlled URLs
- [ ] Missing URL scheme validation (allowing file://, gopher://)
- [ ] DNS rebinding vulnerabilities

---

## Phase 4: Input Validation Review

For each endpoint or request handler in scope:

1. **Identify input sources**: query params, request body, headers, path params, cookies, file uploads
2. **Check validation exists**: type checking, format validation, length limits, range validation, whitelist validation
3. **Check sanitization**: HTML encoding, SQL escaping, shell escaping, path traversal prevention
4. **Check content type validation**: Accept header, Content-Type enforcement

Report as:

| Endpoint | Input Source | Validation | Sanitization | Status |
|----------|-------------|-----------|-------------|--------|
| POST /api/users | body.email | ✅ format check | ✅ sanitized | PASS |
| GET /api/search | query.q | ❌ no length limit | ❌ raw in SQL | FAIL |

---

## Phase 5: Auth/AuthZ Coverage Map

Map all routes/endpoints and verify protection:

| Route | Method | Auth Required | AuthZ Check | Rate Limited | Status |
|-------|--------|--------------|-------------|-------------|--------|
| /api/users | GET | ✅ JWT | ✅ admin role | ✅ | PASS |
| /api/users/:id | DELETE | ✅ JWT | ❌ no ownership check | ❌ | FAIL |
| /api/public/health | GET | ❌ (correct) | N/A | ✅ | PASS |
| /api/admin/config | POST | ❌ missing | ❌ missing | ❌ | CRITICAL |

---

## Phase 6: Security Report

Create `security/audit-{date}.md` (in feature directory or project root):

```markdown
# Security Audit Report

**Date**: {date} | **Scope**: {scope} | **Severity Filter**: {min_severity}

## Executive Summary

| Severity | Count |
|----------|-------|
| Critical | X |
| High | X |
| Medium | X |
| Low | X |
| **Total** | **X** |

## Secret Detection Results

| # | File | Line | Type | Severity | Preview |
|---|------|------|------|----------|---------|
| 1 | config/db.py | 12 | PostgreSQL URI | High | `post...5432` |

## OWASP Findings

### Critical
| # | Category | File | Line | Issue | Remediation |
|---|----------|------|------|-------|-------------|
| 1 | A03 | user_repo.py | 45 | SQL concatenation | Use parameterized queries |

### High
...

### Medium
...

## Dependency Vulnerabilities

| Package | Version | CVE | Severity | Fix Version |
|---------|---------|-----|----------|-------------|
| lodash | 4.17.20 | CVE-2021-23337 | High | 4.17.21 |

## Auth/AuthZ Coverage

| Metric | Value |
|--------|-------|
| Total Endpoints | X |
| Protected | X |
| Unprotected (intentional) | X |
| **Missing Auth** | **X** |
| **Missing AuthZ** | **X** |
| **Missing Rate Limiting** | **X** |

## Input Validation Coverage

| Metric | Value |
|--------|-------|
| Endpoints Reviewed | X |
| Fully Validated | X |
| Partially Validated | X |
| **No Validation** | **X** |

## Recommendations

### Immediate (Critical)
1. {action with file:line reference}

### Short-term (High)
1. {action}

### Long-term (Medium/Low)
1. {action}
```

---

## Phase 7: Create Action Items

Generate security-tagged tasks for each finding:

```markdown
### Security Corrections (Audit {date})

- [ ] T{id} [CRITICAL] [SECURITY] Remove hardcoded AWS key in config/settings.py:23
- [ ] T{id} [CRITICAL] [SECURITY] Parameterize SQL query in repos/user_repo.py:45
- [ ] T{id} [HIGH] [SECURITY] Add auth middleware to POST /api/admin/config
- [ ] T{id} [HIGH] [SECURITY] Update lodash to 4.17.21 (CVE-2021-23337)
- [ ] T{id} [MEDIUM] [SECURITY] Add rate limiting to /api/auth/login
```

If `tasks.md` exists in the feature directory, insert security tasks after the last completed task (same insertion pattern as `/specforge.review`).

---

## Output

Present findings with severity counts and top issues:

```markdown
## Security Audit Result

**{X} findings** (Critical: {n}, High: {n}, Medium: {n}, Low: {n})

### Top Critical Issues
{list with file:line references}

### Top High Issues
{list}

### Dependency Vulnerabilities
{count} vulnerable packages found

### Auth Coverage
{X}/{Y} endpoints properly protected

### Report
Full report: `security/audit-{date}.md`

### Next Steps
- Critical/High findings → `/specforge.fix` to remediate
- After fixes → `/specforge.verify` to confirm nothing broke
```
