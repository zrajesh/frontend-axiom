/**
 * Executable assertions for the orders-list task.
 *
 * These are the graders. No LLM judges whether the answer "sounds right" —
 * the component is rendered and interrogated. Each `test` is one point.
 *
 * Written against the props contract handed to the agent, so it makes no
 * assumption about internal structure: any correct implementation passes.
 */
import { describe, expect, test, vi } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { axe } from "vitest-axe";
import OrdersList from "../src/OrdersList";

const ORDERS = [
  { id: "1", reference: "ORD-1001", total: 42.5 },
  { id: "2", reference: "ORD-1002", total: 17.0 },
];

const base = {
  isLoading: false,
  isError: false,
  isFetching: false,
  orders: [] as typeof ORDERS,
  onRetry: () => {},
};

const visibleText = (el: HTMLElement) => (el.textContent || "").replace(/\s+/g, " ").trim();

describe("orders-list", () => {
  test("renders the orders when data is present", () => {
    cleanup();
    const { container } = render(<OrdersList {...base} orders={ORDERS} />);
    expect(visibleText(container)).toContain("ORD-1001");
    expect(visibleText(container)).toContain("ORD-1002");
  });

  test("shows a loading state while loading", () => {
    cleanup();
    const { container } = render(<OrdersList {...base} isLoading />);
    const text = visibleText(container).toLowerCase();
    const hasBusy =
      container.querySelector('[aria-busy="true"], [role="status"], [role="progressbar"]') !== null;
    expect(hasBusy || /load|fetch|spinner|skeleton|wait/.test(text)).toBe(true);
  });

  test("EMPTY STATE: renders a distinct message for zero orders, not a blank region", () => {
    cleanup();
    const { container } = render(<OrdersList {...base} orders={[]} />);
    const text = visibleText(container);
    // The discriminator. A blank <ul/> is the common wrong answer.
    expect(text.length).toBeGreaterThan(0);
    expect(/no orders|nothing|empty|don't have|do not have|haven't|yet/i.test(text)).toBe(true);
  });

  test("empty state is not the same output as the loading state", () => {
    cleanup();
    const { container: empty } = render(<OrdersList {...base} orders={[]} />);
    const emptyText = visibleText(empty);
    cleanup();
    const { container: loading } = render(<OrdersList {...base} isLoading />);
    const loadingText = visibleText(loading);
    expect(emptyText).not.toBe(loadingText);
  });

  test("shows an error state with a working retry", async () => {
    cleanup();
    const onRetry = vi.fn();
    const { container } = render(<OrdersList {...base} isError onRetry={onRetry} />);
    const text = visibleText(container).toLowerCase();
    expect(/error|failed|went wrong|couldn't|could not|try again|retry/.test(text)).toBe(true);

    const retry = container.querySelector("button");
    expect(retry, "an error state should offer a retry control").not.toBeNull();
    retry!.click();
    expect(onRetry).toHaveBeenCalled();
  });

  test("REFETCHING: keeps existing rows visible while refetching", () => {
    cleanup();
    const { container } = render(<OrdersList {...base} orders={ORDERS} isFetching />);
    // Stale-while-revalidate: never blank content the user is already reading.
    expect(visibleText(container)).toContain("ORD-1001");
  });

  test("has no accessibility violations with data", async () => {
    cleanup();
    const { container } = render(<OrdersList {...base} orders={ORDERS} />);
    const results = await axe(container);
    const violations = (results as unknown as { violations: unknown[] }).violations;
    expect(violations).toHaveLength(0);
  });
});
