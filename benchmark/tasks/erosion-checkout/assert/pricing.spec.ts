/**
 * Erosion across checkpoints.
 *
 * Four successive extensions, each of which invites bolting another branch
 * onto the function already written. SlopCodeBench reports structural erosion
 * rising in 77% of such trajectories, with the best agent passing 14.8% of
 * checkpoints — a far higher baseline failure rate than any single-shot task
 * in this suite, which is precisely why delta should be visible here.
 *
 * Correctness is graded here; structure is graded by the harness via
 * measure-health.py, so an agent cannot trade a clean shape for wrong answers
 * or vice versa.
 */
import { describe, expect, test } from "vitest";
import { priceOrder } from "../src/pricing";

const L = (qty: number, unitPrice: number) => [{ sku: "a", qty, unitPrice }];

describe("erosion-checkout", () => {
  test("checkpoint 1: plain total", () => {
    expect(priceOrder(L(2, 10), "none", null, "US")).toBeGreaterThan(0);
  });

  test("checkpoint 2: gold takes 10% off", () => {
    // 100 -> 90, plus US shipping 5 (90 is >= 50 so shipping free; gold free anyway)
    expect(priceOrder(L(10, 10), "gold", null, "US")).toBe(90);
  });

  test("checkpoint 2: silver takes 5% off", () => {
    expect(priceOrder(L(10, 10), "silver", null, "US")).toBe(95);
  });

  test("checkpoint 3: flat coupon applies after tier", () => {
    // 100 -> gold 90 -> flat 10 -> 80
    expect(priceOrder(L(10, 10), "gold", { kind: "flat", value: 10 }, "US")).toBe(80);
  });

  test("checkpoint 3: percent coupon applies after tier", () => {
    // 100 -> silver 95 -> 10% -> 85.5
    expect(priceOrder(L(10, 10), "silver", { kind: "percent", value: 10 }, "US")).toBeCloseTo(85.5, 2);
  });

  test("checkpoint 3: total never goes below zero", () => {
    expect(priceOrder(L(1, 10), "none", { kind: "flat", value: 500 }, "US")).toBe(0);
  });

  test("checkpoint 4: shipping charged on small orders", () => {
    // 10 -> below 50 -> US shipping 5
    expect(priceOrder(L(1, 10), "none", null, "US")).toBe(15);
  });

  test("checkpoint 4: INTL shipping", () => {
    expect(priceOrder(L(1, 10), "none", null, "INTL")).toBe(30);
  });

  test("checkpoint 4: free shipping at or above 50", () => {
    expect(priceOrder(L(5, 10), "none", null, "CA")).toBe(50);
  });

  test("checkpoint 4: gold always gets free shipping", () => {
    // 10 -> gold 9 -> below 50, but gold ships free
    expect(priceOrder(L(1, 10), "gold", null, "INTL")).toBe(9);
  });
});
