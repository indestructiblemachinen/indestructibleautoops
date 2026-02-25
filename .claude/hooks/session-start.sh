#!/bin/bash
set -euo pipefail

# Only run in Claude Code remote environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo "Installing project dependencies..."

# Install root requirements (AI/ML deps for reasoning system)
pip install -q -r "$CLAUDE_PROJECT_DIR/requirements.txt" 2>/dev/null || true

# Install iaops package with dev dependencies (pytest, ruff)
pip install -q -e "$CLAUDE_PROJECT_DIR/iaops[dev]" 2>/dev/null || true

# Install observops-platform with dev dependencies if present
if [ -f "$CLAUDE_PROJECT_DIR/observops-platform/pyproject.toml" ]; then
  pip install -q -e "$CLAUDE_PROJECT_DIR/observops-platform[dev]" 2>/dev/null || true
fi

echo "Dependencies installed successfully."
