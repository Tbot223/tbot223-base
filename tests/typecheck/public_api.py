from typing import Awaitable, TYPE_CHECKING, Union

from tbot223_base import ExceptionTrackerDecorator, Result


decorator = ExceptionTrackerDecorator()


@decorator
def sync_value(value: int) -> int:
    return value


@decorator
async def async_value(value: int) -> int:
    return value


async def raw_async_value(value: int) -> int:
    return value


@decorator
def awaitable_value(value: int) -> Awaitable[int]:
    return raw_async_value(value)


if TYPE_CHECKING:
    sync_result: Union[int, Result[object]] = sync_value(1)
    async_result: Awaitable[Union[int, Result[object]]] = async_value(1)
    awaitable_result: Awaitable[Union[int, Result[object]]] = awaitable_value(1)
