#!/usr/bin/env python3
"""
Integration Tests for Video Narratives API
==========================================

Tests the main API endpoints with proper test isolation.
"""
import pytest
import requests
import sys
from pathlib import Path

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestAPIEndpoints:
    """Test the main API endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.base_url = "http://localhost:8000"

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy"
            assert data.get("service") == "video-narratives"
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping API tests")

    def test_static_files(self):
        """Test that static files are accessible"""
        try:
            # Test tagger page
            response = requests.get(f"{self.base_url}/", timeout=5)
            assert response.status_code == 200

            # Test that it returns HTML
            assert "html" in response.headers.get("content-type", "").lower()

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping static file tests")

    def test_api_endpoints_exist(self):
        """Test that main API endpoints respond (even if with errors due to test data)"""
        endpoints_to_test = [
            "/leaderboard",
            "/tagged-records",
        ]

        try:
            for endpoint in endpoints_to_test:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                # We expect 200 status codes (endpoints should return empty lists for test data)
                assert (
                    response.status_code == 200
                ), f"Endpoint {endpoint} should be accessible"

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping API endpoint tests")


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])
