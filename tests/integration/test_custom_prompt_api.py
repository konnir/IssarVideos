#!/usr/bin/env python3
"""
Integration tests for Custom Prompt API endpoints
"""

import pytest
import json
import os
import pandas as pd
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

# Set test environment before importing main
# Note: Tests now use Google Sheets integration instead of local database files

from main import app


class TestCustomPromptAPIEndpoints:
    """Test the custom prompt API endpoints"""

    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)

    @patch("main.StoryGenerator")
    def test_generate_story_custom_prompt_success(self, mock_story_generator_class):
        """Test successful custom prompt story generation"""
        # Mock the story generator
        mock_generator = Mock()
        mock_generator.get_story_with_custom_prompt.return_value = {
            "story": "A mysterious package arrives at Sarah's door, containing a key to her family's forgotten past.",
            "narrative": "A mysterious package arrives",
            "metadata": {
                "style": "engaging",
                "custom_prompt": "Create a story about: {narrative}",
                "generation_method": "custom_prompt",
                "timestamp": 1234567890.123,
            },
        }
        mock_story_generator_class.return_value = mock_generator

        # Test data
        request_data = {
            "narrative": "A mysterious package arrives",
            "custom_prompt": "Create a story about: {narrative}",
            "style": "engaging",
        }

        # Make request
        response = self.client.post("/generate-story-custom-prompt", json=request_data)

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert (
            data["story"]
            == "A mysterious package arrives at Sarah's door, containing a key to her family's forgotten past."
        )
        assert data["narrative"] == "A mysterious package arrives"
        assert data["metadata"]["style"] == "engaging"
        assert data["metadata"]["custom_prompt"] == "Create a story about: {narrative}"
        assert data["metadata"]["generation_method"] == "custom_prompt"

        # Verify the generator was called correctly
        mock_generator.get_story_with_custom_prompt.assert_called_once_with(
            narrative="A mysterious package arrives",
            custom_prompt="Create a story about: {narrative}",
            style="engaging",
        )

    def test_generate_story_custom_prompt_missing_narrative(self):
        """Test custom prompt endpoint with missing narrative"""
        request_data = {
            "custom_prompt": "Create a story about: {narrative}",
            "style": "engaging",
        }

        response = self.client.post("/generate-story-custom-prompt", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert "narrative" in str(data).lower()

    def test_generate_story_custom_prompt_missing_custom_prompt(self):
        """Test custom prompt endpoint with missing custom_prompt"""
        request_data = {
            "narrative": "A mysterious package arrives",
            "style": "engaging",
        }

        response = self.client.post("/generate-story-custom-prompt", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert "custom_prompt" in str(data).lower()

    def test_generate_story_custom_prompt_empty_narrative(self):
        """Test custom prompt endpoint with empty narrative"""
        request_data = {
            "narrative": "",
            "custom_prompt": "Create a story about: {narrative}",
            "style": "engaging",
        }

        response = self.client.post("/generate-story-custom-prompt", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert "cannot be empty" in str(data).lower()

    def test_generate_story_custom_prompt_empty_custom_prompt(self):
        """Test custom prompt endpoint with empty custom_prompt"""
        request_data = {
            "narrative": "A mysterious package arrives",
            "custom_prompt": "",
            "style": "engaging",
        }

        response = self.client.post("/generate-story-custom-prompt", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert "cannot be empty" in str(data).lower()

    def test_generate_story_custom_prompt_whitespace_only_fields(self):
        """Test custom prompt endpoint with whitespace-only fields"""
        request_data = {
            "narrative": "   ",
            "custom_prompt": "  \t  ",
            "style": "engaging",
        }

        response = self.client.post("/generate-story-custom-prompt", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert "cannot be empty" in str(data).lower()

    def test_generate_story_custom_prompt_default_style(self):
        """Test custom prompt endpoint with default style"""
        with patch("main.StoryGenerator") as mock_story_generator_class:
            mock_generator = Mock()
            mock_generator.get_story_with_custom_prompt.return_value = {
                "story": "Generated story",
                "narrative": "Test narrative",
                "metadata": {
                    "style": "engaging",
                    "custom_prompt": "Test prompt",
                    "generation_method": "custom_prompt",
                    "timestamp": 1234567890.123,
                },
            }
            mock_story_generator_class.return_value = mock_generator

            request_data = {
                "narrative": "Test narrative",
                "custom_prompt": "Test prompt",
                # No style provided - should default to "engaging"
            }

            response = self.client.post(
                "/generate-story-custom-prompt", json=request_data
            )

            assert response.status_code == 200
            # Verify default style was used
            mock_generator.get_story_with_custom_prompt.assert_called_once_with(
                narrative="Test narrative",
                custom_prompt="Test prompt",
                style="engaging",
            )

    @patch("main.StoryGenerator")
    def test_generate_story_custom_prompt_story_generator_error(
        self, mock_story_generator_class
    ):
        """Test custom prompt endpoint when story generator raises an error"""
        # Mock the story generator to raise an exception
        mock_generator = Mock()
        mock_generator.get_story_with_custom_prompt.side_effect = Exception(
            "Story generation failed"
        )
        mock_story_generator_class.return_value = mock_generator

        request_data = {
            "narrative": "A mysterious package arrives",
            "custom_prompt": "Create a story about: {narrative}",
            "style": "engaging",
        }

        response = self.client.post("/generate-story-custom-prompt", json=request_data)

        assert response.status_code == 500
        data = response.json()
        assert "Failed to generate story with custom prompt" in data["detail"]
        assert "Story generation failed" in data["detail"]

    @patch("main.StoryGenerator")
    def test_generate_story_custom_prompt_various_styles(
        self, mock_story_generator_class
    ):
        """Test custom prompt endpoint with various style values"""
        mock_generator = Mock()
        mock_generator.get_story_with_custom_prompt.return_value = {
            "story": "Generated story",
            "narrative": "Test narrative",
            "metadata": {
                "style": "thriller",
                "custom_prompt": "Test prompt",
                "generation_method": "custom_prompt",
                "timestamp": 1234567890.123,
            },
        }
        mock_story_generator_class.return_value = mock_generator

        styles = ["engaging", "dramatic", "comedy", "thriller", "documentary"]

        for style in styles:
            request_data = {
                "narrative": "Test narrative",
                "custom_prompt": "Test prompt: {narrative}",
                "style": style,
            }

            response = self.client.post(
                "/generate-story-custom-prompt", json=request_data
            )

            assert response.status_code == 200
            # Verify the correct style was passed to the generator
            mock_generator.get_story_with_custom_prompt.assert_called_with(
                narrative="Test narrative",
                custom_prompt="Test prompt: {narrative}",
                style=style,
            )

    @patch("main.StoryGenerator")
    def test_generate_story_custom_prompt_complex_narrative(
        self, mock_story_generator_class
    ):
        """Test custom prompt endpoint with complex narrative content"""
        mock_generator = Mock()
        mock_generator.get_story_with_custom_prompt.return_value = {
            "story": "Complex generated story",
            "narrative": "A complex narrative with special characters",
            "metadata": {
                "style": "engaging",
                "custom_prompt": "Complex prompt",
                "generation_method": "custom_prompt",
                "timestamp": 1234567890.123,
            },
        }
        mock_story_generator_class.return_value = mock_generator

        # Test with complex narrative containing special characters
        complex_narrative = (
            'A story with émojis 🎭, quotes "like this", and symbols & characters!'
        )
        complex_prompt = "Create an elaborate story about: {narrative}. Include dialogue, setting, and character development."

        request_data = {
            "narrative": complex_narrative,
            "custom_prompt": complex_prompt,
            "style": "dramatic",
        }

        response = self.client.post("/generate-story-custom-prompt", json=request_data)

        assert response.status_code == 200

        # Verify the complex content was handled correctly
        mock_generator.get_story_with_custom_prompt.assert_called_once_with(
            narrative=complex_narrative, custom_prompt=complex_prompt, style="dramatic"
        )

    def test_generate_story_custom_prompt_content_type_validation(self):
        """Test that the endpoint requires JSON content type"""
        # Send form data instead of JSON
        response = self.client.post(
            "/generate-story-custom-prompt",
            data={
                "narrative": "Test narrative",
                "custom_prompt": "Test prompt",
                "style": "engaging",
            },
        )

        # Should fail because it expects JSON
        assert response.status_code == 422

    @patch("main.StoryGenerator")
    def test_generate_story_custom_prompt_response_format(
        self, mock_story_generator_class
    ):
        """Test that the response follows the correct format"""
        mock_generator = Mock()
        mock_generator.get_story_with_custom_prompt.return_value = {
            "story": "Test story content",
            "narrative": "Test narrative",
            "metadata": {
                "style": "engaging",
                "custom_prompt": "Test custom prompt",
                "generation_method": "custom_prompt",
                "timestamp": 1234567890.123,
                "extra_field": "should be included",
            },
        }
        mock_story_generator_class.return_value = mock_generator

        request_data = {
            "narrative": "Test narrative",
            "custom_prompt": "Test custom prompt",
            "style": "engaging",
        }

        response = self.client.post("/generate-story-custom-prompt", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify all required fields are present
        assert "story" in data
        assert "narrative" in data
        assert "metadata" in data

        # Verify metadata structure
        metadata = data["metadata"]
        assert "style" in metadata
        assert "custom_prompt" in metadata
        assert "generation_method" in metadata
        assert "timestamp" in metadata
        assert "extra_field" in metadata  # Additional fields should be preserved

    @classmethod
    def teardown_class(cls):
        """Clean up after all tests - Google Sheets tests don't require file cleanup"""
        pass


if __name__ == "__main__":
    pytest.main([__file__])
