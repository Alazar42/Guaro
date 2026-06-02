"""Database migration system for schema management without data loss."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Set
from datetime import datetime

logger = logging.getLogger("guaro.migrations")


class Migration:
    """Represents a single database migration."""

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "timestamp": self.timestamp,
        }


class MigrationTracker:
    """Tracks which migrations have been applied to prevent re-running them."""

    def __init__(self, registry: Any):
        self.registry = registry
        self.applied: Set[str] = set()

    async def get_applied_migrations(self) -> Set[str]:
        """Get set of migration names that have already been applied."""
        return self.applied

    async def record_migration(self, name: str) -> None:
        """Record that a migration has been applied."""
        self.applied.add(name)
        logger.debug(f"[Migration] Recorded: {name}")

    async def initialize(self) -> None:
        """Initialize migration tracking (implementation varies by database type)."""
        pass


class SchemaDiffer:
    """Detects differences between current and desired database schema."""

    @staticmethod
    def compare_columns(
        current: Dict[str, Any],
        desired: Dict[str, str],
    ) -> Dict[str, Any]:
        """Compare current and desired column definitions.
        
        Returns dict of changes needed:
        - added: columns to add
        - removed: columns to remove
        - modified: columns to modify
        """
        current_names = set(current.keys())
        desired_names = set(desired.keys())

        return {
            "added": desired_names - current_names,
            "removed": current_names - desired_names,
            "modified": current_names & desired_names,  # May need type checking
        }


class MigrationStrategy:
    """Base class for database-specific migration strategies."""

    async def detect_schema_changes(
        self, current_schema: Dict[str, Any], desired_schema: Dict[str, Any]
    ) -> List[str]:
        """Detect schema changes and return SQL/commands to apply."""
        raise NotImplementedError()

    async def apply_migrations(self, migrations: List[str]) -> None:
        """Apply migration commands to the database."""
        raise NotImplementedError()


class SQLMigrationStrategy(MigrationStrategy):
    """Migration strategy for SQL databases (SQLite, PostgreSQL, MySQL)."""

    def __init__(self, adapter: Any, engine: Any):
        self.adapter = adapter
        self.engine = engine

    async def detect_schema_changes(
        self, current_schema: Dict[str, Any], desired_schema: Dict[str, Any]
    ) -> List[str]:
        """Generate ALTER TABLE statements for schema differences."""
        migrations = []

        for table_name, desired_columns in desired_schema.items():
            current_columns = current_schema.get(table_name, {})
            differ = SchemaDiffer()
            changes = differ.compare_columns(current_columns, desired_columns)

            # Add new columns
            for col_name in changes["added"]:
                col_type = desired_columns[col_name]
                migration = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type};"
                migrations.append(migration)
                logger.debug(f"[Migration] Add column: {table_name}.{col_name}")

            # Remove unused columns (optional - may want to skip this)
            # for col_name in changes["removed"]:
            #     migration = f"ALTER TABLE {table_name} DROP COLUMN {col_name};"
            #     migrations.append(migration)

        return migrations

    async def apply_migrations(self, migrations: List[str]) -> None:
        """Execute migration statements."""
        for migration in migrations:
            try:
                async with self.engine.begin() as conn:
                    await conn.exec_driver_sql(migration)
                logger.debug(f"[Migration] Applied: {migration}")
            except Exception as e:
                logger.error(f"[Migration] Failed to apply: {migration}. Error: {e}")
                # Decide whether to stop or continue
                raise


class MongoMigrationStrategy(MigrationStrategy):
    """Migration strategy for MongoDB (schema-less, minimal operations needed)."""

    def __init__(self, adapter: Any):
        self.adapter = adapter

    async def detect_schema_changes(
        self, current_schema: Dict[str, Any], desired_schema: Dict[str, Any]
    ) -> List[str]:
        """MongoDB is schema-less, so minimal migrations needed.
        
        Just ensure collections exist.
        """
        migrations = []
        for collection_name in desired_schema.keys():
            migrations.append(f"ensure_collection_exists:{collection_name}")
        return migrations

    async def apply_migrations(self, migrations: List[str]) -> None:
        """Create collections if they don't exist."""
        if not self.adapter.db:
            raise RuntimeError("MongoDB not connected")

        for migration in migrations:
            if migration.startswith("ensure_collection_exists:"):
                collection_name = migration.split(":", 1)[1].lower()
                try:
                    # MongoDB auto-creates collections on first write, but we can explicitly create
                    await self.adapter.db.create_collection(
                        collection_name, check_exists=True
                    )
                    logger.debug(f"[Migration] Ensured collection exists: {collection_name}")
                except Exception as e:
                    # Collection likely already exists
                    logger.debug(f"[Migration] Collection may already exist: {collection_name}")
