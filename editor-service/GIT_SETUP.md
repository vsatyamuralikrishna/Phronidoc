# Git Integration Setup

The editor service automatically commits and pushes changes to Git. Here's how to set it up:

## Prerequisites

1. **Git Repository**: Your documentation folder must be a git repository
   ```bash
   cd /path/to/hpc-documentation
   git init  # If not already initialized
   ```

2. **Git Configuration**: Set up your git user info
   ```bash
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

3. **Remote Repository**: Add your GitHub remote
   ```bash
   git remote add origin https://github.com/your-org/your-repo.git
   # Or if using SSH:
   git remote add origin git@github.com:your-org/your-repo.git
   ```

## Authentication

### Option 1: Personal Access Token (Recommended)

1. Create a GitHub Personal Access Token:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token with `repo` scope
   - Copy the token

2. Use token in remote URL:
   ```bash
   git remote set-url origin https://YOUR_TOKEN@github.com/your-org/your-repo.git
   ```

### Option 2: SSH Keys

1. Generate SSH key (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -C "your.email@example.com"
   ```

2. Add to SSH agent:
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

3. Add public key to GitHub:
   - Copy `~/.ssh/id_ed25519.pub`
   - Add to GitHub Settings → SSH and GPG keys

4. Use SSH remote:
   ```bash
   git remote set-url origin git@github.com:your-org/your-repo.git
   ```

### Option 3: Credential Helper

For HTTPS, you can use credential helper:
```bash
git config --global credential.helper store
# Then do one manual push to store credentials
```

## How It Works

When you create, update, or delete a document:

1. **File Operation**: The file is created/updated/deleted
2. **Git Add**: The file is staged (`git add`)
3. **Git Commit**: A commit is created with message:
   - Create: `docs: Add path/to/file.md`
   - Update: `docs: Update path/to/file.md`
   - Delete: `docs: Delete path/to/file.md`
4. **Git Push**: Changes are pushed to the remote repository

## Custom Commit Messages

You can provide custom commit messages in the API:

```javascript
// When creating/updating
{
  "path": "engineering/new-page.md",
  "content": "# Content",
  "commit_message": "Add new engineering documentation page",
  "push": true
}
```

## Troubleshooting

### "Not a git repository" Error

Make sure you're in a git repository:
```bash
cd /path/to/hpc-documentation
git status  # Should show git status, not an error
```

### Push Fails - Authentication

Check your remote URL:
```bash
git remote -v
```

If using HTTPS, ensure you have credentials configured.

### Push Fails - No Upstream Branch

Set upstream branch:
```bash
git branch --set-upstream-to=origin/main main
# Or for master:
git branch --set-upstream-to=origin/master master
```

### Push Fails - Remote Changes

If remote has changes you don't have:
```bash
git pull --rebase origin main
```

## Testing Git Integration

1. Check git status:
   ```bash
   curl http://localhost:8001/api/git/status
   ```

2. Create a test document through the editor
3. Check git log:
   ```bash
   git log --oneline -5
   ```

4. Verify on GitHub that the commit appears

## Security Notes

⚠️ **Important**: 
- Never commit sensitive information (API keys, passwords, etc.)
- Review commits before pushing in production
- Consider adding pre-commit hooks for validation
- Use branch protection rules on GitHub

## Disabling Auto-Push

If you want to commit but not push automatically, you can modify the API calls to set `push: false`:

```javascript
{
  "content": "...",
  "push": false  // Will commit but not push
}
```

Then manually push when ready:
```bash
git push origin main
```
