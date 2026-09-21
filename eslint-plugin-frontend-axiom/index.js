"use strict";

const noRepeatedPropertyAccess = require("./rules/no-repeated-property-access");

const RULES = {
  // "error", not "warn". This is the one convention the benchmark measured as
  // genuinely differentiated, and verify.sh fails only on errorCount — at
  // "warn" the plugin's own gate could never enforce its own headline rule.
  // knowledge/release-operations.md forbids a permanently-warning rule.
  "frontend-axiom/no-repeated-property-access": "error",
  "prefer-destructuring": [
    "error",
    {
      VariableDeclarator: { array: false, object: true },
      AssignmentExpression: { array: false, object: false },
    },
    { enforceForRenamedProperties: false },
  ],
};

const plugin = {
  meta: {
    name: "eslint-plugin-frontend-axiom",
    version: "0.2.0",
  },
  rules: {
    "no-repeated-property-access": noRepeatedPropertyAccess,
  },
};

plugin.configs = {
  // ESLint 9+ flat config (eslint.config.js):
  //   const frontendAxiom = require("eslint-plugin-frontend-axiom");
  //   module.exports = [frontendAxiom.configs.recommended];
  recommended: {
    name: "frontend-axiom/recommended",
    plugins: { "frontend-axiom": plugin },
    rules: RULES,
  },

  // Legacy eslintrc (.eslintrc.cjs):
  //   extends: ["plugin:frontend-axiom/legacy-recommended"]
  "legacy-recommended": {
    plugins: ["frontend-axiom"],
    rules: RULES,
  },
};

module.exports = plugin;
