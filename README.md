# GitHub Repo Sync

Automatically clone and update GitHub repositories using systemd timers.

## Services

This project provides two sync services:

| Service | Description |
|---------|-------------|
| **github-starred-sync** | Syncs all repositories you've starred on GitHub |
| **github-repos-sync** | Syncs repositories listed in a user-provided file |

## Features

- Securely uses GitHub token (from environment files)
- Automatically clones new repositories
- Pulls updates for `main`, `master`, and `release*` branches
- Runs weekly using `systemd` timers (Sundays at 3AM)
- Logs via journald

---

## Setup Instructions

### 1. Install Python Dependencies

Using pip:

```bash
pip install requests
```

Using system packages:
```bash
sudo apt install python3-requests -y
```

---

## Starred Repos Sync

Automatically clone and update all repositories you've starred on GitHub.

### 2a. Store Your GitHub Token

```bash
mkdir -p ~/.config/github-starred-sync
echo 'GITHUB_TOKEN=your_token_here' > ~/.config/github-starred-sync/secrets.env
chmod 600 ~/.config/github-starred-sync/secrets.env
```

> Get your token from https://github.com/settings/tokens
> It only needs the `public_repo` scope unless you're syncing private repos.

### 3a. Configure Environment Variables

```bash
echo 'GITHUB_USERNAME=your_username' > ~/.config/github-starred-sync/env
chmod 600 ~/.config/github-starred-sync/env
```

Optionally override the destination directory:
```bash
echo 'GITHUB_STARRED_DEST=~/starred_repos' >> ~/.config/github-starred-sync/env
```

### 4a. Install and Enable

```bash
./run_install_starred_sync
```

### 5a. Check Status and Logs

```bash
systemctl --user status github-starred-sync.timer
journalctl --user -u github-starred-sync.service -f
```

### 6a. Manual Run

```bash
# Using the wrapper script
./sync_starred_repos.sh

# Or trigger the service directly
systemctl --user start github-starred-sync.service --no-block
```

---

## File-Based Repos Sync

Sync repositories listed in a user-provided file. Useful for maintaining a curated list of repos.

### 2b. Store Your GitHub Token

```bash
mkdir -p ~/.config/github-repos-sync
echo 'GITHUB_TOKEN=your_token_here' > ~/.config/github-repos-sync/secrets.env
chmod 600 ~/.config/github-repos-sync/secrets.env
```

### 3b. Configure Environment Variables

```bash
echo 'GITHUB_REPOS_FILE=~/my-repos.txt' > ~/.config/github-repos-sync/env
echo 'GITHUB_REPOS_DEST=~/synced_repos' >> ~/.config/github-repos-sync/env
chmod 600 ~/.config/github-repos-sync/env
```

### 4b. Create Your Repos File

Create a file (e.g., `~/my-repos.txt`) with one repository per line:

```
# Comments start with #
https://github.com/torvalds/linux
neovim/neovim
rust-lang/rust
owner/repo-name
```

Supported formats:
- Full URL: `https://github.com/owner/repo`
- Short format: `owner/repo`

### 5b. Install and Enable

```bash
./run_install_file_sync
```

### 6b. Check Status and Logs

```bash
systemctl --user status github-repos-sync.timer
journalctl --user -u github-repos-sync.service -f
```

### 7b. Manual Run

```bash
# Using the wrapper script
./sync_file_repos.sh

# With custom paths
./sync_file_repos.sh ~/my-repos.txt ~/custom-dest

# Or trigger the service directly
systemctl --user start github-repos-sync.service --no-block
```

---

## Disabling Services

To stop and disable the timers:

```bash
# Starred sync
systemctl --user disable --now github-starred-sync.timer

# File-based sync
systemctl --user disable --now github-repos-sync.timer
```

To re-enable:

```bash
# Starred sync
systemctl --user enable --now github-starred-sync.timer

# File-based sync
systemctl --user enable --now github-repos-sync.timer
```

To fully uninstall (remove service files):

```bash
# Starred sync
systemctl --user disable --now github-starred-sync.timer
rm ~/.config/systemd/user/github-starred-sync.{service,timer}
rm ~/.local/bin/github_sync_starred_repos.py

# File-based sync
systemctl --user disable --now github-repos-sync.timer
rm ~/.config/systemd/user/github-repos-sync.{service,timer}
rm ~/.local/bin/github_sync_file_repos.py

# Reload systemd
systemctl --user daemon-reload
```

---

## Configuration Reference

### Starred Sync

| File | Variables |
|------|-----------|
| `~/.config/github-starred-sync/secrets.env` | `GITHUB_TOKEN` |
| `~/.config/github-starred-sync/env` | `GITHUB_USERNAME`, `GITHUB_STARRED_DEST` (optional) |

### File-Based Sync

| File | Variables |
|------|-----------|
| `~/.config/github-repos-sync/secrets.env` | `GITHUB_TOKEN` |
| `~/.config/github-repos-sync/env` | `GITHUB_REPOS_FILE`, `GITHUB_REPOS_DEST` (optional) |

---

## License

MIT
