# Guaro - Modern Python Backend Framework

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)

A powerful, async-first Python framework for building REST & GraphQL APIs with automatic schema management, dependency injection, and type-safe data validation.

## ✨ Features

- **🚀 Async-First**: Built on Starlette for high-performance async request handling
- **🔄 Multi-Protocol**: REST and GraphQL support out of the box
- **📊 Database Agnostic**: SQLite, PostgreSQL, MySQL, MongoDB support with intelligent schema management
- **✅ Auto-Migrate**: Smart schema updates that preserve data (never loses existing data)
- **🔗 Relations**: Built-in support for complex relationships and nested queries
- **💉 Dependency Injection**: Clean dependency resolution for handlers and middleware
- **🛡️ Type Safe**: Full type hints for better IDE support and developer experience
- **📝 Auto Documentation**: Automatic OpenAPI/Swagger generation
- **🔐 Middleware & Auth**: Built-in middleware support for authentication & permissions

## 🚀 Quick Start

### Installation

Install the latest version from PyPI:

```bash
# Basic installation with SQLite support
pip install guaro

# With specific database support
pip install "guaro[postgres]"     # PostgreSQL
pip install "guaro[mysql]"        # MySQL
pip install "guaro[mongodb]"      # MongoDB
pip install "guaro[all-databases]" # All databases

# Development version from source
git clone https://github.com/Alazar42/Guaro.git
cd Guaro
pip install -e ".[all-databases,dev]"
```

**See [Installation & Setup Guide](docs/INSTALLATION.md) for detailed setup instructions and environment configuration.**

### Basic Example

```python
from guaro import API, Model, Router, DatabaseEngine

# Define your models
class User(Model):
    id: int
    name: str
    email: str

class Post(Model):
    id: int
    title: str
    body: str
    author: "User"

# Configure API
api = API(database={
    "engine": DatabaseEngine.POSTGRESQL,
    "url": "postgresql+asyncpg://user:pass@localhost/dbname",
    "auto_migrate": True,  # Automatic schema creation
})

# Register models
api.register_model(User)
api.register_model(Post)

# Create routes
router = Router(prefix="/users")

@router.get("/")
async def list_users() -> list[User]:
    return await User.all()

@router.get("/{id}")
async def get_user(id: int) -> User | None:
    return await User.find(id)

api.register_router(router)

# Run
if __name__ == "__main__":
    api.run(mode="hybrid")  # REST + GraphQL
```

## 📚 Documentation

Full documentation available at [docs/README.md](docs/README.md) with learning paths and guides:

### Getting Started
- **[Installation & Setup](docs/INSTALLATION.md)** - Installation methods (pip, clone, Poetry)
- **[Quick Start Tutorial](docs/INSTALLATION.md#quick-setup-walkthrough)** - Build your first API in 5 minutes

### Core Concepts
- **[Models & Data](docs/MODELS.md)** - Define models with relationships
- **[REST Routing](docs/ROUTING.md)** - Create REST endpoints
- **[Database Configuration](docs/DATABASE.md)** - All supported databases
- **[GraphQL](docs/GRAPHQL.md)** - GraphQL schema and queries

### Advanced Topics
- **[Middleware & Authentication](docs/MIDDLEWARE.md)** - Security and authorization
- **[Dependency Injection](docs/DEPENDENCY_INJECTION.md)** - Service management
- **[Developer Guide](docs/DEVELOPMENT.md)** - Architecture and testing

### Contributing & Deployment
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to Guaro
- **[Development Setup](DEVELOPMENT_SETUP.md)** - Local development environment
- **[Publishing Guide](PUBLISH.md)** - Deploying to PyPI
- **[Changelog](CHANGELOG.md)** - Version history and roadmap

## 🛠️ To Get Started

1. **Users**: Follow the [Installation & Setup](docs/INSTALLATION.md) guide
2. **Developers**: See [Development Setup](DEVELOPMENT_SETUP.md) for cloning and local setup
3. **Contributors**: Read [Contributing Guide](CONTRIBUTING.md) and [Developer Guide](docs/DEVELOPMENT.md)/
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
