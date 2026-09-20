import { describe, expect, test, vi, beforeEach } from "vitest";
import { request } from "../src/apiClient";

function makeFetch() {
  let refreshed = false;
  const calls: string[] = [];
  const fn = vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    calls.push(url);
    if (url === "/auth/refresh") {
      await new Promise((r) => setTimeout(r, 20)); // refresh is not instant
      refreshed = true;
      return new Response("{}", { status: 200 });
    }
    return new Response("{}", { status: refreshed ? 200 : 401 });
  });
  return { fn, calls };
}

describe("refresh-single-flight", () => {
  beforeEach(() => vi.restoreAllMocks());

  test("refreshes and retries a single 401", async () => {
    const { fn, calls } = makeFetch();
    vi.stubGlobal("fetch", fn);
    const res = await request("/api/a");
    expect(res.status).toBe(200);
    expect(calls.filter((c) => c === "/auth/refresh")).toHaveLength(1);
  });

  test("SINGLE-FLIGHT: 5 concurrent 401s trigger exactly ONE refresh", async () => {
    const { fn, calls } = makeFetch();
    vi.stubGlobal("fetch", fn);
    const res = await Promise.all(
      ["/api/a", "/api/b", "/api/c", "/api/d", "/api/e"].map((u) => request(u))
    );
    // Rotating refresh tokens: N refreshes = reuse detection = session revoked.
    expect(calls.filter((c) => c === "/auth/refresh")).toHaveLength(1);
    expect(res.every((r) => r.status === 200)).toBe(true);
  });

  test("all concurrent callers get their own successful response", async () => {
    const { fn } = makeFetch();
    vi.stubGlobal("fetch", fn);
    const res = await Promise.all([request("/api/x"), request("/api/y")]);
    expect(res).toHaveLength(2);
    expect(res.every((r) => r.status === 200)).toBe(true);
  });
});
