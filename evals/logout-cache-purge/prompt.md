---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Task, Agent]
timeout_seconds: 600
---

This is an existing Next.js 15 (App Router) + TypeScript + RTK Query + Tailwind app with Vitest set up. Answer for that stack — do not ask about it, and do not explore the repository.

Implement logout. We use RTK Query, and the session is an httpOnly cookie set by the server.

```ts
function logout() {
  router.push("/login");
}
```
