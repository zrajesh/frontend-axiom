# SEO & Agentic/AI SEO Standards

## Traditional SEO

- Use Next.js Metadata API (`generateMetadata`) for title/description/canonical per route — never client-side-only `document.title` mutation for pages that need indexing.
- Canonical URLs on every indexable page, especially where query params can create duplicate-content URLs.
- `sitemap.xml` and `robots.txt` generated/maintained, kept in sync with actual routes (block genuinely private routes, don't accidentally block the whole site).
- Structured data (JSON-LD, schema.org) for anything with a matching type — Article, Product, FAQ, BreadcrumbList, Organization. This is what powers rich results and is increasingly what AI answer engines parse for facts.
- Semantic HTML (`<nav>`, `<main>`, `<article>`, proper heading hierarchy) — crawlers and accessibility tools both depend on it; don't build the whole page out of generic `<div>`s.

## Rendering for crawlability

- Any content that needs to be indexed should be present in the initial HTML (SSR/SSG/ISR) — don't rely on a CSR-only fetch-after-mount for primary content. Not every crawler executes JS reliably, and even when it does, it costs render budget.
- Pagination/infinite scroll: provide a crawlable path (real paginated URLs or a sitemap listing all items) — a crawler won't scroll.

## Agentic / AI SEO (answer engines, LLM crawlers)

- Structured, factual, well-labeled content is what gets extracted and cited by AI answer engines — same JSON-LD/semantic-HTML investment as traditional SEO pays off here too.
- Consider an `llms.txt` at the site root: a plain-markdown summary of what the site is and links to its key canonical content, written for an LLM to ingest quickly (an emerging convention, not yet universally adopted — treat as a nice-to-have, not a certainty).
- Avoid burying key facts only inside client-JS-rendered widgets an AI crawler may not execute — state the core facts in plain server-rendered text/HTML too.
- Open Graph tags (`og:title`, `og:description`, `og:image`) — used both for social previews and by many AI tools when summarizing/citing a link.
- Keep content unambiguous and self-contained per page — AI answer engines tend to extract and quote in isolation, without surrounding page context.
