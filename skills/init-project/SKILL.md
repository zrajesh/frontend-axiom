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
- Never default silently — even if this plugin's own preference is Next.js + RTK Query + TypeScript (see `${CLAUDE_PLUGIN_ROOT}/knowledge/primer/react-nextjs.md`, `state-data.md`), that's a recommendation to surface, not a default to assume.

## Step 2 — scaffold or apply

Once confirmed:
- Fresh project: scaffold with the appropriate tool (`create-next-app`, or Vite for a React SPA) and install the chosen CSS/state packages.
- Existing project: don't restructure what's already there. Note conventions to adopt going forward, and flag (don't silently fix) any existing code that conflicts with `${CLAUDE_PLUGIN_ROOT}/knowledge/primer/principles.md` — that's a job for `/frontend-axiom:audit`, not a blanket auto-rewrite.

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

The shipped config sets the house rule to **`error`**, so it actually gates — a rule that can only warn is decoration, and `${CLAUDE_PLUGIN_ROOT}/knowledge/primer/release-operations.md` forbids leaving one there.

On an **existing** codebase that will light up immediately. Stage it rather than mass-rewriting during init:

```js
// eslint.config.js — adopt gradually, then delete this override
const frontendAxiom = require("eslint-plugin-frontend-axiom");
module.exports = [
  frontendAxiom.configs.recommended,
  { rules: { "frontend-axiom/no-repeated-property-access": "warn" } }, // TODO: remove
];
```

Record who owns removing that override and by when. An override with no owner is permanent.

## Step 3 — record the decision

Write or update the project's root `CLAUDE.md` with a short "Stack" section recording the confirmed framework/CSS/state/language choices, and a pointer to this plugin's `knowledge/` directory. This means future sessions don't re-ask what's already been decided.

## Step 4 — read the knowledge base

Before generating any scaffold code, read `${CLAUDE_PLUGIN_ROOT}/knowledge/primer/principles.md`, `${CLAUDE_PLUGIN_ROOT}/knowledge/primer/react-nextjs.md`, `${CLAUDE_PLUGIN_ROOT}/knowledge/primer/css.md`, `${CLAUDE_PLUGIN_ROOT}/knowledge/primer/state-data.md`, and any other file in `knowledge/` relevant to this project so the initial structure already follows them (feature-first folders, destructuring convention, 5-state data handling, etc).

## Step 5 — build the project inventory

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/scan-project.py"        # what exists
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/extract-conventions.py" # how this team writes it
```

The second one matters most on an existing repo. Ablation measured ~zero delta on everything a capable model can derive — standards, reuse, even self-verification — and **+1.00 on an arbitrary house convention**, because that answer exists nowhere in training. `extract-conventions.py` infers this repository's own arbitrary choices (export style, import style, props declaration, styling, test location) and only reports those above 80% consistency, since a false rule makes an agent "fix" correct code.

Writes `.frontend-axiom/inventory.md`: every component, hook, API endpoint and design token this repo already has. From then on it is injected automatically on every frontend prompt.

This is the highest-value step on an existing codebase, and it is worth understanding why. Benchmarking this plugin showed a strong model already satisfies the generic standards unaided — a zero delta on most cases. What it cannot know is *your* repository: that a `<Button>` with a `variant` prop already exists, that the endpoint is `refundOrder` and not `refundPayment`. That gap is permanent, and it is where an agent actually goes wrong.

Regenerate it whenever components or endpoints are added. Mention it in the project's `CLAUDE.md` so the team knows to keep it fresh.

## Step 6 — establish the baselines that are expensive to retrofit

Scaffold time is the cheapest moment to set these up, and the hardest to add later once hundreds of files exist. Set up each one, or explicitly tell the user which you skipped and why:

- **Security headers** (`${CLAUDE_PLUGIN_ROOT}/knowledge/primer/security.md`) — CSP, HSTS, `X-Content-Type-Options`, `Referrer-Policy`, `frame-ancestors` in `next.config` / the hosting layer.
- **Accessibility linting** (`${CLAUDE_PLUGIN_ROOT}/knowledge/primer/accessibility.md`) — `eslint-plugin-jsx-a11y` alongside the frontend-axiom rule.
- **Test runner + CI gate** (`${CLAUDE_PLUGIN_ROOT}/knowledge/primer/testing.md`) — the test tooling and a CI job that actually fails the build on failure. A test setup nobody runs is worth nothing.
- **Error tracking and RUM** (`${CLAUDE_PLUGIN_ROOT}/knowledge/primer/observability.md`) — wired on day one, so the app is never in production unobserved.
- **Caching defaults** (`${CLAUDE_PLUGIN_ROOT}/knowledge/primer/caching.md`) — `Cache-Control` for hashed static assets vs HTML/API.
- **SEO baseline** (`${CLAUDE_PLUGIN_ROOT}/knowledge/primer/seo-ai-seo.md`) — `robots.txt` and a sitemap route, if the app is publicly indexable.
