from __future__ import annotations

from typing import Any


def _walk_field_nodes(nodes: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    for node in nodes or []:
        name = getattr(node, "name", None) or getattr(node, "field_name", None)
        if name is None or str(name).startswith("__"):
            continue
        path = f"{prefix}.{name}" if prefix else str(name)
        paths.append(path)
        child_nodes = getattr(node, "selections", None)
        if child_nodes is None:
            selection_set = getattr(node, "selection_set", None)
            child_nodes = getattr(selection_set, "selections", None) if selection_set is not None else None
        paths.extend(_walk_field_nodes(child_nodes, path))
    return paths


def extract_selected_fields(info: Any) -> list[str]:
    if info is None:
        return []
    selected = getattr(info, "selected_fields", None)
    if selected:
        return _walk_field_nodes(selected)
    field_nodes = getattr(info, "field_nodes", None)
    if field_nodes:
        return _walk_field_nodes(field_nodes)
    return []
