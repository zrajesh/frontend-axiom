---
name: init-project
description: Bootstrap Frontend Axiom conventions on a brand-new frontend project, or adopt them onto an existing repo. Use when starting a new frontend project, or the first time this plugin touches an existing codebase.
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, AskUserQuestion
---

# Init Project

Goal: get an explicit, confirmed record of this project's stack before anything else happens — never assume it.

## Step 1 — detect

Check for `package.json` at the repo root.

**If it exists (existing project):**
- Read `package.json`, and whichever of these are present: `next.config.*`, `tailwind.config.*`, `tsconfig.json` vs plain `.js`/`.jsx` source files, any Redux/Zustand/RTK Query usage in `src`/`app`.
- From that, infer: framework (React SPA vs Next.js, and Pages vs App Router if Next), CSS approach, state/data layer, TypeScript vs JavaScript.
- Present what you found as a short summary, then use AskUserQuestion to have the user **confirm or correct each item** — do not proceed on an inferred stack without explicit confirmation.

**If it doesn't exist (fresh project):**
- Use AskUserQuestion to ask, as separate questions:
  1. Framework: React (SPA/Vite) or Next.js (App Router)?
  2. CSS approach: Tailwind CSS / CSS Modules / Styled Components / Other?
  3. State & data layer: RTK Query / Zustand / Other?
  4. TypeScript or JavaScript?
- Never default silently — even if this plugin's own preference is Next.js + RTK Query + TypeScript (see `knowledge/react-nextjs.md`, `state-data.md`), that's a recommendation to surface, not a default to assume.

## Step 2 — scaffold or apply

Once confirmed:
- Fresh project: scaffold with the appropriate tool (`create-next-app`, or Vite for a React SPA) and install the chosen CSS/state packages.
- Existing project: don't restructure what's already there. Note conventions to adopt going forward, and flag (don't silently fix) any existing code that conflicts with `knowledge/principles.md` — that's a job for `/frontend-axiom:audit`, not a blanket auto-rewrite.

### Wiring in the ESLint rule (both cases)

The rule package is not on npm — install it from this plugin's own directory:

```bash
npm install --save-dev "file:$CLAUDE_PLUGIN_ROOT/eslint-plugin-frontend-axiom"
```

Then register it in whichever config style the project actually uses — **check before writing, the two forms are not interchangeable**:

- Flat config (`eslint.config.js` / `.mjs` — the default for ESLint 9+ and current Next.js):
  ```js
  const frontendAxiom = require("eslint-plugin-frontend-axiom");
  module.exports = [frontendAxiom.configs.recommended];
  ```
- Legacy (`.eslintrc.*`): `extends: ["plugin:frontend-axiom/legacy-recommended"]`

Leave it at `"warn"` initially. On an existing codebase it will light up a lot at first — that's expected, and is signal for `/frontend-axiom:audit` to triage, not a reason to mass-rewrite files during init.

## Step 3 — record the decision

Write or update the project's root `CLAUDE.md` with a short "Stack" section recording the confirmed framework/CSS/state/language choices, and a pointer to this plugin's `knowledge/` directory. This means future sessions don't re-ask what's already been decided.

## Step 4 — read the knowledge base

Before generating any scaffold code, read `knowledge/principles.md`, `knowledge/react-nextjs.md`, `knowledge/css.md`, and `knowledge/state-data.md` so the initial structure already follows them (feature-first folders, destructuring convention, 5-state data handling pattern, etc).
