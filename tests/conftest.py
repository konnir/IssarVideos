#!/usr/bin/env python3
"""
Test configuration and fixtures for the Video Narratives project.
Provides shared test utilities and data for Google Sheets based testing.
"""

import pytest
import os
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


def verify_test_environment():
    """Verify that we're in a proper test environment"""
    # Ensure Google Sheets credentials are available for integration tests
    credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
    sheet_id = os.getenv("GOOGLE_SHEETS_ID")

    return {
        "has_credentials": (
            credentials_path is not None and os.path.exists(credentials_path)
            if credentials_path
            else False
        ),
        "has_sheet_id": sheet_id is not None,
        "credentials_path": credentials_path,
        "sheet_id": sheet_id,
    }


# Test data generators for Google Sheets testing
def get_test_record_data():
    """Get test video record data for testing"""
    return {
        "Sheet": "TestTopic",
        "Narrative": "Test narrative for unit testing",
        "Story": "Test story content",
        "Link": "https://youtube.com/test-12345",
        "Tagger_1": None,
        "Tagger_1_Result": 0,
    }


def get_test_update_data():
    """Get test update data"""
    return {"Tagger_1": "TestUser", "Tagger_1_Result": 1}


@pytest.fixture
def test_video_record():
    """Fixture providing test video record data"""
    return get_test_record_data()


@pytest.fixture
def test_update_data():
    """Fixture providing test update data"""
    return get_test_update_data()


@pytest.fixture
def sample_sheet_data():
    """Fixture providing sample sheet data for Google Sheets testing"""
    return [
        {
            "Sheet": "TestSheet1",
            "Narrative": "First test narrative",
            "Story": "Test story content",
            "Link": "https://youtube.com/test-1",
            "Tagger_1": None,
            "Tagger_1_Result": 0,
        },
        {
            "Sheet": "TestSheet1",
            "Narrative": "Second test narrative",
            "Story": "Another test story",
            "Link": "https://youtube.com/test-2",
            "Tagger_1": "TestUser",
            "Tagger_1_Result": 1,
        },
        {
            "Sheet": "TestSheet2",
            "Narrative": "Third test narrative",
            "Story": None,
            "Link": "https://youtube.com/test-3",
            "Tagger_1": None,
            "Tagger_1_Result": None,
        },
    ]


@pytest.fixture
def test_environment_info():
    """Fixture providing test environment information"""
    return verify_test_environment()


# API test base URL
@pytest.fixture
def api_base_url():
    """Fixture providing the base URL for API tests"""
    return "http://localhost:8000"


# Authentication data for tests
@pytest.fixture
def valid_auth_data():
    """Fixture providing valid authentication data"""
    return {"username": "Nir Kon", "password": "originai"}


@pytest.fixture
def invalid_auth_data():
    """Fixture providing invalid authentication data"""
    return {"username": "Invalid User", "password": "wrong_password"}
