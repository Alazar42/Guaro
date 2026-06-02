"""
Guaro: Unified REST + GraphQL API framework

Simple, fast, and async-first framework for building modern APIs with
automatic schema migration, multi-database support, and built-in REST + GraphQL.
"""

__version__ = "0.1.0"

from guaro.app import API
from guaro.config import DatabaseEngine, normalize_database_config
from guaro.core.registry import Registry
from guaro.execution.context import ExecutionContext
from guaro.middleware.auth import require_auth
from guaro.middleware.permissions import permission
from guaro.models.base import Model
from guaro.routing.router import Router

__all__ = [
    "__version__",
    "API",
    "DatabaseEngine",
    "ExecutionContext",
    "Model",
    "Registry",
    "Router",
    "normalize_database_config",
    "permission",
    "require_auth",
]
