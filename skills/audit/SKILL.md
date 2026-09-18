---
name: audit
description: Independent, fresh-eyes review of implemented code against Frontend Axiom's SOLID, security, performance, accessibility, and scalability standards. Produces a markdown report in docs/audits/. Use after a feature is implemented, before merging, or whenever the user runs /frontend-axiom:audit.
context: fork
agent: code-auditor
allowed-tools: Read, Glob, Grep, Bash, Write
---

# Audit

> Implementation note: this skill is declared with `context: fork` + `agent: code-auditor` so the review runs as an independent subagent rather than continuing inline in whatever conversation built the feature — the point is a reviewer with no investment in the code being "done." If on first real use this doesn't actually isolate context the way intended, fall back to invoking the `code-auditor` agent explicitly via the Agent tool instead, and fix this file.

## Target

`$ARGUMENTS` names what to review: a feature name, a file/folder path, or a diff range (e.g. `git diff main...HEAD`). If not given, default to the diff against the repository's default branch (`git diff origin/main...HEAD`, or `master` if that's the default) — it needs no external bookkeeping and is almost always the change set under review.

Whatever scope you end up with, **state it explicitly in the report header**, including the exact diff command or paths used, so a reader can reproduce the review.

## Process

1. Do not assume intent from conversation history — evaluate the code as it exists, on its own merits.
2. Walk every file in scope against each of: `${CLAUDE_PLUGIN_ROOT}/knowledge/principles.md` (SOLID, destructuring rule, 5-state handling), `${CLAUDE_PLUGIN_ROOT}/knowledge/testing.md`, `${CLAUDE_PLUGIN_ROOT}/knowledge/security.md`, `${CLAUDE_PLUGIN_ROOT}/knowledge/performance.md`, `${CLAUDE_PLUGIN_ROOT}/knowledge/observability.md`, `${CLAUDE_PLUGIN_ROOT}/knowledge/release-operations.md`, `${CLAUDE_PLUGIN_ROOT}/knowledge/caching.md`, `${CLAUDE_PLUGIN_ROOT}/knowledge/accessibility.md`, `${CLAUDE_PLUGIN_ROOT}/knowledge/react-nextjs.md`, `${CLAUDE_PLUGIN_ROOT}/knowledge/state-data.md`, plus any other relevant file in `knowledge/`.
   - A green lint run is not sufficient evidence the destructuring convention holds — the rule can't see single deep reads or referentially-unstable defaults, and it over-fires on discriminated unions. Read for those yourself; see `${CLAUDE_PLUGIN_ROOT}/knowledge/principles.md` §3.
3. For each finding, classify severity: **Critical** (security hole, broken functionality, data loss risk), **Warning** (violates a hard rule but not exploitable/broken — e.g. dot-chained access, missing empty-state), **Suggestion** (style/optimization, non-blocking).
4. Report only — do not fix issues in this pass. Fixing is a separate, explicit follow-up step the user asks for after reading the report.

## Output

Write `docs/audits/<feature-slug>-<YYYY-MM-DD>.md` with:

```markdown
# Audit: <feature/scope>
Date: <date> · Reviewed: <files/paths in scope>

## Verdict
<one paragraph: ready to merge / needs work / blocked, and why>

## Critical
- <file:line> — <issue> — <why it matters> — <suggested fix>

## Warnings
- <file:line> — <issue> — <suggested fix>

## Suggestions
- <file:line> — <issue>

## Checklist
| Area | Status |
|---|---|
| SOLID | pass/fail |
| Destructuring convention | pass/fail |
| 5-state data handling | pass/fail |
| Tests (coverage of new behavior, CI-gated) | pass/fail |
| Security (CSP/XSS/CSRF/headers/input validation) | pass/fail |
| Performance (CWV, bundle, images/fonts) | pass/fail |
| Caching (HTTP/CDN/client cache correctness) | pass/fail |
| State & data layer (normalization, cache invalidation) | pass/fail |
| Observability (error tracking, RUM on new paths) | pass/fail |
| Release safety (flag-gated / rollback path, if blast radius warrants) | pass/fail |
| Accessibility | pass/fail |
| SEO (if user-facing/indexable) | pass/fail |
```

Every row must be covered by the process step above — if you add a row here, add the corresponding `knowledge/` file to the walk in step 2, and vice versa. A checklist row with no backing standard is theater.

Keep it concise and actionable — a reviewer document someone will actually read, not a wall of text.
