#!/usr/bin/env python3
"""
Video Narratives Project - Test Runner
=====================================

This is the main entry point for running all tests in the Video Narratives project.
It provides a comprehensive test suite that covers:

- Database unit tests
- API integration tests
- UI/HTML validation tests
- Production protection tests

Usage:
    python run_tests.py [--type all|db|api|ui|protection|comprehensive] [--no-prompt]

Examples:
    python run_tests.py                    # Run comprehensive test suite
    python run_tests.py --type db          # Run only database tests
    python run_tests.py --type api         # Run only API tests
    python run_tests.py --no-prompt        # Skip interactive prompts
"""
import sys
from pathlib import Path

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    # Import the comprehensive test runner
    from tests.test_runner import main

    print("🚀 Video Narratives Test Suite")
    print("=" * 40)

    # Run the tests
    success = main()

    print("\n" + "=" * 40)
    if success:
        print("🎉 Test suite completed successfully!")
    else:
        print("❌ Test suite completed with failures!")

    sys.exit(0 if success else 1)

except ImportError as e:
    print(f"❌ Failed to import test runner: {e}")
    print("💡 Please ensure you're in the project root directory")
    print("💡 And that all dependencies are installed")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
