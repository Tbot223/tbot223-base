#!/usr/bin/env python3
"""Run a small `Result` status flow example."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tbot223_base.result import Result, ResultStatus, ResultUnwrapException


def load_profile(user_id: int) -> Result[dict[str, object]]:
    if user_id <= 0:
        return Result(
            status=ResultStatus.FAILURE,
            error="User id must be positive.",
            context="Profile.Load",
            data={},
        )

    return Result(
        status=ResultStatus.SUCCESS,
        error=None,
        context="Profile.Load",
        data={"user_id": user_id, "name": "Ada"},
    )


def maybe_skip_profile_load(enabled: bool) -> Result[None]:
    if not enabled:
        return Result(
            status=ResultStatus.CANCELLED,
            error=None,
            context="Profile.Load",
            data=None,
        )

    return Result(status=ResultStatus.SUCCESS, error=None, context="Profile.Load", data=None)


def main() -> None:
    success_result = load_profile(1)
    failure_result = load_profile(0)
    cancelled_result = maybe_skip_profile_load(enabled=False)

    print("success:", success_result.status.value, success_result.unwrap())
    print("failure:", failure_result.status.value, failure_result.unwrap_or({"fallback": True}))
    print("cancelled:", cancelled_result.status.value, cancelled_result.success)

    try:
        failure_result.expect("Profile could not be loaded.")
    except ResultUnwrapException as error:
        print("expect error:", error.error)


if __name__ == "__main__":
    main()
