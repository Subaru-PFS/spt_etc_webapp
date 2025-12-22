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
#   ./scripts/serve-app.sh [uv|pdm|venv]
#
# Arguments:
#   uv    - Use 'uv run' to execute the command
#   pdm   - Use 'pdm run' to execute the command
#   venv  - Use '.venv/bin/' to execute the command directly
#   (none) - Auto-detect (priority: uv > pdm > venv)
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
    pdm)
        if ! command -v pdm &> /dev/null; then
            echo "Error: 'pdm' not found in PATH" >&2
            echo "Please install pdm or use a different runner" >&2
            exit 1
        fi
        RUNNER="pdm run"
        ;;
    venv)
        if [ ! -d "${PROJECT_ROOT}/.venv" ]; then
            echo "Error: .venv directory not found" >&2
            echo "Please run 'uv sync' or 'pdm install' first" >&2
            exit 1
        fi
        RUNNER=""
        ;;
    auto)
        # Auto-detect: Priority: uv > pdm > venv
        if command -v uv &> /dev/null; then
            RUNNER="uv run"
        elif command -v pdm &> /dev/null; then
            RUNNER="pdm run"
        elif [ -d "${PROJECT_ROOT}/.venv" ]; then
            RUNNER=""
        else
            echo "Error: Cannot find a suitable package manager" >&2
            echo "Please install dependencies using 'uv sync' or 'pdm install'" >&2
            exit 1
        fi
        ;;
    *)
        echo "Error: Invalid runner type '${RUNNER_TYPE}'" >&2
        echo "Usage: $0 [uv|pdm|venv]" >&2
        exit 1
        ;;
esac

# Execute the command
exec ${RUNNER} panel serve "${PROJECT_ROOT}/app.py" \
    --static-dirs doc="${PROJECT_ROOT}/docs/site" \
    --prefix=etc \
    --websocket-max-message-size=104857600 \
    --port=5007 \
    --dev
