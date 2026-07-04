import pytest

from tbot223_base.tbot223_Result import Result, ResultStatus, ResultUnwrapException


def test_result_status_normalize_accepts_enum_bool_none_and_string():
    assert ResultStatus.normalize(ResultStatus.SUCCESS) is ResultStatus.SUCCESS
    assert ResultStatus.normalize(True) is ResultStatus.SUCCESS
    assert ResultStatus.normalize(False) is ResultStatus.FAILURE
    assert ResultStatus.normalize(None) is ResultStatus.CANCELLED
    assert ResultStatus.normalize("success") is ResultStatus.SUCCESS
    assert ResultStatus.normalize(" FAILURE ") is ResultStatus.FAILURE


def test_result_status_normalize_rejects_invalid_value():
    with pytest.raises(ValueError):
        ResultStatus.normalize("unknown")


def test_result_accepts_status_and_legacy_success_inputs():
    modern = Result(ResultStatus.SUCCESS, None, "Modern", 123)
    legacy = Result(success=False, error="boom", context="Legacy", data=None)

    assert modern.status is ResultStatus.SUCCESS
    assert modern.success is True
    assert legacy.status is ResultStatus.FAILURE
    assert legacy.success is False


def test_result_supports_generic_runtime_subscription():
    result = Result[int](ResultStatus.SUCCESS, None, "Typed", 123)

    assert isinstance(result, Result)
    assert result.data == 123
    assert result.unwrap() == 123
    assert result.expect() == 123
    assert result.unwrap_or("fallback") == 123
    assert Result.__parameters__


def test_result_rejects_missing_or_conflicting_status_inputs():
    with pytest.raises(TypeError):
        Result()

    with pytest.raises(TypeError):
        Result(ResultStatus.SUCCESS, success=True)


def test_result_predicates_and_unwrap_helpers():
    success_result = Result(ResultStatus.SUCCESS, None, "SuccessCase", {"value": 1})
    failure_result = Result(ResultStatus.FAILURE, "boom", "FailureCase", None)
    cancelled_result = Result(ResultStatus.CANCELLED, None, "CancelledCase", None)

    assert success_result.is_success is True
    assert success_result.is_failure is False
    assert success_result.is_cancelled is False
    assert success_result.unwrap() == {"value": 1}
    assert success_result.expect() == {"value": 1}
    assert success_result.unwrap_or("fallback") == {"value": 1}

    assert failure_result.is_success is False
    assert failure_result.is_failure is True
    assert failure_result.unwrap_or("fallback") == "fallback"

    with pytest.raises(ResultUnwrapException) as failure_error:
        failure_result.unwrap()
    assert failure_error.value.error == "boom"

    with pytest.raises(ResultUnwrapException) as cancelled_error:
        cancelled_result.expect()
    assert cancelled_error.value.error == "Operation was cancelled or not executed."


def test_result_cancelled_success_property_and_unwrap():
    result = Result(ResultStatus.CANCELLED, None, "Skipped", None)

    assert result.success is None

    with pytest.raises(ResultUnwrapException) as error:
        result.unwrap()

    assert error.value.error == "Operation was cancelled or not executed."
    assert error.value.context == "Skipped"


def test_result_expect_uses_custom_message_for_failure():
    result = Result(ResultStatus.FAILURE, "raw failure", "Check", {"debug": True})

    with pytest.raises(ResultUnwrapException) as error:
        result.expect("custom failure")

    assert error.value.error == "custom failure"
    assert error.value.data == {"debug": True}
