# React / Next.js Standards

## Server vs Client Components (App Router default)

| Use a Server Component when... | Use a Client Component (`"use client"`) when... |
|---|---|
| Fetching data directly (DB/API) | Using state (`useState`, `useReducer`) |
| No interactivity needed | Using effects/browser APIs |
| Rendering static or per-request content | Handling events (`onClick`, `onChange`) |
| Keeping JS out of the client bundle | Using context that requires a client provider |

Default to Server Components. Push `"use client"` as far down the tree as possible — wrap only the interactive leaf, not the whole page.

## Rendering strategy decision table

| Strategy | When |
|---|---|
| **SSG** (static, build-time) | Content same for all users, changes rarely (marketing pages, docs) |
| **ISR** (`revalidate: N`) | Content changes periodically, staleness of N seconds is acceptable (product listings, blog) |
| **SSR** (per-request) | Content is per-user or must be fresh every request (dashboards, personalized pages), and SEO/first-paint matters |
| **CSR** (client-fetched) | Behind auth, no SEO requirement, highly interactive (internal tools, settings panels) |

Rule of thumb: if it needs to be indexed or needs a fast first paint, it should not be pure CSR. If it's user-specific and behind auth, SSR for the shell + client fetch for live data is usually right.

## Data fetching

- Server Components: `fetch()` directly, with Next's `cache`/`revalidate` options — no client library needed.
- Client Components: RTK Query (see `state-data.md`) for anything cached, deduped, or shared across components. Don't hand-roll `useEffect` + `fetch` + `useState` for data — it re-implements caching/race-condition handling RTK Query already solves.
- Never fetch in a `useEffect` on mount if the data is knowable at request time on the server — that's a waterfall (blank page → JS loads → fetch → render).

## Hooks

- One concern per custom hook. `useUserProfile()` fetches+shapes user data; it does not also manage a modal's open state.
- Rules of Hooks are non-negotiable: no conditional/loop-wrapped hook calls.
- `useMemo`/`useCallback` are for measured cost (expensive computation, or referential stability required by a memoized child/dependency array) — not a default wrapper on every value/function. Adding them without a reason adds complexity and a footgun (stale closures) for zero benefit.
- `React.memo` on a component only when it re-renders often with unchanged props and the render itself is non-trivial.

## Suspense, streaming, error boundaries

- Use `loading.tsx` / `<Suspense>` boundaries around slow data segments so the shell paints immediately (streaming SSR) instead of blocking the whole route.
- Use `error.tsx` (route-level) and local error boundaries around risky client widgets so one failing component doesn't blank the page.

## Forms

- Prefer uncontrolled inputs + a form library (React Hook Form) over controlled state-per-keystroke for anything beyond 2-3 fields — fewer re-renders, less boilerplate.
- Validate with a schema (zod) shared between client-side validation and server-side re-validation — never trust client validation alone (see `security.md`).

## Keys

- `key` must be a stable, unique id from the data — never array index for lists that can reorder/filter/insert.

## Image / Font / Script

- Always `next/image` for images (auto AVIF/WebP, responsive `sizes`, lazy-loading below the fold, `priority` only on the LCP image).
- Always `next/font` for web fonts (self-hosted, zero layout-shift font loading) — never a render-blocking `<link>` to a font CDN.
- Third-party scripts via `next/script` with the correct `strategy` (`beforeInteractive` only for truly critical scripts, `afterInteractive` default, `lazyOnload` for anything non-essential like chat widgets/analytics).
