# Frontend Axiom — Core Principles

Read this before writing or reviewing any code in a Frontend Axiom project. These are non-negotiable defaults, not suggestions.

## 1. Never guess

If a requirement, data shape, design detail, or business rule is ambiguous — stop and ask the user. Never invent an API shape, never assume design intent, never silently pick a library or pattern that wasn't confirmed. Precision over speed. This applies to every skill in this plugin, especially `/init-project` and `/new-feature`.

## 2. SOLID, translated to frontend

- **Single Responsibility** — A component renders. A hook owns logic/state. A service/util fetches or transforms data. Never mix "fetch + transform + render" in one component.
- **Open/Closed** — Extend behavior via props, composition, or slots — not by editing a shared component's internals for every new call site.
- **Liskov Substitution** — Any component implementing a shared prop contract (`variant`, `as`, etc.) must be swappable for another implementing the same contract without breaking the parent.
- **Interface Segregation** — Don't force a component to accept a large props object it mostly ignores. Split props by concern only when it earns its keep — don't over-engineer a 2-prop component.
- **Dependency Inversion** — Components depend on hooks/interfaces (`useUser()`, `usePayments()`), never directly on `fetch`/`axios`/`localStorage`. The data layer underneath must be swappable.

## 3. The destructuring rule (hard rule)

Never chain property access (`user.name`, `data.user.email`). Destructure once, as close to the data's entry point as possible, with a default for every field:

```js
const { user = {}, isPremium = false } = dataObj;
const { name = "", email = "", skills = [] } = user;
```

Then use `name`, `email`, `skills` directly — never `user.name` again in that scope. Applies to function params, hook returns, API responses, and context values, at any nesting depth.

### Defaults must be referentially stable

Primitive defaults (`""`, `0`, `false`) are free. **Object and array defaults allocate a new value on every evaluation** — `const { skills = [] } = user` hands back a brand-new array every render where `user.skills` is undefined. If that value then reaches a `useEffect`/`useMemo`/`useCallback` dependency array, a `React.memo`'d child, or a context value, it silently defeats memoization and can cause infinite effect loops. Applied carelessly, this rule actively contradicts the referential-stability guidance in `react-nextjs.md`.

- Primitive default → inline, always.
- Object/array default that stays local to the render (read, mapped, never passed down or depended on) → inline is fine.
- Object/array default that reaches a dependency array, a memoized child, or a context value → hoist a module-level constant:
  ```js
  const EMPTY_SKILLS = [];               // module scope — one stable reference
  const { skills = EMPTY_SKILLS } = user;
  ```

### Narrow exceptions

Even these get destructured on the first line of the block rather than repeated inline:

1. Event handler signatures (`event.target.value`) — destructure immediately: `const { value } = event.target;`
2. Idiomatic third-party chains you don't control the shape of (`error.response.status` in a catch block)
3. Method/namespace calls that aren't data reads (`router.push(...)`, `array.map(...)`, `api.get(...)`) — this rule is about *data property access*, not calling functions
4. **Discriminated unions / tagged variants — do not destructure before narrowing.** TypeScript narrows a union by testing a discriminant on the *whole* object. Splitting the discriminant off (`const { type, payload } = action`) severs that correlation: narrowing `type` no longer narrows `payload`, and variants with differently-shaped payloads often won't compile when destructured together. Narrow first on the undestructured variable, then destructure *inside* the narrowed branch:
   ```ts
   switch (action.type) {
     case "success": {
       const { payload } = action; // correctly narrowed to the success variant
       return payload;
     }
   }
   ```
   This covers reducers, RTK Query result unions, and any `status`/`kind`/`type`-driven branching. The linter cannot detect narrowing — when it fires here, add an inline disable or put the base name in its `ignore` list.

### CI enforcement — and what it does *not* catch

`eslint-plugin-frontend-axiom` flags reaching into the same object for 2+ distinct properties. It tracks every hop of a chain (so `data.user.email` + `data.user.name` is reported against `data.user`) and resolves the root to its *variable*, so closures sharing a variable share a tally while same-named variables in different scopes stay separate.

It still can't see everything, and these are the gaps a reviewer must cover:
- A **single** deep read (`dataObj.user.email` used once) — each level sees only one property.
- **Type-driven exceptions** — it will fire on the discriminated-union case above, where destructuring is the wrong fix. Suppress deliberately.
- **Referential instability** — `const { skills = [] } = user` lints clean but allocates per render.

A green lint run is a useful signal, not proof of compliance. `/frontend-axiom:audit` is the real check.

## 4. Reuse without premature abstraction

Extract a shared component/hook/util on the **third** duplication, not the first. Two similar blocks are fine left as-is. Don't build a generic `<DataTable>` for one table, or a config-driven form system for two forms.

## 5. Small, composable units

Prefer many small components/hooks over one large one. A component file pushing past ~150 lines, or a hook handling more than one concern, is a signal to split.

## 6. Every data-fetching surface has 5 states

Any screen or section that fetches data must explicitly handle:
1. **Loading** (initial fetch)
2. **Success with data**
3. **Success but empty** (valid response, zero items — not the same UI as an error)
4. **Error** (network failure, 4xx/5xx, malformed response)
5. **Stale/refetching** (revalidating in the background — don't blank the UI)

Never assume the happy path is the only path. See `knowledge/state-data.md` for the RTK Query pattern that maps directly to these five states.

## 7. Ask, confirm, then build

At the start of any new project or feature: interview the user, offer real options (don't silently default), get explicit confirmation, then build. See `/init-project` and `/new-feature`. A wrong assumption caught after code is written costs far more than one clarifying question up front.

## 8. Folder & naming conventions

- Feature-first structure: colocate a feature's components, hooks, and API slice under one folder rather than splitting by file type globally (`components/`, `hooks/`, `services/` at the top level only for things truly shared across features).
- `PascalCase` for components and their files, `camelCase` for hooks/utils/functions, `useX` prefix mandatory for hooks.
- One default export per component file, named the same as the file.
- No barrel (`index.ts` re-export) files for large feature folders in App Router projects — they defeat tree-shaking and slow cold builds. Import directly from the source file.
- Import via a configured path alias (`@/components/...`) rather than relative `../../../` chains for anything outside the current feature folder — keeps imports stable across refactors and file moves.
