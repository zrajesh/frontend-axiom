import { describe, expect, test } from "vitest";
import { render, cleanup } from "@testing-library/react";
import { axe } from "vitest-axe";
import BigList from "../src/BigList";

const rows = Array.from({ length: 10000 }, (_, i) => ({ id: String(i), label: `Entry ${i}` }));

describe("big-list", () => {
  test("renders without crashing on 10k rows", () => {
    cleanup();
    const { container } = render(<BigList rows={rows} />);
    expect(container).toBeTruthy();
  });

  test("VIRTUALIZES: does not put all 10k rows in the DOM", () => {
    cleanup();
    const { container } = render(<BigList rows={rows} />);
    const n = container.querySelectorAll("*").length;
    // A plain .map() yields >=10000 nodes and freezes real browsers.
    expect(n).toBeLessThan(400);
  });

  test("still shows the first rows to the user", () => {
    cleanup();
    const { container } = render(<BigList rows={rows} />);
    expect((container.textContent || "")).toContain("Entry 0");
  });

  test("scroll container is keyboard reachable", () => {
    cleanup();
    const { container } = render(<BigList rows={rows} />);
    const focusable = container.querySelectorAll(
      '[tabindex], a, button, [role="listbox"], [role="grid"], [role="list"], ul, ol'
    );
    expect(focusable.length).toBeGreaterThan(0);
  });

  test("no accessibility violations", async () => {
    cleanup();
    const { container } = render(<BigList rows={rows.slice(0, 50)} />);
    const r = await axe(container);
    expect((r as unknown as { violations: unknown[] }).violations).toHaveLength(0);
  });
});
