# REST Routing Guide

Routes define your REST API endpoints. They're organized by resource using routers.

## Basic Router

```python
from guaro import Router
from models import User

router = Router(prefix="/users")

@router.get("/")
async def list_users() -> list[User]:
    """Get all users"""
    return await User.all()

@router.get("/{id}")
async def get_user(id: int) -> User | None:
    """Get single user by ID"""
    return await User.find(id)

@router.post("/")
async def create_user(name: str, email: str) -> User:
    """Create new user"""
    user = User(name=name, email=email)
    await user.save()
    return user

@router.put("/{id}")
async def update_user(id: int, name: str, email: str) -> User:
    """Update user"""
    user = await User.find(id)
    user.name = name
    user.email = email
    await user.save()
    return user

@router.delete("/{id}")
async def delete_user(id: int) -> dict:
    """Delete user"""
    await User.delete(id)
    return {"deleted": True}

# Register with API
api.register_router(router)
```

## HTTP Methods

Guaro supports all standard HTTP methods:

```python
@router.get("/users/")           # Read
@router.post("/users/")          # Create
@router.put("/users/{id}")       # Full update
@router.patch("/users/{id}")     # Partial update
@router.delete("/users/{id}")    # Delete
@router.options("/users/")       # Options
@router.head("/users/")          # Head
```

## Path Parameters

Extract values from URL paths:

```python
# Single parameter
@router.get("/users/{id}")
async def get_user(id: int) -> User:
    return await User.find(id)

# Multiple parameters
@router.get("/users/{user_id}/posts/{post_id}")
async def get_user_post(user_id: int, post_id: int):
    user = await User.find(user_id)
    # Get post by user_id and post_id...
```

## Query Parameters

Extract from query string:

```python
# /users/?page=2&limit=50
@router.get("/users/")
async def list_users(page: int = 1, limit: int = 10) -> list[User]:
    offset = (page - 1) * limit
    # Get users with pagination
    users = await User.all()
    return users[offset:offset + limit]
```

## Request Body

Accept JSON request bodies:

```python
@router.post("/users/")
async def create_user(name: str, email: str, age: int) -> User:
    """Create user from JSON body"""
    user = User(name=name, email=email, age=age)
    await user.save()
    return user

# Client sends:
# POST /users/
# Content-Type: application/json
# {
#   "name": "Alice",
#   "email": "alice@example.com",
#   "age": 30
# }
```

## Return Types & Serialization

Return types determine JSON output:

```python
# Single model → returns object
@router.get("/users/{id}")
async def get_user(id: int) -> User:
    return await User.find(id)
# Returns: {"id": 1, "name": "Alice", "email": "alice@example.com"}

# List of models → returns array
@router.get("/users/")
async def list_users() -> list[User]:
    return await User.all()
# Returns: [{"id": 1, ...}, {"id": 2, ...}]

# Optional → returns null or object
@router.get("/users/{id}")
async def maybe_user(id: int) -> User | None:
    return await User.find(id)
# Returns: {"id": 1, ...} or null

# Dictionary → returns object
@router.post("/users/")
async def create(name: str) -> dict:
    return {"created": True, "name": name}
# Returns: {"created": true, "name": "Alice"}
```

## Organizing Routes

Group related routes:

```python
# users_router.py
from guaro import Router
from models import User

router = Router(prefix="/users")

@router.get("/")
async def list_users() -> list[User]:
    return await User.all()

# users.py (main app file)
from guaro import API
from users_router import router

api = API(...)
api.register_router(router)
```

Multiple routers:

```python
from users_router import router as users_router
from posts_router import router as posts_router
from comments_router import router as comments_router

api.register_router(users_router)
api.register_router(posts_router)
api.register_router(comments_router)
```

## Status Codes & Error Handling

Handle errors gracefully:

```python
@router.get("/users/{id}")
async def get_user(id: int) -> User | None:
    user = await User.find(id)
    if not user:
        # Return 404
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users/")
async def create_user(email: str) -> User:
    # Validate
    if not "@" in email:
        raise HTTPException(status_code=400, detail="Invalid email")
    
    user = User(email=email)
    await user.save()
    return user  # 200 OK
```

## Field Selection

Clients can request only specific fields:

```python
# Request: GET /users/?fields=id,name
# Response: [{"id": 1, "name": "Alice"}]

@router.get("/users/")
async def list_users() -> list[User]:
    return await User.all()
```

The framework automatically respects the `fields` query parameter.

## Testing Routes

```python
import asyncio
from httpx import AsyncClient
from main import app

async def test():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users/")
        print(response.json())
        assert response.status_code == 200

asyncio.run(test())
```

## Next Steps

- [Middleware & Auth](MIDDLEWARE.md) - Add authentication
- [Dependency Injection](DEPENDENCY_INJECTION.md) - Advanced patterns
- [GraphQL](GRAPHQL.md) - Expose GraphQL endpoints
