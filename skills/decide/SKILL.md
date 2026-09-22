---
name: decide
description: Record a team decision that the codebase cannot express — an approach tried and rejected, a deliberate exception, a rule for new code that the old code contradicts. Use when the user explains WHY something must or must not be done, especially when the existing code suggests otherwise.
allowed-tools: Bash, Read, Glob, Grep
---

# Record a decision

Ablation measured near-zero benefit from telling a capable model anything it could derive — standards, existing components, conventions demonstrated in the code. The one thing that changed its output was a rule that existed **only in a document and nowhere in the codebase**.

That is what this captures. Not style, not anything a reader could infer — the decisions that live in people's heads:

- an approach tried and rejected, where the code shows no trace of the attempt
- a deliberate exception: "not here, even though we do it everywhere else"
- a rule for new code that the existing code contradicts, mid-migration
- a constraint from outside the codebase entirely

## Recording one

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/decisions.py" add "Short imperative title" \
  --why "What goes wrong without this. Name the incident or bug if there was one." \
  --instead "What to do in its place." \
  --paths "src/checkout/**" \
  --tags "card,checkout,receipt"
```

`--why` is required and the command refuses without it. A rule without its reason gets cargo-culted, and nobody can later judge whether it still applies.

`--paths` and `--tags` are what make it surface at the right moment. Choose tags a person would actually type when about to violate the rule — not a taxonomy.

## Listening for them

Record proactively when the user explains a constraint in passing. "We moved off Zustand because cache invalidation had no owner" is exactly this, and it will be lost otherwise. Confirm the wording before writing it, then say it has been recorded.

## Reviewing

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/decisions.py" list
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/decisions.py" stale --days 180
```

A decision nobody has reconfirmed in six months may be describing a problem that no longer exists. Surfacing a stale rule is worse than surfacing none.
