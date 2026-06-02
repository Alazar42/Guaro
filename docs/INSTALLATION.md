# Installation & Setup Guide

## Requirements

- Python 3.11, 3.12, or 3.13+
- pip package manager
- Virtual environment (recommended: venv, conda, pyenv)

## Installation Methods

### Option 1: From PyPI (Recommended for Users)

Install the latest stable release from PyPI:

```bash
# Basic installation with SQLite support
pip install guaro

# With PostgreSQL support
pip install "guaro[postgres]"

# With MySQL support
pip install "guaro[mysql]"

# With MongoDB support
pip install "guaro[mongodb]"

# With all database drivers
pip install "guaro[all-databases]"

# Development version (with dev tools)
pip install "guaro[dev]"
```

**Latest Version**: Check [PyPI](https://pypi.org/project/guaro/) for current version.

### Option 2: From GitHub (Development/Bleeding Edge)

Clone and install from source:

```bash
# Clone the repository
git clone https://github.com/Alazar42/Guaro.git
cd Guaro

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[all-databases,dev]"

# Run tests to verify installation
pytest
```

### Option 3: Using Poetry

If you use Poetry:

```bash
# Create a new project
poetry new my_api
cd my_api

# Add Guaro as dependency
poetry add guaro

# Or with specific database support
poetry add "guaro[postgres]"
```

## Quick Setup Walkthrough

### Step 1: Set Up Your Environment

```bash
# Create project directory
mkdir my_api
cd my_api

# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install Guaro
pip install guaro
```

### Step 2: Create Your First Model

Create `models.py`:

```python
from guaro import Model

class User(Model):
    id: int
    name: str
    email: str
    created_at: str = "2024-01-01"

class Post(Model):
    id: int
    title: str
    content: str
    author_id: int  # Foreign key to User
```

### Step 3: Set Up Your API

Create `main.py`:

```python
from guaro import API, Router
from models import User, Post

# Initialize API with SQLite database
api = API(database={
    "engine": "sqlite",
    "url": "sqlite+aiosqlite:///app.db",
    "auto_migrate": True,  # Auto-create tables
})

# Register models
api.register_model(User)
api.register_model(Post)

# Create routes
users_router = Router(prefix="/users")

@users_router.get("/")
async def list_users() -> list[User]:
    """Get all users"""
    return await User.all()

@users_router.get("/{user_id}")
async def get_user(user_id: int) -> User:
    """Get specific user"""
    user = await User.find(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@users_router.post("/")
async def create_user(name: str, email: str) -> User:
    """Create new user"""
    user = User(name=name, email=email)
    await user.save()
    return user

api.register_router(users_router)

if __name__ == "__main__":
    api.run(mode="hybrid", host="127.0.0.1", port=8000)
```

### Step 4: Run Your API

```bash
# Run the server
python main.py

# Server starts on http://127.0.0.1:8000
```

### Step 5: Test Your API

Access the endpoints:

- **REST API**: http://localhost:8000
- **GraphQL Playground**: http://localhost:8000/graphql
- **Swagger/OpenAPI Docs**: http://localhost:8000/docs

Example requests:

```bash
# Create a user
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'

# Get all users
curl http://localhost:8000/users/

# GraphQL query
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { users { id name email } }"
  }'
```

## Environment Configuration

### Using Environment Variables

Create `.env`:

```bash
DATABASE_URL=sqlite+aiosqlite:///app.db
AUTO_MIGRATE=true
DEBUG=true
```

Update `main.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

api = API(database={
    "url": os.getenv("DATABASE_URL", "sqlite+aiosqlite:///app.db"),
    "auto_migrate": os.getenv("AUTO_MIGRATE", "true").lower() == "true",
})
```

Install python-dotenv:

```bash
pip install python-dotenv
```

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
