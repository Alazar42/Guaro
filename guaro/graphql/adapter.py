from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from guaro.core.execution_engine import ExecutionEngine
from guaro.core.registry import Registry
from guaro.graphql.schema_builder import build_schema


@dataclass
class GraphQLAdapter:
    registry: Registry
    engine: ExecutionEngine

    def build_app(self) -> Any:
        try:
            from strawberry.asgi import GraphQL
        except ImportError as exc:  # pragma: no cover - optional dependency guard
            raise RuntimeError("strawberry-graphql is required for GraphQL support") from exc

        schema = build_schema(self.registry).schema
        return GraphQL(schema)
