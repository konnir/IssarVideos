#!/usr/bin/env python3
"""
Unit tests for Custom Prompt functionality
"""

import pytest
from unittest.mock import Mock, patch
from pydantic import ValidationError

from data.video_record import CustomPromptStoryRequest
from llm.get_story import StoryGenerator


class TestCustomPromptStoryRequest:
    """Test the CustomPromptStoryRequest data model"""

    def test_valid_custom_prompt_request(self):
        """Test creating a valid custom prompt request"""
        request = CustomPromptStoryRequest(
            narrative="A mysterious package arrives",
            custom_prompt="Write a story about: {narrative}",
            style="engaging",
        )

        assert request.narrative == "A mysterious package arrives"
        assert request.custom_prompt == "Write a story about: {narrative}"
        assert request.style == "engaging"

    def test_default_style(self):
        """Test that style defaults to 'engaging'"""
        request = CustomPromptStoryRequest(
            narrative="A mysterious package arrives",
            custom_prompt="Write a story about: {narrative}",
        )

        assert request.style == "engaging"

    def test_empty_narrative_validation(self):
        """Test that empty narrative raises validation error"""
        with pytest.raises(ValidationError) as excinfo:
            CustomPromptStoryRequest(
                narrative="", custom_prompt="Write a story about: {narrative}"
            )

        assert "Field cannot be empty" in str(excinfo.value)

    def test_whitespace_only_narrative_validation(self):
        """Test that whitespace-only narrative raises validation error"""
        with pytest.raises(ValidationError) as excinfo:
            CustomPromptStoryRequest(
                narrative="   ", custom_prompt="Write a story about: {narrative}"
            )

        assert "Field cannot be empty" in str(excinfo.value)

    def test_empty_custom_prompt_validation(self):
        """Test that empty custom prompt raises validation error"""
        with pytest.raises(ValidationError) as excinfo:
            CustomPromptStoryRequest(
                narrative="A mysterious package arrives", custom_prompt=""
            )

        assert "Field cannot be empty" in str(excinfo.value)

    def test_whitespace_only_custom_prompt_validation(self):
        """Test that whitespace-only custom prompt raises validation error"""
        with pytest.raises(ValidationError) as excinfo:
            CustomPromptStoryRequest(
                narrative="A mysterious package arrives", custom_prompt="   "
            )

        assert "Field cannot be empty" in str(excinfo.value)

    def test_valid_styles(self):
        """Test various valid style values"""
        valid_styles = ["engaging", "dramatic", "comedy", "thriller", "documentary"]

        for style in valid_styles:
            request = CustomPromptStoryRequest(
                narrative="A mysterious package arrives",
                custom_prompt="Write a story about: {narrative}",
                style=style,
            )
            assert request.style == style


class TestStoryGeneratorCustomPrompt:
    """Test the StoryGenerator custom prompt functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_openai_client = Mock()
        self.generator = StoryGenerator(openai_client=self.mock_openai_client)

    def test_get_story_with_custom_prompt_success(self):
        """Test successful story generation with custom prompt"""
        # Mock the OpenAI response
        self.mock_openai_client.generate_simple_completion.return_value = (
            "A thrilling story about a mysterious package that changes everything."
        )

        narrative = "A mysterious package arrives"
        custom_prompt = (
            "Create a thrilling story about: {narrative}. Make it suspenseful."
        )

        result = self.generator.get_story_with_custom_prompt(
            narrative=narrative, custom_prompt=custom_prompt, style="thriller"
        )

        # Verify the result structure
        assert "story" in result
        assert "narrative" in result
        assert "metadata" in result

        # Verify the content
        assert (
            result["story"]
            == "A thrilling story about a mysterious package that changes everything."
        )
        assert result["narrative"] == narrative
        assert result["metadata"]["style"] == "thriller"
        assert result["metadata"]["custom_prompt"] == custom_prompt
        assert result["metadata"]["generation_method"] == "custom_prompt"
        assert "timestamp" in result["metadata"]

    def test_get_story_with_custom_prompt_placeholder_replacement(self):
        """Test that {narrative} placeholder is correctly replaced"""
        self.mock_openai_client.generate_simple_completion.return_value = (
            "Generated story"
        )

        narrative = "A cat finds a secret door"
        custom_prompt = "Tell me about this scenario: {narrative}. Make it interesting."
        expected_prompt = "Tell me about this scenario: A cat finds a secret door. Make it interesting."

        self.generator.get_story_with_custom_prompt(
            narrative=narrative, custom_prompt=custom_prompt
        )

        # Verify the OpenAI client was called with the correct prompt
        self.mock_openai_client.generate_simple_completion.assert_called_once()
        args, kwargs = self.mock_openai_client.generate_simple_completion.call_args

        assert kwargs["prompt"] == expected_prompt

    def test_get_story_with_custom_prompt_system_prompt(self):
        """Test that system prompt is correctly generated"""
        self.mock_openai_client.generate_simple_completion.return_value = (
            "Generated story"
        )

        self.generator.get_story_with_custom_prompt(
            narrative="Test narrative",
            custom_prompt="Test prompt: {narrative}",
            style="dramatic",
        )

        # Verify the system prompt was passed
        args, kwargs = self.mock_openai_client.generate_simple_completion.call_args
        system_prompt = kwargs["system_prompt"]

        assert "dramatic" in system_prompt.lower()
        assert "creative video storyteller" in system_prompt.lower()

    def test_get_story_with_custom_prompt_openai_parameters(self):
        """Test that correct parameters are passed to OpenAI"""
        self.mock_openai_client.generate_simple_completion.return_value = (
            "Generated story"
        )

        self.generator.get_story_with_custom_prompt(
            narrative="Test narrative", custom_prompt="Test prompt: {narrative}"
        )

        # Verify OpenAI parameters
        args, kwargs = self.mock_openai_client.generate_simple_completion.call_args

        assert kwargs["max_tokens"] == 150
        assert kwargs["temperature"] == 0.8

    def test_get_story_with_custom_prompt_error_handling(self):
        """Test error handling in custom prompt generation"""
        # Mock OpenAI to raise an exception
        self.mock_openai_client.generate_simple_completion.side_effect = Exception(
            "OpenAI error"
        )

        with pytest.raises(Exception) as excinfo:
            self.generator.get_story_with_custom_prompt(
                narrative="Test narrative", custom_prompt="Test prompt: {narrative}"
            )

        assert "OpenAI error" in str(excinfo.value)

    def test_get_story_with_custom_prompt_multiple_placeholders(self):
        """Test custom prompt with multiple {narrative} placeholders"""
        self.mock_openai_client.generate_simple_completion.return_value = (
            "Generated story"
        )

        narrative = "A robot learns to love"
        custom_prompt = "Start with {narrative}, then explore {narrative} in depth."
        expected_prompt = "Start with A robot learns to love, then explore A robot learns to love in depth."

        self.generator.get_story_with_custom_prompt(
            narrative=narrative, custom_prompt=custom_prompt
        )

        args, kwargs = self.mock_openai_client.generate_simple_completion.call_args
        assert kwargs["prompt"] == expected_prompt

    def test_get_story_with_custom_prompt_empty_response(self):
        """Test handling of empty OpenAI response"""
        self.mock_openai_client.generate_simple_completion.return_value = ""

        result = self.generator.get_story_with_custom_prompt(
            narrative="Test narrative", custom_prompt="Test prompt: {narrative}"
        )

        assert result["story"] == ""

    def test_get_story_with_custom_prompt_whitespace_response(self):
        """Test handling of whitespace-only OpenAI response"""
        self.mock_openai_client.generate_simple_completion.return_value = "   \n\t   "

        result = self.generator.get_story_with_custom_prompt(
            narrative="Test narrative", custom_prompt="Test prompt: {narrative}"
        )

        assert result["story"] == ""  # Should be stripped

    @patch("time.time")
    def test_get_story_with_custom_prompt_timestamp(self, mock_time):
        """Test that timestamp is correctly added to metadata"""
        mock_time.return_value = 1234567890.123
        self.mock_openai_client.generate_simple_completion.return_value = (
            "Generated story"
        )

        result = self.generator.get_story_with_custom_prompt(
            narrative="Test narrative", custom_prompt="Test prompt: {narrative}"
        )

        assert result["metadata"]["timestamp"] == 1234567890.123


if __name__ == "__main__":
    pytest.main([__file__])
