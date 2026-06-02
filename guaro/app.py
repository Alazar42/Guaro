from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from guaro.config import normalize_database_config
from guaro.config.schema import NormalizedDatabaseConfig
from guaro.core.execution_engine import ExecutionEngine
from guaro.core.registry import Registry
from guaro.core.schema import compile_model_schema

logger = logging.getLogger("guaro.app")
from guaro.graphql.adapter import GraphQLAdapter
from guaro.rest.adapter import RestAdapter


@dataclass(slots=True)
class API:
    registry: Registry = field(default_factory=Registry)
    database: Any = None  # Accepts dict, str, NormalizedDatabaseConfig, or None
    engine: ExecutionEngine = field(init=False)
    db_config: NormalizedDatabaseConfig = field(init=False)

    def __post_init__(self) -> None:
        # Normalize database config once at startup
        self.db_config = normalize_database_config(self.database)
        # Store in registry for adapters and repositories to access
        self.registry.db_config = self.db_config
        self.engine = ExecutionEngine(self.registry)

    def register_model(self, model_cls: type[Any]) -> type[Any]:
        compile_model_schema(self.registry, model_cls)
        model_cls.bind_registry(self.registry)
        return model_cls

    def register_router(self, router: Any) -> Any:
        self.registry.register_router(router)
        return router

    def build(self, mode: str = "hybrid") -> Any:
        rest_app = RestAdapter(self.registry, self.engine).build_app()
        graphql_app = GraphQLAdapter(self.registry, self.engine).build_app()

        if mode == "rest":
            try:
                self._attach_lifecycle(rest_app)
            except Exception:
                pass
            return rest_app
        if mode == "graphql":
            try:
                self._attach_lifecycle(graphql_app)
            except Exception:
                pass
            return graphql_app
        if mode != "hybrid":
            raise ValueError("mode must be 'rest', 'graphql', or 'hybrid'")

        try:
            from starlette.applications import Starlette
            from starlette.routing import Mount, Route
            from starlette.responses import HTMLResponse, JSONResponse
        except ImportError as exc:  # pragma: no cover - optional dependency guard
            raise RuntimeError("Starlette is required to build a hybrid app") from exc

        from guaro.openapi.generator import generate_openapi
        from guaro.db.router import get_adapter
        import asyncio

        async def openapi_json_endpoint(request):
            return JSONResponse(generate_openapi(self.registry))

        async def docs_endpoint(request):
            html = """
<!doctype html>
<html>
  <head>
    <title>Guaro Swagger UI</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css" />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
    <script>
      const ui = SwaggerUIBundle({ url: '/openapi.json', dom_id: '#swagger-ui' });
    </script>
  </body>
</html>
"""
            return HTMLResponse(html)

        app = Starlette(routes=[
            Route("/openapi.json", endpoint=openapi_json_endpoint, methods=["GET"]),
            Route("/docs", endpoint=docs_endpoint, methods=["GET"]),
            Mount("/graphql", app=graphql_app),
            Mount("/", app=rest_app),
        ])
        try:
            self._attach_lifecycle(app)
        except Exception:
            pass
        return app

    def _attach_lifecycle(self, app: Any) -> None:
        """Attach startup/shutdown handlers to ensure adapters are connected."""

        async def _startup():
            adapter = get_adapter(self.registry)
            if hasattr(adapter, "connect"):
                try:
                    await adapter.connect()
                    logger.debug("[Guaro] Adapter connected on startup")
                except Exception as e:
                    logger.error(f"[Guaro] Failed to connect adapter on startup: {e}")
                    raise

        async def _shutdown():
            adapter = get_adapter(self.registry)
            if hasattr(adapter, "disconnect"):
                try:
                    await adapter.disconnect()
                    logger.debug("[Guaro] Adapter disconnected on shutdown")
                except Exception as e:
                    logger.error(f"[Guaro] Failed to disconnect adapter on shutdown: {e}")
                    raise

        # Starlette/ASGI apps expose add_event_handler
        try:
            app.add_event_handler("startup", _startup)
            app.add_event_handler("shutdown", _shutdown)
        except AttributeError as e:
            # Some app types (e.g., GraphQL middleware) may not support event handlers
            logger.debug(f"[Guaro] App does not support event handlers: {e}")
        except Exception as e:
            logger.warning(f"[Guaro] Unexpected error attaching lifecycle handlers: {e}")

    def run(self, mode: str = "hybrid", host: str = "127.0.0.1", port: int = 8000) -> Any:
        app = self.build(mode=mode)
        try:
            import uvicorn
        except ImportError:
            return app

        uvicorn.run(app, host=host, port=port)
        return app
