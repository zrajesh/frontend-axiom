---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Task, Agent]
timeout_seconds: 600
---

Write the React component for an orders list, following this project's frontend conventions. If a frontend-architect agent or frontend standards are available to you, use them. Everything you need is in this message — do not explore the repository. The API contract is already agreed and final, so don't ask about it:

`GET /orders` returns `{ orders: Array<{ id: string; reference: string; total: number }> }`

A customer with no orders yet is a normal, expected case — the endpoint returns `{ orders: [] }` for them, with a 200.

Show me the component code.
