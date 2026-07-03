import gc
import weakref
from collections.abc import Mapping
import pytest

from tbot223_base import tbot223_Exception
from tbot223_base.tbot223_Exception import ExceptionTracker, ExceptionTrackerDecorator
from tbot223_base.tbot223_Result import Result, ResultStatus


class _LargeContext:
    def __init__(self):
        self.payload = bytearray(1024 * 1024)

    def __repr__(self):
        raise AssertionError("custom repr should not be called")


class _BadLen:
    def __len__(self):
        raise RuntimeError("len failed")


class _BadShape:
    @property
    def shape(self):
        raise RuntimeError("shape failed")


class _TupleShape:
    shape = (1, object())


class _ListShape:
    shape = [2, object()]


class _ObjectShape:
    shape = object()


class _BadRepr:
    def __repr__(self):
        raise RuntimeError("repr failed")


class _PretendBuiltinBadRepr:
    __module__ = "builtins"

    def __repr__(self):
        raise RuntimeError("repr failed")


class _StringShape:
    shape = "rows"


class _BadMapping(Mapping):
    def __iter__(self):
        return iter(["key"])

    def __len__(self):
        return 1

    def __getitem__(self, key):
        return "value"

    def items(self):
        raise RuntimeError("items failed")


class _BadSequence(list):
    def __iter__(self):
        raise RuntimeError("iter failed")


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


def test_get_exception_location_points_to_origin_frame():
    tracker = ExceptionTracker()

    try:
        _raise_zero_division_error()
    except Exception as error:
        result = tracker.get_exception_location(error)

    assert result.status is ResultStatus.SUCCESS
    assert "inner" in result.data


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
    assert (
        result.data["input_context"]["params"]["args"]["items"][0]["type"]
        == f"{_LargeContext.__module__}._LargeContext"
    )
    assert (
        result.data["input_context"]["local_variables"]["items"]["local_payload"]["type"]
        == f"{_LargeContext.__module__}._LargeContext"
    )

    del large_context
    gc.collect()

    assert context_ref() is None


def test_get_exception_info_snapshots_large_values_and_collections():
    tracker = ExceptionTracker()
    long_text = "x" * (ExceptionTracker.CONTEXT_MAX_REPR_LENGTH + 1)
    large_list = list(range(ExceptionTracker.CONTEXT_MAX_ITEMS + 1))
    large_dict = {
        f"key_{index}": index
        for index in range(ExceptionTracker.CONTEXT_MAX_ITEMS + 1)
    }
    custom_context = _LargeContext()

    try:
        raise RuntimeError("snapshot me")
    except Exception as error:
        result = tracker.get_exception_info(
            error,
            user_input=long_text,
            params=((large_list,), {"mapping": large_dict, "custom": custom_context, "nested": [[custom_context]]}),
            mask_presets=(),
        )

    context = result.data["input_context"]
    assert context["user_input"] == {
        "type": "str",
        "length": ExceptionTracker.CONTEXT_MAX_REPR_LENGTH + 1,
        "preview": "x" * ExceptionTracker.CONTEXT_MAX_REPR_LENGTH,
        "truncated": True,
    }

    args_snapshot = context["params"]["args"]
    list_snapshot = args_snapshot["items"][0]
    assert args_snapshot["type"] == "tuple"
    assert list_snapshot["type"] == "list"
    assert list_snapshot["length"] == ExceptionTracker.CONTEXT_MAX_ITEMS + 1
    assert len(list_snapshot["items"]) == ExceptionTracker.CONTEXT_MAX_ITEMS
    assert list_snapshot["truncated"] is True

    kwargs_snapshot = context["params"]["kwargs"]
    dict_snapshot = kwargs_snapshot["items"]["mapping"]
    custom_snapshot = kwargs_snapshot["items"]["custom"]
    nested_snapshot = kwargs_snapshot["items"]["nested"]
    assert dict_snapshot["type"] == "dict"
    assert dict_snapshot["length"] == ExceptionTracker.CONTEXT_MAX_ITEMS + 1
    assert dict_snapshot["truncated"] is True
    assert custom_snapshot["type"] == f"{_LargeContext.__module__}._LargeContext"
    assert "repr" in custom_snapshot
    assert nested_snapshot["items"][0]["type"] == "list"
    assert nested_snapshot["items"][0]["truncated"] is True


def test_get_exception_info_masks_after_snapshotting():
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


def test_get_exception_info_exposes_snapshots_when_unmasked():
    tracker = ExceptionTracker()

    try:
        _raise_with_large_context(_LargeContext())
    except Exception as error:
        result = tracker.get_exception_info(error, mask_presets=())

    local_variables = result.data["input_context"]["local_variables"]
    assert local_variables["type"] == "dict"
    assert local_variables["items"]["value"]["type"] == f"{_LargeContext.__module__}._LargeContext"
    assert local_variables["items"]["local_list"]["type"] == "list"
    assert local_variables["items"]["local_list"]["items"][0]["type"] == f"{_LargeContext.__module__}._LargeContext"


def test_exception_tracker_helper_structures_are_independent():
    info = tbot223_Exception.ExceptionTrackerHelper.get_error_info_structure()
    public_info = tbot223_Exception.ExceptionTrackerHelper.get_public_error_info_structure()

    info["input_context"]["params"]["args"] = ("changed",)
    public_info["tags"]["changed"] = True

    fresh_info = tbot223_Exception.ExceptionTrackerHelper.get_error_info_structure()
    fresh_public_info = tbot223_Exception.ExceptionTrackerHelper.get_public_error_info_structure()

    assert fresh_info["input_context"]["params"]["args"] is None
    assert fresh_public_info["tags"] == {}


def test_get_system_info_handles_unavailable_cwd(monkeypatch):
    monkeypatch.setattr(tbot223_Exception.os, "access", lambda path, mode: False)

    denied_info = tbot223_Exception.ExceptionTrackerHelper.get_system_info()

    assert denied_info["Current_Working_Directory"] == "<Permission Denied or Unavailable>"

    def broken_getcwd():
        raise RuntimeError("cwd failed")

    monkeypatch.setattr(tbot223_Exception.os, "getcwd", broken_getcwd)

    error_info = tbot223_Exception.ExceptionTrackerHelper.get_system_info()

    assert error_info["Current_Working_Directory"] == "<Permission Denied or Unavailable>"


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


def test_mapping_snapshot_keeps_non_string_keys_in_entries():
    key = object()
    snapshot = ExceptionTracker._snapshot_context({key: "value"})

    assert snapshot["items"] == {}
    assert snapshot["entries"][0]["key"]["type"] == "object"
    assert snapshot["entries"][0]["value"] == "value"


def test_exception_causes_breaks_cycles():
    tracker = ExceptionTracker()
    cause = ValueError("loop")
    error = RuntimeError("wrapper")
    error.__cause__ = cause
    cause.__cause__ = cause

    causes = tracker._get_exception_causes(error, limit=5)

    assert len(causes) == 1
    assert causes[0]["type"] == "ValueError"


def test_snapshot_context_covers_bytes_cycles_shape_and_failure_paths():
    tracker = ExceptionTracker()
    recursive = []
    recursive.append(recursive)

    bytes_snapshot = tracker._snapshot_context(b"x" * (ExceptionTracker.CONTEXT_MAX_REPR_LENGTH + 1))
    bytearray_snapshot = tracker._snapshot_context(bytearray(b"abc"))
    memoryview_snapshot = tracker._snapshot_context(memoryview(b"abcdef"))
    recursive_snapshot = tracker._snapshot_context(recursive)
    bad_mapping_snapshot = tracker._snapshot_context(_BadMapping())
    bad_sequence_snapshot = tracker._snapshot_context(_BadSequence([1]))

    assert bytes_snapshot["type"] == "bytes"
    assert bytes_snapshot["length"] == ExceptionTracker.CONTEXT_MAX_REPR_LENGTH + 1
    assert bytes_snapshot["truncated"] is True
    assert bytearray_snapshot["type"] == "bytearray"
    assert memoryview_snapshot["type"] == "memoryview"
    assert memoryview_snapshot["length"] == 6
    assert recursive_snapshot["items"][0] == {"type": "list", "cycle": True}
    assert bad_mapping_snapshot["type"] == f"{_BadMapping.__module__}._BadMapping"
    assert bad_mapping_snapshot["truncated"] is True
    assert bad_sequence_snapshot["type"] == f"{_BadSequence.__module__}._BadSequence"
    assert bad_sequence_snapshot["truncated"] is True


def test_metadata_snapshot_handles_len_repr_and_shape_edges():
    tracker = ExceptionTracker()

    assert tracker._safe_len(object()) is None
    assert tracker._safe_len(_BadLen()) is None
    assert tracker._safe_shape(_BadShape()) is None
    assert tracker._safe_shape(_StringShape()) == "rows"
    assert tracker._safe_shape(_TupleShape())[0] == 1
    assert tracker._safe_shape(_ListShape())[0] == 2
    assert tracker._safe_shape(_ObjectShape()) == "object"

    bad_repr, truncated = tracker._safe_repr(_BadRepr())
    assert bad_repr.startswith("<")
    assert truncated is False

    builtin_bad_repr, truncated = tracker._safe_repr(_PretendBuiltinBadRepr())
    assert builtin_bad_repr.startswith("<")
    assert truncated is False

    long_repr, truncated = tracker._safe_repr("x" * (ExceptionTracker.CONTEXT_MAX_REPR_LENGTH + 10))
    assert len(long_repr) == ExceptionTracker.CONTEXT_MAX_REPR_LENGTH
    assert truncated is True

    list_metadata = tracker._metadata_snapshot([1, 2], truncated=True)
    object_metadata = tracker._metadata_snapshot(_TupleShape())

    assert list_metadata["repr"] == "<list snapshot omitted>"
    assert list_metadata["truncated"] is True
    assert object_metadata["shape"][0] == 1


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
    assert info["input_context"]["params"]["args"]["type"] == "tuple"
    assert info["input_context"]["params"]["kwargs"]["type"] == "dict"
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

    original_builder = ExceptionTracker._build_public_error_info
    builder_calls = {"count": 0}

    def broken_builder(*args, **kwargs):
        builder_calls["count"] += 1
        if builder_calls["count"] == 1:
            raise RuntimeError("builder broke")
        return original_builder(**kwargs)

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

    monkeypatch.setattr(tbot223_Exception.traceback, "extract_tb", broken_extract_tb)
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
