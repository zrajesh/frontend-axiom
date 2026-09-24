# Observability Standards

If you cannot tell, right now, whether the app is broken for a meaningful fraction of users, it is not production-grade. At millions of users daily, the gap between "a bug shipped" and "someone noticed" is measured in revenue.

## Lab data vs field data — the distinction that matters most

| | Lab (synthetic) | Field (real users) |
|---|---|---|
| Source | Lighthouse, Chrome DevTools traces, CI perf runs | RUM from real sessions, CrUX |
| Answers | "Did this change make it slower?" | "Is it actually fast for our users?" |
| Good for | Catching regressions pre-merge, debugging | Knowing the truth, setting targets, alerting |
| Blind to | Real devices, real networks, real cache states, the long tail | Pinpointing the exact cause |

**The Core Web Vitals thresholds in `performance.md` are defined against field data at the 75th percentile.** A green Lighthouse score proves nothing about them. `/pixel-check` and `/audit` produce lab measurements — a useful smoke test, never evidence the targets are met. You need both: lab to catch regressions before merge, field to know reality.

## Error tracking

Wire an error tracker (Sentry or equivalent) on day one, before the first production deploy — not after the first incident.

Capture from all of:
- React error boundaries — `error.tsx` at route level and local boundaries (`react-nextjs.md`). **An error boundary that renders a fallback but doesn't report is worse than no boundary: it hides the failure from you while still showing it to the user.**
- `window.onerror` and `unhandledrejection` for everything outside React's tree
- Failed API calls, with status and endpoint — but never the response body unmodified (see PII below)

Every report needs release version, user/session id (pseudonymous), route, and breadcrumbs. An error you can't reproduce or attribute to a release is noise.

### Source maps: upload, don't serve

`security.md` correctly says don't serve production source maps publicly — they hand attackers your original source. But minified stack traces are unreadable, so the resolution is not "skip source maps":

**Generate source maps at build time, upload them to the error tracker, and delete them from the deployed bundle.** Errors arrive fully symbolicated; the public gets nothing. This is the standard pattern and it's what makes both rules satisfiable at once.

### PII must never reach the tracker

Scrub before send: auth tokens, passwords, emails, payment details, and full API payloads that may contain any of them. Configure server-side scrubbing as a second layer — client scrubbing can be bypassed by a code path you forgot. This is a compliance obligation, not a preference.

## Real user monitoring (RUM)

Report actual Core Web Vitals from real sessions using the `web-vitals` library — it implements the same definitions Google measures, so your numbers are comparable to CrUX rather than an approximation.

Send LCP, INP, and CLS to your analytics/monitoring backend, with enough dimensions to act on them:
- Route/page template — an aggregate number hides that one critical route is terrible
- Device class and connection type — the p75 that matters is on mid-tier mobile, not your laptop
- Release version — so a regression is attributable to a deploy

**Always look at p75 and p95, never the mean.** An average hides the tail, and the tail is where users leave.

## Alerting

Alert on what indicates users are hurting, tied to the thresholds already in `performance.md`:

| Signal | Alert when |
|---|---|
| Error rate | Spikes above baseline, or any new error class after a deploy |
| CWV (p75, per key route) | Crosses out of "Good" and stays there |
| Failed API calls | Error ratio for an endpoint jumps |
| Core journey completion | Checkout/signup completion drops against its own baseline |

That last row is the highest-value alert most teams don't have: it catches breakage that throws no errors at all — a disabled button, a silently failing validation, a broken redirect.

Every alert must be actionable and routed to someone on call. Alerts nobody acts on get muted, and then the real one gets muted too.

## Frontend logging rules

The browser console is not a log store — anything you need after the fact must be sent somewhere. Log structured events (event name + typed fields), not prose strings.

Never log tokens, credentials, PII, or full request/response bodies. Assume anything logged is readable by whoever can open devtools, and retained by your backend indefinitely.

## Release gate

A feature is not releasable until: its error paths report to the tracker, its routes are covered by RUM, and someone would actually be alerted if it broke. `/frontend-axiom:audit` checks this, and `/frontend-axiom:init-project` sets it up at scaffold time.
