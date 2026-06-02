from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


@dataclass(slots=True)
class QueryPlan:
    entity: str
    fields: set[str] = field(default_factory=set)
    field_tree: dict[str, Any] = field(default_factory=dict)
    relations: set[str] = field(default_factory=set)
    transport: str = "internal"


def normalize_field_selection(selected_fields: Iterable[str] | None) -> list[str]:
    if not selected_fields:
        return []
    normalized: list[str] = []
    for field_name in selected_fields:
        candidate = str(field_name).strip()
        if candidate and candidate not in normalized:
            normalized.append(candidate)
    return normalized


def build_field_tree(selected_fields: Iterable[str] | None) -> dict[str, Any]:
    tree: dict[str, Any] = {}
    for path in normalize_field_selection(selected_fields):
        cursor = tree
        for part in path.split("."):
            cursor = cursor.setdefault(part, {})
    return tree


def build_query_plan(entity: str, selected_fields: Iterable[str] | None, transport: str = "internal") -> QueryPlan:
    normalized = normalize_field_selection(selected_fields)
    field_tree = build_field_tree(normalized)
    relations = {field_name.split(".", 1)[0] for field_name in normalized if "." in field_name}
    return QueryPlan(entity=entity, fields=set(normalized), field_tree=field_tree, relations=relations, transport=transport)
