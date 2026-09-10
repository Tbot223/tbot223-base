"""Explicit immutable operation results."""

from enum import Enum
from typing import ClassVar, Generic, Literal, Optional, TypeVar, Union, cast, overload

_RESULT_SENTINEL = object()
_DataT = TypeVar("_DataT")
_DefaultT = TypeVar("_DefaultT")


class ResultStatus(str, Enum):
    """Define the explicit outcome states supported by `Result`."""

    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"

    @classmethod
    def normalize(cls, value: object) -> "ResultStatus":
        """
        Normalize a status enum, tri-state shorthand, or status string.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `value` | `object` | A `ResultStatus`, `bool`, `None`, or valid status string. |

        ### Returns
        `ResultStatus` — The normalized explicit outcome state.

        ### Raises
        `ValueError` — If `value` is not a supported status representation.
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
    """Represent an attempt to unwrap a non-success `Result`."""

    def __init__(
        self, error: Optional[str], context: Optional[str], data: object
    ) -> None:
        """
        Initialize an unwrap failure without formatting stored result values.

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
        ...     Result(ResultStatus.FAILURE, "Some error", "TestContext", None).unwrap()
        ... except ResultUnwrapException as error:
        ...     str(error)
        'Cannot unwrap a non-success Result.'
        """
        super().__init__("Cannot unwrap a non-success Result.")
        self.error = error
        self.context = context
        self.data = data


class Result(
    tuple[ResultStatus, Optional[str], Optional[str], _DataT], Generic[_DataT]
):
    """
    Represent an immutable tuple-like operation outcome with explicit payload data.

    `Result[_DataT]` stores `(status, error, context, data)` and keeps tuple
    unpacking, indexing, and equality semantics. `data` is required for every
    result state; use `None` explicitly when a result intentionally has no payload.

    ### Arguments
    | Tag | Name | Type | Description |
    |-----|------|------|-------------|
    | **(R)** | `status` | `ResultStatus` | Overall outcome when using positional construction. |
    | **(O)** | `error` | `Optional[str]` | Human-readable error message. Default: `None`. |
    | **(O)** | `context` | `Optional[str]` | Additional context about the operation. Default: `None`. |
    | **(R)** | `data` | `_DataT` | Payload for the outcome. |

    ### Raises
    `TypeError` — If `status` is missing, `status` and `success` are both supplied, or `data` is omitted.

    ### Note
    > - Use `Result.ok()`, `Result.failure()`, or `Result.cancelled()` for new code.
    > - `success=` remains a tri-state construction shorthand and is normalized into `status`.
    > - Raw `NamedTuple` reconstruction helpers are intentionally not part of this API.

    ### Example
    >>> from tbot223_base.result import Result
    >>> result = Result.ok({"key": "value"}, context="FetchData")
    >>> result.unwrap()["key"]
    'value'
    """

    __slots__ = ()
    _fields: ClassVar[tuple[str, str, str, str]] = (
        "status",
        "error",
        "context",
        "data",
    )
    __match_args__: ClassVar[
        tuple[Literal["status"], Literal["error"], Literal["context"], Literal["data"]]
    ] = ("status", "error", "context", "data")

    @overload
    def __new__(
        cls: type["Result[_DataT]"],
        status: object,
        error: Optional[str],
        context: Optional[str],
        data: _DataT,
        /,
    ) -> "Result[_DataT]": ...

    @overload
    def __new__(
        cls: type["Result[_DataT]"],
        *,
        status: object,
        data: _DataT,
        error: Optional[str] = ...,
        context: Optional[str] = ...,
    ) -> "Result[_DataT]": ...

    @overload
    def __new__(
        cls: type["Result[_DataT]"],
        *,
        success: object,
        data: _DataT,
        error: Optional[str] = ...,
        context: Optional[str] = ...,
    ) -> "Result[_DataT]": ...

    def __new__(
        cls: type["Result[_DataT]"],
        status: object = _RESULT_SENTINEL,
        error: Optional[str] = None,
        context: Optional[str] = None,
        data: object = _RESULT_SENTINEL,
        *,
        success: object = _RESULT_SENTINEL,
    ) -> "Result[_DataT]":
        """
        Create an immutable result with explicit status and payload data.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `status` | `object` | Status value unless `success` shorthand is supplied. |
        | **(O)** | `error` | `Optional[str]` | Human-readable error message. Default: `None`. |
        | **(O)** | `context` | `Optional[str]` | Additional operation context. Default: `None`. |
        | **(R)** | `data` | `_DataT` | Payload for every outcome state. |
        | **(O)** | `success` | `object` | Tri-state shorthand used instead of `status`. |

        ### Returns
        `Result[_DataT]` — An immutable normalized result.

        ### Raises
        `TypeError` — If required construction inputs are absent or both status forms are supplied.
        `ValueError` — If the supplied status cannot be normalized.
        """
        if success is not _RESULT_SENTINEL:
            if status is not _RESULT_SENTINEL:
                raise TypeError("Use either `status` or `success` shorthand, not both.")
            status = success

        if status is _RESULT_SENTINEL:
            raise TypeError("Missing required argument: `status`.")
        if data is _RESULT_SENTINEL:
            raise TypeError("Missing required argument: `data`.")

        normalized_status = ResultStatus.normalize(status)
        return cast(
            "Result[_DataT]",
            tuple.__new__(cls, (normalized_status, error, context, data)),
        )

    def __getnewargs__(
        self,
    ) -> tuple[ResultStatus, Optional[str], Optional[str], _DataT]:
        """Preserve validated constructor arguments for copy and pickle."""
        return self.status, self.error, self.context, self.data

    @classmethod
    def ok(
        cls: type["Result[_DataT]"],
        data: _DataT,
        *,
        context: Optional[str] = None,
    ) -> "Result[_DataT]":
        """
        Build a successful `Result` with required payload data.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `data` | `_DataT` | Payload returned by the successful operation. |
        | **(O)** | `context` | `Optional[str]` | Additional operation context. Default: `None`. |

        ### Returns
        `Result[_DataT]` — A result with `ResultStatus.SUCCESS`.
        """
        return cls(ResultStatus.SUCCESS, None, context, data)

    @classmethod
    def failure(
        cls: type["Result[_DataT]"],
        data: _DataT,
        *,
        error: Optional[str] = None,
        context: Optional[str] = None,
    ) -> "Result[_DataT]":
        """
        Build a failed `Result` with required payload data.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `data` | `_DataT` | Payload associated with the failed operation. |
        | **(O)** | `error` | `Optional[str]` | Human-readable failure message. Default: `None`. |
        | **(O)** | `context` | `Optional[str]` | Additional operation context. Default: `None`. |

        ### Returns
        `Result[_DataT]` — A result with `ResultStatus.FAILURE`.
        """
        return cls(ResultStatus.FAILURE, error, context, data)

    @classmethod
    def cancelled(
        cls: type["Result[_DataT]"],
        data: _DataT,
        *,
        error: Optional[str] = None,
        context: Optional[str] = None,
    ) -> "Result[_DataT]":
        """
        Build a cancelled `Result` with required payload data.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `data` | `_DataT` | Payload associated with the cancelled operation. |
        | **(O)** | `error` | `Optional[str]` | Cancellation message. Default: `None`. |
        | **(O)** | `context` | `Optional[str]` | Additional operation context. Default: `None`. |

        ### Returns
        `Result[_DataT]` — A result with `ResultStatus.CANCELLED`.
        """
        return cls(ResultStatus.CANCELLED, error, context, data)

    @property
    def status(self) -> ResultStatus:
        """
        Return the normalized explicit outcome state.

        ### Arguments
        None

        ### Returns
        `ResultStatus` — The stored outcome state.
        """
        return cast(ResultStatus, self[0])

    @property
    def error(self) -> Optional[str]:
        """
        Return the stored human-readable error message.

        ### Arguments
        None

        ### Returns
        `Optional[str]` — The stored error message, if any.
        """
        return cast(Optional[str], self[1])

    @property
    def context(self) -> Optional[str]:
        """
        Return the stored operation context.

        ### Arguments
        None

        ### Returns
        `Optional[str]` — The stored context, if any.
        """
        return cast(Optional[str], self[2])

    @property
    def data(self) -> _DataT:
        """
        Return the payload stored for this outcome.

        ### Arguments
        None

        ### Returns
        `_DataT` — The stored payload.
        """
        return cast(_DataT, self[3])

    @property
    def success(self) -> Optional[bool]:
        """
        Return the tri-state shorthand value for the current `status`.

        ### Arguments
        None

        ### Returns
        `Optional[bool]` — `True`, `False`, or `None` for success, failure, or cancellation.
        """
        if self.status is ResultStatus.SUCCESS:
            return True
        if self.status is ResultStatus.FAILURE:
            return False
        return None

    @property
    def is_success(self) -> bool:
        """
        Return whether this result represents success.

        ### Arguments
        None

        ### Returns
        `bool` — `True` only when `status` is `ResultStatus.SUCCESS`.
        """
        return self.status is ResultStatus.SUCCESS

    @property
    def is_failure(self) -> bool:
        """
        Return whether this result represents failure.

        ### Arguments
        None

        ### Returns
        `bool` — `True` only when `status` is `ResultStatus.FAILURE`.
        """
        return self.status is ResultStatus.FAILURE

    @property
    def is_cancelled(self) -> bool:
        """
        Return whether this result represents cancellation.

        ### Arguments
        None

        ### Returns
        `bool` — `True` only when `status` is `ResultStatus.CANCELLED`.
        """
        return self.status is ResultStatus.CANCELLED

    def unwrap(self) -> _DataT:
        """
        Return `data` when this result is successful.

        ### Arguments
        None

        ### Returns
        `_DataT` — The stored payload.

        ### Raises
        `ResultUnwrapException` — If `status` is not `ResultStatus.SUCCESS`.

        ### Example
        >>> from tbot223_base.result import Result
        >>> Result.ok({"key": "value"}).unwrap()["key"]
        'value'
        """
        if self.is_success:
            return self.data
        if self.is_failure:
            raise ResultUnwrapException(self.error, self.context, self.data)
        raise ResultUnwrapException(
            self.error or "Operation was cancelled or not executed.",
            self.context,
            self.data,
        )

    def expect(self, msg: str = "") -> _DataT:
        """
        Return `data` when successful or raise with an optional caller message.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(O)** | `msg` | `str` | Message stored on the unwrap exception. Default: `""`. |

        ### Returns
        `_DataT` — The stored payload.

        ### Raises
        `ResultUnwrapException` — If `status` is not `ResultStatus.SUCCESS`.

        ### Example
        >>> from tbot223_base.result import Result
        >>> Result.ok(42).expect("Should not fail")
        42
        """
        if self.is_success:
            return self.data
        error_message = msg or self.error
        if error_message is None and self.is_cancelled:
            error_message = "Operation was cancelled or not executed."
        raise ResultUnwrapException(error_message, self.context, self.data)

    def unwrap_or(self, default: _DefaultT) -> Union[_DataT, _DefaultT]:
        """
        Return `data` when successful and `default` otherwise.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `default` | `_DefaultT` | Fallback value for a non-success result. |

        ### Returns
        `Union[_DataT, _DefaultT]` — The stored payload or `default`.

        ### Example
        >>> from tbot223_base.result import Result
        >>> Result.failure(None, error="Not Found").unwrap_or("fallback")
        'fallback'
        """
        if self.is_success:
            return self.data
        return default
