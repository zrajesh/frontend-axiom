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

**Narrow exceptions**, and even these get destructured on the first line of the block rather than repeated inline:
- Event handler signatures (`event.target.value`) — destructure immediately: `const { value } = event.target;`
- Idiomatic third-party chains you don't control the shape of (`error.response.status` in a catch block)
- Method/namespace calls that aren't data reads (`router.push(...)`, `array.map(...)`, `api.get(...)`) — this rule is about *data property access*, not calling functions

CI enforcement: `eslint-plugin-frontend-axiom` flags 2+ dot-accessed properties on the same base identifier within one scope. It's a heuristic, not a perfect parser of intent — see that package's README.

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
