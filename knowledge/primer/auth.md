# Authentication & Session Standards

`storage.md` says *where* a token goes. This says how the whole flow works. Auth bugs are the most expensive class of frontend bug: they don't corrupt one screen, they hand over accounts.

## Where the session lives

| Approach | Use when | Cost |
|---|---|---|
| **httpOnly Secure cookie session** (default) | Anything first-party with a backend you control | Needs CSRF defense (`security.md`) |
| **Access token in memory + httpOnly refresh cookie** | SPA calling an API on another origin | Lost on reload until silent refresh completes — design for it |
| **Token in `localStorage`** | **Never** | One XSS anywhere = account takeover (`storage.md`) |

"In memory" means a module-scoped variable or store slice — never `localStorage`, never `sessionStorage`, and never a global on `window`.

## Token lifetimes

- **Access token: short.** 5–15 minutes. Its only job is to be useless quickly if leaked.
- **Refresh token: long, rotating, httpOnly.** Every refresh issues a new one and invalidates its predecessor.
- **Rotation detection is the point.** If a refresh token is presented twice, treat it as theft: revoke the whole family and force re-authentication. Without this, rotation is bookkeeping, not security.

## Silent refresh

A 401 must not surface as a user-visible error when the session is merely stale.

- Intercept 401 once, refresh, replay the original request. RTK Query does this in a `baseQuery` wrapper; anything else does it in one shared client.
- **Single-flight the refresh.** Ten parallel 401s must trigger one refresh, with the other nine awaiting the same promise. Otherwise you fire ten rotations, nine of which look like token reuse and trip the theft detection above — logging the user out for being *active*.
- Refresh must never recurse: a failed refresh logs out, it does not retry itself.

## Multi-tab

Tabs share cookies but not memory, so they drift apart.

- Broadcast auth transitions across tabs (`BroadcastChannel`, or a `storage` event on a **non-sensitive** flag key — never the token itself).
- Logging out in one tab logs out all of them. A tab still showing a logged-in UI after logout elsewhere is a real and commonly-shipped bug.
- On regaining focus, revalidate rather than trusting stale in-memory state.

## Route protection

- **Enforce server-side.** Middleware, a server component check, or the API itself. Client-side redirects are UX, not a control — the data is already in the bundle by the time they run.
- Never gate on a client-decoded JWT claim. Decode for *display* ("show admin nav"), authorize on the server.
- Protect the API, not just the route. A hidden button with a reachable endpoint is not access control.

## Logout

Logout is server state, not a client redirect.

1. Call the server to revoke the refresh token / destroy the session.
2. Clear the cookie server-side (`Max-Age=0`) — JS cannot clear an httpOnly cookie.
3. Purge client caches. **`dispatch(api.util.resetApiState())`** or equivalent — otherwise the next user on a shared device sees the previous user's cached data.
4. Broadcast to other tabs.

Step 3 is the one most often skipped, and it leaks data between accounts.

## UI states

Auth has a state the 5-state model (`principles.md` §6) doesn't cover: **unknown**. On first paint the app doesn't yet know whether the user is authenticated.

Render a neutral shell during unknown. Never flash the logged-out UI before resolving — that's both a visible flicker and, on a shared screen, an information leak. With SSR, resolve the session server-side so the first paint is already correct.

## OAuth / OIDC

- **Authorization Code + PKCE.** The implicit flow is deprecated; do not use it.
- Generate `state` per attempt, store it server-side or in an httpOnly cookie, and verify it on return — this is your CSRF defense for the callback.
- Validate `nonce` on the ID token.
- Allowlist exact redirect URIs. Never reflect a `returnTo` parameter into a redirect without validating it against an allowlist — that's an open redirect, routinely used for credential phishing.

## What to verify in review

`/frontend-axiom:audit` treats each of these as **Critical**, not a suggestion:

- [ ] No token in `localStorage`/`sessionStorage`
- [ ] Refresh is single-flight and non-recursive
- [ ] Logout revokes server-side *and* purges the client cache
- [ ] Authorization enforced server-side, not only in the client
- [ ] No open redirect via `returnTo`/`next` parameters
- [ ] Auth-state `unknown` handled without flashing the wrong UI
