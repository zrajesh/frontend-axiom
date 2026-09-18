# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning is [SemVer](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `LICENSE` (MIT) — the manifest had claimed MIT with no license file present.
- CI workflow: ESLint rule suite, strict manifest validation, a check that every knowledge file referenced by a skill or agent actually exists, and an opt-in eval smoke test gated on `ANTHROPIC_API_KEY`.

### Known issues

- **The plugin does not reliably auto-engage.** With eval prompts phrased as an ordinary request, runs completed with zero `Skill` invocations — none of `knowledge/` consulted, output equivalent to the base model (ablation delta **−0.08**). Adding an explicit "use the frontend standards if available" hint to the prompts did make skills fire. So the plugin works when engaged; it does not reliably engage itself.
- **The eval suite is not yet a valid measurement.** Cases run in an empty sandbox while several prompts imply an existing codebase, so agents spend their budget searching for a project that isn't there. On the latest run, 4 of 6 `asks-before-guessing` runs hit the 300s timeout — **in both arms**. The headline delta (+0.08) therefore measures timeout noise more than plugin quality. Needs a seeded project fixture and a longer per-case timeout before any published number means anything.
- `skills/audit/SKILL.md` relies on `context: fork` + `agent: code-auditor` for reviewer isolation. That isolation is still unverified at runtime.

## [0.2.0] — 2026-09-18

### Added

- Three production domains the v0.1 standards were missing entirely: `knowledge/testing.md`, `knowledge/observability.md`, `knowledge/release-operations.md`.
- `evals/` — behavioral test suite (4 cases) checking whether the agents actually follow the standards.
- `.claude-plugin/marketplace.json`, making the plugin installable rather than loadable only via `--plugin-dir`.

### Fixed

- `new-feature` now actually delegates to the `frontend-architect` agent. v0.1's README claimed it did; it never referenced the agent at all.
- Rewrote `no-repeated-property-access` to track every hop of a member chain and resolve roots via scope analysis. v0.1 missed multi-hop chains (`data.user.email` — its own headline case), `this.props.x`, and properties split across sibling closures. Each is now a regression test; suite grew 11 → 20 cases.
- ESLint plugin exported a legacy-eslintrc config that could not load under ESLint 9 flat config. Now ships both `recommended` (flat) and `legacy-recommended`.
- Documented exceptions where a convention, applied blindly, produced worse code than it prevented.
- Replaced vague thresholds with numbers: per-route JS budgets, a `warn` → `error` lint promotion rule.
- Corrected FCP/TTFB being labelled Core Web Vitals (only LCP, INP, CLS are).

### Changed

- MCP servers moved to a conventional `.mcp.json`; manifest path fields and inline `mcpServers` objects were both silently registering zero servers.
- Dropped `skills`/`agents` manifest path fields in favour of convention discovery.

## [0.1.0] — 2026-09-18

Initial release: 5 skills, 2 agents, 10 knowledge documents, Figma + Chrome DevTools MCP servers, and a custom ESLint rule.
