# Performance Standards

## Core Web Vitals targets

| Metric | Good | Meaning |
|---|---|---|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | Main content visibly loaded |
| **INP** (Interaction to Next Paint) | ≤ 200ms | Responsiveness to input, replaced FID |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | Visual stability |
| **FCP** (First Contentful Paint) | ≤ 1.8s | Something rendered |
| **TTFB** (Time to First Byte) | ≤ 0.8s | Server responsiveness |

`/pixel-check` and `/audit` should check these via the Chrome DevTools MCP's performance trace tooling, not just eyeball it.

## Resource hints

- `<link rel="preload">` — the LCP image/font/critical resource the browser wouldn't otherwise discover early enough.
- `<link rel="prefetch">` — a resource needed for the *next* likely navigation (hover-intent on a link, or a route the user is statistically about to hit).
- `<link rel="preconnect">` / `dns-prefetch` — third-party origins used early (font CDN, analytics, API host) — warms the connection before the request is actually made.
- Don't over-preload: every preload competes for bandwidth with the resources the browser would prioritize itself. Preload only what's actually render-blocking-critical.

## Bundle optimization

- Route-level code splitting is automatic in Next.js — additionally `dynamic(() => import(...))` for heavy, below-the-fold, or conditionally-rendered components (modals, charts, rich text editors).
- No barrel-file imports that pull in an entire library for one function — import the specific submodule.
- Run a bundle analyzer as part of `/audit` for any PR that adds a new dependency; flag anything that meaningfully grows the shipped JS for a marginal feature.
- Dedupe overlapping dependencies (e.g. two date libraries) — flag in audits.

## Images & fonts

- `next/image` (or equivalent): responsive `sizes`, modern formats (AVIF/WebP) served automatically, lazy-load anything below the fold, `priority` reserved for the actual LCP element only.
- `next/font`: self-hosted, no external font-CDN round trip, subset to the character sets actually used.

## Network

- Compression (Brotli preferred, gzip fallback) enabled at the edge/CDN.
- Cache-Control headers tuned per asset type: long-lived immutable caching for hashed static assets, short/no-cache for HTML/API responses that must stay fresh.
- CDN in front of static assets and, where the platform supports it, edge caching for cacheable SSR/ISR responses.

## INP / long tasks

- Break up long synchronous work (>50ms blocks) — chunk it or move it off the main thread (web worker) for genuinely heavy computation.
- Defer non-critical JS (analytics, chat widgets) via `next/script` `lazyOnload` so it doesn't compete with interaction responsiveness during load.
- Debounce/throttle expensive handlers (search-as-you-type, scroll listeners).

## Service workers

- Use when the app has a real offline/PWA requirement — not by default for a standard SSR site (adds complexity and a stale-cache risk otherwise).
- Caching strategy per resource type: cache-first for hashed static assets (safe, they never change), network-first (with cache fallback) for API/data so users don't see stale data when online, stale-while-revalidate for things like app-shell HTML.
