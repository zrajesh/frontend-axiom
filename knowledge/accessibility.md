# Accessibility Standards

## Defaults

- Semantic HTML first (`<button>` not `<div onClick>`, `<nav>`, `<label>`) — ARIA is a patch for when semantic HTML genuinely can't express the pattern, not a first resort.
- Every interactive element reachable and operable by keyboard alone: correct tab order (source order, avoid `tabindex` > 0), visible focus states (never `outline: none` without a replacement focus style).
- Skip-to-content link on pages with heavy navigation/headers.

## Forms

- Every input has a associated `<label>` (via `htmlFor`/`id`, not placeholder-as-label).
- Errors announced to assistive tech (`aria-live="polite"` region or `aria-describedby` pointing at the error text), not conveyed by color alone.
- Required fields marked both visually and programmatically (`aria-required` / `required`).

## Color & contrast

- WCAG AA minimum: 4.5:1 for normal text, 3:1 for large text/UI components. Check this as part of `/pixel-check` and `/audit`, not just by eye.
- Never convey state (error, success, disabled) by color alone — pair with an icon/text/pattern.

## Images & media

- Meaningful `alt` text for informative images; `alt=""` for purely decorative ones (never omit `alt` entirely).
- Captions/transcripts for video/audio content where feasible.

## Testing

- Automated: axe-core (or equivalent) in CI/`/audit` to catch the mechanically-detectable issues (missing labels, contrast, ARIA misuse).
- Manual: a keyboard-only pass and a screen-reader spot-check on any new significant flow — automated tools catch roughly a third of real issues, the rest need a human pass.
