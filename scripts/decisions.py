#!/usr/bin/env python3
"""
Frontend Axiom — decision capture.

Why this exists, precisely:

Six ablations on a capable model measured ~zero delta: knowledge injection,
component reuse at two scales, self-verification with a shell available,
structural erosion across checkpoints, and inferred house conventions. One
measured +1.00.

The winner was not "an arbitrary rule" — that framing was tested and
falsified. When the same kind of rule was *demonstrated* by twelve example
files, the control arm inferred it by reading them and the delta vanished. The
rule that produced +1.00 existed **only in a document and nowhere in the
code**.

So the boundary is exact: delta requires information absent from training AND
absent from the repository. In practice that is:

  - a decision made in a meeting and never written down
  - an approach tried and rejected, where the code shows no trace of the attempt
  - a deliberate exception ("not here, even though we do it everywhere else")
  - a rule for NEW code that the OLD code contradicts, mid-migration
  - a constraint from outside the codebase entirely

An agent will confidently violate every one of those, because nothing it can
read says otherwise. Often the code actively argues the opposite.

This stores them, and surfaces the relevant ones — matched by keyword and by
path — rather than injecting the whole file. A team with 200 decisions cannot
afford to pay for 200 every turn.

Usage:
  decisions.py add "title" --why "..." [--instead "..."] [--paths "src/x/**"] [--tags a,b]
  decisions.py list
  decisions.py match "prompt text" [--files a.tsx b.tsx]
  decisions.py stale [--days 180]
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import sys

STORE_DIR = ".frontend-axiom"
STORE = "decisions.json"
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "for", "with", "this", "that", "it",
    "is", "are", "was", "be", "to", "of", "in", "on", "at", "we", "our", "use",
    "using", "used", "add", "new", "make", "do", "not", "should", "can", "will",
}


def store_path(root: str) -> str:
    return os.path.join(root, STORE_DIR, STORE)


def load(root: str) -> list[dict]:
    p = store_path(root)
    if not os.path.isfile(p):
        return []
    try:
        data = json.load(open(p, encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save(root: str, items: list[dict]) -> None:
    os.makedirs(os.path.join(root, STORE_DIR), exist_ok=True)
    json.dump(items, open(store_path(root), "w", encoding="utf-8"), indent=2)


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:48] or "decision"


def words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z0-9-]{2,}", (text or "").lower())
            if w not in STOPWORDS}


def cmd_add(root: str, args) -> int:
    items = load(root)
    item = {
        "id": slug(args.title),
        "title": args.title.strip(),
        "why": (args.why or "").strip(),
        "instead": (args.instead or "").strip(),
        "paths": [p.strip() for p in (args.paths or "").split(",") if p.strip()],
        "tags": [t.strip().lower() for t in (args.tags or "").split(",") if t.strip()],
        "decided": dt.date.today().isoformat(),
        "by": args.by or os.environ.get("USER", "unknown"),
    }
    if not item["why"]:
        print("refusing to store a decision with no --why.\n"
              "A rule without its reason gets cargo-culted, and nobody can tell "
              "later whether it still applies.", file=sys.stderr)
        return 2

    items = [i for i in items if i.get("id") != item["id"]]  # replace by id
    items.append(item)
    save(root, items)
    print(f"recorded: {item['id']}")
    return 0


def relevance(item: dict, text: str, files: list[str]) -> int:
    """How strongly this decision bears on what is happening right now."""
    score = 0
    tokens = words(text)

    for tag in item.get("tags", []):
        if tag in tokens:
            score += 3
    overlap = tokens & (words(item.get("title", "")) | words(item.get("instead", "")))
    score += min(len(overlap), 4)

    for pattern in item.get("paths", []):
        for f in files:
            norm = f.replace(os.sep, "/")
            if fnmatch.fnmatch(norm, pattern) or fnmatch.fnmatch(os.path.basename(norm), pattern):
                score += 5  # a path hit is the strongest signal there is
                break
    return score


def cmd_match(root: str, args) -> int:
    items = load(root)
    if not items:
        return 0
    scored = [(relevance(i, args.text, args.files or []), i) for i in items]
    # 5 = one path hit, or two independent keyword signals. A single weak tag
    # match ("page") surfacing an unrelated decision is how a tool like this
    # trains people to ignore it, so one signal is deliberately not enough.
    hits = [i for s, i in sorted(scored, key=lambda x: -x[0]) if s >= 5][: args.limit]
    if not hits:
        return 0

    if args.json:
        print(json.dumps(hits, indent=2))
        return 0

    print("DECISIONS THIS TEAM HAS ALREADY MADE — they override what the code suggests:")
    for i in hits:
        print(f"\n  {i['title']}")
        print(f"    why: {i['why']}")
        if i.get("instead"):
            print(f"    instead: {i['instead']}")
        if i.get("paths"):
            print(f"    applies to: {', '.join(i['paths'])}")
        print(f"    decided {i['decided']} by {i['by']}")
    print("\n  These are not inferable from the codebase — in some cases the existing "
          "code contradicts them. Follow them, and say so if you believe one is wrong.")
    return 0


def cmd_list(root: str, args) -> int:
    items = load(root)
    if not items:
        print("no decisions recorded yet")
        return 0
    for i in items:
        scope = ", ".join(i.get("paths") or i.get("tags") or []) or "global"
        print(f"  {i['id']:40} {scope:28} {i['decided']}")
    return 0


def cmd_stale(root: str, args) -> int:
    """Old decisions are how a codebase ends up cargo-culting its own history."""
    cutoff = dt.date.today() - dt.timedelta(days=args.days)
    old = []
    for i in load(root):
        try:
            if dt.date.fromisoformat(i["decided"]) < cutoff:
                old.append(i)
        except (ValueError, KeyError):
            continue
    if not old:
        print(f"no decisions older than {args.days} days")
        return 0
    print(f"{len(old)} decision(s) older than {args.days} days — confirm they still hold:")
    for i in old:
        print(f"  {i['id']}  (decided {i['decided']} by {i['by']})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="record and surface team decisions")
    ap.add_argument("--root", default=os.getcwd())
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("title")
    a.add_argument("--why", required=True)
    a.add_argument("--instead", default="")
    a.add_argument("--paths", default="", help="comma-separated globs, e.g. 'src/checkout/**'")
    a.add_argument("--tags", default="", help="comma-separated keywords")
    a.add_argument("--by", default="")

    m = sub.add_parser("match")
    m.add_argument("text")
    m.add_argument("--files", nargs="*", default=[])
    m.add_argument("--limit", type=int, default=4)
    m.add_argument("--json", action="store_true")

    sub.add_parser("list")

    s = sub.add_parser("stale")
    s.add_argument("--days", type=int, default=180)

    args = ap.parse_args()
    root = os.path.abspath(args.root)
    return {"add": cmd_add, "match": cmd_match, "list": cmd_list, "stale": cmd_stale}[args.cmd](root, args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
