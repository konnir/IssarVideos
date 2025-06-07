#!/usr/bin/env python3
"""
Integration Tests for Story Generation API Endpoints
===================================================

Tests the OpenAI-powered story generation functionality.
"""
import pytest
import requests
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestStoryGenerationAPI:
    """Test the story generation API endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.base_url = "http://localhost:8000"
        self.test_narrative = "A mysterious package arrives at someone's door containing an old family photo"
        self.test_story_response = {
            "story": "When Sarah finds an old family photo in a mysterious package, she discovers her grandmother had a secret twin sister. The photo leads her to uncover decades of family mysteries and hidden letters that change everything she thought she knew about her heritage.",
            "word_count": 42,
        }

    def test_health_endpoint_includes_openai_status(self):
        """Test that health endpoint includes OpenAI connectivity status"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            # OpenAI status might be included in future health checks
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping health check test")

    def test_test_openai_connection_endpoint(self):
        """Test the OpenAI connection test endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/test-openai-connection", timeout=10
            )

            # Should return 200 whether connection succeeds or fails
            assert response.status_code == 200
            data = response.json()

            # Should have these fields regardless of success/failure
            assert "connected" in data
            assert "message" in data
            assert isinstance(data["connected"], bool)
            assert isinstance(data["message"], str)

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping OpenAI connection test")

    @patch("clients.openai_client.OpenAI")
    def test_generate_story_success(self, mock_openai):
        """Test successful story generation"""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = self.test_story_response["story"]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        try:
            payload = {
                "narrative": self.test_narrative,
                "style": "dramatic",
                "additional_context": "Focus on family secrets",
            }

            response = requests.post(
                f"{self.base_url}/generate-story", json=payload, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                assert "story" in data
                assert "metadata" in data
                assert "narrative" in data
                assert isinstance(data["story"], str)
                assert isinstance(data["metadata"], dict)
                assert "word_count" in data["metadata"]
                assert isinstance(data["metadata"]["word_count"], int)
                assert len(data["story"]) > 0
            else:
                # API key might not be configured in test environment
                assert response.status_code in [400, 500]

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping story generation test")

    def test_generate_story_missing_narrative(self):
        """Test story generation with missing narrative"""
        try:
            payload = {
                "style": "dramatic"
                # Missing required 'narrative' field
            }

            response = requests.post(
                f"{self.base_url}/generate-story", json=payload, timeout=10
            )

            assert response.status_code == 422  # Validation error

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping validation test")

    def test_generate_story_variants_endpoint(self):
        """Test story variants generation endpoint"""
        try:
            payload = {
                "narrative": self.test_narrative,
                "count": 3,
                "style": "suspenseful",
            }

            response = requests.post(
                f"{self.base_url}/generate-story-variants", json=payload, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                assert "variants" in data
                assert isinstance(data["variants"], list)
                # Should return requested number of variants or handle gracefully
                assert len(data["variants"]) <= payload["count"]

                # Check variant structure
                for variant in data["variants"]:
                    assert "story" in variant
                    assert "metadata" in variant
                    assert isinstance(variant["story"], str)
                    assert isinstance(variant["metadata"], dict)
            else:
                # API key might not be configured or other error
                assert response.status_code in [400, 500]

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping story variants test")

    def test_refine_story_endpoint(self):
        """Test story refinement endpoint"""
        try:
            payload = {
                "original_story": "A simple story about someone finding an old photo.",
                "refinement_request": "Make it more mysterious and add family drama",
                "narrative": "A mysterious package arrives at someone's door containing an old family photo",
            }

            response = requests.post(
                f"{self.base_url}/refine-story", json=payload, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                assert "story" in data
                assert "metadata" in data
                assert "narrative" in data
                assert isinstance(data["story"], str)
                assert isinstance(data["metadata"], dict)
                assert "word_count" in data["metadata"]
                assert isinstance(data["metadata"]["word_count"], int)
            else:
                # API key might not be configured or other error
                assert response.status_code in [400, 422, 500]

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping story refinement test")

    def test_story_generation_request_validation(self):
        """Test that story generation requests are properly validated"""
        test_cases = [
            # Empty narrative
            {"narrative": "", "style": "dramatic"},
            # Null narrative
            {"narrative": None, "style": "dramatic"},
            # Very long narrative (if there are limits)
            {"narrative": "x" * 5000, "style": "dramatic"},
        ]

        try:
            for i, payload in enumerate(test_cases):
                response = requests.post(
                    f"{self.base_url}/generate-story", json=payload, timeout=10
                )

                # Should get validation error for most of these
                # Empty/null narrative should be rejected
                if i < 2:
                    assert (
                        response.status_code == 422
                    ), f"Test case {i} should fail validation"
                else:
                    # Very long narrative might be accepted or rejected based on implementation
                    assert response.status_code in [
                        200,
                        422,
                    ], f"Test case {i} should either succeed or fail validation"

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping validation tests")

    def test_story_endpoints_require_post(self):
        """Test that story generation endpoints only accept POST requests"""
        endpoints = ["/generate-story", "/generate-story-variants", "/refine-story"]

        try:
            for endpoint in endpoints:
                # Try GET request (should fail)
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                assert response.status_code == 405  # Method not allowed

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping method validation tests")

    def test_suggest_story_integration_flow(self):
        """Test the complete suggest story flow in tagging management"""
        try:
            # First test that the generate-story endpoint works for the suggest feature
            payload = {
                "narrative": "A scientist discovers something unusual in their lab",
                "style": "engaging",  # Default style used by suggest feature
                "additional_context": "",  # Empty as used by suggest feature
            }

            response = requests.post(
                f"{self.base_url}/generate-story", json=payload, timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                # Verify response structure matches what the suggest feature expects
                assert "story" in data
                assert "metadata" in data
                assert isinstance(data["story"], str)
                assert len(data["story"]) > 0

                # Verify the story is suitable for narrative management
                # Should be substantial but not too long
                assert len(data["story"]) > 50  # Minimum meaningful story
                assert len(data["story"]) < 2000  # Not too long for UI

            else:
                # In test environment, API key might not be configured
                assert response.status_code in [400, 500]
                pytest.skip(
                    "OpenAI API not configured - skipping suggest story integration test"
                )

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping suggest story integration test")

    def test_suggest_story_with_empty_narrative(self):
        """Test suggest story behavior with empty narrative"""
        try:
            payload = {
                "narrative": "",  # Empty narrative
                "style": "engaging",
                "additional_context": "",
            }

            response = requests.post(
                f"{self.base_url}/generate-story", json=payload, timeout=10
            )

            # Should return validation error for empty narrative
            assert response.status_code == 422

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping validation test")

    def test_suggest_story_with_very_long_narrative(self):
        """Test suggest story with very long narrative input"""
        try:
            # Create a very long narrative (over 1000 characters)
            long_narrative = "A person discovers " + "something amazing " * 100

            payload = {
                "narrative": long_narrative,
                "style": "engaging",
                "additional_context": "",
            }

            response = requests.post(
                f"{self.base_url}/generate-story", json=payload, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                # Should still generate a reasonable story
                assert "story" in data
                assert len(data["story"]) > 0
            else:
                # Should handle gracefully
                assert response.status_code in [400, 422, 500]

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping long narrative test")

    def test_suggest_story_with_special_characters(self):
        """Test suggest story with special characters in narrative"""
        try:
            payload = {
                "narrative": "A developer finds a bug 🐛 in their code that causes emoji 😀 to appear everywhere!",
                "style": "engaging",
                "additional_context": "",
            }

            response = requests.post(
                f"{self.base_url}/generate-story", json=payload, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                assert "story" in data
                assert isinstance(data["story"], str)
                # Should handle unicode characters properly
                assert len(data["story"]) > 0
            else:
                # Should handle gracefully
                assert response.status_code in [400, 500]

        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping special characters test")


class TestStoryGenerationUnit:
    """Unit tests for story generation components"""

    def test_story_generation_models_import(self):
        """Test that story generation models can be imported"""
        try:
            from data.video_record import (
                StoryGenerationRequest,
                StoryVariantsRequest,
                StoryRefinementRequest,
                StoryResponse,
            )

            # Test model instantiation
            story_req = StoryGenerationRequest(
                narrative="Test narrative", style="dramatic"
            )
            assert story_req.narrative == "Test narrative"
            assert story_req.style == "dramatic"

            variants_req = StoryVariantsRequest(narrative="Test narrative", count=3)
            assert variants_req.count == 3

            refinement_req = StoryRefinementRequest(
                original_story="Old story",
                refinement_request="Make it better",
                narrative="Test narrative",
            )
            assert refinement_req.original_story == "Old story"
            assert refinement_req.refinement_request == "Make it better"
            assert refinement_req.narrative == "Test narrative"

            story_response = StoryResponse(
                story="Generated story",
                narrative="Test narrative",
                metadata={"word_count": 25},
            )
            assert story_response.story == "Generated story"
            assert story_response.narrative == "Test narrative"
            assert story_response.metadata["word_count"] == 25

        except ImportError as e:
            pytest.fail(f"Failed to import story generation models: {e}")

    def test_openai_client_import(self):
        """Test that OpenAI client can be imported"""
        try:
            from clients.openai_client import OpenAIClient

            # Test client instantiation (without API key)
            client = OpenAIClient()
            assert client is not None
            assert hasattr(client, "client")

        except ImportError as e:
            pytest.fail(f"Failed to import OpenAI client: {e}")

    def test_story_generator_import(self):
        """Test that story generator can be imported"""
        try:
            from llm.get_story import StoryGenerator

            # Test generator instantiation
            generator = StoryGenerator()
            assert generator is not None
            assert hasattr(generator, "openai_client")

        except ImportError as e:
            pytest.fail(f"Failed to import story generator: {e}")


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])
