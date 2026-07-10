#!/usr/bin/env python3
"""Wrap a function boundary with `ExceptionTrackerDecorator`."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tbot223_base.exception_tracker import ExceptionTrackerDecorator
from tbot223_base.result import Result


@ExceptionTrackerDecorator(mask_presets=("private", "traceback", "system_info"))
def parse_count(raw_value: str) -> int:
    return 100 // int(raw_value)


def describe_call(raw_value: str) -> None:
    output = parse_count(raw_value)

    if isinstance(output, Result):
        print(f"{raw_value!r} failed:", output.error)
        print("context:", output.context)
        return

    print(f"{raw_value!r} succeeded:", output)


def main() -> None:
    describe_call("5")
    describe_call("0")
    describe_call("not-a-number")


if __name__ == "__main__":
    main()
