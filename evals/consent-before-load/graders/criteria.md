---
type: llm
weight: 1
---
The trap: loading tags on page load and only *activating* them after consent. Under GDPR the network request itself transmits IP/user-agent to a third party, so the violation happens before any activation flag is read.

**Pass** requires:
1. States clearly that the third-party scripts must NOT be requested/loaded until consent is granted — gating the load, not just the firing/activation.
2. Implements conditional loading (e.g. `next/script` rendered only once consent is granted, or a consent-mode gate), rather than loading unconditionally and checking a flag afterward.

Bonus: reject must be as easy as accept; analytics and marketing are separate consent categories; consent in `localStorage` is spoofable and should be recorded server-side.

**Fail** if scripts load on mount with consent checked afterward, if consent is treated as fire-time only, or if it merely says "make sure you have a cookie banner".
