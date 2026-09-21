#!/usr/bin/env python3
"""
PostToolUse hook — verification on the build path, not behind a slash command.

Why this exists:

Every ablation this plugin has run says the same thing. Injecting standards a
capable model already knows moves nothing: zero delta on 7 of 10 eval cases and
on both artifact-graded benchmark tasks. The founding insight — "a hook is not a
suggestion" — was right and was aimed at the wrong half. Engagement was made
deterministic and measured worthless; verification, the half that produces
evidence, was left as prose ("re-read your own diff") behind a command a user
has to remember to type.

This closes that. When the agent writes a source file, its own linter runs and
real errors come straight back to it. A weak model that writes a type error is
told the exact error and fixes it — capability transfer that no amount of prose
achieves. A strong model stops asserting the code is fine and gets it checked.

Design constraints, learned the hard way:
  - FAST. Scoped to the one file just written. A project-wide typecheck on every
    keystroke would make the plugin unusable, so tsc and the test suite stay in
    scripts/verify.sh at review time.
  - SILENT unless it has something real. No config, no linter, no project — exit
    0 and say nothing. A hook that nags on every write gets disabled, and then
    it protects nothing.
  - NEVER wedge the session. Bounded attempts per file, a hard timeout, and any
    unexpected exception exits 0. Blocking forever on something the agent cannot
    fix is worse than not checking at all.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile

CHECKABLE = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
ESLINT_CONFIGS = (
    "eslint.config.js", "eslint.config.mjs", "eslint.config.cjs", "eslint.config.ts",
    ".eslintrc", ".eslintrc.js", ".eslintrc.cjs", ".eslintrc.json", ".eslintrc.yml",
)
TIMEOUT_S = 20
MAX_BLOCKS_PER_FILE = 3  # then stop blocking: the agent is stuck, let a human see it


def project_root(path: str) -> str | None:
    d = os.path.dirname(os.path.abspath(path))
    while True:
        if os.path.isfile(os.path.join(d, "package.json")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def has_eslint(root: str) -> bool:
    if not any(os.path.exists(os.path.join(root, c)) for c in ESLINT_CONFIGS):
        return False
    return os.path.isdir(os.path.join(root, "node_modules", "eslint"))


def attempts_path(file_path: str) -> str:
    key = hashlib.sha256(os.path.abspath(file_path).encode()).hexdigest()[:16]
    return os.path.join(tempfile.gettempdir(), f"fa-verify-{key}")


def bump_attempts(file_path: str) -> int:
    p = attempts_path(file_path)
    try:
        n = int(open(p).read().strip() or "0")
    except (OSError, ValueError):
        n = 0
    n += 1
    try:
        open(p, "w").write(str(n))
    except OSError:
        pass
    return n


def clear_attempts(file_path: str) -> None:
    try:
        os.unlink(attempts_path(file_path))
    except OSError:
        pass


def lint_errors(root: str, file_path: str) -> list[str]:
    """ESLint on the single written file. Errors only — warnings are not worth
    interrupting for, and a hook that interrupts for everything gets removed."""
    try:
        proc = subprocess.run(
            ["npx", "--no-install", "eslint", file_path, "--format", "json"],
            cwd=root, capture_output=True, text=True, timeout=TIMEOUT_S,
        )
    except (subprocess.TimeoutExpired, OSError):
        return []

    try:
        results = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        return []

    out: list[str] = []
    for f in results:
        for m in f.get("messages", []):
            if m.get("severity") != 2:
                continue
            rule = m.get("ruleId") or "parse-error"
            out.append(f"  line {m.get('line', '?')}  {rule}  {m.get('message', '')}")
    return out


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("path") or ""
    if not file_path or os.path.splitext(file_path)[1] not in CHECKABLE:
        return 0
    if not os.path.isfile(file_path):
        return 0
    if f"{os.sep}node_modules{os.sep}" in file_path:
        return 0

    root = project_root(file_path)
    if not root or not has_eslint(root):
        return 0  # nothing to check against — stay quiet

    errors = lint_errors(root, file_path)
    if not errors:
        clear_attempts(file_path)
        return 0

    n = bump_attempts(file_path)
    if n > MAX_BLOCKS_PER_FILE:
        # Three tries is enough. Surface it without wedging the session.
        clear_attempts(file_path)
        print(
            f"frontend-axiom: {len(errors)} lint error(s) still present in "
            f"{os.path.relpath(file_path, root)} after {MAX_BLOCKS_PER_FILE} attempts. "
            "Not blocking again — mention them to the user rather than silently moving on.",
            file=sys.stderr,
        )
        return 2

    rel = os.path.relpath(file_path, root)
    shown = errors[:10]
    more = f"\n  …and {len(errors) - 10} more" if len(errors) > 10 else ""
    print(
        f"frontend-axiom: {rel} has {len(errors)} lint error(s). Fix them before "
        f"continuing — do not describe this file as done.\n"
        + "\n".join(shown) + more,
        file=sys.stderr,
    )
    return 2  # exit 2 sends stderr back to the model


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)  # a verification hook must never break the session
