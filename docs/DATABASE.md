# Database Configuration Guide

Guaro supports multiple databases with a unified interface. Configuration is flexible and can be adapted to your deployment environment.

## Supported Databases

| Database | Async Driver | Production Ready | Auto-Migrate |
|----------|------------|-----------------|--------------|
| SQLite | aiosqlite | Development | ✓ Yes |
| PostgreSQL | asyncpg | ✓ Yes | ✓ Yes |
| MySQL | aiomysql | ✓ Yes | ✓ Yes |
| MongoDB | motor | ✓ Yes | ✓ Schema-less |

## Connection Methods

### Method 1: Connection String (Simplest)

```python
from guaro import API

api = API(database="sqlite+aiosqlite:///local.db")
```

### Method 2: Dictionary with Components

```python
from guaro import API, DatabaseEngine

api = API(database={
    "host": "localhost",
    "port": 5432,
    "database_name": "myapp",
    "user": "postgres",
    "password": "secret",
    "engine": DatabaseEngine.POSTGRESQL,
})
```

### Method 3: Environment Variables

```python
import os
from guaro import API

api = API(database=os.getenv("DATABASE_URL"))
```

## Database-Specific Setup

### SQLite (Development)

```python
api = API(database={
    "engine": DatabaseEngine.SQLITE,
    "url": "sqlite+aiosqlite:///app.db",
    "auto_migrate": True,
    "echo": True,  # Log all SQL statements
})
```

**Pros:**
- No setup required
- Perfect for local development
- File-based (easy to backup)

**Cons:**
- Single-process only
- Not suitable for production
- No concurrent writes

### PostgreSQL (Production)

```python
api = API(database={
    "host": "db.example.com",
    "port": 5432,
    "database_name": "myapp",
    "user": "app_user",
    "password": os.getenv("DB_PASSWORD"),
    "engine": DatabaseEngine.POSTGRESQL,
    "auto_migrate": False,  # Use Alembic for migrations in prod
    "pool_size": 20,
    "pool_pre_ping": True,
    "timeout": 60,
})
```

**Connection String:**
```python
api = API(database="postgresql+asyncpg://user:pass@host:5432/dbname")
```

### MySQL (Production)

```python
api = API(database={
    "host": "db.example.com",
    "port": 3306,
    "database_name": "myapp",
    "user": "app_user",
    "password": os.getenv("DB_PASSWORD"),
    "engine": DatabaseEngine.MYSQL,
    "auto_migrate": True,
    "pool_size": 10,
})
```

**Connection String:**
```python
api = API(database="mysql+aiomysql://user:pass@host:3306/dbname")
```

### MongoDB (Document Store)

```python
api = API(database={
    "host": "mongodb.example.com",
    "database_name": "myapp",
    "engine": DatabaseEngine.MONGODB,
    "auto_migrate": True,  # Creates collections on first write
})
```

**Connection String with Auth:**
```python
api = API(database="mongodb://user:pass@host:27017/dbname")
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `engine` | DatabaseEngine | Auto-detect | Database type |
| `auto_migrate` | bool | True | Auto-create schema |
| `pool_size` | int | 5 | Connection pool size |
| `pool_pre_ping` | bool | True | Test connections before use |
| `echo` | bool | False | Log all SQL statements |
| `timeout` | int | 30 | Query timeout (seconds) |
| `extra` | dict | {} | Driver-specific options |

## Environment-Based Configuration

Switch databases per environment:

```python
import os
from guaro import API, DatabaseEngine

env = os.getenv("ENVIRONMENT", "development")

if env == "production":
    db_config = {
        "url": os.getenv("DATABASE_URL"),
        "auto_migrate": False,
        "pool_size": 20,
        "pool_pre_ping": True,
    }
elif env == "staging":
    db_config = {
        "url": os.getenv("STAGING_DATABASE_URL"),
        "auto_migrate": True,
        "pool_size": 10,
    }
else:  # development
    db_config = {
        "engine": DatabaseEngine.SQLITE,
        "url": "sqlite+aiosqlite:///dev.db",
        "auto_migrate": True,
        "echo": True,
    }

api = API(database=db_config)
```

## Connection Pooling

Connection pooling improves performance:

```python
api = API(database={
    "host": "db.example.com",
    "database_name": "myapp",
    "pool_size": 20,                    # Maximum connections
    "pool_recycle": 3600,               # Recycle after 1 hour
    "pool_pre_ping": True,              # Test connection before use
    "pool_timeout": 30,                 # Wait 30s for available connection
})
```

## URL Format

Standard SQLAlchemy URL format:

```
dialect+driver://username:password@host:port/database
│       │         │        │       │    │    │
│       │         │        │       │    │    └── Database name
│       │         │        │       │    └── Port (optional)
│       │         │        │       └── Host
│       │         │        └── Password
│       │         └── Username
│       └── Driver (async)
└── Dialect (database type)
```

## Testing Configurations

```python
# test_database.py
import os
from guaro import API, DatabaseEngine

# Use in-memory SQLite for tests
api = API(database={
    "engine": DatabaseEngine.SQLITE,
    "url": "sqlite+aiosqlite:///:memory:",
    "auto_migrate": True,
})
```

## Production Best Practices

1. **Use connection strings from environment:**
   ```python
   api = API(database=os.getenv("DATABASE_URL"))
   ```

2. **Set reasonable pool size:**
   ```python
   "pool_size": 10  # Adjust to your workload
   ```

3. **Enable connection validation:**
   ```python
   "pool_pre_ping": True  # Prevents stale connections
   ```

4. **Disable auto_migrate:**
   ```python
   "auto_migrate": False  # Use Alembic for schema changes
   ```

5. **Use environment-specific timeouts:**
   ```python
   "timeout": 60 if is_production else 30
   ```

## Troubleshooting

**"No module named 'asyncpg'"**
```bash
pip install asyncpg
```

**"No module named 'aiomysql'"**
```bash
pip install aiomysql pymysql
```

**"Connection refused"**
- Verify host/port are correct
- Check firewall rules
- Ensure database is running

**"Too many connections"**
- Reduce pool_size
- Check for connection leaks
- Monitor database connections

## Next Steps

- [Auto-Migration](MIGRATION.md) - Manage schema changes
- [Models](MODELS.md) - Define data models
- [INSTALLATION.md](INSTALLATION.md) - Complete setup guide
