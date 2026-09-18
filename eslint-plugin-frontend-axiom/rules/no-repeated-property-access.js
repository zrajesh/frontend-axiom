"use strict";

/**
 * Flags 2+ dot-accessed properties on the same base identifier within one
 * function/program scope, where destructuring the base once is the
 * Frontend Axiom convention (see knowledge/principles.md #3).
 *
 * Heuristic, not a full data-flow analysis — see this plugin's README for
 * known false-positive/false-negative cases and the `ignore` option.
 */

const IGNORED_BASE_NAMES = new Set([
  "window",
  "document",
  "console",
  "process",
  "Math",
  "JSON",
  "Object",
  "Array",
  "Number",
  "String",
  "Boolean",
  "Symbol",
  "Promise",
  "Error",
  "Reflect",
  "Proxy",
  "module",
  "exports",
  "require",
  "global",
  "globalThis",
  "navigator",
  "location",
  "history",
]);

const SCOPE_VISITORS = [
  "Program",
  "FunctionDeclaration",
  "FunctionExpression",
  "ArrowFunctionExpression",
];

function isWriteOrCallTarget(node) {
  const { parent } = node;
  if (!parent) return false;
  if (parent.type === "AssignmentExpression" && parent.left === node) return true;
  if (parent.type === "UnaryExpression" && parent.operator === "delete") return true;
  if (parent.type === "CallExpression" && parent.callee === node) return true;
  return false;
}

module.exports = {
  meta: {
    type: "suggestion",
    docs: {
      description:
        "Require destructuring instead of accessing 2+ different properties of the same object via dot-chains in one scope.",
      recommended: false,
    },
    schema: [
      {
        type: "object",
        properties: {
          threshold: { type: "integer", minimum: 2 },
          ignore: { type: "array", items: { type: "string" } },
        },
        additionalProperties: false,
      },
    ],
    messages: {
      preferDestructure:
        "'{{base}}' is dot-accessed for {{count}} different properties ({{props}}) in this scope. Destructure once instead: const { {{props}} } = {{base}};",
    },
  },

  create(context) {
    const options = context.options[0] || {};
    const threshold = options.threshold || 2;
    const ignored = new Set([...IGNORED_BASE_NAMES, ...(options.ignore || [])]);

    const scopeStack = [];

    function pushScope() {
      scopeStack.push(new Map());
    }

    function popScopeAndReport() {
      const scope = scopeStack.pop();
      for (const [base, info] of scope.entries()) {
        if (info.props.size >= threshold) {
          context.report({
            node: info.nodes[0],
            messageId: "preferDestructure",
            data: {
              base,
              count: String(info.props.size),
              props: [...info.props].join(", "),
            },
          });
        }
      }
    }

    return {
      Program: pushScope,
      "Program:exit": popScopeAndReport,
      FunctionDeclaration: pushScope,
      "FunctionDeclaration:exit": popScopeAndReport,
      FunctionExpression: pushScope,
      "FunctionExpression:exit": popScopeAndReport,
      ArrowFunctionExpression: pushScope,
      "ArrowFunctionExpression:exit": popScopeAndReport,

      MemberExpression(node) {
        if (node.computed) return;
        if (node.object.type !== "Identifier") return;
        if (node.property.type !== "Identifier") return;

        const base = node.object.name;
        if (ignored.has(base)) return;
        if (isWriteOrCallTarget(node)) return;

        const scope = scopeStack[scopeStack.length - 1];
        if (!scope) return;

        if (!scope.has(base)) {
          scope.set(base, { props: new Set(), nodes: [] });
        }
        const info = scope.get(base);
        info.props.add(node.property.name);
        info.nodes.push(node);
      },
    };
  },
};
