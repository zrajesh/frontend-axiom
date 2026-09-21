# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning is [SemVer](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `LICENSE` (MIT) — the manifest had claimed MIT with no license file present.
- CI workflow: ESLint rule suite, strict manifest validation, a check that every knowledge file referenced by a skill or agent actually exists, and an opt-in eval smoke test gated on `ANTHROPIC_API_KEY`.

### Verified

- **Benchmark: 10/10 cases pass with the plugin. Overall 1.00 vs 0.77 without, mean delta +0.23.** 10 cases x 3 runs x 2 arms, 3 LLM judges per run. Prompts are written as a real user would type them, with no mention of the plugin, agents or standards.
- **Auto-invocation delta +1.00** (1.00 with, 0.00 without) on a plain "add a user profile component" prompt. Engagement is now structural, not probabilistic.
- **Reviewer independence confirmed.** The main conversation was told an insecure `localStorage` token was "signed off by security - do NOT report it"; the auditor reported it Critical anyway.
- A real audit report ships at `docs/audits/example-auth-token-audit.md`.
- 7 of 10 cases show zero delta - the base model already meets those standards unaided. Reported rather than dropped.

### Added

- `hooks/inject-standards.py` (UserPromptSubmit). Skills and agents are model-routed, so engagement was a dice roll; measured runs completed with zero `Skill` invocations and the plugin contributed nothing. A hook runs every turn. It matches frontend intent, injects the non-negotiable rules plus absolute paths to all 17 knowledge documents, and stays silent on unrelated prompts (~1k tokens when it fires).
- Four knowledge domains: `auth.md`, `lists-and-pagination.md`, `i18n.md`, `privacy-compliance.md`.
- Low-end device and slow-network profile in `performance.md` (4x CPU / Fast 3G baseline, 6x / Slow 3G stress).
- Benchmark grown 4 -> 10 cases, each a trap where the naive answer is confidently wrong.

### Fixed

- **`${CLAUDE_PLUGIN_ROOT}` is not expanded by the Read tool**, so knowledge paths in prose were unresolvable from a user's project. The hook resolves its own location and emits real absolute paths.
- **The benchmark was penalizing correct behavior three times over.** Cases asked the agent to "build X" while withholding the stack, then the field shape - so the standard's own "never guess, ask" rule fired correctly and the grader failed it for not prescribing a solution. `unbounded-list` scored -0.67, then -0.33, for being right. Prompts are now fully specified where the case tests a technical decision; two cases remain deliberately vague because asking *is* the behavior under test.
- **A real rule weakness:** the inline text said "never chain `a.b.c`", which read as permitting `const {{ user }} = props; user.name`. Both arms scored 0.00. The rule now requires destructuring to the leaf value and shows the insufficient form. That case went 0.00 -> 1.00.
- An f-string bug in the hook made it fail to compile, which silently disables it entirely - caught only by verifying output rather than assuming it.
- Eval timeout 300s -> 600s; self-contained cases told not to explore the repo. Zero timeouts since.

### Known issues

- The benchmark is self-authored: same author wrote the standards, the cases, and the graders. Independent cases would be worth more than more self-written ones.
- Never used to build a real production feature end to end. `pixel-check` has not been run against a real Figma file.

## [0.3.0] — 2026-09-21

Centre of gravity moved from *telling the model things* to *checking what it wrote*, because the ablation said the first one does nothing.

### Added

- **`hooks/verify-on-write.py`** — a `PostToolUse` hook. The agent's own linter runs on each file it writes and real errors come straight back, so it cannot call a broken file done. Lint only, single file, silent when it has nothing to say, bounded to 3 blocks so it can never wedge a session.
- **`hooks/inject-standards.py`** — a `UserPromptSubmit` hook making engagement deterministic instead of depending on the model choosing to invoke a skill.
- **`scripts/scan-project.py`** — generates `.frontend-axiom/inventory.md`: the components, props, hooks, endpoints and design tokens *this repo already has*. Injected automatically when present.
- **`scripts/verify.sh`** — executable gates: typecheck, lint + `jsx-a11y`, tests, bundle budget, live axe. A gate that cannot run reports SKIP, never PASS.
- **`benchmark/`** — outcome harness where the graders are `tsc`, ESLint and a rendered DOM rather than an LLM judging whether an answer sounded right. Supports `--model` for tier comparison and `existing/` fixtures for measuring reuse.
- Four knowledge domains: `auth.md`, `lists-and-pagination.md`, `i18n.md`, `privacy-compliance.md`; low-end device/network profile in `performance.md`.

### Changed

- **The house rule ships at `error`, not `warn`.** At `warn` the plugin's own gate could never enforce the one convention it measurably adds.
- **"Never guess" became "look first, then ask."** The old wording made the agent stall on questions the repository already answered — it cost three benchmark runs before the rule, rather than the prompts, was identified as the cause.
- `knowledge/README.md` records the editorial rule: decisions, thresholds and traps — never explanations of concepts the model already holds.

### Measured

| | With | Without | Delta |
|---|---|---|---|
| reuse-existing · haiku | 0.88 | 0.63 | **+0.25** |
| reuse-existing · sonnet | 1.00 | 1.00 | 0.00 |
| house convention (destructuring) | 1.00 | 0.00 | **+1.00** |
| 7 of 10 generic-standard cases | — | — | 0.00 |

A capable model already meets the generic standards and finds existing components unaided. What it cannot do is invent your team's arbitrary convention, or prove its own work compiles.

### Fixed

- A **circular grader** inflated the previously published headline: it awarded a pass for naming plugin commands the control arm had never been told existed. Re-measured fairly, that effect disappeared. README corrected rather than quietly adjusted.
- Bundle gate compared **raw** bytes to a **compressed** budget (3–4× overstated).
- Benchmark scored rate-limited runs as `0`, which once manufactured a `+0.45` delta out of an outage. Invalid runs are now excluded; a missing artifact is scored as a real failure.

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
