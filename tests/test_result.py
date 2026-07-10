import pytest

import tbot223_base
from tbot223_base.result import Result, ResultStatus, ResultUnwrapException


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


def test_result_accepts_status_and_success_shorthand_inputs():
    modern = Result(ResultStatus.SUCCESS, None, "Modern", 123)
    shorthand = Result(success=False, error="boom", context="Shorthand", data=None)

    assert modern.status is ResultStatus.SUCCESS
    assert modern.success is True
    assert shorthand.status is ResultStatus.FAILURE
    assert shorthand.success is False


@pytest.mark.parametrize(
    ("status", "expected_status"),
    [
        (ResultStatus.SUCCESS, ResultStatus.SUCCESS),
        (True, ResultStatus.SUCCESS),
        (False, ResultStatus.FAILURE),
        (None, ResultStatus.CANCELLED),
        (" cancelled ", ResultStatus.CANCELLED),
    ],
)
def test_result_make_and_replace_normalize_reconstructed_status(status, expected_status):
    reconstructed = Result._make([status, None, "Reconstructed", 123])
    replaced = reconstructed._replace(status=status)

    assert reconstructed.status is expected_status
    assert replaced.status is expected_status
    assert replaced.context == "Reconstructed"


def test_result_reconstruction_preserves_namedtuple_behavior():
    class DerivedResult(Result[int]):
        pass

    result = DerivedResult._make(["success", None, "Derived", 1])
    replaced = result._replace(data=2)

    assert isinstance(result, DerivedResult)
    assert result.status is ResultStatus.SUCCESS
    assert replaced == DerivedResult(ResultStatus.SUCCESS, None, "Derived", 2)

    with pytest.raises(TypeError):
        Result._make([ResultStatus.SUCCESS])

    with pytest.raises((TypeError, ValueError)):
        result._replace(extra=3)


def test_result_reconstruction_rejects_invalid_status():
    with pytest.raises(ValueError):
        Result._make(["invalid", None, "Reconstructed", 123])

    with pytest.raises(ValueError):
        Result(ResultStatus.SUCCESS, None, "Original", 123)._replace(status="invalid")


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
