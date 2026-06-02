from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from guaro.execution.context import ExecutionContext


class Middleware(Protocol):
    async def before(self, ctx: ExecutionContext) -> None: ...

    async def after(self, ctx: ExecutionContext, result: Any) -> None: ...

    async def on_error(self, ctx: ExecutionContext, exc: Exception) -> None: ...


async def _maybe_await(value: Any) -> Any:
    if hasattr(value, "__await__"):
        return await value
    return value


@dataclass(slots=True)
class ExecutionPipeline:
    middleware: list[Any] = field(default_factory=list)

    async def before(self, ctx: ExecutionContext) -> None:
        for item in self.middleware:
            before_hook = getattr(item, "before", None)
            if before_hook is not None:
                await _maybe_await(before_hook(ctx))
            elif callable(item):
                await _maybe_await(item(ctx, route=ctx.route))

    async def after(self, ctx: ExecutionContext, result: Any) -> None:
        for item in reversed(self.middleware):
            after_hook = getattr(item, "after", None)
            if after_hook is not None:
                await _maybe_await(after_hook(ctx, result))

    async def on_error(self, ctx: ExecutionContext, exc: Exception) -> None:
        for item in reversed(self.middleware):
            error_hook = getattr(item, "on_error", None)
            if error_hook is not None:
                await _maybe_await(error_hook(ctx, exc))
