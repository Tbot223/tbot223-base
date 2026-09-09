from typing import TYPE_CHECKING, Awaitable, Union

from tbot223_base import ExceptionTrackerDecorator, Result

decorator = ExceptionTrackerDecorator()


@decorator
def sync_value(value: int) -> int:
    return value


@decorator.wrap_awaitable
async def async_value(value: int) -> int:
    return value


async def raw_async_value(value: int) -> int:
    return value


@decorator.wrap_awaitable
def awaitable_value(value: int) -> Awaitable[int]:
    return raw_async_value(value)


if TYPE_CHECKING:
    sync_result: Union[int, Result[object]] = sync_value(1)
    async_result: Awaitable[Union[int, Result[object]]] = async_value(1)
    awaitable_result: Awaitable[Union[int, Result[object]]] = awaitable_value(1)

    result: Result[int] = Result.ok(1)
    payload: int = result[3]
    negative_payload: int = result[-1]
    status, error, context, data = result
    unpacked_payload: int = data
    unwrapped_payload: int = result.unwrap()
