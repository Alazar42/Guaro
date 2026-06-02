from __future__ import annotations

from urllib.parse import quote_plus
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


def _coerce_engine(engine: Any) -> DatabaseEngine:
    if isinstance(engine, DatabaseEngine):
        return engine
    if isinstance(engine, str):
        try:
            return DatabaseEngine(engine.lower())
        except ValueError as exc:
            raise ValueError(f"Unknown engine: {engine}") from exc
    raise ValueError(f"engine must be DatabaseEngine or string; got {type(engine)}")


def _build_url_from_parts(config: dict[str, Any], engine: DatabaseEngine) -> str:
    """Build a DB URL from host credentials when `url` is not provided."""
    host = config.get("host")
    database = config.get("database_name") or config.get("database") or config.get("db")
    user = config.get("user") or config.get("username")
    password = config.get("password")
    port = config.get("port")

    if engine == DatabaseEngine.MEMORY:
        return "memory://"

    if engine == DatabaseEngine.SQLITE:
        # For sqlite, allow a file path via database_name/database
        db_file = database or "guaro.db"
        return f"sqlite+aiosqlite:///{db_file}"

    if engine == DatabaseEngine.MONGODB:
        if not host:
            raise ValueError("MongoDB config requires 'host' when 'url' is missing")
        auth = ""
        if user:
            encoded_user = quote_plus(str(user))
            encoded_password = quote_plus(str(password or ""))
            auth = f"{encoded_user}:{encoded_password}@"
        host_port = f"{host}:{port}" if port else str(host)
        db_segment = f"/{database}" if database else ""
        return f"mongodb://{auth}{host_port}{db_segment}"

    # SQL engines
    if engine == DatabaseEngine.POSTGRESQL:
        driver = "postgresql+asyncpg"
        default_port = 5432
    elif engine == DatabaseEngine.MYSQL:
        driver = "mysql+aiomysql"
        default_port = 3306
    else:
        raise ValueError(f"Unsupported engine for URL construction: {engine}")

    missing = [
        key
        for key, value in {
            "host": host,
            "database_name|database": database,
            "user|username": user,
            "password": password,
        }.items()
        if not value
    ]
    if missing:
        raise ValueError(
            "Database config missing required fields when 'url' is omitted: " + ", ".join(missing)
        )

    encoded_user = quote_plus(str(user))
    encoded_password = quote_plus(str(password))
    host_port = f"{host}:{port or default_port}"
    return f"{driver}://{encoded_user}:{encoded_password}@{host_port}/{database}"


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

        # Determine engine: explicit > inferred from URL > default memory fallback
        if "engine" in config and config.get("engine") is not None:
            engine = _coerce_engine(config.get("engine"))
        elif url:
            engine = _infer_engine_from_url(url)
        else:
            engine = DatabaseEngine.MEMORY

        # Build URL from host-based fields when URL is missing
        if not url:
            url = _build_url_from_parts(config, engine)

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
