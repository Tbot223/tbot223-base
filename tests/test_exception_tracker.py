from concurrent.futures import ThreadPoolExecutor
import gc
import sys
import weakref
from typing import Dict, cast

import pytest
import tbot223_base
from tbot223_base import exception_tracker
from tbot223_base.exception_tracker import ExceptionTracker, ExceptionTrackerDecorator
from tbot223_base.result import Result, ResultStatus


class _LargeContext:
    def __init__(self):
        self.payload = bytearray(1024 * 1024)

    def __repr__(self):
        raise AssertionError("custom repr should not be called")


class _CustomText(str):
    pass


class _CustomInteger(int):
    pass


class _CustomFloat(float):
    pass


class _SelfFormattingError(Exception):
    def __str__(self):
        raise self


def _raise_zero_division_error():
    secret_token = "hidden"

    def inner():
        local_value = 1
        return local_value / 0

    return inner() + len(secret_token)


def _raise_chained_error():
    try:
        int("not-a-number")
    except ValueError as error:
        raise RuntimeError("wrapper") from error


def _raise_with_large_context(value):
    local_payload = value
    local_list = [value]
    return len(local_list) / 0 + len(local_payload.payload)


def _contains_identity(value, target):
    if value is target:
        return True
    if isinstance(value, dict):
        return any(
            _contains_identity(key, target) or _contains_identity(item, target)
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple, set, frozenset)):
        return any(_contains_identity(item, target) for item in value)
    return False


def _raise_without_context():
    raise RuntimeError("plain")


def _raise_context_without_cause():
    try:
        int("nan")
    except ValueError:
        raise RuntimeError("context wrapper")


def _raise_threaded_worker_error(worker_id):
    raise RuntimeError(f"worker-{worker_id}")


def _raise_with_scalar_subclass_locals():
    local_text = _CustomText("blocked-local")
    local_number = _CustomInteger(7)
    local_float = _CustomFloat(2.5)
    raise RuntimeError(f"{local_text}-{local_number}-{local_float}")


def test_get_exception_location_points_to_origin_frame():
    tracker = ExceptionTracker()

    try:
        _raise_zero_division_error()
    except Exception as error:
        result = tracker.get_exception_location(error)

    assert result.status is ResultStatus.SUCCESS
    assert "inner" in result.data


def test_exception_tracker_package_exports_share_api_objects():
    assert tbot223_base.ExceptionTracker is ExceptionTracker
    assert tbot223_base.ExceptionTrackerDecorator is ExceptionTrackerDecorator
    assert exception_tracker.ExceptionTracker is ExceptionTracker
    assert exception_tracker.ExceptionTrackerDecorator is ExceptionTrackerDecorator


def test_get_exception_info_returns_debug_payload_with_masking():
    tracker = ExceptionTracker()

    try:
        _raise_zero_division_error()
    except Exception as error:
        result = tracker.get_exception_info(
            error,
            user_input="demo-user-input",
            params=((1, 2), {"mode": "test"}),
            mask_presets=("private",),
            mask_paths=["id"],
            traceback_frame_limit=2,
            cause_limit=1,
        )

    info = result.data

    assert result.status is ResultStatus.FAILURE
    assert info["status"] == "failure"
    assert info["success"] is False
    assert info["id"] == ExceptionTracker.MASKED_VALUE
    assert info["input_context"]["user_input"] == ExceptionTracker.MASKED_VALUE
    assert info["input_context"]["params"] == ExceptionTracker.MASKED_VALUE
    assert info["input_context"]["local_variables"] == ExceptionTracker.MASKED_VALUE
    assert sorted(info["location"].keys()) == ["entry", "origin"]
    assert info["location"]["origin"]["function"] == "inner"
    assert len(info["traceback_frames"]) <= 2
    assert info["error"]["type"] == "ZeroDivisionError"


def test_get_exception_info_tracks_chained_causes():
    tracker = ExceptionTracker()

    try:
        _raise_chained_error()
    except Exception as error:
        result = tracker.get_exception_info(error, cause_limit=2)

    assert result.status is ResultStatus.FAILURE
    assert result.data["causes"][0]["type"] == "ValueError"


def test_exception_tracker_reuses_one_instance_across_threads():
    tracker = ExceptionTracker()

    def run_worker(worker_id):
        try:
            _raise_threaded_worker_error(worker_id)
        except Exception as error:
            result = tracker.get_exception_info(
                error,
                user_input=f"user-{worker_id}",
                params=((worker_id,), {"worker": worker_id}),
                mask_presets=(),
            )
            return cast(Dict[str, object], result.data)

    worker_ids = tuple(range(8))
    with ThreadPoolExecutor(max_workers=4) as executor:
        payloads = list(executor.map(run_worker, worker_ids))

    payload_ids = [payload["id"] for payload in payloads]
    started_at_snapshots = []

    for worker_id, payload in zip(worker_ids, payloads):
        error_info = cast(Dict[str, object], payload["error"])
        input_context = cast(Dict[str, object], payload["input_context"])
        params_context = cast(Dict[str, object], input_context["params"])
        location = cast(Dict[str, object], payload["location"])
        origin_location = cast(Dict[str, object], location["origin"])
        system_info = cast(Dict[str, object], payload["system_info"])

        assert error_info["message"] == f"worker-{worker_id}"
        assert input_context["user_input"] == f"user-{worker_id}"
        assert params_context["args"] == (worker_id,)
        assert params_context["kwargs"] == {"worker": worker_id}
        assert origin_location["function"] == "_raise_threaded_worker_error"
        started_at_snapshots.append(system_info["started_at"])

    assert len(set(payload_ids)) == len(worker_ids)
    assert len({id(snapshot) for snapshot in started_at_snapshots}) == len(worker_ids)


def test_get_exception_return_reuses_debug_info_result_shape():
    tracker = ExceptionTracker()

    try:
        _raise_zero_division_error()
    except Exception as error:
        info_result = tracker.get_exception_info(error, mask_presets=())
        return_result = tracker.get_exception_return(error, mask_presets=())

    assert return_result.status is ResultStatus.FAILURE
    assert return_result.error == info_result.error == "ZeroDivisionError: division by zero"
    assert return_result.context == info_result.context
    assert return_result.data["error"] == info_result.data["error"]
    assert return_result.data["location"] == info_result.data["location"]


def test_get_exception_info_masks_origin_before_result_context_derivation():
    tracker = ExceptionTracker()

    try:
        _raise_zero_division_error()
    except Exception as error:
        masked_result = tracker.get_exception_info(
            error,
            mask_presets=(),
            mask_paths=["location.origin"],
        )
        partial_result = tracker.get_exception_info(
            error,
            mask_presets=(),
            mask_paths=["location.origin.function"],
        )

    assert masked_result.context == "<unknown>"
    assert masked_result.data["location"]["origin"] == ExceptionTracker.MASKED_VALUE
    assert partial_result.data["location"]["origin"]["function"] == ExceptionTracker.MASKED_VALUE
    assert partial_result.context.endswith(f"in {ExceptionTracker.MASKED_VALUE}")


def test_get_exception_return_masks_origin_before_result_context_derivation():
    tracker = ExceptionTracker()

    try:
        _raise_zero_division_error()
    except Exception as error:
        result = tracker.get_exception_return(
            error,
            mask_presets=(),
            mask_paths=["location.origin"],
        )

    assert result.context == "<unknown>"
    assert result.data["location"]["origin"] == ExceptionTracker.MASKED_VALUE


def test_get_exception_info_does_not_retain_raw_context_objects():
    tracker = ExceptionTracker()
    large_context = _LargeContext()
    context_ref = weakref.ref(large_context)

    try:
        _raise_with_large_context(large_context)
    except Exception as error:
        result = tracker.get_exception_info(
            error,
            params=((large_context,), {"context": large_context}),
            mask_presets=(),
        )

    assert result.status is ResultStatus.FAILURE
    assert not _contains_identity(result.data, large_context)
    assert result.data["input_context"]["params"]["args"] == (ExceptionTracker.BLOCKED_VALUE,)
    assert result.data["input_context"]["params"]["kwargs"]["context"] == ExceptionTracker.BLOCKED_VALUE
    assert result.data["input_context"]["local_variables"]["local_payload"] == ExceptionTracker.BLOCKED_VALUE
    assert result.data["input_context"]["local_variables"]["local_list"] == [ExceptionTracker.BLOCKED_VALUE]

    del large_context
    gc.collect()

    assert context_ref() is None


def test_get_exception_info_blocks_large_values_and_heavy_objects():
    tracker = ExceptionTracker()
    long_text = "x" * (ExceptionTracker.CONTEXT_MAX_VALUE_LENGTH + 1)
    large_list = list(range(ExceptionTracker.CONTEXT_MAX_ITEMS + 1))
    large_dict = {
        f"key_{index}": index
        for index in range(ExceptionTracker.CONTEXT_MAX_ITEMS + 1)
    }
    custom_context = _LargeContext()
    small_tuple = ("ok", 1, True, None)
    small_list = ["ok", 2.5, False, None]

    try:
        raise RuntimeError("block me")
    except Exception as error:
        result = tracker.get_exception_info(
            error,
            user_input=long_text,
            params=(
                (large_list, small_tuple),
                {
                    "mapping": large_dict,
                    "custom": custom_context,
                    "nested": [[custom_context]],
                    "small_list": small_list,
                },
            ),
            mask_presets=(),
        )

    context = result.data["input_context"]
    assert context["user_input"] == ExceptionTracker.BLOCKED_VALUE

    args_context = context["params"]["args"]
    assert args_context == (ExceptionTracker.BLOCKED_VALUE, small_tuple)
    assert args_context[1] is not small_tuple

    kwargs_context = context["params"]["kwargs"]
    assert kwargs_context["mapping"] == ExceptionTracker.BLOCKED_VALUE
    assert kwargs_context["custom"] == ExceptionTracker.BLOCKED_VALUE
    assert kwargs_context["nested"] == [ExceptionTracker.BLOCKED_VALUE]
    assert kwargs_context["small_list"] == small_list
    assert kwargs_context["small_list"] is not small_list


def test_get_exception_info_masks_after_context_capture():
    tracker = ExceptionTracker()

    try:
        _raise_with_large_context(_LargeContext())
    except Exception as error:
        result = tracker.get_exception_info(
            error,
            params=((_LargeContext(),), {"context": _LargeContext()}),
            mask_presets=("private",),
        )

    assert result.data["input_context"]["params"] == ExceptionTracker.MASKED_VALUE
    assert result.data["input_context"]["local_variables"] == ExceptionTracker.MASKED_VALUE


def test_get_exception_info_exposes_safe_context_when_unmasked():
    tracker = ExceptionTracker()

    try:
        _raise_with_large_context(_LargeContext())
    except Exception as error:
        result = tracker.get_exception_info(error, mask_presets=())

    local_variables = result.data["input_context"]["local_variables"]
    assert local_variables["value"] == ExceptionTracker.BLOCKED_VALUE
    assert local_variables["local_payload"] == ExceptionTracker.BLOCKED_VALUE
    assert local_variables["local_list"] == [ExceptionTracker.BLOCKED_VALUE]


def test_exception_tracker_helper_structures_are_independent():
    info = exception_tracker.ExceptionTrackerHelper.get_error_info_structure()
    public_info = exception_tracker.ExceptionTrackerHelper.get_public_error_info_structure()

    info["input_context"]["params"]["args"] = ("changed",)
    public_info["tags"]["changed"] = True

    fresh_info = exception_tracker.ExceptionTrackerHelper.get_error_info_structure()
    fresh_public_info = exception_tracker.ExceptionTrackerHelper.get_public_error_info_structure()

    assert fresh_info["input_context"]["params"]["args"] is None
    assert fresh_public_info["tags"] == {}


def test_get_system_info_handles_unavailable_cwd(monkeypatch):
    monkeypatch.setattr(exception_tracker.os, "access", lambda path, mode: False)

    denied_info = exception_tracker.ExceptionTrackerHelper.get_system_info()

    assert denied_info["Current_Working_Directory"] == "<Permission Denied or Unavailable>"

    def broken_getcwd():
        raise RuntimeError("cwd failed")

    monkeypatch.setattr(exception_tracker.os, "getcwd", broken_getcwd)

    error_info = exception_tracker.ExceptionTrackerHelper.get_system_info()

    assert error_info["Current_Working_Directory"] == "<Permission Denied or Unavailable>"


def test_get_system_info_collects_only_bounded_environment_variables(monkeypatch):
    helper = exception_tracker.ExceptionTrackerHelper
    large_value = "x" * (helper.ENVIRONMENT_VARIABLE_MAX_VALUE_LENGTH + 1)
    long_key = "K" * (helper.ENVIRONMENT_VARIABLE_MAX_VALUE_LENGTH + 1)
    list_value = ["ok", 1, True, None]
    tuple_value = ("ok", 1.5, False, None)
    limited_environ = {
        "SMALL_ENV": "ok",
        "INT_ENV": 1,
        "BOOL_ENV": True,
        "NONE_ENV": None,
        "LIST_ENV": list_value,
        "TUPLE_ENV": tuple_value,
        "VIRTUAL_ENV": tuple_value,
        "LARGE_ENV": large_value,
        "DICT_ENV": {"nested": "value"},
        "SET_ENV": {"value"},
        "BYTES_ENV": b"value",
        "OBJECT_ENV": object(),
        "NESTED_LIST_ENV": [["nested"]],
        "LIST_WITH_LARGE_STRING_ENV": [large_value],
        "LARGE_LIST_ENV": list(range(helper.ENVIRONMENT_VARIABLE_MAX_COUNT + 1)),
        long_key: "ok",
        object(): "bad-key",
    }
    limited_environ.update(
        {
            f"SMALL_{index}": "ok"
            for index in range(helper.ENVIRONMENT_VARIABLE_MAX_COUNT + 1)
        }
    )
    monkeypatch.setattr(exception_tracker.os, "environ", limited_environ)

    info = helper.get_system_info()
    environment_variables = info["Environment_Variables"]

    assert environment_variables["SMALL_ENV"] == "ok"
    assert environment_variables["INT_ENV"] == 1
    assert environment_variables["BOOL_ENV"] is True
    assert environment_variables["NONE_ENV"] is None
    assert environment_variables["LIST_ENV"] == list_value
    assert environment_variables["LIST_ENV"] is not list_value
    assert environment_variables["TUPLE_ENV"] == tuple_value
    assert environment_variables["TUPLE_ENV"] is not tuple_value
    assert environment_variables["VIRTUAL_ENV"] == tuple_value
    assert "LARGE_ENV" not in environment_variables
    assert "DICT_ENV" not in environment_variables
    assert "SET_ENV" not in environment_variables
    assert "BYTES_ENV" not in environment_variables
    assert "OBJECT_ENV" not in environment_variables
    assert "NESTED_LIST_ENV" not in environment_variables
    assert "LIST_WITH_LARGE_STRING_ENV" not in environment_variables
    assert "LARGE_LIST_ENV" not in environment_variables
    assert long_key not in environment_variables
    assert all(isinstance(key, str) for key in environment_variables)
    assert info["Virtual_Env"] == "None"
    assert len(environment_variables) == helper.ENVIRONMENT_VARIABLE_MAX_COUNT

    monkeypatch.setattr(exception_tracker.os, "environ", {"VIRTUAL_ENV": "venv"})
    string_virtual_info = helper.get_system_info()

    assert string_virtual_info["Virtual_Env"] == "venv"
    assert string_virtual_info["Environment_Variables"]["VIRTUAL_ENV"] == "venv"

    monkeypatch.setattr(exception_tracker.os, "environ", {"VIRTUAL_ENV": large_value})
    large_virtual_info = helper.get_system_info()

    assert large_virtual_info["Virtual_Env"] == "None"
    assert "VIRTUAL_ENV" not in large_virtual_info["Environment_Variables"]

    class _NonMappingEnvironment:
        environ = []

    monkeypatch.setattr(exception_tracker, "os", _NonMappingEnvironment)

    assert helper._get_small_environment_variables() == {}


def test_get_system_info_uses_argument_and_path_snapshots():
    info = exception_tracker.ExceptionTrackerHelper.get_system_info()

    assert info["Command_Args"] == sys.argv
    assert info["Command_Args"] is not sys.argv
    assert info["Python_Path"] == sys.path
    assert info["Python_Path"] is not sys.path


def test_debug_system_info_started_at_is_isolated_between_payloads():
    tracker = ExceptionTracker()

    def capture_payload(message):
        try:
            raise RuntimeError(message)
        except Exception as error:
            result = tracker.get_exception_info(error, mask_presets=())
            return cast(Dict[str, object], result.data)

    first_payload = capture_payload("first")
    first_system_info = cast(Dict[str, object], first_payload["system_info"])
    first_started_at = cast(Dict[str, object], first_system_info["started_at"])
    first_started_at["mutated"] = True

    second_payload = capture_payload("second")
    second_system_info = cast(Dict[str, object], second_payload["system_info"])
    second_started_at = cast(Dict[str, object], second_system_info["started_at"])

    assert first_started_at is not second_started_at
    assert "mutated" not in second_started_at


def test_format_location_and_traceback_helpers_handle_missing_values():
    tracker = ExceptionTracker()
    empty_error = RuntimeError("not raised")

    assert tracker._format_location({"file": None}) == "<unknown>"
    assert tracker._frame_to_location(None) == {"file": None, "line": None, "function": None}
    assert tracker._frame_to_traceback_frame(None) == {
        "file": None,
        "line": None,
        "function": None,
        "code": None,
    }
    assert tracker._get_origin_traceback(empty_error) is None
    assert tracker._get_local_variables(empty_error) == {}


def test_normalize_helpers_accept_invalid_and_duplicate_inputs():
    tracker = ExceptionTracker()

    assert tracker._normalize_limit("bad") == ExceptionTracker.DEFAULT_TRACEBACK_LIMIT
    assert tracker._normalize_limit(-1) == ExceptionTracker.DEFAULT_TRACEBACK_LIMIT
    assert tracker._normalize_limit(ExceptionTracker.MAX_TRACEBACK_LIMIT + 1) == ExceptionTracker.MAX_TRACEBACK_LIMIT
    assert tracker._normalize_limit(0) == 0
    assert tracker._normalize_exception_params(((1, 2), {"mode": "test"})) == (
        (1, 2),
        {"mode": "test"},
    )
    assert tracker._normalize_exception_params(("bad", "shape")) == ((), {})
    assert tracker._normalize_mask_paths(None) == ()
    assert tracker._normalize_mask_paths("location.origin") == (("location", "origin"),)
    assert tracker._normalize_mask_paths(("error", "message")) == (("error", "message"),)
    assert tracker._normalize_mask_paths(123) == ()
    assert tracker._normalize_mask_paths(["id", "id", ("error", "message"), (), 123]) == (
        ("id",),
        ("error", "message"),
    )
    assert tracker._normalize_mask_presets(None) == ()
    assert tracker._normalize_mask_presets("private") == ("private",)
    assert tracker._normalize_mask_presets(["private", "private", "unknown", 1]) == ("private",)
    assert tracker._normalize_mask_presets(123) == ()
    assert tracker._get_preset_mask_paths(("private", "traceback", "private")) == (
        ("input_context", "user_input"),
        ("input_context", "params"),
        ("input_context", "local_variables"),
        ("causes",),
        ("traceback",),
        ("traceback_frames",),
    )


def test_mask_presets_are_read_only():
    with pytest.raises(TypeError):
        cast(dict[str, object], ExceptionTracker.MASK_PRESETS)["custom"] = ()


def test_mask_paths_ignores_missing_and_masks_existing_values():
    payload = {
        "level": {
            "secret": "value",
            "not_dict": "text",
        }
    }

    ExceptionTracker._mask_path(payload, ("missing", "secret"))
    ExceptionTracker._mask_path(payload, ("level", "missing"))
    ExceptionTracker._mask_path(payload, ("level", "not_dict", "ignored"))
    ExceptionTracker._mask_paths(payload, (("level", "secret"),))

    assert payload["level"]["secret"] == ExceptionTracker.MASKED_VALUE
    assert payload["level"]["not_dict"] == "text"


def test_copy_safe_context_keeps_small_values_and_blocks_heavy_values():
    key = object()
    small_list = ["ok", 1, True, None]
    small_tuple = ("ok", 2.5, False, None)
    payload = {
        "text": "ok",
        "number": 1,
        "list": small_list,
        "tuple": small_tuple,
        "nested": [["nested"]],
        "nested_dict": {"small": "value"},
        "bytes": b"value",
        "object": object(),
        key: "ignored",
    }

    copied = ExceptionTracker._copy_safe_context(payload)

    assert copied["text"] == "ok"
    assert copied["number"] == 1
    assert copied["list"] == small_list
    assert copied["list"] is not small_list
    assert copied["tuple"] == small_tuple
    assert copied["tuple"] is not small_tuple
    assert copied["nested"] == [["nested"]]
    assert copied["nested_dict"] == ExceptionTracker.BLOCKED_VALUE
    assert copied["bytes"] == ExceptionTracker.BLOCKED_VALUE
    assert copied["object"] == ExceptionTracker.BLOCKED_VALUE
    assert all(isinstance(copied_key, str) for copied_key in copied)

    assert ExceptionTracker._copy_safe_context("x" * (ExceptionTracker.CONTEXT_MAX_VALUE_LENGTH + 1)) == ExceptionTracker.BLOCKED_VALUE
    assert ExceptionTracker._copy_safe_context(list(range(ExceptionTracker.CONTEXT_MAX_ITEMS + 1))) == ExceptionTracker.BLOCKED_VALUE
    assert ExceptionTracker._copy_safe_context({f"key_{index}": index for index in range(ExceptionTracker.CONTEXT_MAX_ITEMS + 1)}) == ExceptionTracker.BLOCKED_VALUE


def test_copy_safe_context_blocks_scalar_subclasses_without_retaining_identity():
    text = _CustomText("ok")
    number = _CustomInteger(1)
    floating = _CustomFloat(2.5)

    for value in (text, number, floating):
        is_small, copied_value = ExceptionTracker._copy_safe_context_primitive(value)

        assert is_small is False
        assert copied_value == ExceptionTracker.BLOCKED_VALUE
        assert copied_value is not value


def test_get_exception_info_blocks_scalar_subclasses_in_debug_context():
    tracker = ExceptionTracker()
    text = _CustomText("blocked-user")
    number = _CustomInteger(3)
    floating = _CustomFloat(4.5)

    try:
        _raise_with_scalar_subclass_locals()
    except Exception as error:
        result = tracker.get_exception_info(
            error,
            user_input=text,
            params=((number,), {"value": floating}),
            mask_presets=(),
        )

    context = result.data["input_context"]
    assert context["user_input"] == ExceptionTracker.BLOCKED_VALUE
    assert context["params"]["args"] == (ExceptionTracker.BLOCKED_VALUE,)
    assert context["params"]["kwargs"]["value"] == ExceptionTracker.BLOCKED_VALUE
    assert context["local_variables"]["local_text"] == ExceptionTracker.BLOCKED_VALUE
    assert context["local_variables"]["local_number"] == ExceptionTracker.BLOCKED_VALUE
    assert context["local_variables"]["local_float"] == ExceptionTracker.BLOCKED_VALUE
    assert not _contains_identity(result.data, text)
    assert not _contains_identity(result.data, number)
    assert not _contains_identity(result.data, floating)


def test_exception_causes_breaks_cycles():
    tracker = ExceptionTracker()
    cause = ValueError("loop")
    error = RuntimeError("wrapper")
    error.__cause__ = cause
    cause.__cause__ = cause

    causes = tracker._get_exception_causes(error, limit=5)

    assert len(causes) == 1
    assert causes[0]["type"] == "ValueError"


def test_get_exception_info_handles_invalid_params_and_limits():
    tracker = ExceptionTracker()

    try:
        _raise_without_context()
    except Exception as error:
        result = tracker.get_exception_info(
            error,
            params="invalid",
            mask_presets=("traceback", "system_info"),
            traceback_frame_limit=0,
            cause_limit=-1,
    )

    info = result.data
    assert info["input_context"]["params"]["args"] == ()
    assert info["input_context"]["params"]["kwargs"] == {}
    assert info["traceback_frames"] == ExceptionTracker.MASKED_VALUE
    assert info["traceback"] == ExceptionTracker.MASKED_VALUE
    assert info["system_info"] == ExceptionTracker.MASKED_VALUE


def test_get_exception_info_extra_mask_paths_and_no_traceback_error():
    tracker = ExceptionTracker()
    error = RuntimeError("not raised")

    result = tracker.get_exception_info(
        error,
        mask_presets=(),
        mask_paths=["quick_info", ("error", "message")],
    )

    assert result.context == "<unknown>"
    assert result.data["quick_info"] == ExceptionTracker.MASKED_VALUE
    assert result.data["error"]["message"] == ExceptionTracker.MASKED_VALUE
    assert result.data["location"]["origin"] == {"file": None, "line": None, "function": None}


def test_exception_causes_use_context_when_cause_is_absent():
    tracker = ExceptionTracker()

    try:
        _raise_context_without_cause()
    except Exception as error:
        causes = tracker._get_exception_causes(error, limit=1)

    assert causes[0]["type"] == "ValueError"


def test_public_exception_info_normalizes_invalid_inputs_and_fallback(monkeypatch):
    tracker = ExceptionTracker()

    try:
        _raise_zero_division_error()
    except Exception as error:
        result = tracker.get_public_exception_info(
            error,
            error_code=404,
            public_message="",
            public_context="",
            tags=[("bad", "tags")],
            retryable="yes",
        )

    assert result.context is None
    assert result.data["error"] == {
        "code": 404,
        "message": ExceptionTracker.DEFAULT_PUBLIC_MESSAGE,
    }
    assert result.data["tags"] == {}
    assert result.data["retryable"] is None

    def broken_builder(*args, **kwargs):
        raise RuntimeError("builder broke")

    monkeypatch.setattr(ExceptionTracker, "_build_public_error_info", broken_builder)
    fallback = tracker.get_public_exception_info(RuntimeError("boom"), public_context="Public.Context")

    assert fallback.context == "Public.Context"
    assert fallback.data["error"]["code"] == ExceptionTracker.DEFAULT_PUBLIC_ERROR_CODE
    assert fallback.data["tags"] == {"tracker_failure": True}


def test_get_exception_info_and_return_fallbacks(monkeypatch):
    tracker = ExceptionTracker()

    def broken_preset_paths(*args, **kwargs):
        raise RuntimeError("preset broke")

    monkeypatch.setattr(ExceptionTracker, "_get_preset_mask_paths", broken_preset_paths)
    info_result = tracker.get_exception_info(RuntimeError("boom"))

    assert info_result.status is ResultStatus.FAILURE
    assert "RuntimeError" in info_result.error
    assert info_result.context == "Core.ExceptionTracker.get_exception_info, L1"

    def broken_exception_info(*args, **kwargs):
        raise RuntimeError("info broke")

    monkeypatch.setattr(ExceptionTracker, "get_exception_info", broken_exception_info)
    return_result = tracker.get_exception_return(RuntimeError("boom"))

    assert return_result.status is ResultStatus.FAILURE
    assert "RuntimeError" in return_result.error
    assert return_result.context == "Core.ExceptionTracker.get_exception_return, L2"


def test_get_exception_location_fallback(monkeypatch):
    tracker = ExceptionTracker()

    def broken_extract_tb(*args, **kwargs):
        raise RuntimeError("traceback broke")

    monkeypatch.setattr(exception_tracker.traceback, "extract_tb", broken_extract_tb)
    result = tracker.get_exception_location(RuntimeError("boom"))

    assert result.status is ResultStatus.FAILURE
    assert "RuntimeError" in result.error
    assert result.context == "Core.ExceptionTracker.get_exception_location, L1"


def test_public_exception_info_returns_lightweight_safe_payload():
    tracker = ExceptionTracker()

    try:
        _raise_zero_division_error()
    except Exception as error:
        result = tracker.get_public_exception_info(
            error,
            error_code="DIVIDE_BY_ZERO",
            public_message="The calculation could not be completed.",
            public_context="Calculator.Divide",
            tags={"layer": "service", 1: "numeric-key"},
            retryable=False,
        )

    public_info = result.data

    assert result.status is ResultStatus.FAILURE
    assert result.context == "Calculator.Divide"
    assert result.error == "The calculation could not be completed."
    assert sorted(public_info.keys()) == [
        "error",
        "id",
        "retryable",
        "status",
        "success",
        "tags",
        "timestamp",
    ]
    assert public_info["error"]["code"] == "DIVIDE_BY_ZERO"
    assert public_info["error"]["message"] == "The calculation could not be completed."
    assert public_info["tags"] == {"layer": "service", "1": "numeric-key"}
    assert public_info["retryable"] is False
    assert "traceback" not in public_info
    assert "input_context" not in public_info
    assert "system_info" not in public_info


def test_public_exception_return_uses_safe_defaults():
    tracker = ExceptionTracker()

    try:
        raise ValueError("internal secret message")
    except Exception as error:
        result = tracker.get_public_exception_return(error)

    assert result.status is ResultStatus.FAILURE
    assert result.error == "The operation could not be completed."
    assert result.data["error"] == {
        "code": "UNEXPECTED_ERROR",
        "message": "The operation could not be completed.",
    }


def test_get_error_code_returns_success_and_failure_results():
    tracker = ExceptionTracker()

    try:
        _raise_zero_division_error()
    except Exception as error:
        success_result = tracker.get_error_code({"ZeroDivisionError": 1001}, error)
        failure_result = tracker.get_error_code({}, error)

    assert success_result.status is ResultStatus.SUCCESS
    assert success_result.data == 1001
    assert failure_result.status is ResultStatus.FAILURE
    assert "KeyError" in failure_result.error


def test_exception_tracker_decorator_converts_exception_to_result():
    tracker = ExceptionTracker()

    @ExceptionTrackerDecorator(mask_presets=("private",), tracker=tracker)
    def risky_divide(x, y):
        return x / y

    result = risky_divide(10, 0)

    assert isinstance(result, Result)
    assert result.status is ResultStatus.FAILURE
    assert result.data["input_context"]["params"] == ExceptionTracker.MASKED_VALUE


def test_get_exception_info_handles_unprintable_exception_text():
    tracker = ExceptionTracker()

    try:
        raise _SelfFormattingError()
    except Exception as error:
        result = tracker.get_exception_info(error, mask_presets=())

    assert result.status is ResultStatus.FAILURE
    assert result.error == "_SelfFormattingError: <unprintable _SelfFormattingError>"
    assert result.data["quick_info"] == result.error
    assert result.data["error"]["message"] == "<unprintable _SelfFormattingError>"


def test_exception_tracker_decorator_returns_failure_result_for_unprintable_exception():
    @ExceptionTrackerDecorator(mask_presets=())
    def explode():
        raise _SelfFormattingError()

    result = explode()

    assert isinstance(result, Result)
    assert result.status is ResultStatus.FAILURE
    assert result.error == "_SelfFormattingError: <unprintable _SelfFormattingError>"
    assert result.data["error"]["message"] == "<unprintable _SelfFormattingError>"


def test_exception_tracker_decorator_preserves_success_return_and_default_tracker():
    @ExceptionTrackerDecorator(mask_presets="private")
    def add(x, y):
        return x + y

    assert add(2, 3) == 5


def test_public_exception_return_forwards_arguments():
    tracker = ExceptionTracker()
    result = tracker.get_public_exception_return(
        RuntimeError("boom"),
        error_code="BOOM",
        public_message="Safe",
        public_context="Layer.Operation",
        tags={"scope": "test"},
        retryable=True,
    )

    assert result.error == "Safe"
    assert result.context == "Layer.Operation"
    assert result.data["error"]["code"] == "BOOM"
    assert result.data["tags"] == {"scope": "test"}
    assert result.data["retryable"] is True
