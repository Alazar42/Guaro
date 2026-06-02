# Dependency Injection

Guaro's dependency injection system enables flexible, testable code and automatic service management.

## Basic Service Registration

Register services for injection:

```python
from guaro import API
from guaro.dependency.injector import ServiceContainer

# Create container
container = ServiceContainer()

# Register simple service
class UserService:
    async def get_user(self, user_id: int):
        return {"id": user_id, "name": "John"}

container.register(UserService)

# Register singleton (reused instance)
container.register_singleton(UserService)
```

## Injecting Services

Services are automatically injected into routes:

```python
from guaro import Router

router = Router()

@router.get("/users/{user_id}/")
async def get_user(user_id: int, service: UserService) -> dict:
    """UserService is automatically injected"""
    return await service.get_user(user_id)

# Register container with API
api = API(database={...})
api.set_dependency_container(container)
api.register_router(router)
```

## Service Lifetimes

Control how long services exist:

```python
# Transient: New instance per request (default)
container.register(UserService)

# Singleton: One instance for entire app
container.register_singleton(UserService)

# Scoped: One instance per request scope
container.register_scoped(UserService)
```

## Service Factories

Use factory functions:

```python
def create_db_connection(config: dict):
    """Factory function"""
    return create_sql_connection(config["db_url"])

# Register factory
container.register_factory(
    "database",
    create_db_connection,
    config={"db_url": "sqlite:///app.db"}
)

# Use in routes
@router.get("/data/")
async def get_data(database) -> dict:
    result = await database.query("SELECT * FROM users")
    return result
```

## Service Dependencies

Services can depend on other services:

```python
class DatabaseService:
    def __init__(self):
        self.connection = None
    
    async def connect(self):
        self.connection = sqlite3.connect("app.db")

class UserRepository:
    def __init__(self, db: DatabaseService):
        self.db = db
    
    async def find_user(self, user_id: int):
        return await self.db.connection.query("...")

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    async def get_user(self, user_id: int):
        return await self.repo.find_user(user_id)

# Guaro automatically resolves the dependency chain
container.register(DatabaseService)
container.register(UserRepository)
container.register(UserService)
```

## Configuration Injection

Inject configuration:

```python
from dataclasses import dataclass

@dataclass
class AppConfig:
    debug: bool
    database_url: str
    secret_key: str

config = AppConfig(
    debug=True,
    database_url="sqlite:///app.db",
    secret_key="secret"
)

container.register_singleton(AppConfig, instance=config)

# Use in services
class AuthService:
    def __init__(self, config: AppConfig):
        self.secret = config.secret_key
    
    def create_token(self, user_id: int) -> str:
        import jwt
        return jwt.encode(
            {"user_id": user_id},
            self.secret,
            algorithm="HS256"
        )

container.register(AuthService)

# Use in routes
@router.post("/login/")
async def login(auth: AuthService) -> dict:
    token = auth.create_token(user_id=1)
    return {"token": token}
```

## Repository Pattern with DI

Improve data access layer:

```python
class BaseRepository:
    """Abstract repository"""
    pass

class UserRepository(BaseRepository):
    async def all(self):
        return await User.all()
    
    async def find(self, user_id: int):
        return await User.find(user_id)
    
    async def create(self, data: dict):
        user = User(**data)
        return await user.save()

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    async def list_users(self):
        return await self.repo.all()
    
    async def get_user(self, user_id: int):
        return await self.repo.find(user_id)

# Easy to test - inject mock repository
container.register(UserRepository)
container.register(UserService)

@router.get("/users/")
async def list_users(service: UserService) -> list:
    return await service.list_users()
```

## Request Scoped Services

Services that live for request duration:

```python
from contextvars import ContextVar

class RequestContext:
    """Scoped to single request"""
    def __init__(self):
        self.user = None
        self.request_id = None
        self.start_time = None

container.register_scoped(RequestContext)

@router.get("/me/")
async def get_current_user(context: RequestContext) -> dict:
    # Each request gets its own RequestContext instance
    return {"user": context.user, "request_id": context.request_id}
```

## Testing with Mock Services

Easily test with mocks:

```python
import pytest

class MockUserRepository:
    async def find(self, user_id: int):
        return {"id": user_id, "name": "Mock User"}

@pytest.mark.asyncio
async def test_get_user():
    # Create test container with mocks
    test_container = ServiceContainer()
    test_container.register(MockUserRepository)
    
    # Create service
    service = UserService(repo=MockUserRepository())
    
    # Test
    user = await service.get_user(1)
    assert user["name"] == "Mock User"
```

## Conditional Registration

Register services based on environment:

```python
import os

container = ServiceContainer()

if os.getenv("ENVIRONMENT") == "production":
    # Production database
    container.register(
        "database",
        ProductionDatabase
    )
else:
    # In-memory database for testing
    container.register(
        "database",
        MockDatabase
    )
```

## Multiple Implementations

Register multiple implementations:

```python
class CacheService:
    """Abstract cache"""
    pass

class RedisCache(CacheService):
    async def get(self, key: str):
        pass

class MemoryCache(CacheService):
    async def get(self, key: str):
        pass

# Register concrete implementation
if os.getenv("USE_REDIS"):
    container.register(CacheService, implementation=RedisCache)
else:
    container.register(CacheService, implementation=MemoryCache)
```

## Service Initialization

Initialize services on startup:

```python
class DatabaseService:
    async def startup(self):
        """Called when app starts"""
        self.connection = await create_connection()
    
    async def shutdown(self):
        """Called when app stops"""
        await self.connection.close()

# Register lifecycle hooks
api = API(database={...})
api.on_startup(container.get(DatabaseService).startup)
api.on_shutdown(container.get(DatabaseService).shutdown)
```

## Advanced Pattern: Service Locator

```python
class ServiceLocator:
    """Access any service without injection"""
    def __init__(self, container: ServiceContainer):
        self.container = container
    
    def get_service(self, service_type):
        return self.container.resolve(service_type)

container.register_singleton(ServiceLocator, instance=ServiceLocator(container))

# Use in routes
@router.get("/debug/")
async def debug_info(locator: ServiceLocator) -> dict:
    db = locator.get_service(DatabaseService)
    return {"status": "ok"}
```

## Best Practices

1. **Use abstract base classes** - Separate interface from implementation
2. **Prefer constructor injection** - Clear dependencies
3. **Keep services simple** - One responsibility per service
4. **Use singletons carefully** - Avoid shared state issues
5. **Test with mocks** - Inject test doubles
6. **Register early** - Setup DI before creating app
7. **Document dependencies** - Make relationships clear
8. **Use type hints** - Enable auto-resolution

## Common Patterns

**Repository Pattern:**
- Model → Repository (async data access) → Service → Route

**Service Layer:**
- Route → Service (business logic) → Repository (data) → Database

**Middleware Pattern:**
- Request → Middleware (DI-injected) → Route → Response

## Related Documentation

- [Models](MODELS.md) - Model structure
- [Routing](ROUTING.md) - Route definition
- [Development](DEVELOPMENT.md) - Testing patterns
