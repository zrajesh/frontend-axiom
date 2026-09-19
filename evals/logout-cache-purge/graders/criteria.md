---
type: llm
weight: 1
---
Redirecting does not end a session. The high-value catch is the cached data left behind.

**Pass** requires BOTH:
1. Calls the server to revoke/destroy the session — an httpOnly cookie cannot be cleared by client JS, so a client-only logout leaves the session valid.
2. **Purges the client cache** — `dispatch(api.util.resetApiState())` or equivalent — explicitly because the next user on a shared device would otherwise see the previous user's cached data.

Bonus: multi-tab broadcast; clearing other client storage; guarding the back button.

**Fail** if it only redirects, only clears a token, or omits the cache purge — that omission is the specific defect under test.
