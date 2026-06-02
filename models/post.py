from guaro import Model


class Post(Model):
    id: int
    title: str
    body: str
    author: "User"
