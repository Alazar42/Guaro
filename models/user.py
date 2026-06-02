from guaro import Model


class User(Model):
    id: int
    name: str
    email: str
    posts: list["Post"]
