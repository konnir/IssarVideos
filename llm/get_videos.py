"""
Video Search Query Generator

This module uses the LLM client to generate optimized YouTube search queries
based on a given story. It provides functionality to analyze stories and
generate a single, effective search string for finding suitable video content.
"""

import logging
from typing import Dict, Any, Optional
from clients.openai_client import OpenAIClient

# Set up logging
logger = logging.getLogger(__name__)


class VideoKeywordGenerator:
    """Generate YouTube search query based on story content using LLM."""

    def __init__(self, openai_client: Optional[OpenAIClient] = None):
        """
        Initialize the video search query generator.

        Args:
            openai_client: Optional OpenAI client instance. If None, creates a new one.
        """
        self.openai_client = openai_client or OpenAIClient()

    def generate_keywords(self, story: str, max_keywords: int = 10) -> Dict[str, Any]:
        """
        Generate a single optimized YouTube search query based on a story.

        Args:
            story: The story content to analyze
            max_keywords: Not used, kept for API compatibility

        Returns:
            Dictionary containing:
            - search_query: Single optimized YouTube search string

        Raises:
            Exception: If search query generation fails
        """
        try:
            # Create system prompt for single search query generation
            system_prompt = self._create_system_prompt()

            # Create user prompt with the story
            user_prompt = self._create_user_prompt(story)

            # Generate search query using LLM
            response = self.openai_client.generate_simple_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.5,  # Less creative, more focused
                max_tokens=50,  # Short response
            )

            # Clean up the response
            search_query = response.strip().strip('"').strip("'")

            return {"search_query": search_query}

        except Exception as e:
            logger.error(f"Search query generation failed: {str(e)}")
            raise Exception(f"Failed to generate search query: {str(e)}")

    def _create_system_prompt(self) -> str:
        """Create the system prompt for search query generation."""

        return """You are a YouTube search expert. Your task is to analyze a story and generate ONE optimized search query that would find the most relevant videos on YouTube.

Requirements:
- Return only ONE search query (2-6 words)
- Focus on the main theme/concept that would have actual videos
- Use terms people actually search for on YouTube
- Make it broad enough to find results but specific to the story theme
- Do not include quotes or extra formatting

Examples:
Story about cooking pasta → "pasta cooking tutorial"
Story about dog training → "dog training tips"
Story about artist success → "artist success story"

Return ONLY the search query, nothing else."""

    def _create_user_prompt(self, story: str) -> str:
        """Create the user prompt with the story content."""

        return f"""Story: "{story}"

Generate ONE YouTube search query that would find videos related to this story's main theme."""
