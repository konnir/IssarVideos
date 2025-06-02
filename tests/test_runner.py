#!/usr/bin/env python3
"""
Comprehensive Test Runner for Video Narratives Project
===============================================

This script runs all tests for the Video Narratives project including:
- Database unit tests
- API integration tests
- HTML/UI tests validation
- Production protection tests

Usage:
    python tests/test_runner.py [--type all|db|api|ui|protection] [--no-prompt]
"""
import os
import sys
import subprocess
import time
import shutil
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestRunner:
    """Comprehensive test runner for the Video Narratives project"""

    def __init__(self):
        self.results: Dict[str, bool] = {}
        self.project_root = PROJECT_ROOT

    def log(self, message: str, level: str = "INFO"):
        """Log messages with consistent formatting"""
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️ ",
            "TEST": "🧪",
        }.get(level, "")
        print(f"{prefix} {message}")

    def verify_production_protection(self) -> bool:
        """Ensure production database is protected during testing"""
        self.log("Verifying production database protection...", "TEST")

        current_db_path = os.getenv("NARRATIVES_DB_PATH")
        if current_db_path:
            if (
                "test" not in current_db_path.lower()
                and "temp" not in current_db_path.lower()
            ):
                self.log(
                    f"DANGER: NARRATIVES_DB_PATH points to production database: {current_db_path}",
                    "ERROR",
                )
                self.log("Tests aborted to protect production data!", "ERROR")
                return False
            self.log(
                f"NARRATIVES_DB_PATH safely points to test database: {current_db_path}",
                "SUCCESS",
            )
        else:
            self.log("No NARRATIVES_DB_PATH set, using test isolation", "SUCCESS")
        return True

    def run_database_tests(self) -> bool:
        """Run database unit tests"""
        self.log("Running Database Unit Tests...", "TEST")
        print("=" * 60)

        test_script = self.project_root / "tests" / "test_db.py"
        if not test_script.exists():
            self.log("Database test script not found", "ERROR")
            return False

        result = subprocess.run(
            [sys.executable, str(test_script)],
            capture_output=True,
            text=True,
            cwd=self.project_root,
        )

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        success = result.returncode == 0
        self.results["database"] = success
        return success

    def run_api_tests(self) -> bool:
        """Run API integration tests with isolated test server"""
        self.log("Running API Integration Tests...", "TEST")
        print("=" * 60)

        # Verify production protection
        if not self.verify_production_protection():
            return False

        # Import test utilities
        try:
            from tests.conftest import DBTestManager
        except ImportError:
            self.log("Test utilities not found", "ERROR")
            return False

        # Create isolated test database
        with DBTestManager() as test_db_path:
            self.log(
                f"Starting test server with isolated database: {test_db_path}", "INFO"
            )

            # Set environment variable for test database
            env = os.environ.copy()
            env["NARRATIVES_DB_PATH"] = test_db_path

            # Start test server
            server_process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=self.project_root,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            try:
                # Wait for server to start
                time.sleep(3)

                # Check if server is running
                try:
                    import requests

                    response = requests.get("http://localhost:8000/health", timeout=5)
                    if response.status_code != 200:
                        self.log("Test server failed to start properly", "ERROR")
                        return False
                except requests.exceptions.RequestException:
                    self.log("Test server not accessible", "ERROR")
                    return False

                self.log("Test server started successfully", "SUCCESS")

                # Run the API tests
                test_script = self.project_root / "tests" / "test_api.py"
                if not test_script.exists():
                    self.log("API test script not found", "ERROR")
                    return False

                result = subprocess.run(
                    [sys.executable, str(test_script)],
                    capture_output=True,
                    text=True,
                    env=env,
                    cwd=self.project_root,
                )

                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)

                success = result.returncode == 0
                self.results["api"] = success
                return success

            finally:
                # Clean up server
                server_process.terminate()
                server_process.wait()
                self.log("Test server stopped", "INFO")
                self.log("Test database cleaned up", "INFO")

    def run_ui_tests(self) -> bool:
        """Validate HTML/UI test files"""
        self.log("Running UI/HTML Validation Tests...", "TEST")
        print("=" * 60)

        html_test_dir = self.project_root / "tests" / "html_tests"
        if not html_test_dir.exists():
            self.log("No HTML test files found", "WARNING")
            self.results["ui"] = True
            return True

        html_files = list(html_test_dir.glob("*.html"))
        if not html_files:
            self.log("No HTML test files found", "WARNING")
            self.results["ui"] = True
            return True

        success = True
        for html_file in html_files:
            self.log(f"Validating {html_file.name}...", "INFO")

            # Basic HTML validation - check if file is readable and has basic structure
            try:
                content = html_file.read_text()
                if "<html" in content.lower() and "</html>" in content.lower():
                    self.log(f"✓ {html_file.name} has valid HTML structure", "SUCCESS")
                else:
                    self.log(f"✗ {html_file.name} missing HTML structure", "WARNING")

            except Exception as e:
                self.log(f"✗ Error reading {html_file.name}: {e}", "ERROR")
                success = False

        self.results["ui"] = success
        return success

    def run_protection_tests(self) -> bool:
        """Run production protection tests"""
        self.log("Running Production Protection Tests...", "TEST")
        print("=" * 60)

        protection_test = self.project_root / "tests" / "test_protection.py"
        if not protection_test.exists():
            self.log("Protection test script not found", "WARNING")
            self.results["protection"] = True
            return True

        result = subprocess.run(
            [sys.executable, str(protection_test)],
            capture_output=True,
            text=True,
            cwd=self.project_root,
        )

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        success = result.returncode == 0
        self.results["protection"] = success
        return success

    def run_comprehensive_tests(self) -> bool:
        """Run all tests in the correct order"""
        self.log("Starting Comprehensive Test Suite", "TEST")
        print("=" * 60)
        self.log(
            "Testing the entire system with isolated copies of the production database",
            "INFO",
        )
        self.log("The original database will not be modified.", "INFO")
        print("=" * 60)

        # Test 1: Production Protection
        if not self.verify_production_protection():
            self.log("Production protection check failed!", "ERROR")
            return False

        # Test 2: Database unit tests
        db_success = self.run_database_tests()

        # Test 3: UI validation tests
        ui_success = self.run_ui_tests()

        # Test 4: Protection tests
        protection_success = self.run_protection_tests()

        # Test 5: API integration tests (if previous tests passed)
        api_success = True
        if db_success and ui_success and protection_success:
            try:
                api_success = self.run_api_tests()
            except KeyboardInterrupt:
                self.log("API tests skipped by user", "WARNING")
                api_success = True
        else:
            self.log("Skipping API tests due to previous failures", "WARNING")

        # Summary
        self.print_summary()

        return all([db_success, ui_success, protection_success, api_success])

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        self.log("Test Summary:", "INFO")

        test_names = {
            "database": "Database Tests",
            "ui": "UI/HTML Tests",
            "protection": "Protection Tests",
            "api": "API Tests",
        }

        for test_key, test_name in test_names.items():
            if test_key in self.results:
                status = "✅ PASSED" if self.results[test_key] else "❌ FAILED"
                print(f"   {test_name}: {status}")

        all_passed = all(self.results.values())
        if all_passed:
            self.log(
                "All tests passed! Your application is working correctly.", "SUCCESS"
            )
        else:
            self.log("Some tests failed. Please check the output above.", "ERROR")

        return all_passed


def main():
    """Main test runner entry point"""
    import argparse

    runner = TestRunner()

    # First thing: verify production database protection
    runner.log("Verifying production database protection...", "TEST")
    if not runner.verify_production_protection():
        runner.log("ABORTING: Production database protection failed!", "ERROR")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Comprehensive Test Runner for Video Narratives"
    )
    parser.add_argument(
        "--type",
        choices=["all", "db", "api", "ui", "protection", "comprehensive"],
        default="comprehensive",
        help="Type of tests to run (default: comprehensive)",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Skip prompts and run tests automatically",
    )

    args = parser.parse_args()

    success = True

    if args.type == "comprehensive":
        success = runner.run_comprehensive_tests()
    elif args.type == "all":
        # Run all test types individually
        success &= runner.run_database_tests()
        success &= runner.run_ui_tests()
        success &= runner.run_protection_tests()
        if success and not args.no_prompt:
            try:
                input("\nPress Enter to run API tests, or Ctrl+C to skip...")
                success &= runner.run_api_tests()
            except KeyboardInterrupt:
                runner.log("API tests skipped by user", "WARNING")
        elif success:
            success &= runner.run_api_tests()
        runner.print_summary()
    elif args.type == "db":
        success = runner.run_database_tests()
    elif args.type == "api":
        if not args.no_prompt:
            try:
                input("Press Enter to start API tests with isolated test server...")
            except KeyboardInterrupt:
                runner.log("API tests skipped by user", "WARNING")
                return True
        success = runner.run_api_tests()
    elif args.type == "ui":
        success = runner.run_ui_tests()
    elif args.type == "protection":
        success = runner.run_protection_tests()

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
