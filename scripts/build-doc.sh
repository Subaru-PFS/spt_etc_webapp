#!/usr/bin/env bash
#
# build-doc.sh - Build MkDocs documentation site
#
# Usage:
#   ./scripts/build-doc.sh [uv|venv]
#
# This script builds the MkDocs documentation into static HTML files.
# Output directory: docs/site/
#
# Auto-detects package manager (uv > venv).
#
# Requirements:
#   - the 'docs' dependency group must be installed
#

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root (parent of scripts/)
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

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
        elif [ -d "${PROJECT_ROOT}/.venv" ]; then
            RUNNER=""
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

# Check if mkdocs is available
if ! ${RUNNER} python -c "import mkdocs" 2>/dev/null; then
    echo "Error: mkdocs is not installed." >&2
    echo "" >&2
    echo "This script requires the 'docs' dependency group." >&2
    echo "To install:" >&2
    echo "  uv sync --group docs   (if using uv)" >&2
    echo "  pip install mkdocs mkdocs-material mkdocs-macros-plugin mkdocs-video myst-parser   (if using venv)" >&2
    exit 1
fi

# Change to docs directory and execute
cd "${PROJECT_ROOT}/docs" && exec ${RUNNER} mkdocs build
