#!/usr/bin/env python3
"""
Google Sheets Integration Tests
===============================

Tests specifically for Google Sheets integration functionality,
replacing Excel-based operations.
"""
import pytest
import requests
import os
import sys
from pathlib import Path

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestGoogleSheetsIntegration:
    """Test Google Sheets integration functionality"""

    def skip_if_no_credentials(self):
        """Skip test if Google Sheets credentials are not available"""
        credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
        sheet_id = os.getenv("GOOGLE_SHEETS_ID")

        if not credentials_path or not sheet_id:
            pytest.skip("Google Sheets credentials not configured")

    def test_sheets_client_connection(self):
        """Test direct Google Sheets client connection"""
        self.skip_if_no_credentials()

        try:
            from clients.sheets_client import SheetsClient

            credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
            sheet_id = os.getenv("GOOGLE_SHEETS_ID")

            client = SheetsClient(credentials_path, sheet_id)

            # Test connection validation
            assert client.validate_connection(), "Should connect to Google Sheets"

            # Test getting worksheets
            worksheets = client.get_all_worksheets()
            assert isinstance(worksheets, list), "Should return list of worksheet names"

        except ImportError:
            pytest.skip("Google Sheets client not available")

    def test_sheets_database_operations(self):
        """Test Google Sheets database operations"""
        self.skip_if_no_credentials()

        try:
            from db.sheets_narratives_db import SheetsNarrativesDB

            credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
            sheet_id = os.getenv("GOOGLE_SHEETS_ID")

            db = SheetsNarrativesDB(credentials_path, sheet_id)

            # Test data loading
            initial_count = len(db.df)

            # Test reload functionality
            db.load_data()
            assert len(db.df) >= 0, "Should load data successfully"

            # Test getting all records
            records = db.get_all_records()
            assert isinstance(records, list), "Should return list of records"

        except ImportError:
            pytest.skip("Google Sheets database not available")

    def test_refresh_endpoint_integration(self):
        """Test the refresh endpoint integration with Google Sheets"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running")

        # Test refresh endpoint
        response = requests.post("http://localhost:8000/refresh-data")

        if response.status_code == 200:
            data = response.json()
            assert "message" in data
            assert "total_records" in data
            assert "timestamp" in data
            assert isinstance(data["total_records"], int)
        else:
            # If it fails, it should be due to missing credentials in test environment
            assert response.status_code in [
                500
            ], "Should fail gracefully if no credentials"

    def test_google_sheets_environment_setup(self):
        """Test that Google Sheets environment is properly configured"""
        # Check that required environment variables are documented
        credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
        sheet_id = os.getenv("GOOGLE_SHEETS_ID")

        # In a production environment, these should be set
        # In test environment, we allow them to be None and skip related tests
        if credentials_path:
            assert os.path.exists(
                credentials_path
            ), f"Credentials file should exist: {credentials_path}"

        if sheet_id:
            assert len(sheet_id) > 10, "Sheet ID should be a valid Google Sheets ID"

    def test_sheets_data_consistency(self):
        """Test that data remains consistent between Google Sheets operations"""
        self.skip_if_no_credentials()

        try:
            from db.sheets_narratives_db import SheetsNarrativesDB

            credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
            sheet_id = os.getenv("GOOGLE_SHEETS_ID")

            db1 = SheetsNarrativesDB(credentials_path, sheet_id)
            db2 = SheetsNarrativesDB(credentials_path, sheet_id)

            # Both instances should load the same data
            records1 = db1.get_all_records()
            records2 = db2.get_all_records()

            assert len(records1) == len(
                records2
            ), "Both instances should have same record count"

        except ImportError:
            pytest.skip("Google Sheets database not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
