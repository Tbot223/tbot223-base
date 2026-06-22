#external Modules
from typing import Any, NamedTuple, Optional

#internal Modules

class ResultUnwrapException(RuntimeError):
    """
    Raised when `unwrap()` or `expect()` is called on a `Result` that does not represent success.
    """
    def __init__(self, error, context, data):
        """
        Initialize the exception with the details stored in the `Result`.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `error` | `Optional[str]` | Error message associated with the failed result. |
        | **(R)** | `context` | `Optional[str]` | Additional context attached to the result. |
        | **(R)** | `data` | `Any` | Payload stored in the result. |

        ### Returns
        `None` — Initializes the exception object.

        ### Example
        >>> from tbot223_base.tbot223_Result import Result, ResultUnwrapException
        >>> try:
        >>>     result = Result(success=False, error="Some error", context="TestContext", data=None)
        >>>     result.unwrap()
        >>> except ResultUnwrapException as e:
        >>>     print(e)
        """
        super().__init__(f"Cannot unwrap Result: {error}, Context: {context}, Data: {data}")
        self.error = error
        self.context = context
        self.data = data

class Result(NamedTuple):
    """
    Immutable container that represents the outcome of an operation.

    `Result` is implemented as a `NamedTuple`, so instances are lightweight,
    readable, and immutable once created. This makes it easier to pass results
    across application layers without accidentally changing their state.

    - **(R)** = Required argument
    - **(O)** = Optional argument (has a default value)
    - **(D)** = Dependency Injection (advanced usage)

    ### Arguments
    | Tag | Name | Type | Description |
    |-----|------|------|-------------|
    | **(R)** | `success` | `Optional[bool]` | Overall outcome. `True` on success, `False` on failure, `None` for neither. |
    | **(R)** | `error` | `Optional[str]` | Human-readable error message. |
    | **(R)** | `context` | `Optional[str]` | Additional context about the operation. |
    | **(R)** | `data` | `Any` | Data returned from the operation. |

    ### Note
    > - `unwrap()`, `expect()`, and `unwrap_or()` are convenience methods.
    > - In most code, directly checking `success`, `error`, and `data` is recommended.

    ### Example
    >>> from tbot223_base.tbot223_Result import Result
    >>> result = Result(success=True, error=None, context="FetchData", data={"key": "value"})
    >>> if result.success:
    >>>     print("Operation succeeded with data:", result.data)
    """
    success: Optional[bool]
    error: Optional[str]
    context: Optional[str]
    data: Any

    def unwrap(self) -> Any:
        """
        Return the contained `data` if the result is successful.

        ### Arguments
        None

        ### Constraint
        > - `self.success` MUST be `True`.

        ### Returns
        `Any` — The stored payload.

        ### Example
        >>> from tbot223_base.tbot223_Result import Result
        >>> result = Result(success=True, error=None, context="FetchData", data={"key": "value"})
        >>> data = result.unwrap()
        >>> print(data)
        """
        if self.success is True:
            return self.data
        elif self.success is False:
            raise ResultUnwrapException(self.error, self.context, self.data)
        else:
            raise ResultUnwrapException("Operation was cancelled or not executed.", self.context, self.data)

    def expect(self, msg: str = "") -> Any:
        """
        Return the contained `data` if the result is successful.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(O)** | `msg` | `str` | Optional message to use if the result is not successful. Default: `""`. |

        ### Constraint
        > - `self.success` MUST be `True`.

        ### Returns
        `Any` — The stored payload.

        ### Example
        >>> from tbot223_base.tbot223_Result import Result
        >>> result = Result(success=True, error=None, context="FetchData", data={"key": "value"})
        >>> data = result.expect("Should not fail")
        >>> print(data)
        """
        if self.success is True:
            return self.data
        error_message = msg or self.error
        if error_message is None and self.success is None:
            error_message = "Operation was cancelled or not executed."
        raise ResultUnwrapException(error_message, self.context, self.data)

    def unwrap_or(self, default: Any) -> Any:
        """
        Return the contained `data` if successful; otherwise return `default`.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `default` | `Any` | Fallback value. |

        ### Returns
        `Any` — The stored payload if successful, otherwise `default`.

        ### Example
        >>> from tbot223_base.tbot223_Result import Result
        >>> result = Result(success=False, error="Not Found", context="FetchData", data=None)
        >>> data = result.unwrap_or({"key": "default_value"})
        >>> print(data)
        """
        if self.success is True:
            return self.data
        return default
