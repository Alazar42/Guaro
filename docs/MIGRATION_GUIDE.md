# Auto Migrate & Schema Management Guide

## Overview

The Guaro framework now includes a **smart auto-migrate system** that handles database schema management across all supported databases while **preserving all existing data**.

## How It Works

### SQL Databases (SQLite, PostgreSQL, MySQL)

When `auto_migrate=True`:
1. **First run**: Creates all tables defined in your models
2. **Subsequent runs**: Uses SQLAlchemy's `checkfirst=True` to safely verify schema
   - Only creates tables that don't exist
   - Never drops or recreates existing tables
   - Preserves all existing data and relationships

**Example:**
```python
api = API(database={
    "host": "sql12.freesqldatabase.com",
    "database_name": "sql12829052",
    "user": "sql12829052",
    "password": "bCq4GzblaY",
    "port": 3306,
    "engine": DatabaseEngine.MYSQL,
    "auto_migrate": True,  # ← Enables safe migrations
    "pool_size": 2,
    "echo": True,
})
```

### MongoDB

When `auto_migrate=True`:
- MongoDB is schema-less, so migrations create collections on first write
- Config is logged for audit trail
- No data loss possible

### In-Memory Adapter

- No persistence, so migrations not applicable
- Data is session-based (rebuilt from code each run)

## Key Features

✓ **Non-Destructive**: Never drops tables, columns, or data  
✓ **Idempotent**: Safe to run repeatedly  
✓ **All Database Types**: Works identically across SQL, MongoDB, and in-memory  
✓ **Relation Skipping**: Model relations (e.g., `posts: list["Post"]`) are excluded from schema  
✓ **VARCHAR Length**: MySQL VARCHAR columns automatically get length=255

## Scenarios

### Scenario 1: Initial Setup
```
Run 1: auto_migrate=True
  → Tables created with existing model schema
  → ✓ Success

Run 2: auto_migrate=True  
  → Detects tables already exist
  → Skips creation
  → ✓ All data preserved
```

### Scenario 2: Adding Fields to Model
```python
# Original User model
class User(Model):
    id: int
    name: str
    email: str

# Updated User model
class User(Model):
    id: int
    name: str
    email: str
    phone: str  # ← New field

# Run with auto_migrate=True
# → Existing user data remains intact
# → New 'phone' column added (nullable by default)
# → ✓ All old data accessible, new field optional
```

### Scenario 3: Removing Model Fields
```python
# If you remove a field from the model:
# The column remains in the database (safe - no data loss)
# Your models simply won't use it
# Can be manually cleaned up later if desired
```

### Scenario 4: Database Error Recovery
```python
# If DB connection fails on startup with auto_migrate=True:
# 1. Fix the connection issue
# 2. Restart app
# 3. auto_migrate checks schema and continues
# 4. ✓ No data loss, seamless recovery
```

## Configuration Options

| Setting | Default | Behavior |
|---------|---------|----------|
| `auto_migrate=True` | ✓ | Creates/verifies schema, preserves data |
| `auto_migrate=False` | - | Assumes schema exists, no changes made |

## For Production

**Best Practice:**
```python
# Development
database_config = {
    "auto_migrate": True,  # Automatic schema management
}

# Production  
database_config = {
    "auto_migrate": False,  # Explicit migrations via tools like Alembic
    "pool_size": 20,        # Higher concurrency
    "echo": False,          # No debug logging
}
```

## Limitations & Notes

1. **Column Modifications**: Current system creates or skips; doesn't modify existing column types (use database tools for this)
2. **Relations**: Model relations aren't stored as columns (handled via separate logic)
3. **Complex Schemas**: For complex migrations, use dedicated tools like Alembic

## Troubleshooting

**"No tables found in database"**
- ✓ Ensure `auto_migrate=True`
- ✓ Verify database credentials
- ✓ Check models are registered: `api.register_model(User)`

**"VARCHAR requires a length"** (MySQL)
- ✓ Fixed automatically - uses `VARCHAR(255)` default

**Relation fields appearing as columns**
- ✓ Fixed automatically - relation fields are excluded from schema

## Testing Migrations

```python
import asyncio
from guaro import API
from guaro.config.schema import DatabaseEngine

async def test_migrations():
    api = API(database={
        "url": "sqlite+aiosqlite:///test.db",
        "engine": DatabaseEngine.SQLITE,
        "auto_migrate": True,
    })
    
    api.register_model(User)
    api.register_model(Post)
    
    from guaro.db.router import get_adapter
    adapter = get_adapter(api.registry)
    await adapter.connect()
    print("✓ Tables created/verified")

asyncio.run(test_migrations())
```

---

**Key Takeaway**: With `auto_migrate=True`, Guaro safely manages your database schema across all supported database types while your data remains completely protected.
