#!/usr/bin/env python3
"""
Unit Tests for Main Application Functions
========================================

Tests for utility functions in main.py including YouTube Shorts conversion.
"""
import pytest
import sys
from pathlib import Path

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main import convert_youtube_shorts_url


class TestMainFunctions:
    """Test utility functions from main.py"""

    def test_convert_youtube_shorts_url_valid_shorts(self):
        """Test conversion of valid YouTube Shorts URLs"""
        # Test basic shorts URL
        shorts_url = "https://www.youtube.com/shorts/9m19poxkkpg"
        expected = "https://www.youtube.com/watch?v=9m19poxkkpg"
        result = convert_youtube_shorts_url(shorts_url)
        assert result == expected

        # Test shorts URL with query parameters
        shorts_url_with_params = "https://www.youtube.com/shorts/9m19poxkkpg?feature=share"
        expected_with_params = "https://www.youtube.com/watch?v=9m19poxkkpg"
        result_with_params = convert_youtube_shorts_url(shorts_url_with_params)
        assert result_with_params == expected_with_params

        # Test shorts URL with fragment
        shorts_url_with_fragment = "https://www.youtube.com/shorts/9m19poxkkpg#t=10"
        expected_with_fragment = "https://www.youtube.com/watch?v=9m19poxkkpg"
        result_with_fragment = convert_youtube_shorts_url(shorts_url_with_fragment)
        assert result_with_fragment == expected_with_fragment

    def test_convert_youtube_shorts_url_regular_youtube(self):
        """Test that regular YouTube URLs are not modified"""
        # Regular YouTube URL should remain unchanged
        regular_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = convert_youtube_shorts_url(regular_url)
        assert result == regular_url

        # YouTube embed URL should remain unchanged
        embed_url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        result_embed = convert_youtube_shorts_url(embed_url)
        assert result_embed == embed_url

        # Shortened YouTube URL should remain unchanged
        short_url = "https://youtu.be/dQw4w9WgXcQ"
        result_short = convert_youtube_shorts_url(short_url)
        assert result_short == short_url

    def test_convert_youtube_shorts_url_non_youtube(self):
        """Test that non-YouTube URLs are not modified"""
        # TikTok URL should remain unchanged
        tiktok_url = "https://www.tiktok.com/@username/video/1234567890"
        result_tiktok = convert_youtube_shorts_url(tiktok_url)
        assert result_tiktok == tiktok_url

        # Generic URL should remain unchanged
        generic_url = "https://example.com/video"
        result_generic = convert_youtube_shorts_url(generic_url)
        assert result_generic == generic_url

        # Empty string should remain unchanged
        empty_result = convert_youtube_shorts_url("")
        assert empty_result == ""

    def test_convert_youtube_shorts_url_edge_cases(self):
        """Test edge cases for YouTube Shorts conversion"""
        # None input should return None
        none_result = convert_youtube_shorts_url(None)
        assert none_result is None

        # Non-string input should return as-is
        number_input = 123
        number_result = convert_youtube_shorts_url(number_input)
        assert number_result == number_input

        # Malformed shorts URL (no video ID) - function will try to convert but result will be empty video ID
        malformed_url = "https://www.youtube.com/shorts/"
        malformed_result = convert_youtube_shorts_url(malformed_url)
        # Since there's no video ID after /shorts/, it becomes /watch?v=
        assert malformed_result == "https://www.youtube.com/watch?v="

        # URL without protocol should work if it contains shorts pattern
        no_protocol = "www.youtube.com/shorts/abc123"
        no_protocol_result = convert_youtube_shorts_url(no_protocol)
        expected_no_protocol = "https://www.youtube.com/watch?v=abc123"
        assert no_protocol_result == expected_no_protocol

    def test_convert_youtube_shorts_url_different_domains(self):
        """Test YouTube Shorts conversion with different domain formats"""
        # Test with mobile YouTube domain - function will convert since it contains "youtube.com/shorts/"
        mobile_shorts = "https://m.youtube.com/shorts/abc123"
        mobile_result = convert_youtube_shorts_url(mobile_shorts)
        # Will be converted since it matches the pattern
        expected_mobile = "https://www.youtube.com/watch?v=abc123"
        assert mobile_result == expected_mobile

        # Test with youtube-nocookie domain - should remain unchanged since it doesn't contain "youtube.com/shorts/"
        nocookie_shorts = "https://www.youtube-nocookie.com/shorts/abc123"
        nocookie_result = convert_youtube_shorts_url(nocookie_shorts)
        # Should remain unchanged as it contains "youtube-nocookie.com" not "youtube.com"
        assert nocookie_result == nocookie_shorts

    def test_convert_youtube_shorts_url_case_sensitivity(self):
        """Test case sensitivity in URL conversion"""
        # Test with uppercase SHORTS
        upper_shorts = "https://www.youtube.com/SHORTS/abc123"
        upper_result = convert_youtube_shorts_url(upper_shorts)
        # Should remain unchanged as our function is case-sensitive
        assert upper_result == upper_shorts

        # Test with mixed case
        mixed_shorts = "https://www.YouTube.com/shorts/abc123"
        mixed_result = convert_youtube_shorts_url(mixed_shorts)
        # Should remain unchanged as our function checks for exact "youtube.com"
        assert mixed_result == mixed_shorts
