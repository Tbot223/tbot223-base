from tbot223_base.tbot223_Exception import ExceptionTracker, ExceptionTrackerDecorator
from tbot223_base.tbot223_Result import Result, ResultStatus


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
