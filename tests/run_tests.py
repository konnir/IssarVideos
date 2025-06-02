#!/usr/bin/env python3
"""
Legacy test runner - DEPRECATED
Use tests/test_runner.py for comprehensive testing
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

print("⚠️  DEPRECATED: This test runner is deprecated.")
print("✨ Use the new comprehensive test runner instead:")
print("   python tests/test_runner.py")
print("")
print("🔄 Redirecting to new test runner...")
print("")

# Import and run the new test runner
try:
    from test_runner import main

    sys.exit(0 if main() else 1)
except ImportError:
    print("❌ Could not import new test runner")
    print("💡 Please run: python tests/test_runner.py")
    sys.exit(1)
