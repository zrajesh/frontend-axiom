# Outcome benchmark

`evals/` asks an LLM whether an answer *sounds* right. This asks whether the
produced **code actually works**: the agent writes a file, then it is compiled,
linted, and rendered. The graders are `tsc`, ESLint (incl. `jsx-a11y`), and a
headless DOM — not an opinion, and not authored by the same hand as the standards.

```bash
./benchmark/run.sh                      # all tasks, 3 runs/arm
./benchmark/run.sh --task big-list --runs 2 --keep
```

## Arms

| Arm | How | Verified |
|---|---|---|
| treatment | installed plugin disabled + `--plugin-dir <repo>` | sees the standards |
| control | installed plugin disabled, no plugin | does not |

`--bare` looks right for the control arm but also skips keychain reads, so it
cannot authenticate. The harness restores your plugin on exit, including on
Ctrl-C or crash.

## Invalid runs are excluded, not scored zero

A run that hit a rate limit or produced no file is marked **INVALID** and left
out. This is not pedantry: an earlier revision scored such runs as `0`, and
because a session limit struck during the control arm it manufactured a
**+0.45 delta out of an outage**. A task that loses an entire arm is excluded
from the mean, and if every task does, the report prints `NO VALID RESULT`
rather than a number.

## Validate the grader before trusting a number

```bash
# a correct implementation must score full marks; a bad one must not
# verified: good 9/9, bad (happy-path only, onClick on <li>) 4/9
```

A grader that cannot fail bad code is worthless.

## Model tier matters, and a single number hides it

```bash
./benchmark/run.sh --model haiku    # smaller model
./benchmark/run.sh --model sonnet
./benchmark/run.sh --model opus     # top tier
```

A top-tier model already knows most of these standards, so the plugin can only
add engagement and project-specific facts. A smaller model does not know them,
so the same injection may be the whole value — while also consuming a larger
share of a smaller context budget. **Averaging across tiers hides both effects.**
Always report the delta per model, never pooled.

## Tasks that ship an existing codebase

A task directory may contain `existing/`, copied in before the agent runs, with
the inventory generated from it automatically. This is what lets a task measure
**reuse** — the thing single-file tasks structurally cannot see. `reuse-existing`
seeds a repo that already has `Modal`, `Button` and a `cancelOrder()` API, then
asks for a cancel-confirmation dialog. Composing what exists scores 8/8; writing
a fresh dialog with a raw `<button>` and an inline `fetch` scores 3/8 — code that
works in isolation and quietly forks the design system.

## Findings so far

| Task | Treatment | Control | Delta | Read |
|---|---|---|---|---|
| orders-list | 1.00 | 1.00 | 0.00 | Props contract listed `isLoading`/`isError`/`isFetching`, which telegraphed the states. Task design flaw. |
| big-list | 0.67 | 0.62 | +0.05 | Not significant at n=3. Both arms reason about virtualization equally. |

The consistent result across both this and `evals/`: **on well-specified
single-file tasks, a strong modern model already meets these standards.** The
plugin's measurable value shows up elsewhere — guaranteed engagement, and
house-specific conventions the model has no way to guess.
