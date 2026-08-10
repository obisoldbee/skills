# Fork Workflow — Full Setup & PR Guide

This document provides the workflow for one Project Root that wraps one upstream repository fork and contributes back by PR.

## When to Use

- Forking an upstream repo to contribute changes back via PR
- Setting up a fork-based workspace for the first time
- Syncing with upstream, submitting PRs, or resolving remote issues
- Recording one fork's Project Root and Repository Root mapping

## Prerequisites

### GitHub CLI (`gh`)

The `gh` CLI is the recommended tool for fork workflows. Install it first:

**Windows (winget)**:
```bash
winget install --id GitHub.cli --silent --accept-source-agreements --accept-package-agreements
```

**macOS (Homebrew)**:
```bash
brew install gh
```

**Linux**: See [gh installation guide](https://github.com/cli/cli/blob/trunk/docs/install_linux.md).

**Verify**:
```bash
gh --version
```

**Windows PATH note**: winget installs to `C:\Program Files\GitHub CLI\` but may not add it to the persistent PATH. In Git Bash, run `export PATH="$PATH:/c/Program Files/GitHub CLI"` for the current session, or add it to `~/.bashrc` / system PATH for persistence.

### Authentication

```bash
gh auth login
```

Choose: GitHub.com → HTTPS → "Login with a web browser" (recommended) or paste a Personal Access Token.

**Verify**:
```bash
gh auth status
```

### Git Identity

Ensure git user.name and user.email are configured (required for commits):
```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

## Directory Layout

```
project-root/                 # SOP wrapper (NOT pushed to upstream)
├── AGENTS.md                 # Must include "Fork Workflow" section
├── docs/                     # SOP docs (specs/plans/reviews) — outside src/
├── memory/                   # Agent memory — outside src/
├── conversation/             # Decision records — outside src/
└── src/                      # Source container
    └── <repo-name>/          # The one mapped fork Repository Root
        ├── .git/
        ├── (upstream repo contents)
        └── ...
```

**Key principle**: this Project Root has one fork repository mapping. Put that Repository Root at `src/<repo-name>/` and record it in `AGENTS.md`. Do not add an unrelated second fork to the same Project Root.

This ordinary fork rule does not override the explicit shared-repository Skills collection profile. In that profile, the collection-local Repository Root and each member's managed scope are declared separately; read `shared-repository.md`.

## Setup Methods

### Method A: `gh repo fork --remote` (Recommended)

Best when you want to contribute back via PR. One command does three things: forks on GitHub, renames `origin` to `upstream`, and adds your fork as new `origin`.

```bash
# 1. Clone the upstream repo first
cd <project-root>
git clone https://github.com/<upstream-owner>/<repo>.git src/<repo-name>

# 2. Fork + reconfigure remotes in one command
cd src/<repo-name>
gh repo fork --remote

# 3. Verify remotes
git remote -v
# Expected:
# origin    https://github.com/<your-username>/<repo>.git (fetch/push)
# upstream  https://github.com/<upstream-owner>/<repo>.git (fetch/push)
```

**What `gh repo fork --remote` does**:
1. Creates a fork of `<upstream-owner>/<repo>` under your GitHub account
2. Renames the existing `origin` remote to `upstream`
3. Adds your fork (`https://github.com/<your-username>/<repo>.git`) as the new `origin`

### Method B: Manual fork + clone

Use when `gh` CLI is unavailable or you want explicit control.

```bash
# 1. Fork on GitHub.com manually (via the "Fork" button on the repo page)

# 2. Clone YOUR fork (not the upstream)
cd <project-root>
git clone https://github.com/<your-username>/<repo>.git src/<repo-name>

# 3. Add upstream remote
cd src/<repo-name>
git remote add upstream https://github.com/<upstream-owner>/<repo>.git

# 4. Verify
git remote -v
```

### Method C: Clone only (no fork)

Use when you just want to read/inspect the code and don't plan to submit PRs yet.

```bash
cd <project-root>
git clone https://github.com/<upstream-owner>/<repo>.git src/<repo-name>

# origin points to upstream — can fetch/pull but cannot push
```

**To upgrade to a fork later**: run `cd src/<repo-name> && gh repo fork --remote` — it works on an already-cloned repo (Method A's step 2).

## Daily PR Workflow

```bash
cd src/<repo-name>

# 1. Sync with upstream before starting work
git fetch upstream
git checkout main
git rebase upstream/main

# 2. Create a feature branch
git checkout -b fix/short-description
# Branch naming: fix/..., feat/..., docs/..., refactor/... (match upstream conventions if they have CONTRIBUTING.md)

# 3. Make changes and commit
# ... edit files ...
git add .
git commit -m "fix: concise description of the change"

# 4. Push to YOUR fork (origin, not upstream)
git push origin fix/short-description

# 5. Create PR
gh pr create --base main --head fix/short-description \
  --title "Fix: concise title" \
  --body "## What changed
- Description of changes

## Why
- Rationale

## Testing
- How tested

## Checklist
- [ ] Tests pass
- [ ] Code follows project conventions"
```

**Multiple commits**: squash or keep them based on the upstream project's conventions. Check `CONTRIBUTING.md` in the forked repo.

## Syncing with Upstream

### Rebase (Recommended for clean history)

```bash
cd src/<repo-name>
git fetch upstream
git checkout main
git rebase upstream/main
git push origin main --force-with-lease
```

**Use rebase when**: you want a linear history, your commits haven't been pushed yet, or the upstream prefers it.

### Merge (Preserves merge commits)

```bash
cd src/<repo-name>
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

**Use merge when**: commits are already pushed, multiple people work on the same fork, or you want to preserve the exact history.

### Resolving rebase/merge conflicts

```bash
# After conflict occurs
git status                    # see conflicted files
# ... resolve conflicts manually ...
git add <resolved-files>
git rebase --continue         # or: git merge --continue
```

If you want to abort:
```bash
git rebase --abort            # or: git merge --abort
```

## More Than One Fork

Create a sibling Project Root for every additional fork. If the forks are related, a Project Collection may route between them without owning their source:

```
collection-root/
├── repo-a-project/
│   └── src/repo-a/.git/
└── repo-b-project/
    └── src/repo-b/.git/
```

Each ordinary member `AGENTS.md` records only its own Repository Root, `origin`, and `upstream`. The collection member index records membership, not Git remotes on behalf of ordinary projects. The explicit shared-repository profile is the exception: its member row records the shared Repository Root and normalized remote needed to map a managed package scope; see `shared-repository.md`.

## AGENTS.md Fork Section

Every fork workspace's AGENTS.md **must** include a "Fork Workflow" section. Template:

```markdown
## Fork Workflow

- Fork repo: `src/<repo-name>/` (independent `.git/`)
- Upstream: `https://github.com/<owner>/<repo>`
- Remotes: `origin` → your fork, `upstream` → original repo
- PR flow: branch → commit → push origin → `gh pr create`
- Sync: `git fetch upstream && git rebase upstream/main`
```

## Troubleshooting

### `gh: command not found` (Windows)

The winget install doesn't always update the current shell's PATH.

```bash
# Temp fix (current session)
export PATH="$PATH:/c/Program Files/GitHub CLI"

# Permanent fix: add to ~/.bashrc
echo 'export PATH="$PATH:/c/Program Files/GitHub CLI"' >> ~/.bashrc
source ~/.bashrc
```

### `gh auth login` is interactive and can't run in non-interactive shell

Run `gh auth login` in a separate terminal where you can interact with the prompts. If using a Personal Access Token:

```bash
echo "ghp_YOUR_TOKEN" | gh auth login --with-token
```

### `gh auth login` fails with "TLS handshake timeout" / network error

This is common when connecting to GitHub from networks with restricted access to GitHub (e.g., mainland China). The device-code flow tries to reach `github.com/login/device/code` and times out.

**Solution 1 — Configure proxy (if you have one)**:

PowerShell (current session):
```powershell
$env:HTTPS_PROXY = "http://127.0.0.1:7890"  # change to your proxy port
$env:HTTP_PROXY = "http://127.0.0.1:7890"
gh auth login
```

Git Bash (current session):
```bash
export HTTPS_PROXY=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
gh auth login
```

**Solution 2 — Use a Personal Access Token (bypasses device-code flow)**:

1. Open https://github.com/settings/tokens in a browser (browser may work even when `gh` CLI can't reach GitHub directly)
2. Generate a classic token with `repo` and `workflow` scopes
3. Authenticate via token:

```powershell
# PowerShell
$env:GH_TOKEN = "ghp_YOUR_TOKEN_HERE"
gh repo fork --remote   # will use GH_TOKEN automatically
```

Or persist the token:
```powershell
gh auth login --with-token   # then paste token and press Enter
```

**Solution 3 — Retry later**: TLS timeout may be transient. Wait a few minutes and try again.

**Verify proxy is working**: `curl -I https://github.com` should return `HTTP/2 200` (not a timeout).

### `gh repo fork` fails with "already forked"

If you've already forked the repo on GitHub previously:

```bash
# Just add the remote manually
cd src/<repo-name>
git remote rename origin upstream
git remote add origin https://github.com/<your-username>/<repo>.git
git remote -v
```

### Push to upstream rejected (permission denied)

This is **expected** — you should never push to upstream. Always push to your fork (`origin`):

```bash
git push origin <branch>      # correct
# git push upstream <branch>  # WRONG — will be rejected
```

### `git push` fails with TLS timeout / network error (network-restricted environments)

In networks with restricted access to GitHub (e.g., mainland China), `git push` may fail with `TLS handshake timeout` even though `gh` CLI works fine. This is because `git` and `gh` use different network channels.

**Solution — sync fork server-side via `gh repo sync` (bypasses local push entirely)**:

```bash
# Sync your fork's main with upstream, entirely on GitHub's servers
gh repo sync <your-username>/<repo> --source <upstream-owner>/<repo> --branch main

# Then fetch the updated fork locally
git fetch origin
```

This is the recommended approach when `git push` is blocked by network issues but `gh` CLI is authenticated and working.

**For feature branches** (not main): `gh repo sync` only syncs from upstream, so it won't help push your feature branch. In this case:
1. Configure a proxy for git: `git config --global http.proxy http://127.0.0.1:7890`
2. Or use `gh pr create` directly — if the local branch has commits, `gh` can push it via its own network channel before creating the PR

### `git push origin main --force-with-lease` rejected after rebase

Someone else (or another machine) pushed to your fork's main. Fetch and retry:

```bash
git fetch origin
git rebase upstream/main
git push origin main --force-with-lease
```

### Accidentally committed to main instead of a branch

```bash
# Create a branch from current state
git branch fix/your-changes
# Reset main to upstream
git reset --hard upstream/main
# Switch to the branch
git checkout fix/your-changes
```

### Upstream repo URL changed

```bash
git remote set-url upstream https://github.com/<new-owner>/<repo>.git
git fetch upstream
```

## Quick Reference

| Action | Command |
|---|---|
| Install gh (Windows) | `winget install --id GitHub.cli` |
| Authenticate | `gh auth login` |
| Fork + configure remotes | `cd src/<repo> && gh repo fork --remote` |
| Sync with upstream | `git fetch upstream && git rebase upstream/main` |
| Push to your fork | `git push origin <branch>` |
| Create PR | `gh pr create --base main --head <branch>` |
| Check PR status | `gh pr status` |
| Merge PR (if you have permission) | `gh pr merge <number>` |
| List your PRs | `gh pr list --author @me` |
