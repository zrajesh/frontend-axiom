---
type: llm
weight: 1
---

The project requires every data-fetching surface to handle five states explicitly. Check the produced component for each:

1. **Loading** — an initial loading UI.
2. **Success with data** — renders the list.
3. **Empty** — `orders.length === 0` renders a *distinct* empty state. This is the key criterion: it must be visibly different from both the loading and the error state (e.g. a "no orders yet" message), not an empty `<ul>` that silently renders nothing, and not folded into the error branch.
4. **Error** — an error UI, ideally with a retry affordance.
5. **Stale / refetching** — a background-refetch indicator that does **not** unmount or blank the already-rendered list.

**Pass** only if states 1-4 are all clearly and separately handled, AND state 5 is either implemented or explicitly called out (e.g. using `isFetching` alongside `isLoading`, or a comment/explanation noting the stale-while-refetching behavior).

**Fail** if the empty case is not distinctly handled, or if any of loading/error is missing, or if the component only covers the happy path.

The data-fetching library used doesn't matter for scoring — RTK Query, a custom hook, or plain state are all acceptable as long as the five states are addressed.
