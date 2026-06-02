from __future__ import annotations

from typing import Any

from guaro.config.schema import DatabaseEngine, NormalizedDatabaseConfig


def _infer_engine_from_url(url: str) -> DatabaseEngine:
    """Infer database engine from URL scheme if possible.

    Examples:
        sqlite:/// → SQLITE
        postgresql:// → POSTGRESQL
        mysql:// → MYSQL
        mongodb:// → MONGODB
    """
    if not url or not isinstance(url, str):
        return DatabaseEngine.SQLITE

    scheme = url.split("://")[0].lower() if "://" in url else url.lower()
    scheme = scheme.split("+")[0]  # handle sqlite+aiosqlite

    engine_map = {
        "sqlite": DatabaseEngine.SQLITE,
        "postgresql": DatabaseEngine.POSTGRESQL,
        "postgres": DatabaseEngine.POSTGRESQL,
        "mysql": DatabaseEngine.MYSQL,
        "mongodb": DatabaseEngine.MONGODB,
        "mongo": DatabaseEngine.MONGODB,
        "memory": DatabaseEngine.MEMORY,
    }

    return engine_map.get(scheme, DatabaseEngine.SQLITE)


def normalize_database_config(config: Any | None = None) -> NormalizedDatabaseConfig:
    """Normalize database configuration from various input formats.

    Supports:
        - None (uses default SQLite)
        - dict (with url, engine, etc.)
        - NormalizedDatabaseConfig (pass-through)
        - string (treated as URL)

    Args:
        config: Configuration in any supported format

    Returns:
        NormalizedDatabaseConfig: Unified internal config

    Raises:
        ValueError: If config is invalid or required fields are missing
    """
    # Default: SQLite in-memory or file
    if config is None:
        return NormalizedDatabaseConfig(
            url="sqlite+aiosqlite:///guaro.db",
            engine=DatabaseEngine.SQLITE,
            auto_migrate=True,
            pool_size=1,
        )

    # Pass-through if already normalized
    if isinstance(config, NormalizedDatabaseConfig):
        return config

    # String URL
    if isinstance(config, str):
        engine = _infer_engine_from_url(config)
        return NormalizedDatabaseConfig(
            url=config,
            engine=engine,
            auto_migrate=True,
            pool_size=5,
        )

    # Dictionary
    if isinstance(config, dict):
        url = config.get("url")
        if not url:
            raise ValueError("Database config dict must include 'url' field")

        # Determine engine: explicit > inferred from URL
        if "engine" in config:
            engine = config["engine"]
            if isinstance(engine, str):
                try:
                    engine = DatabaseEngine(engine)
                except ValueError:
                    raise ValueError(f"Unknown engine: {engine}")
            elif not isinstance(engine, DatabaseEngine):
                raise ValueError(f"engine must be DatabaseEngine or string; got {type(engine)}")
        else:
            engine = _infer_engine_from_url(url)

        return NormalizedDatabaseConfig(
            url=url,
            engine=engine,
            auto_migrate=config.get("auto_migrate", True),
            pool_size=config.get("pool_size", 5),
            pool_pre_ping=config.get("pool_pre_ping", True),
            echo=config.get("echo", False),
            timeout=config.get("timeout", 30),
            extra=config.get("extra"),
        )

    raise ValueError(
        f"Invalid database config type {type(config).__name__}. "
        f"Expected dict, str, NormalizedDatabaseConfig, or None."
    )
