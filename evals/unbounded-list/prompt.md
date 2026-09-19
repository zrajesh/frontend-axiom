---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Task, Agent]
timeout_seconds: 600
---

This is an existing Next.js 15 (App Router) + TypeScript + RTK Query + Tailwind app with Vitest set up. Answer for that stack — do not ask about it, and do not explore the repository.

Build the admin screen that lists every customer order so support can scan them.

The API contract is already agreed and final, so don't ask about it:

`GET /orders` returns `{ orders: Array<{ id: string; reference: string; customerEmail: string; status: "paid" | "refunded" | "pending"; total: number; createdAt: string }> }`

It takes no query parameters today — it returns every order for the merchant in one response. Some of our bigger merchants have well over 50,000 orders.

Tell me how you'd build this and why. Show the key code.
