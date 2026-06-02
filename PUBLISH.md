# Publishing Guaro to PyPI

This guide explains how to publish new versions of Guaro to PyPI.

## Prerequisites

### One-time Setup

1. **Create PyPI account**: https://pypi.org/account/register/
2. **Get API token**: https://pypi.org/manage/account/token/
3. **Configure GitHub Secret**:
   - Go to Repository Settings → Secrets and variables → Actions
   - Add `PYPI_API_TOKEN` with your token value

## Versioning

Guaro follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR**: New features, backward compatible (e.g., 1.0.0 → 1.1.0)
- **PATCH**: Bug fixes (e.g., 1.0.0 → 1.0.1)

## Pre-Release Checklist

Before publishing a new version:

```bash
# 1. Update version in pyproject.toml
nano pyproject.toml
# Change: version = "0.1.0" → version = "0.2.0"

# 2. Run tests locally
pytest

# 3. Check that it builds
python -m build

# 4. Update CHANGELOG.md
nano CHANGELOG.md
# Add new version section with changes

# 5. Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to 0.2.0"

# 6. Push to main
git push origin main
```

## Publishing Methods

### Method 1: GitHub Release (Recommended)

Automatic via GitHub Actions:

```bash
# 1. Create a tag
git tag v0.2.0

# 2. Push tag to trigger workflow
git push origin v0.2.0

# 3. Create GitHub Release
# - Go to https://github.com/Alazar42/Guaro/releases/new
# - Select tag v0.2.0
# - Add release notes (copy from CHANGELOG.md)
# - Click "Publish release"

# The GitHub Actions workflow will automatically:
# - Build the package
# - Publish to PyPI
# - Verify the installation
```

### Method 2: Manual Publishing

For advanced use cases:

```bash
# 1. Install build tools
pip install build twine

# 2. Clean previous builds
rm -rf build/ dist/

# 3. Build package
python -m build

# 4. Check distribution
twine check dist/*

# 5. Upload to PyPI (interactive)
twine upload dist/*
# OR upload to TestPyPI first
twine upload --repository testpypi dist/*
```

## Testing Installation

After publishing:

```bash
# Wait 1-2 minutes for PyPI to index

# Test pip install
pip install guaro

# Test specific version
pip install guaro==0.2.0

# Test optional dependencies
pip install "guaro[all-databases]"
pip install "guaro[mysql]"
pip install "guaro[postgres]"
```

## Troubleshooting

### Build Fails

```bash
# Clean build files and retry
rm -rf build/ dist/ *.egg-info
python -m build
```

### Version Already Exists on PyPI

This happens when you try to republish the same version. Either:
- Increment version number and republish
- Use `twine upload --skip-existing dist/*` to skip

### GitHub Action Fails

Check the workflow run:
1. Go to Actions tab
2. Click on the failed workflow
3. View logs for error messages

Common issues:
- `PYPI_API_TOKEN` not set in Secrets → Configure it in Settings
- Incorrect token format → Regenerate token on PyPI
- Network issues → Try again in a few minutes

## Yanking a Release

If you need to remove a version from PyPI:

```bash
# Via PyPI web interface:
# https://pypi.org/project/guaro/
# Go to Release History → Click version → "Yank this Release"

# This prevents new installations but keeps old installations working
```

## Documentation

After publishing, update:

- `docs/INSTALLATION.md` - Include new version in examples
- `CHANGELOG.md` - Ensure it matches the release notes
- GitHub README - Update links to stable version

## Release Checklist

- [ ] Version updated in `pyproject.toml`
- [ ] `CHANGELOG.md` updated with changes
- [ ] All tests passing locally (`pytest`)
- [ ] Package builds successfully (`python -m build`)
- [ ] Git tag created (`git tag v0.2.0`)
- [ ] Tag pushed (`git push origin v0.2.0`)
- [ ] GitHub Release published
- [ ] PyPI email notification received
- [ ] Installation tested (`pip install guaro`)
- [ ] Documentation links verified

## Automating the Release

For more automation, consider GitHub Actions workflow that:

1. Runs tests on all push
2. Automatically publishes on release
3. Sends notifications to Discord/Slack

See `.github/workflows/publish.yml` for current setup.

## Support

For issues with PyPI publishing:
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
