---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Task, Agent]
timeout_seconds: 600
---

Implement logout. We use RTK Query, and the session is an httpOnly cookie set by the server.

```ts
function logout() {
  router.push("/login");
}
```
