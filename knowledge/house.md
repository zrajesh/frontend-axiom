# House decisions

Everything here is a choice, not a fact. A capable model derives the facts on its own — six ablations measured ~zero delta from telling it any of them. It cannot derive what *this team* picked, or what we tried and abandoned.

## Conventions

**Destructure to the leaf value, then use the bare variable.** Pulling the object out and still reading through it is not enough:

```js
const { user } = props; user.name          // still wrong
const { user = {} } = props;
const { name = "", email = "" } = user;    // correct — now use name, email
```

Two exceptions, both verified the hard way:

- **Discriminated unions:** narrow on the whole value first, destructure inside the branch. Destructuring first severs TypeScript's correlation between the discriminant and the payload, and often won't compile.
- **Referential stability:** an object/array default allocates a fresh value each render. If it can reach a dependency array, a memoized child, or a context value, hoist it to a module-level constant. Otherwise the convention quietly breaks memoization.

**Five states, every data surface:** loading · data · **empty** (visually distinct, not a blank list) · error (with retry) · refetching (never blank stale content).

**Extract on the third duplication, not the first.** Two similar blocks are fine.

**Feature-first folders.** Colocate a feature's components, hooks and API slice. Top-level `components/` only for what is genuinely shared. No barrel files — they defeat tree-shaking and slow cold builds.

## Thresholds

These numbers are ours. Change them deliberately, in one place.

| Thing | Limit |
|---|---|
| First-load JS — marketing / SEO route | ≤ 100 KB compressed |
| First-load JS — app route | ≤ 170 KB |
| First-load JS — heavy tooling route | ≤ 250 KB, justified in review |
| Cyclomatic complexity, per function | 15 |
| Function length | 80 lines |
| Nesting depth | 5 |
| Duplicated 5-line windows | 15% |
| Virtualize a list past | ~1,000 rows |

**Performance is measured on a mid-range Android over Fast 3G (4× CPU throttle), not a laptop.** A stress profile of 6× / Slow 3G for global reach. Unthrottled numbers are not evidence.

**Core Web Vitals:** LCP ≤ 2.5s · INP ≤ 200ms · CLS ≤ 0.1, measured on *field* data at p75. A green lab trace is a smoke test, nothing more.

## Testing

Coverage is risk-weighted, never a blanket percentage — a global target is satisfied by testing getters while payment logic goes untested.

| Code | Requirement |
|---|---|
| Auth, payments, permissions, mutations, money/date math | Exhaustive. Every branch, every error path. |
| Business logic, hooks, reducers, selectors | Thorough, including edge cases |
| Feature components | All five data states + primary interactions |
| Presentational / layout | Light, or none |

Mock at the network boundary (MSW), not by stubbing hooks. Tests ship in the same PR as the code.

## Non-negotiable

- **Auth tokens live in httpOnly + Secure + SameSite cookies.** Never `localStorage` or `sessionStorage`. Logout revokes server-side *and* purges the client cache, or the next user on a shared device reads the previous one's data.
- **No unbounded collection fetch.** Append-heavy data uses cursor, not offset pagination.
- **Third-party scripts that touch user data do not load before consent** — the network request itself is the violation, not the tracking.
- **Lint rules ship at `error`.** A rule that can only warn is decoration; promote once the count reaches zero and gate CI on it.
- **Look first, then ask.** Never invent an API shape or field name — but do not ask for what the repository already answers. Grep, read the types, check the inventory. Ask only for what is genuinely undiscoverable.

## Rejected alternatives

The highest-value section here, and the only one a model cannot reconstruct from the codebase — because a rejected approach leaves no trace in the code. "Use X" is derivable. "We tried X and it cost us Y" is not.

Record these with `/frontend-axiom:decide`, which stores them with their reasoning and surfaces them when relevant. Add entries as they come up:

- _(example)_ **Zustand for server state — rejected.** Two stores meant cache invalidation had no single owner; three stale-data bugs in a month. RTK Query for anything server-derived, Zustand only for ephemeral UI state.
- _(add yours)_

An entry is only worth writing if it includes what went wrong. A rule without its reason gets cargo-culted, and nobody can later judge whether it still applies.
