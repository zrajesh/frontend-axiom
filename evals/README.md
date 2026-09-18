# Evals

Behavioral tests for the plugin. The ESLint suite tests a *rule*; these test whether the skills and agents actually produce the behavior the standards describe.

This exists because of a real failure: v0.1's README claimed `/new-feature` delegated to the `frontend-architect` agent. It didn't, and nothing caught it, because agent behavior was asserted rather than tested.

## Running

```bash
# One case, one run — fast sanity check
claude plugin eval . --case token-storage-security --runs 1 --ablation none

# Full suite (default 3 runs/case, plus a no-plugin baseline arm)
claude plugin eval . --trust-plugin

# Cap spend
claude plugin eval . --max-cost-usd 5.00
```

Each run is a full Claude child process on your own credential, so the full suite costs real money and time — roughly $0.05-0.20 per run depending on the case. Budget accordingly; a single case at `--runs 1` is ~$0.05.

The default `--ablation with-without` also runs each case *without* the plugin and reports the delta. That's the number that matters: it shows whether the plugin changed the outcome, or whether the model would have done the right thing anyway. A case with a zero delta isn't testing the plugin — it's testing the base model.

## Cases

| Case | What it pins down |
|---|---|
| `asks-before-guessing` | Given a deliberately underspecified request, the agent asks about the data contract instead of inventing field names. This is principle #1 and the easiest to regress. |
| `destructuring-rule` | Applies the destructuring convention to chained access — **and** correctly exempts a discriminated union, where destructuring before narrowing would break TypeScript. Guards both directions of the rule. |
| `five-data-states` | Handles loading / data / **empty** / error / refetching. The empty state, distinct from loading and error, is the one that ships broken most often. |
| `token-storage-security` | Refuses `localStorage` for an auth token and recommends httpOnly cookies — with the prompt actively arguing for the wrong answer. |

## MCP servers

The Figma and Chrome DevTools servers have no mocks, so they aren't started and their tools are unavailable during eval runs. None of the current cases need them. If you add a case exercising `/pixel-check`, add a mock under `evals/mocks/<server>/` rather than passing `--allow-real-servers`.

## Writing a new case

```bash
claude plugin eval init --bare <case-name>
```

Then fill `prompt.md` (frontmatter: `max_turns`, `allowed_tools`) and `graders/criteria.md` (frontmatter: `type: llm`, `weight`).

Write graders with explicit pass **and** fail conditions, and say what shouldn't count either way — a vague grader produces noisy scores across runs and teaches you nothing. Where a standard has a documented exception, test the exception too: a case that only checks the happy direction will happily pass an agent that over-applies the rule.

Results land in `evals/results/<timestamp>/` (gitignored) with an HTML report.
