#!/bin/bash
# cleanup.sh - Remove Python cache files and other temporary files

echo "🧹 Cleaning up Python cache files and temporary files..."

# Remove Python cache files
find . -name "*.pyc" -not -path "./.venv/*" -delete
find . -name "*.pyo" -not -path "./.venv/*" -delete
find . -name "__pycache__" -not -path "./.venv/*" -type d -exec rm -rf {} + 2>/dev/null

# Remove pytest cache
rm -rf .pytest_cache

# Remove editor temporary files
find . -name "*.swp" -delete
find . -name "*.swo" -delete
find . -name "*~" -delete

# Remove OS-specific files
find . -name ".DS_Store" -delete
find . -name "Thumbs.db" -delete

echo "✅ Cleanup completed!"
