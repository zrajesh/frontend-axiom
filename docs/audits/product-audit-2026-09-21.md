# Product Audit: Frontend Axiom

Date: 2026-09-21 · Scope: the whole plugin as shipped — `hooks/`, `knowledge/` (17 docs), `skills/` (5), `agents/` (2), `scripts/`, `eslint-plugin-frontend-axiom/`, `evals/`, `benchmark/` (incl. all five result sets)
Reviewer: independent product audit. Every claim below is cited to the file that supports it; measurements were re-derived from the repo, not taken from the briefing.

---

## 1. Verdict

Frontend Axiom is, today, **a reliable context-injector wrapped around a standards library that a strong model does not need, plus an evidence harness that almost never runs.** The one structural thing it does well — `hooks/inject-standards.py` makes engagement deterministic instead of probabilistic — is real and worth keeping. But look at what it made deterministic: 1,041 tokens (measured, not estimated) of rules the model already follows, plus seventeen *paths* the model may or may not read. Meanwhile the one asset that produces evidence rather than opinion, `scripts/verify.sh`, is reachable from exactly two places (`skills/audit/SKILL.md:24`, `agents/code-auditor.md:22`) and from neither the hook nor the builder. The plugin therefore guarantees the cheap half of the discipline (telling the model what it knows) and leaves the expensive half (checking what it wrote) to chance — a precise inversion of its own measurements. It is pretending to be a knowledge product. The measurements say it is a *determinism* product that has so far pointed its determinism at the wrong payload. The two things that scored +1.00 — engaging at all, and a convention nothing in training implies — are both instances of "make an unguessable, unskippable thing happen." Everything that scored 0.00 is an instance of "restate what the model knows." The product should be built entirely out of the first category. It currently spends most of its bytes on the second.

One further honesty note the README does not make: **the headline `auto-invocation` +1.00 is close to circular.** Its grader passes a response that "references a project convention by name" or "names one of the project's own workflows or commands" (`evals/auto-invocation/graders/criteria.md:14-15`). The control arm has no injected text and therefore *cannot* name a workflow it was never told about. That case proves the hook fires. It does not prove the artifact improved — and the outcome benchmark, which grades artifacts, found ~0 delta on every task that grades artifacts. The honest claim is: *the plugin reliably changes the conversation; it has not yet been shown to change the code, except for house conventions.* That is a smaller claim, and it is the one the evidence supports.

---

## 2. REMOVE

### 2.1 Seven knowledge documents, outright

Delete `knowledge/react-nextjs.md`, `state-data.md`, `security.md`, `accessibility.md`, `css.md`, `storage.md`, `seo-ai-seo.md`. That is 18,888 bytes — **28% of the knowledge base** (67KB excluding its README) — and it is pure recall.

The case against them is not my taste; it is the folder's own editorial rule, which they violate:

> "**Write down decisions, thresholds, traps, and house choices. Never explain a concept.**" — `knowledge/README.md:7`
> "A good test: would a competent senior engineer already know this? If yes, it belongs in the model, not in this folder." — `knowledge/README.md:19`

Apply that test:

- `knowledge/react-nextjs.md:5-12` is the Server-vs-Client component table from the Next.js docs. `:14-23` is the rendering-strategy table from the Next.js docs. There is not one house decision in the file.
- `knowledge/state-data.md:26-38` *explains what normalization is*, with a worked `{ids, entities}` example. This is the single most direct violation of `README.md:7` in the repo.
- `knowledge/security.md` is OWASP plus Next.js specifics, end to end. No threshold, no house choice, no trap.
- `knowledge/accessibility.md` is 1,610 bytes of WCAG recall. The `token-storage-security` and consent cases already measured 1.00/1.00 unaided; there is no reason to believe "use `<button>` not `<div onClick>`" is the exception.
- `knowledge/storage.md` restates inline rule #3 (`hooks/inject-standards.py:61-63`) and `auth.md:11` for a third time. Triple redundancy on the one rule the model already gets right.
- `knowledge/css.md`, `knowledge/seo-ai-seo.md` — same shape. The only non-obvious line in either is `seo-ai-seo.md:19` on `llms.txt`; move it into whatever survives and delete the rest.

The editorial rule was clearly written *after* the measurements landed and the folder was never re-edited against it. Do that now.

### 2.2 The inline rule block, cut from 8 rules to 2

`hooks/inject-standards.py:56-78` costs ~430 of the 1,041 injected tokens. Six of its eight rules were measured at zero delta:

| Inline rule | Line | Measured |
|---|---|---|
| #1 never guess | :57 | `asks-before-guessing` 1.00 / 1.00 — **cut** |
| #2 five data states | :58 | +0.33, n=3, one control flip — **keep, provisionally** |
| #3 tokens in cookies | :61 | `token-storage-security` 1.00 / 1.00 — **cut** |
| #4 destructure to leaf | :64 | **+1.00 — keep. This is the product.** |
| #5 tests ship with code | :73 | untested claim; enforce with a gate, not prose — **cut** |
| #6 semantic HTML | :74 | generic; `jsx-a11y` + axe enforce it — **cut** |
| #7 no unbounded fetch | :75 | `unbounded-list` 1.00 / 1.00 — **cut** |
| #8 consent gates loading | :77 | `consent-before-load` 1.00 / 1.00 — **cut** |

Rules #1, #3, #7, #8 each have a passing zero-delta eval sitting in `evals/` proving the model does this unaided. Keeping them is not caution, it is paying rent on measured-worthless bytes on every single turn.

### 2.3 The seventeen-path directory listing

`hooks/inject-standards.py:80-97` spends ~330 tokens printing absolute paths and one-line descriptions of all 17 docs. Two problems:

1. It is a *menu*, not content. Whether the model reads any of it is exactly the probabilistic choice the hook was built to eliminate (`hooks/inject-standards.py:4-8`). The hook fixed skill invocation and then reintroduced the same failure mode one layer down.
2. After 2.1 there are ten docs, and after 2.4 fewer. A menu that long is ignored anyway.

Replace with the routing table already maintained in `agents/frontend-architect.md:19-33` and inject at most the two paths the trigger actually matched.

### 2.4 `knowledge/performance.md`, roughly half

`:43-48` (resource hints), `:66-69` (images/fonts, verbatim duplicate of `react-nextjs.md:52-56`), `:71-75` (network), `:77-81` (INP), `:83-86` (service workers, duplicating `caching.md:26-36`) are all recall. Keep `:17-41` — the throttled device profile and the lab-vs-field distinction are the only parts that constitute a *decision*, and they are genuinely the part teams skip. Keep `:54-62` (the budget table) because a number is a house choice. Delete the rest.

### 2.5 `skills/learn-guide`

`skills/learn-guide/SKILL.md:21` states: *"Every skill/agent already reads the whole `knowledge/` tree, so a new file needs no separate index update."* This is false, and CI knows it is false — `.github/workflows/ci.yml:44-55` exists specifically to fail when a knowledge file is not routed from the hook. A skill whose job is to grow the knowledge base, which grows it in a way the build gate rejects, is a defect generator. Worse: its whole purpose is to add more prose to the layer measured at zero delta. Delete it, or rewrite it as "extract a convention from this doc and emit a lint rule" (see §4.6).

### 2.6 Stop reporting ±0.05 as a result

`benchmark/results/20260920T041541/summary.tsv` has `big-list` treatment **1.000**; `benchmark/results/20260920T132921/summary.tsv` has the same task, same arm, **0.667**. The arm moved 0.33 between runs. Against that variance, the reported "+0.05, not significant at n=3" is not a weak signal — it is indistinguishable from noise, and publishing it (`benchmark/README.md`) invites the reader to treat it as a small positive. Report it as **no measurable effect**, or raise n until the confidence interval is narrower than the effect you care about.

---

## 3. KEEP

### 3.1 The hook mechanism — but not its current payload

`hooks/hooks.json:3-9` + `hooks/inject-standards.py` is the only thing in the repo that converts a probability into a guarantee, and the CHANGELOG records why it had to exist (measured runs completed with zero `Skill` invocations). Keep the mechanism without reservation. Everything in §2 is an argument about *what* it should carry, never *whether* it should fire.

### 3.2 The destructuring rule and its ESLint enforcement

`knowledge/principles.md:17-67` + `eslint-plugin-frontend-axiom/rules/no-repeated-property-access.js` + 20 tests. This is the only asset with a +1.00 delta that isn't measuring its own presence. It earns that score for a precise reason worth naming: **it is unguessable by construction**, and it is *executable* — a rule with a linter behind it is a rule that survives the model forgetting it.

The rule implementation is genuinely good: it keys on the resolved `Variable` rather than per-function (`no-repeated-property-access.js:121-138`), so sibling closures share a tally and shadowed names don't collide; and it tracks every hop of a chain (`:160-170`), so `data.user.email` + `data.user.name` reports against `data.user`. And `principles.md:58-67` honestly documents the three things it cannot catch. That honesty is the right standard for the rest of the repo.

**But it is not enforced by the plugin's own gate.** `eslint-plugin-frontend-axiom/index.js:6` ships the rule at `"warn"`; `scripts/verify.sh:81` fails only when `errorCount > 0`. So the one differentiator in the product cannot fail the one gate in the product — while `knowledge/release-operations.md:20` explicitly says a permanent `warn` is decoration. Fix this first; it is a one-word change with more measured justification behind it than anything else in the repo.

### 3.3 `scripts/verify.sh` — the right idea, wired to almost nothing

The design rules in its header (`:7-12`) are correct and rare: a gate that cannot run reports SKIP, never PASS; a missing gate is itself a finding; never mutate the project. The `nfiles == 0` check at `:77-80` (a lint run that inspected nothing is not a pass) is the kind of detail that separates a real harness from a green checkmark. Keep all of it.

Two defects to fix while keeping it:

- **The bundle gate is miscalibrated by roughly 3-5×.** `:120` sums *raw, uncompressed* bytes across *every chunk in the app*; `:123` compares that to `BUDGET_KB=170`, which `knowledge/performance.md:54-60` defines as **compressed, first-load JS, per route**. Three mismatches at once (compression, scope, route granularity). This gate will fail a hello-world Next.js app, which means in practice it gets ignored or the budget gets raised until it's meaningless.
- **`:95` detects `jsx-a11y` by grepping the config text**, so a project that inherits it through a shared or extended config reports SKIP. Resolve the config instead (`eslint --print-config`).

### 3.4 `scripts/scan-project.py` and the inventory

The docstring at `:5-19` contains the single sharpest strategic sentence in the repository: *"What a model can NEVER know is your codebase... That is unguessable by construction."* Correct. Regex-over-parser (`:20-24`) is the right call for something that must never block a session.

Keep it. But it is currently delivered wrong — see §4.2.

### 3.5 `agents/code-auditor.md` and the reviewer-independence property

Independence was demonstrated, not asserted: the main conversation was told the insecure token was signed off and not to report it, and the auditor reported it Critical anyway (`README.md:64`). That is a genuine architectural property and the hardest thing in the repo to replicate by prompting alone. `agents/code-auditor.md:27` — treat SKIP as a finding — is exactly right.

### 3.6 The benchmark harness itself (not its tasks)

`benchmark/run.sh` is better engineering than the results it has produced. `:114-124` marks a rate-limited or output-less run **INVALID** rather than scoring it zero, and `benchmark/README.md:24-31` records why: an earlier revision manufactured a +0.45 delta out of an outage. `:98-101` already supports a task shipping an `existing/` codebase with the inventory auto-generated. `:31`/`:80` already support `--model` and record it. The scaffolding for the right experiment is built; it has never been pointed at the right tasks (§6).

---

## 4. ADD — ranked by value per unit of effort

### 4.1 Make verification deterministic, the same way engagement was made deterministic (⭐ highest)

**Effort: ~40 lines. Value: this is the product.**

Today: the builder's self-check is `agents/frontend-architect.md:52-64` — a prose instruction to "re-read your own diff." That is precisely the "opinion, not evidence" the plugin says it exists to replace (`scripts/verify.sh:4-6`). And `verify.sh` is never invoked on the build path: it appears only in `skills/audit/SKILL.md:24` and `agents/code-auditor.md:22`, both of which require the user to explicitly run `/audit`.

So the architecture is:

```
engagement:    hook    → deterministic ✓   (payload measured ~0 delta)
verification:  prose   → probabilistic ✗   (produces the only evidence)
```

Invert it. Add a `Stop` hook (and/or `PostToolUse` on Write/Edit of `*.tsx|*.ts`) that runs the cheap gates — `tsc --noEmit`, `eslint` on changed files — and, on failure, blocks the turn with the compiler's own output. This is the same trick that made engagement reliable, applied to the half of the discipline where measurement shows the value is.

It is also the single highest-leverage thing for weak models (§5): a Haiku-class model that cannot reliably apply a prose standard *can* reliably fix a type error it is shown. **A correction loop transfers capability; a longer prompt does not.**

### 4.2 Inject inventory *content*, and keep it fresh automatically

**Effort: ~25 lines. Value: very high.**

`hooks/inject-standards.py:120-131` emits the inventory's **path** and a count, then instructs the model to go read it. Whether it does is a coin flip — the exact failure the hook exists to prevent. And `:131` says "If it looks stale, regenerate" — the model has no way to tell whether it is stale.

Fix both:
- Inject the actual component/hook/endpoint **names** (a budgeted ~200-400 token digest — names and paths only, props on demand), not a pointer.
- Compare `inventory.md` mtime against the newest source mtime and regenerate in-hook when stale. Deterministic freshness beats an instruction to notice staleness.

This is the highest-ceiling *content* change in the plugin, because it is the only content whose value does not decay as models improve.

### 4.3 A decision log that compounds

**Effort: ~1 skill + 15 lines of hook. Value: high.**

`skills/init-project/SKILL.md:53-55` writes a Stack section to `CLAUDE.md` and then nothing ever appends to it. Every subsequent architectural choice — why cursor not offset here, why this stays a Server Component, why we rejected that library — is made, applied, and forgotten. The next session re-derives it, differently.

Add `.frontend-axiom/decisions.md`, appended on every non-trivial choice, injected alongside the inventory. This is category-identical to the inventory (unguessable project fact, permanently valuable) and it is the thing a senior architect does that an agent structurally does not: **maintain continuity of reasoning across sessions.**

### 4.4 Blast-radius map before a multi-file change

**Effort: medium. Value: high; nothing else covers it.**

Every asset in this repo grades a single file. `benchmark/tasks/*/task.md` all say "Write only that file." The characteristic senior-vs-agent gap is not in the file — it is in the *other eight call sites*. An agent asked to rename a prop changes six of nine and reports success; `tsc` catches the static ones and nothing catches the dynamic one or the test fixture.

Add a pre-edit step for any change to an exported symbol: enumerate call sites (`scan-project.py` already parses exports, so this is an extension, not a new tool), state the count, and make "all N updated" a checkable claim. Then grade it (§6.2).

### 4.5 A "don't build it" protocol

**Effort: low (a rule + a benchmark task). Value: high, and nothing addresses it.**

`knowledge/principles.md:5-7` says never guess. Nothing says *push back*. `skills/new-feature/SKILL.md:13-21` interviews the user about requirements and never once asks whether the requirement is right. An agent is a compliance machine by default; a senior's most valuable output is regularly "this shouldn't be built," "you already have this," or "this is a server-side problem and the frontend cannot fix it."

Add an explicit refusal clause: *when the request would create a duplicate of something in the inventory, encode a security control on the client, or be cheaper to fix a layer down — say so before writing code.* And grade it (§6.3), because a prose instruction to push back that is never measured will not survive contact with a compliant model.

### 4.6 Generalize the one thing that works: extract conventions instead of shipping them (the strategic ADD)

**Effort: high. Value: this is what the product should become.**

The destructuring rule scored +1.00 because it is unguessable. But it is *one team's* unguessable rule, and the plugin ships it to everyone. That is a product with n=1 of its only proven ingredient. Every team has a handful of such rules, and they are all different and all invisible to training data.

The generalizable product is a **convention extractor**: read the repo, infer what this codebase actually does consistently (error-handling shape, folder layout, naming, data-layer idiom, how empty states are rendered), write it to `.frontend-axiom/conventions.md`, inject it, and where the pattern is mechanically checkable, emit an ESLint rule for it. This is `scan-project.py` pointed at *patterns* instead of *inventory*, plus the one part of `learn-guide` worth saving.

That is the version of this product that gets better as models get better, because its entire payload is by definition outside training data. Everything in `knowledge/` that isn't a house choice is, by contrast, a depreciating asset.

### 4.7 Deduplicate the injection across turns

**Effort: ~10 lines. Value: moderate but free.**

`hooks/inject-standards.py:142-145` injects on *every* matching prompt with no session state. At turn 10 of a frontend session the transcript holds ~10,400 tokens of ten byte-identical copies of the same block. The hook payload carries `session_id`; the code reads only `prompt` (`:140`) and `cwd` (`:145`). Inject the full block once per session, a ~40-token reminder thereafter.

Related, and worth a line in the same patch: the trigger is broad enough to misfire meaningfully. I ran it — `"what is the state of the union"`, `"add a test for the rust parser"` and `"deploy the api"` all fire. `:27-28` justifies this as costing "a few hundred tokens"; it actually costs 1,041 tokens *plus* an authoritative frame (`:54` "Frontend Axiom is ACTIVE... They override generic habits") dropped into a conversation about Rust. On a strong model that is waste. On a weak model it is a derailment risk — it will start asking about API contracts in a Python task. Require two distinct trigger matches, or match only in the framework/UI term groups.

---

## 5. Model-tier architecture

**The conflict in the briefing dissolves once the payload is layered, because only one layer is tier-dependent — and it is the layer measured at zero delta for strong models.**

Split the injection into four layers with independent lifetimes:

| Layer | Content | Budget | Tier-dependent? |
|---|---|---|---|
| **L0 Gates** | Executable verification, hook-driven (§4.1) | 0 tokens | No — more valuable on weak models |
| **L1 Project facts** | Inventory digest, decisions, extracted conventions (§4.2-4.3, §4.6) | ~300-600 | No — unguessable at every tier |
| **L2 House rules** | The destructuring rule; the 5-state rule pending better evidence | ~120 | No |
| **L3 Recall** | Generic standards: what survives of `knowledge/` | 0-250 | **Yes — this is the only tiered layer** |

Strong model: L0 + L1 + L2 ≈ **450-700 tokens**, down from 1,041, and every token of it is either unguessable or executable. L3 off entirely.

Weak model: L0 + L1 + L2 + a **task-scoped slice** of L3 — at most two topic blocks chosen from which trigger group actually matched, capped at ~250 tokens. The instinct to give a weak model *more* standard is wrong: weak models degrade with prompt length and conflicting instruction density. They need a *narrower* instruction and a *tighter* correction loop. The L0 gates are what actually lifts them, because a compile error is unambiguous where a prose standard is not.

**Tier detection, concretely.** The `UserPromptSubmit` payload carries `transcript_path`. Read the last assistant line of that JSONL and take `.message.model`; map `haiku` → weak, `sonnet`/`opus` → strong. Turn 1 has no assistant message: default to strong (the cheap arm) and correct from turn 2. Allow an explicit override via `.frontend-axiom/config.json` (`{"tier": "weak"}`) or `FRONTEND_AXIOM_TIER`, so open-model users who route through a proxy can set it by hand. This is ~20 lines in the hook and requires no new infrastructure.

**And then measure it, because right now this entire section is a hypothesis.** `benchmark/run.sh:31` has accepted `--model` and `:80` has written `model.txt` for some time. I checked every result directory: **not one contains a `model.txt`.** Every number this product has ever reported — the +0.23, the seven zeros, the +1.00s — comes from a single undifferentiated model tier. The tier problem the briefing calls a hard constraint has never once been measured. Until `./benchmark/run.sh --model haiku` runs, "lower-end models need the knowledge base" is an assumption, and it is the assumption that justifies keeping 67KB of documents.

---

## 6. What the benchmark should measure

Current tasks (`benchmark/tasks/*/task.md`) are single-file, fully-specified, and instruct "Write only that file." They measure *recall under ideal specification* — the one axis where both arms are saturated. `orders-list` even hands the model `isLoading`/`isError`/`isFetching` in the props contract (`benchmark/tasks/orders-list/task.md:8-12`), telegraphing the answer; the README already concedes this as a task-design flaw.

Discriminating tasks share one property: **the right answer depends on something outside the prompt.** Six, implementable against the existing harness:

**6.1 `reuse-existing` — already built, run it.** `benchmark/tasks/reuse-existing/` seeds `Modal`, `Button`, `cancelOrder()` and asks for a cancel dialog; the grader checks imports and forbids an inline `fetch` (`assert/CancelOrderDialog.spec.tsx:21-36`). This is the correct shape and there are no results for it yet. One strengthening: also assert no raw `<button` appears in the source, which is the design-system fork the docstring describes.

**6.2 `prop-rename-migration`.** Seed `Badge` with a `kind` prop used at 9 call sites across 6 files — one inside a nested feature folder, one in a test fixture, one passed through a wrapper via spread so `tsc` cannot see it. Task: rename `kind` → `variant`. Grade: `tsc` clean (catches the static misses) **plus** a spec asserting all 9 render **plus** `grep -c 'kind='` is 0. Measures thoroughness under multi-file blast radius, which nothing currently measures and where agents reliably fail.

**6.3 `dont-build-it`.** Seed an API that returns all records to every user. Task: "add an admin-only filter so non-admins don't see internal orders." The correct answer is to refuse the framing — a client-side filter is not access control. Grade: the response log must flag it as a server-side concern, and `src/` must not contain a client filter presented as a permission gate. Measures pushback, which no current asset touches.

**6.4 `ambiguous-contract`.** The existing `src/api/orders.ts` returns `reference`; the task prompt calls it "the order number." Grade: the produced code uses `reference` and never invents `orderNumber`. This is the literal thesis of `scan-project.py:5-19` and it has never been tested.

**6.5 `silent-break`.** Ship a seed repo with a passing test suite and ask for a feature that requires editing a shared component. Grade: the **pre-existing** tests must still pass. Measures regression safety — the failure mode that makes agents expensive in real codebases and that every current task structurally cannot see.

**6.6 `house-convention-under-load`.** A 120-line refactor with deep-chained access throughout, run with `eslint-plugin-frontend-axiom` **promoted to `error`** in the seed config (see §3.2 — it is currently `warn`, so the benchmark's lint gate has never graded the plugin's own rule). This is the one dimension with a proven delta and the outcome benchmark does not measure it at all.

**Cross-cutting, and non-optional: run every task at `--model haiku`, `sonnet`, `opus`, and report per tier, never pooled.** `benchmark/README.md` now says exactly this. No run has ever done it.

Also: **raise n or stop quoting small numbers.** The same arm on the same task moved 1.000 → 0.667 between `20260920T041541` and `20260920T132921`. With that variance, n=3 detects only large effects. Report tasks as pass/fail-shaped (did it reuse? did it break the suite?) rather than fractional scores — binary outcomes need far fewer runs to be readable, and every task above is naturally binary.

---

## 7. The one thing

**Move `verify.sh` from the audit path to the build path — make it a hook, not a suggestion — and gate it on the destructuring rule at `error`.**

The plugin's founding insight is written at `hooks/inject-standards.py:4-8`: *relying on the model to spontaneously do the right thing is probabilistic; a hook is not a suggestion.* That insight was correct and it was applied to the wrong half of the workflow. Engagement with the knowledge base was made deterministic and then measured at zero delta on 7 of 10 cases and both artifact-grading benchmark tasks. Verification — the one thing that produces evidence instead of opinion, the one thing that is equally valuable at every model tier, the one thing that gets a weak model to a correct answer it could not have reached by reading prose — was left as a prose instruction to "re-read your own diff" (`agents/frontend-architect.md:52-64`) behind a slash command the user has to remember to type.

Change that and three separate problems close at once. The strong-model context tax drops, because the payload stops being a lecture and becomes a gate. The weak-model gap closes, because a correction loop transfers capability in a way a longer prompt does not. And the product acquires the property it currently only claims: **it stops asserting that the code is good and starts proving it.**

Everything else in this audit is a refinement. That one is the difference between a prompt library and a tool.
