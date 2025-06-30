"""
Video search module for finding relevant videos based on stories.
Uses OpenAI to generate search queries and simulate video search results.
"""

import logging
import time
import json
from typing import Optional, Dict, Any, List
from clients.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class VideoSearcher:
    """Search for videos based on story content using AI-generated queries."""

    def __init__(self, openai_client: Optional[OpenAIClient] = None):
        """
        Initialize the video searcher.

        Args:
            openai_client: Optional OpenAI client instance. If None, creates a new one.
        """
        self.openai_client = openai_client or OpenAIClient()

    def search_videos(
        self,
        story: str,
        max_duration: int = 300,  # 5 minutes
        platforms: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Search for videos based on a story description using real web search.

        Args:
            story: The story to search videos for
            max_duration: Maximum video duration in seconds (default: 5 minutes)
            platforms: List of platforms to search (default: YouTube, TikTok)

        Returns:
            Dictionary containing:
            - query: The generated search query
            - results: List of 5 video results from web search
            - metadata: Additional information about the search

        Raises:
            Exception: If video search fails
        """
        if platforms is None:
            platforms = ["youtube", "tiktok"]

        try:
            # Generate optimized search query using OpenAI
            search_query = self._generate_search_query(story, max_duration, platforms)

            # Perform actual web search for videos
            video_results = self._search_videos_web(
                search_query, story, platforms, max_duration
            )

            return {
                "query": search_query,
                "results": video_results,
                "metadata": {
                    "platforms": platforms,
                    "max_duration": max_duration,
                    "result_count": len(video_results),
                    "timestamp": time.time(),
                },
            }

        except Exception as e:
            logger.error(f"Video search failed: {str(e)}")
            raise Exception(f"Failed to search videos: {str(e)}")

    def _generate_search_query(
        self, story: str, max_duration: int, platforms: List[str]
    ) -> str:
        """
        Generate an optimized search query based on the story.

        Args:
            story: The story content
            max_duration: Maximum duration constraint
            platforms: Target platforms

        Returns:
            Optimized search query string
        """
        system_prompt = """You are a video search expert. Your task is to create the most effective search query to find short videos that match a given story description.

Requirements:
- Create a concise, keyword-rich search query
- Focus on visual and action-oriented terms
- Consider platform-specific content styles
- Optimize for discoverability
- Keep it under 10 words for best results

Return ONLY the search query, nothing else."""

        user_prompt = f"""Create an optimal search query for finding videos matching this story:

Story: "{story}"

Target platforms: {', '.join(platforms)}
Max duration: {max_duration} seconds ({max_duration // 60} minutes)

The query should help find short videos that tell or demonstrate this story. Focus on the key visual elements, actions, or themes that would be searchable."""

        try:
            search_query = self.openai_client.generate_simple_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for more focused results
                max_tokens=50,  # Short query
            )
            return search_query.strip().strip('"').strip("'")
        except Exception as e:
            logger.error(f"Failed to generate search query: {str(e)}")
            # Fallback: extract key words from story
            words = story.split()[:5]  # Take first 5 words as fallback
            return " ".join(words)

    def _search_videos_web(
        self, query: str, story: str, platforms: List[str], max_duration: int
    ) -> List[Dict[str, Any]]:
        """
        Search for videos using OpenAI's web search tool - simplified version.

        Args:
            query: The search query
            story: Original story for context
            platforms: Target platforms
            max_duration: Maximum duration

        Returns:
            List of 5 video results from web search
        """
        try:
            # Enhanced search prompt asking for real, verifiable videos
            search_input = f"""Find 5 REAL, currently accessible YouTube videos about: {query}

CRITICAL REQUIREMENTS:
- Only videos published after 2022 (less than 3 years old)
- Provide ACTUAL YouTube video URLs that work (not placeholders like "example1")
- Include the complete YouTube video ID (11-character alphanumeric string)
- Verify the videos are currently available and not deleted

For each video, provide:
- Exact title as it appears on YouTube
- Platform: youtube
- Complete working URL: https://www.youtube.com/watch?v=[REAL_VIDEO_ID]
- Duration in minutes/seconds
- Brief description of content
- Upload date or year
- Channel name

IMPORTANT: Do not use placeholder URLs like "example1", "example2", etc. Only provide real, working YouTube links that users can actually visit."""

            # Use OpenAI responses API
            response = self.openai_client.client.responses.create(
                model="gpt-4o",
                tools=[{"type": "web_search_preview"}],
                input=search_input,
            )

            search_results = response.output_text
            logger.info("Successfully used web search tool via responses API")

            # Print raw search results for debugging
            print("=" * 80)
            print("🔍 RAW OPENAI SEARCH RESULTS:")
            print("=" * 80)
            print(search_results)
            print("=" * 80)

            # Simple parsing - ask OpenAI to extract 5 videos from the results
            return self._simple_parse_results(search_results, max_duration)

        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")
            raise Exception(f"Video search failed: {str(e)}")

    def _simple_parse_results(
        self, search_results: str, max_duration: int
    ) -> List[Dict[str, Any]]:
        """
        Simple parsing - just ask OpenAI to extract 5 videos, no validation.

        Args:
            search_results: Raw search results from OpenAI
            max_duration: Maximum duration for videos

        Returns:
            List of 5 video results (whatever OpenAI gives us)
        """
        parse_prompt = f"""Extract 5 REAL YouTube videos from these search results. Only include videos with WORKING URLs.

Search Results:
{search_results}

CRITICAL: Skip any videos with placeholder URLs (like "example1", "example2", etc.) or invalid video IDs.

Return exactly 5 videos as JSON array. For each video include:
- title (exact title from YouTube)
- platform (always "youtube")
- url (complete working YouTube URL with real 11-character video ID)
- duration (in seconds, max {max_duration})
- description
- channel (YouTube channel name)

Format:
[
  {{
    "title": "Exact Video Title",
    "platform": "youtube", 
    "url": "https://www.youtube.com/watch?v=REAL_VIDEO_ID",
    "duration": 180,
    "description": "Video description",
    "channel": "Channel Name"
  }}
]

Only include videos with REAL YouTube URLs that contain valid 11-character alphanumeric video IDs."""

        try:
            response = self.openai_client.generate_simple_completion(
                prompt=parse_prompt,
                temperature=0.1,
                max_tokens=1000,
            )

            # Clean JSON response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]

            results = json.loads(response)

            # Filter out any videos with invalid URLs
            valid_results = []
            for video in results:
                if "url" in video and "youtube.com/watch?v=" in video["url"]:
                    video_id = video["url"].split("v=")[1].split("&")[0]
                    # Check if it's a valid YouTube video ID (not placeholder)
                    if (
                        len(video_id) == 11
                        and not video_id.startswith("example")
                        and not "," in video_id
                    ):
                        valid_results.append(video)

            # If we have valid results, return them; otherwise return original results
            if valid_results:
                return valid_results[:5]  # Return up to 5 valid results
            else:
                # Fallback: return original results but log the issue
                logger.warning(
                    "No valid YouTube URLs found, returning original results"
                )
                return results[:5]

        except Exception as e:
            logger.error(f"Failed to parse results: {str(e)}")
            raise Exception(f"Failed to parse video results: {str(e)}")

    # Remove all the complex validation methods - we don't need them anymore


# Convenience function for quick video search
def search_videos_for_story(story: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to quickly search videos for a story.

    Args:
        story: The story to search videos for
        **kwargs: Additional parameters for VideoSearcher.search_videos

    Returns:
        Video search results dictionary
    """
    searcher = VideoSearcher()
    return searcher.search_videos(story, **kwargs)
