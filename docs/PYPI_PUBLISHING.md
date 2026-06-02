# Publishing Guaro to PyPI - Quick Start

Your package is built and ready! Follow these steps to publish:

## Step 1: Create PyPI Account (if you don't have one)

1. Go to https://pypi.org/account/register/
2. Create your account
3. Verify your email

## Step 2: Create API Token

1. Go to https://pypi.org/account/token/
2. Click "Add API token"
3. Name: `guaro-publishing`
4. Scope: "Entire account"
5. Click "Create token" and **save it securely**

## Step 3: Configure Your System

Option A: Interactive (will prompt for token each time)
```bash
pip install --upgrade twine
twine upload dist/guaro-*.whl dist/guaro-*.tar.gz
# When prompted, enter your username (__token__) and password (the token)
```

Option B: Create .pypirc file for automated authentication

Create `~/.pypirc` (Linux/Mac) or `%APPDATA%\pip\pip.conf` (Windows):

```ini
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = pypi-Your-Token-Here-From-Step-2
```

Then upload with:
```bash
twine upload dist/guaro-*.whl dist/guaro-*.tar.gz
```

## Step 4: Verify Installation

After uploading (wait 1-2 minutes for PyPI to index):

```bash
# Create a new virtual environment to test
python -m venv test_install
source test_install/bin/activate  # or test_install\Scripts\activate on Windows

# Install from PyPI
pip install guaro

# Test it works
python -c "import guaro; print(f'Guaro {guaro.__version__} installed successfully!')"
```

## Troubleshooting

**"HTTP 403"** - Token is invalid or expired
- Generate a new token at https://pypi.org/account/token/

**"Already exists"** - Version 0.1.0 already on PyPI
- Update version in `pyproject.toml` to `0.1.1`
- Rebuild: `python -m build`
- Upload new version

**"No module named 'guaro'"** - Package not indexed yet
- Wait 2-3 minutes and try again
- Check https://pypi.org/project/guaro/

## Your Package Files

Ready to upload:
- `dist/guaro-0.1.0-py3-none-any.whl` (wheel - recommended)
- `dist/guaro-0.1.0.tar.gz` (source distribution)

**Next Steps After Publishing:**

1. Git commit your updated files:
   ```bash
   git add -A
   git commit -m "Update repo links and prepare for PyPI publishing"
   git push origin main
   ```

2. Create a GitHub Release:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   # Then go to https://github.com/Alazar42/Guaro/releases/new
   ```

3. Update the README to link to PyPI page

Good luck! 🚀
