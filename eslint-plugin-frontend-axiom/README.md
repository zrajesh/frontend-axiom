# eslint-plugin-frontend-axiom

Enforces the Frontend Axiom destructuring convention (`knowledge/primer/principles.md` §3) in CI, not just by agent convention.

## Rules

### `frontend-axiom/no-repeated-property-access`

Flags when the same base identifier has 2+ *different* properties dot-accessed by read within one function/program scope, e.g.:

```js
// flagged: 'user' accessed for 2 different properties
function greet(user) {
  return `Hi ${user.name}, your email is ${user.email}`;
}

// fixed
function greet(user) {
  const { name = "", email = "" } = user;
  return `Hi ${name}, your email is ${email}`;
}
```

## What it deliberately ignores

This is a heuristic, not a data-flow/type analysis. It skips:
- Computed access (`obj[x]`)
- Assignment targets (`obj.x = 1`) and `delete obj.x`
- The callee of a call expression (`api.get(...)`, `router.push(...)`, `array.map(...)`) — those are invocations, not data reads
- A fixed ignore-list of common globals/namespaces (`window`, `document`, `process`, `Math`, `console`, etc.) plus anything you add via the `ignore` option

## What it will still false-positive on

- A single property accessed twice (e.g. `user.name` read twice) won't trigger — only 2+ *distinct* properties do — but a legitimate pattern like `theme.colors.primary` used alongside `theme.spacing.md` will trigger on `theme`, even though destructuring nested design-token objects isn't always cleaner. Use `// eslint-disable-next-line frontend-axiom/no-repeated-property-access` or add the base name to `ignore` for cases like this.
- Fluent/builder-style chains that happen to read two properties before calling something.
- Discriminated unions read after a narrowing check (`switch (action.type)` then `action.payload` per branch). Destructuring there is the *wrong* fix — it breaks TypeScript narrowing. See `knowledge/primer/principles.md` §3 exception 4; suppress with an inline disable or the `ignore` option.

## Coverage

| Pattern | Caught | Reported against |
|---|---|---|
| `user.name + user.email` | ✅ | `user` |
| `data.user.email + data.user.name` | ✅ | `data.user` — the level actually reached into twice |
| `res.data.user.id + res.data.user.role` | ✅ | `res.data.user` |
| `this.props.a + this.props.b` | ✅ | `this.props`, scoped to its enclosing function/class |
| `product.id` / `product.name` in two sibling closures | ✅ | `product` — closures share the variable, so the tally is shared |
| Two different variables that happen to share a name | ✅ not flagged | Resolved per-variable, so they're never conflated |

v0.1 missed the middle four. They're covered now because the rule tracks **every hop of a chain keyed by its full static path**, and resolves the root identifier to its **variable via scope analysis** rather than tallying per-function. Each is a regression test in `tests/`.

## Known limitations

- **A single deep read isn't flagged.** `dataObj.user.email` appearing exactly once sees one property at each level, so nothing crosses the threshold. The rule targets *repeated* reaching-in; a lone deep read is left to review.
- **Not type-aware.** It can't tell a discriminated union from an ordinary object, so it will fire on `action.type` + `action.payload` in a narrowing `switch` — where destructuring is the *wrong* fix because it breaks TypeScript narrowing (`knowledge/primer/principles.md` §3, exception 4). Suppress with an inline disable or the `ignore` option.
- **Nested design-token objects** (`theme.colors` + `theme.spacing`) are flagged even though destructuring them isn't always clearer. Add the base name to `ignore`.
- **Referential instability is invisible to it.** `const { skills = [] } = user` passes lint but allocates a fresh array each render. That's a review concern, not a lint one.

So: it's a real backstop for the common shapes now, not a token one — but `/frontend-axiom:audit` is still the enforcement mechanism, not a green lint run.

## Install

Not published to npm. Install it straight from the plugin directory — inside a Claude Code session the plugin root is available as `$CLAUDE_PLUGIN_ROOT`:

```bash
npm install --save-dev "file:$CLAUDE_PLUGIN_ROOT/eslint-plugin-frontend-axiom"
```

## Usage — ESLint 9+ flat config (`eslint.config.js`)

```js
const frontendAxiom = require("eslint-plugin-frontend-axiom");

module.exports = [
  frontendAxiom.configs.recommended,
  // or wire the rule yourself:
  // {
  //   plugins: { "frontend-axiom": frontendAxiom },
  //   rules: {
  //     "frontend-axiom/no-repeated-property-access": ["warn", { threshold: 2, ignore: ["theme"] }],
  //   },
  // },
];
```

## Usage — legacy eslintrc (`.eslintrc.cjs`)

```js
module.exports = {
  plugins: ["frontend-axiom"],
  extends: ["plugin:frontend-axiom/legacy-recommended"],
};
```

Note the different config name: `recommended` is the flat config (an object with a `plugins` **map**), `legacy-recommended` is the eslintrc one (a `plugins` **array**). The two formats are not interchangeable — using `recommended` from an `.eslintrc` file, or `legacy-recommended` from a flat config, will fail to load.

`/frontend-axiom:init-project` wires the right one in automatically based on which config style the project uses.

## Tests

```bash
npm test
```

Runs the rule against ESLint's official `RuleTester` (8 valid + 3 invalid cases), covering the ignore-list, call/assignment exclusions, computed access, per-scope budgets, the `ignore` and `threshold` options, and the exact anti-pattern from `knowledge/primer/principles.md` §3.

## Status

v0.3. Rule logic is covered by a 20-case `RuleTester` suite (including regression tests for every false negative found in v0.1) and verified end-to-end through the `eslint` CLI in a real ESLint 9 flat-config project.

`configs.recommended` ships the rule at **`error`**. It previously shipped at `"warn"`, which meant `scripts/verify.sh` — which fails on `errorCount` — could never enforce the one convention this plugin measurably adds. Adopting on an existing codebase? Override to `"warn"` locally with an owner and a removal date, rather than weakening the shipped default for everyone.

It remains a **heuristic**, not type-aware analysis. Tune `ignore`/`threshold` against your codebase.
