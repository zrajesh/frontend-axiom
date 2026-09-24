# State & Data Management Standards

## Local vs global state decision tree

1. Does only one component (and its direct children via props) need it? → `useState`/`useReducer` locally.
2. Is it server data (fetched from an API)? → RTK Query. Never mirror server data into local/global client state by hand — that's a cache you now have to invalidate manually.
3. Is it client-only UI state shared across distant components (theme, sidebar open/closed, current modal)? → Zustand (lighter) or a Redux slice if the project already runs RTK Query (keeps one mental model/devtools).
4. Is it derived from other state? → a memoized selector, never its own stored state (avoid state that can go out of sync with its source).

## RTK Query patterns

- One API slice per backend domain (`usersApi`, `ordersApi`), not one giant slice for the whole app.
- Tag-based cache invalidation (`providesTags` / `invalidatesTags`) — mutations invalidate exactly the tags they affect, not a blanket refetch-everything.
- Map every query's states to the 5-state rule in `principles.md`:
  - `isLoading` → initial loading UI
  - `data && data.length > 0` (or equivalent) → success-with-data UI
  - `data && data.length === 0` → explicit empty state UI (not the same component as loading or error)
  - `isError` → error UI with retry
  - `isFetching && data` → stale-while-refetching indicator (don't unmount the existing content)
- Optimistic updates via `onQueryStarted` + `updateQueryData` for mutations where latency would otherwise hurt UX (likes, toggles, reorders) — always with rollback on failure.
- Tune `keepUnusedDataFor` per endpoint (default 60s) — how long unused cached data survives after the last subscriber unmounts. Raise it for expensive/rarely-changing queries, lower it for data that goes stale fast.
- Polling (`pollingInterval`) only where genuinely needed (live dashboards) — prefer refetch-on-focus/reconnect (`refetchOnFocus`, `refetchOnReconnect`) as the default freshness strategy, it's cheaper.

## Normalization

Store collections keyed by id rather than nested/duplicated objects — RTK's `createEntityAdapter` gives you this shape for free:

```js
{
  ids: [1, 2],
  entities: {
    1: { id: 1, name: "Alice", postIds: [101, 102] },
    2: { id: 2, name: "Bob", postIds: [103] },
  },
}
```

Why: `entities[id]` is an O(1) lookup instead of scanning an array. An entity referenced from more than one place (a post shown in both a feed and a profile) exists in exactly one place, so updating it updates everywhere it's used. Deeply nested relationships (`user.posts[].comments[].author`) get flattened into separate collections linked by id instead of duplicated inline. Do this for any collection where the same entity can be read or updated from more than one screen/component.

## Selectors

- Memoize derived/computed reads with `createSelector` (reselect, built into RTK) so components don't recompute or re-render on unrelated state changes.

## Server state vs UI state — keep them separate

Never put server-fetched data and its loading/error flags in the same slice as unrelated UI state (e.g. a modal's open flag). Mixing them causes unrelated re-renders and makes the cache harder to reason about.
