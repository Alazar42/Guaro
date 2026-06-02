from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from guaro.core.execution_engine import ExecutionEngine
from guaro.core.registry import Registry
from guaro.execution.context import ExecutionContext
from guaro.execution.planner import build_field_tree, normalize_field_selection
from guaro.loaders.relation_loader import clone_request_loaders


@dataclass
class RestAdapter:
    registry: Registry
    engine: ExecutionEngine

    def build_app(self) -> Any:
        try:
            from starlette.applications import Starlette
            from starlette.responses import JSONResponse
            from starlette.routing import Route
        except ImportError as exc:  # pragma: no cover - optional dependency guard
            raise RuntimeError("Starlette is required for REST support") from exc

        routes: list[Any] = []
        for route in self.registry.routes:
            routes.append(Route(route.path, self._build_handler(route, JSONResponse), methods=[route.method]))
        return Starlette(routes=routes)

    def _build_handler(self, route: Any, json_response: Any):
        async def handler(request: Any) -> Any:
            try:
                kwargs = await self._extract_kwargs(route, request)
                selected_fields = normalize_field_selection(self._extract_fields(request))
                context = ExecutionContext(
                    request=request,
                    response=None,
                    selected_fields=set(selected_fields),
                    field_tree=build_field_tree(selected_fields),
                    loaders=clone_request_loaders(self.registry.loaders),
                    transport="rest",
                    params=dict(request.path_params),
                    user=self._extract_user(request),
                    permissions=self._extract_permissions(request),
                )
                result = await self.engine.execute(route, context=context, kwargs=kwargs)
                return json_response(result.data)
            except PermissionError as exc:
                return json_response({"detail": str(exc)}, status_code=401)
            except Exception as exc:
                # Graceful, user-facing error without traceback leakage.
                return json_response(
                    {
                        "detail": "Request failed",
                        "error": str(exc),
                        "route": route.path,
                    },
                    status_code=500,
                )

        return handler

    async def _extract_kwargs(self, route: Any, request: Any) -> dict[str, Any]:
        kwargs = dict(request.path_params)
        if request.method in {"POST", "PUT", "PATCH"}:
            try:
                body = await request.json()
            except Exception:
                body = {}
            if isinstance(body, dict):
                kwargs.update(body)
        return kwargs

    def _extract_fields(self, request: Any) -> list[str]:
        value = request.query_params.get("fields")
        return value.split(",") if value else []

    def _extract_user(self, request: Any) -> Any:
        if hasattr(request, "headers"):
            return request.headers.get("authorization")
        return None

    def _extract_permissions(self, request: Any) -> set[str]:
        permissions: set[str] = set()
        headers = getattr(request, "headers", {})
        if hasattr(headers, "get"):
            raw = headers.get("x-guaro-permissions", "")
            permissions.update(item.strip() for item in raw.split(",") if item.strip())
        state_permissions = getattr(getattr(request, "state", object()), "permissions", None)
        if isinstance(state_permissions, (list, tuple, set)):
            permissions.update(str(item) for item in state_permissions)
        return permissions
