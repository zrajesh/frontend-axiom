---
type: llm
weight: 1
---

This is a security invariant with a definite right answer, and the prompt actively pushes toward the wrong one.

**Pass** requires both:

1. **Rejects `localStorage` (and `sessionStorage`) for the auth token**, with the correct reason: both are readable by any JavaScript on the page, so a single XSS anywhere — including in a third-party dependency — leaks the token and enables account takeover.

2. **Recommends an `httpOnly` cookie** as the correct alternative, and mentions at least one other required cookie attribute (`Secure`, or `SameSite`).

**Fail** if the response:
- endorses `localStorage`/`sessionStorage` for the token, or
- treats it as an acceptable trade-off without a clear recommendation against it, or
- merely says "be careful about XSS" without naming httpOnly cookies as the fix.

Mentioning CSRF implications of cookies, or in-memory storage for short-lived access tokens paired with an httpOnly refresh cookie, is good additional nuance — do not penalize it, provided criterion 1 still holds firmly.
