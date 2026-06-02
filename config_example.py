"""Database Configuration Examples for Guaro

This file demonstrates the three supported configuration patterns:
1. Inline configuration (simple, for development)
2. External module configuration (recommended for production)
3. Environment-based configuration (dev/staging/prod)
"""

from guaro import DatabaseEngine

# ============================================================================
# Pattern 1: Environment-Specific Configurations
# ============================================================================

# Development configuration (SQLite, fast, no connections pooling)
dev_config = {
    "url": "sqlite+aiosqlite:///guaro_dev.db",
    "engine": DatabaseEngine.SQLITE,
    "auto_migrate": True,
    "pool_size": 1,
    "echo": True,  # Log all SQL for debugging
}

# Staging configuration (PostgreSQL via internal network)
staging_config = {
    "url": "postgresql+asyncpg://dbuser:dbpass@db-staging.internal:5432/guaro_staging",
    "engine": DatabaseEngine.POSTGRESQL,
    "auto_migrate": True,
    "pool_size": 10,
    "pool_pre_ping": True,
    "echo": False,
}

# Production configuration (PostgreSQL with connection pooling)
prod_config = {
    "url": "postgresql+asyncpg://dbuser:dbpass@db-prod.internal:5432/guaro_prod",
    "engine": DatabaseEngine.POSTGRESQL,
    "auto_migrate": False,  # Migrations run separately in production
    "pool_size": 20,
    "pool_pre_ping": True,
    "echo": False,
    "timeout": 60,
}

# ============================================================================
# Pattern 2: Export the Active Configuration
# ============================================================================

# In a real app, you would select based on environment:
# import os
# environment = os.getenv("ENVIRONMENT", "dev")
# database_config = globals()[f"{environment}_config"]

# For now, default to dev:
database_config = dev_config

# ============================================================================
# Pattern 3: URL-Only Configuration (auto-detects engine)
# ============================================================================

minimal_config = "sqlite+aiosqlite:///guaro.db"

# ============================================================================
# Pattern 4: Extended Configuration with Extra Options
# ============================================================================

advanced_config = {
    "url": "postgresql+asyncpg://user:pass@localhost/guaro",
    "engine": DatabaseEngine.POSTGRESQL,
    "auto_migrate": True,
    "pool_size": 15,
    "pool_pre_ping": True,
    "echo": False,
    "timeout": 45,
    "extra": {
        "ssl": "require",
        "application_name": "guaro_api",
        "statement_cache_size": 100,
    },
}

# ============================================================================
# Usage Examples
# ============================================================================

# Example 1: Use external configuration (recommended)
# from config import database_config
# from guaro import API
#
# api = API(database=database_config)
# api.run()

# Example 2: Inline configuration
# from guaro import API, DatabaseEngine
#
# api = API(
#     database={
#         "url": "sqlite+aiosqlite:///local.db",
#         "engine": DatabaseEngine.SQLITE,
#     }
# )
# api.run()

# Example 3: Default SQLite (no config)
# from guaro import API
#
# api = API()  # Automatically uses SQLite in guaro.db
# api.run()

# Example 4: URL-only configuration
# from guaro import API
#
# api = API(database="postgresql://user:pass@localhost/guaro")
# api.run()
