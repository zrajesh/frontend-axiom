# What belongs in here

These files are read by agents mid-task, so every word competes with the budget needed to do the work. An earlier version had agents reading twelve documents before writing a line of code, and runs timed out.

## The rule

**Write down decisions, thresholds, traps, and house choices. Never explain a concept.**

The model knows what `no-store` means, what `Intl.NumberFormat` does, why SSR helps SEO. Benchmarking this plugin measured a **zero delta on most generic standards** — the model already met them unaided. Restating them costs budget and buys nothing.

| Include | Exclude |
|---|---|
| "Hashed assets get `immutable`; HTML gets `no-cache`" | What `immutable` means |
| "Virtualize past ~1,000 rows" | What virtualization is |
| "Forwarding cookies fragments the cache key to a ~0% hit rate" | What a cache key is |
| "Destructure to the leaf value" | What destructuring is |
| "Default `Array.sort()` misplaces accented characters" | How `sort` works |

A good test: **would a competent senior engineer already know this?** If yes, it belongs in the model, not in this folder. What they *couldn't* know is what this team decided, and which specific mistake keeps reaching production.

## Where the real value is

Benchmark results put the plugin's measurable gains in two places, neither of which is general knowledge:

1. **Engaging at all** — the `UserPromptSubmit` hook, not a document.
2. **House conventions the model cannot guess** — the destructuring rule scored **+1.00** precisely because nothing in training implies it.

Project-specific facts beat both, and they live in `.frontend-axiom/inventory.md`, generated per repo — which components exist, which endpoints are real. That gap never closes with a better model.

## Adding a file

Only for a domain with no coverage. Prefer a tight section in an existing file. Then add it to the routing table in `agents/frontend-architect.md` and the list in `hooks/inject-standards.py`, or agents will never find it.
