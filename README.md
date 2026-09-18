# Frontend Axiom

A Claude Code plugin that turns Claude into a senior frontend architect for React/Next.js work — built for apps that serve millions of users daily.

SOLID principles, a destructuring-first code style enforced in CI, mandatory handling of every data state, testing and observability and release standards, pixel-perfect Figma-to-code validation, and independent audits by an agent that didn't write the code.

---

## Quick start

```bash
# 1. Register the marketplace  (use a ./ or absolute path — a bare path is rejected)
claude plugin marketplace add /path/to/frontend-axiom

# 2. Install at user scope — available in every project from now on
claude plugin install frontend-axiom@frontend-axiom

# 3. Confirm it loaded
claude plugin details frontend-axiom
```

Then in any project:

```bash
cd ~/your-project
claude
```

```
/frontend-axiom:init-project
```

> **Installing from GitHub instead:** once this repo is pushed, others install it with
> `claude plugin marketplace add <your-username>/frontend-axiom` — same `plugin install` step after.

---

## Slash commands

Run these inside a Claude Code session. All are namespaced `frontend-axiom:`.

| Command | What it does |
|---|---|
| `/frontend-axiom:init-project` | **Run this first in any project.** On an existing repo, detects the stack from `package.json` and asks you to confirm. On a fresh one, interviews you (React vs Next.js, Tailwind vs CSS Modules vs Styled Components, RTK Query vs Zustand, TS vs JS). Then sets up the ESLint rule, security headers, a11y linting, test runner, error tracking, and caching defaults. |
| `/frontend-axiom:new-feature` | Interviews you for requirements — it will not guess an API shape — plans the breakdown, delegates the build to the `frontend-architect` agent with a complete spec, then verifies what comes back. |
| `/frontend-axiom:pixel-check` | Pulls the Figma frame via the Figma MCP, screenshots the live page via Chrome DevTools MCP, diffs them, and iterates until they match. |
| `/frontend-axiom:audit` | Runs the `code-auditor` agent with fresh context against every standard, ranks findings Critical/Warning/Suggestion, and writes `docs/audits/<feature>-<date>.md`. |
| `/frontend-axiom:learn-guide` | Paste a best-practices doc and it's distilled into the relevant `knowledge/*.md` file — every skill and agent consults it from then on. |

Useful built-ins alongside these:

| Command | Why you'd use it |
|---|---|
| `/mcp` | **Authenticate Figma** — required before `pixel-check` works (Chrome DevTools needs no auth) |
| `/reload-plugins` | Pick up plugin edits without restarting the session |
| `/context` | See which skills and agents are currently loaded |

---

## CLI reference

### Install & verify

```bash
claude plugin marketplace add /path/to/frontend-axiom   # register (./ or absolute path)
claude plugin install frontend-axiom@frontend-axiom     # install at user scope

claude plugin list                                      # expect: enabled, scope user
claude plugin details frontend-axiom                    # expect: 5 skills, 2 agents, 2 MCP servers
```

If `plugin details` reports `MCP servers (0)`, the wiring is broken — see [Plugin wiring gotchas](#plugin-wiring-gotchas).

### Update after changing the plugin

```bash
claude plugin marketplace update frontend-axiom
claude plugin update frontend-axiom
```

### Develop the plugin

Load it live instead of reinstalling on every edit:

```bash
claude --plugin-dir /path/to/frontend-axiom
```

Inside that session, `/reload-plugins` picks up changes to skills, agents, and knowledge docs.

### Validate & test

```bash
# Plugin manifest, skills, agents — warnings treated as errors
claude plugin validate /path/to/frontend-axiom --strict

# ESLint rule suite (20 cases)
cd /path/to/frontend-axiom/eslint-plugin-frontend-axiom && npm install && npm test

# Behavioral evals — do the agents actually follow the standards?
claude plugin eval /path/to/frontend-axiom --trust-plugin --max-cost-usd 5.00

# One eval case, cheap sanity check (~$0.05)
claude plugin eval /path/to/frontend-axiom --case token-storage-security --runs 1 --ablation none
```

Evals spawn real Claude child processes on your credential — see [`evals/README.md`](evals/README.md) for cost and for why the `--ablation` delta is the number that matters.

### Disable / uninstall

```bash
claude plugin disable frontend-axiom
claude plugin enable frontend-axiom
claude plugin uninstall frontend-axiom
claude plugin marketplace remove frontend-axiom
```

---

## The one hard rule

Never chain property access. Destructure once, with defaults, at every level:

```js
const { user = {}, isPremium = false } = dataObj;
const { name = "", email = "", skills = [] } = user;
```

Then use `name` / `email` / `skills` — never `user.name` again.

Two documented exceptions exist because applying this blindly produces *worse* code: **discriminated unions** (destructuring before narrowing breaks TypeScript) and **object/array defaults that reach a dependency array** (a fresh `[]` every render defeats memoization). See [`knowledge/principles.md`](knowledge/principles.md) §3.

`eslint-plugin-frontend-axiom` enforces the mechanical part in CI.

---

## What's in here

```
frontend-axiom/
├── .claude-plugin/
│   ├── plugin.json                # manifest (metadata only)
│   └── marketplace.json           # makes it installable
├── .mcp.json                      # Figma + Chrome DevTools MCP servers
├── skills/                        # the 5 slash commands above
├── agents/
│   ├── frontend-architect.md      # builds features
│   └── code-auditor.md            # independently reviews them
├── knowledge/                     # what the agents read before acting
│   ├── principles.md              # SOLID + the destructuring rule — start here
│   ├── react-nextjs.md            # Server vs Client Components, rendering strategy
│   ├── css.md
│   ├── state-data.md              # RTK Query patterns, normalization
│   ├── testing.md                 # risk-weighted coverage, MSW, E2E, CI gating
│   ├── security.md                # CSP, XSS, CSRF, headers, secrets
│   ├── performance.md             # Core Web Vitals, bundle budgets, INP
│   ├── observability.md           # error tracking, RUM, lab-vs-field, alerting
│   ├── release-operations.md      # CI gates, feature flags, canary, rollback
│   ├── caching.md                 # HTTP, CDN/edge, service worker, API cache
│   ├── seo-ai-seo.md              # traditional SEO + AI answer engines
│   ├── accessibility.md
│   └── storage.md                 # cookies vs local/session vs IndexedDB
├── eslint-plugin-frontend-axiom/  # the destructuring rule, enforced
├── evals/                         # behavioral tests for the agents
└── docs/audits/                   # /audit writes reports here
```

Skills, agents, and MCP servers are discovered by **convention** from their directories — the manifest deliberately carries no `skills`/`agents`/`mcpServers` path fields.

---

## Plugin wiring gotchas

Established by testing against the installed CLI, not from docs — the docs were wrong on some of these:

- **MCP servers must live in `.mcp.json` (leading dot) at the plugin root.** A plain `mcp.json` is ignored, a manifest `"mcpServers": "./mcp.json"` field is ignored, and an **inline `mcpServers` object in `plugin.json` registers nothing** despite being documented as the recommended form.
- **`"agents": ["./agents/"]` fails validation.** That field accepts explicit *file* paths only. Omit it — `agents/` is auto-discovered. Same for `skills`.
- **`marketplace add` rejects a bare path** — use `./path` or an absolute one.
- **A marketplace with no top-level `description` fails `--strict`** validation.

---

## Status

**v0.2.0** — wiring verified by execution, standards reviewed by an independent audit.

Verified, not assumed:
- `claude plugin validate --strict` passes.
- All 5 skills, 2 agents, and 2 MCP servers confirmed loading via `plugin details` from an unrelated directory.
- The ESLint rule passes a 20-case `RuleTester` suite and works end-to-end through the `eslint` CLI in a real ESLint 9 flat-config project.
- The eval harness is confirmed working against a live case.

v0.2 acted on an independent audit ([`docs/audits/frontend-axiom-self-audit-2026-09-18.md`](docs/audits/frontend-axiom-self-audit-2026-09-18.md)), which found v0.1 stopped at "code that looks clean in a PR":
- Added the three missing production domains: `testing.md`, `observability.md`, `release-operations.md`.
- `new-feature` now actually delegates to `frontend-architect` — v0.1's README claimed it did, and it didn't.
- The destructuring rule gained the two exceptions above, which it needed to stop producing worse code.
- Rewrote the ESLint rule to close verified blind spots — it had been missing `data.user.email`, its own headline case.
- Added `evals/`, because that false `frontend-architect` claim survived precisely by being asserted rather than tested.
- Replaced hand-wavy thresholds with numbers: per-route JS budgets, a `warn`→`error` promotion rule.

**Known gaps, deliberately unfilled:** auth architecture, privacy/consent, i18n, real-time data patterns, list virtualization, design-system governance. The audit's "Missing knowledge domains" table has the prioritized list.

**Still unverified:** `skills/audit/SKILL.md` uses `context: fork` + `agent: code-auditor` intending to give the auditor isolated context — that isolation hasn't been confirmed at runtime. Check it on the first real audit.
