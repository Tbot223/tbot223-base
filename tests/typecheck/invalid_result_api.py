from typing import Awaitable

from tbot223_base import ExceptionTrackerDecorator, Result, ResultStatus

# Keep diagnostics and their expected markers on the same line.
# fmt: off
missing_data: Result[int] = Result(ResultStatus.SUCCESS)  # expect-error: call-overload
wrong_data: Result[int] = Result(ResultStatus.SUCCESS, None, None, "wrong")  # expect-error: arg-type
raw_make = Result._make([ResultStatus.SUCCESS, None, None, 1])  # expect-error: attr-defined
raw_replace = Result.ok(1)._replace(data="wrong")  # expect-error: attr-defined
# fmt: on
wrong_index: str = Result.ok(1)[3]  # expect-error: assignment
status, error, context, data = Result.ok(1)
wrong_unpack: str = data  # expect-error: assignment


@ExceptionTrackerDecorator()
def automatic_factory() -> Awaitable[int]:
    raise ValueError("before creating awaitable")


async def unchecked_await() -> None:
    await automatic_factory()  # expect-error: misc
