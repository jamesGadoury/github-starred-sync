#!/bin/bash
#
# sync_file_repos.sh
#
# Syncs GitHub repos listed in a user-provided file.
# Sources the same environment files as the systemd service.
#
# Usage: sync_file_repos.sh [REPOS_FILE] [DEST_DIR]
#

set -euo pipefail

CONFIG_DIR="${HOME}/.config/github-repos-sync"
SECRETS_FILE="${CONFIG_DIR}/secrets.env"
ENV_FILE="${CONFIG_DIR}/env"

# Show usage
usage() {
    echo "Usage: $(basename "$0") [REPOS_FILE] [DEST_DIR]"
    echo ""
    echo "Syncs GitHub repos listed in a user-provided file."
    echo ""
    echo "Arguments:"
    echo "  REPOS_FILE  File containing repo URLs/names (default: from env or ~/.config/github-repos-sync/repos.txt)"
    echo "  DEST_DIR    Directory to clone repos into (default: ~/synced_repos)"
    echo ""
    echo "Repos file format (one per line):"
    echo "  https://github.com/owner/repo"
    echo "  owner/repo"
    echo "  # Comments start with #"
    echo ""
    echo "Environment files sourced:"
    echo "  ~/.config/github-repos-sync/secrets.env  (GITHUB_TOKEN)"
    echo "  ~/.config/github-repos-sync/env          (GITHUB_REPOS_FILE, GITHUB_REPOS_DEST)"
    exit 0
}

# Handle --help
[[ "${1:-}" == "-h" || "${1:-}" == "--help" ]] && usage

# Accept repos file and destination directory as arguments
REPOS_FILE_ARG="${1:-}"
DEST_ARG="${2:-}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Source environment files (same as systemd service)
if [[ -f "$SECRETS_FILE" ]]; then
    log_info "Loading secrets from: $SECRETS_FILE"
    set -a
    source "$SECRETS_FILE"
    set +a
else
    log_error "Secrets file not found: $SECRETS_FILE"
    log_error "Create it with: echo 'GITHUB_TOKEN=your_token_here' > $SECRETS_FILE && chmod 600 $SECRETS_FILE"
    exit 1
fi

if [[ -f "$ENV_FILE" ]]; then
    log_info "Loading environment from: $ENV_FILE"
    set -a
    source "$ENV_FILE"
    set +a
else
    log_warn "Environment file not found: $ENV_FILE"
    log_warn "Create it with: echo 'GITHUB_REPOS_FILE=~/repos.txt' > $ENV_FILE && chmod 600 $ENV_FILE"
fi

# Validate required variables
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    log_error "GITHUB_TOKEN is not set in $SECRETS_FILE"
    exit 1
fi

# Set repos file: CLI arg > env var > default
if [[ -n "$REPOS_FILE_ARG" ]]; then
    GITHUB_REPOS_FILE="$REPOS_FILE_ARG"
else
    GITHUB_REPOS_FILE="${GITHUB_REPOS_FILE:-$HOME/.config/github-repos-sync/repos.txt}"
fi

# Expand tilde
GITHUB_REPOS_FILE="${GITHUB_REPOS_FILE/#\~/$HOME}"

# Set destination: CLI arg > env var > default
if [[ -n "$DEST_ARG" ]]; then
    GITHUB_REPOS_DEST="$DEST_ARG"
else
    GITHUB_REPOS_DEST="${GITHUB_REPOS_DEST:-$HOME/synced_repos}"
fi

# Expand tilde
GITHUB_REPOS_DEST="${GITHUB_REPOS_DEST/#\~/$HOME}"

# Check if repos file exists
if [[ ! -f "$GITHUB_REPOS_FILE" ]]; then
    log_error "Repos file not found: $GITHUB_REPOS_FILE"
    log_error "Create it with repo URLs/names, one per line"
    exit 1
fi

log_info "Configuration:"
log_info "  Repos file: $GITHUB_REPOS_FILE"
log_info "  Destination: $GITHUB_REPOS_DEST"

# Export for Python script
export GITHUB_TOKEN
export GITHUB_REPOS_FILE
export GITHUB_REPOS_DEST

# Run the Python sync script
exec python3 "$(dirname "$0")/.local/bin/github_sync_file_repos.py"
