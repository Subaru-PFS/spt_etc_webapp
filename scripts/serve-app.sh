#!/usr/bin/env bash
#
# serve-app.sh - Start the PFS ETC Panel web application
#
# This script starts the PFS Exposure Time Calculator web application with:
# - Port 5007
# - URL prefix: /etc
# - Static documentation: /etc/doc
# - WebSocket max message size: 100MB
# - Development mode enabled (--dev) for auto-reload
#
# Usage:
#   ./scripts/serve-app.sh [uv|venv]
#
# Arguments:
#   uv    - Use 'uv run' to execute the command
#   venv  - Use '.venv/bin/' to execute the command directly
#   (none) - Auto-detect (priority: uv > venv)
#
# Requirements:
#   - panel must be installed
#   - Documentation built (docs/site/ directory)
#

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root (parent of scripts/)
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Change to project root
cd "${PROJECT_ROOT}"

ensure_watchfiles() {
    if ${RUNNER} python -c "import watchfiles" >/dev/null 2>&1; then
        return 0
    fi

    echo "watchfiles is not installed; syncing dev dependencies before startup..."

    case "${RUNNER_TYPE}" in
        uv)
            uv sync --group dev
            ;;
        venv|auto)
            "${PROJECT_ROOT}/.venv/bin/python" -m pip install -e "${PROJECT_ROOT}"
            "${PROJECT_ROOT}/.venv/bin/python" -m pip install watchfiles
            ;;
    esac
}

# Parse command-line argument
RUNNER_TYPE="${1:-auto}"

# Detect or validate package manager
case "${RUNNER_TYPE}" in
    uv)
        if ! command -v uv &> /dev/null; then
            echo "Error: 'uv' not found in PATH" >&2
            echo "Please install uv or use a different runner" >&2
            exit 1
        fi
        RUNNER="uv run"
        ;;
    venv)
        if [ ! -d "${PROJECT_ROOT}/.venv" ]; then
            echo "Error: .venv directory not found" >&2
            echo "Please run 'uv sync' first" >&2
            exit 1
        fi
        RUNNER=""
        ;;
    auto)
        # Auto-detect: Priority: uv > venv
        if command -v uv &> /dev/null; then
            RUNNER="uv run"
            RUNNER_TYPE="uv"
        elif [ -d "${PROJECT_ROOT}/.venv" ]; then
            RUNNER=""
            RUNNER_TYPE="venv"
        else
            echo "Error: Cannot find a suitable package manager" >&2
            echo "Please install dependencies using 'uv sync'" >&2
            exit 1
        fi
        ;;
    *)
        echo "Error: Invalid runner type '${RUNNER_TYPE}'" >&2
        echo "Usage: $0 [uv|venv]" >&2
        exit 1
        ;;
esac

# In venv mode RUNNER is empty, so put .venv/bin first on PATH to make the
# bare `python`/`panel` invocations below resolve to the venv, as documented.
if [ "${RUNNER_TYPE}" = "venv" ]; then
    export PATH="${PROJECT_ROOT}/.venv/bin:${PATH}"
fi

ensure_watchfiles

# Execute the command
exec ${RUNNER} panel serve "${PROJECT_ROOT}/app.py" \
    --static-dirs doc="${PROJECT_ROOT}/docs/site" \
    --prefix=etc \
    --websocket-max-message-size=104857600 \
    --port=5007 \
    --dev
