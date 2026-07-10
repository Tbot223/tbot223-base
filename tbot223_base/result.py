# external modules
from collections.abc import Iterable
from enum import Enum
from typing import TYPE_CHECKING, Generic, NamedTuple, Optional, TypeVar, Union, cast

# internal modules

_RESULT_SENTINEL = object()
_DataT = TypeVar("_DataT")
_DefaultT = TypeVar("_DefaultT")


class ResultStatus(str, Enum):
    """
    Explicit status enum for `Result`.
    """

    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"

    @classmethod
    def normalize(cls, value: object) -> "ResultStatus":
        """
        Normalize `ResultStatus`, tri-state shorthand, and string input into a `ResultStatus`.
        """
        if isinstance(value, cls):
            return value
        if value is True:
            return cls.SUCCESS
        if value is False:
            return cls.FAILURE
        if value is None:
            return cls.CANCELLED
        if isinstance(value, str):
            normalized_value = value.strip().lower()
            for status in cls:
                if status.value == normalized_value:
                    return status
        raise ValueError(
            "Result status must be one of ResultStatus, bool, None, or a valid status string."
        )


class ResultUnwrapException(RuntimeError):
    """
    Raised when `unwrap()` or `expect()` is called on a `Result` that does not represent success.
    """

    def __init__(self, error: Optional[str], context: Optional[str], data: object) -> None:
        """
        Initialize the exception with the details stored in the `Result`.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `error` | `Optional[str]` | Error message associated with the failed result. |
        | **(R)** | `context` | `Optional[str]` | Additional context attached to the result. |
        | **(R)** | `data` | `object` | Payload stored in the result. |

        ### Returns
        `None` — Initializes the exception object.

        ### Example
        >>> from tbot223_base.result import Result, ResultStatus, ResultUnwrapException
        >>> try:
        ...     result = Result(status=ResultStatus.FAILURE, error="Some error", context="TestContext", data=None)
        ...     result.unwrap()
        ... except ResultUnwrapException as e:
        ...     print(e)
        """
        super().__init__(f"Cannot unwrap Result: {error}, Context: {context}, Data: {data}")
        self.error = error
        self.context = context
        self.data = data


if TYPE_CHECKING:
    class _ResultBase(NamedTuple, Generic[_DataT]):
        status: ResultStatus
        error: Optional[str]
        context: Optional[str]
        data: _DataT
else:
    class _ResultBase(NamedTuple):
        status: ResultStatus
        error: Optional[str]
        context: Optional[str]
        data: object


class Result(_ResultBase[_DataT], Generic[_DataT]):
    """
    Immutable tuple-like container that represents the outcome of an operation.

    `Result[_DataT]` stores an explicit `status` based on `ResultStatus`, so success,
    failure, and cancelled states are modeled directly instead of sharing one
    `Optional[bool]` field. The `success=` input and `result.success` property
    are supported tri-state shorthand APIs.

    - **(R)** = Required argument
    - **(O)** = Optional argument (has a default value)
    - **(D)** = Dependency Injection (advanced usage)

    ### Arguments
    | Tag | Name | Type | Description |
    |-----|------|------|-------------|
    | **(R)** | `status` | `ResultStatus` | Overall outcome. Use `SUCCESS`, `FAILURE`, or `CANCELLED`. |
    | **(R)** | `error` | `Optional[str]` | Human-readable error message. |
    | **(R)** | `context` | `Optional[str]` | Additional context about the operation. |
    | **(R)** | `data` | `_DataT` | Data returned from the operation. |

    ### Note
    > - Use `Result[T]` when the payload type is known.
    > - `unwrap()`, `expect()`, and `unwrap_or()` are convenience methods.
    > - `unwrap()` and `expect()` return `_DataT`.
    > - `success=` is supported as tri-state shorthand and is normalized into `status`.
    > - `result.success` returns the tri-state shorthand value `True`, `False`, or `None`.
    > - In most code, directly checking `status`, `error`, and `data` is recommended.

    ### Example
    >>> from tbot223_base.result import Result, ResultStatus
    >>> result: Result[dict[str, str]] = Result(status=ResultStatus.SUCCESS, error=None, context="FetchData", data={"key": "value"})
    >>> if result.is_success:
    ...     print("Operation succeeded with data:", result.data)
    """

    __slots__ = ()

    def __new__(
        cls: type["Result[_DataT]"],
        status: object = _RESULT_SENTINEL,
        error: Optional[str] = None,
        context: Optional[str] = None,
        data: _DataT = cast(_DataT, None),
        *,
        success: object = _RESULT_SENTINEL,
    ) -> "Result[_DataT]":
        if success is not _RESULT_SENTINEL:
            if status is not _RESULT_SENTINEL:
                raise TypeError("Use either `status` or `success` shorthand, not both.")
            status = success

        if status is _RESULT_SENTINEL:
            raise TypeError("Missing required argument: `status`.")

        normalized_status = ResultStatus.normalize(status)
        return cast("Result[_DataT]", tuple.__new__(cls, (normalized_status, error, context, data)))

    @classmethod
    def _make(cls: type["Result[_DataT]"], iterable: Iterable[object]) -> "Result[_DataT]":
        result = super()._make(iterable)
        return cls(result.status, result.error, result.context, cast(_DataT, result.data))

    def _replace(self, /, **kwds: object) -> "Result[_DataT]":
        return cast("Result[_DataT]", super()._replace(**kwds))

    @property
    def success(self) -> Optional[bool]:
        """
        Return the tri-state shorthand value for the current `status`.
        """
        if self.status is ResultStatus.SUCCESS:
            return True
        if self.status is ResultStatus.FAILURE:
            return False
        return None

    @property
    def is_success(self) -> bool:
        """
        Return whether the result represents success.
        """
        return self.status is ResultStatus.SUCCESS

    @property
    def is_failure(self) -> bool:
        """
        Return whether the result represents failure.
        """
        return self.status is ResultStatus.FAILURE

    @property
    def is_cancelled(self) -> bool:
        """
        Return whether the result represents a cancelled or non-executed state.
        """
        return self.status is ResultStatus.CANCELLED

    def unwrap(self) -> _DataT:
        """
        Return the contained `data` if the result is successful.

        ### Arguments
        None

        ### Constraint
        > - `self.status` MUST be `ResultStatus.SUCCESS`.

        ### Returns
        `_DataT` — The stored payload.

        ### Example
        >>> from tbot223_base.result import Result, ResultStatus
        >>> result: Result[dict[str, str]] = Result(status=ResultStatus.SUCCESS, error=None, context="FetchData", data={"key": "value"})
        >>> data = result.unwrap()
        >>> print(data)
        """
        if self.is_success:
            return self.data
        if self.is_failure:
            raise ResultUnwrapException(self.error, self.context, self.data)
        raise ResultUnwrapException("Operation was cancelled or not executed.", self.context, self.data)

    def expect(self, msg: str = "") -> _DataT:
        """
        Return the contained `data` if the result is successful.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(O)** | `msg` | `str` | Optional message to use if the result is not successful. Default: `""`. |

        ### Constraint
        > - `self.status` MUST be `ResultStatus.SUCCESS`.

        ### Returns
        `_DataT` — The stored payload.

        ### Example
        >>> from tbot223_base.result import Result, ResultStatus
        >>> result: Result[dict[str, str]] = Result(status=ResultStatus.SUCCESS, error=None, context="FetchData", data={"key": "value"})
        >>> data = result.expect("Should not fail")
        >>> print(data)
        """
        if self.is_success:
            return self.data
        error_message = msg or self.error
        if error_message is None and self.is_cancelled:
            error_message = "Operation was cancelled or not executed."
        raise ResultUnwrapException(error_message, self.context, self.data)

    def unwrap_or(self, default: _DefaultT) -> Union[_DataT, _DefaultT]:
        """
        Return the contained `data` if successful; otherwise return `default`.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `default` | `_DefaultT` | Fallback value. |

        ### Returns
        `Union[_DataT, _DefaultT]` — The stored payload if successful, otherwise `default`.

        ### Example
        >>> from tbot223_base.result import Result, ResultStatus
        >>> result: Result[dict[str, str]] = Result(status=ResultStatus.FAILURE, error="Not Found", context="FetchData", data=None)
        >>> data = result.unwrap_or({"key": "default_value"})
        >>> print(data)
        """
        if self.is_success:
            return self.data
        return default
