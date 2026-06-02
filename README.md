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

## MVP notes

This repository contains a production-oriented MVP architecture, not a finished distributed system. The implementation focuses on:

- unified metadata registration
- shared execution and planning
- automatic REST and GraphQL generation
- request-scoped batching and caching hooks

## Startup modes

- `rest` serves only REST routes
- `graphql` serves only GraphQL
- `hybrid` serves both simultaneously
