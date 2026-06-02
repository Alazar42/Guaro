from __future__ import annotations

from typing import Any, get_args, get_origin

from guaro.core.registry import FieldMetadata, ModelMetadata, Registry


PRIMITIVES = {int, str, float, bool, dict, list}


def _unwrap_optional(annotation: Any) -> tuple[Any, bool]:
    origin = get_origin(annotation)
    args = get_args(annotation)
    union_type = getattr(__import__("types"), "UnionType", object())
    if origin is union_type or origin is getattr(__import__("typing"), "Union", object()):
        non_none = [arg for arg in args if arg is not type(None)]
        if len(non_none) == 1 and len(non_none) != len(args):
            return non_none[0], True
    return annotation, False


def _unwrap_list(annotation: Any) -> Any | None:
    origin = get_origin(annotation)
    if origin is list:
        args = get_args(annotation)
        return args[0] if args else Any
    return None


def _resolve_forward_reference(annotation: Any, registry: Registry) -> Any:
    if isinstance(annotation, str):
        for metadata in registry.models.values():
            if metadata.name == annotation or metadata.model_cls.__name__ == annotation:
                return metadata.model_cls
        return annotation
    return annotation


def _resolve_relationship(annotation: Any, registry: Registry) -> tuple[Any, bool, Any | None]:
    optional_annotation, optional = _unwrap_optional(annotation)
    list_item = _unwrap_list(optional_annotation)
    if list_item is not None:
        list_item = _resolve_forward_reference(list_item, registry)
        return list[list_item], optional, list_item
    resolved = _resolve_forward_reference(optional_annotation, registry)
    return resolved, optional, resolved if hasattr(resolved, "__guaro_model__") else None


def compile_model_schema(registry: Registry, model_cls: type[Any]) -> ModelMetadata:
    fields: dict[str, FieldMetadata] = {}

    raw_annotations = dict(getattr(model_cls, "__annotations__", {}))
    for name, annotation in raw_annotations.items():
        resolved, optional, list_item = _resolve_relationship(annotation, registry)
        relationship = not (resolved in PRIMITIVES or isinstance(resolved, type) and resolved.__module__ == "builtins")
        fields[name] = FieldMetadata(
            name=name,
            annotation=resolved,
            optional=optional,
            list_of=list_item,
            relationship=relationship,
        )

    metadata = ModelMetadata(name=model_cls.__name__, model_cls=model_cls, fields=fields)
    registry.register_model_metadata(metadata)
    setattr(model_cls, "__guaro_model__", metadata)
    return metadata
