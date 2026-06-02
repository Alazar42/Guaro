# GraphQL Guide

Guaro automatically exposes your models and routes through GraphQL using Strawberry.

## Automatic Schema Generation

Your models automatically become GraphQL queries:

```python
from guaro import API, Model, DatabaseEngine

class User(Model):
    id: int
    name: str
    email: str

class Post(Model):
    id: int
    title: str
    content: str

api = API(database={...})
api.register_model(User)
api.register_model(Post)

# GraphQL schema automatically generated!
# Access at http://localhost:8000/graphql
```

## Available Queries

Once models are registered:

```graphql
query {
  users {
    id
    name
    email
  }
}

query {
  posts {
    id
    title
    content
  }
}

query {
  user(id: 1) {
    id
    name
    email
  }
}
```

## Field Selection

Request only needed fields for better performance:

```graphql
query {
  users {
    id
    name
  }
}
```

## Relations

Query related data in one request:

```graphql
query {
  users {
    id
    name
    posts {
      id
      title
    }
  }
}
```

## Mutations

GraphQL mutations are automatically created for create/update/delete:

```graphql
mutation {
  createUser(name: "Alice", email: "alice@example.com") {
    id
    name
    email
  }
}

mutation {
  updateUser(id: 1, name: "Alice Updated") {
    id
    name
  }
}

mutation {
  deleteUser(id: 1)
}
```

## Using REST Routes in GraphQL

REST routes can be queried through GraphQL when registered:

```python
from guaro import Router

router = Router()

@router.get("/greeting/")
async def greeting(name: str) -> dict:
    return {"greeting": f"Hello, {name}!"}

api.register_router(router)

# Now in GraphQL:
# query {
#   greeting(name: "Alice")
# }
```

## Playground

GraphQL Playground is available at:
- Development: http://localhost:8000/graphql

### Example Queries

**List all users:**
```graphql
query ListUsers {
  users {
    id
    name
    email
  }
}
```

**Get specific user with posts:**
```graphql
query GetUserWithPosts {
  user(id: 1) {
    id
    name
    posts {
      id
      title
      content
    }
  }
}
```

**Create and return:**
```graphql
mutation CreateUserAndGetPost {
  createUser(name: "Bob", email: "bob@example.com") {
    id
    name
  }
}
```

## Bypassing REST Decorators in GraphQL

By default, GraphQL exposes all models. To restrict access:

```python
# Use middleware to check GraphQL context
from guaro.execution.context import ExecutionContext

async def graphql_auth_middleware(context: ExecutionContext):
    if context.transport == "graphql":
        # Check authentication for GraphQL separately
        if not context.user:
            # Handle auth
            pass
```

## Performance: N+1 Query Prevention

Guaro includes automatic dataloader support:

```python
# Backend optimizes related queries automatically
# One query for users, one batch query for related posts
# NOT N queries (one per user)

query {
  users {
    id
    name
    posts {      # This doesn't create N queries!
      id
      title
    }
  }
}
```

## Next Steps

- [REST Routing](ROUTING.md) - Learn REST endpoints
- [Models](MODELS.md) - Define models better
- [Database](DATABASE.md) - Configure database
