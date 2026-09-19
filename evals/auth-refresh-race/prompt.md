---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Task, Agent]
timeout_seconds: 600
---

Our app fires several API calls in parallel when the dashboard loads. When the access token has expired, users sometimes get logged out even though they're actively using the app. Here's our interceptor:

```ts
async function request(url: string) {
  let res = await fetch(url);
  if (res.status === 401) {
    const r = await fetch("/auth/refresh", { method: "POST" });
    const { token } = await r.json();
    localStorage.setItem("access_token", token);
    res = await fetch(url);
  }
  return res;
}
```

Why are they getting logged out, and how would you fix it?
