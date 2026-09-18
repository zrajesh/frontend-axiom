# Caching Standards

## Mental model

A request passes through several caching layers before it hits real work: Service Worker cache (if registered) → browser HTTP cache → CDN/edge cache → origin server → the client-side API cache (RTK Query, etc.) for data already fetched into the app. Each layer intercepts before the next — get the cheapest, closest layer right first rather than over-engineering the farthest one.

## HTTP caching (`Cache-Control`)

| Directive | Meaning |
|---|---|
| `public` | Any cache (browser, CDN, proxy) may store it |
| `private` | Only the end-user's browser may store it — required for per-user responses |
| `max-age=N` | Fresh for N seconds, then stale |
| `s-maxage=N` | Like `max-age`, but only for shared caches (CDN) — lets the CDN cache longer/shorter than the browser |
| `no-cache` | May be stored, but must be revalidated with the server before reuse (misleading name — it doesn't mean "don't cache") |
| `no-store` | Never store it anywhere — for sensitive responses |
| `must-revalidate` | Once stale, must revalidate before reuse (no serving stale-while-erroring) |

**Validators** avoid a full re-download when content hasn't changed: `ETag` (content hash) + `If-None-Match`, or `Last-Modified` + `If-Modified-Since` — server replies `304 Not Modified` and the browser reuses its cached copy.

**Cache-busting**: content-hashed filenames (`app.a1b2c3.js`) let hashed static assets carry a far-future `public, max-age=31536000, immutable` — a new deploy produces a new hash/URL, so there's never a stale-cache problem and never a need to manually bust anything. Don't rely on query-string versioning (`?v=2`) for CDN-cached assets — some caches/proxies ignore query strings entirely.

**Defaults by asset type**:
- Hashed static assets (JS/CSS/images with a build hash) → long-lived `immutable`
- HTML and API responses → short `max-age` or `no-cache` (must revalidate) — the URL doesn't change when the content does
- Anything per-user or sensitive → `private`, or `no-store` if it must never be cached at all

## CDN / edge caching

Purpose: absorb traffic at edge locations near the user so requests don't all hit the origin — this is what actually lets a spike in traffic not take the origin down.

- Set TTL per route by how often that route's content actually changes — don't apply one blanket TTL site-wide. Near-static pages (marketing, listings that update occasionally) get long TTLs (hours); frequently-changing or personalized pages get short TTLs (minutes) or bypass the CDN.
- Prefer explicit path-pattern cache behaviors over one default (`*`) behavior for everything — more precise, and typically cheaper since fewer requests need full CDN processing.
- Forward only the request headers/cookies the origin actually needs for that route. Forwarding everything (cookies especially) fragments the cache key per-visitor and collapses your hit rate toward zero.
- Let the CDN honor the origin's `Cache-Control` headers rather than hardcoding edge TTLs that can silently drift out of sync with what the app intends.
- Lightweight edge compute (e.g. CloudFront Functions, Cloudflare Workers) is the right place for simple per-request logic — redirects, header rewrites, A/B routing — that would otherwise cost a full round trip to origin.

## Service Worker caching

Only add a service worker when there's a genuine offline/PWA requirement (see `performance.md`) — it's a second, developer-controlled cache layer on top of HTTP caching, not a replacement for it.

| Strategy | Use for |
|---|---|
| Cache-first | Hashed static assets — safe, they never change under the same URL |
| Network-first, cache fallback | API/data responses — don't show stale data while online, degrade gracefully offline |
| Stale-while-revalidate | App-shell HTML — show the cached shell instantly, refresh it quietly in the background |

Lifecycle: **install** (pre-cache the app shell) → **activate** (delete old cache versions — bump `CACHE_NAME` on every deploy, or old caches accumulate forever) → **fetch** (intercept requests and apply the strategy above).

## Client-side / API caching layer

This is the layer covered in `state-data.md` (RTK Query) — it caches parsed API responses in memory so multiple components share one fetch instead of each re-requesting the same data. Comparable tools: TanStack Query, SWR, Apollo Client (GraphQL, normalized cache). This project defaults to RTK Query to keep one mental model with Redux/devtools — reach for an alternative only with a concrete reason (e.g. a GraphQL backend, where Apollo's normalized cache is the better native fit).

This layer is response-shape-aware — it can invalidate or update at the entity level (see `state-data.md`'s normalization section) — where the HTTP cache above only replays raw bytes by URL. The two layers are complementary, not redundant: get HTTP caching right for the network cost, then the API cache right for avoiding redundant re-renders/re-fetches within the app.
