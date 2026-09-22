#!/usr/bin/env bash
# Frontend Axiom — outcome-based benchmark.
#
# The eval suite in evals/ asks an LLM whether an answer sounds right. This
# asks whether the produced CODE actually works: it runs the agent on a task,
# then compiles, lints and renders the result. The grader is tsc, eslint and
# a headless DOM — not an opinion, and not authored by the same hand that
# wrote the standards.
#
# Arms:
#   treatment = installed plugin disabled + --plugin-dir <repo>  (local code)
#   control   = installed plugin disabled, no plugin at all
# Both verified: treatment sees the standards, control does not.
#
# Usage: run.sh [--runs N] [--task NAME] [--keep] [--model haiku|sonnet|opus]
#
# --model matters more than it looks. A top-tier model already knows most of
# these standards, so the plugin can only add engagement and house-specific
# facts. A smaller model does not know them, so the same injection may be the
# whole value. A single number averaged across tiers hides both effects.

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BENCH="$ROOT/benchmark"
TEMPLATE="$BENCH/.template/node_modules"
RUNS=3; ONLY=""; KEEP=0; MODEL=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --runs) RUNS="$2"; shift 2 ;;
    --task) ONLY="$2"; shift 2 ;;
    --keep) KEEP=1; shift ;;
    --model) MODEL="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

[[ -d "$TEMPLATE" ]] || { echo "missing $TEMPLATE — run npm install in benchmark/.template" >&2; exit 2; }

STAMP="$(date +%Y%m%dT%H%M%S)"
OUT="$BENCH/results/$STAMP"; mkdir -p "$OUT"
WORK="$(mktemp -d)"
# Always restore the user's plugin state, even on Ctrl-C or error.
restore() { claude plugin enable frontend-axiom >/dev/null 2>&1 || true
            [[ "$KEEP" -eq 1 ]] || rm -rf "$WORK"; }
trap restore EXIT INT TERM
claude plugin disable frontend-axiom >/dev/null 2>&1

# score_run <dir> -> "passed total"
score_run() {
  local d="$1" passed=0 total=0
  pushd "$d" >/dev/null || return 1

  # Gate 1: it must compile.
  total=$((total+1))
  npx --no-install tsc --noEmit >/dev/null 2>&1 && passed=$((passed+1))

  # Gate 2: lint clean (includes jsx-a11y).
  total=$((total+1))
  local errs
  errs=$(npx --no-install eslint src --format json 2>/dev/null \
         | node -e "let d='';process.stdin.on('data',c=>d+=c).on('end',()=>{
             try{const r=JSON.parse(d);console.log(r.reduce((a,f)=>a+f.errorCount,0))}catch(e){console.log(99)}})" 2>/dev/null)
  [[ "${errs:-99}" -eq 0 ]] && passed=$((passed+1))

  # Gates 3..N: the behavioural spec. Each test is one point.
  npx --no-install vitest run --reporter=json --outputFile=.vitest.json >/dev/null 2>&1
  if [[ -f .vitest.json ]]; then
    read -r tp tt <<<"$(node -e "
      try{const r=require('./.vitest.json');
        console.log(r.numPassedTests||0, r.numTotalTests||0);}catch(e){console.log(0,0)}" 2>/dev/null)"
    passed=$((passed + ${tp:-0})); total=$((total + ${tt:-0}))
  else
    total=$((total+7))   # spec failed to run at all: all behavioural points lost
  fi
  # Structural health. Long-horizon degradation is the failure mode that
  # prompt text provably does not fix, so it is scored, not just described.
  if [[ -f "$ROOT/scripts/measure-health.py" ]]; then
    read -r hp ht <<<"$(python3 - "$ROOT/scripts/measure-health.py" "$d" <<'PYEOF'
import json, subprocess, sys
script, root = sys.argv[1], sys.argv[2]
try:
    out = subprocess.run([sys.executable, script, root, "--json"],
                         capture_output=True, text=True, timeout=60).stdout
    e = (json.loads(out or "{}").get("erosion") or {})
    v = (json.loads(out or "{}").get("verbosity") or {})
except Exception:
    print(0, 0); raise SystemExit
checks = [
    e.get("max_complexity", 99) <= 15,
    e.get("max_function_lines", 999) <= 80,
    e.get("max_nesting", 99) <= 5,
    v.get("duplication_ratio", 1.0) <= 0.15,
]
print(sum(1 for c in checks if c), len(checks))
PYEOF
)"
    passed=$((passed + ${hp:-0})); total=$((total + ${ht:-0}))
  fi

  popd >/dev/null
  echo "$passed $total"
}

echo "=== OUTCOME BENCHMARK · $RUNS run(s)/arm · model=${MODEL:-default} · $STAMP ==="
echo "${MODEL:-default}" > "$OUT/model.txt"
printf '%-16s %-10s %-8s %s\n' TASK ARM SCORE DETAIL
SUMMARY="$OUT/summary.tsv"; : > "$SUMMARY"
INVALID_TOTAL=0

for TASKDIR in "$BENCH/tasks"/*/; do
  TASK="$(basename "$TASKDIR")"
  [[ -n "$ONLY" && "$TASK" != "$ONLY" ]] && continue
  PROMPT="$(cat "$TASKDIR/task.md")"

  for ARM in treatment control; do
    armpass=0; armtotal=0; arminvalid=0
    for i in $(seq 1 "$RUNS"); do
      D="$WORK/$TASK-$ARM-$i"; mkdir -p "$D/src"
      cp -R "$TASKDIR/seed/." "$D/" 2>/dev/null
      # An existing codebase, when the task ships one. This is what lets a task
      # measure reuse — whether the agent extends what is there or writes a
      # second component that does the same job.
      if [[ -d "$TASKDIR/existing" ]]; then
        cp -R "$TASKDIR/existing/." "$D/" 2>/dev/null
      fi
      cp "$BENCH/template-package.json" "$D/package.json"
      ln -s "$TEMPLATE" "$D/node_modules"

      # A task may ship checkpoints/ — sequential prompts against the same
      # sandbox, resumed in one session so context carries forward. This is
      # the long-horizon regime; single prompts cannot show degradation.
      PROMPTS=()
      if [[ -d "$TASKDIR/checkpoints" ]]; then
        while IFS= read -r cp; do PROMPTS+=("$(cat "$cp")"); done \
          < <(find "$TASKDIR/checkpoints" -name "*.md" | sort)
      else
        PROMPTS=("$PROMPT")
      fi
      SID=$(uuidgen | tr "[:upper:]" "[:lower:]")

      if [[ "$ARM" == "treatment" ]]; then
        # The inventory ships with the plugin, so it is generated only here.
        [[ -d "$TASKDIR/existing" ]] && python3 "$ROOT/scripts/scan-project.py" "$D" >/dev/null 2>&1
        for ci in "${!PROMPTS[@]}"; do
          if [[ "$ci" -eq 0 ]]; then SESS=(--session-id "$SID"); else SESS=(--resume "$SID"); fi
          (cd "$D" && claude --plugin-dir "$ROOT" ${MODEL:+--model "$MODEL"} "${SESS[@]}" \
              --allowedTools "Read" "Write" "Edit" "Glob" "Grep" "Bash" "Skill" "Task" "Agent" \
              -p "${PROMPTS[$ci]}" < /dev/null >> "$OUT/$TASK-$ARM-$i.log" 2>&1)
        done
      else
        for ci in "${!PROMPTS[@]}"; do
          if [[ "$ci" -eq 0 ]]; then SESS=(--session-id "$SID"); else SESS=(--resume "$SID"); fi
          (cd "$D" && claude ${MODEL:+--model "$MODEL"} "${SESS[@]}" \
              --allowedTools "Read" "Write" "Edit" "Glob" "Grep" "Bash" \
              -p "${PROMPTS[$ci]}" < /dev/null >> "$OUT/$TASK-$ARM-$i.log" 2>&1)
        done
      fi
      # A run that never happened is not a zero — scoring it as one lets a
      # rate limit or a crash manufacture a delta out of nothing.
      LOG="$OUT/$TASK-$ARM-$i.log"
      # Infrastructure failure = INVALID (excluded). The agent declining to
      # produce the artifact is a REAL failure and must be scored as one.
      # Note src/ is pre-populated when a task ships existing/, so "src is
      # empty" cannot detect a missing artifact — declare it per task instead.
      EXPECT=""
      [[ -f "$TASKDIR/expect_file" ]] && EXPECT=$(cat "$TASKDIR/expect_file")
      if [[ -n "$EXPECT" ]]; then
        [[ -f "$D/$EXPECT" ]] && produced=1 || produced=0
      else
        produced=$(ls "$D/src" 2>/dev/null | wc -l | tr -d ' ')
      fi
      if grep -qiE "usage limit|session limit|Not logged in|rate.?limit|API Error" "$LOG" 2>/dev/null; then
        why=$(grep -oiE "usage limit|session limit|Not logged in|rate.?limit|API Error" "$LOG" 2>/dev/null | head -1)
        arminvalid=$((arminvalid + 1)); INVALID_TOTAL=$((INVALID_TOTAL + 1))
        printf '%-16s %-10s %-8s %s\n' "$TASK" "$ARM#$i" "INVALID" "${why:-no file produced} — excluded"
        continue
      fi

      if [[ "${produced:-1}" -eq 0 ]]; then
        nspec=$(grep -c "^\s*test(" "$TASKDIR"/assert/*.* 2>/dev/null | awk -F: '{s+=$2} END{print s+0}')
        armpass=$((armpass + 0)); armtotal=$((armtotal + 2 + ${nspec:-6}))
        printf '%-16s %-10s %-8s %s\n' "$TASK" "$ARM#$i" "0/$((2 + ${nspec:-6}))" "did not produce $EXPECT — scored as failure"
        continue
      fi

      mkdir -p "$D/assert" && cp -R "$TASKDIR/assert/." "$D/assert/"
      read -r p t <<<"$(score_run "$D")"
      armpass=$((armpass + p)); armtotal=$((armtotal + t))
      printf '%-16s %-10s %-8s %s\n' "$TASK" "$ARM#$i" "$p/$t" "$(ls "$D/src" 2>/dev/null | tr '\n' ' ')"
    done
    valid=$((RUNS - arminvalid))
    pct=$(node -e "console.log(${armtotal:-0}?(${armpass}/${armtotal}).toFixed(3):'0.000')")
    echo -e "$TASK\t$ARM\t$armpass\t$armtotal\t$pct\t$valid" >> "$SUMMARY"
  done
done

echo
echo "=== RESULTS ==="
node "$BENCH/report.js" "$SUMMARY"
if [[ "$INVALID_TOTAL" -gt 0 ]]; then
  echo "WARNING: $INVALID_TOTAL run(s) were INVALID (limit/error/no output) and excluded."
fi
echo "artifacts: $OUT"
