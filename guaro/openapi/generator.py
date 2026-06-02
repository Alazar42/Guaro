from __future__ import annotations

import inspect
from typing import Any

from starlette.responses import JSONResponse

from guaro.core.registry import Registry
from guaro.core.schema import PRIMITIVES


PRIMITIVE_MAP = {
    int: ("integer", "int32"),
    float: ("number", "float"),
    str: ("string", None),
    bool: ("boolean", None),
    dict: ("object", None),
    list: ("array", None),
}


def _schema_for_annotation(annotation: Any, registry: Registry, components: dict) -> Any:
    # Handle optional / list by inspecting annotation types from registry metadata usage
    # If annotation is a registered model name or class, reference the component
    if isinstance(annotation, str):
        model_name = annotation
        if model_name in registry.models:
            return {"$ref": f"#/components/schemas/{model_name}"}
        return {"type": "object"}

    # model classes are registered in registry.model_name_map
    if hasattr(annotation, "__name__") and annotation.__name__ in registry.models:
        return {"$ref": f"#/components/schemas/{annotation.__name__}"}

    # primitives
    if annotation in PRIMITIVES or hasattr(annotation, "__origin__"):
        # handle simple primitives mapping
        if annotation in PRIMITIVE_MAP:
            t, fmt = PRIMITIVE_MAP[annotation]
            schema = {"type": t}
            if fmt:
                schema["format"] = fmt
            return schema
        # fallback
        return {"type": "object"}

    return {"type": "object"}


def _build_components(registry: Registry) -> dict:
    components: dict = {"schemas": {}}
    for name, metadata in registry.models.items():
        props: dict = {}
        required = []
        for fname, fmeta in metadata.fields.items():
            if fmeta.relationship and fmeta.list_of:
                # array of refs
                item = _schema_for_annotation(fmeta.list_of, registry, components)
                props[fname] = {"type": "array", "items": item}
            elif fmeta.relationship:
                props[fname] = _schema_for_annotation(fmeta.annotation, registry, components)
            else:
                props[fname] = _schema_for_annotation(fmeta.annotation, registry, components)
            if not fmeta.optional:
                required.append(fname)

        schema: dict = {"type": "object", "properties": props}
        if required:
            schema["required"] = required
        components["schemas"][name] = schema

    return components


def generate_openapi(registry: Registry, title: str = "Guaro API", version: str = "0.1.0") -> dict:
    openapi: dict = {
        "openapi": "3.0.0",
        "info": {"title": title, "version": version},
        "paths": {},
        "components": {},
    }

    openapi["components"] = _build_components(registry)

    for route in registry.routes:
        path = route.path
        if path not in openapi["paths"]:
            openapi["paths"][path] = {}

        method = route.method.lower()
        # build parameters from resolver signature
        parameters = []
        sig = inspect.signature(route.resolver)
        for name, param in sig.parameters.items():
            if name in {"self", "cls", "request"}:
                continue
            param_schema = {"name": name, "in": "path" if f"{{{name}}}" in path else "query", "required": True}
            annotation = param.annotation if param.annotation is not inspect._empty else None
            if annotation:
                param_schema["schema"] = _schema_for_annotation(annotation, registry, openapi["components"])
            else:
                param_schema["schema"] = {"type": "string"}

            # path params must be required
            if param_schema["in"] == "path":
                param_schema["required"] = True
            else:
                param_schema["required"] = not (param.default is not inspect._empty)

            parameters.append(param_schema)

        # simple responses
        responses = {"200": {"description": "Successful Response", "content": {"application/json": {"schema": {"type": "object"}}}}}

        openapi["paths"][path][method] = {
            "summary": route.name,
            "operationId": route.resolver_name,
            "parameters": parameters,
            "responses": responses,
        }

    return openapi
