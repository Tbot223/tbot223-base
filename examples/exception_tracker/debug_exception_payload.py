#!/usr/bin/env python3
"""Build a masked debug exception payload."""

from pathlib import Path
import json
import sys
from collections.abc import Mapping
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tbot223_base.exception_tracker import ExceptionTracker


def load_config() -> dict[str, str]:
    secret_token = "internal-token"
    config = {"mode": "example", "token": secret_token}
    return {"mode": config["missing"]}


def main() -> None:
    tracker = ExceptionTracker()

    try:
        load_config()
    except Exception as error:
        result = tracker.get_exception_info(
            error,
            user_input={"source": "example"},
            params=((), {"config_name": "demo"}),
            mask_presets=("private", "system_info"),
            mask_paths=["id"],
            traceback_frame_limit=3,
            cause_limit=2,
        )
        payload = cast(Mapping[str, object], result.data)
        traceback_frames = payload.get("traceback_frames")
        summary = {
            "status": payload.get("status"),
            "quick_info": payload.get("quick_info"),
            "context": result.context,
            "location": payload.get("location"),
            "input_context": payload.get("input_context"),
            "traceback_frame_count": (
                len(traceback_frames)
                if isinstance(traceback_frames, list)
                else 0
            ),
            "system_info": payload.get("system_info"),
        }
        print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
