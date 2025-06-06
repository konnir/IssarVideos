#!/usr/bin/env python3
"""
API Integration Tests for Video Narratives FastAPI Application
============================================================

This module contains comprehensive integration tests for all API endpoints
using the FastAPI TestClient with isolated test database.
"""
import os
import sys
import json
import requests
from pathlib import Path

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class APITester:
    """API integration tester with comprehensive endpoint coverage"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []

    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        prefix = {"INFO": "ℹ️ ", "SUCCESS": "✅", "ERROR": "❌", "TEST": "🧪"}.get(
            level, ""
        )
        print(f"{prefix} {message}")

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        self.log("Testing health endpoint...", "TEST")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log("Health endpoint working correctly", "SUCCESS")
                    return True
                else:
                    self.log(f"Unexpected health response: {data}", "ERROR")
                    return False
            else:
                self.log(
                    f"Health endpoint returned status {response.status_code}", "ERROR"
                )
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"Health endpoint failed: {e}", "ERROR")
            return False

    def test_random_narrative_endpoint(self):
        """Test the random narrative endpoint"""
        self.log("Testing random narrative endpoint...", "TEST")
        try:
            response = requests.get(f"{self.base_url}/random-narrative", timeout=10)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["Link", "Title", "Tagger_1"]
                if all(field in data for field in required_fields):
                    self.log("Random narrative endpoint working correctly", "SUCCESS")
                    return True
                else:
                    self.log(f"Missing required fields in response: {data}", "ERROR")
                    return False
            elif response.status_code == 404:
                self.log(
                    "No untagged narratives found (this is normal for fully tagged databases)",
                    "SUCCESS",
                )
                return True
            else:
                self.log(
                    f"Random narrative endpoint returned status {response.status_code}",
                    "ERROR",
                )
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"Random narrative endpoint failed: {e}", "ERROR")
            return False

    def test_all_records_endpoint(self):
        """Test the all records endpoint"""
        self.log("Testing all records endpoint...", "TEST")
        try:
            response = requests.get(f"{self.base_url}/all-records", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log(
                        f"All records endpoint working correctly (returned {len(data)} records)",
                        "SUCCESS",
                    )
                    return True
                else:
                    self.log(f"Unexpected response format: {type(data)}", "ERROR")
                    return False
            else:
                self.log(
                    f"All records endpoint returned status {response.status_code}",
                    "ERROR",
                )
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"All records endpoint failed: {e}", "ERROR")
            return False

    def test_leaderboard_endpoint(self):
        """Test the leaderboard endpoint"""
        self.log("Testing leaderboard endpoint...", "TEST")
        try:
            response = requests.get(f"{self.base_url}/leaderboard", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log(
                        f"Leaderboard endpoint working correctly (returned {len(data)} users)",
                        "SUCCESS",
                    )
                    return True
                else:
                    self.log(f"Unexpected response format: {type(data)}", "ERROR")
                    return False
            else:
                self.log(
                    f"Leaderboard endpoint returned status {response.status_code}",
                    "ERROR",
                )
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"Leaderboard endpoint failed: {e}", "ERROR")
            return False

    def test_user_tagged_count_endpoint(self):
        """Test the user tagged count endpoint"""
        self.log("Testing user tagged count endpoint...", "TEST")
        try:
            test_username = "test_user"
            response = requests.get(
                f"{self.base_url}/user-tagged-count/{test_username}", timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if "username" in data and "tagged_count" in data:
                    self.log("User tagged count endpoint working correctly", "SUCCESS")
                    return True
                else:
                    self.log(f"Missing required fields in response: {data}", "ERROR")
                    return False
            else:
                self.log(
                    f"User tagged count endpoint returned status {response.status_code}",
                    "ERROR",
                )
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"User tagged count endpoint failed: {e}", "ERROR")
            return False

    def test_static_files(self):
        """Test static file serving"""
        self.log("Testing static file serving...", "TEST")
        try:
            # Test main tagger page
            response = requests.get(f"{self.base_url}/", timeout=10)
            if (
                response.status_code == 200
                and "html" in response.headers.get("content-type", "").lower()
            ):
                self.log("Main tagger page serving correctly", "SUCCESS")
                return True
            else:
                self.log(f"Main page returned status {response.status_code}", "ERROR")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"Static file serving failed: {e}", "ERROR")
            return False

    def run_all_tests(self):
        """Run all API tests"""
        self.log("Starting API Integration Tests", "TEST")
        print("=" * 60)

        tests = [
            ("Health Check", self.test_health_endpoint),
            ("Random Narrative", self.test_random_narrative_endpoint),
            ("All Records", self.test_all_records_endpoint),
            ("Leaderboard", self.test_leaderboard_endpoint),
            ("User Tagged Count", self.test_user_tagged_count_endpoint),
            ("Static Files", self.test_static_files),
        ]

        results = {}
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                self.log(f"Test {test_name} crashed: {e}", "ERROR")
                results[test_name] = False

        # Print summary
        print("\n" + "=" * 60)
        self.log("API Test Summary:", "INFO")

        passed = 0
        total = len(results)

        for test_name, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {test_name}: {status}")
            if success:
                passed += 1

        print(f"\nTotal: {passed}/{total} tests passed")

        if passed == total:
            self.log("All API tests passed!", "SUCCESS")
            return True
        else:
            self.log(f"{total - passed} API tests failed", "ERROR")
            return False


def main():
    """Main entry point for API tests"""
    # Check if server is running
    tester = APITester()

    # First verify the server is accessible
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Test server is not responding correctly")
            return False
    except requests.exceptions.RequestException:
        print("❌ Test server is not accessible at http://localhost:8000")
        print("💡 Make sure the test server is running before running API tests")
        return False

    # Run all tests
    return tester.run_all_tests()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
