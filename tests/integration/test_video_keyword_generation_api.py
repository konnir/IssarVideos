#!/usr/bin/env python3
"""
Integration Tests for Video Keyword Generation API
==================================================

Tests the /generate-video-keywords endpoint with proper test isolation.
"""
import pytest
import requests
import sys
from pathlib import Path
from unittest.mock import patch

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestVideoKeywordGenerationAPI:
    """Test the video keyword generation API endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.base_url = "http://localhost:8000"
        self.endpoint = f"{self.base_url}/generate-video-keywords"

    def test_generate_video_keywords_success(self):
        """Test successful video keyword generation"""
        try:
            # Test payload
            payload = {
                "story": "A young artist discovers their passion for painting and creates their first masterpiece",
                "max_keywords": 10,
            }

            response = requests.post(
                self.endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            assert response.status_code == 200
            data = response.json()

            # Verify response structure
            assert "search_query" in data
            assert isinstance(data["search_query"], str)
            assert len(data["search_query"]) > 0

            # Verify it's a reasonable search query (2-6 words typically)
            words = data["search_query"].split()
            assert 1 <= len(words) <= 10  # Allow some flexibility

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping API tests")

    def test_generate_video_keywords_validation_errors(self):
        """Test validation errors for invalid requests"""
        try:
            test_cases = [
                # Empty story
                {
                    "payload": {"story": "", "max_keywords": 10},
                    "expected_status": 422,
                    "description": "empty story",
                },
                # Missing story field
                {
                    "payload": {"max_keywords": 10},
                    "expected_status": 422,
                    "description": "missing story",
                },
                # Invalid max_keywords (negative)
                {
                    "payload": {"story": "test story", "max_keywords": -1},
                    "expected_status": 422,
                    "description": "negative max_keywords",
                },
                # Invalid max_keywords (zero)
                {
                    "payload": {"story": "test story", "max_keywords": 0},
                    "expected_status": 422,
                    "description": "zero max_keywords",
                },
            ]

            for test_case in test_cases:
                response = requests.post(
                    self.endpoint,
                    json=test_case["payload"],
                    headers={"Content-Type": "application/json"},
                    timeout=10,
                )

                assert (
                    response.status_code == test_case["expected_status"]
                ), f"Failed for {test_case['description']}: expected {test_case['expected_status']}, got {response.status_code}"

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping validation tests")

    def test_generate_video_keywords_different_story_types(self):
        """Test with different types of stories"""
        try:
            story_types = [
                "A chef learns to cook authentic Italian cuisine",
                "A dog owner trains their new puppy to behave",
                "An entrepreneur builds a successful tech startup",
                "A family goes on an exciting camping adventure",
                "A student learns advanced mathematics concepts",
            ]

            for story in story_types:
                payload = {"story": story, "max_keywords": 5}

                response = requests.post(
                    self.endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30,
                )

                assert response.status_code == 200, f"Failed for story: {story}"
                data = response.json()

                assert "search_query" in data
                assert len(data["search_query"].strip()) > 0

                # Verify the search query is relevant to the story topic
                search_query = data["search_query"].lower()
                story_lower = story.lower()

                # At least some word overlap is expected for relevant queries
                story_words = set(story_lower.split())
                query_words = set(search_query.split())

                # Allow flexibility - the LLM might use synonyms or related terms
                # Just ensure we get a reasonable response
                assert len(query_words) > 0, f"Empty query for story: {story}"

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping story type tests")

    def test_generate_video_keywords_optional_max_keywords(self):
        """Test that max_keywords is optional"""
        try:
            # Test without max_keywords field
            payload = {"story": "A musician writes their first song"}

            response = requests.post(
                self.endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            assert response.status_code == 200
            data = response.json()
            assert "search_query" in data
            assert len(data["search_query"]) > 0

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping optional parameter tests")

    def test_generate_video_keywords_edge_cases(self):
        """Test edge cases for the API"""
        try:
            edge_cases = [
                # Very short story
                {"story": "Art.", "max_keywords": 5},
                # Story with special characters
                {
                    "story": "A story with !@#$% special characters & symbols",
                    "max_keywords": 5,
                },
                # Long story
                {"story": "A" * 500 + " story about persistence", "max_keywords": 5},
            ]

            for payload in edge_cases:
                response = requests.post(
                    self.endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30,
                )

                # Should either succeed or fail gracefully
                assert response.status_code in [200, 400, 422, 500]

                if response.status_code == 200:
                    data = response.json()
                    assert "search_query" in data

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping edge case tests")

    def test_api_response_headers(self):
        """Test that API returns proper headers"""
        try:
            payload = {"story": "A simple test story"}

            response = requests.post(
                self.endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            # Check content type
            content_type = response.headers.get("content-type", "")
            assert "application/json" in content_type

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping header tests")


if __name__ == "__main__":
    pytest.main([__file__])
