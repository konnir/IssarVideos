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

    def generate_keywords(
        self, narrative: str, story: str, max_keywords: int = 10
    ) -> Dict[str, Any]:
        """
        Generate a single optimized YouTube search query based on a story.

        Args:
            narrative: The narrative content to analyze
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
            user_prompt = self._create_user_prompt(story, narrative)

            # Generate search query using LLM
            response = self.openai_client.generate_simple_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.8,  # More creative, less focused
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

        return """You are a YouTube search expert. Your task is to generate ONE optimized search query that aligns with a given narrative theme and is grounded in a supporting story.

Instructions:
- Your goal is to create a search query (2-6 words) that helps find relevant YouTube videos aligned with the core narrative concept.
- Use the story to inform tone or context, but focus on capturing the broader theme.
- Favor phrases that reflect change, action, or emotional stakes (e.g., quitting, overcoming, learning, rediscovering), rather than static descriptors.
- Avoid generic terms. Use specific, searchable phrases that reflect the unique aspects of each story.
- Do not include quotes, formatting, or additional commentary.

Examples across different domains:

Career & Professional:
Narrative: Career pivoting as growth  
Story: A burnt-out office worker rediscovers their love for music and begins performing at open mics.  
→ "office worker musician transition"

Technology & Innovation:
Narrative: Embracing technological change
Story: An elderly librarian learns to use tablets to help visitors access digital resources.
→ "elderly librarian uses tablets"

Relationships & Family:
Narrative: Intergenerational bonding
Story: A teenager teaches their grandmother how to play video games, creating unexpected friendship.
→ "grandma grandson gaming"

Health & Wellness:
Narrative: Mental health awareness
Story: A college student starts a mindfulness club after overcoming anxiety through meditation.
→ "student anxiety meditation"

Creativity & Arts:
Narrative: Artistic self-expression
Story: A shy accountant discovers street art and transforms their neighborhood with colorful murals.
→ "accountant street art transformation"

Adventure & Travel:
Narrative: Finding courage through exploration
Story: A person afraid of heights decides to go skydiving and discovers inner strength.
→ "fear of heights skydiving"

Creativity & Identity:
Narrative: Reclaiming identity through art  
Story: A factory worker secretly paints abstract self-portraits at night, eventually displaying them anonymously around town.  
→ "factory worker secret street art"

Community & Social Impact:
Narrative: Grassroots activism
Story: Neighbors organize to save a local park from being turned into a parking lot.
→ "neighbors save local park"

Personal Growth:
Narrative: Overcoming limitations
Story: Someone with social anxiety starts a podcast and builds confidence through storytelling.
→ "social anxiety podcast confidence"

Return ONLY the search query. Nothing else."""

    def _create_user_prompt(self, narrative: str, story: str) -> str:
        """Create the user prompt with the story content."""

        return f"""Narrative: "{narrative}"

Story: "{story}"

Based on the narrative theme and how it's expressed in the story, generate ONE YouTube search query that would surface videos reflecting the core idea."""
