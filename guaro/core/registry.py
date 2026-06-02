from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


MiddlewareCallable = Callable[..., Any]
PermissionCallable = Callable[..., Any]


@dataclass(slots=True)
class FieldMetadata:
    name: str
    annotation: Any
    optional: bool = False
    list_of: Any | None = None
    relationship: bool = False
    default: Any = None


@dataclass(slots=True)
class ModelMetadata:
    name: str
    model_cls: type[Any]
    fields: dict[str, FieldMetadata] = field(default_factory=dict)
    primary_key: str = "id"


@dataclass(slots=True)
class RouteMetadata:
    method: str
    path: str
    resolver: Callable[..., Any]
    name: str
    resolver_name: str
    permissions: list[str] = field(default_factory=list)
    middleware: list[MiddlewareCallable] = field(default_factory=list)
    return_type: Any = Any
    model_name: str | None = None
    is_mutation: bool = False


@dataclass(slots=True)
class RequestContext:
    request: Any | None = None
    selected_fields: list[str] | None = None
    field_tree: dict[str, Any] = field(default_factory=dict)
    cache: dict[str, Any] = field(default_factory=dict)
    loaders: dict[str, Any] = field(default_factory=dict)


@dataclass
class Registry:
    models: dict[str, ModelMetadata] = field(default_factory=dict)
    routes: list[RouteMetadata] = field(default_factory=list)
    middleware: list[MiddlewareCallable] = field(default_factory=list)
    permissions: list[PermissionCallable] = field(default_factory=list)
    serializers: dict[str, Any] = field(default_factory=dict)
    compiled_serializers: dict[str, Any] = field(default_factory=dict)
    graphql: dict[str, Any] = field(default_factory=dict)
    loaders: dict[str, Any] = field(default_factory=dict)
    dependencies: dict[str, Any] = field(default_factory=dict)
    model_name_map: dict[type[Any], str] = field(default_factory=dict)
    db_config: Any = None  # NormalizedDatabaseConfig set by API at initialization

    def register_model_metadata(self, metadata: ModelMetadata) -> None:
        self.models[metadata.name] = metadata
        self.model_name_map[metadata.model_cls] = metadata.name

    def get_model_metadata(self, model_cls: type[Any] | str) -> ModelMetadata:
        if isinstance(model_cls, str):
            return self.models[model_cls]
        return self.models[self.model_name_map[model_cls]]

    def register_route(self, metadata: RouteMetadata) -> None:
        self.routes.append(metadata)

    def register_router(self, router: Any) -> None:
        for route in router.routes:
            self.register_route(route)

    def register_loader(self, name: str, loader: Any) -> None:
        self.loaders[name] = loader

    def register_compiled_serializer(self, model_name: str, serializer: Any) -> None:
        self.compiled_serializers[model_name] = serializer

    def register_dependency(self, name: str, provider: Any) -> None:
        self.dependencies[name] = provider
