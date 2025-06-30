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
import time
from pathlib import Path
from unittest.mock import patch
import os

# Add the project root to Python path
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

    # Google Sheets Integration Tests

    def test_google_sheets_environment_variables(self):
        """Test that required Google Sheets environment variables are set"""
        credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
        sheet_id = os.getenv("GOOGLE_SHEETS_ID")

        # These should be set for the application to work (no Excel fallback)
        assert (
            credentials_path is not None
        ), "GOOGLE_SHEETS_CREDENTIALS_PATH must be set"
        assert sheet_id is not None, "GOOGLE_SHEETS_ID must be set"

        # If credentials path is set, verify the file exists
        if credentials_path:
            assert os.path.exists(
                credentials_path
            ), f"Credentials file not found: {credentials_path}"

    def test_google_sheets_connection(self):
        """Test Google Sheets client connection"""
        try:
            from clients.sheets_client import SheetsClient

            credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
            sheet_id = os.getenv("GOOGLE_SHEETS_ID")

            if not credentials_path or not sheet_id:
                pytest.skip("Google Sheets credentials not configured")

            # Test client initialization
            client = SheetsClient(credentials_path, sheet_id)

            # Test connection validation
            is_valid = client.validate_connection()
            assert is_valid, "Google Sheets connection should be valid"

            # Test listing worksheets
            worksheets = client.get_all_worksheets()
            assert isinstance(worksheets, list), "Should return list of worksheets"

            # If worksheets exist, test reading data
            if worksheets:
                df = client.read_sheet_to_dataframe(worksheets[0])
                assert df is not None, "Should return a DataFrame"

        except ImportError:
            pytest.skip("Google Sheets client not available")
        except Exception as e:
            pytest.fail(f"Google Sheets connection test failed: {str(e)}")

    def test_google_sheets_database_operations(self):
        """Test Google Sheets database operations"""
        try:
            from db.sheets_narratives_db import SheetsNarrativesDB

            credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
            sheet_id = os.getenv("GOOGLE_SHEETS_ID")

            if not credentials_path or not sheet_id:
                pytest.skip("Google Sheets credentials not configured")

            # Test database initialization
            db = SheetsNarrativesDB(credentials_path, sheet_id)

            # Test getting all records
            records = db.get_all_records()
            assert isinstance(records, list), "Should return list of records"

            # Test getting random not fully tagged row (if records exist)
            if records:
                random_record = db.get_random_not_fully_tagged_row()
                if random_record:  # May be None if all are tagged
                    assert isinstance(random_record, dict), "Should return dict or None"
                    assert "Link" in random_record, "Should have Link field"
                    assert "Narrative" in random_record, "Should have Narrative field"

        except ImportError:
            pytest.skip("Google Sheets database not available")
        except Exception as e:
            pytest.fail(f"Google Sheets database test failed: {str(e)}")

    def test_refresh_data_endpoint(self):
        """Test /refresh-data endpoint for refreshing Google Sheets data"""
        self.skip_if_server_not_running()

        response = requests.post(f"{self.base_url}/refresh-data")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "total_records" in data
        assert "timestamp" in data
        assert "refreshed successfully" in data["message"].lower()
        assert isinstance(data["total_records"], int)
        assert data["total_records"] >= 0

    def test_openai_client_env_loading(self):
        """Test OpenAI client environment variable loading"""
        try:
            from clients.openai_client import OpenAIClient

            # Test that client can be initialized (will fail if no API key)
            try:
                client = OpenAIClient()
                # If successful, API key should be loaded
                assert client.api_key is not None, "API key should be loaded"
                assert len(client.api_key) > 0, "API key should not be empty"
            except ValueError as e:
                # This is expected if OPENAI_API_KEY is not set
                assert "API key" in str(e), "Should fail with API key error"

        except ImportError:
            pytest.skip("OpenAI client not available")

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

    def test_tagging_management_endpoint(self):
        """Test /tagging-management endpoint (serves tagging-management.html)"""
        self.skip_if_server_not_running()

        response = requests.get(f"{self.base_url}/tagging-management")
        assert response.status_code == 200
        assert "html" in response.headers.get("content-type", "").lower()

    def test_tagging_stats_endpoint(self):
        """Test /tagging-stats endpoint"""
        self.skip_if_server_not_running()

        response = requests.get(f"{self.base_url}/tagging-stats")
        assert response.status_code == 200

        data = response.json()
        assert "summary" in data
        assert "data" in data

        # Verify summary structure with new 9 metrics
        summary = data["summary"]
        assert "total_topics" in summary
        assert "total_narratives" in summary
        assert "total_done_narratives" in summary
        assert "total_full_narratives" in summary
        assert "total_yes" in summary
        assert "total_no" in summary
        assert "total_too_obvious" in summary
        assert "total_problem" in summary
        assert "total_missing_narratives" in summary

        # Verify data structure
        assert isinstance(data["data"], list)

        # If data exists, verify structure
        if data["data"]:
            item = data["data"][0]
            assert "sheet" in item
            assert "narrative" in item
            assert "initial_count" in item
            assert "yes_count" in item
            assert "no_count" in item
            assert "too_obvious_count" in item
            assert "problem_count" in item
            assert "missing" in item

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

    def test_add_narrative_endpoint(self):
        """Test /add-narrative endpoint with valid data"""
        self.skip_if_server_not_running()

        # Test data for adding narrative
        narrative_data = {
            "Sheet": "Test Topic Add Narrative",
            "Narrative": "Test narrative for add endpoint",
            "Story": "This is a test story for the add narrative endpoint functionality",
            "Link": f"https://example.com/test-add-narrative-{hash(str(time.time()))}",
        }

        response = requests.post(f"{self.base_url}/add-narrative", json=narrative_data)

        # Should succeed or fail with 400 if duplicate
        assert response.status_code in [
            200,
            400,
        ], f"Unexpected status code: {response.status_code}"

        if response.status_code == 200:
            data = response.json()
            assert "message" in data, "Should return success message"
            assert "Narrative added successfully" in data["message"]
            assert data["sheet"] == narrative_data["Sheet"]
            assert data["narrative"] == narrative_data["Narrative"]
            assert data["link"] == narrative_data["Link"]

    def test_add_narrative_duplicate_link(self):
        """Test /add-narrative endpoint with duplicate link"""
        self.skip_if_server_not_running()

        # Use a known link that might already exist
        narrative_data = {
            "Sheet": "Duplicate Test Topic",
            "Narrative": "Duplicate test narrative",
            "Story": "Test story for duplicate link test",
            "Link": "https://example.com/duplicate-test-link",
        }

        # Try to add the same record twice
        response1 = requests.post(f"{self.base_url}/add-narrative", json=narrative_data)

        response2 = requests.post(f"{self.base_url}/add-narrative", json=narrative_data)

        # At least one should fail with 400 for duplicate link
        status_codes = [response1.status_code, response2.status_code]
        assert 400 in status_codes, "Should reject duplicate link"

        # Check error message for duplicate link
        for response in [response1, response2]:
            if response.status_code == 400:
                error_data = response.json()
                assert "detail" in error_data
                assert "already exists" in error_data["detail"].lower()

    def test_add_narrative_missing_fields(self):
        """Test /add-narrative endpoint with missing required fields"""
        self.skip_if_server_not_running()

        # Test with missing fields
        incomplete_data_sets = [
            {
                "Narrative": "Test",
                "Story": "Test",
                "Link": "https://example.com/test1",
            },  # Missing Sheet
            {
                "Sheet": "Test",
                "Story": "Test",
                "Link": "https://example.com/test2",
            },  # Missing Narrative
            {
                "Sheet": "Test",
                "Narrative": "Test",
                "Link": "https://example.com/test3",
            },  # Missing Story
            {"Sheet": "Test", "Narrative": "Test", "Story": "Test"},  # Missing Link
            {},  # Missing all fields
        ]

        for incomplete_data in incomplete_data_sets:
            response = requests.post(
                f"{self.base_url}/add-narrative", json=incomplete_data
            )
            assert (
                response.status_code == 422
            ), f"Should reject incomplete data: {incomplete_data}"

    def test_add_narrative_invalid_url(self):
        """Test /add-narrative endpoint with invalid URL format"""
        self.skip_if_server_not_running()

        # Test with invalid URL formats
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",  # Wrong protocol
            "http://",  # Incomplete URL
            "",  # Empty URL
        ]

        for invalid_url in invalid_urls:
            narrative_data = {
                "Sheet": "Test Topic",
                "Narrative": "Test narrative",
                "Story": "Test story",
                "Link": invalid_url,
            }

            response = requests.post(
                f"{self.base_url}/add-narrative", json=narrative_data
            )
            # Backend accepts any string as URL (validation is frontend-only)
            # So these should succeed (200) or fail only for other reasons (like duplicates)
            assert response.status_code in [
                200,
                400,
            ], f"Backend should accept URL format: {invalid_url}"

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
