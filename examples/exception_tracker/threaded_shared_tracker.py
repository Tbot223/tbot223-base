#!/usr/bin/env python3
"""Share one `ExceptionTracker` across thread workers."""

from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tbot223_base.exception_tracker import ExceptionTracker


def fail_task(task_id: int) -> None:
    raise RuntimeError(f"task-{task_id}")


def run_task(tracker: ExceptionTracker, task_id: int) -> Mapping[str, object]:
    try:
        fail_task(task_id)
    except Exception as error:
        result = tracker.get_exception_info(
            error,
            user_input=f"user-{task_id}",
            params=((task_id,), {"task_id": task_id}),
            mask_presets=("private", "traceback", "system_info"),
        )
        return cast(Mapping[str, object], result.data)

    return {}


def main() -> None:
    tracker = ExceptionTracker()

    with ThreadPoolExecutor(max_workers=4) as executor:
        payloads = list(executor.map(lambda task_id: run_task(tracker, task_id), range(4)))

    for payload in payloads:
        error_info = cast(Mapping[str, object], payload["error"])
        print(
            "payload:",
            payload["id"],
            payload["status"],
            f"{error_info['type']}: {error_info['message']}",
        )

    print("unique payload ids:", len({payload["id"] for payload in payloads}))


if __name__ == "__main__":
    main()
