# Middleware & Authentication

Guaro provides middleware and authentication support for securing your API.

## Basic Middleware

Middleware functions run before or after route handlers:

```python
from guaro import API, Router
from guaro.execution.context import ExecutionContext

router = Router()

@router.get("/protected/")
async def protected_route() -> dict:
    return {"data": "secret"}

# Add middleware globally
api = API(database={...})

async def auth_middleware(context: ExecutionContext) -> None:
    """Runs before each route"""
    token = context.request.headers.get("Authorization")
    if not token:
        from starlette.exceptions import HTTPException
        raise HTTPException(status_code=401, detail="Missing token")

api.register_middleware(auth_middleware)
```

## Route-Level Middleware

Protect specific routes:

```python
from guaro.middleware import Requires, Permission

router = Router()

@router.get("/admin/")
@Requires(permission=Permission.ADMIN)
async def admin_only() -> dict:
    return {"status": "admin access"}
```

## Authorization Headers

Extract and validate tokens:

```python
from guaro.execution.context import ExecutionContext

async def token_validator(context: ExecutionContext) -> dict:
    """Extract and validate JWT token"""
    auth_header = context.request.headers.get("Authorization", "")
    
    if not auth_header.startswith("Bearer "):
        raise ValueError("Invalid auth header")
    
    token = auth_header.split(" ")[1]
    
    # Validate and decode token
    user_data = validate_jwt(token)
    return user_data

# Store in context for route use
async def extract_user(context: ExecutionContext) -> None:
    try:
        context.user = await token_validator(context)
    except ValueError:
        from starlette.exceptions import HTTPException
        raise HTTPException(status_code=401, detail="Invalid token")

api.register_middleware(extract_user)
```

## Custom User Object

Store authenticated user in context:

```python
from dataclasses import dataclass

@dataclass
class User:
    id: int
    username: str
    permissions: list[str]

async def load_user(context: ExecutionContext) -> None:
    token = context.request.headers.get("Authorization")
    if token:
        # Verify and decode
        user_id = decode_token(token)
        context.user = User(
            id=user_id,
            username="john",
            permissions=["read", "write"]
        )
    else:
        context.user = None

api.register_middleware(load_user)
```

## Using User in Routes

Access authenticated user:

```python
router = Router()

@router.get("/profile/")
async def get_profile(context: ExecutionContext) -> dict:
    if not context.user:
        raise HTTPException(status_code=401)
    
    return {
        "id": context.user.id,
        "username": context.user.username,
        "permissions": context.user.permissions
    }
```

## Permission Checking

Implement permission-based access:

```python
async def require_permission(required: str):
    """Decorator factory for permission checks"""
    async def middleware(context: ExecutionContext) -> None:
        if not context.user or required not in context.user.permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Permission '{required}' required"
            )
    return middleware

# Usage
@router.post("/users/create")
@require_permission("admin")
async def create_user(name: str) -> dict:
    return {"created": True}
```

## CORS Middleware

Enable cross-origin requests:

```python
from starlette.middleware.cors import CORSMiddleware

app = api.to_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Error Handling in Middleware

Catch and handle errors:

```python
import logging

logger = logging.getLogger(__name__)

async def error_handler(context: ExecutionContext) -> None:
    try:
        # Middleware logic
        pass
    except HTTPException:
        # Expected HTTP errors
        raise
    except Exception as e:
        logger.exception("Middleware error")
        raise HTTPException(status_code=500, detail="Internal error")

api.register_middleware(error_handler)
```

## Rate Limiting

Implement simple rate limiting:

```python
from collections import defaultdict
from datetime import datetime, timedelta

rate_limit_store = defaultdict(list)

async def rate_limit_middleware(context: ExecutionContext) -> None:
    """Allow 100 requests per minute per IP"""
    ip = context.request.client.host
    now = datetime.now()
    cutoff = now - timedelta(minutes=1)
    
    # Clean old entries
    rate_limit_store[ip] = [
        ts for ts in rate_limit_store[ip]
        if ts > cutoff
    ]
    
    # Check limit
    if len(rate_limit_store[ip]) >= 100:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    rate_limit_store[ip].append(now)

api.register_middleware(rate_limit_middleware)
```

## Logging Middleware

Track all requests:

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def logging_middleware(context: ExecutionContext) -> None:
    start = datetime.now()
    
    # Store start time in context
    context.start_time = start
    context.route = context.request.url.path
    context.method = context.request.method
    
    # Will log after handler completes via after-hook
    yield  # Allow handler to run

async def after_logging(context: ExecutionContext) -> None:
    duration = (datetime.now() - context.start_time).total_seconds()
    logger.info(
        f"{context.method} {context.route} - {duration:.3f}s"
    )

api.register_middleware(logging_middleware)
api.register_after_handler(after_logging)
```

## JWT Authentication Example

Complete example with JWT:

```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"

def create_token(user_id: int) -> str:
    """Create JWT token"""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> int:
    """Verify JWT token and extract user_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

async def jwt_auth(context: ExecutionContext) -> None:
    """JWT authentication middleware"""
    auth_header = context.request.headers.get("Authorization", "")
    
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            user_id = verify_token(token)
            context.user_id = user_id
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid token")
    else:
        context.user_id = None

api.register_middleware(jwt_auth)

# Usage in routes
@router.post("/login/")
async def login(username: str, password: str) -> dict:
    # Verify credentials
    user_id = authenticate_user(username, password)
    token = create_token(user_id)
    return {"token": token}

@router.get("/me/")
async def get_current_user(context: ExecutionContext) -> dict:
    if not context.user_id:
        raise HTTPException(status_code=401)
    return {"user_id": context.user_id}
```

## Testing Middleware

Unit test middleware:

```python
import pytest
from guaro.execution.context import ExecutionContext

@pytest.mark.asyncio
async def test_auth_middleware():
    # Create mock request
    class MockRequest:
        headers = {"Authorization": "Bearer valid-token"}
        client = type('obj', (object,), {'host': '127.0.0.1'})
    
    context = ExecutionContext(request=MockRequest())
    
    # Test middleware
    await jwt_auth(context)
    assert hasattr(context, 'user_id')
```

## Best Practices

1. **Always validate input** - Never trust client data
2. **Use HTTPS in production** - Tokens vulnerable to interception
3. **Short token expiration** - Reduce impact of stolen tokens
4. **Log security events** - Track auth failures and suspicious activity
5. **Separate public/private routes** - Group sensitive endpoints
6. **Rate limit** - Protect against brute force attacks
7. **CORS carefully** - Only allow trusted origins
8. **Use secure headers** - X-Frame-Options, X-Content-Type-Options, etc.

## Related Documentation

- [Routing](ROUTING.md) - Route definition
- [Models](MODELS.md) - Model authentication fields
- [Development](DEVELOPMENT.md) - Testing and debugging
