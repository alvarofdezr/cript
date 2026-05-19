#!/bin/bash
#
# Quick setup script for CRIPT on Linux/macOS
# 
# Usage:
#   bash setup.sh
#

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║            CRIPT Setup Script                                  ║"
echo "║   Cryptographic Ratcheting Implementation Protocol              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "🔧 Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✓ UV installed"
    echo ""
    export PATH="$HOME/.cargo/bin:$PATH"
fi

echo "✓ UV is installed: $(uv --version)"
echo ""

# Sync dependencies
echo "📦 Syncing CRIPT dependencies..."
uv sync --group dev

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   Setup Complete! ✓                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "1. Activate virtual environment:"
echo "   source .venv/bin/activate"
echo ""
echo "2. Run tests:"
echo "   uv run pytest tests/ -v"
echo ""
echo "3. Run examples:"
echo "   uv run python examples/01_basic.py"
echo ""
echo "4. Start server:"
echo "   uv run python -m cript.network.server"
echo ""
echo "5. View documentation:"
echo "   cat UV_GUIDE.md"
echo "   cat README.md"
echo ""
