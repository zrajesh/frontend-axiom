/**
 * Measures REUSE, which single-file tasks cannot.
 *
 * The repo already has Modal, Button and a cancelOrder() API function. A
 * senior engineer composes those. The common agent failure is to write a
 * fresh dialog with a raw <button> and a hand-rolled fetch — code that works
 * in isolation and quietly forks the design system.
 */
import { describe, expect, test, vi, beforeEach } from "vitest";
import { render, cleanup, screen } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import CancelOrderDialog from "../src/CancelOrderDialog";

const SRC = readFileSync(join(__dirname, "../src/CancelOrderDialog.tsx"), "utf8");
const base = { orderId: "ord_1", isOpen: true, onClose: () => {} };

describe("reuse-existing", () => {
  beforeEach(() => { cleanup(); vi.restoreAllMocks(); });

  test("reuses the existing Modal instead of hand-rolling a dialog", () => {
    expect(/from\s+["'].*components\/Modal["']/.test(SRC)).toBe(true);
  });

  test("reuses the existing Button instead of raw <button>", () => {
    expect(/from\s+["'].*components\/Button["']/.test(SRC)).toBe(true);
  });

  test("calls the existing cancelOrder() API, not a hand-written fetch", () => {
    expect(/from\s+["'].*api\/orders["']/.test(SRC)).toBe(true);
    expect(/cancelOrder/.test(SRC)).toBe(true);
  });

  test("does not re-implement the network call inline", () => {
    // A raw fetch to the orders endpoint means it ignored the existing module.
    expect(/fetch\(\s*[`'"]\/orders/.test(SRC)).toBe(false);
  });

  test("renders a confirm affordance when open", () => {
    const { container } = render(<CancelOrderDialog {...base} />);
    const text = (container.textContent || "").toLowerCase();
    expect(/cancel|confirm|sure|yes/.test(text)).toBe(true);
  });

  test("renders nothing when closed", () => {
    const { container } = render(<CancelOrderDialog {...base} isOpen={false} />);
    expect((container.textContent || "").trim()).toBe("");
  });
});
