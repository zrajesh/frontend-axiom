#!/usr/bin/env bash
# Frontend Axiom — executable verification gates.
#
# Turns review from opinion into evidence. A model can assert "this is
# accessible"; only axe can tell you the contrast ratio is 2.1:1.
#
# Design rules:
#   - A gate that cannot run reports SKIP, never PASS. Silent skipping is how
#     "all checks passed" comes to mean nothing.
#   - A missing gate is itself a finding: testing.md requires CI to gate, so
#     "no test runner configured" is a defect, not a neutral state.
#   - Never mutate the project. Read-only.
#
# Usage:
#   verify.sh [--url http://localhost:3000] [--budget-kb 170]
# Exit: 0 all runnable gates passed · 1 a gate failed · 2 bad invocation

set -uo pipefail

URL=""
BUDGET_KB=170
while [[ $# -gt 0 ]]; do
  case "$1" in
    --url)       URL="${2:-}"; shift 2 ;;
    --budget-kb) BUDGET_KB="${2:-170}"; shift 2 ;;
    -h|--help)   sed -n '2,18p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

FAILED=0
SKIPPED=0
declare -a ROWS=()

row() { # name status detail
  ROWS+=("$(printf '%-12s %-5s %s' "$1" "$2" "$3")")
  [[ "$2" == "FAIL" ]] && FAILED=1
  [[ "$2" == "SKIP" ]] && SKIPPED=$((SKIPPED+1))
  return 0
}

has_npm_script() { # does package.json define this npm script?
  [[ -f package.json ]] || return 1
  node -e "const s=(require('./package.json').scripts)||{};process.exit(s['$1']?0:1)" 2>/dev/null
}

echo "=== FRONTEND AXIOM — VERIFICATION GATES ==="
echo "cwd: $(pwd)"
echo

# ---------------------------------------------------------------- typecheck
if [[ -f tsconfig.json ]]; then
  if out=$(npx --no-install tsc --noEmit 2>&1); then
    row typecheck PASS "no type errors"
  else
    n=$(grep -cE "error TS" <<<"$out" || true)
    row typecheck FAIL "$n type error(s)"
    echo "$out" | grep -E "error TS" | head -8 | sed 's/^/    /'
  fi
else
  row typecheck SKIP "no tsconfig.json — untyped project is itself a finding"
fi

# --------------------------------------------------------------------- lint
shopt -s nullglob
ESLINT_CFGS=(.eslintrc* eslint.config.*)
shopt -u nullglob
if [[ ${#ESLINT_CFGS[@]} -gt 0 ]]; then
  json=$(npx --no-install eslint . -f json 2>/dev/null)
  read -r nfiles errs warns <<<"$(node -e "
    let r=[]; try { r = JSON.parse(process.argv[1]||'[]'); } catch (e) {}
    const e = r.reduce((a,f)=>a+f.errorCount,0);
    const w = r.reduce((a,f)=>a+f.warningCount,0);
    console.log(r.length, e, w);
  " "$json" 2>/dev/null || echo "0 0 0")"

  if [[ "${nfiles:-0}" -eq 0 ]]; then
    # A lint run that inspected nothing is not a pass. Almost always the flat
    # config's `files` patterns omit .ts/.tsx, so JSX/TS code goes unchecked.
    row lint SKIP "eslint matched 0 files — check the config's \`files\` patterns"
  elif [[ "${errs:-0}" -gt 0 ]]; then
    row lint FAIL "$errs error(s), $warns warning(s) across $nfiles file(s)"
    node -e "
      let r=[]; try { r = JSON.parse(process.argv[1]||'[]'); } catch (e) {}
      let n=0;
      for (const f of r) for (const m of f.messages) {
        if (m.severity !== 2 || n++ >= 8) continue;
        const file = f.filePath.split('/').pop();
        console.log('    ' + file + ':' + m.line + '  ' + (m.ruleId||'?') + '  ' + m.message.slice(0,60));
      }
    " "$json" 2>/dev/null
  else
    row lint PASS "0 errors, $warns warning(s) across $nfiles file(s)"
  fi
  if ! grep -q "jsx-a11y" <<<"$(cat "${ESLINT_CFGS[@]}" 2>/dev/null)"; then
    row a11y-lint SKIP "eslint-plugin-jsx-a11y not configured — static a11y unchecked"
  else
    row a11y-lint PASS "jsx-a11y active (see lint row for violations)"
  fi
else
  row lint SKIP "no eslint config — conventions unenforced in CI"
  row a11y-lint SKIP "no eslint config"
fi

# -------------------------------------------------------------------- tests
if has_npm_script test; then
  if out=$(npm test --silent 2>&1); then
    row tests PASS "suite green"
  else
    row tests FAIL "suite failing"
    echo "$out" | tail -12 | sed 's/^/    /'
  fi
else
  row tests SKIP "no test script — testing.md treats untested logic as Critical"
fi

# ------------------------------------------------------------------- bundle
if [[ -d .next ]]; then
  # The budget in knowledge/performance.md is COMPRESSED bytes — that is what
  # crosses the wire. Summing raw bytes overstates by roughly 3-4x and fails
  # projects that are comfortably within budget, so compress before comparing.
  if command -v gzip >/dev/null 2>&1; then
    bytes=$(find .next/static/chunks -name '*.js' -not -name '*.map' -exec cat {} + 2>/dev/null \
            | gzip -c 2>/dev/null | wc -c | tr -d ' ')
    unit="KB gzipped"
  else
    bytes=""
  fi
  if [[ "${bytes:-0}" -gt 0 ]]; then
    kb=$((bytes/1024))
    if [[ "$kb" -gt "$BUDGET_KB" ]]; then
      row bundle FAIL "${kb}${unit} client JS > ${BUDGET_KB}KB budget"
    else
      row bundle PASS "${kb}${unit} client JS (budget ${BUDGET_KB}KB)"
    fi
    # Honest about what this is: all chunks concatenated, not per-route
    # first-load. Good for catching regressions, not a substitute for
    # `next build`'s own per-route table.
    echo "    note: all chunks combined — see \`next build\` output for per-route first-load"
  else
    row bundle SKIP "no chunks found under .next/static, or gzip unavailable"
  fi
else
  row bundle SKIP "no build output — run the production build first"
fi

# --------------------------------------------------------------- a11y (live)
if [[ -n "$URL" ]]; then
  if out=$(npx --yes @axe-core/cli "$URL" --exit 2>&1); then
    row a11y-live PASS "axe found 0 violations at $URL"
  else
    v=$(grep -oE "[0-9]+ violation" <<<"$out" | head -1)
    row a11y-live FAIL "axe: ${v:-violations found} at $URL"
    echo "$out" | grep -A2 -iE "violation|impact" | head -14 | sed 's/^/    /'
  fi
else
  row a11y-live SKIP "no --url given — runtime a11y unverified (static lint only)"
fi

# ------------------------------------------------------------------- report
echo
printf '%s\n' "${ROWS[@]}"
echo
if [[ "$FAILED" -eq 1 ]]; then
  echo "=== VERDICT: FAIL — at least one gate failed ==="
  exit 1
fi
if [[ "$SKIPPED" -gt 0 ]]; then
  echo "=== VERDICT: PASS (with $SKIPPED gate(s) SKIPPED) ==="
  echo "Report every SKIP as a finding. An unrunnable gate proves nothing."
  exit 0
fi
echo "=== VERDICT: PASS — all gates ran and passed ==="
exit 0
