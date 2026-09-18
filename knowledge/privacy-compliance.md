# Privacy & Consent Standards

At millions of users daily you are almost certainly in scope for GDPR (EU/UK) or CCPA/CPRA (California) whether or not you targeted those markets. These are engineering requirements with statutory penalties, not legal-team paperwork — most of the obligations land in frontend code.

This file is engineering guidance, not legal advice. Jurisdictional specifics belong with counsel.

## Consent gates loading, not just firing

The most common — and most expensive — mistake is loading a third-party tag on page load and only *activating* it after consent. Under GDPR the violation is the network request itself: it transmits IP and user agent to a third party before consent exists.

**No non-essential third-party script may be requested until consent is granted.**

| Category | Consent | Examples |
|---|---|---|
| Strictly necessary | Not required | Session/auth cookies, CSRF token, load balancing, language preference |
| Functional | Required | Embedded video, live chat, personalization |
| Analytics | Required (EU) | Product analytics, heatmaps, session replay |
| Marketing | Required | Ad pixels, retargeting, conversion tags |

Gate through `next/script` with a consent-conditional render, or a consent-mode API — never a "load it and hope" flag.

## The banner

- **Reject must be as easy as accept.** Equal prominence, same number of clicks. A prominent "Accept all" beside a buried "Manage preferences" is a documented enforcement target.
- No pre-ticked boxes. No implied consent from scrolling or continued browsing.
- Withdrawal must be as easy as granting — a persistent, reachable control, not a one-time modal.
- Record consent: which categories, which policy version, when. You must be able to demonstrate it.
- Don't block the page behind a banner for crawlers — it harms indexing and isn't required (`seo-ai-seo.md`).

## Minimize what you collect

- Collect a field only if there's a stated purpose for it. "It might be useful later" is not a lawful basis.
- **Never put PII in URLs.** Query strings land in server logs, `Referer` headers sent to third parties, analytics, and browser history. Email addresses and tokens in URLs are a routine leak path.
- Never put PII in analytics event properties or error breadcrumbs (`observability.md`). Scrub client-side *and* server-side.
- Session replay is the highest-risk tool in common use: mask all input fields by default and allowlist what's recorded, rather than blocklisting what isn't. Default-on recording will capture a password or card number eventually.

## Data subject rights

Users can request access, deletion, correction, and export. The frontend's part:

- Reachable self-service UI for export and deletion — not an email address.
- Deletion must clear **client-side** stores too: `localStorage`, `sessionStorage`, IndexedDB, caches, and any service-worker cache (`storage.md`, `caching.md`). A "deleted" account whose data is still in IndexedDB on the device is not deleted.
- Cover the multi-tab and offline cases (`auth.md`) — purge on the tab that's still open.

## Children and sensitive data

If the product may be used by under-13s (COPPA) or handles health, biometric, financial, or similar special-category data, requirements are stricter and this file is not sufficient. Escalate to counsel before building.

## Review checklist

`/frontend-axiom:audit` treats these as **Critical**:

- [ ] No non-essential third-party request before consent — verify in the network tab, not in code
- [ ] Reject is as easy and prominent as accept; withdrawal is persistent
- [ ] No pre-ticked consent
- [ ] No PII in URLs, analytics properties, or error breadcrumbs
- [ ] Session replay masks inputs by default
- [ ] Deletion clears client-side storage, not just the server
- [ ] Consent record captures categories, policy version, timestamp
