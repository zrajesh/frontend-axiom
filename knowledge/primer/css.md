# CSS / Styling Standards

## Approach selection (ask, don't assume — see `/init-project`)

| Approach | Good fit when |
|---|---|
| **Tailwind CSS** | Team wants speed + consistency via design tokens in config, no context-switching to separate files |
| **CSS Modules** | Team prefers plain CSS/SCSS, scoped by default, no runtime cost |
| **Styled Components / Emotion** | Heavy dynamic/theme-driven styling logic tied to component props (runtime cost — ships JS to compute styles; avoid for large static sites where CSS-in-JS hurts TTFB/bundle) |

Whichever is chosen, it's fixed for the project in the root `CLAUDE.md` — don't mix approaches within one codebase.

## Structure & naming

- Design tokens (color, spacing, radius, type scale) defined once (Tailwind config, or CSS custom properties) — never hardcoded magic values (`padding: 13px`) in components.
- Mobile-first: base styles target the smallest viewport, `min-width` media queries layer up.
- Prefer container queries over viewport media queries for components that must adapt based on their container, not the page (reusable components dropped into varying layouts).

## Avoiding layout shift (CLS)

- Reserve space for anything that loads late: explicit `width`/`height` or `aspect-ratio` on images/embeds, skeleton loaders sized to match final content, never let ads/late-loading widgets push content down without a reserved slot.
- `font-display: swap` (or `next/font`'s default handling) so text isn't invisible during font load, but layout dimensions are pre-computed via font metrics to avoid reflow when the real font swaps in.

## Critical rendering path

- Keep above-the-fold CSS minimal and inlined/critical where the framework supports it (Next.js handles this automatically for its own stylesheets).
- Avoid `@import` in CSS (serial blocking request) — use bundler-level imports instead.
- Don't ship unused CSS: Tailwind's JIT/content-scanning or CSS Modules' inherent scoping both help here; audit with the coverage tab in Chrome DevTools MCP during `/pixel-check` or `/audit` if bundle size is flagged.

## Responsive & theming

- Support light/dark via CSS custom properties or Tailwind's `dark:` variant — never hardcode colors that ignore a theme switch.
- Test real breakpoints, not just resizing a desktop browser: verify at common device widths (360, 390, 768, 1024, 1440).
