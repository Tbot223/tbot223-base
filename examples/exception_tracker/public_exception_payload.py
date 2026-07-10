#!/usr/bin/env python3
"""Build a public-safe exception payload."""

from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tbot223_base.exception_tracker import ExceptionTracker


def divide(left: int, right: int) -> float:
    return left / right


def main() -> None:
    tracker = ExceptionTracker()

    try:
        divide(10, 0)
    except Exception as error:
        result = tracker.get_public_exception_return(
            error,
            error_code="DIVIDE_BY_ZERO",
            public_message="The calculation could not be completed.",
            public_context="Calculator.Divide",
            tags={"layer": "example"},
            retryable=False,
        )
        print("result:", result.status.value, result.context)
        print(json.dumps(result.data, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
