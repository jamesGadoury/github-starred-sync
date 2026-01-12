#!/bin/bash
#
# sync_starred_repos.sh
#
# Re-queries starred GitHub repos and re-clones/updates them.
# Sources the same environment files as the systemd service.
#
# Usage: sync_starred_repos.sh [DEST_DIR]
#

set -euo pipefail

CONFIG_DIR="${HOME}/.config/github-starred-sync"
SECRETS_FILE="${CONFIG_DIR}/secrets.env"
ENV_FILE="${CONFIG_DIR}/env"

# Show usage
usage() {
    echo "Usage: $(basename "$0") [DEST_DIR]"
    echo ""
    echo "Re-queries starred GitHub repos and re-clones/updates them."
    echo ""
    echo "Arguments:"
    echo "  DEST_DIR    Directory to clone repos into (default: ~/starred_repos)"
    echo ""
    echo "Environment files sourced:"
    echo "  ~/.config/github-starred-sync/secrets.env  (GITHUB_TOKEN)"
    echo "  ~/.config/github-starred-sync/env          (GITHUB_USERNAME)"
    exit 0
}

# Handle --help
[[ "${1:-}" == "-h" || "${1:-}" == "--help" ]] && usage

# Accept destination directory as argument
DEST_ARG="${1:-}"

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
    log_error "Environment file not found: $ENV_FILE"
    log_error "Create it with: echo 'GITHUB_USERNAME=your_username' > $ENV_FILE && chmod 600 $ENV_FILE"
    exit 1
fi

# Validate required variables
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    log_error "GITHUB_TOKEN is not set in $SECRETS_FILE"
    exit 1
fi

if [[ -z "${GITHUB_USERNAME:-}" ]]; then
    log_error "GITHUB_USERNAME is not set in $ENV_FILE"
    exit 1
fi

# Set destination: CLI arg > env var > default
if [[ -n "$DEST_ARG" ]]; then
    GITHUB_STARRED_DEST="$DEST_ARG"
else
    GITHUB_STARRED_DEST="${GITHUB_STARRED_DEST:-$HOME/starred_repos}"
fi

log_info "Configuration:"
log_info "  Username: $GITHUB_USERNAME"
log_info "  Destination: $GITHUB_STARRED_DEST"

# Export for Python script
export GITHUB_TOKEN
export GITHUB_USERNAME
export GITHUB_STARRED_DEST

# Run the Python sync script
exec python3 "$(dirname "$0")/.local/bin/github_sync_starred_repos.py"
