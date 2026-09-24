# Testing Standards

A feature is not done when it renders correctly once. It's done when a regression in it will be caught automatically before it reaches users.

## The testing pyramid, weighted for frontend

| Level | Tool | What it covers | How much |
|---|---|---|---|
| **Component / unit** | Vitest (or Jest) + React Testing Library | Component behavior, hooks, pure logic, data transforms | The bulk — fast, cheap, run on every save |
| **Integration** | RTL + MSW | A feature slice end-to-end in jsdom: fetch → cache → render → interact, with the network mocked at the HTTP layer | Every feature with a data dependency |
| **E2E** | Playwright | Critical user journeys in a real browser against a real build | A deliberately small, high-value set |
| **Visual regression** | Playwright snapshots / Chromatic / Percy | That a design, once matched, stays matched | Shared components + key pages |

Inverting this weighting (a few slow E2E tests and no component tests) is the most common failure mode: slow feedback, flaky CI, and gaps everywhere the journey didn't walk.

## Test behavior, not implementation

Query the DOM the way a user finds things — `getByRole`, `getByLabelText`, `getByText`. Reach for `data-testid` only when no accessible query works, and treat that as a hint the markup may have an accessibility problem (`accessibility.md`).

Never assert on internal state, private functions, or the shape of a component's props. Those are implementation details — tests coupled to them break on every refactor while catching no real bugs, which teaches the team to distrust and delete the tests.

**Snapshot tests are not assertions.** A giant auto-generated markup snapshot documents that markup changed, not that behavior is correct — and the reflex is to `--update` it without reading the diff. Use small, targeted snapshots or none at all.

## Mock at the network boundary (MSW)

Mock HTTP with MSW, not by stubbing hooks or the data layer. Stubbing `useGetUsersQuery` tests that your mock returns what you told it to; mocking the endpoint exercises the real RTK Query cache, loading/error transitions, and serialization — which is where the bugs actually live.

One MSW handler set per API domain, shared between tests and local dev.

## Every test suite covers all 5 data states

`principles.md` §6 requires the UI handle loading, success-with-data, success-empty, error, and stale/refetching. **Each of those needs a test.** The empty and error states are where untested code ships most often, and where users notice it most. With MSW this is cheap: return `[]`, return a 500, return a slow response.

## Coverage policy — risk-weighted, never a blanket number

A global "80% coverage" gate is an anti-pattern: it's satisfied by testing trivial getters while payment logic goes untested, and it drives tests written to move a number.

| Code | Requirement |
|---|---|
| Auth, payments, permissions, data mutation, money/date math | Exhaustive — every branch, every error path. No exceptions. |
| Business logic, custom hooks, reducers, selectors | Thorough, including edge cases |
| Feature components | All 5 data states + the primary interactions |
| Presentational/layout components | Light — a render test, or none |
| Generated files, type-only modules, config | None |

Track coverage as a diagnostic to find untested risky code. Don't gate CI on a global percentage; gate it on the first row of this table.

## E2E: few, critical, stable

Cover the journeys where failure is unacceptable — signup, login, checkout/payment, the core "job to be done." These run against a real build in CI as a release gate.

Keep the set small on purpose: every E2E test is a recurring maintenance and flake cost. A flaky test is worse than no test — it trains everyone to re-run CI without looking. Fix flakes immediately or delete the test; never retry-loop around one.

Never depend on real third-party services, shared mutable fixtures, or `sleep`-based waits. Wait on conditions, seed your own data, tear it down after.

## Visual regression pairs with `/pixel-check`

`/frontend-axiom:pixel-check` gets a component matching its Figma design *once*. Visual regression is what keeps it matching after the next hundred commits. Baseline shared components and key pages; review diffs deliberately rather than blanket-approving.

## CI gating

Tests that don't block a merge are documentation. CI must fail on: any failing test, a type error, a lint error, and a bundle budget breach (`performance.md`).

Run unit/component/integration on every push; E2E and visual regression at minimum on PRs to the default branch and before release.

## Writing tests is part of building the feature

Tests land in the same PR as the code — not "a follow-up ticket," which reliably never happens. `/frontend-axiom:new-feature` writes them during the build, and `/frontend-axiom:audit` treats untested auth/payment/mutation logic as a **Critical** finding, not a suggestion.
