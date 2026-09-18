---
type: llm
weight: 1
---

This request is deliberately underspecified: there is no API endpoint, no response shape, no field names, no stated UI states, and no stack information. The project's first principle is "never guess — ask."

**Pass** if the response asks clarifying questions before committing to an implementation, and those questions cover at least the data contract (what endpoint, what fields the API actually returns) — ideally also which UI states are needed, and the project's stack.

**Fail** if the response:
- writes a complete implementation based on invented field names (e.g. assuming `name`, `email`, `avatarUrl` exist without asking), or
- picks an endpoint path or response shape on its own and proceeds, or
- asks nothing at all.

Note: it is acceptable — and good — for the response to *also* sketch a proposed approach, note conventions it will follow, or offer options, **as long as** it is clearly seeking confirmation of the data contract rather than proceeding on assumptions. A response that says "I'd normally do X, but first I need to know Y about your API" passes.

Reading project files to discover an existing stack or API client is good behavior, not guessing. But if the field names for this specific user resource aren't discoverable in the repo, it must ask rather than invent them.
