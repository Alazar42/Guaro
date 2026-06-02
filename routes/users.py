from guaro import Router
from middleware.auth import require_auth
from models.user import User


router = Router(prefix="/users")


@router.get("/")
@require_auth
def get_users() -> list[User]:
    return User.all()


@router.get("/{id}")
@require_auth
def get_user(id: int) -> User | None:
    return User.find(id)
