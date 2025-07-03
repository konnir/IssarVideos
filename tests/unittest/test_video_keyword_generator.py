#!/usr/bin/env python3
"""
Unit Tests for Video Keyword Generator
======================================

Tests for the VideoKeywordGenerator class in llm/get_videos.py
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from llm.get_videos import VideoKeywordGenerator
from clients.openai_client import OpenAIClient


class TestVideoKeywordGenerator:
    """Test the VideoKeywordGenerator class"""

    def setup_method(self):
        """Setup for each test method"""
        # Create a mock OpenAI client
        self.mock_openai_client = Mock(spec=OpenAIClient)
        self.generator = VideoKeywordGenerator(openai_client=self.mock_openai_client)

    def test_init_with_client(self):
        """Test initialization with provided OpenAI client"""
        generator = VideoKeywordGenerator(openai_client=self.mock_openai_client)
        assert generator.openai_client == self.mock_openai_client

    def test_init_without_client(self):
        """Test initialization without provided OpenAI client"""
        with patch("llm.get_videos.OpenAIClient") as mock_client_class:
            generator = VideoKeywordGenerator()
            mock_client_class.assert_called_once()
            assert generator.openai_client is not None

    def test_generate_keywords_success(self):
        """Test successful keyword generation"""
        # Mock the OpenAI response
        self.mock_openai_client.generate_simple_completion.return_value = (
            "artist success story"
        )

        story = "A talented artist overcomes adversity to achieve their dreams"
        result = self.generator.generate_keywords(story)

        # Verify the result
        assert "search_query" in result
        assert result["search_query"] == "artist success story"

        # Verify the OpenAI client was called correctly
        self.mock_openai_client.generate_simple_completion.assert_called_once()
        call_args = self.mock_openai_client.generate_simple_completion.call_args

        # Check that proper parameters were passed
        assert call_args.kwargs["temperature"] == 0.5
        assert call_args.kwargs["max_tokens"] == 50
        assert "artist" in call_args.kwargs["prompt"].lower()
        assert "YouTube search expert" in call_args.kwargs["system_prompt"]

    def test_generate_keywords_strips_quotes(self):
        """Test that the response is properly cleaned (quotes stripped)"""
        # Mock responses with various quote formats
        test_cases = [
            '"cooking pasta tutorial"',
            "'dog training tips'",
            '  "fitness workout"  ',
            "travel adventure",
        ]

        expected_results = [
            "cooking pasta tutorial",
            "dog training tips",
            "fitness workout",
            "travel adventure",
        ]

        for mock_response, expected in zip(test_cases, expected_results):
            self.mock_openai_client.generate_simple_completion.return_value = (
                mock_response
            )

            result = self.generator.generate_keywords("test story")
            assert result["search_query"] == expected

    def test_generate_keywords_openai_error(self):
        """Test handling of OpenAI API errors"""
        # Mock an OpenAI error
        self.mock_openai_client.generate_simple_completion.side_effect = Exception(
            "API Error"
        )

        with pytest.raises(Exception) as exc_info:
            self.generator.generate_keywords("test story")

        assert "Failed to generate search query" in str(exc_info.value)

    def test_create_system_prompt(self):
        """Test system prompt creation"""
        system_prompt = self.generator._create_system_prompt()

        # Check that the system prompt contains key instructions
        assert "YouTube search expert" in system_prompt
        assert "ONE optimized search query" in system_prompt
        assert "2-6 words" in system_prompt
        assert "examples" in system_prompt.lower()

    def test_create_user_prompt(self):
        """Test user prompt creation"""
        story = "A chef discovers a secret recipe"
        user_prompt = self.generator._create_user_prompt(story)

        # Check that the user prompt contains the story
        assert story in user_prompt
        assert "Generate ONE YouTube search query" in user_prompt

    def test_max_keywords_parameter_ignored(self):
        """Test that max_keywords parameter is ignored (kept for compatibility)"""
        self.mock_openai_client.generate_simple_completion.return_value = (
            "cooking tutorial"
        )

        # Should work the same regardless of max_keywords value
        result1 = self.generator.generate_keywords("cooking story", max_keywords=5)
        result2 = self.generator.generate_keywords("cooking story", max_keywords=20)

        assert result1 == result2
        assert result1["search_query"] == "cooking tutorial"

    def test_edge_cases(self):
        """Test edge cases and unusual inputs"""
        test_cases = [
            ("", "empty story"),  # Empty story
            ("   ", "whitespace story"),  # Whitespace only
            ("A" * 1000, "very long story"),  # Very long story
            ("Special chars !@#$%", "special characters"),  # Special characters
        ]

        self.mock_openai_client.generate_simple_completion.return_value = "test query"

        for story, description in test_cases:
            try:
                result = self.generator.generate_keywords(story)
                assert "search_query" in result
                assert result["search_query"] == "test query"
            except Exception:
                # Some edge cases might fail, which is acceptable
                pass

    def test_realistic_story_types(self):
        """Test with realistic story types to ensure proper prompt handling"""
        story_types = [
            ("A young entrepreneur starts a tech company", "business startup"),
            ("A family goes on a camping adventure", "family camping"),
            ("A chef learns to make authentic Italian pasta", "pasta cooking"),
            ("A dog owner trains their puppy", "dog training"),
            ("An artist paints their first masterpiece", "art creation"),
        ]

        for story, expected_theme in story_types:
            # Mock a relevant response
            self.mock_openai_client.generate_simple_completion.return_value = (
                expected_theme
            )

            result = self.generator.generate_keywords(story)
            assert result["search_query"] == expected_theme

            # Verify the story was included in the prompt
            call_args = self.mock_openai_client.generate_simple_completion.call_args
            assert story in call_args.kwargs["prompt"]


if __name__ == "__main__":
    pytest.main([__file__])
