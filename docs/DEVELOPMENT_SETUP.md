# Local Development Setup

This guide covers setting up Guaro for local development from source.

## Prerequisites

- Python 3.11 or higher
- Git
- pip (usually included with Python)

## Step 1: Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/Alazar42/Guaro.git
cd Guaro

# Or if using SSH
git clone git@github.com:Alazar42/Guaro.git
cd Guaro
```

## Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate

# On Windows (Command Prompt):
.venv\Scripts\activate

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

Verify activation - prompt should show `(.venv)` prefix.

## Step 3: Install Guaro in Development Mode

```bash
# Install with all optional dependencies for development
pip install -e ".[all-databases,dev]"

# Or install step by step
pip install -e .              # Core
pip install -e ".[sqlite]"    # SQLite
pip install -e ".[postgres]"  # PostgreSQL
pip install -e ".[mysql]"     # MySQL
pip install -e ".[mongodb]"   # MongoDB
pip install -e ".[dev]"       # Development tools
```

This installs Guaro in "editable" mode, meaning changes to source files are reflected immediately without reinstalling.

## Step 4: Verify Installation

```bash
# Check version
python -c "import guaro; print(f'Guaro {guaro.__version__}')"

# List installed packages
pip list | grep guaro

# Run basic import test
python -c "from guaro import API, Model, Router; print('✓ All imports working')"
```

## Step 5: Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=guaro

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

## Development Workflow

### Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make your changes to files in `guaro/`

3. Run tests to verify:
   ```bash
   pytest
   ```

4. Check code style:
   ```bash
   black --check guaro/
   pylint guaro/
   mypy guaro/
   ```

### Running Locally Built Examples

Create a test file `test_local.py`:

```python
from guaro import API, Model, Router

class User(Model):
    id: int
    name: str
    email: str

api = API(database={
    "engine": "sqlite",
    "url": "sqlite+aiosqlite:///test.db",
})

api.register_model(User)

router = Router(prefix="/users")

@router.get("/")
async def list_users() -> list[User]:
    return await User.all()

if __name__ == "__main__":
    api.run(mode="hybrid")
```

Run it:

```bash
python test_local.py
```

### Viewing Changes in Real-time

Since Guaro is installed in editable mode (`-e` flag), changes are reflected immediately. You don't need to reinstall!

```bash
# Make change to guaro/app.py
nano guaro/app.py

# Your change is available immediately in any new Python process
python test_local.py
```

## Common Development Tasks

### Adding a New Feature

```bash
# 1. Create feature branch
git checkout -b feature/field-validation

# 2. Make changes
# Edit guaro/models/base.py

# 3. Write tests
# Add tests/test_field_validation.py

# 4. Run tests
pytest tests/test_field_validation.py

# 5. Commit
git add .
git commit -m "Add field validation support"

# 6. Push and create PR
git push origin feature/field-validation
```

### Debugging

```bash
# Add debug prints to code
print(f"Debug: {variable}")

# Or use Python debugger
import pdb; pdb.set_trace()

# When it breaks, use:
# l - list code
# n - next line
# s - step into
# c - continue
# p variable - print variable
# h - help
```

### Performance Profiling

```bash
# Use cProfile to profile code
python -m cProfile -s cumulative test_local.py

# Or import in your code:
import cProfile
cProfile.run('my_function()')
```

## Environment Setup

### Using Environment Variables

Create `.env.local`:

```bash
DATABASE_URL=sqlite+aiosqlite:///dev.db
AUTO_MIGRATE=true
DEBUG=true
LOG_LEVEL=DEBUG
```

Load in your code:

```python
import os
from dotenv import load_dotenv

load_dotenv(".env.local")

database_url = os.getenv("DATABASE_URL")
```

Install python-dotenv:

```bash
pip install python-dotenv
```

## Project Structure

```
Guaro/
├── guaro/              # Main package
│   ├── __init__.py    # Package exports
│   ├── app.py         # API class
│   ├── config/        # Configuration
│   ├── core/          # Core logic
│   ├── db/            # Database adapters
│   ├── models/        # Model definitions
│   ├── routing/       # Routing
│   └── ...
├── docs/              # Documentation
├── tests/             # Test suite
├── pyproject.toml     # Package configuration
├── CHANGELOG.md       # Version history
├── CONTRIBUTING.md    # Contribution guide
└── README.md          # Project overview
```

## Troubleshooting

### Import Errors

```bash
# Reinstall in editable mode
pip uninstall guaro -y
pip install -e ".[all-databases,dev]"

# Verify
python -c "from guaro import API; print('OK')"
```

### Test Failures

```bash
# Run with verbose output
pytest -vv

# Run specific test with print output
pytest -s tests/test_models.py::test_name

# Check for missing dependencies
pip list
```

### Database Issues

```bash
# Clean up test databases
rm test.db test_migration.db

# Recreate with auto-migrate
python test_local.py
```

## Getting Help

- Check [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines
- Read [Development Guide](../docs/DEVELOPMENT.md) for architecture
- Look at [existing tests](../tests/) for examples
- Open an issue on GitHub for questions

## Next Steps

1. Read [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
2. Pick an issue labeled "good first issue"
3. Create a feature branch and submit a PR
4. See [PUBLISH.md](../PUBLISH.md) if publishing to PyPI

---

Happy coding! 🚀
