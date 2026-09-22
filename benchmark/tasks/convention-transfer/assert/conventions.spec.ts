/**
 * Does an arbitrary house convention transfer to new code?
 *
 * Five ablations found ~zero delta on anything a capable model can derive.
 * The one that measured +1.00 was an arbitrary convention — unguessable by
 * construction. This tests whether that generalises: the extractor infers a
 * repo's own rules, and this asks whether a new file then follows them.
 *
 * Every convention here is deliberately COUNTER-DEFAULT, because a rule the
 * model would follow anyway cannot show delta:
 *   - kebab-case filenames      (models default to PascalCase for components)
 *   - named exports             (models often reach for export default)
 *   - `interface` for props     (vs a type alias)
 *   - relative imports          (despite an @/ alias being configured in
 *                                tsconfig — using it would be the natural move)
 *
 * The component's own correctness is not graded. This measures conformity
 * only, which is the thing under test.
 */
import { describe, expect, test } from "vitest";
import { readdirSync, readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const DIR = join(__dirname, "../src/components");

function newFile(): { name: string; src: string } | null {
  if (!existsSync(DIR)) return null;
  const known = new Set([
    "user-badge-row","status-chip","avatar-stack","inline-note","meta-line",
    "count-pill","divider-rule","label-tag","hint-text","icon-slot",
    "tone-dot","stack-row",
  ]);
  for (const f of readdirSync(DIR)) {
    const stem = f.replace(/\.(tsx|jsx|ts|js)$/, "");
    if (!known.has(stem)) return { name: f, src: readFileSync(join(DIR, f), "utf8") };
  }
  return null;
}

describe("convention-transfer", () => {
  test("the component was created alongside the others", () => {
    expect(newFile()).not.toBeNull();
  });

  test("filename follows kebab-case, not PascalCase", () => {
    const f = newFile();
    expect(f).not.toBeNull();
    expect(/^[a-z0-9]+(-[a-z0-9]+)+\.(tsx|jsx)$/.test(f!.name)).toBe(true);
  });

  test("uses a named export, not a default export", () => {
    const f = newFile();
    expect(/export\s+function\s+PriceTag\b|export\s+const\s+PriceTag\b/.test(f?.src || "")).toBe(true);
    expect(/export\s+default/.test(f?.src || "")).toBe(false);
  });

  test("declares props with `interface`, not a type alias", () => {
    const f = newFile();
    expect(/interface\s+\w*Props\b/.test(f?.src || "")).toBe(true);
    expect(/type\s+\w*Props\s*=/.test(f?.src || "")).toBe(false);
  });

  test("imports relatively, not via the configured @/ alias", () => {
    const f = newFile();
    const src = f?.src || "";
    expect(/from\s+["']\.\.?\//.test(src)).toBe(true);
    expect(/from\s+["']@\//.test(src)).toBe(false);
  });
});
