# eslint-plugin-frontend-axiom

Enforces the Frontend Axiom destructuring convention (`knowledge/principles.md` §3) in CI, not just by agent convention.

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

Runs the rule against ESLint's official `RuleTester` (8 valid + 3 invalid cases), covering the ignore-list, call/assignment exclusions, computed access, per-scope budgets, the `ignore` and `threshold` options, and the exact anti-pattern from `knowledge/principles.md` §3.

## Status

v0.1. Rule logic is covered by the `RuleTester` suite above and verified end-to-end through the `eslint` CLI in a real ESLint 9 flat-config project. It is still a **heuristic**, not data-flow analysis — start it at `"warn"` and tune `ignore`/`threshold` against your codebase before promoting it to `"error"` in CI.
