# Installation & Setup Guide

## Requirements

- Python 3.11 or higher
- pip or poetry
- (Optional) Virtual environment tool (venv, conda, poetry)

## Installation

### Option 1: From PyPI (Recommended)

```bash
pip install guaro
```

### Option 2: From Source (Development)

```bash
# Clone the repository
git clone https://github.com/MickyCodes/guaro.git
cd guaro

# Create virtual environment
python -m venv .venv
source .venv/Scripts/activate  # On Windows: .\.venv\Scripts\activate

# Install in editable mode
pip install -e ".[dev]"
```

## Quick Setup

### 1. Initialize Your Project

```bash
mkdir my_api
cd my_api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install guaro
```

### 2. Create Your First Model

```python
# models.py
from guaro import Model

class User(Model):
    id: int
    name: str
    email: str

class Post(Model):
    id: int
    title: str
    content: str
    author_id: int
```

### 3. Create Your API

```python
# main.py
from guaro import API, DatabaseEngine, Router
from models import User, Post

# Initialize API
api = API(database={
    "engine": DatabaseEngine.SQLITE,
    "url": "sqlite+aiosqlite:///app.db",
    "auto_migrate": True,
})

# Register models
api.register_model(User)
api.register_model(Post)

# Create routes
users_router = Router(prefix="/users")

@users_router.get("/")
async def list_users() -> list[User]:
    return await User.all()

@users_router.post("/")
async def create_user(name: str, email: str) -> User:
    user = User(name=name, email=email)
    await user.save()
    return user

api.register_router(users_router)

# Run the API
if __name__ == "__main__":
    api.run(mode="hybrid")  # REST + GraphQL on http://localhost:8000
```

### 4. Run Your API

```bash
python main.py
```

Visit:
- REST API: http://localhost:8000/openapi.json
- GraphQL: http://localhost:8000/graphql
- Swagger UI: http://localhost:8000/docs

## Database Configuration

### SQLite (Local Development)

```python
api = API(database={
    "engine": DatabaseEngine.SQLITE,
    "url": "sqlite+aiosqlite:///local.db",
    "auto_migrate": True,
})
```

### PostgreSQL (Production)

```python
api = API(database={
    "host": "db.example.com",
    "database_name": "myapp",
    "user": "postgres",
    "password": "secret",
    "port": 5432,
    "engine": DatabaseEngine.POSTGRESQL,
    "auto_migrate": True,
    "pool_size": 20,
    "pool_pre_ping": True,
})
```

### MySQL

```python
api = API(database={
    "host": "db.example.com",
    "database_name": "myapp",
    "user": "root",
    "password": "secret",
    "port": 3306,
    "engine": DatabaseEngine.MYSQL,
    "auto_migrate": True,
    "pool_size": 10,
})
```

### MongoDB

```python
api = API(database={
    "host": "mongodb.example.com",
    "database_name": "myapp",
    "engine": DatabaseEngine.MONGODB,
    "auto_migrate": True,
})
```

## Environment Variables

Create a `.env` file for sensitive configuration:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
DEBUG=True
LOG_LEVEL=INFO
```

Load in your app:

```python
import os
from dotenv import load_dotenv

load_dotenv()

api = API(database=os.getenv("DATABASE_URL"))
```

## Next Steps

- Read [Models Guide](MODELS.md) to learn about data modeling
- Check [Routing Guide](ROUTING.md) for REST endpoints
- See [Auto-Migration](MIGRATION.md) for database management
- Review [examples/](../examples/) for complete working examples
