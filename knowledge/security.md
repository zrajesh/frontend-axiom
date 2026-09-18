# Frontend Security Standards

## Content Security Policy (CSP)

- Strict CSP by default: no `unsafe-inline`, no `unsafe-eval`. Use nonces (per-request, server-generated) or hashes for any inline script that's unavoidable.
- `strict-dynamic` when using nonces, so trusted scripts can load their own dependencies without whitelisting every third-party domain.
- Set `frame-ancestors` in CSP (modern replacement for `X-Frame-Options`) to control who can iframe your site — `'none'` unless embedding is a required feature, then an explicit allowlist.

## XSS prevention

- Never use `dangerouslySetInnerHTML` with unsanitized input. If HTML rendering from user/CMS content is genuinely required, sanitize with DOMPurify (or the framework's equivalent) server-side, not just client-side.
- React escapes text content by default — don't defeat that by concatenating raw HTML strings and injecting them another way (e.g. via `innerHTML` in a ref effect).
- Treat all URLs from user input as untrusted before using in `href`/`src` — block `javascript:` scheme.

## CSRF

- Cookie-based auth: `SameSite=Lax` or `Strict` on the session cookie as the primary defense, plus a CSRF token (double-submit cookie or server-session-bound token) on state-changing requests as defense-in-depth.
- Token-based auth (Bearer in `Authorization` header, not a cookie) is inherently CSRF-resistant since browsers don't auto-attach it — but then XSS becomes the bigger risk (see storage.md on where to keep the token).

## Security headers checklist

- `Strict-Transport-Security` (HSTS) — force HTTPS, include `includeSubDomains` and a long `max-age` once confirmed safe.
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin` (or stricter)
- `Permissions-Policy` — explicitly disable browser features the app doesn't use (camera, microphone, geolocation, etc.)
- `frame-ancestors` (CSP) as covered above for clickjacking protection

## Dependency security

- Lockfile committed, CI runs an audit (`npm audit` / `pnpm audit` or a dedicated scanner) on every PR, not just periodically.
- Automated update PRs (Renovate/Dependabot) so patches land quickly instead of batching into a risky big-bang upgrade.
- Be wary of new/low-download packages with postinstall scripts — prefer well-maintained, widely-used alternatives.

## Input validation & sanitization

- Validate at every trust boundary with a schema (zod or equivalent): form submission, API route handler, and again server-side even if the client already validated — client-side validation is UX, not security.
- Never trust client-supplied IDs/roles/prices — re-derive or re-check authorization and pricing server-side on every mutating request.

## Secrets & tokens

- Nothing secret in `NEXT_PUBLIC_*` env vars — anything prefixed for client exposure is public, full stop.
- Never put an auth token, API key, or PII in `localStorage`/`sessionStorage` — both are readable by any script on the page, so one XSS bug becomes full account takeover. See `storage.md` for where tokens belong (httpOnly secure cookies).
- Minification/obfuscation is not a security control — it slows down casual inspection, not a motivated attacker. Never treat "it's minified" as a reason something sensitive is safe to ship to the client; if it's in the bundle, treat it as public. Don't serve production source maps publicly for the same reason (see `performance.md`).
