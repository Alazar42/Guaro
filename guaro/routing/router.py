from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from guaro.routing.route import RouteDefinition


@dataclass
class Router:
    prefix: str = ""
    routes: list[Any] = field(default_factory=list)

    def _register(self, method: str, path: str, resolver: Callable[..., Any]) -> Callable[..., Any]:
        route_definition = RouteDefinition(
            method=method,
            path=f"{self.prefix}{path}",
            resolver=resolver,
            permissions=list(getattr(resolver, "__guaro_permissions__", [])),
            middleware=list(getattr(resolver, "__guaro_middleware__", [])),
        )
        self.routes.append(route_definition.metadata)
        return resolver

    def get(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(resolver: Callable[..., Any]) -> Callable[..., Any]:
            return self._register("GET", path, resolver)

        return decorator

    def post(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(resolver: Callable[..., Any]) -> Callable[..., Any]:
            return self._register("POST", path, resolver)

        return decorator

    def put(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(resolver: Callable[..., Any]) -> Callable[..., Any]:
            return self._register("PUT", path, resolver)

        return decorator

    def delete(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(resolver: Callable[..., Any]) -> Callable[..., Any]:
            return self._register("DELETE", path, resolver)

        return decorator
