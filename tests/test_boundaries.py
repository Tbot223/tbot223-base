"""Consumer regressions for result transport and exception boundaries."""

import asyncio
import copy
import io
import json
import pickle
import sys
from collections.abc import Mapping

import pytest

from tbot223_base import ExceptionTracker, ExceptionTrackerDecorator, Result
from tbot223_base.exception_tracker import ExceptionTrackerHelper


@pytest.fixture(autouse=True)
def isolated_system_snapshot(monkeypatch):
    monkeypatch.setattr(
        ExceptionTrackerHelper, "get_system_info", lambda: {"audit": True}
    )


@pytest.mark.parametrize(
    "number", [10**5000, -(10**5000)], ids=["positive", "negative"]
)
def test_public_large_integers_are_blocked_without_breaking_json(number):
    payload = (
        ExceptionTracker()
        .get_public_exception_return(
            RuntimeError("private"),
            tags={"value": number, number: "drop", "valid": 42},
            error_code=number,
        )
        .data
    )
    assert payload["tags"] == {"value": "<BLOCKED>", "valid": 42}
    assert payload["error"]["code"] == "UNEXPECTED_ERROR"
    json.dumps(payload, allow_nan=False)


@pytest.mark.parametrize("sign", [-1, 1])
def test_public_integer_bit_boundary_and_normalized_key_length(sign):
    accepted = sign * (2**512 - 1)
    blocked = sign * 2**512
    payload = (
        ExceptionTracker()
        .get_public_exception_info(
            RuntimeError(),
            tags={
                "accepted": accepted,
                "blocked": blocked,
                10**200: "drop",
                accepted: "keep",
            },
            error_code=accepted,
        )
        .data
    )
    assert payload["tags"]["accepted"] == accepted
    assert payload["tags"]["blocked"] == "<BLOCKED>"
    assert payload["tags"][str(accepted)] == "keep"
    assert all(len(key) <= 200 for key in payload["tags"])
    assert payload["error"]["code"] == accepted
    json.dumps(payload, allow_nan=False)


def test_oversized_public_code_uses_default():
    payload = (
        ExceptionTracker()
        .get_public_exception_info(RuntimeError(), error_code="x" * 201)
        .data
    )
    assert payload["error"]["code"] == "UNEXPECTED_ERROR"


def test_repeated_nested_tag_references_have_a_global_budget():
    value = "x" * 200
    for _ in range(3):
        value = [value] * 20
    tags = {str(index): value for index in range(20)}
    payload = (
        ExceptionTracker().get_public_exception_info(RuntimeError(), tags=tags).data
    )
    encoded = json.dumps(payload, allow_nan=False)
    assert len(encoded) < 100_000
    assert "<BLOCKED>" in encoded
    assert len(tags["0"]) == 20


@pytest.mark.parametrize("factory", [Result.ok, Result.failure, Result.cancelled])
def test_result_copy_and_deepcopy_preserve_status_and_payload_semantics(factory):
    original = factory({"items": [1]})
    shallow = copy.copy(original)
    deep = copy.deepcopy(original)
    assert type(shallow) is type(deep) is Result
    assert shallow == deep == original
    assert shallow.data is original.data
    deep.data["items"].append(2)
    assert original.data == {"items": [1]}


@pytest.mark.parametrize("protocol", range(pickle.HIGHEST_PROTOCOL + 1))
@pytest.mark.parametrize("factory", [Result.ok, Result.failure, Result.cancelled])
def test_result_pickle_roundtrip(factory, protocol):
    original = factory({"items": [1]})
    restored = pickle.loads(pickle.dumps(original, protocol=protocol))
    assert type(restored) is Result
    assert restored == original
    assert restored.status is original.status
    assert restored.data is not original.data


@pytest.mark.parametrize("stage", ["call", "await", "success"])
def test_explicit_awaitable_wrapper_covers_both_failure_stages(stage):
    calls = []

    async def operation():
        if stage == "await":
            raise ValueError("await failed")
        return 42

    @ExceptionTrackerDecorator().wrap_awaitable
    def factory():
        calls.append("called")
        if stage == "call":
            raise ValueError("factory failed")
        return operation()

    pending = factory()
    assert calls == []
    result = asyncio.run(pending)
    assert calls == ["called"]
    if stage == "success":
        assert result == 42
    else:
        assert result.is_failure


def test_explicit_awaitable_wrapper_supports_async_functions_and_cancellation():
    @ExceptionTrackerDecorator().wrap_awaitable
    async def value():
        return 42

    @ExceptionTrackerDecorator().wrap_awaitable
    async def cancelled():
        raise asyncio.CancelledError()

    assert asyncio.run(value()) == 42
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(cancelled())


def test_automatic_factory_still_returns_result_on_immediate_failure():
    @ExceptionTrackerDecorator()
    def factory():
        raise ValueError("before awaitable")

    assert factory().is_failure


class BrokenMapping(Mapping):
    def __iter__(self):
        raise ValueError("private mapping error")

    def __len__(self):
        return 1

    def __getitem__(self, key):
        raise KeyError(key)


def test_public_fallback_is_independent_of_stdout(monkeypatch):
    output = io.StringIO()
    output.close()
    with monkeypatch.context() as context:
        context.setattr(sys, "stdout", output)
        result = ExceptionTracker().get_public_exception_return(
            RuntimeError("original private error"), tags=BrokenMapping()
        )
    assert result.data["tags"] == {"tracker_failure": True}
    assert "private" not in json.dumps(result)


def test_debug_mask_failure_has_no_original_exception_or_traceback(capsys):
    def broken_paths():
        yield "quick_info"
        raise ValueError("private mask error")

    try:
        raise RuntimeError("original private error")
    except RuntimeError as error:
        result = ExceptionTracker().get_exception_info(
            error,
            mask_presets=("private", "traceback", "system_info"),
            mask_paths=broken_paths(),
        )
    assert result.data == {"tracker_failure": True, "message": result.error}
    assert "private" not in json.dumps(result)
    assert "traceback" not in json.dumps(result)
    assert capsys.readouterr().out == ""


def test_debug_masks_do_not_claim_to_sanitize_error_messages():
    error = ValueError("private error")
    tracker = ExceptionTracker()
    debug = tracker.get_exception_info(
        error, mask_presets=("private", "traceback", "system_info")
    )
    assert debug.data["error"]["message"] == "private error"
    public = tracker.get_public_exception_return(error)
    assert "private error" not in json.dumps(public)


def test_public_path_never_formats_exception_or_collects_system_info(monkeypatch):
    def forbidden():
        raise AssertionError("unexpected system collection")

    class UnprintableError(Exception):
        def __str__(self):
            raise AssertionError("unexpected formatting")

    monkeypatch.setattr(ExceptionTrackerHelper, "get_system_info", forbidden)
    payload = ExceptionTracker().get_public_exception_return(UnprintableError()).data
    json.dumps(payload, allow_nan=False)
