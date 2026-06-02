from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, get_args, get_origin, get_type_hints

from guaro.core.registry import RouteMetadata


def _singularize(name: str) -> str:
    return name[:-1] if name.endswith("s") and len(name) > 1 else name


def _camel_case(name: str) -> str:
    parts = [part for part in name.replace("-", "_").split("_") if part]
    return "".join(part[:1].upper() + part[1:] for part in parts)


def _derive_operation_name(method: str, path: str) -> str:
    resource = path.strip("/").split("/", 1)[0] or "root"
    resource = resource.split("{")[0].strip() or "root"
    singular = _singularize(resource)
    if method == "GET":
        return singular if "{" in path else resource
    if method == "POST":
        return f"create{_camel_case(singular)}"
    if method == "PUT":
        return f"update{_camel_case(singular)}"
    if method == "DELETE":
        return f"delete{_camel_case(singular)}"
    return f"{method.lower()}{_camel_case(resource)}"


@dataclass(slots=True)
class RouteDefinition:
    method: str
    path: str
    resolver: Callable[..., Any]
    permissions: list[str] = field(default_factory=list)
    middleware: list[Callable[..., Any]] = field(default_factory=list)

    def _infer_model_name(self, return_type: Any) -> str | None:
        if isinstance(return_type, str):
            return return_type
        origin = get_origin(return_type)
        if origin is not None:
            args = get_args(return_type)
            union_type = getattr(__import__("types"), "UnionType", object())
            if origin is union_type or origin is getattr(__import__("typing"), "Union", object()):
                non_none_args = [arg for arg in args if arg is not type(None)]
                if len(non_none_args) == 1:
                    return self._infer_model_name(non_none_args[0])
        if origin is list:
            args = get_args(return_type)
            return self._infer_model_name(args[0]) if args else None
        if hasattr(return_type, "__name__"):
            return return_type.__name__
        return None

    @property
    def metadata(self) -> RouteMetadata:
        hints = get_type_hints(self.resolver)
        return_type = hints.get("return", Any)
        model_name = self._infer_model_name(return_type)
        return RouteMetadata(
            method=self.method,
            path=self.path,
            resolver=self.resolver,
            name=_derive_operation_name(self.method, self.path),
            resolver_name=self.resolver.__name__,
            permissions=list(self.permissions),
            middleware=list(self.middleware),
            return_type=return_type,
            model_name=model_name,
            is_mutation=self.method in {"POST", "PUT", "DELETE"},
        )
