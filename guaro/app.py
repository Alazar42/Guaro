from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from guaro.core.execution_engine import ExecutionEngine
from guaro.core.registry import Registry
from guaro.core.schema import compile_model_schema
from guaro.graphql.adapter import GraphQLAdapter
from guaro.rest.adapter import RestAdapter


@dataclass(slots=True)
class API:
    registry: Registry = field(default_factory=Registry)
    engine: ExecutionEngine = field(init=False)

    def __post_init__(self) -> None:
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
            return rest_app
        if mode == "graphql":
            return graphql_app
        if mode != "hybrid":
            raise ValueError("mode must be 'rest', 'graphql', or 'hybrid'")

        try:
            from starlette.applications import Starlette
            from starlette.routing import Mount
        except ImportError as exc:  # pragma: no cover - optional dependency guard
            raise RuntimeError("Starlette is required to build a hybrid app") from exc

        return Starlette(routes=[Mount("/graphql", app=graphql_app), Mount("/", app=rest_app)])

    def run(self, mode: str = "hybrid", host: str = "127.0.0.1", port: int = 8000) -> Any:
        app = self.build(mode=mode)
        try:
            import uvicorn
        except ImportError:
            return app

        uvicorn.run(app, host=host, port=port)
        return app
