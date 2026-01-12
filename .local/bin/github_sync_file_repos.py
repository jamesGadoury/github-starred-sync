#!/usr/bin/env python3
import logging
import os
import subprocess
from datetime import datetime

# === CONFIGURATION ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPOS_FILE = os.path.expanduser(os.getenv("GITHUB_REPOS_FILE", "~/.config/github-repos-sync/repos.txt"))
DEST_DIR = os.path.expanduser(os.getenv("GITHUB_REPOS_DEST", "~/synced_repos"))
# ======================

# === LOGGING SETUP ===
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter("[%(levelname)s] %(message)s")
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)
# =======================


def log_and_print(msg, level="info"):
    getattr(logger, level)(msg)


def parse_repo_line(line):
    """Parse a line from the repos file.

    Supports formats:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - owner/repo

    Returns dict with 'owner', 'repo', 'url' keys or None if invalid/comment.
    """
    line = line.strip()
    if not line or line.startswith('#'):
        return None

    # Full URL format
    if line.startswith('https://github.com/'):
        path = line.replace('https://github.com/', '').rstrip('/')
        # Remove .git suffix if present
        if path.endswith('.git'):
            path = path[:-4]
        parts = path.split('/')
        if len(parts) >= 2:
            owner, repo = parts[0], parts[1]
            clone_url = f'https://github.com/{owner}/{repo}.git'
            return {'owner': owner, 'repo': repo, 'url': clone_url}
        return None

    # Short owner/repo format
    if '/' in line and not line.startswith('http'):
        parts = line.split('/', 1)
        if len(parts) == 2:
            owner, repo = parts
            # Remove .git suffix if present
            if repo.endswith('.git'):
                repo = repo[:-4]
            clone_url = f'https://github.com/{owner}/{repo}.git'
            return {'owner': owner, 'repo': repo, 'url': clone_url}

    return None


def read_repos_from_file(filepath):
    """Read and parse repos from file."""
    repos = []
    if not os.path.exists(filepath):
        log_and_print(f"Repos file not found: {filepath}", level="error")
        return repos

    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            parsed = parse_repo_line(line)
            if parsed:
                repos.append(parsed)
            elif line.strip() and not line.strip().startswith('#'):
                log_and_print(f"Skipping invalid line {line_num}: {line.strip()}", level="warning")

    return repos


def run_git_command(args, cwd):
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        logger.debug(f"Ran command: {' '.join(args)}\n{result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running {' '.join(args)} in {cwd}:\n{e.stderr}")
        return None


def clone_repo(clone_url, repo_name):
    log_and_print(f"Cloning new repo: {repo_name}")
    return run_git_command(["git", "clone", clone_url], cwd=DEST_DIR)


def pull_repo(repo_path, repo_name):
    log_and_print(f"Pulling latest changes for repo: {repo_name}")
    run_git_command(["git", "fetch", "--all"], cwd=repo_path)

    branches_output = run_git_command(["git", "branch", "-r"], cwd=repo_path)
    if not branches_output:
        log_and_print(f"No remote branches found for {repo_name}", level="warning")
        return

    remote_branches = [
        line.strip().split("/")[-1] for line in branches_output.splitlines()
    ]
    branches_to_pull = []

    for branch in ["main", "master"]:
        if branch in remote_branches:
            branches_to_pull.append(branch)
            break

    branches_to_pull.extend([b for b in remote_branches if b.startswith("release")])

    for branch in set(branches_to_pull):
        log_and_print(f"Checking out and pulling branch '{branch}' in {repo_name}")
        run_git_command(["git", "checkout", branch], cwd=repo_path)
        run_git_command(["git", "pull", "origin", branch], cwd=repo_path)


def sync_repo(repo_url, repo_name):
    repo_path = os.path.join(DEST_DIR, repo_name)
    if not os.path.exists(repo_path):
        clone_repo(repo_url, repo_name)
    else:
        log_and_print(f"Repo already exists: {repo_name}")
        pull_repo(repo_path, repo_name)


def sync_file_repos():
    if not GITHUB_TOKEN:
        log_and_print("Environment variable GITHUB_TOKEN is not set.", level="error")
        return

    if not os.path.exists(REPOS_FILE):
        log_and_print(f"Repos file not found: {REPOS_FILE}", level="error")
        return

    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
        log_and_print(f"Created destination directory: {DEST_DIR}")

    try:
        log_and_print(f"Starting sync of repos from file: {REPOS_FILE}")
        repos = read_repos_from_file(REPOS_FILE)
        log_and_print(f"Found {len(repos)} repositories in file.")
        for repo in repos:
            try:
                name = repo["repo"]
                full_name = f"{repo['owner']}/{repo['repo']}"
                clone_url = repo["url"]
                log_and_print(f"Syncing repository: {full_name}")
                sync_repo(clone_url, name)
            except Exception as e:
                logger.error(f"Error syncing repo {repo.get('owner')}/{repo.get('repo')}: {e}")
    except Exception as e:
        logger.exception("Unhandled exception during sync.")
    finally:
        log_and_print("Finished sync.")


if __name__ == "__main__":
    log_and_print("\n" + "=" * 40 + f"\nSync started at {datetime.now()}\n" + "=" * 40)
    sync_file_repos()
