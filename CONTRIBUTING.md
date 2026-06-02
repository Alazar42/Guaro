# Contributing to Guaro

This document provides guidelines for contributing to Guaro.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally: `git clone https://github.com/Alazar42/Guaro.git`
3. **Set up development environment** - See [Development Guide](docs/DEVELOPMENT.md)
4. **Create a branch** for your feature: `git checkout -b feature/my-feature`

## Development Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

See [Development Guide](docs/DEVELOPMENT.md) for more details.

## Code Guidelines

### Style

- Follow PEP 8 with Black formatter
- Use type hints for all functions
- Document complex logic with comments
- Keep functions focused and testable

### Naming

- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants
- Prefix private methods with `_`

### Example

```python
from typing import Optional

class UserRepository:
    """Repository for user data access."""
    
    DEFAULT_LIMIT = 100
    
    async def find_by_email(
        self, 
        email: str,
        limit: Optional[int] = None
    ) -> Optional[dict]:
        """Find user by email address.
        
        Args:
            email: User email to search for
            limit: Maximum results (defaults to DEFAULT_LIMIT)
        
        Returns:
            User dict if found, None otherwise
        """
        effective_limit = limit or self.DEFAULT_LIMIT
        return await self._query(f"SELECT * FROM users WHERE email = ?", email)
    
    async def _query(self, sql: str, *args):
        """Private method for database queries."""
        pass
```

## Testing

All contributions must include tests.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=guaro

# Run specific test file
pytest tests/test_models.py

# Run specific test
pytest tests/test_models.py::test_model_creation
```

### Writing Tests

```python
import pytest
from guaro import Model, API

class TestUserModel:
    """Tests for User model"""
    
    @pytest.mark.asyncio
    async def test_user_creation(self):
        """Test creating a new user."""
        user = User(name="John", email="john@example.com")
        await user.save()
        
        found = await User.find(user.id)
        assert found.name == "John"
    
    @pytest.mark.asyncio
    async def test_user_all(self):
        """Test fetching all users."""
        # Setup
        await User(name="User1", email="user1@example.com").save()
        await User(name="User2", email="user2@example.com").save()
        
        # Test
        users = await User.all()
        
        # Assert
        assert len(users) >= 2
```

## Commit Messages

Write clear commit messages:

```
Short description (50 chars or less)

Longer description explaining the change, why it was made,
and any important context. Wrap at 72 characters.

Fixes #123
```

### Example

```
Add auto_migrate flag to skip schema creation

Previously, Guaro always created tables on startup.
This adds a config flag to skip auto-migration when
deploying with pre-created schemas.

Fixes #123
Closes #456
```

## Pull Requests

### Before Submitting

1. **Sync with main** - `git pull origin main`
2. **Run tests** - `pytest`
3. **Check coverage** - `pytest --cov=guaro`
4. **Format code** - `black guaro/`
5. **Lint code** - `pylint guaro/`

### PR Description

Include:

- **What**: Description of changes
- **Why**: Motivation and problem solved
- **How**: Implementation approach
- **Tests**: How to verify the changes work
- **Docs**: Any documentation updates needed

### Example PR Template

```markdown
## Description

Add configuration option to disable auto-migration for pre-created schemas.

## Problem

Deploying to production with existing databases fails if auto_migrate=True
because it attempts to create already-existing tables, potentially causing
conflicts or downtime.

## Solution

Add `auto_migrate` config flag (defaults to True for backward compatibility).
When False, Guaro skips the metadata.create_all() call during startup.

## Testing

- [x] Tested with SQLite database
- [x] Tested with PostgreSQL
- [x] Tested with MySQL
- [x] Verified existing data is not affected
- [x] Added unit tests

## Related Issues

Fixes #123
Closes #456

## Checklist

- [x] Tests pass
- [x] Docs updated
- [x] Commits are descriptive
- [x] No breaking changes (or version bump planned)
```

## Documentation

When adding features, update relevant docs:

- **New database support**: Update [DATABASE.md](docs/DATABASE.md)
- **New query features**: Update [MODELS.md](docs/MODELS.md)
- **New middleware**: Update [MIDDLEWARE.md](docs/MIDDLEWARE.md)
- **Breaking changes**: Update [CHANGELOG.md](CHANGELOG.md)
- **Internal changes**: Update [Development Guide](docs/DEVELOPMENT.md)

## Reporting Bugs

Use GitHub Issues to report bugs.

### Bug Report Template

```markdown
## Description

A clear description of what the bug is.

## Steps to Reproduce

1. Create a model with...
2. Call route with...
3. Error occurs when...

## Expected Behavior

What should happen instead?

## Actual Behavior

What actually happened?

## Environment

- Python: 3.11.8
- Guaro: 0.1.0
- Database: MySQL 8.0
- OS: Windows 11

## Error Log

```
[Paste error trace here]
```

## Additional Context

Any other information that might help?
```

## Feature Requests

Have an idea? Create a GitHub Issue!

### Feature Request Template

```markdown
## Description

Clear description of the feature.

## Motivation

Why would this be useful?

## Proposed Solution

How should it work?

## Alternatives

Any other approaches considered?

## Additional Context

Examples, links, related issues?
```

## Code Review

All PRs require at least one code review before merging.

### Review Guidelines

- **Be constructive** - Focus on code, not author
- **Ask questions** - Help others learn
- **Suggest improvements** - Share knowledge
- **Approve when satisfied** - Don't block unnecessarily

## Architecture Decisions

For significant changes, open an issue first for discussion.

### RFCs (Request for Comments)

For major features:

1. Create issue with Design Proposal
2. Discuss approach with maintainers
3. Build consensus in community
4. Implement with feedback
5. Document decision

## Project Structure

Key directories:

- `guaro/` - Main framework code
- `docs/` - User documentation
- `tests/` - Test suite
- `examples/` - Example projects
- `.gitignore` - Git configuration
- `pyproject.toml` - Package configuration

## Getting Help

- **Questions**: GitHub Discussions
- **Issues**: GitHub Issues
- **Design**: Create an RFC issue
- **Real-time**: GitHub Issues

## License

By contributing, you agree your work will be licensed under the MIT License.

## FAQ

**Q: How do I get started?**
A: See Development Guide, fork the repo, and create a feature branch.

**Q: What should I work on?**
A: Check GitHub Issues for "good first issue" or pick something you need!

**Q: How long do reviews take?**
A: Usually 1-3 days. Complex changes may take longer.

**Q: Can I commit directly?**
A: Only maintainers can commit to main. Create PRs for all contributions.

**Q: What if my PR gets rejected?**
A: Get feedback and iterate! Most PRs have feedback before merging.

---

## Thank You!

Thank you for contributing to Guaro.
