---
name: new-feature
description: Plan and build a new frontend feature the Frontend Axiom way. Interviews requirements first, never assumes, then implements following SOLID and the destructuring convention with full data-state handling. Use whenever the user asks to build/add a new UI feature, page, or flow.
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, AskUserQuestion
---

# New Feature

## Step 1 — interview, don't assume (see `knowledge/principles.md` §1 and §7)

Before writing any code, get clear on:
- What problem/user story is this solving, and for whom?
- Data source and exact shape — do we have a real API contract/schema, or does one need to be defined? Never invent field names.
- Every UI state that applies: loading, success-with-data, success-empty, error, and any permission/auth-gated variants.
- Edge cases the user cares about (pagination? real-time updates? offline?).
- Is there a Figma design reference? If yes, this feature should end with `/frontend-axiom:pixel-check` against it.
- Any auth/permission requirements that change what's rendered.
- Any non-functional expectations that shape the approach (expected scale/traffic, latency targets, offline/availability needs) — these drive architectural decisions as much as the functional ask does.

Ask via AskUserQuestion where there's a genuine decision the user must make (not things inferable from the confirmed project stack in `CLAUDE.md`).

## Step 2 — plan

Sketch the component/hook/API-slice breakdown against `knowledge/principles.md` (SOLID, small units, reuse-on-third-duplication) and `knowledge/react-nextjs.md` (Server vs Client Component split, rendering strategy). If Claude Code's Plan Mode is available in this session, use it to get explicit sign-off on the plan before writing code.

## Step 3 — build

- Follow the destructuring rule exactly (`knowledge/principles.md` §3) — no `obj.prop.prop2` chains.
- Implement RTK Query endpoints (or the confirmed data layer) per `knowledge/state-data.md`, mapped to all 5 data states.
- Apply `knowledge/security.md` at every boundary this feature touches (input validation, no secrets in client code, correct storage for any tokens — `knowledge/storage.md`).
- Apply `knowledge/performance.md` (image/font handling, code-splitting heavy pieces, resource hints if this feature is on a critical path) and `knowledge/accessibility.md` (semantic HTML, keyboard/labels/contrast) as you go, not as an afterthought.

## Step 4 — self-check before declaring done

Re-read the diff against `knowledge/principles.md` directly: any dot-chained property access? Any component doing more than one job? Any data state left unhandled? Fix before finishing rather than leaving it for `/audit` to catch.
