from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class DatabaseEngine(str, Enum):
    """Supported database engines for Guaro."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    MEMORY = "memory"


@dataclass(frozen=True, slots=True)
class NormalizedDatabaseConfig:
    """Unified internal database configuration after normalization.

    This is the canonical config format used internally by Guaro adapters, repositories, and engines.
    All external config formats (dict, module imports, Pydantic, dataclass, YAML, JSON) are
    normalized into this structure at startup and cached.
    """

    url: str
    engine: DatabaseEngine
    auto_migrate: bool = True
    pool_size: int = 5
    pool_pre_ping: bool = True
    echo: bool = False
    timeout: int = 30
    extra: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        # Validate URL is not empty
        if not self.url or not isinstance(self.url, str):
            raise ValueError("Database URL must be a non-empty string")
        # Validate engine is a valid DatabaseEngine
        if not isinstance(self.engine, DatabaseEngine):
            raise ValueError(f"Database engine must be a DatabaseEngine; got {type(self.engine)}")
        # Validate pool size
        if self.pool_size < 1:
            raise ValueError("pool_size must be >= 1")
        # Validate timeout
        if self.timeout < 0:
            raise ValueError("timeout must be >= 0")

    def to_dict(self) -> dict[str, Any]:
        """Export config as dictionary for adapter use."""
        return {
            "url": self.url,
            "engine": self.engine.value,
            "auto_migrate": self.auto_migrate,
            "pool_size": self.pool_size,
            "pool_pre_ping": self.pool_pre_ping,
            "echo": self.echo,
            "timeout": self.timeout,
            "extra": self.extra or {},
        }
