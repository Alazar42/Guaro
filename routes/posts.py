from guaro import Router
from middleware.auth import require_auth
from models.post import Post


router = Router(prefix="/posts")


@router.get("/")
@require_auth
def get_posts() -> list[Post]:
    return Post.all()
