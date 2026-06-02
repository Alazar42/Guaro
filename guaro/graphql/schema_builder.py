from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, get_args, get_origin

from guaro.core.registry import Registry
from guaro.execution.context import ExecutionContext
from guaro.execution.planner import build_field_tree, normalize_field_selection
from guaro.loaders.relation_loader import clone_request_loaders


def _graphql_scalar(annotation: Any) -> Any:
    try:
        import strawberry
    except ImportError as exc:  # pragma: no cover - optional dependency guard
        raise RuntimeError("strawberry-graphql is required for GraphQL support") from exc

    mapping = {int: int, str: str, float: float, bool: bool}
    return mapping.get(annotation, strawberry.scalars.JSON)


def _unwrap_optional(annotation: Any) -> tuple[Any, bool]:
    origin = get_origin(annotation)
    args = get_args(annotation)
    union_type = getattr(__import__("types"), "UnionType", object())
    if origin is union_type or origin is getattr(__import__("typing"), "Union", object()):
        non_none = [arg for arg in args if arg is not type(None)]
        if len(non_none) == 1 and len(non_none) != len(args):
            return non_none[0], True
    return annotation, False


def _build_field_type(annotation: Any, registry: Registry, cache: dict[str, Any]) -> Any:
    annotation, optional = _unwrap_optional(annotation)
    origin = get_origin(annotation)
    if origin is list:
        args = get_args(annotation)
        item_type = _build_field_type(args[0], registry, cache) if args else Any
        result = list[item_type]
        return result if not optional else result | None
    if isinstance(annotation, type) and annotation.__name__ in registry.models:
        resolved = cache[annotation.__name__]
        return resolved if not optional else resolved | None
    resolved = _graphql_scalar(annotation)
    return resolved if not optional else resolved | None


def _build_return_type(route: Any, registry: Registry, cache: dict[str, Any]) -> Any:
    import strawberry

    return_annotation = route.return_type
    if return_annotation is Any or return_annotation is None:
        return strawberry.scalars.JSON

    origin = get_origin(return_annotation)
    if origin is list:
        args = get_args(return_annotation)
        item_annotation = args[0] if args else Any
        if isinstance(item_annotation, type) and item_annotation.__name__ in registry.models:
            return list[cache[item_annotation.__name__]]
        return list[_graphql_scalar(item_annotation)]

    return_annotation, optional = _unwrap_optional(return_annotation)
    if isinstance(return_annotation, type) and return_annotation.__name__ in registry.models:
        resolved = cache[return_annotation.__name__]
    else:
        resolved = _graphql_scalar(return_annotation)
    return resolved if not optional else resolved | None


@dataclass
class GraphQLSchemaBundle:
    schema: Any
    types: dict[str, Any]


def build_schema(registry: Registry) -> GraphQLSchemaBundle:
    try:
        import strawberry
    except ImportError as exc:  # pragma: no cover - optional dependency guard
        raise RuntimeError("strawberry-graphql is required for GraphQL support") from exc

    type_cache: dict[str, Any] = {}
    for model_metadata in registry.models.values():
        namespace: dict[str, Any] = {"__annotations__": {}}
        model_type = dataclass(type(f"{model_metadata.name}Type", (), namespace))
        type_cache[model_metadata.name] = model_type

    for model_metadata in registry.models.values():
        annotations: dict[str, Any] = {}
        for field_name, field_meta in model_metadata.fields.items():
            annotations[field_name] = _build_field_type(field_meta.annotation, registry, type_cache)
        type_cache[model_metadata.name].__annotations__ = annotations

    for model_name, model_type in list(type_cache.items()):
        type_cache[model_name] = strawberry.type(model_type)

    query_fields: dict[str, Any] = {}
    mutation_fields: dict[str, Any] = {}

    for route in registry.routes:
        return_annotation = _build_return_type(route, registry, type_cache)
        resolver = _build_route_resolver(route, registry, return_annotation)

        if route.method == "GET":
            query_fields[route.name] = strawberry.field(resolver=resolver)
        else:
            mutation_fields[route.name] = strawberry.field(resolver=resolver)

    Query = type("Query", (), query_fields) if query_fields else type("Query", (), {})
    Mutation = type("Mutation", (), mutation_fields) if mutation_fields else None
    schema = strawberry.Schema(query=strawberry.type(Query), mutation=strawberry.type(Mutation) if Mutation else None)
    return GraphQLSchemaBundle(schema=schema, types=type_cache)


def _build_route_resolver(route: Any, registry: Registry, return_annotation: Any):
    async def resolver(*args: Any, **kwargs: Any) -> Any:
        from guaro.core.execution_engine import ExecutionEngine
        from guaro.graphql.selection import extract_selected_fields

        context_value = kwargs.pop("context", None)
        info = kwargs.pop("info", None)
        selected_fields = normalize_field_selection(extract_selected_fields(info))
        engine = ExecutionEngine(registry)
        context = ExecutionContext(
            request=getattr(context_value, "request", context_value),
            response=None,
            selected_fields=set(selected_fields),
            field_tree=build_field_tree(selected_fields),
            loaders=clone_request_loaders(registry.loaders),
            transport="graphql",
            user=getattr(context_value, "user", None),
            permissions=set(getattr(context_value, "permissions", set())),
            params=kwargs,
        )
        result = await engine.execute(route, context=context, kwargs=kwargs)
        return result.data

    try:
        from strawberry.types import Info
    except ImportError:  # pragma: no cover - strawberry is required by the adapter
        Info = Any

    route_signature = inspect.signature(route.resolver)
    parameters: list[inspect.Parameter] = [
        inspect.Parameter("info", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Info)
    ]
    for parameter in route_signature.parameters.values():
        if parameter.kind in {inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
            continue
        if parameter.name in {"self", "cls", "context", "request", "info"}:
            continue
        annotation = parameter.annotation if parameter.annotation is not inspect._empty else Any
        parameters.append(
            inspect.Parameter(
                parameter.name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=parameter.default,
                annotation=annotation,
            )
        )

    resolver.__signature__ = inspect.Signature(parameters=parameters, return_annotation=return_annotation)
    resolver.__annotations__["return"] = return_annotation
    return resolver
