# Development Guide

This guide is for developers contributing to Guaro itself, not using Guaro in projects.

## Prerequisites

- Python 3.11+
- Git
- Poetry or pip
- A code editor (VS Code, PyCharm, etc.)

## Setup Development Environment

### 1. Clone Repository

```bash
git clone https://github.com/Alazar42/Guaro.git
cd guaro
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv .venv
source .venv/Scripts/activate  # Windows: .\.venv\Scripts\activate

# Or using conda
conda create -n guaro python=3.11
conda activate guaro
```

### 3. Install Dependencies

```bash
# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# Or with poetry
poetry install
```

## Project Structure

```
guaro/
├── guaro/                       # Main package
│   ├── app.py                  # API class
│   ├── config/                 # Configuration
│   ├── core/                   # Core execution engine
│   ├── db/                     # Database layer
│   │   └── adapters/          # Database drivers
│   ├── graphql/               # GraphQL support
│   ├── rest/                  # REST support
│   ├── middleware/            # Middleware system
│   ├── loaders/               # Data loaders
│   ├── serialization/         # Output serialization
│   └── validation/            # Input validation
├── docs/                       # Documentation
├── examples/                   # Example implementations
├── tests/                      # Test suite
├── pyproject.toml             # Package config
├── README.md                  # Main README
└── LICENSE                    # MIT License
```

## Code Style

Guaro follows PEP 8 with type hints:

```python
from __future__ import annotations

from typing import Any, Dict, List
from dataclasses import dataclass

@dataclass
class MyClass:
    """Class docstring with description."""
    
    name: str
    value: int = 0
    
    async def my_method(self, arg1: str, arg2: int) -> Dict[str, Any]:
        """Method docstring."""
        result: Dict[str, Any] = {}
        return result
```

### Style Checks

```bash
# Format code
black guaro/

# Check formatting
flake8 guaro/

# Type checking
mypy guaro/
```

## Testing

Write tests in the `tests/` directory:

```python
# tests/test_models.py
import pytest
from guaro import API, Model, DatabaseEngine

class User(Model):
    id: int
    name: str

@pytest.mark.asyncio
async def test_user_creation():
    api = API(database={
        "engine": DatabaseEngine.SQLITE,
        "url": "sqlite+aiosqlite:///:memory:",
    })
    
    api.register_model(User)
    
    user = User(name="Alice")
    await user.save()
    
    found = await User.find(user.id)
    assert found.name == "Alice"
```

Run tests:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=guaro

# Watch mode (requires pytest-watch)
ptw
```

## Key Modules

### guaro/core/
- `execution_engine.py` - Executes routes and resolvers
- `registry.py` - Stores models, routes, middleware
- `schema.py` - Model schema compilation
- `query_ir.py` - Internal query representation

### guaro/db/
- `repository.py` - Data access layer
- `adapters/` - Database drivers (SQL, MongoDB, Memory)
- `router.py` - Adapter factory

### guaro/rest/
- `adapter.py` - REST API builder using Starlette

### guaro/graphql/
- `adapter.py` - GraphQL API builder using Strawberry
- `schema_builder.py` - GraphQL schema generation

## Common Tasks

### Adding a New Database Adapter

1. Create `guaro/db/adapters/new_adapter.py`:

```python
from guaro.db.adapters.base import DatabaseAdapter
from guaro.core.query_ir import QueryIR

class NewAdapter(DatabaseAdapter):
    async def execute_query(self, ir: QueryIR):
        # Implement query execution
        pass
    
    async def insert(self, entity: str, data: dict):
        # Implement insertion
        pass
```

2. Register in `guaro/db/router.py`:

```python
elif engine == DatabaseEngine.NEWDB:
    from guaro.db.adapters.new_adapter import NewAdapter
    adapter = NewAdapter(...)
```

### Adding Middleware

```python
# guaro/middleware/custom.py
from guaro.execution.context import ExecutionContext

async def my_middleware(context: ExecutionContext) -> None:
    # Before request
    context.user = extract_user(context.request)
    
    # Handler runs here
    # Runs after_handler...
```

Register in API:

```python
from guaro.middleware.custom import my_middleware

registry.middleware.append(my_middleware)
```

## Debugging

Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

Debug a route:

```python
import pdb; pdb.set_trace()  # Breakpoint
```

## Performance Profiling

```bash
# Profile with cProfile
python -m cProfile -s cumulative main.py

# Flamegraph (requires py-spy)
py-spy record -o profile.svg -- python main.py
```

## Documentation

Documentation is in the `docs/` directory using Markdown.

Update docs when:
- Adding new features
- Changing API
- Fixing bugs
- Improving examples

## Version Bumping

1. Update `pyproject.toml`:

```toml
[project]
version = "0.2.0"
```

2. Update `CHANGELOG.md` (if exists)

3. Tag release:

```bash
git tag v0.2.0
git push origin v0.2.0
```

## Submitting Changes

1. Create feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make changes and commit:
   ```bash
   git add .
   git commit -m "Add my feature"
   ```

3. Push and create PR:
   ```bash
   git push origin feature/my-feature
   ```

4. Ensure:
   - Tests pass
   - Code is formatted
   - Documentation updated
   - No breaking changes (without discussion)

## Resources

- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Starlette Docs](https://www.starlette.io/)
- [Strawberry GraphQL Docs](https://strawberry.rocks/)
- [AsyncIO Docs](https://docs.python.org/3/library/asyncio.html)

## Getting Help

- Open an issue on GitHub
- Check existing issues/PRs
- Ask in discussions

Thank you for contributing to Guaro! ❤️
