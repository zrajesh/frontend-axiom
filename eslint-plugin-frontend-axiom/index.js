"use strict";

const noRepeatedPropertyAccess = require("./rules/no-repeated-property-access");

const RULES = {
  "frontend-axiom/no-repeated-property-access": "warn",
  "prefer-destructuring": [
    "warn",
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
