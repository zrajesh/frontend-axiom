Create `src/apiClient.ts` exporting an async function:

```ts
export async function request(url: string): Promise<Response>
```

It calls `fetch(url, { credentials: "include" })`.

If the response status is 401, the session has expired: refresh it by calling
`fetch("/auth/refresh", { method: "POST", credentials: "include" })`, then retry
the original request once and return that response.

Our dashboard fires many of these at once when it mounts.

Write only that file. No new dependencies.
