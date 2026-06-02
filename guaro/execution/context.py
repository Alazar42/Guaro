from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExecutionContext:
    request: Any | None = None
    response: Any | None = None
    selected_fields: set[str] = field(default_factory=set)
    field_tree: dict[str, Any] = field(default_factory=dict)
    loaders: dict[str, Any] = field(default_factory=dict)
    cache: dict[str, Any] = field(default_factory=dict)
    user: Any | None = None
    permissions: set[str] = field(default_factory=set)
    transport: str = "internal"
    params: dict[str, Any] = field(default_factory=dict)
    route: Any | None = None
    operation: str | None = None
    plan: Any | None = None
    errors: list[Exception] = field(default_factory=list)
