---
type: llm
weight: 1
---

The response must do BOTH of the following to pass.

**1. Flag the chained property access in `ProfileCard`.**
It must identify `props.user.name` / `props.user.email` as violating the project's destructuring convention, and show destructuring instead — something equivalent to:

```js
const { user = {} } = props;
const { name = "", email = "" } = user;
```

Extracting `user` once and then still writing `user.name` / `user.email` is NOT sufficient — the convention requires destructuring down to the leaf values.

**2. Must NOT tell the reducer to destructure the discriminated union before narrowing.**
`action` is a discriminated union. Destructuring `const { type, payload } = action` before the `switch` breaks TypeScript's narrowing (and wouldn't compile, since `payload` doesn't exist on the `failed` variant). The project documents this as an explicit exception to the destructuring rule.

Pass if the response either:
- leaves the reducer's `action.type` / `action.payload` access alone, or
- explicitly identifies it as an exception because destructuring would break narrowing, or
- recommends destructuring only *inside* a narrowed `case` branch (e.g. `const { payload } = action;` after `case "loaded":`).

**Fail** if the response recommends destructuring `action` at the top of the reducer or before the `switch`, or applies the destructuring rule to `action` without acknowledging the narrowing problem.

Graders should judge only these two points. Extra commentary (naming, typing `props`, etc.) is fine and neither earns nor loses credit.
