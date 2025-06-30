#!/usr/bin/env python3
"""
Comprehensive Test Runner for Video Narratives Project
=======================================================

This script runs all tests including:
- Unit tests (Google Sheets functionality)
- Integration tests (API endpoints)
- UI tests (HTML validation)

By default, shows individual test names and results.
Use --verbose for even more detailed output including print statements.

Usage:
    python tests/run_all_tests.py [--type all|unit|integration|ui] [--verbose]
"""
import os
import sys
import subprocess
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class ComprehensiveTestRunner:
    """Runs all tests for the Video Narratives project"""

    def __init__(self, verbose: bool = False):
        self.results: Dict[str, bool] = {}
        self.project_root = PROJECT_ROOT
        self.tests_dir = PROJECT_ROOT / "tests"
        self.verbose = verbose

    def log(self, message: str, level: str = "INFO"):
        """Log messages with consistent formatting"""
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️ ",
            "TEST": "🧪",
            "RUNNING": "🚀",
        }.get(level, "")
        print(f"{prefix} {message}")

    def run_unit_tests(self) -> bool:
        """Run unit tests using pytest"""
        self.log("Running Unit Tests (Google Sheets functionality)...", "RUNNING")

        try:
            # Set test environment for Google Sheets
            env = os.environ.copy()
            # No longer need NARRATIVES_DB_PATH since we use Google Sheets

            # Run pytest on unittest directory
            unittest_dir = self.tests_dir / "unittest"
            if not unittest_dir.exists():
                self.log("No unit tests found", "WARNING")
                return True

            cmd = (
                [sys.executable, "-m", "pytest", str(unittest_dir), "-v", "-s"]
                if self.verbose
                else [sys.executable, "-m", "pytest", str(unittest_dir), "-v"]
            )
            result = subprocess.run(cmd, env=env, capture_output=False)

            if result.returncode == 0:
                self.log("Unit tests passed", "SUCCESS")
                return True
            else:
                self.log("Unit tests failed", "ERROR")
                return False

        except Exception as e:
            self.log(f"Error running unit tests: {e}", "ERROR")
            return False

    def run_integration_tests(self) -> bool:
        """Run integration tests"""
        self.log("Running Integration Tests (API endpoints)...", "RUNNING")

        try:
            # Set test environment for Google Sheets
            env = os.environ.copy()
            # No longer need NARRATIVES_DB_PATH since we use Google Sheets

            # Check if we need to start the server for integration tests
            integration_dir = self.tests_dir / "integration"
            if not integration_dir.exists():
                self.log("No integration tests found", "WARNING")
                return True

            # Run pytest on integration directory
            cmd = (
                [sys.executable, "-m", "pytest", str(integration_dir), "-v", "-s"]
                if self.verbose
                else [sys.executable, "-m", "pytest", str(integration_dir), "-v"]
            )
            result = subprocess.run(cmd, env=env, capture_output=False)

            if result.returncode == 0:
                self.log("Integration tests passed", "SUCCESS")
                return True
            else:
                self.log("Integration tests failed", "ERROR")
                return False

        except Exception as e:
            self.log(f"Error running integration tests: {e}", "ERROR")
            return False

    def run_ui_tests(self) -> bool:
        """Run UI tests (HTML validation)"""
        self.log("Running UI Tests (HTML validation)...", "RUNNING")

        try:
            ui_dir = self.tests_dir / "ui"
            if not ui_dir.exists():
                self.log("No UI tests found", "WARNING")
                return True

            # Run pytest on UI directory
            cmd = (
                [sys.executable, "-m", "pytest", str(ui_dir), "-v", "-s"]
                if self.verbose
                else [sys.executable, "-m", "pytest", str(ui_dir), "-v"]
            )
            result = subprocess.run(cmd, capture_output=False)

            if result.returncode == 0:
                self.log("UI tests passed", "SUCCESS")
                return True
            else:
                self.log("UI tests failed", "ERROR")
                return False

        except Exception as e:
            self.log(f"Error running UI tests: {e}", "ERROR")
            return False

    def verify_google_sheets_environment(self) -> bool:
        """Ensure Google Sheets environment is properly configured for testing"""
        self.log("Verifying Google Sheets test environment...", "TEST")

        # Check if Google Sheets credentials are configured
        credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
        sheet_id = os.getenv("GOOGLE_SHEETS_ID")

        if credentials_path and sheet_id:
            self.log("✓ Google Sheets environment configured", "SUCCESS")
            return True
        else:
            self.log(
                "ℹ️  Google Sheets not configured - some tests may be skipped", "WARNING"
            )
            return True  # Don't fail tests if Google Sheets isn't configured

    def run_all_tests(self, test_type: str = "all") -> bool:
        """Run all or specific types of tests"""
        self.log("Starting Comprehensive Test Suite", "RUNNING")
        self.log(f"Test Type: {test_type}", "INFO")
        print("=" * 50)

        # Verify Google Sheets environment first
        if not self.verify_google_sheets_environment():
            self.log("Google Sheets environment check failed - aborting tests", "ERROR")
            return False

        all_passed = True

        if test_type in ["all", "unit"]:
            print("-" * 30)
            unit_passed = self.run_unit_tests()
            self.results["Unit"] = unit_passed
            all_passed = all_passed and unit_passed

        if test_type in ["all", "integration"]:
            print("-" * 30)
            integration_passed = self.run_integration_tests()
            self.results["Integration"] = integration_passed
            all_passed = all_passed and integration_passed

        if test_type in ["all", "ui"]:
            print("-" * 30)
            ui_passed = self.run_ui_tests()
            self.results["Ui"] = ui_passed
            all_passed = all_passed and ui_passed

        # Summary
        print("=" * 50)
        self.log("Test Results Summary:", "INFO")
        for test_name, passed in self.results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            self.log(f"  {test_name:<12}: {status}", "INFO")

        print("=" * 50)
        if all_passed:
            self.log("All tests passed! 🎉", "SUCCESS")
        else:
            self.log("Some tests failed!", "ERROR")

        return all_passed


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run comprehensive tests for Video Narratives API"
    )
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "ui"],
        default="all",
        help="Type of tests to run (default: all)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    runner = ComprehensiveTestRunner(verbose=args.verbose)
    success = runner.run_all_tests(args.type)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
