# Guaro

Guaro is a unified API framework for building REST APIs, GraphQL APIs, or both from one codebase, one schema system, and one execution engine.

## What Guaro provides

- One model registry for REST and GraphQL
- One router system for REST endpoints and GraphQL operations
- One middleware and permission abstraction
- One query planner for REST field selection and GraphQL selection sets
- One execution engine with sync and async support
- Automatic serialization and relation batching hooks

## Project layout

```text
project/
├── app.py
├── models/
├── routes/
├── middleware/
└── guaro/
```

## Quick start

```bash
python -m pip install -e .
python app.py
```

## Example usage

```python
from guaro import API, Model, Router, permission, require_auth


class User(Model):
    id: int
    name: str
    email: str


router = Router(prefix="/users")


@router.get("/")
@require_auth
def get_users():
    return User.all()


api = API()
api.register_model(User)
api.register_router(router)
api.run(mode="hybrid")
```

## Database Configuration

Guaro supports fully externalized, environment-driven database configuration. Configuration is decoupled from application code and can be environment-specific (dev/staging/prod).

### Configuration Patterns

#### Pattern 1: Default Configuration (Automatic SQLite)

Works out of the box with zero configuration:

```python
from guaro import API

api = API()  # Automatically uses sqlite+aiosqlite:///guaro.db
api.run()
```

#### Pattern 2: Inline Configuration

Convenient for quick prototypes and testing:

```python
from guaro import API, DatabaseEngine

api = API(
    database={
        "url": "sqlite+aiosqlite:///local.db",
        "engine": DatabaseEngine.SQLITE,
        "auto_migrate": True,
        "pool_size": 2,
        "echo": True,
    }
)
api.run()
```

#### Pattern 3: External Configuration (Recommended)

Production-grade pattern — configuration is isolated from application code:

**config.py:**
```python
from guaro import DatabaseEngine

# Development
dev_config = {
    "url": "sqlite+aiosqlite:///guaro_dev.db",
    "engine": DatabaseEngine.SQLITE,
    "auto_migrate": True,
}

# Staging
staging_config = {
    "url": "postgresql+asyncpg://user:pass@db-staging.internal/guaro_staging",
    "engine": DatabaseEngine.POSTGRESQL,
    "auto_migrate": True,
    "pool_size": 10,
}

# Production
prod_config = {
    "url": "postgresql+asyncpg://user:pass@db-prod.internal/guaro_prod",
    "engine": DatabaseEngine.POSTGRESQL,
    "auto_migrate": False,  # Migrations run separately
    "pool_size": 20,
}

# Load based on environment
import os
environment = os.getenv("ENVIRONMENT", "dev")
database_config = locals()[f"{environment}_config"]
```

**app.py:**
```python
from guaro import API
from config import database_config

api = API(database=database_config)
api.run()
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `url` | str | `"sqlite+aiosqlite:///guaro.db"` | Database connection URL |
| `engine` | DatabaseEngine | inferred from URL or SQLITE | Database engine type |
| `auto_migrate` | bool | `True` | Run migrations automatically on startup |
| `pool_size` | int | `5` | Connection pool size |
| `pool_pre_ping` | bool | `True` | Test connections before use |
| `echo` | bool | `False` | Log all SQL statements |
| `timeout` | int | `30` | Connection timeout in seconds |
| `extra` | dict | `{}` | Engine-specific options |

### Supported Engines

```python
from guaro import DatabaseEngine

DatabaseEngine.SQLITE      # SQLite (default)
DatabaseEngine.POSTGRESQL # PostgreSQL
DatabaseEngine.MYSQL      # MySQL
DatabaseEngine.MONGODB    # MongoDB
DatabaseEngine.MEMORY     # In-memory cache
```

### URL Format

Guaro normalizes URLs into transport strings that are passed to adapters. The engine determines how the URL is interpreted:

- **SQLite**: `sqlite+aiosqlite:///path/to/db.db`
- **PostgreSQL**: `postgresql+asyncpg://user:pass@host:port/dbname`
- **MySQL**: `mysql+aiomysql://user:pass@host:port/dbname`
- **MongoDB**: `mongodb://user:pass@host:port/dbname`
- **Custom**: `https://db.api.company.com/api` (engine must be specified)

### Environment-Based Configuration

For multi-environment deployments:

```bash
# Development (automatic SQLite)
python app.py

# Staging environment
export ENVIRONMENT=staging
python app.py

# Production environment
export ENVIRONMENT=prod
python app.py
```

In `config.py`:
```python
import os

environment = os.getenv("ENVIRONMENT", "dev")
database_config = locals()[f"{environment}_config"]
```

### Advanced Configuration

With extra options for engine-specific settings:

```python
database_config = {
    "url": "postgresql+asyncpg://user@localhost/guaro",
    "engine": DatabaseEngine.POSTGRESQL,
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
```



This repository contains a production-oriented MVP architecture, not a finished distributed system. The implementation focuses on:

- unified metadata registration
- shared execution and planning
- automatic REST and GraphQL generation
- request-scoped batching and caching hooks

## Startup modes

- `rest` serves only REST routes
- `graphql` serves only GraphQL
- `hybrid` serves both simultaneously
