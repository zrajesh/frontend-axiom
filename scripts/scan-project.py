#!/usr/bin/env python3
"""
Frontend Axiom — project inventory scanner.

Why this exists, specifically:

The benchmark showed that on general frontend tasks a strong model already
meets the standards — 7 of 10 eval cases and both outcome tasks measured a
zero delta. Re-teaching the model what a Core Web Vital is buys nothing.

What a model can NEVER know is *your* codebase: that you already have a
`<Button>` with a `variant` prop, that your orders endpoint returns
`reference` and not `orderNumber`, that your spacing scale stops at 96. That
is unguessable by construction, and it is where an agent actually goes wrong —
by cheerfully writing a ninth button component.

This scans a project and writes `.frontend-axiom/inventory.md`, which the
agents read before creating anything.

Deliberately regex-based rather than a real TS parser: it must run anywhere
with zero install, tolerate broken syntax, and never block a session. It
aims for high recall on the common shapes and is explicit about being a map,
not a compiler.

Usage: scan-project.py [project_dir] [--stdout]
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    "node_modules", ".git", ".next", "dist", "build", "out", "coverage",
    ".turbo", ".cache", "__pycache__", ".frontend-axiom", ".vercel",
}
CODE_EXT = {".tsx", ".jsx", ".ts", ".js"}
MAX_FILES = 4000

# export default function Foo(  |  export function Foo(  |  export const Foo = (
COMPONENT_RE = re.compile(
    r"export\s+(?:default\s+)?(?:async\s+)?function\s+([A-Z]\w*)\s*\(|"
    r"export\s+const\s+([A-Z]\w*)\s*[:=]"
)
HOOK_RE = re.compile(r"export\s+(?:default\s+)?(?:async\s+)?(?:function|const)\s+(use[A-Z]\w*)")
PROPS_RE = re.compile(
    r"(?:type|interface)\s+(\w*(?:Props|Params))\s*(?:=\s*)?\{([^}]{0,600})\}", re.S
)
ENDPOINT_RE = re.compile(
    r"(\w+)\s*:\s*builder\.(query|mutation)\s*[<(]", re.S
)
URL_RE = re.compile(r"""query\s*:\s*\(?[^)]*\)?\s*=>\s*[`'"]([^`'"]+)""")
CSS_VAR_RE = re.compile(r"(--[a-z][\w-]*)\s*:")


def iter_files(root: Path):
    seen = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if Path(fn).suffix in CODE_EXT:
                seen += 1
                if seen > MAX_FILES:
                    return
                yield Path(dirpath) / fn


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


FIELD_RE = re.compile(r"(?:^|[{;,\n])\s*([A-Za-z_$][\w$]*)\s*\??\s*:")


def summarize_props(body: str) -> str:
    """Field names from a props body.

    Must handle both multi-line declarations and the single-line form
    (`{ variant: "a" | "b"; size?: "sm" }`), so it scans the whole body for
    `name:` after a delimiter rather than reading line by line. Union members
    are quoted and carry no colon, so they do not register as fields.
    """
    body = re.sub(r"//[^\n]*", "", body)
    fields: list[str] = []
    for name in FIELD_RE.findall(body):
        if name not in fields:
            fields.append(name)
        if len(fields) >= 10:
            fields.append("…")
            break
    return ", ".join(fields)


def scan(root: Path) -> str:
    components: list[tuple[str, str, str]] = []   # name, relpath, props
    hooks: list[tuple[str, str]] = []
    endpoints: list[tuple[str, str, str]] = []
    tokens: set[str] = set()
    files_scanned = 0

    for path in iter_files(root):
        files_scanned += 1
        text = read(path)
        if not text:
            continue
        rel = str(path.relative_to(root))

        propmap = {m.group(1): summarize_props(m.group(2)) for m in PROPS_RE.finditer(text)}

        if path.suffix in {".tsx", ".jsx"} and ("return (" in text or "=> (" in text or "<" in text):
            for m in COMPONENT_RE.finditer(text):
                name = m.group(1) or m.group(2)
                if not name or name.endswith("Props"):
                    continue
                props = propmap.get(f"{name}Props") or (
                    next(iter(propmap.values())) if len(propmap) == 1 else ""
                )
                components.append((name, rel, props))

        for m in HOOK_RE.finditer(text):
            hooks.append((m.group(1), rel))

        if "builder." in text:
            urls = URL_RE.findall(text)
            for i, m in enumerate(ENDPOINT_RE.finditer(text)):
                endpoints.append((m.group(1), m.group(2), urls[i] if i < len(urls) else ""))

        if path.suffix in {".css", ".scss"} or "createGlobalStyle" in text:
            tokens.update(CSS_VAR_RE.findall(text))

    for css in list(root.rglob("*.css"))[:60]:
        if any(s in css.parts for s in SKIP_DIRS):
            continue
        tokens.update(CSS_VAR_RE.findall(read(css)))

    # de-dupe, keep first occurrence
    seen: set[str] = set()
    comps = [c for c in components if not (c[0] in seen or seen.add(c[0]))]
    seen = set()
    hks = [h for h in hooks if not (h[0] in seen or seen.add(h[0]))]

    out: list[str] = []
    out.append("# Project inventory")
    out.append("")
    out.append(
        "Generated by Frontend Axiom from this repository. **Read this before creating "
        "any component, hook, or endpoint.** If something here already does the job, "
        "extend it — do not write a second one."
    )
    out.append("")
    out.append(f"Scanned {files_scanned} source file(s).")
    out.append("")

    out.append(f"## Components ({len(comps)})")
    out.append("")
    if comps:
        out.append("| Component | Path | Props |")
        out.append("|---|---|---|")
        for name, rel, props in sorted(comps)[:200]:
            out.append(f"| `{name}` | `{rel}` | {props or '—'} |")
    else:
        out.append("_None found._")
    out.append("")

    out.append(f"## Hooks ({len(hks)})")
    out.append("")
    if hks:
        out.append("| Hook | Path |")
        out.append("|---|---|")
        for name, rel in sorted(hks)[:120]:
            out.append(f"| `{name}` | `{rel}` |")
    else:
        out.append("_None found._")
    out.append("")

    out.append(f"## API endpoints ({len(endpoints)})")
    out.append("")
    if endpoints:
        out.append("| Endpoint | Kind | URL |")
        out.append("|---|---|---|")
        for name, kind, url in sorted(endpoints)[:120]:
            out.append(f"| `{name}` | {kind} | `{url or '—'}` |")
        out.append("")
        out.append(
            "**Use these exact names and shapes.** Do not invent an endpoint or a field "
            "that is not listed here — ask instead."
        )
    else:
        out.append("_None found._")
    out.append("")

    if tokens:
        out.append(f"## Design tokens ({len(tokens)})")
        out.append("")
        out.append(", ".join(f"`{t}`" for t in sorted(tokens)[:80]))
        out.append("")
        out.append("Use these. Never hardcode a value that one of them already expresses.")
        out.append("")

    out.append("---")
    out.append("")
    out.append(
        "_Regenerate after adding components:_ "
        "`python3 <plugin>/scripts/scan-project.py`. This is a map produced by pattern "
        "matching, not a compiler — treat a miss as a gap in the map, not proof the code "
        "does not exist._"
    )
    return "\n".join(out) + "\n"


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--stdout"]
    root = Path(args[0]).resolve() if args else Path.cwd()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2

    report = scan(root)
    if "--stdout" in sys.argv:
        print(report)
        return 0

    dest = root / ".frontend-axiom"
    dest.mkdir(exist_ok=True)
    target = dest / "inventory.md"
    target.write_text(report, encoding="utf-8")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
