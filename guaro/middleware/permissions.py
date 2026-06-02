from __future__ import annotations

from functools import wraps
from typing import Any, Callable


def permission(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        permissions = list(getattr(func, "__guaro_permissions__", []))
        permissions.append(name)
        setattr(wrapper, "__guaro_permissions__", permissions)
        setattr(wrapper, "__guaro_permission_name__", name)
        return wrapper

    return decorator
