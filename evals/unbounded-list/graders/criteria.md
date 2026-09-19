---
type: llm
weight: 1
---
A naive answer maps 50,000 rows into the DOM. That is the failure this case tests.

**Pass** requires BOTH:
1. Refuses to fetch the unbounded collection — requires server-side pagination with a limit, and treats an endpoint returning everything as a problem to fix rather than work around on the client.
2. Requires **virtualization / windowing** for rendered rows (react-window, @tanstack/react-virtual, or equivalent), rather than rendering all rows.

Bonus, not required: cursor over offset pagination; accessibility of virtualized rows; memory/INP impact on low-end devices.

**Fail** if it renders the full array, relies only on CSS `overflow` scrolling, or treats "add a search filter" as the fix.
