#!/usr/bin/env python3
"""
Comprehensive Test Runner for Video Narratives Project
=======================================================

This script runs all tests including:
- Unit tests (database functionality)
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
        self.log("Running Unit Tests (Database functionality)...", "RUNNING")

        try:
            # Set test environment
            env = os.environ.copy()
            env["NARRATIVES_DB_PATH"] = "test_temp_db.xlsx"

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
            # Set test environment
            env = os.environ.copy()
            env["NARRATIVES_DB_PATH"] = "test_temp_db.xlsx"

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

    def verify_production_protection(self) -> bool:
        """Ensure production database is protected during testing"""
        self.log("Verifying production database protection...", "TEST")

        current_db_path = os.getenv("NARRATIVES_DB_PATH")
        if current_db_path:
            if "test" in current_db_path.lower() or "temp" in current_db_path.lower():
                self.log("✓ Using test database - production protected", "SUCCESS")
                return True
            else:
                self.log("⚠️  WARNING: Production database path detected!", "ERROR")
                self.log(f"Current path: {current_db_path}", "ERROR")
                return False
        else:
            self.log("✓ No database path set - will use test database", "SUCCESS")
            return True

    def run_all_tests(self, test_type: str = "all") -> bool:
        """Run all or specific types of tests"""
        self.log("Starting Comprehensive Test Suite", "RUNNING")
        self.log(f"Test Type: {test_type}", "INFO")
        print("=" * 50)

        # Verify production protection first
        if not self.verify_production_protection():
            self.log("Production protection check failed - aborting tests", "ERROR")
            return False

        all_passed = True

        if test_type in ["all", "unit"]:
            self.results["unit"] = self.run_unit_tests()
            all_passed &= self.results["unit"]
            print("-" * 30)

        if test_type in ["all", "integration"]:
            self.results["integration"] = self.run_integration_tests()
            all_passed &= self.results["integration"]
            print("-" * 30)

        if test_type in ["all", "ui"]:
            self.results["ui"] = self.run_ui_tests()
            all_passed &= self.results["ui"]
            print("-" * 30)

        # Print summary
        print("=" * 50)
        self.log("Test Results Summary:", "INFO")

        for test_name, passed in self.results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"  {test_name.title():<12}: {status}")

        print("=" * 50)

        if all_passed:
            self.log("All tests passed!", "SUCCESS")
        else:
            self.log("Some tests failed!", "ERROR")

        return all_passed


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run comprehensive tests for Video Narratives project"
    )
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "ui"],
        default="all",
        help="Type of tests to run (default: all)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable extra verbose output (shows print statements and more details)",
    )

    args = parser.parse_args()

    # Set test environment
    os.environ["NARRATIVES_DB_PATH"] = "test_temp_db.xlsx"

    runner = ComprehensiveTestRunner(verbose=args.verbose)
    success = runner.run_all_tests(args.type)

    return success


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
