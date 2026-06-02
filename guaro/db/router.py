from __future__ import annotations

from typing import Any

from guaro.config.schema import DatabaseEngine


def get_adapter(registry: Any) -> Any:
    """Return a cached adapter instance for the registry, creating it if needed.

    The adapter is stored in `registry.dependencies['db_adapter']` so it's
    reused across the app. This function does not connect the adapter; the
    API is responsible for calling `connect()` at startup and `disconnect()` at
    shutdown for adapters that require it.
    """
    deps = registry.dependencies
    if "db_adapter" in deps:
        return deps["db_adapter"]

    cfg = getattr(registry, "db_config", None)
    engine = getattr(cfg, "engine", None)

    # Lazy import adapters to avoid optional dependency errors at module import
    if engine is None or engine == DatabaseEngine.MEMORY:
        from guaro.db.adapters.memory_adapter import MemoryAdapter

        adapter = MemoryAdapter(registry)
    elif engine in (DatabaseEngine.SQLITE, DatabaseEngine.POSTGRESQL, DatabaseEngine.MYSQL):
        from guaro.db.adapters.sql_adapter import SQLAdapter

        adapter = SQLAdapter(registry, cfg.url)
    elif engine == DatabaseEngine.MONGODB:
        from guaro.db.adapters.mongo_adapter import MongoAdapter

        adapter = MongoAdapter(registry, cfg.url)
    else:
        raise RuntimeError(f"Unsupported database engine: {engine}")

    deps["db_adapter"] = adapter
    return adapter
