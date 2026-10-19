#!/usr/bin/env python3
"""Deterministic size gate. No inference. Fails on new bloat or growth.

Usage: python scripts/size_ratchet.py [--update] [--base <git-ref>]

  --base: enable the top-level-unit gate, comparing AST top-level
          FunctionDef/AsyncFunctionDef/ClassDef counts vs that ref
          (CI passes the PR base ref; pushes to main pass none, so the
          line ratchet runs without the diff gate)
  --update: rewrite size-ratchet.json from current state (run after a
          split to lower budgets - never to raise one)

Counts .py files only. Excluded paths: .git, node_modules, dist/, build/,
.venv, data/, examples/.

Thresholds:
  800   flag: files over this many non-blank lines must be ratcheted
  2000  hard: changed files over this may not gain top-level units
  x3    test file budget multiplier (tests/ dir or *_test.py)

The ratchet is a ratchet: budgets shrink, never grow (outside --update).
"""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

FLAG = 800
HARD = 2000
TEST_MULT = 3
RATCHET = Path("size-ratchet.json")
EXCLUDE = re.compile(
    r"(\.git|node_modules|(^|/)dist/|(^|/)build/|\.venv|(^|/)data/|(^|/)examples/)"
)
UNIT_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def walk(root: Path) -> list[Path]:
    """Collect .py files under root, skipping excluded paths."""
    return [p for p in sorted(root.rglob("*.py")) if not EXCLUDE.search(p.as_posix())]


def count_nonblank(p: Path) -> int:
    """Count non-blank lines in a file."""
    return sum(
        1
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip()
    )


def top_units_src(src: str) -> int:
    """Count top-level def / async def / class nodes in module source."""
    tree = ast.parse(src)
    return sum(isinstance(n, UNIT_NODES) for n in tree.body)


def git_out(*args: str) -> str:
    """Run git with fixed argv (no shell) and return stdout."""
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True
    ).stdout


def main() -> int:
    """Run the size gate; return 0 on pass, 1 on fail."""
    args = sys.argv[1:]
    update = "--update" in args
    base = ""
    if "--base" in args:
        i = args.index("--base")
        if i + 1 < len(args):
            base = args[i + 1]
    base = base.strip()

    changed: set[str] = set()
    if base:
        changed = set(git_out("diff", "--name-only", f"{base}...HEAD").split())

    ratchet: dict[str, int] = {}
    if RATCHET.exists():
        ratchet = json.loads(RATCHET.read_text(encoding="utf-8"))

    fail = False
    for f in walk(Path()):
        rel = f.as_posix()
        n = count_nonblank(f)
        is_test = rel.startswith("tests/") or rel.endswith("_test.py")
        mult = TEST_MULT if is_test else 1
        if n > FLAG * mult:
            if rel not in ratchet:
                if update:
                    ratchet[rel] = n
                else:
                    fail = True
                    print(
                        f"NEW BLOAT {rel}: {n} lines > {FLAG * mult} - split, do not ratchet"
                    )
            elif n > ratchet[rel] * mult:
                if update:
                    ratchet[rel] = n
                else:
                    fail = True
                    print(f"GROWTH    {rel}: {n} > budget {ratchet[rel]}")
        if base and n > HARD and rel in changed:
            try:
                prev = top_units_src(git_out("show", f"{base}:{rel}"))
            except subprocess.CalledProcessError:
                prev = 0  # new file at this path
            cur = top_units_src(f.read_text(encoding="utf-8"))
            if cur > prev:
                fail = True
                print(
                    f"EXPORT GATE {rel}: {cur} top-level units (was {prev}) - extract to a sibling module"
                )

    if update:
        RATCHET.write_text(
            json.dumps(dict(sorted(ratchet.items())), indent=2) + "\n", encoding="utf-8"
        )
    print("SIZE GATE: FAIL" if fail else f"SIZE GATE: OK ({len(ratchet)} ratcheted)")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
