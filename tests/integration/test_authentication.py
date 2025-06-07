#!/usr/bin/env python3
"""
Authentication and Security Tests
=================================

Tests for authentication endpoints and security measures.
"""
import pytest
import requests
import sys
from pathlib import Path

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestAuthentication:
    """Test authentication functionality"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for authentication tests"""
        self.base_url = "http://localhost:8000"
        self.valid_credentials = [
            {"username": "Nir Kon", "password": "originai"},
            {"username": "Issar Tzachor", "password": "originai"},
        ]
        self.invalid_credentials = [
            {"username": "Invalid User", "password": "originai"},
            {"username": "Nir Kon", "password": "wrong_password"},
            {"username": "", "password": "originai"},
            {"username": "Nir Kon", "password": ""},
            {"username": "", "password": ""},
            {"username": "admin", "password": "admin"},
            {"username": "test", "password": "test"},
        ]

    def skip_if_server_not_running(self):
        """Skip test if server is not running"""
        try:
            requests.get(f"{self.base_url}/health", timeout=2)
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping authentication tests")

    def test_valid_authentication(self):
        """Test authentication with valid credentials"""
        self.skip_if_server_not_running()

        for credentials in self.valid_credentials:
            response = requests.post(f"{self.base_url}/auth-report", json=credentials)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "message" in data
            assert data["message"] == "Authentication successful"

    def test_invalid_authentication(self):
        """Test authentication with invalid credentials"""
        self.skip_if_server_not_running()

        for credentials in self.invalid_credentials:
            response = requests.post(f"{self.base_url}/auth-report", json=credentials)

            assert response.status_code == 401
            data = response.json()
            assert "detail" in data
            assert data["detail"] == "Invalid credentials"

    def test_authentication_with_extra_whitespace(self):
        """Test authentication with whitespace in credentials - should fail with exact matching"""
        self.skip_if_server_not_running()

        # Test with extra whitespace (should now fail with exact matching)
        credentials_with_whitespace = [
            {"username": "  Nir Kon  ", "password": "  originai  "},
            {"username": "\tIssar Tzachor\t", "password": "\toriginai\t"},
            {"username": " Nir Kon", "password": "originai "},
        ]

        for credentials in credentials_with_whitespace:
            response = requests.post(f"{self.base_url}/auth-report", json=credentials)

            # With exact matching, these should all fail
            assert response.status_code == 401

    def test_authentication_case_sensitivity(self):
        """Test authentication case sensitivity"""
        self.skip_if_server_not_running()

        # Test case-sensitive username (should fail)
        case_sensitive_attempts = [
            {"username": "nir kon", "password": "originai"},
            {"username": "NIR KON", "password": "originai"},
            {"username": "Nir kon", "password": "originai"},
            {"username": "Nir Kon", "password": "ORIGINAI"},
            {"username": "Nir Kon", "password": "Originai"},
        ]

        for credentials in case_sensitive_attempts:
            response = requests.post(f"{self.base_url}/auth-report", json=credentials)

            # These should fail due to case sensitivity
            assert response.status_code == 401

    def test_authentication_malformed_request(self):
        """Test authentication with malformed requests"""
        self.skip_if_server_not_running()

        # Test with missing fields
        malformed_requests = [
            {"username": "Nir Kon"},  # Missing password
            {"password": "originai"},  # Missing username
            {},  # Empty object
            {"user": "Nir Kon", "pass": "originai"},  # Wrong field names
        ]

        for request_data in malformed_requests:
            response = requests.post(f"{self.base_url}/auth-report", json=request_data)

            # Should fail with 401 (treated as invalid credentials)
            assert response.status_code == 401

    def test_authentication_with_none_values(self):
        """Test authentication with None values"""
        self.skip_if_server_not_running()

        none_value_requests = [
            {"username": None, "password": "originai"},
            {"username": "Nir Kon", "password": None},
            {"username": None, "password": None},
        ]

        for request_data in none_value_requests:
            response = requests.post(f"{self.base_url}/auth-report", json=request_data)

            assert response.status_code == 401


class TestSecurityMeasures:
    """Test security measures and protections"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for security tests"""
        self.base_url = "http://localhost:8000"

    def skip_if_server_not_running(self):
        """Skip test if server is not running"""
        try:
            requests.get(f"{self.base_url}/health", timeout=2)
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping security tests")

    def test_sql_injection_attempts(self):
        """Test protection against SQL injection attempts"""
        self.skip_if_server_not_running()

        sql_injection_attempts = [
            {"username": "'; DROP TABLE users; --", "password": "originai"},
            {"username": "Nir Kon", "password": "'; DROP TABLE users; --"},
            {"username": "admin' OR '1'='1", "password": "anything"},
            {"username": "Nir Kon", "password": "originai' OR '1'='1"},
        ]

        for credentials in sql_injection_attempts:
            response = requests.post(f"{self.base_url}/auth-report", json=credentials)

            # Should fail authentication, not cause server errors
            assert response.status_code == 401

            # Server should still be functional
            health_response = requests.get(f"{self.base_url}/health")
            assert health_response.status_code == 200

    def test_script_injection_attempts(self):
        """Test protection against script injection attempts"""
        self.skip_if_server_not_running()

        script_injection_attempts = [
            {"username": "<script>alert('xss')</script>", "password": "originai"},
            {"username": "Nir Kon", "password": "<script>alert('xss')</script>"},
            {"username": "javascript:alert('xss')", "password": "originai"},
            {"username": "Nir Kon", "password": "javascript:alert('xss')"},
        ]

        for credentials in script_injection_attempts:
            response = requests.post(f"{self.base_url}/auth-report", json=credentials)

            # Should fail authentication without causing issues
            assert response.status_code == 401

    def test_excessive_request_handling(self):
        """Test handling of excessive authentication requests"""
        self.skip_if_server_not_running()

        # Send multiple rapid authentication requests
        invalid_credentials = {"username": "invalid", "password": "invalid"}

        responses = []
        for _ in range(20):  # Send 20 rapid requests
            try:
                response = requests.post(
                    f"{self.base_url}/auth-report", json=invalid_credentials, timeout=5
                )
                responses.append(response.status_code)
            except requests.exceptions.RequestException:
                # If server limits requests, that's acceptable
                pass

        # All responses should be 401 (not server errors)
        for status_code in responses:
            assert status_code == 401

        # Server should still be functional after rapid requests
        health_response = requests.get(f"{self.base_url}/health")
        assert health_response.status_code == 200

    def test_content_type_validation(self):
        """Test that endpoints properly validate content types"""
        self.skip_if_server_not_running()

        # Test sending non-JSON data to JSON endpoint
        response = requests.post(
            f"{self.base_url}/auth-report",
            data="username=Nir Kon&password=originai",  # Form data instead of JSON
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Should handle gracefully (likely return 422 or 400)
        assert response.status_code in [400, 422]

    def test_oversized_request_handling(self):
        """Test handling of oversized requests"""
        self.skip_if_server_not_running()

        # Create an oversized request payload
        large_string = "A" * 10000  # 10KB string
        oversized_request = {"username": large_string, "password": "originai"}

        response = requests.post(f"{self.base_url}/auth-report", json=oversized_request)

        # Should handle gracefully (fail authentication or request too large)
        assert response.status_code in [401, 413, 422]

    def test_special_characters_handling(self):
        """Test handling of special characters in authentication"""
        self.skip_if_server_not_running()

        special_char_attempts = [
            {"username": "Nir Kon\x00", "password": "originai"},  # Null byte
            {"username": "Nir Kon\n", "password": "originai"},  # Newline
            {"username": "Nir Kon\r", "password": "originai"},  # Carriage return
            {"username": "Nir Kon\t", "password": "originai"},  # Tab
            {"username": "Nir Kon", "password": "originai\x00"},  # Null in password
        ]

        for credentials in special_char_attempts:
            response = requests.post(f"{self.base_url}/auth-report", json=credentials)

            # Should handle gracefully (likely fail authentication)
            assert response.status_code in [401, 422]


class TestAuthenticationIntegration:
    """Test authentication integration with other endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for integration tests"""
        self.base_url = "http://localhost:8000"
        self.valid_auth = {"username": "Nir Kon", "password": "originai"}

    def skip_if_server_not_running(self):
        """Skip test if server is not running"""
        try:
            requests.get(f"{self.base_url}/health", timeout=2)
        except requests.exceptions.ConnectionError:
            pytest.skip(
                "Server not running - skipping authentication integration tests"
            )

    def test_report_access_flow(self):
        """Test the complete report access flow with authentication"""
        self.skip_if_server_not_running()

        # Step 1: Access report page (should work without auth)
        report_response = requests.get(f"{self.base_url}/report")
        assert report_response.status_code == 200

        # Step 2: Authenticate for report data
        auth_response = requests.post(
            f"{self.base_url}/auth-report", json=self.valid_auth
        )
        assert auth_response.status_code == 200

        # Step 3: Access tagged records (may require auth in future implementations)
        tagged_response = requests.get(f"{self.base_url}/tagged-records")
        assert tagged_response.status_code == 200

        # Step 4: Download Excel (may require auth in future implementations)
        excel_response = requests.get(f"{self.base_url}/download-excel")
        assert excel_response.status_code == 200

    def test_multiple_authentication_sessions(self):
        """Test multiple authentication sessions"""
        self.skip_if_server_not_running()

        # Multiple users authenticating
        users = [
            {"username": "Nir Kon", "password": "originai"},
            {"username": "Issar Tzachor", "password": "originai"},
        ]

        for user in users:
            response = requests.post(f"{self.base_url}/auth-report", json=user)
            assert response.status_code == 200

            data = response.json()
            assert data["success"] is True


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])
