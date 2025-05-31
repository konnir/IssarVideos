#!/usr/bin/env python3
"""
Integration tests for the FastAPI endpoints
"""
import pytest
import requests
import urllib.parse
import time
import subprocess
import signal
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.conftest import (
    DBTestManager,
    get_test_record_data,
    get_test_update_data,
    verify_production_db_protection,
)


class TestAPIEndpoints:
    """Test suite for FastAPI endpoints"""

    BASE_URL = "http://localhost:8000"

    @classmethod
    def setup_class(cls):
        """Set up test server with test database"""
        # First, verify production database protection
        verify_production_db_protection()

        cls.test_db_manager = DBTestManager()
        cls.test_db_path = cls.test_db_manager.__enter__()

        # Start the test server in background with test database
        cls.server_process = None
        print("🚀 Starting test server with test database...")

        # Set environment variable for test database path
        import os
        import subprocess
        import time
        import sys
        from pathlib import Path

        # Get project root
        project_root = Path(__file__).parent.parent

        # Start server with test database path
        env = os.environ.copy()
        env["NARRATIVES_DB_PATH"] = cls.test_db_path

        cls.server_process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=project_root,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait for server to start
        time.sleep(3)
        print(f"📊 Test server started with database: {cls.test_db_path}")

    @classmethod
    def teardown_class(cls):
        """Clean up test server and database"""
        if cls.server_process:
            cls.server_process.terminate()
            cls.server_process.wait()
            print("🛑 Test server stopped")

        cls.test_db_manager.__exit__(None, None, None)
        print("🧹 Test cleanup completed")

    def test_get_random_narrative(self):
        """Test GET /random-narrative endpoint"""
        response = requests.get(f"{self.BASE_URL}/random-narrative")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        assert "Link" in data, "Response should contain Link"
        assert "Narrative" in data, "Response should contain Narrative"
        assert "Platform" in data, "Response should contain Platform"

        print(f"✅ Random narrative: {data['Link']}")
        return data

    def test_add_record_endpoint(self):
        """Test POST /add-record endpoint"""
        import uuid

        test_record = get_test_record_data()
        # Make link unique for this test with UUID
        unique_id = str(uuid.uuid4())
        test_record["Link"] = f"https://test.com/api-test-{unique_id}"

        response = requests.post(f"{self.BASE_URL}/add-record", json=test_record)

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        assert data["Link"] == test_record["Link"], "Link should match"
        assert data["Title"] == test_record["Title"], "Title should match"

        print(f"✅ Added record: {data['Link']}")
        return data

    def test_update_record_endpoint(self):
        """Test PUT /update-record endpoint"""
        # First add a record to update
        test_record = self.test_add_record_endpoint()

        # Update the record
        update_data = get_test_update_data()
        encoded_link = urllib.parse.quote(test_record["Link"], safe="")

        response = requests.put(
            f"{self.BASE_URL}/update-record/{encoded_link}", json=update_data
        )

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        assert "message" in data, "Response should contain message"
        assert "updated_fields" in data, "Response should contain updated_fields"
        assert "Tagger_1" in data["updated_fields"], "Should update Tagger_1"

        print(f"✅ Updated record: {data['message']}")
        return data

    def test_get_all_records_endpoint(self):
        """Test GET /all-records endpoint"""
        response = requests.get(f"{self.BASE_URL}/all-records")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Should have at least one record"

        print(f"✅ Retrieved {len(data)} total records")
        return data

    def test_get_records_by_sheet_endpoint(self):
        """Test GET /records-by-sheet/{sheet_name} endpoint"""
        response = requests.get(f"{self.BASE_URL}/records-by-sheet/Political")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        assert isinstance(data, list), "Response should be a list"

        # Check that all records are from Political sheet
        for record in data:
            assert (
                record["Sheet"] == "Political"
            ), "All records should be from Political sheet"

        print(f"✅ Retrieved {len(data)} Political records")
        return data

    def test_add_duplicate_record(self):
        """Test adding a record with duplicate link"""
        import uuid

        test_record = get_test_record_data()
        # Use a fixed link for duplicate testing
        test_record["Link"] = f"https://test.com/duplicate-test-{str(uuid.uuid4())[:8]}"

        # Add the record first time
        response1 = requests.post(f"{self.BASE_URL}/add-record", json=test_record)

        # Try to add the same record again
        response2 = requests.post(f"{self.BASE_URL}/add-record", json=test_record)

        assert response2.status_code == 400, "Should return 400 for duplicate link"
        print("✅ Correctly handled duplicate record")

    def test_update_nonexistent_record(self):
        """Test updating a record that doesn't exist"""
        fake_link = "https://nonexistent-test-link.com/fake"
        encoded_link = urllib.parse.quote(fake_link, safe="")
        update_data = get_test_update_data()

        response = requests.put(
            f"{self.BASE_URL}/update-record/{encoded_link}", json=update_data
        )

        assert response.status_code == 404, "Should return 404 for non-existent record"
        print("✅ Correctly handled non-existent record update")

    # Additional standalone test methods from root test_api.py
    def test_standalone_random_narrative(self):
        """Test getting a random narrative (standalone style)"""
        print("Testing GET /random-narrative...")
        response = requests.get(f"{self.BASE_URL}/random-narrative")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "Link" in data, "Response should contain Link"

        print(f"✅ Success: Got random narrative with link: {data['Link']}")
        return data

    def test_standalone_add_record(self):
        """Test adding a new record (standalone style)"""
        import uuid

        print("\nTesting POST /add-record...")
        new_record = {
            "Sheet": "TestAPI",
            "Narrative": "API Testing Narrative",
            "Platform": "YouTube",
            "Title": "Test Video from API",
            "Hebrew_Title": "וידאו בדיקה מ-API",
            "Link": f"https://youtube.com/standalone-test-{str(uuid.uuid4())[:8]}",
            "Tagger_1": "APITester",
            "Tagger_1_Result": 1,
            "Tagger_2": "Init",
            "Tagger_2_Result": 0,
        }

        response = requests.post(f"{self.BASE_URL}/add-record", json=new_record)

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["Link"] == new_record["Link"], "Link should match"

        print(f"✅ Success: Added record with link: {data['Link']}")
        return data

    def test_standalone_update_record(self):
        """Test updating a record (standalone style)"""
        # First add a record to update
        test_record = self.test_standalone_add_record()

        print(f"\nTesting PUT /update-record...")
        encoded_link = urllib.parse.quote(test_record["Link"], safe="")
        update_data = {
            "Tagger_1": "UpdatedUser",
            "Tagger_1_Result": 2,
            "Tagger_2": "CompletedTag",
            "Tagger_2_Result": 2,
        }

        response = requests.put(
            f"{self.BASE_URL}/update-record/{encoded_link}", json=update_data
        )

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data, "Response should contain message"
        assert "updated_fields" in data, "Response should contain updated_fields"

        print(f"✅ Success: Updated record - {data['message']}")
        print(f"   Updated fields: {data['updated_fields']}")
        return True

    def test_standalone_get_all_records(self):
        """Test getting all records (standalone style)"""
        print(f"\nTesting GET /all-records...")
        response = requests.get(f"{self.BASE_URL}/all-records")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"

        print(f"✅ Success: Got {len(data)} total records")
        return len(data)

    def test_standalone_get_records_by_sheet(self):
        """Test getting records by sheet (standalone style)"""
        print(f"\nTesting GET /records-by-sheet/Political...")
        response = requests.get(f"{self.BASE_URL}/records-by-sheet/Political")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"

        # Check that all records are from Political sheet
        for record in data:
            assert (
                record["Sheet"] == "Political"
            ), "All records should be from Political sheet"

        print(f"✅ Success: Got {len(data)} Political records")
        return len(data)

    def test_standalone_comprehensive_flow(self):
        """Test comprehensive API flow (standalone style)"""
        print("🚀 Starting Comprehensive API Flow Test...")
        print("=" * 50)

        # Test 1: Get random narrative
        random_record = self.test_standalone_random_narrative()

        # Test 2: Add new record
        new_record = self.test_standalone_add_record()

        # Test 3: Update record (use the new record we just added)
        if new_record:
            self.test_standalone_update_record()

        # Test 4: Get all records
        total_count = self.test_standalone_get_all_records()

        # Test 5: Get records by sheet
        political_count = self.test_standalone_get_records_by_sheet()

        print("\n" + "=" * 50)
        print("📊 API Test Summary:")
        print(f"   Total records in database: {total_count}")
        print(f"   Political records: {political_count}")
        print("🎉 All standalone tests completed!")

        return True


def run_standalone_api_tests():
    """Run API tests against an existing server"""
    print("🧪 Running API Integration Tests...")
    print("=" * 50)
    print("⚠️  Make sure the server is running at http://localhost:8000")
    print("=" * 50)

    test_api = TestAPIEndpoints()

    try:
        # Test basic connectivity first
        response = requests.get(f"{test_api.BASE_URL}/random-narrative")
        if response.status_code != 200:
            print("❌ Server not accessible. Please start the server first.")
            return False

        # Run comprehensive integration tests
        test_api.test_get_random_narrative()
        test_api.test_add_record_endpoint()
        test_api.test_update_record_endpoint()
        test_api.test_get_all_records_endpoint()
        test_api.test_get_records_by_sheet_endpoint()
        test_api.test_add_duplicate_record()
        test_api.test_update_nonexistent_record()

        # Run standalone-style comprehensive flow test
        test_api.test_standalone_comprehensive_flow()

        print("=" * 50)
        print("🎉 All API tests passed!")
        return True

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first:")
        print("   python3 main.py")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_standalone_api_tests()
    exit(0 if success else 1)
