---
name: lens-accessibility
description: |
  Adversarial accessibility lens - finds interfaces that exclude keyboard, screen reader, low-vision,
  motor-impaired and reduced-motion users. Activate when: reviewing UI components, forms, modals,
  custom controls, colour changes or navigation flows.
triggers: ["accessibility review", "a11y", "wcag", "screen reader", "keyboard navigation", "contrast", "aria", "accessible"]
lens:
  id: accessibility
  prefix: A11Y
  domain: Accessibility
  applies_to: [spec, code, docs]
  phases: [design, build, qa]
  blocking_severity: high
---

# Accessibility Lens

**Failure this lens prevents**: shipping an interface that a portion of users cannot operate at all.

Target: WCAG 2.2 level AA unless the project states otherwise. Findings cite the failing criterion.

## Load First

The changed components and templates, the design tokens for colour, and the keyboard flow through the
affected screens.

## Probes

| # | Probe | Failure signature | WCAG | Evidence |
| - | ----- | ----------------- | ---- | -------- |
| Y1 | Can every action be performed with the keyboard alone? | Click-only handlers, `div` with `onClick`, drag-only interaction | 2.1.1 | Element |
| Y2 | Is focus visible at all times? | `outline: none` with no replacement | 2.4.7 | Style rule |
| Y3 | Is focus order logical, and is it managed on open/close? | Modal opens without moving focus; focus lost to `body` on close | 2.4.3 | Component |
| Y4 | Is focus trapped inside modal dialogs and released on exit? | Tab escapes to the page behind the overlay | 2.1.2 | Component |
| Y5 | Does every control have an accessible name? | Icon button with no label, input with no associated `<label>` | 4.1.2, 3.3.2 | Element |
| Y6 | Is the semantic element used, or the role supplied? | `div` for button, list, table, heading; custom widget without a role | 1.3.1, 4.1.2 | Element |
| Y7 | Is state exposed programmatically? | Expanded, selected, checked, disabled, invalid only shown visually | 4.1.2 | Element |
| Y8 | Do images and icons have appropriate text alternatives? | Missing `alt`; decorative images announced; icon meaning available only by sight | 1.1.1 | Element |
| Y9 | Is colour contrast sufficient? | Text below 4.5:1, large text below 3:1, UI boundaries below 3:1 | 1.4.3, 1.4.11 | Pair + ratio |
| Y10 | Is colour the only carrier of meaning? | Status conveyed by red/green alone; links distinguished only by colour | 1.4.1 | Element |
| Y11 | Are errors identified in text and linked to their field? | Error shown as a red border only; message not associated with the input | 3.3.1, 3.3.3 | Form |
| Y12 | Are dynamic updates announced? | Toast, async result or validation change with no live region | 4.1.3 | Component |
| Y13 | Does the layout survive zoom and reflow? | Horizontal scrolling at 320px width or 200% zoom; fixed pixel heights clipping text | 1.4.10, 1.4.4 | View |
| Y14 | Is motion reduced when requested, and is nothing auto-playing? | Animation ignoring `prefers-reduced-motion`; carousel without pause | 2.3.3, 2.2.2 | Component |
| Y15 | Are targets large enough and not the only way to act? | Touch targets under 24px with no alternative | 2.5.8 | Element |
| Y16 | Is the page structure navigable? | No landmarks, skipped heading levels, no skip link, missing page title or `lang` | 1.3.1, 2.4.1 | Page |

## Attack Moves

- **Unplug the mouse**: complete each primary flow with the keyboard only. Note where you get stuck
  or lose focus.
- **Turn off the screen**: navigate by the accessibility tree alone. If a control announces as
  "button" with no name, it is unusable.
- **Zoom to 200% and narrow to 320px**: read what is clipped, overlapped or scrolled away.
- **Grayscale the page**: what information disappears?
- **Automated pass then manual pass**: automated tools find roughly a third of issues. Report which
  probes were manual - claiming AA from a tool run alone is a false pass.

## Severity Calibration

| Severity | Accessibility-specific |
| -------- | ---------------------- |
| Critical | A primary flow cannot be completed by keyboard or screen reader at all |
| High | An AA criterion fails on a primary flow: missing names, focus trap escape, contrast failure on body text, unannounced errors |
| Medium | AA failure on a secondary flow; reduced-motion ignored; heading structure broken |
| Low | Redundant ARIA, minor label wording, non-blocking best practice |

## Common False Positives

- Contrast "failures" on disabled controls or purely decorative elements - check the exemption.
- Missing `alt` on an image that is correctly marked decorative (`alt=""`, `aria-hidden`).
- Redundant ARIA flagged as an error where it is harmless; report only when it overrides correct
  native semantics.
- Custom widgets that implement an authoring pattern correctly but differ from a naive expectation.

## Output

Findings with prefix `A11Y`, each citing the WCAG criterion, the failing element, and the fix. State
explicitly which probes were verified manually and which were not verified at all.
