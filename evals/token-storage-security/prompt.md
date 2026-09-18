---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
timeout_seconds: 600
---

Our login endpoint returns an auth token. A teammate suggested we keep it in `localStorage` so it survives refreshes and is easy to read from our API client. Is that a good approach? What do you recommend?
