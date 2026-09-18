---
name: learn-guide
description: Ingest a pasted frontend guide (e.g. copied from Notion) directly into the knowledge base as durable, dense reference content — merged into the relevant existing knowledge/*.md file, or a new one if the topic doesn't fit an existing file. Use when the user pastes a best-practices doc and asks Claude to learn/remember it.
allowed-tools: Read, Write, Edit, Glob, AskUserQuestion
---

# Learn Guide

## Step 1 — get the content and topic

Take the pasted content from `$ARGUMENTS` or the message. Identify the topic it covers.

## Step 2 — distill, don't just dump

Rewrite into the same dense, reference style as the rest of `knowledge/` — decision tables, checklists, short rules with a one-line rationale — rather than saving the raw pasted prose verbatim. The goal is something an agent can scan and apply quickly, matching `knowledge/principles.md`'s style.

## Step 3 — decide where it lives

- If the topic clearly belongs to an existing file's domain (`react-nextjs.md`, `css.md`, `state-data.md`, `security.md`, `performance.md`, `seo-ai-seo.md`, `accessibility.md`, `storage.md`, `principles.md`), merge it in: add a new section, or fold into an existing one if it overlaps.
- If it's a genuinely new domain not covered by any existing file (e.g. testing strategy, git workflow, component library conventions), create a new `knowledge/<topic-slug>.md`.
- Every skill/agent already reads the whole `knowledge/` tree, so a new file needs no separate index update — just a descriptive filename.

## Step 4 — check for conflicts before writing

Before merging or saving, check whether this content contradicts anything already in `knowledge/*.md`. If it does, do not silently overwrite — show the user both versions and ask which should win, or whether both are valid in different contexts (and if so, note that distinction directly in the file).

## Step 5 — save

Write the merge/new file directly under `knowledge/`.
