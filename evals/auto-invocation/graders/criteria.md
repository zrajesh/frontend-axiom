---
type: llm
weight: 1
---

This prompt deliberately contains **no hint** about any plugin, standard, agent, or convention. It is a plain feature request, exactly as a real user would type it.

The question this case answers: does the tooling engage *on its own*, or only when the prompt asks it to?

**Pass** requires the response to show at least TWO distinct markers that project-specific standards were actually applied — not merely competent generic advice:

- Explicitly enumerates the five data states (loading / data / **empty** / error / refetching or stale). Listing only loading + error is generic and does NOT count; the *empty* and *refetching* states are the discriminator.
- Refuses to invent the API response shape and asks for the real contract or field names.
- References a project convention by name (e.g. RTK Query as the agreed data layer, feature-first structure, a destructuring convention).
- Names one of the project's own workflows or commands (an init/scaffold step, a design-comparison step, an audit step).
- Raises where the auth token belongs (httpOnly cookie vs client-readable storage) as a decision rather than assuming.

**Fail** if the response simply writes a profile component with invented field names, or gives only generic React advice with no sign that a specific standards set was consulted.

Judge only on evidence of standards being applied. Do not reward or penalize verbosity, and do not require the component to actually be written — asking first is correct behavior here.
