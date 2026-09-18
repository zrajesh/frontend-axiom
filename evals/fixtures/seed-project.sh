#!/usr/bin/env bash
# Seeds a minimal, realistic Next.js + TypeScript + RTK Query project into the
# eval sandbox's working directory.
#
# Why this exists: eval cases previously ran in an EMPTY directory while the
# prompts said "our app" and "this project's conventions". Agents in both arms
# burned their whole budget searching for a codebase that did not exist, and
# most runs hit the timeout. That measured the sandbox, not the plugin.
#
# Deliberately withheld so cases still measure something:
#   - no user/profile API endpoint  -> "ask, don't invent field names" stays the
#     correct behavior for asks-before-guessing
#   - no component that handles empty/error states -> five-data-states can't be
#     solved by copying a neighbour
#   - no destructuring examples      -> destructuring-rule isn't cued by context

set -euo pipefail

cat > package.json <<'JSON'
{
  "name": "acme-storefront",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "test": "vitest run",
    "lint": "eslint ."
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@reduxjs/toolkit": "^2.2.0",
    "react-redux": "^9.1.0"
  },
  "devDependencies": {
    "typescript": "^5.4.0",
    "vitest": "^2.0.0",
    "@testing-library/react": "^16.0.0",
    "eslint": "^9.0.0"
  }
}
JSON

cat > tsconfig.json <<'JSON'
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "ES2022"],
    "strict": true,
    "jsx": "preserve",
    "module": "esnext",
    "moduleResolution": "bundler",
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src/**/*.ts", "src/**/*.tsx"]
}
JSON

cat > CLAUDE.md <<'MD'
# Acme Storefront

## Stack

Confirmed via `/frontend-axiom:init-project`:

- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript (strict)
- **Styling:** Tailwind CSS
- **State & data:** Redux Toolkit + RTK Query
- **Tests:** Vitest + React Testing Library

Feature-first structure under `src/features/<feature>/`.
MD

mkdir -p src/app src/features/cart src/store

cat > src/store/api.ts <<'TS'
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const api = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({ baseUrl: "/api" }),
  tagTypes: ["Cart"],
  endpoints: (builder) => ({
    getCart: builder.query<{ items: CartItem[] }, void>({
      query: () => "/cart",
      providesTags: ["Cart"],
    }),
  }),
});

export interface CartItem {
  id: string;
  sku: string;
  quantity: number;
}

export const { useGetCartQuery } = api;
TS

cat > src/features/cart/CartBadge.tsx <<'TSX'
"use client";

import { useGetCartQuery } from "@/store/api";

export default function CartBadge() {
  const { data } = useGetCartQuery();
  const { items = [] } = data ?? {};

  return <span aria-label="Cart items">{items.length}</span>;
}
TSX

cat > src/app/layout.tsx <<'TSX'
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
TSX

echo "node_modules/" > .gitignore
