from __future__ import annotations

from functools import wraps
from typing import Any, Callable


def auth_middleware(context: Any, *, route: Any) -> None:
    if getattr(context, "user", None) is None:
        raise PermissionError(f"Authentication required for {route.method} {route.path}")


def require_auth(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    middleware = list(getattr(func, "__guaro_middleware__", []))
    middleware.append(auth_middleware)
    setattr(wrapper, "__guaro_middleware__", middleware)
    setattr(wrapper, "__guaro_requires_auth__", True)
    return wrapper

