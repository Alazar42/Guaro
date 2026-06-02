# Model Definition Guide

Models are the core of Guaro applications. They define your data structure and automatically generate database schemas.

## Basic Model

```python
from guaro import Model

class User(Model):
    id: int
    name: str
    email: str
    age: int
```

## Supported Field Types

| Python Type | Database Type | Notes |
|------------|--------------|-------|
| `int` | INTEGER | Whole numbers |
| `str` | VARCHAR(255) | Text strings |
| `float` | FLOAT | Decimal numbers |
| `bool` | BOOLEAN | True/False values |
| `list["Model"]` | Relation | One-to-many relationship |
| `"Model"` | Relation | Many-to-one relationship |

## Field Relationships

### One-to-Many Relationship

```python
class User(Model):
    id: int
    name: str
    posts: list["Post"]  # User has many Posts

class Post(Model):
    id: int
    title: str
    content: str
    author: "User"  # Post has one User
```

Relation fields are NOT stored as database columns. They're resolved through queries.

## Primary Key

By default, the `id` field is the primary key:

```python
class User(Model):
    id: int  # ← Automatically marked as PRIMARY KEY
    name: str
```

## Model Methods

### Querying

```python
# Get all records
users = await User.all()

# Find by ID
user = await User.find(1)

# Find with multiple IDs
users = await User.find_multiple([1, 2, 3])
```

### Creating & Saving

```python
# Create and save
user = User(id=1, name="Alice", email="alice@example.com")
await user.save()

# Create without explicit ID (auto-generated)
user = User(name="Bob", email="bob@example.com")
returned_user = await user.save()  # Returns with generated ID
```

### Updating

```python
user = await User.find(1)
user.name = "Updated Name"
await user.save()
```

### Deleting

```python
user = await User.find(1)
await user.delete()

# Or delete by ID
await User.delete(1)
```

## Registering Models

Models must be registered with the API:

```python
from guaro import API
from models import User, Post

api = API(database={...})

api.register_model(User)
api.register_model(Post)
```

## Type Hints & Validation

Guaro uses Python type hints for validation and documentation:

```python
class Product(Model):
    id: int
    name: str
    price: float
    in_stock: bool
    tags: list[str]  # Lists create VARCHAR columns

# Type hints enable:
# - IDE autocomplete
# - API documentation generation
# - Data validation
# - Better error messages
```

## Auto-Migrate

When `auto_migrate=True`, Guaro automatically:

✓ Creates tables on first run
✓ Adds new columns when model fields change
✓ Preserves existing data (never destructive)
✓ Works across all database types

```python
api = API(database={
    "auto_migrate": True,  # Default
    ...
})
```

See [Migration Guide](MIGRATION.md) for details.

## Advanced: Custom Model Behavior

You can extend models with methods:

```python
class User(Model):
    id: int
    name: str
    email: str
    
    async def get_posts(self):
        """Get posts by this user"""
        from models import Post
        return await Post.find_by_author(self.id)
    
    async def send_email(self, subject: str, body: str):
        """Send email to user"""
        # Your email logic here
        pass
```

## Model Metadata

Access model information:

```python
class User(Model):
    id: int
    name: str

# Get model metadata
metadata = User._metadata()
print(metadata.name)  # "User"
print(metadata.primary_key)  # "id"
print(metadata.fields.keys())  # dict_keys(['id', 'name'])
```

## Next Steps

- [Routing](ROUTING.md) - Create API endpoints
- [Database Configuration](DATABASE.md) - Connect to different databases
- [Auto-Migration](MIGRATION.md) - Database schema management
