from __future__ import annotations

from functools import wraps
from typing import Any, Callable


def auth_middleware(context: Any, *, route: Any) -> None:
    # Permissions are disabled for now — no-op middleware.
    return None


def require_auth(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    middleware = list(getattr(func, "__guaro_middleware__", []))
    middleware.append(auth_middleware)
    setattr(wrapper, "__guaro_middleware__", middleware)
    # Do not mark the resolver as requiring auth while permissions are disabled
    setattr(wrapper, "__guaro_requires_auth__", False)
    return wrapper

