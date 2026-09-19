---
type: llm
weight: 1
---
**Pass** requires BOTH:
1. Identifies that client-side fetch-after-mount is wrong for indexable content — the HTML ships without product data, creating a render/crawl dependency and slow first paint. Moves it server-side: Server Component with SSG/ISR (ideal for product pages) or SSR.
2. Names a concrete Next.js mechanism: Server Components, `generateStaticParams`/`generateMetadata`, `revalidate`/ISR, or equivalent — not just "use SSR".

Bonus: per-page metadata/canonical; structured data; LCP image/`next/image`; mobile traffic making hydration cost matter.

**Fail** if it keeps the `useEffect` fetch and only adds meta tags, or gives only generic "improve SEO" advice.
