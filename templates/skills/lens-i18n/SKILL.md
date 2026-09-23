---
name: lens-i18n
description: |
  Adversarial internationalisation lens - finds assumptions about language, locale, time zone,
  currency, encoding and name formats baked into code and copy. Activate when: reviewing user-facing
  strings, dates, numbers, money, sorting, names, addresses or anything that varies by locale.
triggers: ["i18n review", "localization", "translation", "timezone", "currency", "locale", "rtl", "unicode"]
lens:
  id: i18n
  prefix: I18N
  domain: Internationalisation and localisation
  applies_to: [spec, contracts, code, data-model, config, docs]
  phases: [design, build]
  blocking_severity: medium
---

# Internationalisation Lens

**Failure this lens prevents**: a system that silently assumes everyone is in one place, speaking one
language, in one calendar.

Even single-locale products inherit these bugs: time zones, unicode names and currency precision are
not optional concerns.

## Load First

User-facing strings in the diff, date and number formatting calls, storage types for temporal and
monetary values, sorting and comparison code, and any locale configuration.

## Probes

| # | Probe | Failure signature | Evidence |
| - | ----- | ----------------- | -------- |
| N1 | Are user-facing strings externalised? | Literal copy inside components or handlers | String location |
| N2 | Are strings composed by concatenation? | `"You have " + n + " items"` - untranslatable word order | Concatenation site |
| N3 | Is pluralisation handled by a plural-rules API? | `n === 1 ? "item" : "items"` - wrong for most languages | Code |
| N4 | Is gender or grammatical agreement assumed? | Templates that only work in one grammatical form | Template |
| N5 | Are timestamps stored in UTC with an explicit type? | Naive datetime; local time in the database; ambiguous type | Field |
| N6 | Is the user's time zone used for display and for "day" boundaries? | Server-local dates; "today" computed in the wrong zone; DST-broken schedules | Code |
| N7 | Are dates formatted by locale, not hardcoded? | `MM/DD/YYYY` in output; parsing ambiguous date strings | Format call |
| N8 | Is money stored in minor units or decimal, with the currency alongside? | Float amounts; amount without currency; assumed 2 decimal places | Field |
| N9 | Are numbers formatted with locale separators? | `1,234.56` hardcoded; parsing user input with the wrong separator | Format or parse |
| N10 | Is text handled as unicode throughout? | Byte-length limits truncating multi-byte characters; case-folding assumptions; emoji breaking a grapheme | Code |
| N11 | Is sorting locale-aware? | Bytewise sort presented as alphabetical; accents misordered | Sort call |
| N12 | Are names and addresses over-constrained? | Required first/last split, ASCII-only validation, mandatory postcode or state | Validation |
| N13 | Are input formats over-validated? | Phone, postcode or tax id regex for one country | Regex |
| N14 | Does the layout survive longer text and RTL? | Fixed-width labels, truncation, layout hardcoded left-to-right | Component |
| N15 | Is the locale resolved from an explicit source? | Locale inferred from IP; no user preference; no fallback chain | Resolution code |
| N16 | Are translated strings given context for translators? | Ambiguous keys with no comment ("Open", "Post") | Key |

## Attack Moves

- **German and Japanese test**: replace every string with a version three times longer, then with one
  much shorter. What breaks visually?
- **Zażółć gęślą jaźń**: run non-ASCII names, emoji and combining characters through validation,
  storage, search and display.
- **Midnight in Auckland**: pick a user in UTC+13 and one in UTC-11. Do "today's report", scheduling
  and expiry behave for both?
- **DST crossing**: schedule something across a DST transition; observe duplicates or gaps.
- **Currency drift**: a currency with zero decimals (JPY) and one with three (BHD). Does the rounding
  still hold?

## Severity Calibration

| Severity | i18n-specific |
| -------- | ------------- |
| Critical | Money rounding or currency confusion producing wrong amounts; data corrupted by encoding assumptions |
| High | Time zone errors changing which day something belongs to; validation rejecting legitimate names or addresses; unicode truncation corrupting stored text |
| Medium | Hardcoded strings or formats in a product that intends to localise; non-locale sorting shown as alphabetical |
| Low | Missing translator context; layout tightness with longer text |

## Common False Positives

- Hardcoded strings in an internal tool with a documented single-locale scope. Check the decision.
- Naive datetimes for values that are genuinely local wall-clock times (a store's opening hour) -
  that can be correct, if the type says so.
- Locale-aware sorting on identifiers or codes where bytewise order is intended.

## Output

Findings with prefix `I18N`. Separate what breaks correctness today (time zones, money, unicode) from
what blocks future localisation (hardcoded strings, layout).
