#!/usr/bin/env python3
"""
UserPromptSubmit hook — makes Frontend Axiom engage deterministically.

Why this exists: relying on the model to spontaneously invoke a skill or agent
is probabilistic. Measured runs completed with zero Skill invocations, in which
case none of the standards were consulted and the output was whatever the base
model would have produced. A hook is not a suggestion — it runs every turn.

Design constraints:
  - Injected on every matching prompt, so it must stay SMALL. The inline rules
    are only the ones most often violated; everything else is a pointer.
  - Gated on relevance, so non-frontend prompts pay nothing.
  - Emits ABSOLUTE paths. ${CLAUDE_PLUGIN_ROOT} is expanded in hooks.json
    commands but NOT by the Read tool, so resolving it here is what makes the
    knowledge base reliably reachable from any project directory.
"""

import json
import os
import re
import sys

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE = os.path.join(PLUGIN_ROOT, "knowledge")

# Deliberately broad: a missed injection costs correctness, a spurious one
# costs a few hundred tokens. Bias toward firing.
TRIGGER = re.compile(
    r"""(?ix)
    \b(
      front[- ]?end | ui | ux | web\s?app
    | react | next\.?js | vue | svelte | remix | vite
    | component | jsx | tsx | hook | props | state | render(ing)?
    | redux | rtk | zustand | context | store | selector
    | css | tailwind | styled|scss | style | layout | responsive | design
    | api | fetch | endpoint | request | response | query | mutation | cache
    | page | route | router | navigation | link | form | input | button | modal
    | list | table | grid | pagination | scroll | virtual
    | auth | login | logout | session | token | cookie | jwt | oauth
    | accessib | a11y | aria | keyboard | screen\s?reader | contrast
    | performance | bundle | lighthouse | web\s?vitals | lcp | inp | cls | slow
    | seo | meta\s?tag | sitemap | ssr | csr | ssg | isr | hydrat
    | test | vitest | jest | playwright | storybook
    | i18n | locale | translat | rtl
    | consent | gdpr | analytics | tracking | pixel
    | typescript | javascript
    )\b
    """,
)

CONTEXT = f"""\
<frontend-axiom-standards>
Frontend Axiom is ACTIVE. Apply these without being asked. They override generic habits.

NON-NEGOTIABLE:
1. NEVER GUESS. If the API shape, field names, requirements, or stack are unclear, ASK
   before writing code. Inventing a response shape is a defect, not a head start.
2. EVERY data-fetching surface handles five states: loading / data / EMPTY (visually
   distinct, not a blank list) / error (with retry) / refetching (don't blank stale UI).
3. AUTH TOKENS live in httpOnly+Secure+SameSite cookies. NEVER localStorage or
   sessionStorage — one XSS there is account takeover. Logout revokes server-side AND
   purges the client cache.
4. DESTRUCTURE TO THE LEAF VALUE, then use the bare variable. Pulling out the object and
   still reading through it is NOT enough:
       const {{ user }} = props; user.name        <- still wrong
       const {{ user = {{}} }} = props;
       const {{ name = "", email = "" }} = user;  <- correct; now use `name`, `email`
   Applies at every depth. Object/array defaults that reach a dependency array must be
   module-level constants, not fresh literals. EXCEPTION: discriminated unions — narrow on
   the whole value first, destructure inside the branch (destructuring first breaks
   TypeScript narrowing).
5. TESTS ship with the code. Untested auth, payment, or mutation logic is a Critical defect.
6. SEMANTIC HTML, keyboard operability, real labels, and contrast are defaults, not a pass.
7. NO unbounded collection fetch. Past ~1,000 rows, virtualize. Append-heavy data uses
   cursor, not offset pagination.
8. Third-party scripts that touch user data do NOT load before consent — the network
   request itself is the violation.

FULL STANDARDS — read the ones this task touches (absolute paths, read before deciding):
  {KNOWLEDGE}/principles.md            ALWAYS — SOLID, the 5-state rule, conventions
  {KNOWLEDGE}/react-nextjs.md          components, Server vs Client, SSR/SSG/ISR/CSR
  {KNOWLEDGE}/state-data.md            RTK Query, caching, normalization
  {KNOWLEDGE}/auth.md                  sessions, refresh rotation, logout, route guards
  {KNOWLEDGE}/security.md              CSP, XSS, CSRF, headers, input validation
  {KNOWLEDGE}/testing.md               what to test, coverage policy, CI gating
  {KNOWLEDGE}/performance.md           Core Web Vitals, budgets, low-end device profile
  {KNOWLEDGE}/accessibility.md         semantics, keyboard, contrast
  {KNOWLEDGE}/lists-and-pagination.md  virtualization, cursor vs offset
  {KNOWLEDGE}/observability.md         error tracking, RUM, alerting
  {KNOWLEDGE}/release-operations.md    CI gates, feature flags, rollback
  {KNOWLEDGE}/caching.md               HTTP/CDN/service worker/API cache
  {KNOWLEDGE}/css.md                   styling approach, CLS
  {KNOWLEDGE}/storage.md               cookies vs local/session vs IndexedDB
  {KNOWLEDGE}/seo-ai-seo.md            metadata, structured data, crawlability
  {KNOWLEDGE}/i18n.md                  ICU, Intl, RTL, hreflang
  {KNOWLEDGE}/privacy-compliance.md    consent gating, PII, deletion

DEEPER WORKFLOWS: /frontend-axiom:init-project (stack setup), :new-feature (interview →
build), :audit (independent review), :pixel-check (Figma diff), :learn-guide (ingest docs).
</frontend-axiom-standards>"""


def main() -> int:
    raw = sys.stdin.read()
    try:
        prompt = (json.loads(raw) or {}).get("prompt", "")
    except (json.JSONDecodeError, AttributeError):
        prompt = raw  # tolerate a non-JSON stdin rather than failing the turn

    if not prompt or not TRIGGER.search(prompt):
        return 0  # not frontend work — inject nothing, cost nothing

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": CONTEXT,
            }
        },
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # A hook must never break the user's turn.
        sys.exit(0)
