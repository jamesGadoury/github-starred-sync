
# GitHub Starred Repo Sync

Automatically clone and update all the repositories you’ve starred on GitHub.

## Features

- Securely uses GitHub token (stored in your system keyring)
- Automatically clones any new starred repositories
- Pulls updates for `main`, `master`, and `release*` branches
- Runs weekly using a `systemd` timer
- Logs to disk with rotation support
- Mocked CI test included

## Setup Instructions

### 1. Install Python Dependencies

Using pip:

```bash
pip install requests keyring
```

Using system packages:
```bash
sudo apt install python3-keyring python3-lcm python3-requests -y
```


### 2. Store GitHub Token Securely

```bash
python3 -c "import keyring; keyring.set_password('github_starred_sync', 'GITHUB_TOKEN', 'your_token_here')"
```

### 3. Set Your GitHub Username

```bash
mkdir -p ~/.config/github-starred-sync
echo 'GITHUB_USERNAME=your_username' > ~/.config/github-starred-sync/env
chmod 600 ~/.config/github-starred-sync/env
```

### 4. Install Script and Enable Service

```bash
./run_install
```

### 5. Check Timer and Logs

```bash
systemctl --user status github-starred-sync.timer
journalctl --user -u github-starred-sync.service
```

### 6. Enable Log Rotation

```bash
sudo cp logrotate.conf /etc/logrotate.d/github-starred-sync
```

## Run CI Test

CI runs mocked unit test to verify logic.

## License

MIT
