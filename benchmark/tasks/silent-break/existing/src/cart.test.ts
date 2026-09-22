import { describe, expect, test } from "vitest";
import { subtotal, applyDiscount, formatTotal } from "./cart";

describe("cart", () => {
  test("subtotal sums line items", () => {
    expect(subtotal([{ sku: "a", qty: 2, unitPrice: 5 }, { sku: "b", qty: 1, unitPrice: 3 }])).toBe(13);
  });
  test("subtotal of empty cart is 0", () => {
    expect(subtotal([])).toBe(0);
  });
  test("ten percent off two hundred", () => {
    expect(applyDiscount(200, 10)).toBe(180);
  });
  test("half off", () => {
    expect(applyDiscount(100, 50)).toBe(50);
  });
  test("a quarter off eighty", () => {
    expect(applyDiscount(80, 25)).toBe(60);
  });
  test("full discount leaves nothing", () => {
    expect(applyDiscount(45, 100)).toBe(0);
  });
  test("zero discount is a no-op", () => {
    expect(applyDiscount(200, 0)).toBe(200);
  });
  test("formatTotal renders two decimal places", () => {
    expect(formatTotal(13)).toBe("$13.00");
  });
});
