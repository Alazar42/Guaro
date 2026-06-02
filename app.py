from guaro import API

from models.post import Post
from models.user import User
from routes.posts import router as posts_router
from routes.users import router as users_router


api = API()

api.register_model(User)
api.register_model(Post)

api.register_router(users_router)
api.register_router(posts_router)


if __name__ == "__main__":
    api.run(mode="hybrid")
