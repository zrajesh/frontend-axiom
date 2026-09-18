# Performance Standards

## Core Web Vitals targets

These three — and only these three — are Google's Core Web Vitals. Don't report anything else as a "Core Web Vital" in an audit.

| Metric | Good | Meaning |
|---|---|---|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | Main content visibly loaded |
| **INP** (Interaction to Next Paint) | ≤ 200ms | Responsiveness to input, replaced FID |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | Visual stability |

## Other key metrics (diagnostic, not CWV)

| Metric | Good | Meaning |
|---|---|---|
| **FCP** (First Contentful Paint) | ≤ 1.8s | Something rendered |
| **TTFB** (Time to First Byte) | ≤ 0.8s | Server responsiveness |

**Lab vs field — these are not interchangeable.** `/pixel-check` and `/audit` measure via the Chrome DevTools MCP, which is a *lab* trace on one machine, on one network, with a warm cache. Google's "Good" thresholds above are defined against *field* data from real users. A passing lab trace is a smoke test, not evidence the targets are met in production — for that you need real-user monitoring, which is why every feature also needs the field-side setup covered in `observability.md`.

## Resource hints

- `<link rel="preload">` — the LCP image/font/critical resource the browser wouldn't otherwise discover early enough.
- `<link rel="prefetch">` — a resource needed for the *next* likely navigation (hover-intent on a link, or a route the user is statistically about to hit).
- `<link rel="preconnect">` / `dns-prefetch` — third-party origins used early (font CDN, analytics, API host) — warms the connection before the request is actually made.
- Don't over-preload: every preload competes for bandwidth with the resources the browser would prioritize itself. Preload only what's actually render-blocking-critical.

## Bundle optimization

- Route-level code splitting is automatic in Next.js — additionally `dynamic(() => import(...))` for heavy, below-the-fold, or conditionally-rendered components (modals, charts, rich text editors).
- No barrel-file imports that pull in an entire library for one function — import the specific submodule.
- **Set a per-route JS budget and enforce it in CI** — a prose instruction to "watch bundle size" is ignored within a sprint. Starting defaults, compressed (brotli/gzip), for first-load JS per route:

  | Route type | Budget |
  |---|---|
  | Landing / marketing / anything SEO-critical | ≤ 100 KB |
  | Standard app route | ≤ 170 KB |
  | Heavy tooling route (editor, dashboard, charts) | ≤ 250 KB, and justified in review |

  Tune to your product, but tune deliberately and in one place. Enforce with `next build` output diffing, `bundlesize`, or Lighthouse CI budgets, and fail the build on a breach (`release-operations.md`). A budget raise is a decision someone signs off on, not a silent commit.
- Run a bundle analyzer in `/audit` for any PR adding a dependency. Flag: a new library duplicating existing capability, a large import for one function, and anything pushing a route toward its budget.
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
