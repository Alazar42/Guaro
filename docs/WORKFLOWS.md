# GitHub Actions Workflows

Guaro uses GitHub Actions for automated testing, building, and publishing. This guide explains each workflow.

## Available Workflows

### 1. CI (ci.yml) - Runs on Every Push

**Triggers:**
- Every push to `main` or `develop` branches
- Every pull request to `main` or `develop`

**What it does:**
- Tests code with Python 3.11, 3.12, and 3.13
- Runs linters (pylint, black, mypy)
- Runs test suite (pytest)
- Builds distribution packages
- Checks security with Bandit

**Status:** Shows in branch protection and PR checks

```
Push to main
    ↓
Run tests on Python 3.11/3.12/3.13
    ↓
Check code quality (pylint, black, mypy)
    ↓
Build distribution
    ↓
Check security
```

### 2. Publish (publish.yml) - Publishes to PyPI

**Triggers:**
- GitHub Release published
- Manual trigger via workflow dispatch

**What it does:**
- Builds distribution packages
- Publishes to PyPI
- Verifies installation works

**How to use:**

Option A: Create a GitHub Release (Recommended):
```bash
# Tag the commit
git tag v0.1.0
git push origin v0.1.0

# Then go to: https://github.com/Alazar42/Guaro/releases/new
# - Select tag v0.1.0
# - Add title and description
# - Click "Publish release"
# → Workflow automatically runs and publishes to PyPI
```

Option B: Manual trigger:
```
Go to: Actions → Publish to PyPI → Run workflow → main branch → Run
```

```
GitHub Release created
    ↓
Build distribution
    ↓
Publish to PyPI
    ↓
Verify installation
```

## Setup Requirements

### 1. PyPI API Token (Required for Publishing)

1. Create account at https://pypi.org/account/register/
2. Go to https://pypi.org/account/token/
3. Create new token named "guaro-github-actions"
4. Copy token
5. Add to GitHub: Repository Settings → Secrets and variables → Actions
   - Secret name: `PYPI_API_TOKEN`
   - Secret value: (paste token)

### 2. Branch Protection (Recommended)

To require CI passes before merging:

1. Go to: Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Require status checks to pass: Select "ci.yml - test"
4. Save

## Monitoring Workflows

### View Status

1. Go to repository
2. Click "Actions" tab
3. See all workflow runs
4. Click run for details

### See Logs

1. Click workflow run
2. Click job name (test, build, etc.)
3. Click step to expand
4. Review output

## Troubleshooting

### CI fails on tests

Check logs:
1. Actions → failed workflow
2. Click "test" job
3. Look for error in "Run tests" step

**Common causes:**
- Missing dependencies → Update `pyproject.toml [dev]`
- Import errors → Check test files
- Database test issues → See test setup

### Publish fails

Check logs for error:
1. Actions → failed workflow
2. Click "build-and-publish" job
3. Check error in logs

**Common causes:**
- `PYPI_API_TOKEN` not set → Add to Secrets
- Token expired → Generate new token on PyPI
- Version already published → Increment version number
- Missing metadata → Check `pyproject.toml`

### Workflows not running

**Check:**
- Is commit on `main` or `develop` branch?
- Are workflows enabled? (Settings → Actions)
- Are branch protection rules too strict?

## Creating a Release

### Manual Process

```bash
# 1. Make sure main is up to date
git checkout main
git pull origin main

# 2. Update version in pyproject.toml
# Change: version = "0.1.0" → version = "0.2.0"
nano pyproject.toml

# 3. Update CHANGELOG.md
nano CHANGELOG.md

# 4. Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "Release v0.2.0"
git push origin main

# 5. Create and push tag
git tag v0.2.0
git push origin v0.2.0

# 6. Create GitHub Release
# Go to: https://github.com/Alazar42/Guaro/releases/new
# - Select tag v0.2.0
# - Use version number as title
# - Copy CHANGELOG section as description
# - Click "Publish release"
```

Workflow automatically publishes to PyPI!

## Version Numbering

Use [Semantic Versioning](https://semver.org/):

- **0.1.0** → Initial release
- **0.1.1** → Patch fix (bug)
- **0.2.0** → Minor feature (backward compatible)
- **1.0.0** → Major release (breaking changes)

## Tips

### Run CI locally before push

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run linters
black guaro/
pylint guaro/
mypy guaro/

# Run tests
pytest
```

### Skip CI (not recommended)

```bash
# Add [skip ci] to commit message
git commit -m "Update docs [skip ci]"
```

### Test workflow syntax

```bash
# Install act locally (optional)
# https://github.com/nektos/act

# Run workflow locally
act -j test
```

### View workflow file differences

```bash
# Check syntax
python -m yaml .github/workflows/ci.yml
```

## Related Documentation

- [PUBLISH.md](../PUBLISH.md) - Publishing guide
- [PYPI_PUBLISHING.md](../PYPI_PUBLISHING.md) - PyPI setup
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
