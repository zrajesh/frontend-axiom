# Caching Standards

You know what the `Cache-Control` directives mean. This is only what we've decided and where teams get burned.

## Layer order

Service Worker → browser HTTP cache → CDN/edge → origin → client API cache (RTK Query). Fix the cheapest, closest layer first; most "we need a CDN" problems are a missing `Cache-Control` header.

## Defaults by asset type

| Asset | Header |
|---|---|
| Hashed build assets (`app.a1b2c3.js`) | `public, max-age=31536000, immutable` |
| HTML, API responses | short `max-age`, or `no-cache` to force revalidation |
| Per-user or sensitive | `private`, or `no-store` when it must never be stored |

Content-hashed filenames are the only cache-busting we use. **Never query-string versioning (`?v=2`)** — some CDNs and proxies strip or ignore query strings, so you get a stale asset with no way to force a refresh.

## CDN / edge

- **TTL per route by how often that route actually changes.** One blanket site-wide TTL is how stale checkout pages happen.
- **Forward only the headers and cookies the origin genuinely needs.** Forwarding everything — cookies especially — puts a per-visitor value in the cache key, fragmenting the cache until the hit rate approaches zero. This is the most common reason a CDN "isn't helping".
- Let the CDN honor origin `Cache-Control` rather than hardcoding edge TTLs that silently drift from what the app intends.
- Edge compute is for redirects, header rewrites, A/B routing — things that would otherwise cost a full origin round trip.

## Service Worker

Only with a genuine offline/PWA requirement. It is a second, developer-owned cache on top of HTTP caching, and a wrong one is worse than none.

| Strategy | For |
|---|---|
| Cache-first | Hashed static assets — safe, the URL changes when content does |
| Network-first, cache fallback | API/data — never serve stale data to an online user |
| Stale-while-revalidate | App shell — instant paint, refresh behind it |

**Bump `CACHE_NAME` and delete old caches on `activate`.** Skip it and old caches accumulate on users' devices indefinitely.

## Client API cache

Covered in `state-data.md`. It is entity-aware — it can invalidate one record — where the HTTP cache only replays bytes by URL. Complementary, not redundant: get the HTTP layer right for network cost, the API layer right for redundant refetching.

**Logout must purge it** (`auth.md`), or the next user on a shared device reads the previous user's data.
