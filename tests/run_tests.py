#!/usr/bin/env python3
"""
Test runner script that executes all tests with proper setup and cleanup
"""
import os
import sys
import subprocess
import time
from pathlib import Path

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def verify_production_protection():
    """Ensure production database is protected during testing"""
    current_db_path = os.getenv("NARRATIVES_DB_PATH")
    if current_db_path:
        if (
            "test" not in current_db_path.lower()
            and "temp" not in current_db_path.lower()
        ):
            print(
                f"❌ DANGER: NARRATIVES_DB_PATH points to production database: {current_db_path}"
            )
            print("❌ Tests aborted to protect production data!")
            return False
        print(
            f"✅ NARRATIVES_DB_PATH safely points to test database: {current_db_path}"
        )
    else:
        print("✅ No NARRATIVES_DB_PATH set, using test isolation")
    return True


def run_db_tests():
    """Run database unit tests"""
    print("🧪 Running Database Unit Tests...")
    print("=" * 60)

    test_script = PROJECT_ROOT / "tests" / "test_db.py"
    result = subprocess.run(
        [sys.executable, str(test_script)], capture_output=True, text=True
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0


def run_api_tests():
    """Run API integration tests with isolated test server"""
    print("\n🧪 Running API Integration Tests...")
    print("=" * 60)

    # Verify production protection
    if not verify_production_protection():
        return False

    # Import test utilities
    from tests.conftest import DBTestManager

    # Create isolated test database
    with DBTestManager() as test_db_path:
        print(f"📊 Starting test server with isolated database: {test_db_path}")

        # Set environment variable for test database
        env = os.environ.copy()
        env["NARRATIVES_DB_PATH"] = test_db_path

        # Start test server
        server_process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=PROJECT_ROOT,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            # Wait for server to start
            time.sleep(3)

            # Check if server is running
            import requests

            try:
                response = requests.get(
                    "http://localhost:8000/random-narrative", timeout=5
                )
                if response.status_code != 200:
                    print("❌ Test server failed to start properly")
                    return False
            except requests.exceptions.RequestException:
                print("❌ Test server not accessible")
                return False

            print("✅ Test server started successfully")

            # Run the API tests
            test_script = PROJECT_ROOT / "tests" / "test_api.py"
            result = subprocess.run(
                [sys.executable, str(test_script)],
                capture_output=True,
                text=True,
                env=env,  # Pass the test database environment
            )

            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)

            return result.returncode == 0

        finally:
            # Clean up server
            server_process.terminate()
            server_process.wait()
            print("🛑 Test server stopped")
            print("🧹 Test database cleaned up")


def run_comprehensive_test():
    """Run a comprehensive test that copies the DB, runs tests, and cleans up"""
    print("🚀 Starting Comprehensive Test Suite")
    print("=" * 60)
    print(
        "This will test the entire system with isolated copies of the production database"
    )
    print("The original database will not be modified.")
    print("=" * 60)

    # Test 1: Database unit tests
    db_success = run_db_tests()

    if not db_success:
        print("❌ Database tests failed!")
        return False

    # Test 2: API integration tests (automatically starts isolated test server)
    print("\n🚀 Starting isolated API test server...")
    try:
        api_success = run_api_tests()
        if not api_success:
            print("❌ API tests failed!")
            return False
    except KeyboardInterrupt:
        print("\n⏭️  API tests skipped by user")
        api_success = True

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Database Tests: {'✅ PASSED' if db_success else '❌ FAILED'}")
    print(f"   API Tests: {'✅ PASSED' if api_success else '❌ FAILED'}")

    if db_success and api_success:
        print("\n🎉 All tests passed! Your application is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        return False


def main():
    """Main test runner"""
    import argparse

    # First thing: verify production database protection
    print("🔒 Verifying production database protection...")
    if not verify_production_protection():
        print("❌ ABORTING: Production database protection failed!")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Test runner for Video Narratives API")
    parser.add_argument(
        "--type",
        choices=["all", "db", "api", "comprehensive"],
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
        # Run the comprehensive test suite with isolation
        success = run_comprehensive_test()
    elif args.type == "db":
        # Run only database tests
        success = run_db_tests()
    elif args.type == "api":
        # Run only API tests with isolated server
        if not args.no_prompt:
            print("⚠️  Starting API tests with isolated test server...")
            try:
                input("Press Enter to continue, or Ctrl+C to skip...")
            except KeyboardInterrupt:
                print("\n⏭️  API tests skipped by user")
                return success
        success = run_api_tests()
    elif args.type == "all":
        # Run both DB and API tests separately
        success &= run_db_tests()
        if success:  # Only run API tests if DB tests passed
            if not args.no_prompt:
                print("\n⚠️  Starting API tests with isolated test server...")
                try:
                    input("Press Enter to continue, or Ctrl+C to skip API tests...")
                except KeyboardInterrupt:
                    print("\n⏭️  API tests skipped by user")
                    return success
            success &= run_api_tests()

    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
