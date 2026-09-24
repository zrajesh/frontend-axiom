# Release Operations Standards

Most large-scale outages don't come from bad code review. They come from good code released badly — to everyone at once, with no way to turn it off. At millions of users daily, how a change reaches production matters as much as what's in it.

## CI gates — what must pass before merge

| Gate | Fails the build when |
|---|---|
| Typecheck | Any type error (`tsc --noEmit`) |
| Lint | Any lint **error** (see severity policy below) |
| Tests | Any failing unit/component/integration test (`testing.md`) |
| Bundle budget | Per-route JS exceeds its ceiling (`performance.md`) |
| A11y scan | New axe violations (`accessibility.md`) |
| E2E | A critical journey breaks — on PRs to the default branch, at minimum |

A gate that warns but doesn't block is not a gate.

### Lint severity policy

New rules start at `warn` so adopting them doesn't block work on an existing codebase. But a permanent `warn` is decoration — nobody reads it. So: **once a rule's warning count reaches zero, promote it to `error` in the same PR and gate CI on it.** Otherwise the count creeps back up forever. This applies to `frontend-axiom/no-repeated-property-access` and `prefer-destructuring` — `/frontend-axiom:audit` should flag a long-lived `warn` with a zero or near-zero count as a finding.

## Feature flags

Any change with meaningful blast radius ships behind a flag — a new user-facing flow, a data-layer or API migration, anything touching auth/payments, anything you can't fully verify pre-production.

- **The flag is a kill switch.** Turning it off must fully restore previous behavior without a deploy. That's the entire point: mitigation in seconds rather than a revert-build-deploy cycle.
- Default off. Enable deliberately.
- Flags are temporary. Every flag needs an owner and a removal date — stale flags multiply untested code paths combinatorially until nobody knows which combination is actually in production.
- Evaluate flags server-side or at the edge where possible, so flagged-off code can be excluded from the bundle rather than shipped-but-dormant.

## Staged rollout

Never go 0 → 100%. Promote through stages, watching real metrics at each:

```
internal → 1% → 10% → 50% → 100%
```

Hold at each stage long enough to cover a real usage cycle (and peak traffic), not five minutes.

**Define promote/rollback criteria before you start rolling out** — deciding what counts as "bad" while watching a graph at 2am guarantees a bad decision. Tie them to `observability.md` signals:

| Roll back immediately when |
|---|
| Error rate exceeds baseline for the cohort |
| A core journey's completion rate drops against baseline |
| CWV (p75) for affected routes crosses out of "Good" |
| Any new Critical error class appears |

Compare the exposed cohort against the unexposed one, not against yesterday — that controls for traffic, seasonality, and unrelated deploys.

## Environments

`local → preview (per-PR) → staging → production`. Per-PR preview deployments are the highest-value piece: they let review, `/frontend-axiom:pixel-check`, and stakeholder sign-off happen against a real deployed build instead of a description.

Staging must run the production build with production-equivalent config. A staging environment that differs meaningfully from production tests something that doesn't exist.

## Rollback

**Rollback is a first-class procedure, not an improvisation.** Requirements:

- Documented, practiced, and executable by whoever is on call — not only by the person who wrote the feature
- Fast: flag off in seconds; redeploy of the previous build in minutes
- Prefer flag-off over revert for anything flagged — it's faster and lower-risk
- Every deploy artifact is immutable and versioned, so "the previous build" is an exact, redeployable thing, not a rebuild from a moving branch

Watch for the asymmetric cases: a client-side rollback does **not** undo a backend or schema migration, and users holding a stale JS bundle may keep calling an endpoint you just changed. Roll forward-compatible: deploy the API change first, the client that depends on it second, and remove the old path only once the old clients are gone.

## Release readiness checklist

Before a feature reaches 100%:

- [ ] CI gates green (above)
- [ ] Tests cover the new behavior, including failure paths (`testing.md`)
- [ ] Error tracking and RUM live on the new paths (`observability.md`)
- [ ] Alerting would actually fire if this broke
- [ ] Flag-gated with a verified kill switch, if blast radius warrants
- [ ] Rollback path confirmed
- [ ] Rollout stages and promote/rollback criteria agreed in advance
- [ ] Design matched via `/frontend-axiom:pixel-check`, with a visual-regression baseline captured
