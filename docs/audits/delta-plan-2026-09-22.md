# Delta Plan — where the large delta actually lives, and how to prove it

Date: 2026-09-22 · Scope: strategy for producing a large, defensible delta on real projects
Author: principal-engineer research pass. Every claim cited to a file in this repo; measurements re-derived from `benchmark/results/`, not taken from the briefing.

---

## 0. The one-paragraph answer

The under-specification hypothesis is **close, and falsified by this repo's own best task.** The variable is not how much the prompt omits — it is **how expensive it is for the agent to recover what the prompt omits.** Every zero in the dataset is a fact the agent could buy cheaply; the one +1.00 is a fact it could not buy at any price. That reframe moves the product's target from *knowledge* to *acquisition cost*, and it immediately explains why no experiment so far has produced a large delta on a capable model: **every mechanism with a plausibly large delta is one the current harness structurally cannot see.** Neither arm has `Bash` (`benchmark/run.sh:107,111`), so nothing can be executed. No task ships a test suite, so nothing can be regressed. No task exceeds 44 components, so search never gets expensive. No task runs past one turn, so nothing can drift. The zeros are a property of the *task shape*, not of the model. Fix the harness first — it is four hours of work and it is the precondition for every number that follows.

---

## 1. Stress-testing the hypothesis

### 1.1 The three points fit. The fourth one breaks it.

| Case | Prompt specifies the answer? | Under-spec theory predicts | Measured |
|---|---|---|---|
| `orders-list` | yes — props contract telegraphs `isLoading`/`isError`/`isFetching` (`benchmark/tasks/orders-list/task.md:8-12`) | 0 | 0.00 ✓ |
| `five-data-states` (states omitted) | no | positive | +0.33 ✓ |
| destructuring convention | no | positive | +1.00 ✓ |
| **`reuse-at-scale`** | **no — the prompt names nothing** | **positive** | **0.00 ✗** |

`reuse-at-scale` is the most under-specified task in the suite. `benchmark/tasks/reuse-at-scale/task.md` says only *"ask the user to confirm cancelling the order."* The answer is two files out of 44, deliberately named so they cannot be guessed (`Overlay`, not `Modal`; `ActionButton`, not `Button`), ringed with four decoys, with a grader that fails on any decoy (`benchmark/tasks/reuse-at-scale/assert/CancelOrderDialog.spec.tsx:42-45`). Under-specification theory predicts the largest delta in the suite. It measured **1.00 vs 1.00**.

### 1.2 What actually separates +1.00 from 0.00

Both `destructuring-rule` and `reuse-at-scale` are under-specified. The difference is where the answer was sitting:

- `reuse-at-scale`: the answer was in 44 files the agent could read in under a minute. **Acquisition cost: low.** Control paid it, and won.
- destructuring: the answer was nowhere in the task, the repo, or the training data. **Acquisition cost: infinite.** Control could not pay it, at any budget.

So the model is not `delta = f(specification gap)`. It is:

> **Delta = P(control fails) × P(treatment succeeds | control fails)**
>
> where **P(control fails) ≈ f(acquisition cost of the decisive fact)**.

This also explains the one clean positive on artifact-graded work that the briefing under-weights: `reuse-existing` on haiku, **+0.25** (`benchmark/results/20260921T215938/summary.tsv`). Same fixture, same prompt, sonnet gets 1.00/1.00. Nothing about the *knowledge* changed between tiers. What changed is haiku's cost of search — it is worse at exploration, so the pre-computed index was worth more to it. That is acquisition cost, cleanly isolated, and it is the single most informative number in the dataset.

### 1.3 The corollary that should reorganise the product

Acquisition cost has three tiers with completely different trajectories:

| Tier | Examples | P(control fails) | Trajectory as models improve |
|---|---|---|---|
| **∞ — unknowable** | house conventions, product intent, why we rejected that library | 1.0 | **Flat forever.** But it is per-team, so it must be *extracted*, never *shipped*. |
| **High — unreachable in practice** | the repo at 800 components; the build output; the test suite; the rendered DOM; turn 14 after compaction | 0.4–0.9, **rising with project size** | Falls slowly. Project size rises faster than model capability. **Never tested here.** |
| **Low — un-elected** | "handle the empty state", "tokens go in cookies", "virtualize past 1k rows" | 0.0–0.3, **falling every generation** | **Depreciating asset.** All seven zeros live here. So does ~90% of `knowledge/`. |

The briefing's "completeness engine" idea sits squarely in the **low** tier. It is the right description of what a senior does and the wrong bet on where delta lives, because exhaustiveness is precisely the axis post-training optimises hardest. And the evidence for it is thin: +0.33 at n=3 means *one run in three flipped*, against a harness where the same arm on the same task moved 1.000 → 0.667 between `benchmark/results/20260920T041541/summary.tsv` and `20260920T132921/summary.tsv`. That is not a signal yet.

**Actionable form of the reframe:** `knowledge/` is organised by *topic* (auth, css, seo). It should be organised by *acquisition cost* — "could the agent have got this itself, and at what price?" Everything in the low tier is rent paid on every turn for nothing (`hooks/inject-standards.py:52-105`, ~1,040 tokens).

### 1.4 The measurement problem that invalidates every existing null result

Before ranking mechanisms, three defects make the current numbers uninterpretable at the mechanism level:

1. **Control-arm contamination.** `benchmark/run.sh:98-101` runs `scan-project.py` *before* the arm branch at `:105`, so `.frontend-axiom/inventory.md` is written into the **control** sandbox too. The treatment's most valuable payload is physically present in the control's working directory on every task that ships `existing/` — i.e. on both reuse tasks, the two that matter most.
2. **Process is invisible.** Both arms run plain `-p` (`:108,112`), so the log is the final assistant message only — 359 bytes for `benchmark/results/20260922T021545/reuse-at-scale-control-1.log`. You cannot tell whether the treatment ever *read* a knowledge doc, whether `verify-on-write.py` ever fired, or whether the control found the inventory. Every null result today is ambiguous between "the standards didn't help" and "the standards were never read."
3. **Only aggregates survive.** `benchmark/run.sh:143-149` writes one row per arm; `benchmark/report.js:56-72` reports a mean of fractions. Per-run scores are discarded, so variance, floor, and worst-case are uncomputable — see §2.1, which argues that is where the shippable claim actually is.

---

## 2. Where large delta lives — ranked

Ranked by expected effect size × probability the mechanism is real × cheapness of proof.

### 2.1 Reporting the floor instead of the mean ⭐ *(the thing not on the list)*

**Expected effect: large, and available today at zero mechanism cost.**

`big-list` treatment scored **1.000** in one run-set and **0.667** in the next. The product has been treating that as noise to be averaged away. It is the result. A gate does not raise the median run — it **removes the left tail**, which is exactly what CI does and exactly why CI is universally adopted despite making nobody's median commit better.

Two statistics, both computable from runs you are already paying for:

- **Floor rate**: `P(run scores < 1.0)`, per arm. On `big-list` the existing data already implies treatment 1/3 vs control 3/3 imperfect — a far larger and more decision-relevant gap than the reported "+0.05."
- **Overclaim rate**: fraction of runs where the final assistant message asserts success and the graders disagree. `reuse-at-scale-control-1.log` is a confident 359-byte claim that everything was done correctly; it happened to be true, and nothing in the harness would have noticed if it were not. This number is free once §3.0 lands, nobody in this space measures it, and it is the number a user viscerally cares about: *how often does it tell me it's done when it isn't?*

Why this outranks everything: it changes the reportable claim from "+0.05, not significant" to a binary outcome, and binary outcomes need far fewer runs to read. It requires no new mechanism, no new task, no new model spend.

### 2.2 Execution-derived facts, made mandatory ⭐⭐

**Expected effect: large on both tiers. Non-depreciating. Currently unmeasurable.**

This is the mechanism with the highest ceiling and it has never been tested, because **neither arm has `Bash`** (`benchmark/run.sh:107,111`). The agent physically cannot run a build, a test suite, or a typecheck in any experiment this repo has conducted.

The reason this does not depreciate is that it is not a knowledge gap, it is an **economics** gap. A model that knows everything about bundle size still cannot know that `src/lib/charts.ts` pulls in 380KB — and, critically, **will not voluntarily spend twelve tool calls finding out.** Post-training makes models know more; it does not make them pay costs they can skip without being caught.

Note what the plugin currently does with this mechanism: `hooks/verify-on-write.py:98` runs **ESLint only**, on a single file. No `tsc`. No tests. The plugin's own README concedes the scope (`README.md:72`) and defers everything real to `scripts/verify.sh` — which is reachable from exactly two places, both requiring the user to type a slash command (`skills/audit/SKILL.md:24`, `agents/code-auditor.md:22`). **The single most mechanically-fixable failure class in frontend work — a type error — is not caught on the build path at all.**

### 2.3 Retrieval at scale ⭐⭐

**Expected effect: large and *growing*, with a dose-response curve you can plot.**

`reuse-at-scale` is 44 components (`benchmark/tasks/reuse-at-scale/generate.py:60-72`). Real projects are 400–2,000. Under the acquisition-cost model the prediction is specific and falsifiable: **control's pass rate falls with N while treatment's stays flat**, because reading a pre-computed index is O(1) and exhaustive grep is not. The haiku +0.25 at N=44 is the same curve sampled at a higher effective search cost.

A dose-response curve at N ∈ {44, 200, 800} is dramatically more convincing than any single delta, and the fixture is already procedural so it costs a script edit. If control holds 1.00 at N=800, the retrieval thesis is dead for capable models and the plan should say so and move the budget to §2.2.

### 2.4 Arbitrary house conventions — but extracted, not shipped ⭐

**Expected effect: +1.00 where it applies. Proven. But the product ships n=1 of it.**

The destructuring rule is the only asset with a non-circular +1.00, and the reason is structural: it is unguessable **and** executable — `eslint-plugin-frontend-axiom/index.js:10` now ships it at `"error"`, so it survives the model forgetting it. That combination, not the rule's content, is the product.

Two things blunt it today:

- It is **one team's rule, shipped to everyone.** Every team has three or four such rules and they are all different. The generalisable asset is an extractor, not this rule.
- **The outcome benchmark has never graded it.** No `benchmark/tasks/*/seed/eslint.config.js` loads `eslint-plugin-frontend-axiom`, so the harness's lint gate (`benchmark/run.sh:60-63`) cannot see the one convention with a proven delta. The plugin *is* in `benchmark/.template/node_modules/`, so wiring it up is a three-line config change.

### 2.5 Long-horizon drift

**Expected effect: medium-to-large, expensive to prove, partially already mitigated.**

Plausible, and untested — `benchmark/run.sh` is strictly single-turn. Worth noting that the plugin already has an accidental defence: `hooks/inject-standards.py:144-149` re-injects on *every* matching prompt with no session state. The prior audit (`docs/audits/product-audit-2026-09-21.md` §4.7) wants that deduplicated to save tokens. **These two positions are in direct conflict and the drift experiment is what resolves them.** If drift is real, per-turn re-injection is the feature, not the bug, and the correct optimisation is not "inject once" but "inject full after compaction" — `PreCompact` is a real hook event in the installed CLI (verified in `claude` 2.1.278), so this is implementable.

### 2.6 Negative work — the thing agents structurally never do

**Expected effect: medium. Untested. Mechanically gradeable. Nothing in the repo touches it.**

Agents add; they do not remove. Asked to replace a component, they write the new one and leave the old path live. Asked to migrate a prop, they add the new one and keep the old as an alias "for compatibility." The result is a codebase that grows a duplicate every time an agent touches it — the single most-cited complaint about agent-written code, and the most-cited senior-vs-agent gap.

It grades trivially: assert the old file is gone, assert zero remaining references, assert the orphaned test was deleted. It is not a knowledge gap — the model knows to clean up — so it belongs to the "un-elected" tier and would normally depreciate. But unlike the other un-elected items, **it is verifiable**, which means a gate converts it into a guarantee rather than a suggestion.

### 2.7 Omission / completeness

**Expected effect: small and shrinking. Do not build the product on this.**

This is the briefing's leading hypothesis and I rank it seventh. +0.33 at n=3, one control flip, on a harness with demonstrated ±0.33 run-to-run variance on an adjacent task. It is not yet distinguishable from noise, and its trajectory is the wrong direction. Raise n to 10 before quoting it again; if it survives, it is worth ~120 tokens of inline rule and nothing more.

### 2.8 Pushback / "don't build it"

**Expected effect: small in measurement, real in practice, hard to grade.** Genuine senior behaviour, but any grader for it is an LLM judging tone, which is the failure mode `benchmark/` exists to escape. Park it.

---

## 3. Experiments, in priority order

### 3.0 — PREREQUISITE: instrument the harness (~4h, $0)

**Nothing below is interpretable until this lands.** Five changes to `benchmark/run.sh`:

1. **Move the scan inside the treatment branch.** `run.sh:98-101` currently writes `.frontend-axiom/inventory.md` into both arms. Move the `scan-project.py` call to after the `if [[ "$ARM" == "treatment" ]]` test at `:105`.
2. **Log the process.** Add `--output-format stream-json --verbose` to both invocations (`:108,112`). Write a `tools.tsv` per run: tool name, target path, order. This is what makes "did the treatment actually read the standards?" answerable.
3. **Add `Bash` to both arms' `--allowedTools`.** Without it §2.2 and §2.6 cannot be measured at all. Add `--permission-mode acceptEdits` so Bash does not deadlock on a prompt in `-p` mode.
4. **Emit per-run rows** to `summary.tsv` (`task, arm, run, passed, total, valid`), not just per-arm aggregates (`:143-149`). Then extend `benchmark/report.js` to print, per arm: mean, **floor rate** `P(score < 1.0)`, and **overclaim rate** (final message asserts success ∧ score < 1.0).
5. **Add a third arm, `treatment-noverify`** — `--plugin-dir` with `FRONTEND_AXIOM_NO_HOOKS=1` honoured as an early exit in `hooks/verify-on-write.py:119`. This is the highest-information change in the whole plan: it separates *the prose* from *the gate*. Every experiment below should run three arms.

### 3.1 — `silent-break`: does a gate transfer capability? (⭐ run first)

**The cleanest possible test of §2.2, and the cheapest.**

*Seed*: `existing/src/Money.tsx` formatting currency, used at four call sites; `existing/src/__tests__/money.spec.tsx` with six **pre-existing, passing** tests, two of which assert exact output (`$12,000.00`, `$9,999.99`). `package.json` has a `test` script (the template already does — `benchmark/template-package.json:5`).

*Task*: "`Money` should render large values compactly — `$12.0k` above 10,000. Add it." (The obvious implementation breaks the two exact-output tests.)

*Graders* (binary per assertion, all in the existing harness):
- `tsc --noEmit` clean.
- **The six pre-existing tests still pass, unmodified.** Guard this: assert `git diff --stat` touches no file under `__tests__/`, or hash the spec file before and after. An agent that "fixes" the failure by editing the test must score zero.
- A new assertion file verifies the compact behaviour, so doing nothing also scores zero.

*Confirms*: treatment (with the Stop-hook gate from §4.1) ≥ 0.7 pass rate vs control ≤ 0.3 at n=8 → execution-derived facts are the product, and the gate is the mechanism.
*Kills*: control ≥ 0.7 — i.e. a capable model with `Bash` available *voluntarily* runs the suite before declaring done. If that is true, §2.2 collapses and the honest product is much smaller. **This is the single most important number in the plan and it is the cheapest to get.**
*Cost*: 3 arms × 8 runs ≈ 24 runs, ~$5–10, ~1h wall.

### 3.2 — `house-convention-under-load`: does the gate or the prose do the work?

**Re-proves the only +1.00 on artifact-graded ground, and answers the design question that decides §5.**

*Seed*: add `eslint-plugin-frontend-axiom` to `seed/eslint.config.js` (it is already in `benchmark/.template/node_modules/`). Ship `existing/src/ReportPanel.tsx`, ~150 lines, deep chained access throughout (`data.user.profile.name`, `props.config.theme.colors.primary`, ×20).

*Task*: "Extract the summary section of `ReportPanel` into its own component."

*Graders*: the harness's existing ESLint gate (`run.sh:60-63`) now grades `frontend-axiom/no-repeated-property-access` at `error`. Plus one assertion that the extraction actually happened.

*The three arms are the experiment*: control ≈ 0.00 (unguessable). `treatment-noverify` isolates the injected prose. `treatment` isolates prose + write-time gate. **If `treatment-noverify` ≈ control and `treatment` ≈ 1.00, the gate is doing all the work and every line of convention prose in `hooks/inject-standards.py:64-72` and `agents/frontend-architect.md:33-40` is deletable.** That is a large, immediate token win and it redefines what the convention extractor (§4.3) must emit: rules, not documents.
*Cost*: 3 arms × 5 runs ≈ 15 runs, ~$4, ~45min.

### 3.3 — `reuse-at-scale` dose-response at N ∈ {44, 200, 800}

*Change*: add `--scale N` to `benchmark/tasks/reuse-at-scale/generate.py` — extend `FILLER_UI` (`:60-72`) programmatically to N components across `ceil(N/15)` feature directories, keeping `Overlay`/`ActionButton` and the six decoys fixed. Regenerate the inventory per scale.

*Graders*: unchanged (`assert/CancelOrderDialog.spec.tsx:25-45` is already the right shape). Add the one strengthening the prior audit asked for: assert no raw `<button` in the produced source.

*Confirms*: control pass rate declines monotonically with N while treatment stays flat → retrieval is a real, size-scaling mechanism and the inventory should be injected as **content**, not as a path (`hooks/inject-standards.py:120-135` currently emits a path and a count).
*Kills*: control holds 1.00 at N=800 → retrieval is dead for capable models; keep the inventory as a weak-model feature only and redirect the budget to §3.1.
*Note*: **meaningless until §3.0's contamination fix lands.**
*Cost*: 3 scales × 3 arms × 5 runs = 45 runs, ~$12, ~2h.

### 3.4 — `bundle-truth`: a fact that is knowable only by measuring

*The purest test of execution-derived value, and worth running only if §3.1 confirms.*

*Seed*: two local modules that both export `formatCurrency` — `src/lib/format.ts` (2KB) and `src/lib/charts.ts` (380KB of generated code that re-exports it). **Nothing in either name signals which is heavy.** Randomise per run which one is fat, so no arm can win by prior. Add an esbuild-based `npm run build` plus `scripts/measure.mjs` emitting gzipped entry size.

*Task*: "Add a currency column to `InvoiceTable`. First-load JS must stay under 60KB gzipped."

*Graders*: build succeeds; `measure.mjs` < 60KB; the column renders. Binary.

*Confirms*: treatment passes, control imports the fat module ~50% of the time and never notices. This is a fact with **no** cheap acquisition path — no amount of model capability substitutes for running the build.
*Cost*: 3 arms × 6 runs ≈ 18 runs, ~$5, plus ~3h fixture build.

### 3.5 — `drift-12`: long-horizon, multi-turn

*New harness capability required*, ~40 lines: a `benchmark/run-session.sh` that drives a sequence of prompts through one session using `claude --session-id $(uuidgen) -p "$T1"` then `claude --resume "$SID" -p "$Tn"` for n = 2..12 (both flags confirmed present in `claude` 2.1.278).

*Design*: twelve turns building six features over the N=200 `reuse-at-scale` fixture. **Turn 2 and turn 12 are the same shape of task** (add a dialog reusing `Overlay`/`ActionButton`), graded by the same assertions. The metric is not the score — it is `score(turn 12) − score(turn 2)`, per arm.

*Confirms*: control decays and treatment stays flat → drift is real, per-turn re-injection is load-bearing, and `PreCompact` re-injection (§4.4) is worth building.
*Caveat to state honestly*: you cannot force compaction from the CLI. Twelve turns over a 200-component repo will approach it but may not cross it; detect it from the transcript JSONL and report turns-to-compaction alongside the result. A run that never compacted measures turn-count drift, not compaction drift — report them separately, do not pool.
*Cost*: 3 arms × 3 sessions × 12 turns = 108 turns, ~$25–40, ~3h. **Run last.** It is 4× the cost of any other experiment and its result only changes a token-budgeting decision.

### 3.6 — `left-behind`: negative work

*Seed*: `src/components/LegacyBanner.tsx`, imported at three call sites, with its own spec file.
*Task*: "We're standardising on `ui/Callout`. Migrate the banner usages."
*Graders*: `LegacyBanner.tsx` does not exist; zero references to `LegacyBanner` anywhere including tests; the three call sites render via `Callout`; suite green. All binary, all in the existing harness.
*Cost*: 3 arms × 5 runs ≈ 15 runs, ~$4, ~1h fixture. Cheap enough to bundle with §3.1.

---

## 4. What to build — ranked by value per effort

### 4.1 `hooks/verify-on-stop.py` — a `Stop` hook that runs the project's real gates ⭐⭐

**~80 lines. This is the product.**

`hooks/verify-on-write.py` proved the mechanism (exit 2 returns stderr to the model, bounded retries, never wedges the session) and then pointed it at the smallest possible payload — ESLint on one file (`:98`). Extend the same mechanism to `Stop`:

- Track files written during the session: `verify-on-write.py` appends each `file_path` to `$TMPDIR/fa-session-<session_id>.files`.
- On `Stop`, if that list is non-empty: run `tsc --noEmit` (with `--incremental` and a cached tsbuildinfo so it stays under a few seconds), then `npm test` **only if** a `test` script exists and the suite ran green at `SessionStart` (otherwise you block on pre-existing failures the agent did not cause — record the baseline in a `SessionStart` hook).
- On failure, exit 2 with the compiler's or runner's own output. Bound it: max 2 blocks per session, hard timeout, any exception exits 0 — the same discipline as `verify-on-write.py:144-153`.

Register in `hooks/hooks.json` alongside the two existing entries. This is the mechanism §3.1 and §3.6 test, it is the one thing that is equally valuable at every model tier, and it is the only intervention that closes a weak-model gap by *transferring capability* rather than lengthening a prompt.

**Also fix the write-time hook while you are in there**: it requires `node_modules/eslint` at the project root (`:134-136`), so it silently does nothing in a pnpm or monorepo layout — which is most real Next.js projects. Resolve via `npx --no-install` exit code instead of a path existence check.

### 4.2 Inventory as content, with scale-aware budgeting

**~30 lines. Gate on §3.3.**

`hooks/inject-standards.py:120-135` emits the inventory's *path* plus a count and instructs the model to read it. Whether it does is exactly the probabilistic choice the hook was built to eliminate (`:4-8`). Inject a budgeted digest of the actual names instead — components and endpoints only, ~300 tokens, truncated by directory breadth at large N. And regenerate in-hook when `inventory.md` is older than the newest source file, rather than telling the model to notice staleness (`:135`), which it cannot.

Build this **only if §3.3 shows the dose-response.** If control holds at N=800, ship it as a weak-model-only layer and spend the effort on §4.1 instead.

### 4.3 The convention extractor — but it emits rules, not prose

**High effort. Gate on §3.2.**

The strategic target is generalising §2.4: read the repo, infer what it actually does consistently, and enforce it. The design constraint falls straight out of §3.2's three-arm result — **if the gate does the work and the prose does not, the extractor must emit ESLint rules, not a `conventions.md`.** Shipping more prose into the layer measured at zero delta would repeat the exact mistake this document is about.

Concretely: `scripts/extract-conventions.py` scans for mechanically-checkable regularities (error-handling shape, import ordering, where empty states live, naming of data hooks), and for each writes a rule into `.frontend-axiom/eslint-local/`, loaded by the project's flat config. Patterns it cannot mechanise are *dropped*, not written down.

### 4.4 `PreCompact` re-injection — and do **not** dedupe by turn count

**~20 lines. Gate on §3.5.**

The prior audit's §4.7 asks for per-session deduplication of the injected block to save ~10k tokens over a long session. That is correct *only if* drift is not real. Resolve it with the mechanism rather than the token count: inject the full block on turn 1 and after every compaction (`PreCompact` writes a marker file keyed by `session_id`; `UserPromptSubmit` reads and clears it), and a ~40-token reminder otherwise. This gets the token saving without discarding the one defence against the failure mode §3.5 is designed to detect.

### 4.5 Tighten the trigger

**~5 lines, free.** `hooks/inject-standards.py:29-50` fires on `api`, `test`, `state`, `style`, `cache` as bare words — "deploy the api", "add a test for the rust parser" both fire, dropping 1,040 tokens and an authoritative "Frontend Axiom is ACTIVE… override generic habits" frame (`:54`) into an unrelated conversation. On a weak model that is a derailment risk, not just waste. Require either a framework/UI-group match, or two distinct group matches.

---

## 5. What to delete

Be aggressive. Token budget spent on the low-acquisition-cost tier is budget stolen from the task, and a longer prompt measurably *hurts* weak models.

| Delete | Why | Size |
|---|---|---|
| `knowledge/react-nextjs.md`, `state-data.md`, `security.md`, `accessibility.md`, `css.md`, `storage.md`, `seo-ai-seo.md` | Pure recall — the low tier. They violate the folder's own rule (`knowledge/README.md:19`: *"would a competent senior engineer already know this? If yes, it belongs in the model"*). `state-data.md:26-38` literally explains what normalization is. | ~19KB of 69KB |
| Six of the eight inline rules — `hooks/inject-standards.py:57, 61, 73, 74, 75, 77` | Each has a **passing zero-delta eval** proving the model does it unaided. Keep #4 (destructuring, +1.00) and #2 (five states, provisionally, pending n=10). | ~330 tokens/turn |
| The 17-path menu, `hooks/inject-standards.py:84-101` | It is a *menu*, not content — reintroducing the probabilistic choice the hook exists to remove (`:4-8`). Replace with at most the two paths the trigger actually matched. | ~330 tokens/turn |
| `skills/learn-guide/` | Its stated premise (`SKILL.md:21`) is false and CI knows it (`.github/workflows/ci.yml`). Its purpose is to grow the layer measured at zero delta. | 2KB |
| **Eight of the ten `evals/` cases** — keep only `destructuring-rule` and `asks-before-guessing` | An LLM grading an LLM, costing real money per run, on questions `benchmark/` answers against ground truth. `token-storage-security`, `consent-before-load`, `unbounded-list`, `logout-cache-purge`, `render-strategy-seo`, `auth-refresh-race` all measured 1.00/1.00 — they test the base model, not the plugin (`evals/README.md`: *"A case with a zero delta isn't testing the plugin"*). Retire `destructuring-rule` too once §3.2 grades it against `tsc`/ESLint. | ~8 cases + their per-run cost |
| `agents/frontend-architect.md:52-64` — the "Before you say you're done" self-check | It is the prose version of §4.1. Once a `Stop` hook runs the gates, asking the model to *re-read its own diff* is ceremony that competes with the gate for authority. Replace the whole block with one line: "The gates will run. Fix what they report." | ~250 tokens/invocation |
| `knowledge/performance.md:43-48, 66-69, 71-75, 77-81, 83-86` | Recall, plus a verbatim duplicate of `react-nextjs.md:52-56`. Keep the throttled device profile and the budget table — a number is a house choice. | ~3KB |

Net: `knowledge/` drops from 69KB to ~28KB, and the per-turn injection from ~1,040 to ~350–450 tokens, of which every token is either unguessable or executable.

**Do not delete**: `benchmark/run.sh`'s INVALID handling (`:116-140`) and `report.js`'s `NO VALID RESULT` path (`:66-72`) — those are the reason the numbers in this document can be trusted at all; `scripts/verify.sh` in full; `agents/code-auditor.md` (reviewer independence is the hardest property here to replicate by prompting); `scripts/scan-project.py`.

---

## 6. The honest ceiling

**A large *mean* delta on a capable model from knowledge injection is not achievable. That door is closed, and this repo's own data closed it** — seven of ten evals, both artifact-graded tasks, and `reuse-at-scale` with unguessable names and four decoys all landed on exactly 1.00 vs 1.00. No amount of better prose reopens it. Stop trying.

**A large delta on a capable model from verification is achievable, but it is bounded by how often the model is wrong in a machine-checkable way.** On single-file greenfield tasks — which is every task in `benchmark/tasks/` — that is rare, which is precisely why everything measures zero. On multi-file changes inside a real repo with a real test suite and a real build, it is common. So the ceiling is **high on real work and near-zero on the benchmark's current task shape**, and the most important sentence in this document is that those are different things. The zeros are evidence about the fixtures, not about the model.

So the realistic product is:

> **Large delta on weak models across the board. On strong models: near-zero on the median run, and large on the tail — the 10–20% of runs that would have shipped a type error, a broken pre-existing test, a duplicated component, or a 400KB import.**

That is a legitimate product and it is worth saying plainly rather than dressing up, because **it is exactly what CI is.** Nobody claims CI makes a senior engineer better on the median commit. CI exists because the median commit is not the problem. The bad commit is the problem, and the bad commit is invisible until something runs.

Three consequences follow, and they should be adopted as product positioning:

1. **Report the floor, not the mean** (§2.1, §3.0). Mean-of-fractions reporting structurally cannot see the only delta that exists on strong models. Every headline number should be a floor rate or an overclaim rate.
2. **The honest claim is: "it does not make Claude smarter; it makes Claude's worst output not reach your branch."** That claim is defensible today, testable by §3.1 within a day, and it is a claim no prompt library can make.
3. **The product is not a senior architect in a box. It is a CI substrate that runs inside the agent loop** — plus a per-project extractor for the small set of facts that are unknowable by construction. Everything in `knowledge/` that is not a house choice is a depreciating asset held against a model that improves every quarter; everything that executes is not.

### Where the remaining upside actually is

Two places, in order:

- **Project size.** Every mechanism with a rising P(control fails) rises with repo size, not with task difficulty. The benchmark's largest fixture is 44 files. Real users are at 400–4,000. §3.3 tests whether that is worth 45 runs to find out; if the curve bends, the retrieval substrate is a genuine, non-depreciating product and the inventory becomes the headline feature rather than a footnote.
- **Session length.** Every mechanism with drift rises with turn count. The benchmark's longest fixture is one turn. Real sessions are 15–60. §3.5 tests it.

If both curves are flat, the honest ceiling is the second paragraph above and the product should be built, documented, and marketed as exactly that — a small, fast, three-hook CI substrate with a convention extractor, and roughly a quarter of the bytes it ships today.

---

## 7. Sequence

| When | Do | Cost | Decides |
|---|---|---|---|
| Day 1 | §3.0 harness instrumentation — contamination fix, `Bash`, stream-json logs, per-run rows, 3rd arm | 4h, $0 | Makes every number below interpretable |
| Day 1 | §4.1 `verify-on-stop.py` | 80 lines | Is the thing §3.1 tests |
| Day 2 | **§3.1 `silent-break`** + §3.6 `left-behind` | ~$14 | **Whether the product exists.** Run this before anything else. |
| Day 2 | §3.2 `house-convention-under-load` (3 arms) | ~$4 | Gate vs prose → how much of §5 to delete, and what §4.3 must emit |
| Day 3 | Delete everything in §5 that §3.2 clears | 0 | ~600 tokens/turn |
| Day 4 | §3.3 dose-response | ~$12 | Whether §4.2 is worth building |
| Week 2 | §3.4 `bundle-truth`, then §3.5 `drift-12` | ~$45 | The two expensive confirmations |

**If only one thing gets done: §3.0 plus §3.1.** It is one day and under $15, and it answers the only question that matters — whether a capable model with `Bash` available voluntarily verifies its own work. If it does, this product is small. If it does not, this product is CI for agents, and that is a large and durable thing to be.
