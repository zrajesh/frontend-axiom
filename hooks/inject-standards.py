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
import subprocess
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
1. LOOK FIRST, THEN ASK. Never invent an API shape, field name, or endpoint — but do not
   ask for something the repository already answers. Order: check the inventory below,
   grep the codebase, read the types. ASK only for what genuinely is not discoverable
   (a product decision, an endpoint that does not exist yet, an ambiguous requirement).
   Stalling on a question the code already answers wastes the user's turn as surely as
   guessing wrong does.
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
build), :audit (independent review), :pixel-check (Figma diff), :decide (record a team decision).
</frontend-axiom-standards>"""


def team_decisions(cwd: str, prompt: str) -> str:
    """Decisions that exist nowhere in the code — the one measured +1.00.

    Six ablations found ~zero delta on everything a capable model can derive.
    The exception was a rule present only in a document; when the same kind of
    rule was demonstrated by example files, the model inferred it by reading
    and the delta vanished. So this surfaces only what the repository cannot
    tell it, matched by keyword and path so a team with 200 decisions does not
    pay for 200 every turn.
    """
    script = os.path.join(PLUGIN_ROOT, "scripts", "decisions.py")
    store = os.path.join(cwd or ".", ".frontend-axiom", "decisions.json")
    if not (os.path.isfile(script) and os.path.isfile(store)):
        return ""
    try:
        out = subprocess.run(
            [sys.executable, script, "--root", cwd or ".", "match", prompt],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        return ""
    return f"\n\n{out}" if out else ""


def project_inventory(cwd: str) -> str:
    """Point at this project's generated inventory, if one exists.

    This is the part a model cannot know from training: which components,
    hooks and endpoints this repository already has. Benchmarking showed the
    model already meets the generic standards above, so the inventory is where
    the real leverage is — it stops the agent writing a ninth Button.
    """
    base = os.path.join(cwd or ".", ".frontend-axiom")
    conv = os.path.join(base, "conventions.md")
    conv_block = ""
    if os.path.isfile(conv):
        try:
            rows = [l for l in open(conv, encoding="utf-8").read().splitlines()
                    if l.startswith("| ") and "**" in l]
        except OSError:
            rows = []
        if rows:
            conv_block = (
                "\n\nTHIS REPO'S OWN CONVENTIONS — inferred from its code, follow them:\n"
                + "\n".join("  " + r for r in rows[:10])
                + f"\n  (full detail, including dissenting files: {conv})"
                + "\nThese are arbitrary team choices, not derivable from the task. Where a "
                  "file disagrees it is the exception, not the licence."
            )

    path = os.path.join(base, "inventory.md")
    if not os.path.isfile(path):
        return conv_block
    try:
        head = open(path, encoding="utf-8").read(400)
    except OSError:
        return conv_block
    counts = " ".join(re.findall(r"##\s+(Components|Hooks|API endpoints)\s+\(\d+\)", head)) or ""
    return f"""

THIS PROJECT'S INVENTORY — READ IT BEFORE CREATING ANYTHING:
  {path}
It lists the components, hooks, API endpoints and design tokens that already
exist here. {counts}
- Reuse or extend what is listed. Do NOT write a second component that does an
  existing one's job.
- Use the endpoint names and field names exactly as listed. If what you need
  is not there, ASK — do not invent it.
- Use the listed design tokens rather than hardcoding values.
If it looks stale, regenerate: python3 {PLUGIN_ROOT}/scripts/scan-project.py""" + conv_block


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) or {}
    except (json.JSONDecodeError, AttributeError):
        payload = {}
    prompt = payload.get("prompt", raw if isinstance(raw, str) else "")

    if not prompt or not TRIGGER.search(prompt):
        return 0  # not frontend work — inject nothing, cost nothing

    cwd = payload.get("cwd") or os.getcwd()
    context = CONTEXT + project_inventory(cwd) + team_decisions(cwd, prompt)

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": context,
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
