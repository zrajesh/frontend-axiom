# Frontend Axiom

A Claude Code plugin that turns Claude into a senior frontend architect for React/Next.js work: SOLID principles, a hard destructuring-first code style, full data-state handling, pixel-perfect Figma-to-code validation, and independent code audits — backed by a knowledge base you can grow from your own team docs.

## What's in here

```
frontend-axiom/
├── .claude-plugin/plugin.json     # plugin manifest (metadata only)
├── .mcp.json                      # Figma + Chrome DevTools MCP servers
├── skills/
│   ├── init-project/              # /frontend-axiom:init-project — bootstrap or adopt onto a repo
│   ├── new-feature/                # /frontend-axiom:new-feature — interview, plan, then build
│   ├── audit/                      # /frontend-axiom:audit — fresh, independent review → doc
│   ├── pixel-check/                # /frontend-axiom:pixel-check — Figma vs live screenshot diff
│   └── learn-guide/                # /frontend-axiom:learn-guide — ingest a pasted guide
├── agents/
│   ├── frontend-architect.md      # main build agent
│   └── code-auditor.md            # independent reviewer used by /audit
├── knowledge/                      # the reference the agents actually read before acting
│   ├── principles.md               # SOLID + the destructuring rule (start here)
│   ├── react-nextjs.md
│   ├── css.md
│   ├── state-data.md
│   ├── testing.md
│   ├── security.md
│   ├── performance.md
│   ├── observability.md
│   ├── release-operations.md
│   ├── caching.md
│   ├── seo-ai-seo.md
│   ├── accessibility.md
│   └── storage.md
├── eslint-plugin-frontend-axiom/  # enforces the destructuring rule in CI, not just by convention
├── evals/                          # behavioral tests — do the agents actually follow the standards?
└── docs/audits/                    # /audit writes its reports here
```

Skills, agents, and MCP servers are all discovered by **convention** from their directories — the manifest deliberately carries no `skills`/`agents`/`mcpServers` path fields. See "Plugin wiring gotchas" below before changing that.

## Try it locally

```bash
claude --plugin-dir /path/to/frontend-axiom
```

Inside that session, edits to skills/agents/knowledge pick up after `/reload-plugins`.

Verify what actually loaded at any time:

```bash
claude plugin validate /path/to/frontend-axiom --strict
claude --plugin-dir /path/to/frontend-axiom plugin details frontend-axiom
```

The second command prints the real component inventory. Expected: **5 skills, 2 agents, 2 MCP servers**. If MCP servers show `(0)`, the wiring is broken — see below.

## Core workflow

1. **`/frontend-axiom:init-project`** — on a fresh repo, interviews you for framework / CSS approach / state & data layer / TS vs JS. On an existing repo, auto-detects the stack from `package.json` and configs, then asks you to confirm.
2. **`/frontend-axiom:new-feature`** — never assumes requirements. Interviews and plans inline (it needs to talk to you), then delegates the build to the `frontend-architect` agent with the fully-settled spec, and verifies what comes back.
3. **`/frontend-axiom:pixel-check`** — pulls the Figma frame via the Figma MCP, screenshots the live page via Chrome DevTools MCP, and iterates until they match.
4. **`/frontend-axiom:audit`** — runs the `code-auditor` agent fresh (no prior conversation bias) against SOLID, security, performance, accessibility, and scalability, and writes `docs/audits/<feature>-<date>.md`.
5. **`/frontend-axiom:learn-guide`** — paste a topic (or any best-practice writeup) and it's merged directly into the relevant `knowledge/*.md` file (or saved as a new one) that every other skill/agent will consult going forward.

## Plugin wiring gotchas

These were established by testing against the installed Claude Code CLI, not from docs — docs on some of these points were wrong:

- **MCP servers must live in `.mcp.json` (leading dot) at the plugin root.** A plain `mcp.json` is ignored, a manifest `"mcpServers": "./mcp.json"` field is ignored, and an **inline `mcpServers` object in `plugin.json` registers nothing** despite being documented as the recommended form. Only the dotted conventional file works.
- **`"agents": ["./agents/"]` fails validation.** The `agents` field only accepts explicit _file_ paths, not directories. Omitting the field entirely is better — the `agents/` directory is auto-discovered.
- Same for `skills` — omit it and let convention do the work, so adding a skill never means editing the manifest.

## Status

v0.2 — wiring verified by execution, standards reviewed by an independent audit.

Verified:
- `claude plugin validate --strict` passes.
- All skills, agents, and 2 MCP servers confirmed loading via `plugin details`.
- The ESLint rule passes a 20-case `RuleTester` suite (`npm test` in `eslint-plugin-frontend-axiom/`) and works end-to-end through the `eslint` CLI in a real ESLint 9 flat-config project.
- A behavioral eval suite (`evals/`) pins the four standards most likely to regress; the harness is confirmed working (`claude plugin eval .`).

v0.2 acted on an independent audit (`docs/audits/frontend-axiom-self-audit-2026-09-18.md`), which found the v0.1 standards stopped at "code that looks clean in a PR." Fixed since:
- Added the three missing production domains: `testing.md`, `observability.md`, `release-operations.md`.
- `new-feature` now actually delegates to `frontend-architect` — v0.1's README claimed it did, and it didn't.
- The destructuring rule gained two exceptions it needed to stop producing *worse* code: discriminated unions (destructuring breaks TypeScript narrowing) and referentially-unstable object/array defaults (which silently defeat memoization).
- Rewrote the ESLint rule to close the blind spots the audit found. It now tracks every hop of a chain (`data.user.email` — its own headline case, previously missed) and resolves roots via scope analysis so sibling closures share a tally. Every one of those is now a regression test.
- Added `evals/` — behavioral tests for the standards, because v0.1's false `frontend-architect` claim survived precisely by being asserted rather than tested.
- Replaced hand-wavy thresholds with numbers: per-route JS budgets, a `warn`→`error` promotion rule.

Known gaps, deliberately not yet filled: auth architecture, privacy/consent, i18n, real-time data patterns, list virtualization, design-system governance. See the audit's "Missing knowledge domains" table for the prioritized list.

Still unverified at runtime: `skills/audit/SKILL.md` uses `context: fork` + `agent: code-auditor` intending to give the auditor isolated, unbiased context — **that isolation has not been confirmed.** Check it on the first real audit.
