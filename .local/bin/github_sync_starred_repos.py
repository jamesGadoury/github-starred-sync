#!/usr/bin/env python3
import logging
import os
import subprocess
from datetime import datetime

import keyring
import requests

# === CONFIGURATION ===
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = keyring.get_password("github_starred_sync", "GITHUB_TOKEN")
DEST_DIR = os.path.expanduser("~/starred_repos")
LOG_FILE = os.path.expanduser("~/starred_repo_sync.log")
# ======================

# === LOGGING SETUP ===
logging.basicConfig(
    filename=LOG_FILE,
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# =======================


def log_and_print(msg, level="info"):
    print(msg)
    getattr(logging, level)(msg)


def get_starred_repos(username, token):
    starred = []
    page = 1
    headers = {"Authorization": f"token {token}"}

    while True:
        url = (
            f"https://api.github.com/users/{username}/starred?per_page=100&page={page}"
        )
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"GitHub API error {response.status_code}: {response.text}")
        data = response.json()
        if not data:
            break
        starred.extend(data)
        page += 1

    return starred


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
        logging.debug(f"Ran command: {' '.join(args)}\n{result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running {' '.join(args)} in {cwd}:\n{e.stderr}")
        return None


def clone_repo(clone_url, repo_name):
    log_and_print(f"Cloning new repo: {repo_name}")
    return run_git_command(["git", "clone", clone_url], cwd=DEST_DIR)


def pull_repo(repo_path):
    log_and_print(f"Pulling latest changes in: {repo_path}")
    run_git_command(["git", "fetch", "--all"], cwd=repo_path)

    branches_output = run_git_command(["git", "branch", "-r"], cwd=repo_path)
    if not branches_output:
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
        log_and_print(f"Pulling branch '{branch}' in {repo_path}")
        run_git_command(["git", "checkout", branch], cwd=repo_path)
        run_git_command(["git", "pull", "origin", branch], cwd=repo_path)


def sync_repo(repo_url, repo_name):
    repo_path = os.path.join(DEST_DIR, repo_name)
    if not os.path.exists(repo_path):
        clone_repo(repo_url, repo_name)
    else:
        pull_repo(repo_path)


def sync_starred():
    if not GITHUB_USERNAME:
        log_and_print("Environment variable GITHUB_USERNAME is not set.", level="error")
        return

    if not GITHUB_TOKEN:
        log_and_print("GitHub token not found in keyring.", level="error")
        return

    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    try:
        log_and_print("Starting sync of starred GitHub repos...")
        repos = get_starred_repos(GITHUB_USERNAME, GITHUB_TOKEN)
        log_and_print(f"Found {len(repos)} starred repositories.")
        for repo in repos:
            try:
                name = repo["name"]
                clone_url = repo["clone_url"]
                sync_repo(clone_url, name)
            except Exception as e:
                logging.error(f"Error syncing repo {repo.get('full_name')}: {e}")
    except Exception as e:
        logging.exception("Unhandled exception during sync.")
    finally:
        log_and_print("Finished sync.")


if __name__ == "__main__":
    log_and_print("\n" + "=" * 40 + f"\nSync started at {datetime.now()}\n" + "=" * 40)
    sync_starred()
