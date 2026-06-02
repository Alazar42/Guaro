from __future__ import annotations

from typing import Any, get_args, get_origin


def coerce_value(annotation: Any, value: Any) -> Any:
    origin = get_origin(annotation)
    if value is None:
        return None
    if origin is list:
        inner = get_args(annotation)[0] if get_args(annotation) else Any
        return [coerce_value(inner, item) for item in value]
    if annotation in {int, str, float, bool}:
        return annotation(value)
    return value
