# Client Storage Standards

## Decision table

| Storage | Use for | Never for |
|---|---|---|
| **httpOnly Secure cookie** | Auth/session tokens — the only correct place for these | Large data (size limits, sent on every request) |
| **localStorage** | Small, non-sensitive, persistent preferences (theme, locale, dismissed-banner flags) | Auth tokens, PII, anything sensitive (readable by any script — one XSS bug = full compromise) |
| **sessionStorage** | Tab-scoped ephemeral UI state (wizard step, unsaved form draft the user might reload) | Anything sensitive, anything needed beyond the tab's life |
| **IndexedDB** | Larger structured/offline data (cached API results for offline support, large datasets) | Nothing sensitive without app-level encryption — it's still client-readable storage |

## Quick facts

| Storage | Size limit | API |
|---|---|---|
| Cookie | ~4KB per cookie | Synchronous; sent on every matching HTTP request — don't bloat it |
| localStorage / sessionStorage | ~5MB per origin | Synchronous — a large read/write blocks the main thread, don't store big payloads |
| IndexedDB | Much larger (browser/disk-dependent) | Asynchronous — safe for large structured data, doesn't block the main thread |

## Why tokens never go in localStorage/sessionStorage

Both are fully readable by any JavaScript running on the page. A single XSS vulnerability anywhere in the app (a third-party script, a dependency, an unsanitized render) exposes everything stored there. `httpOnly` cookies are invisible to JS entirely — that's the whole point.

## Secure cookie flags (non-negotiable for auth cookies)

- `HttpOnly` — inaccessible to JS
- `Secure` — HTTPS only
- `SameSite=Lax` (or `Strict` if the flow allows) — CSRF mitigation, see `security.md`

## Data normalization in client cache

When caching fetched data client-side (RTK Query cache, IndexedDB for offline), normalize by entity id (see `state-data.md`) rather than storing denormalized nested blobs — avoids duplicate/stale copies of the same record living in multiple places.
