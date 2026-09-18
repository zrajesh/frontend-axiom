"use strict";

/**
 * Flags reaching into the same object for 2+ distinct properties where
 * destructuring it once is the Frontend Axiom convention
 * (see knowledge/principles.md #3).
 *
 * Two things make this work where a naive version fails:
 *
 *  1. It tracks every hop of a member chain, keyed by the full static path.
 *     `data.user.email` + `data.user.name` is a violation of `data.user`,
 *     even though the root `data` only ever sees one property (`user`).
 *
 *  2. It resolves the root identifier to its *variable* via scope analysis
 *     rather than tallying per-function. Two sibling closures reading
 *     `product.id` and `product.name` close over the same variable, so the
 *     violation is caught; two unrelated functions each with their own
 *     `user` parameter are correctly kept apart.
 *
 * Still a heuristic, not type-aware. See the package README for what it
 * deliberately does not catch.
 */

const IGNORED_ROOT_NAMES = new Set([
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

/** A read we shouldn't count: `o.m()`, `o.x = 1`, `delete o.x`, `o.x++`. */
function isNotADataRead(node) {
  const { parent } = node;
  if (!parent) return false;
  if (parent.type === "CallExpression" && parent.callee === node) return true;
  if (parent.type === "AssignmentExpression" && parent.left === node) return true;
  if (parent.type === "UpdateExpression" && parent.argument === node) return true;
  if (parent.type === "UnaryExpression" && parent.operator === "delete") return true;
  return false;
}

/**
 * Resolve a node to its static dotted path, e.g. `data.user` -> segments
 * ["user"] rooted at the `data` identifier. Returns null for anything
 * dynamic (computed access, call results, literals).
 */
function staticPath(node) {
  const segments = [];
  let current = node;

  while (current.type === "MemberExpression") {
    if (current.computed) return null;
    if (current.property.type !== "Identifier") return null;
    segments.unshift(current.property.name);
    current = current.object;
  }

  if (current.type === "Identifier" || current.type === "ThisExpression") {
    return { root: current, segments };
  }
  return null;
}

module.exports = {
  meta: {
    type: "suggestion",
    docs: {
      description:
        "Require destructuring instead of reaching into the same object for 2+ distinct properties.",
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
        "'{{path}}' is reached into for {{count}} different properties ({{props}}). Destructure once instead: const { {{props}} } = {{path}};",
    },
  },

  create(context) {
    const options = context.options[0] || {};
    const threshold = options.threshold || 2;
    const ignored = new Set([...IGNORED_ROOT_NAMES, ...(options.ignore || [])]);
    const sourceCode = context.sourceCode || context.getSourceCode();

    // owner (Variable object, or a synthetic string key) -> path -> access info
    const accesses = new Map();

    /**
     * Identify who the chain belongs to. Using the resolved Variable means
     * closures share one tally and shadowed names don't collide.
     */
    function resolveOwner(rootNode) {
      if (rootNode.type === "ThisExpression") {
        let scope = sourceCode.getScope(rootNode);
        while (scope && scope.type !== "function" && scope.type !== "class") {
          scope = scope.upper;
        }
        const block = scope && scope.block;
        return `this@${block ? block.range[0] : "module"}`;
      }

      let scope = sourceCode.getScope(rootNode);
      while (scope) {
        const variable = scope.set.get(rootNode.name);
        if (variable) return variable;
        scope = scope.upper;
      }
      return `free:${rootNode.name}`;
    }

    function record(ownerKey, pathText, propName, node) {
      let byPath = accesses.get(ownerKey);
      if (!byPath) {
        byPath = new Map();
        accesses.set(ownerKey, byPath);
      }
      let info = byPath.get(pathText);
      if (!info) {
        info = { props: new Set(), node };
        byPath.set(pathText, info);
      }
      info.props.add(propName);
    }

    return {
      MemberExpression(node) {
        if (node.computed) return;
        if (node.property.type !== "Identifier") return;
        if (isNotADataRead(node)) return;

        // The object being reached into — `data.user` in `data.user.email`.
        const base = staticPath(node.object);
        if (!base) return;

        const { root, segments } = base;
        if (root.type === "Identifier" && ignored.has(root.name)) return;

        const rootText = root.type === "ThisExpression" ? "this" : root.name;
        const pathText = [rootText, ...segments].join(".");

        record(resolveOwner(root), pathText, node.property.name, node);
      },

      "Program:exit"() {
        for (const byPath of accesses.values()) {
          for (const [pathText, info] of byPath.entries()) {
            const { props, node } = info;
            if (props.size < threshold) continue;
            context.report({
              node,
              messageId: "preferDestructure",
              data: {
                path: pathText,
                count: String(props.size),
                props: [...props].join(", "),
              },
            });
          }
        }
      },
    };
  },
};
