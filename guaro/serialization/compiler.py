from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from guaro.core.registry import FieldMetadata, ModelMetadata, Registry
from guaro.execution.context import ExecutionContext
from guaro.execution.planner import QueryPlan, build_field_tree
from guaro.loaders.relation_loader import loader_key


async def _maybe_await(value: Any) -> Any:
    if hasattr(value, "__await__"):
        return await value
    return value


def _resolve_model_name(field_meta: FieldMetadata) -> str | None:
    candidate = field_meta.list_of or field_meta.annotation
    if isinstance(candidate, str):
        return candidate
    if isinstance(candidate, type):
        return candidate.__name__
    return None


@dataclass(slots=True)
class CompiledSerializer:
    model_name: str
    registry: Registry
    metadata: ModelMetadata

    async def serialize(self, value: Any, context: ExecutionContext, plan: QueryPlan, field_tree: dict[str, Any] | None = None) -> Any:
        if value is None:
            return None
        tree = field_tree or plan.field_tree or build_field_tree(self.metadata.fields.keys())
        if isinstance(value, list):
            return await self._serialize_many(value, context, plan, tree)
        return await self._serialize_one(value, context, plan, tree)

    async def _serialize_many(self, values: list[Any], context: ExecutionContext, plan: QueryPlan, field_tree: dict[str, Any]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = [{} for _ in values]
        scalar_fields: list[tuple[str, FieldMetadata]] = []
        relation_fields: list[tuple[str, FieldMetadata, dict[str, Any]]] = []

        for field_name, subtree in field_tree.items():
            field_meta = self.metadata.fields.get(field_name)
            if field_meta is None:
                continue
            if field_meta.relationship:
                relation_fields.append((field_name, field_meta, subtree))
            else:
                scalar_fields.append((field_name, field_meta))

        for row, value in zip(rows, values):
            for field_name, _ in scalar_fields:
                row[field_name] = getattr(value, field_name, None)

        for field_name, field_meta, subtree in relation_fields:
            await self._serialize_relation_many(values, rows, field_name, field_meta, subtree, context, plan)

        return rows

    async def _serialize_one(self, value: Any, context: ExecutionContext, plan: QueryPlan, field_tree: dict[str, Any]) -> dict[str, Any]:
        row: dict[str, Any] = {}
        for field_name, subtree in field_tree.items():
            field_meta = self.metadata.fields.get(field_name)
            if field_meta is None:
                continue
            field_value = getattr(value, field_name, None)
            if field_meta.relationship:
                row[field_name] = await self._serialize_relation_one(value, field_meta, field_value, subtree, context, plan)
            else:
                row[field_name] = field_value
        return row

    async def _serialize_relation_many(self, parents: list[Any], rows: list[dict[str, Any]], field_name: str, field_meta: FieldMetadata, subtree: dict[str, Any], context: ExecutionContext, plan: QueryPlan) -> None:
        parent_ids = [getattr(parent, self.metadata.primary_key, None) for parent in parents]
        loader = context.loaders.get(loader_key(self.model_name, field_name))
        batch_map: dict[Any, Any] | None = None

        if loader is not None and hasattr(loader, "load_many"):
            batch_map = await _maybe_await(loader.load_many(parent_ids))

        for index, parent in enumerate(parents):
            value = batch_map.get(parent_ids[index]) if batch_map is not None else getattr(parent, field_name, None)
            rows[index][field_name] = await self._serialize_loaded_value(field_meta, value, subtree, context, plan)

    async def _serialize_relation_one(self, parent: Any, field_meta: FieldMetadata, value: Any, subtree: dict[str, Any], context: ExecutionContext, plan: QueryPlan) -> Any:
        if value is None:
            loader = context.loaders.get(loader_key(self.model_name, field_meta.name))
            if loader is not None and hasattr(loader, "load_one"):
                value = await _maybe_await(loader.load_one(getattr(parent, self.metadata.primary_key, None)))
        return await self._serialize_loaded_value(field_meta, value, subtree, context, plan)

    async def _serialize_loaded_value(self, field_meta: FieldMetadata, value: Any, subtree: dict[str, Any], context: ExecutionContext, plan: QueryPlan) -> Any:
        if value is None:
            return None

        child_model_name = _resolve_model_name(field_meta)
        if child_model_name is None:
            return value

        child_serializer = self.registry.compiled_serializers.get(child_model_name)
        if child_serializer is None:
            from guaro.serialization.compiler import compile_serializer

            child_metadata = self.registry.models.get(child_model_name)
            if child_metadata is None:
                return value
            child_serializer = compile_serializer(self.registry, child_metadata)

        return await child_serializer.serialize(value, context, plan, subtree)


def compile_serializer(registry: Registry, metadata: ModelMetadata) -> CompiledSerializer:
    serializer = CompiledSerializer(model_name=metadata.name, registry=registry, metadata=metadata)
    registry.register_compiled_serializer(metadata.name, serializer)
    return serializer
