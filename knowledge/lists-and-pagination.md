# Lists, Pagination & Virtualization Standards

Lists are where frontends quietly fail at scale. A page that is fine with 50 rows in development becomes unusable at 5,000 in production, and the failure is invisible until real data arrives.

## Decision table

| Rendered rows | Approach |
|---|---|
| < ~100 | Render normally. Virtualization here is complexity with no payoff. |
| ~100–1,000 | Paginate, or virtualize if the UX genuinely needs one continuous scroll. |
| > ~1,000 | Virtualize. Non-negotiable. |
| Unbounded / user-driven | Virtualize **and** paginate the fetch. Never fetch an unbounded collection in one request. |

Row count is what matters, not payload size: 5,000 DOM nodes with three elements each is ~15,000 nodes, and that's what wrecks INP and memory.

## Never fetch unbounded

`GET /orders` with no limit is a defect even if it's fast today — it's a query whose cost grows with your most successful customer's data. Every collection endpoint takes a limit, and the client always sends one.

## Cursor vs offset

| | Offset (`?page=3`) | Cursor (`?after=<id>`) |
|---|---|---|
| Stable under inserts/deletes | ❌ rows shift — items get skipped or duplicated | ✅ |
| Deep-page cost | ❌ degrades (the database still scans what it skips) | ✅ constant |
| Jump to arbitrary page | ✅ | ❌ next/prev only |
| Total count available | ✅ | usually not |

**Default to cursor** for anything append-heavy, real-time, or deep — feeds, activity logs, messages, notifications. Use offset only when the user genuinely needs numbered pages *and* the dataset is small and stable enough that drift doesn't matter.

Offset pagination on a live feed is the classic source of "I saw the same post twice and missed one."

## Infinite scroll

- Trigger with `IntersectionObserver` on a sentinel element — never a `scroll` listener doing arithmetic on every frame.
- **Always pair it with a crawlable path.** Crawlers don't scroll, so content behind infinite scroll is invisible to search and AI answer engines unless real paginated URLs or a sitemap expose it (`seo-ai-seo.md`).
- Provide an explicit "Load more" fallback. Infinite scroll traps keyboard and screen-reader users who need to reach the footer (`accessibility.md`).
- Preserve scroll position on back-navigation, or the pattern is actively hostile.

## Virtualization

Use a maintained library (`@tanstack/react-virtual`, `react-window`) rather than hand-rolling.

Requirements that are easy to get wrong:
- **Reserve height.** Unknown row heights cause scrollbar jitter and CLS (`performance.md`). Measure dynamically or fix the row height.
- **Keep accessibility intact.** A virtualized list is still a `list`/`listbox`. Windowing breaks the implicit relationship between visible rows and the full set, so set `aria-setsize` and `aria-posinset` — otherwise a screen reader announces "3 of 12" for a list of 5,000.
- **Keyboard navigation must span the whole set**, not just rendered rows. Arrowing past the rendered window must scroll and render, not dead-end.
- **Ctrl/Cmd-F will not find unrendered rows.** If in-page search matters, provide your own filter — users will otherwise assume the data is missing.
- Stable `key` from the record id, never the index (`principles.md` §8) — index keys plus windowing produces visibly wrong rows.

## Interaction with the data layer

- Use the cache's own pagination merge (RTK Query `serializeQueryArgs` + `merge`, or `infiniteQuery`) rather than accumulating pages in component state — component state resets on unmount and desynchronizes from the cache (`state-data.md`).
- Normalize by entity id so a row updated elsewhere updates everywhere (`state-data.md`).
- The **empty** state is distinct from the loading state and from "end of list" (`principles.md` §6). Three different messages; "no results" and "you've reached the end" are not the same sentence.
- Preserve already-loaded pages during a background refetch — don't blank a list the user is reading.

## Review checklist

- [ ] No unbounded collection fetch
- [ ] Cursor pagination where the data is append-heavy or deep
- [ ] Virtualized past ~1,000 rows
- [ ] `aria-setsize` / `aria-posinset` on virtualized rows
- [ ] Keyboard reaches rows outside the rendered window
- [ ] Infinite scroll has a crawlable path and a non-scroll fallback
- [ ] Empty, loading, and end-of-list are three distinct states
