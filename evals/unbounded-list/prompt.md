---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Task, Agent]
timeout_seconds: 600
---

Build the admin screen that lists every customer order so support can scan them. `GET /orders` returns the full array. Some of our bigger merchants have well over 50,000 orders.
