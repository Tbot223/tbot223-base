import pytest

import tbot223_base
from tbot223_base.result import Result, ResultStatus, ResultUnwrapException


class _BrokenStringValue:
    def __str__(self):
        raise AssertionError("stored result data must not be formatted")


def test_result_status_normalize_accepts_enum_bool_none_and_string():
    assert ResultStatus.normalize(ResultStatus.SUCCESS) is ResultStatus.SUCCESS
    assert ResultStatus.normalize(True) is ResultStatus.SUCCESS
    assert ResultStatus.normalize(False) is ResultStatus.FAILURE
    assert ResultStatus.normalize(None) is ResultStatus.CANCELLED
    assert ResultStatus.normalize("success") is ResultStatus.SUCCESS
    assert ResultStatus.normalize(" FAILURE ") is ResultStatus.FAILURE


def test_result_package_exports_share_api_objects():
    assert tbot223_base.Result is Result
    assert tbot223_base.ResultStatus is ResultStatus
    assert tbot223_base.ResultUnwrapException is ResultUnwrapException


def test_result_status_normalize_rejects_invalid_value():
    with pytest.raises(ValueError):
        ResultStatus.normalize("unknown")


def test_result_accepts_explicit_data_with_status_or_success_shorthand():
    modern = Result(ResultStatus.SUCCESS, None, "Modern", 123)
    shorthand = Result(success=False, error="boom", context="Shorthand", data=None)

    assert modern.status is ResultStatus.SUCCESS
    assert modern.success is True
    assert shorthand.status is ResultStatus.FAILURE
    assert shorthand.success is False


def test_result_requires_data_and_rejects_conflicting_status_inputs():
    with pytest.raises(TypeError, match="Missing required argument: `data`"):
        Result(ResultStatus.SUCCESS)

    with pytest.raises(TypeError, match="Missing required argument: `status`"):
        Result()

    with pytest.raises(TypeError, match="Use either `status` or `success`"):
        Result(ResultStatus.SUCCESS, None, None, 1, success=True)


def test_result_factories_build_explicit_statuses_with_required_payloads():
    success = Result.ok({"value": 1}, context="SuccessCase")
    failure = Result.failure(None, error="boom", context="FailureCase")
    cancelled = Result.cancelled(None, context="CancelledCase")

    assert success == (ResultStatus.SUCCESS, None, "SuccessCase", {"value": 1})
    assert failure == (ResultStatus.FAILURE, "boom", "FailureCase", None)
    assert cancelled == (ResultStatus.CANCELLED, None, "CancelledCase", None)
    assert tuple(success) == (success.status, success.error, success.context, success.data)


def test_result_retains_tuple_like_behavior_without_raw_reconstruction_helpers():
    result = Result.ok(123, context="Typed")
    status, error, context, data = result

    assert isinstance(result, tuple)
    assert result[3] == 123
    assert (status, error, context, data) == (ResultStatus.SUCCESS, None, "Typed", 123)
    assert not hasattr(Result, "_make")
    assert not hasattr(result, "_replace")


def test_result_supports_generic_runtime_subscription_and_helpers():
    result = Result[int](ResultStatus.SUCCESS, None, "Typed", 123)

    assert isinstance(result, Result)
    assert result.data == 123
    assert result.unwrap() == 123
    assert result.expect() == 123
    assert result.unwrap_or("fallback") == 123
    assert Result.__parameters__


def test_result_predicates_and_unwrap_helpers():
    success_result = Result.ok({"value": 1}, context="SuccessCase")
    failure_result = Result.failure(None, error="boom", context="FailureCase")
    cancelled_result = Result.cancelled(None, context="CancelledCase")

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


def test_result_unwrap_exception_never_formats_stored_values():
    unsafe_data = _BrokenStringValue()
    result = Result.failure(unsafe_data, error="internal secret", context="Sensitive")

    with pytest.raises(ResultUnwrapException) as captured:
        result.unwrap()

    assert str(captured.value) == "Cannot unwrap a non-success Result."
    assert captured.value.error == "internal secret"
    assert captured.value.context == "Sensitive"
    assert captured.value.data is unsafe_data


def test_result_unwrap_exception_message_omits_large_and_sensitive_data():
    secret = "secret-token-" + ("x" * 4096)

    with pytest.raises(ResultUnwrapException) as captured:
        Result.failure(secret, error="failure", context="context").expect()

    assert secret not in str(captured.value)


def test_result_expect_uses_custom_message_for_failure():
    result = Result.failure({"debug": True}, error="raw failure", context="Check")

    with pytest.raises(ResultUnwrapException) as error:
        result.expect("custom failure")

    assert error.value.error == "custom failure"
    assert error.value.data == {"debug": True}
