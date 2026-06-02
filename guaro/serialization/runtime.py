from __future__ import annotations

from typing import Any

from guaro.core.registry import ModelMetadata, Registry
from guaro.execution.context import ExecutionContext
from guaro.execution.planner import QueryPlan, build_field_tree


async def serialize_model(instance: Any, plan: QueryPlan | None, context: ExecutionContext, registry: Registry) -> Any:
    if instance is None:
        return None
    model_metadata = registry.get_model_metadata(instance.__class__)
    serializer = registry.compiled_serializers.get(model_metadata.name)
    if serializer is None:
        from guaro.serialization.compiler import compile_serializer

        serializer = compile_serializer(registry, model_metadata)
    effective_plan = plan or QueryPlan(entity=model_metadata.name, fields=set(model_metadata.fields.keys()), field_tree=build_field_tree(model_metadata.fields.keys()))
    return await serializer.serialize(instance, context, effective_plan)


async def serialize_many(values: list[Any], plan: QueryPlan | None, context: ExecutionContext, registry: Registry, metadata: ModelMetadata | None = None) -> Any:
    if not values:
        return []
    model_metadata = metadata or registry.get_model_metadata(values[0].__class__)
    serializer = registry.compiled_serializers.get(model_metadata.name)
    if serializer is None:
        from guaro.serialization.compiler import compile_serializer

        serializer = compile_serializer(registry, model_metadata)
    effective_plan = plan or QueryPlan(entity=model_metadata.name, fields=set(model_metadata.fields.keys()), field_tree=build_field_tree(model_metadata.fields.keys()))
    return await serializer.serialize(values, context, effective_plan)
