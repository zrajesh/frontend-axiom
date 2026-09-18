---
name: pixel-check
description: Compare a running page or component against its Figma design and iterate the implementation until pixel-accurate, using the Figma MCP for the design source and the Chrome DevTools MCP for the live render. Use whenever a feature has a Figma reference and needs visual validation.
allowed-tools: Read, Edit, Bash
---

# Pixel Check

## Step 1 — gather references

- If not already provided, ask for the Figma frame/node link (or node id) to validate against, and the local URL where the implementation is running (start the dev server if it isn't running).

## Step 2 — pull the design spec

- Use the Figma MCP tools to get the node's rendered image and its design properties: spacing, colors, typography (family/size/weight/line-height), corner radius, layout (flex direction, gaps, alignment).

## Step 3 — capture the live render

- Use the Chrome DevTools MCP tools to navigate to the local URL and screenshot the matching component/page at the same viewport width the Figma frame was designed for (ask if unclear rather than guessing a breakpoint).

## Step 4 — diff and report

Compare the two and report concrete deltas, not vague impressions: exact spacing differences, color hex mismatches, font-size/weight mismatches, alignment/gap differences. Reference `${CLAUDE_PLUGIN_ROOT}/knowledge/css.md` for how the project's chosen styling approach expresses tokens (Tailwind scale, CSS variables, etc.) so fixes match the existing convention rather than introducing one-off values.

## Step 5 — fix and iterate

Apply the fix, re-screenshot, re-diff. Repeat until within a reasonable tolerance (sub-pixel/rounding differences aren't worth chasing). Finish with a short summary of what was adjusted and confirmation the final screenshot matches.
