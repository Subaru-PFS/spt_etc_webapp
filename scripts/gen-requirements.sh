#!/usr/bin/env bash
#
# gen-requirements.sh - Generate requirements.txt from project dependencies
#
# Usage:
#   ./scripts/gen-requirements.sh [uv|pdm]
#
# This script exports all project dependencies to requirements.txt:
# - Production dependencies
# - Development dependencies
# - Optional mkdocs dependencies
# - Editable self-install (-e .)
# - Git and URL dependencies
#
# Output: requirements.txt (at project root)
#
# Note: Prefers uv export, falls back to pdm export if uv not available.
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
            echo "Please install uv" >&2
            exit 1
        fi
        # Use uv export
        echo "Generating requirements.txt using uv export..."
        exec uv export \
            --format requirements-txt \
            --no-hashes \
            --all-groups \
            --extra mkdocs \
            --output-file "${PROJECT_ROOT}/requirements.txt"
        ;;
    pdm)
        if ! command -v pdm &> /dev/null; then
            echo "Error: 'pdm' not found in PATH" >&2
            echo "Please install pdm" >&2
            exit 1
        fi
        # Use pdm export
        echo "Generating requirements.txt using pdm export..."
        exec pdm export \
            --format requirements \
            --without-hashes \
            --pyproject \
            --dev \
            --group mkdocs \
            --output "${PROJECT_ROOT}/requirements.txt" \
            --editable-self \
            --verbose
        ;;
    auto)
        # Auto-detect: Priority: uv > pdm
        if command -v uv &> /dev/null; then
            echo "Generating requirements.txt using uv export..."
            exec uv export \
                --format requirements-txt \
                --no-hashes \
                --all-groups \
                --extra mkdocs \
                --output-file "${PROJECT_ROOT}/requirements.txt"
        elif command -v pdm &> /dev/null; then
            echo "Generating requirements.txt using pdm export..."
            exec pdm export \
                --format requirements \
                --without-hashes \
                --pyproject \
                --dev \
                --group mkdocs \
                --output "${PROJECT_ROOT}/requirements.txt" \
                --editable-self \
                --verbose
        else
            echo "Error: Neither 'uv' nor 'pdm' found in PATH" >&2
            echo "Please install uv or pdm" >&2
            exit 1
        fi
        ;;
    *)
        echo "Error: Invalid runner type '${RUNNER_TYPE}'" >&2
        echo "Usage: $0 [uv|pdm]" >&2
        exit 1
        ;;
esac
