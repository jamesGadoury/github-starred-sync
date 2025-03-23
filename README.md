# GitHub Starred Repo Sync

Automatically clone and update all the repositories you’ve starred on GitHub.

## Features

- Securely uses GitHub token (from an environment file)
- Automatically clones any new starred repositories
- Pulls updates for `main`, `master`, and `release*` branches
- Runs weekly using a `systemd` timer
- Logs to disk with rotation support
- Mocked CI test included

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

### 2. Store Your GitHub Token Securely

#### Create secrets file:

```bash
mkdir -p ~/.config/github-starred-sync
vi ~/.config/github-starred-sync/secrets.env
```

#### Add the following line:

```env
GITHUB_TOKEN=your_token_here
```

> Get your token from https://github.com/settings/tokens  
> It only needs the `public_repo` scope unless you're syncing private repos.

#### Lock it down:

```bash
chmod 600 ~/.config/github-starred-sync/secrets.env
```

---

### 3. Configure env variables for the service 

```bash
mkdir -p ~/.config/github-starred-sync
echo 'GITHUB_USERNAME=your_username' > ~/.config/github-starred-sync/env
chmod 600 ~/.config/github-starred-sync/env
```

NOTE: If you also want to override the DEST_DIR (where the github repos are cloned), you can also do the following:
```bash
echo 'GITHUB_STARRED_DEST=your_desired_path' >> ~/.config/github-starred-sync/env
```

---

### 4. Install Script and Enable Service

```bash
./run_install
```

---

### 5. Check Timer and Logs

```bash
systemctl --user status github-starred-sync.timer
journalctl --user -u github-starred-sync.service
```

---

### 6. Enable Log Rotation

```bash
sudo cp logrotate.conf /etc/logrotate.d/github-starred-sync
```

---

### 7. [Optional] Enable for first time:

If you don't want to wait for the timer to run for first time, you can trigger the start the service manually:
```bash
systemctl --user start github-starred-sync.service
```

## License

MIT
