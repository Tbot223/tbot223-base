#!/usr/bin/env python3
"""Require the expected mypy error at every marked invalid consumer line."""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE = pathlib.Path("tests/typecheck/invalid_result_api.py")


def main() -> int:
    expected = set()
    for number, line in enumerate(
        (ROOT / FIXTURE).read_text(encoding="utf-8").splitlines(), 1
    ):
        marker = re.search(r"# expect-error: ([a-z-]+)\s*$", line)
        if marker:
            expected.add((number, marker.group(1)))
    if not expected:
        print("No expected type errors were declared.", file=sys.stderr)
        return 1

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            "--no-incremental",
            "--no-pretty",
            "--show-error-codes",
            str(FIXTURE),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    actual = set()
    unexpected = []
    for line in result.stdout.splitlines():
        if ": error:" not in line:
            continue
        diagnostic = re.fullmatch(
            r"tests[/\\]typecheck[/\\]invalid_result_api\.py:(\d+)(?::\d+)?: error: .*\[([a-z-]+)\]",
            line,
        )
        if diagnostic:
            actual.add((int(diagnostic.group(1)), diagnostic.group(2)))
        else:
            unexpected.append(line)
    if result.returncode != 1 or actual != expected or unexpected:
        print(result.stdout, end="", file=sys.stderr)
        print(result.stderr, end="", file=sys.stderr)
        print(f"Missing expected errors: {sorted(expected - actual)}", file=sys.stderr)
        print(
            f"Unexpected errors: {sorted(actual - expected)} {unexpected}",
            file=sys.stderr,
        )
        return 1
    print(
        f"Rejected-type contract passed: {len(expected)} individually verified diagnostics."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
