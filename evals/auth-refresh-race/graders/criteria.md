---
type: llm
weight: 1
---
The bug: N parallel 401s each fire their own refresh. With rotating refresh tokens, the first rotation invalidates the rest, which the server reads as token reuse/theft and revokes the session — logging out an active user.

**Pass** requires BOTH:
1. Correctly identifies the concurrency cause — parallel/simultaneous refreshes racing, not merely "the token expired". Must connect it to refresh rotation or reuse-detection invalidating the session.
2. Prescribes **single-flight** refresh: one in-flight refresh promise shared by all waiters (dedupe/mutex/queue), so N 401s trigger exactly one refresh and the rest await it.

Credit as a bonus, not required: flagging the `localStorage` token, or noting refresh must not recurse.

**Fail** if it only suggests retry/backoff, blames clock skew or short expiry, or "fixes" it by extending token lifetime.
