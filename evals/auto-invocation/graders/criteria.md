---
type: llm
weight: 1
---

The prompt is a plain feature request with **no hint** of any plugin, standard, agent, or convention — exactly what a real user types.

## Fairness rule for this grader

Every criterion below must be one that a model with **no plugin at all** could satisfy on its own merits. A criterion the control arm is structurally incapable of meeting does not measure quality — it measures whether the plugin is installed, which we already know.

**Specifically: award nothing for naming a plugin command, a plugin agent, or a "project convention" by name.** An earlier version of this grader did, and the control arm cannot name a workflow it was never told exists. That made the case unfalsifiable and inflated its score. Judge the *substance of the engineering answer*, never its vocabulary.

## Pass

Requires at least **two** of the following, each judged on substance:

- **Handles the empty state as a distinct case.** Names loading / data / **empty** / error, where empty is explicitly different from loading and from error. Loading + error alone is the generic answer and does NOT count.
- **Handles the stale/refetching case** — that already-rendered content should not be blanked while revalidating.
- **Refuses to invent the API response shape**, and asks for the real contract or field names instead of assuming `name`/`email`/`avatarUrl`.
- **Raises where the auth token lives** (httpOnly cookie vs client-readable storage) as a decision to make rather than an assumption.
- **Raises accessibility concretely** — semantic elements, a real label, keyboard operability — not "make it accessible".

## Fail

- Writes the component with invented field names and no question.
- Generic React advice with none of the above.
- Mentions plugin commands or conventions but shows **none** of the substantive markers. Vocabulary is not evidence.

Do not reward verbosity. Do not require the component to be written — asking first is correct here, and an answer that asks well should score as highly as one that builds well.
