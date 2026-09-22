#!/usr/bin/env python3
"""
Frontend Axiom — structural health measurement.

Why this exists:

Four ablations on a capable model measured zero delta — knowledge injection,
reuse at two scales, and self-verification. Single-shot well-specified tasks
are a solved regime; SWE-bench Verified saturates in the low-to-mid 90s.

The regime that is *not* solved is long-horizon iterative work. SlopCodeBench
(arXiv 2603.24755) reports the best agent passing 14.8% of checkpoints, with
structural erosion rising in 77% of trajectories and verbosity in 75.5%, and
agent code measuring 2.3x more verbose and 2.0x more eroded than human code.
Critically, it reports that prompt-engineering interventions improve *initial*
quality while failing to halt the *rate* of degradation.

So this measures the two things that degrade, so they can be gated on:

  structural erosion — complexity concentrating into a few large functions
  verbosity          — the same logic written repeatedly

Deliberately dependency-free and regex-based rather than a real TS parser: it
must run in any repo with no install, tolerate syntax it does not understand,
and never block a session. It approximates cyclomatic complexity by counting
decision points, which is the standard approximation and is stable enough for
*comparison between checkpoints* — which is all a degradation gate needs. It
is not a substitute for a real complexity tool on absolute numbers.

Usage:
  measure-health.py [dir]              measure, write .frontend-axiom/health.json
  measure-health.py [dir] --compare    measure and diff against the saved baseline
  measure-health.py [dir] --json       print the report as JSON
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys

SKIP_DIRS = {
    "node_modules", ".git", ".next", "dist", "build", "out", "coverage",
    ".turbo", ".cache", "__pycache__", ".frontend-axiom", ".vercel", "vendor",
}
CODE_EXT = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}

# Decision points — the standard cyclomatic approximation.
DECISION = re.compile(
    r"(?<![\w.])(if|for|while|case|catch)(?![\w])|&&|\|\||\?\?|(?<![:?])\?(?!\.)"
)
FUNC_START = re.compile(
    r"(?:function\s+\w*\s*\(|"                      # function foo(
    r"(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\(|"  # const foo = (
    r"=>\s*\{|"                                      # => {
    r"^\s*(?:async\s+)?\w+\s*\([^)]*\)\s*\{)"        # method() {
)
COMMENT = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)


def strip_noise(src: str) -> str:
    src = COMMENT.sub("", src)
    src = re.sub(r"'[^'\n]*'|\"[^\"\n]*\"|`[^`]*`", '""', src)  # string bodies
    return src


def iter_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if os.path.splitext(fn)[1] in CODE_EXT and ".test." not in fn and ".spec." not in fn:
                yield os.path.join(dirpath, fn)


def analyse_file(path: str, root: str) -> dict | None:
    try:
        raw = open(path, encoding="utf-8", errors="ignore").read()
    except OSError:
        return None
    src = strip_noise(raw)
    lines = [ln for ln in src.splitlines() if ln.strip()]
    if not lines:
        return None

    # Per-function complexity and length, tracked by brace depth.
    functions: list[dict] = []
    depth = 0
    cur: dict | None = None
    max_nest = 0
    for ln in lines:
        if cur is None and FUNC_START.search(ln):
            cur = {"complexity": 1, "lines": 0, "start_depth": depth, "max_nest": 0}
        if cur is not None:
            cur["lines"] += 1
            cur["complexity"] += len(DECISION.findall(ln))
            cur["max_nest"] = max(cur["max_nest"], depth - cur["start_depth"])
        depth += ln.count("{") - ln.count("}")
        max_nest = max(max_nest, depth)
        if cur is not None and depth <= cur["start_depth"] and cur["lines"] > 1:
            functions.append(cur)
            cur = None
    if cur is not None:
        functions.append(cur)

    comps = [f["complexity"] for f in functions] or [1]
    lens = [f["lines"] for f in functions] or [len(lines)]
    return {
        "path": os.path.relpath(path, root),
        "loc": len(lines),
        "functions": len(functions),
        "max_complexity": max(comps),
        "total_complexity": sum(comps),
        "max_function_lines": max(lens),
        "max_nesting": max([f["max_nest"] for f in functions] or [max_nest]),
    }


def duplication(files: list[str], root: str) -> float:
    """Fraction of 5-line windows that appear more than once across the repo.

    Verbosity in the SlopCodeBench sense is redundant code, and near-identical
    blocks are what that looks like in practice.
    """
    seen: dict[str, int] = {}
    windows = 0
    for path in files:
        try:
            raw = open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        lines = [re.sub(r"\s+", " ", ln).strip() for ln in strip_noise(raw).splitlines()]
        lines = [ln for ln in lines if len(ln) > 12]  # ignore braces and noise
        for i in range(len(lines) - 4):
            key = hashlib.md5("\n".join(lines[i:i + 5]).encode()).hexdigest()
            seen[key] = seen.get(key, 0) + 1
            windows += 1
    if not windows:
        return 0.0
    repeated = sum(c - 1 for c in seen.values() if c > 1)
    return round(repeated / windows, 4)


def measure(root: str) -> dict:
    paths = list(iter_files(root))
    per_file = [r for r in (analyse_file(p, root) for p in paths) if r]
    if not per_file:
        return {"files": 0, "loc": 0, "erosion": {}, "verbosity": {}, "per_file": []}

    loc = sum(f["loc"] for f in per_file)
    total_complexity = sum(f["total_complexity"] for f in per_file)
    worst = sorted(per_file, key=lambda f: -f["max_complexity"])[:5]

    return {
        "files": len(per_file),
        "loc": loc,
        # Structural erosion: complexity concentrating into a few big functions.
        "erosion": {
            "max_complexity": max(f["max_complexity"] for f in per_file),
            "max_function_lines": max(f["max_function_lines"] for f in per_file),
            "max_nesting": max(f["max_nesting"] for f in per_file),
            "complexity_per_loc": round(total_complexity / loc, 4) if loc else 0,
        },
        # Verbosity: the same logic written repeatedly.
        "verbosity": {
            "duplication_ratio": duplication(paths, root),
            "loc_per_file": round(loc / len(per_file), 1),
        },
        "worst_offenders": [
            {"path": f["path"], "max_complexity": f["max_complexity"],
             "max_function_lines": f["max_function_lines"]} for f in worst
        ],
        "per_file": per_file,
    }


# Which direction is bad, and how much movement is worth reporting.
REGRESSIONS = [
    ("erosion", "max_complexity", 1, "a function became more branchy"),
    ("erosion", "max_function_lines", 10, "a function grew"),
    ("erosion", "max_nesting", 1, "nesting got deeper"),
    ("erosion", "complexity_per_loc", 0.02, "complexity per line rose"),
    ("verbosity", "duplication_ratio", 0.02, "more duplicated code"),
]


def compare(base: dict, now: dict) -> list[str]:
    out: list[str] = []
    for group, key, tol, why in REGRESSIONS:
        b = (base.get(group) or {}).get(key)
        n = (now.get(group) or {}).get(key)
        if b is None or n is None:
            continue
        if n - b > tol:
            out.append(f"{group}.{key}: {b} -> {n}  ({why})")
    return out


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = os.path.abspath(args[0]) if args else os.getcwd()
    now = measure(root)

    if "--json" in sys.argv:
        print(json.dumps(now, indent=2))
        return 0

    dest = os.path.join(root, ".frontend-axiom")
    os.makedirs(dest, exist_ok=True)
    target = os.path.join(dest, "health.json")

    if "--compare" in sys.argv and os.path.isfile(target):
        try:
            base = json.load(open(target, encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            base = {}
        regressions = compare(base, now)
        ero, verb = now["erosion"], now["verbosity"]
        print(f"files {now['files']}  loc {now['loc']}  "
              f"max-complexity {ero.get('max_complexity')}  "
              f"dup {verb.get('duplication_ratio')}")
        if regressions:
            print("STRUCTURAL REGRESSION:")
            for r in regressions:
                print("  " + r)
            for w in now["worst_offenders"][:3]:
                print(f"    worst: {w['path']} (complexity {w['max_complexity']}, "
                      f"{w['max_function_lines']} lines)")
            return 1
        print("no structural regression")
        return 0

    json.dump(now, open(target, "w", encoding="utf-8"), indent=2)
    print(f"wrote {target}  (files {now['files']}, loc {now['loc']}, "
          f"max-complexity {now['erosion'].get('max_complexity')})")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
