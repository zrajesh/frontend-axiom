/**
 * Reuse at scale.
 *
 * The 3-file version of this task measured 0.00 on a capable model: with only
 * Modal and Button present they were impossible to miss. Here the pieces that
 * must be reused are two of 33 UI components, deliberately named so they
 * cannot be guessed — `Overlay`, not `Modal`; `ActionButton`, not `Button` —
 * and surrounded by dialog-shaped decoys (Drawer, Sheet, Popover, Tooltip).
 *
 * Finding them requires actually reading the codebase. That is the condition
 * real projects have and small fixtures never do.
 */
import { describe, expect, test, vi, beforeEach } from "vitest";
import { render, cleanup } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import CancelOrderDialog from "../src/CancelOrderDialog";

const SRC = readFileSync(join(__dirname, "../src/CancelOrderDialog.tsx"), "utf8");
const base = { orderId: "ord_1", isOpen: true, onClose: () => {} };

describe("reuse-at-scale", () => {
  beforeEach(() => { cleanup(); vi.restoreAllMocks(); });

  test("reuses the existing Overlay rather than hand-rolling a dialog", () => {
    expect(/from\s+["'][^"']*ui\/Overlay["']/.test(SRC)).toBe(true);
  });

  test("reuses the existing ActionButton rather than a raw <button>", () => {
    expect(/from\s+["'][^"']*ui\/ActionButton["']/.test(SRC)).toBe(true);
  });

  test("calls the existing cancelOrder() rather than writing its own fetch", () => {
    expect(/from\s+["'][^"']*api\/orders["']/.test(SRC)).toBe(true);
    expect(/cancelOrder/.test(SRC)).toBe(true);
  });

  test("does not re-implement the network call inline", () => {
    expect(/fetch\(\s*[`'"]\/orders/.test(SRC)).toBe(false);
  });

  test("did not pick a decoy component instead", () => {
    // Drawer/Sheet/Popover/Tooltip are the wrong answers a shallow search finds.
    expect(/ui\/(Drawer|Sheet|Popover|Tooltip)/.test(SRC)).toBe(false);
  });

  test("renders a confirm affordance when open", () => {
    const { container } = render(<CancelOrderDialog {...base} />);
    expect(/cancel|confirm|sure|yes/i.test(container.textContent || "")).toBe(true);
  });

  test("renders nothing when closed", () => {
    const { container } = render(<CancelOrderDialog {...base} isOpen={false} />);
    expect((container.textContent || "").trim()).toBe("");
  });
});
