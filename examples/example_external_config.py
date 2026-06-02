"""
Example 3: External Configuration (RECOMMENDED FOR PRODUCTION)

Production-grade pattern — configuration is isolated in a separate module,
can be environment-driven, and does not mix with application bootstrap code.

This example assumes a config.py file in the project root:

    from guaro import DatabaseEngine

    prod_config = {
        "url": "postgresql+asyncpg://user:pass@db.company.com/guaro_prod",
        "engine": DatabaseEngine.POSTGRESQL,
        "auto_migrate": False,
        "pool_size": 20,
    }

    database_config = prod_config  # or load from os.getenv("ENVIRONMENT")
"""

from guaro import API, Model, Router

# Import external database configuration
# In production, this can be environment-driven:
#   import os
#   env = os.getenv("ENVIRONMENT", "dev")
#   if env == "prod":
#       from config import prod_config as database_config
#   elif env == "staging":
#       from config import staging_config as database_config
#   else:
#       from config import dev_config as database_config

try:
    from config import database_config  # Located in project root
except ImportError:
    # Fallback if config.py doesn't exist
    database_config = None

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


# Bootstrap with external configuration
if __name__ == "__main__":
    api = API(database=database_config)
    api.register_model(User)
    api.register_router(router)
    api.run()  # Open http://127.0.0.1:8000/docs for Swagger UI
