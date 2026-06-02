from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any

from guaro.core.registry import Registry
from guaro.execution.context import ExecutionContext


@dataclass(slots=True)
class DependencyInjector:
    registry: Registry

    async def resolve(self, resolver: Any, context: ExecutionContext, initial_kwargs: dict[str, Any] | None = None) -> dict[str, Any]:
        provided = dict(initial_kwargs or {})
        signature = inspect.signature(resolver)

        for parameter in signature.parameters.values():
            if parameter.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
                continue
            if parameter.name in provided:
                continue

            value = self._resolve_parameter(parameter, context)
            if value is _MISSING:
                if parameter.default is inspect._empty:
                    raise TypeError(f"Cannot resolve dependency '{parameter.name}' for {resolver.__name__}")
                continue
            provided[parameter.name] = value

        return provided

    def _resolve_parameter(self, parameter: inspect.Parameter, context: ExecutionContext) -> Any:
        if parameter.name in {"ctx", "context"}:
            return context
        if parameter.annotation is ExecutionContext:
            return context
        if parameter.name == "request":
            return context.request
        if parameter.name == "response":
            return context.response
        if parameter.name in {"current_user", "user"}:
            return context.user
        if parameter.name in context.loaders:
            return context.loaders[parameter.name]
        if parameter.name in context.params:
            return context.params[parameter.name]
        if parameter.name in self.registry.dependencies:
            provider = self.registry.dependencies[parameter.name]
            return provider(context) if callable(provider) else provider
        return _MISSING


class _Missing:
    pass


_MISSING = _Missing()
