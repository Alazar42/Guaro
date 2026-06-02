"""
Example 2: Inline Configuration

Convenient for quick prototypes — database config defined directly in the app file
"""

from guaro import API, DatabaseEngine, Model, Router

# Define models
class User(Model):
    id: int
    name: str
    email: str


# Define routes
router = Router(prefix="/users")

@router.get("/")
def list_users() -> list[User]:
    return []

@router.get("/{id}")
def get_user(id: int) -> User | None:
    return None


# Bootstrap with inline configuration
if __name__ == "__main__":
    api = API(
        database={
            "url": "sqlite+aiosqlite:///local_test.db",
            "engine": DatabaseEngine.SQLITE,
            "auto_migrate": True,
            "pool_size": 2,
            "echo": True,
        }
    )
    api.register_model(User)
    api.register_router(router)
    api.run()  # Open http://127.0.0.1:8000/docs for Swagger UI
