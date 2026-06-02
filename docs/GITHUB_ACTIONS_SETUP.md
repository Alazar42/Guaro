# GitHub Actions Setup

Before the workflows can publish to PyPI, you need to configure GitHub trusted publishing.

## Quick Setup (5 minutes)

### Step 1: Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Create account with email
3. Verify email address

### Step 2: Add a Trusted Publisher on PyPI

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Set the fields to:
   - PyPI project name: `guaro`
   - Owner: `Alazar42`
   - Repository name: `Guaro`
   - Workflow name: `workflow.yml`
   - Environment name: `pypi`
4. Save the publisher

### Step 3: Add the GitHub Environment

1. Go to your repository: https://github.com/Alazar42/Guaro
2. Click "Settings"
3. In left menu, click "Environments"
4. Create or select an environment named `pypi`
5. Save it; no secret is required for trusted publishing

That completes the setup.

## Verify It Works

### Test 1: Check Secret is Stored

1. Go to Settings → Secrets and variables → Actions
2. You should see `pypi` listed.

### Test 2: Manual Workflow Trigger

1. Go to "Actions" tab
2. Click "Publish to PyPI"
3. Click "Run workflow"
4. Select branch: `main`
5. Click "Run workflow"

**Expected result:** Workflow runs and publishes current version to PyPI

### Test 3: Install from PyPI

```bash
pip install guaro
python -c "import guaro; print(guaro.__version__)"
```

## Environment Variables in Workflows

### Available in CI Workflow

```yaml
${{ github.ref }}           # git reference (branch/tag)
${{ github.event_name }}    # push, pull_request, release
${{ github.actor }}         # who triggered it
${{ github.run_id }}        # unique run ID
```

### Available in Publish Workflow

```yaml
${{ github.event_name }}    # release or workflow_dispatch
```

Trusted publishing has the following properties:
- Hidden in logs
- Encrypted at rest
- Only accessible in workflows
- Visible only to creators

## Troubleshooting

### "Error 403: Invalid credentials"

- Trusted publisher not configured → Add it on PyPI
- Repository owner/name mismatch → Must be `Alazar42/Guaro`
- Workflow name mismatch → Must be `workflow.yml`

### "Secret not found"

- Not added to repository → Add to Settings → Secrets
- Added to wrong location → Must be at repository level (not organization)
- Try pushing again → Sometimes needs refresh

### "Workflow not running"

- Check if workflow file exists: `.github/workflows/ci.yml` and `workflow.yml`
- Check if file has proper YAML syntax
- Check GitHub Actions are enabled: Settings → Actions → General

## File Structure

Your workflows should look like:

```
.github/
├── workflows/
│   ├── ci.yml         Tests on every push
│   └── workflow.yml   Publishes on release
```

## Next Steps

1. Create a PyPI account.
2. Add a trusted publisher on PyPI.
3. Configure the GitHub environment `pypi`.
4. Create a release to test.
5. Verify `pip install guaro` works.

## Security Notes

- **Never commit tokens** to git
- **Always use GitHub Secrets** for sensitive data
- **Scope tokens** - create separate tokens for different purposes
- **Rotate tokens** - regenerate periodically
- **Review logs** - check workflows for accidental leaks

## Support

- [GitHub OIDC Trusted Publishing](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

Go to https://pypi.org/manage/account/publishing/ and add the trusted publisher.
