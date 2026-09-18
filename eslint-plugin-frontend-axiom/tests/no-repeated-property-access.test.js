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
    // Assignment targets are writes, not reads.
    `function set(obj) { obj.a = 1; obj.b = 2; }`,
    // Computed access is out of scope for this heuristic.
    `function pick(obj, k1, k2) { return obj[k1] + obj[k2]; }`,
    // Explicit ignore option suppresses a known-noisy base.
    {
      code: `function styled(theme) { return theme.colors + theme.spacing; }`,
      options: [{ ignore: ["theme"] }],
    },
    // Separate scopes each get their own budget.
    `function a(user) { return user.name; }
     function b(user) { return user.email; }`,
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
  ],
});

console.log("✔ no-repeated-property-access: all RuleTester cases passed");
