"use strict";

const { RuleTester } = require("eslint");
const rule = require("../rules/no-repeated-property-access");

const ruleTester = new RuleTester({
  languageOptions: { ecmaVersion: 2022, sourceType: "module" },
});

ruleTester.run("no-repeated-property-access", rule, {
  valid: [
    // Already destructured — the pattern we want.
    `function greet(user) {
       const { name = "", email = "" } = user;
       return name + email;
     }`,
    // Same property read twice is not 2 *distinct* properties.
    `function greet(user) { return user.name + "-" + user.name; }`,
    // Ignored globals/namespaces.
    `function log() {
       console.log(window.location);
       console.error(process.env);
     }`,
    // Call targets are invocations, not data reads.
    `function go(api, router) { api.get("/x").then(() => router.push("/y")); }`,
    // Assignment / update / delete targets are writes, not reads.
    `function set(obj) { obj.a = 1; obj.b = 2; }`,
    `function bump(obj) { obj.count++; delete obj.tmp; }`,
    // Computed access is out of scope for this heuristic.
    `function pick(obj, k1, k2) { return obj[k1] + obj[k2]; }`,
    // Explicit ignore option suppresses a known-noisy base.
    {
      code: `function styled(theme) { return theme.colors + theme.spacing; }`,
      options: [{ ignore: ["theme"] }],
    },
    // Distinct variables that merely share a name must NOT be merged.
    `function a(user) { return user.name; }
     function b(user) { return user.email; }`,
    // Shadowing: the inner `user` is a different variable from the outer one.
    `function outer(user) {
       return user.name + [1].map((user) => user.email).join("");
     }`,
    // A single deep read is not (yet) flagged — each level sees one property.
    // Documented in the package README as a known limitation.
    `function f(dataObj) { return dataObj.user.email; }`,
  ],

  invalid: [
    {
      code: `function greet(user) { return user.name + user.email; }`,
      errors: [{ messageId: "preferDestructure" }],
    },
    {
      // The exact anti-pattern from knowledge/principles.md §3.
      code: `function render(dataObj) { return dataObj.user + dataObj.isPremium; }`,
      errors: [{ messageId: "preferDestructure" }],
    },
    {
      // Threshold is configurable upward.
      code: `function wide(o) { return o.a + o.b + o.c; }`,
      options: [{ threshold: 3 }],
      errors: [{ messageId: "preferDestructure" }],
    },

    // --- Regression tests for the v0.1 false negatives ---

    {
      // Multi-hop: the violation is on `data.user`, not on `data`.
      code: `function f(data) { return data.user.email + data.user.name; }`,
      errors: [
        {
          messageId: "preferDestructure",
          data: { path: "data.user", count: "2", props: "email, name" },
        },
      ],
    },
    {
      // Deep chains at the second level and beyond.
      code: `function f(res) { return res.data.user.id + res.data.user.role; }`,
      errors: [
        {
          messageId: "preferDestructure",
          data: { path: "res.data.user", count: "2", props: "id, role" },
        },
      ],
    },
    {
      // `this` is now tracked, scoped to its enclosing function/class.
      code: `class C { render() { return this.props.a + this.props.b; } }`,
      errors: [
        {
          messageId: "preferDestructure",
          data: { path: "this.props", count: "2", props: "a, b" },
        },
      ],
    },
    {
      // Sibling closures over the same variable — a very common React shape.
      code: `function ProductRow({ product }) {
               const onClick = () => track(product.id);
               const onHover = () => track(product.name);
               return [onClick, onHover];
             }`,
      errors: [
        {
          messageId: "preferDestructure",
          data: { path: "product", count: "2", props: "id, name" },
        },
      ],
    },
    {
      // A violation split across a nested function still resolves to one variable.
      code: `function Card(user) {
               const label = user.name;
               return () => user.email + label;
             }`,
      errors: [{ messageId: "preferDestructure" }],
    },
  ],
});

console.log("✔ no-repeated-property-access: all RuleTester cases passed");
