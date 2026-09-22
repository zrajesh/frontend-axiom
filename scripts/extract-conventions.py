#!/usr/bin/env python3
"""
Frontend Axiom — convention extractor.

Why this exists:

Five ablations on a capable model measured ~zero delta: knowledge injection,
component reuse at two scales, self-verification with a shell available, and
structural erosion across checkpoints. The one mechanism that measured +1.00
was an arbitrary house convention — a rule whose answer exists nowhere in
training data and nowhere in the repository's behaviour, only in the team's
preference.

That is the whole finding. A capable model does not need help with anything it
can derive; it needs the things it cannot possibly know. And unlike a knowledge
base, which depreciates as models improve, arbitrary conventions stay
unguessable by construction.

So instead of shipping one team's rule, this infers each repository's own.

The hard part is telling a convention from a coincidence. If 95% of components
use named exports that is a rule worth enforcing; at 55% it is noise, and
emitting it would be worse than saying nothing — an agent told a false rule
will "fix" correct code. Every detector therefore reports a ratio, and only
findings above a confidence floor are emitted, with the dissenting files named
so a human can check.

Usage:
  extract-conventions.py [dir]           write .frontend-axiom/conventions.md
  extract-conventions.py [dir] --json    print findings as JSON
  extract-conventions.py [dir] --min 0.9 raise the confidence floor
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter

SKIP_DIRS = {
    "node_modules", ".git", ".next", "dist", "build", "out", "coverage",
    ".turbo", ".cache", "__pycache__", ".frontend-axiom", ".vercel",
}
COMPONENT_EXT = {".tsx", ".jsx"}
CODE_EXT = COMPONENT_EXT | {".ts", ".js", ".mjs", ".cjs"}

DEFAULT_MIN_CONFIDENCE = 0.80
MIN_SAMPLES = 5  # below this, "90%" is one file's opinion


def iter_files(root: str, exts: set[str]):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if os.path.splitext(fn)[1] in exts:
                yield os.path.join(dirpath, fn)


def read(p: str) -> str:
    try:
        return open(p, encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def verdict(counts: Counter, min_conf: float) -> tuple[str, float, int] | None:
    """Dominant value, its share, and the sample size — or None if too weak."""
    total = sum(counts.values())
    if total < MIN_SAMPLES:
        return None
    value, n = counts.most_common(1)[0]
    ratio = n / total
    if ratio < min_conf:
        return None
    return value, round(ratio, 3), total


# ---------------------------------------------------------------- detectors

def detect_export_style(files: list[str]) -> Counter:
    c = Counter()
    for p in files:
        src = read(p)
        base = os.path.splitext(os.path.basename(p))[0]
        if not base[:1].isupper():
            continue  # components only
        if re.search(rf"export\s+default\s+(?:function\s+)?{re.escape(base)}\b", src) or \
           re.search(r"export\s+default\s+function\s*\(", src):
            c["default export"] += 1
        elif re.search(rf"export\s+(?:function|const)\s+{re.escape(base)}\b", src):
            c["named export"] += 1
    return c


def detect_file_naming(files: list[str]) -> Counter:
    c = Counter()
    for p in files:
        base = os.path.splitext(os.path.basename(p))[0]
        if base in {"index", "page", "layout", "route", "loading", "error"}:
            continue
        if re.fullmatch(r"[A-Z][A-Za-z0-9]*", base):
            c["PascalCase"] += 1
        elif re.fullmatch(r"[a-z][a-z0-9]*(-[a-z0-9]+)+", base):
            c["kebab-case"] += 1
        elif re.fullmatch(r"[a-z][A-Za-z0-9]*", base):
            c["camelCase"] += 1
    return c


def detect_import_style(files: list[str]) -> Counter:
    c = Counter()
    for p in files:
        for m in re.finditer(r"""from\s+["']([^"']+)["']""", read(p)):
            spec = m.group(1)
            if spec.startswith("@/") or spec.startswith("~/"):
                c["path alias (@/…)"] += 1
            elif spec.startswith("../"):
                c["relative (../)"] += 1
    return c


def detect_props_style(files: list[str]) -> Counter:
    c = Counter()
    for p in files:
        src = read(p)
        c["type alias"] += len(re.findall(r"\btype\s+\w*Props\s*=", src))
        c["interface"] += len(re.findall(r"\binterface\s+\w*Props\b", src))
    return Counter({k: v for k, v in c.items() if v})


def detect_test_location(root: str) -> Counter:
    c = Counter()
    for p in iter_files(root, CODE_EXT):
        base = os.path.basename(p)
        if ".test." in base or ".spec." in base:
            c["colocated (*.test.ts beside source)" if "__tests__" not in p
              else "separate __tests__/ directory"] += 1
    return c


def detect_client_directive(files: list[str]) -> Counter:
    c = Counter()
    for p in files:
        src = read(p)
        if "useState" in src or "onClick" in src or "useEffect" in src:
            c['"use client" on interactive components'] += 1 if '"use client"' in src or "'use client'" in src else 0
            c["no directive"] += 0 if '"use client"' in src or "'use client'" in src else 1
    return Counter({k: v for k, v in c.items() if v})


def detect_styling(files: list[str]) -> Counter:
    c = Counter()
    for p in files:
        src = read(p)
        if re.search(r'className="[^"]*\b(flex|grid|p-\d|m-\d|text-|bg-)', src):
            c["Tailwind utility classes"] += 1
        elif re.search(r"from\s+[\"'][^\"']+\.module\.(css|scss)[\"']", src):
            c["CSS Modules"] += 1
        elif re.search(r"styled\.\w+`", src):
            c["styled-components"] += 1
    return c


DETECTORS = [
    ("Component exports", detect_export_style, "component files",
     "Match it — a file exporting the other way is the odd one out."),
    ("Component file naming", detect_file_naming, "source files", ""),
    ("Imports across modules", detect_import_style, "import statements",
     "Use the same form for anything outside the current folder."),
    ("Props types", detect_props_style, "props declarations", ""),
    ("Styling", detect_styling, "component files", ""),
]


def extract(root: str, min_conf: float) -> list[dict]:
    comps = list(iter_files(root, COMPONENT_EXT))
    allsrc = list(iter_files(root, CODE_EXT))
    findings: list[dict] = []

    for label, fn, unit, note in DETECTORS:
        counts = fn(comps if fn is not detect_file_naming else allsrc)
        v = verdict(counts, min_conf)
        if not v:
            continue
        value, ratio, total = v
        dissent = {k: n for k, n in counts.items() if k != value}
        findings.append({
            "convention": label, "rule": value, "confidence": ratio,
            "sample": total, "unit": unit, "note": note,
            "exceptions": dissent,
        })

    v = verdict(detect_test_location(root), min_conf)
    if v:
        value, ratio, total = v
        findings.append({"convention": "Test location", "rule": value,
                         "confidence": ratio, "sample": total,
                         "unit": "test files", "note": "", "exceptions": {}})
    return findings


def render(findings: list[dict], root: str, min_conf: float) -> str:
    out = ["# Conventions in this repository", ""]
    out.append(
        "Inferred from the code itself, not assumed. These are the arbitrary choices "
        "this team has already made — the kind of thing no model can know from training, "
        "and the one category measured to change a capable model's output."
    )
    out.append("")
    out.append(f"Only patterns at or above {int(min_conf * 100)}% consistency across at least "
               f"{MIN_SAMPLES} samples are listed. A weaker pattern is a coincidence, and an "
               "agent told a false rule will 'fix' correct code.")
    out.append("")

    if not findings:
        out.append("_No convention met the confidence floor. Either the repository is small, "
                   "or it genuinely is not consistent yet — in which case there is nothing "
                   "honest to enforce._")
        return "\n".join(out) + "\n"

    out.append("| Convention | This repo does | Consistency | Sample |")
    out.append("|---|---|---|---|")
    for f in findings:
        out.append(f"| {f['convention']} | **{f['rule']}** | "
                   f"{int(f['confidence'] * 100)}% | {f['sample']} {f['unit']} |")
    out.append("")
    out.append("**Follow these.** Where a file disagrees, it is the exception, not the licence.")
    out.append("")

    noted = [f for f in findings if f.get("note")]
    if noted:
        for f in noted:
            out.append(f"- **{f['convention']}** — {f['note']}")
        out.append("")

    exc = [(f, f["exceptions"]) for f in findings if f.get("exceptions")]
    if exc:
        out.append("## Dissenting files")
        out.append("")
        out.append("Listed so a human can decide whether these are deliberate or drift:")
        out.append("")
        for f, d in exc:
            detail = ", ".join(f"{k} ({n})" for k, n in d.items())
            out.append(f"- {f['convention']}: {detail}")
        out.append("")

    out.append("---")
    out.append("")
    out.append("_Regenerate after refactors: `python3 <plugin>/scripts/extract-conventions.py`_")
    return "\n".join(out) + "\n"


def main() -> int:
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = os.path.abspath(argv[0]) if argv else os.getcwd()
    min_conf = DEFAULT_MIN_CONFIDENCE
    if "--min" in sys.argv:
        try:
            min_conf = float(sys.argv[sys.argv.index("--min") + 1])
        except (IndexError, ValueError):
            pass

    findings = extract(root, min_conf)
    if "--json" in sys.argv:
        print(json.dumps(findings, indent=2))
        return 0

    dest = os.path.join(root, ".frontend-axiom")
    os.makedirs(dest, exist_ok=True)
    target = os.path.join(dest, "conventions.md")
    open(target, "w", encoding="utf-8").write(render(findings, root, min_conf))
    print(f"wrote {target}  ({len(findings)} convention(s) above {int(min_conf*100)}% confidence)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
