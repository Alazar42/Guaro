"""
Example 1: Default Configuration (No Config File)

Lowest-friction startup — Guaro automatically creates a SQLite database in guaro.db
"""

from guaro import API, Model, Router

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


# Bootstrap with zero database configuration
# Guaro automatically uses: sqlite+aiosqlite:///guaro.db
if __name__ == "__main__":
    api = API()
    api.register_model(User)
    api.register_router(router)
    api.run()  # Open http://127.0.0.1:8000/docs for Swagger UI
