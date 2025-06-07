#!/usr/bin/env python3
"""
Comprehensive API Endpoint Tests
================================

Tests for all API endpoints in the FastAPI application.
This covers all 16 endpoints identified in main.py.
"""
import pytest
import requests
import json
import sys
from pathlib import Path
from unittest.mock import patch

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestAllAPIEndpoints:
    """Comprehensive tests for all API endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.base_url = "http://localhost:8000"
        self.test_video_record = {
            "Sheet": "Test Sheet",
            "Narrative": "Test narrative for comprehensive testing",
            "Story": "Test story content",
            "Link": "https://example.com/test-video-comprehensive",
        }
        self.test_update_data = {"Tagger_1": "Test User", "Tagger_1_Result": 1}
        self.auth_data = {"username": "Nir Kon", "password": "originai"}

    def skip_if_server_not_running(self):
        """Skip test if server is not running"""
        try:
            requests.get(f"{self.base_url}/health", timeout=2)
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping API tests")

    # GET Endpoint Tests

    def test_health_endpoint(self):
        """Test /health endpoint"""
        self.skip_if_server_not_running()

        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "video-narratives"

    def test_root_endpoint(self):
        """Test / endpoint (serves tagger.html)"""
        self.skip_if_server_not_running()

        response = requests.get(f"{self.base_url}/")
        assert response.status_code == 200
        assert "html" in response.headers.get("content-type", "").lower()

    def test_tagger_endpoint(self):
        """Test /tagger endpoint (alternative route)"""
        self.skip_if_server_not_running()

        response = requests.get(f"{self.base_url}/tagger")
        assert response.status_code == 200
        assert "html" in response.headers.get("content-type", "").lower()

    def test_report_endpoint(self):
        """Test /report endpoint (serves report.html)"""
        self.skip_if_server_not_running()

        response = requests.get(f"{self.base_url}/report")
        assert response.status_code == 200
        assert "html" in response.headers.get("content-type", "").lower()

    def test_random_narrative_endpoint(self):
        """Test /random-narrative endpoint"""
        self.skip_if_server_not_running()

        response = requests.get(f"{self.base_url}/random-narrative")
        # Should return 200 with a record or 404 if no untagged narratives
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            # Verify it's a valid VideoRecord structure
            assert "Sheet" in data
            assert "Narrative" in data
            assert "Link" in data

    def test_all_records_endpoint(self):
        """Test /all-records endpoint"""
        self.skip_if_server_not_running()

        response = requests.get(f"{self.base_url}/all-records")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # If records exist, verify structure
        if data:
            record = data[0]
            assert "Sheet" in record
            assert "Narrative" in record
            assert "Link" in record

    def test_records_by_sheet_endpoint(self):
        """Test /records-by-sheet/{sheet_name} endpoint"""
        self.skip_if_server_not_running()

        # Test with a sheet name (may not exist in test data)
        response = requests.get(f"{self.base_url}/records-by-sheet/Test Sheet")
        # Should return 200 with records or 404 if sheet doesn't exist
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

            if data:
                record = data[0]
                assert record["Sheet"] == "Test Sheet"

    def test_random_narrative_for_user_endpoint(self):
        """Test /random-narrative-for-user/{username} endpoint"""
        self.skip_if_server_not_running()

        response = requests.get(f"{self.base_url}/random-narrative-for-user/TestUser")
        # Should return 200 with a record or 404 if no untagged narratives for user
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "Sheet" in data
            assert "Narrative" in data
            assert "Link" in data

    def test_user_tagged_count_endpoint(self):
        """Test /user-tagged-count/{username} endpoint"""
        self.skip_if_server_not_running()

        response = requests.get(f"{self.base_url}/user-tagged-count/TestUser")
        assert response.status_code == 200

        data = response.json()
        assert "username" in data
        assert "tagged_count" in data
        assert data["username"] == "TestUser"
        assert isinstance(data["tagged_count"], int)
        assert data["tagged_count"] >= 0

    def test_leaderboard_endpoint(self):
        """Test /leaderboard endpoint"""
        self.skip_if_server_not_running()

        response = requests.get(f"{self.base_url}/leaderboard")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # If leaderboard has entries, verify structure
        if data:
            entry = data[0]
            assert "username" in entry
            assert "tagged_count" in entry
            assert isinstance(entry["tagged_count"], int)

    def test_tagged_records_endpoint(self):
        """Test /tagged-records endpoint"""
        self.skip_if_server_not_running()

        response = requests.get(f"{self.base_url}/tagged-records")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # If tagged records exist, verify structure
        if data:
            record = data[0]
            assert "Sheet" in record
            assert "Narrative" in record
            assert "Link" in record
            assert "Tagger_1" in record
            # Tagger_1 should not be empty for tagged records
            assert record["Tagger_1"] is not None
            assert record["Tagger_1"] != ""

    def test_download_excel_endpoint(self):
        """Test /download-excel endpoint"""
        self.skip_if_server_not_running()

        response = requests.get(f"{self.base_url}/download-excel")
        assert response.status_code == 200

        # Verify it's an Excel file
        content_type = response.headers.get("content-type", "")
        assert "spreadsheet" in content_type or "excel" in content_type

        # Verify content disposition header
        content_disposition = response.headers.get("content-disposition", "")
        assert "attachment" in content_disposition
        assert "narratives_report.xlsx" in content_disposition

    # POST Endpoint Tests

    def test_auth_report_endpoint_success(self):
        """Test /auth-report endpoint with valid credentials"""
        self.skip_if_server_not_running()

        response = requests.post(f"{self.base_url}/auth-report", json=self.auth_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "message" in data

    def test_auth_report_endpoint_failure(self):
        """Test /auth-report endpoint with invalid credentials"""
        self.skip_if_server_not_running()

        invalid_auth = {"username": "Invalid User", "password": "wrong_password"}

        response = requests.post(f"{self.base_url}/auth-report", json=invalid_auth)
        assert response.status_code == 401

    def test_add_record_endpoint(self):
        """Test /add-record endpoint"""
        self.skip_if_server_not_running()

        # Use a unique link to avoid conflicts
        import time

        unique_record = self.test_video_record.copy()
        unique_record["Link"] = f"https://example.com/test-video-{int(time.time())}"

        response = requests.post(f"{self.base_url}/add-record", json=unique_record)

        # Should succeed or fail with 400 if record already exists
        assert response.status_code in [200, 400]

        if response.status_code == 200:
            data = response.json()
            assert data["Sheet"] == unique_record["Sheet"]
            assert data["Narrative"] == unique_record["Narrative"]
            assert data["Link"] == unique_record["Link"]

    def test_add_record_duplicate_link(self):
        """Test /add-record endpoint with duplicate link"""
        self.skip_if_server_not_running()

        # Try to add the same record twice
        response1 = requests.post(
            f"{self.base_url}/add-record", json=self.test_video_record
        )

        response2 = requests.post(
            f"{self.base_url}/add-record", json=self.test_video_record
        )

        # Second request should fail with 400
        if response1.status_code == 200:
            assert response2.status_code == 400
        # If first failed, both should have same error
        elif response1.status_code == 400:
            assert response2.status_code == 400

    def test_tag_record_endpoint(self):
        """Test /tag-record endpoint"""
        self.skip_if_server_not_running()

        tag_request = {
            "link": "https://example.com/test-video",
            "username": "Test User",
            "result": 1,
        }

        response = requests.post(f"{self.base_url}/tag-record", json=tag_request)

        # Should succeed or fail with 404 if record not found
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "message" in data
            assert data["username"] == "Test User"
            assert data["result"] == 1

    def test_tag_record_invalid_result(self):
        """Test /tag-record endpoint with invalid result value"""
        self.skip_if_server_not_running()

        tag_request = {
            "link": "https://example.com/test-video",
            "username": "Test User",
            "result": 5,  # Invalid result (should be 1-4)
        }

        response = requests.post(f"{self.base_url}/tag-record", json=tag_request)

        assert response.status_code == 400

    # PUT Endpoint Tests

    def test_update_record_endpoint(self):
        """Test /update-record/{link:path} endpoint"""
        self.skip_if_server_not_running()

        # URL encode the link for the path parameter
        import urllib.parse

        encoded_link = urllib.parse.quote("https://example.com/test-video", safe="")

        response = requests.put(
            f"{self.base_url}/update-record/{encoded_link}", json=self.test_update_data
        )

        # Should succeed or fail with 404 if record not found
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "message" in data
            assert "updated_fields" in data
            assert "link" in data

    def test_update_record_no_data(self):
        """Test /update-record endpoint with no update data"""
        self.skip_if_server_not_running()

        import urllib.parse

        encoded_link = urllib.parse.quote("https://example.com/test-video", safe="")

        response = requests.put(
            f"{self.base_url}/update-record/{encoded_link}", json={}
        )

        assert response.status_code == 400

    # Error Handling Tests

    def test_nonexistent_endpoint(self):
        """Test accessing a non-existent endpoint"""
        self.skip_if_server_not_running()

        response = requests.get(f"{self.base_url}/nonexistent-endpoint")
        assert response.status_code == 404

    def test_method_not_allowed(self):
        """Test using wrong HTTP method on endpoints"""
        self.skip_if_server_not_running()

        # Try POST on a GET endpoint
        response = requests.post(f"{self.base_url}/health")
        assert response.status_code == 405  # Method Not Allowed

    def test_malformed_json(self):
        """Test sending malformed JSON to POST endpoints"""
        self.skip_if_server_not_running()

        response = requests.post(
            f"{self.base_url}/auth-report",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422  # Unprocessable Entity


class TestAPIEndpointIntegration:
    """Integration tests that test multiple endpoints together"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for integration tests"""
        self.base_url = "http://localhost:8000"

    def skip_if_server_not_running(self):
        """Skip test if server is not running"""
        try:
            requests.get(f"{self.base_url}/health", timeout=2)
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping integration tests")

    def test_add_and_retrieve_record_flow(self):
        """Test adding a record and then retrieving it"""
        self.skip_if_server_not_running()

        import time

        unique_record = {
            "Sheet": "Integration Test",
            "Narrative": "Integration test narrative",
            "Story": "Integration test story",
            "Link": f"https://example.com/integration-test-{int(time.time())}",
        }

        # Add the record
        add_response = requests.post(f"{self.base_url}/add-record", json=unique_record)

        if add_response.status_code == 200:
            # Retrieve all records and verify our record is there
            all_response = requests.get(f"{self.base_url}/all-records")
            assert all_response.status_code == 200

            records = all_response.json()
            our_record = next(
                (r for r in records if r["Link"] == unique_record["Link"]), None
            )
            assert our_record is not None
            assert our_record["Sheet"] == unique_record["Sheet"]
            assert our_record["Narrative"] == unique_record["Narrative"]

    def test_tag_and_leaderboard_flow(self):
        """Test tagging a record and checking leaderboard"""
        self.skip_if_server_not_running()

        # Get initial leaderboard
        leaderboard_response = requests.get(f"{self.base_url}/leaderboard")
        assert leaderboard_response.status_code == 200

        initial_leaderboard = leaderboard_response.json()

        # Try to tag a record (may fail if no records exist)
        tag_request = {
            "link": "https://example.com/test-video",
            "username": "Integration Test User",
            "result": 1,
        }

        tag_response = requests.post(f"{self.base_url}/tag-record", json=tag_request)

        # If tagging succeeded, check leaderboard again
        if tag_response.status_code == 200:
            new_leaderboard_response = requests.get(f"{self.base_url}/leaderboard")
            assert new_leaderboard_response.status_code == 200

            new_leaderboard = new_leaderboard_response.json()

            # Find our user in the leaderboard
            our_user = next(
                (
                    u
                    for u in new_leaderboard
                    if u["username"] == "Integration Test User"
                ),
                None,
            )

            if our_user:
                assert our_user["tagged_count"] > 0


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])
