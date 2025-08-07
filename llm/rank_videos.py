"""
Video Ranking Module

This module uses the LLM client to rank YouTube videos based on their relevance
to a given narrative. It analyzes video metadata and determines which videos
are most aligned with the narrative theme.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from clients.openai_client import OpenAIClient

# Set up logging
logger = logging.getLogger(__name__)


class VideoRanker:
    """Rank videos based on their relevance to a narrative using LLM."""

    def __init__(self, openai_client: Optional[OpenAIClient] = None):
        """
        Initialize the video ranker.

        Args:
            openai_client: Optional OpenAI client instance. If None, creates a new one.
        """
        self.openai_client = openai_client or OpenAIClient()

    def rank_videos(
        self, videos: List[Dict[str, Any]], narrative: str
    ) -> List[Dict[str, Any]]:
        """
        Rank videos based on their relevance to the narrative.

        Args:
            videos: List of video dictionaries with metadata
            narrative: The narrative to rank against

        Returns:
            List of videos sorted by relevance (most relevant first),
            with added relevance_score and relevance_reasoning fields.
            Only returns videos with relevance_score >= 6.0

        Raises:
            Exception: If ranking fails
        """
        if not videos:
            logger.warning("No videos provided for ranking")
            return []

        try:
            # Create system prompt for ranking
            system_prompt = self._create_system_prompt()

            # Create user prompt with videos and narrative
            user_prompt = self._create_user_prompt(videos, narrative)

            # Generate ranking using LLM
            response = self.openai_client.generate_simple_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for more consistent ranking
                max_tokens=2000,  # Enough for detailed analysis
            )

            # Parse the response and apply rankings
            ranked_videos = self._parse_ranking_response(response, videos)

            # Filter out videos with relevance score below 8.0
            filtered_videos = [
                video
                for video in ranked_videos
                if video.get("relevance_score", 0) >= 8.0
            ]

            logger.info(
                f"Successfully ranked {len(ranked_videos)} videos, filtered to {len(filtered_videos)} relevant videos (score >= 8.0)"
            )
            return filtered_videos

        except Exception as e:
            logger.error(f"Video ranking failed: {str(e)}")
            # Return empty list if ranking fails to maintain filtering behavior
            return []

    def _create_system_prompt(self) -> str:
        """Create the system prompt for video ranking."""
        return """You are a video content analyst specializing in narrative alignment. Your task is to analyze YouTube videos and rank them based on their relevance to a given narrative theme.

For each video, you will analyze:
1. Title - How well does it align with the narrative?
2. Description - Does the content description support the narrative?
3. Uploader - Is the channel type relevant to the narrative?
4. Duration - Is the video length appropriate for the narrative content?
5. View count - Does popularity indicate relevance?

You must provide a JSON response with the following structure:
{
  "rankings": [
    {
      "video_id": "video_id_here",
      "relevance_score": 8.5,
      "relevance_reasoning": "Detailed explanation of why this video is relevant to the narrative"
    }
  ]
}

Scoring criteria:
- 9-10: Perfectly aligned with narrative, highly relevant content
- 7-8: Strong alignment, clearly relevant
- 5-6: Moderate alignment, somewhat relevant
- 3-4: Weak alignment, tangentially relevant
- 1-2: Poor alignment, barely relevant

Focus on narrative alignment over video quality or popularity. Be thorough in your reasoning."""

    def _create_user_prompt(self, videos: List[Dict[str, Any]], narrative: str) -> str:
        """Create the user prompt with video data and narrative."""

        # Format videos for analysis
        video_data = []
        for video in videos:
            video_info = {
                "id": video.get("id", ""),
                "title": video.get("title", ""),
                "description": video.get("description", "")[
                    :300
                ],  # Truncate for token efficiency
                "uploader": video.get("uploader", ""),
                "duration": video.get("duration", 0),
                "view_count": video.get("view_count", 0),
            }
            video_data.append(video_info)

        prompt = f"""Narrative: "{narrative}"

Videos to analyze and rank:
{json.dumps(video_data, indent=2)}

Please analyze each video's relevance to the narrative and provide rankings in the specified JSON format. Consider how well each video's content, as indicated by its title, description, and context, aligns with the narrative theme.

Focus on:
1. Thematic alignment with the narrative
2. Content relevance based on available metadata
3. Appropriateness of the video format for the narrative
4. Potential storytelling value

Provide your response as valid JSON only."""

        return prompt

    def _parse_ranking_response(
        self, response: str, original_videos: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Parse the LLM response and apply rankings to videos.

        Args:
            response: LLM response containing rankings
            original_videos: Original video list to apply rankings to

        Returns:
            Sorted list of videos with ranking information
        """
        try:
            # Clean the response to extract JSON
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:-3]
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:-3]

            # Parse JSON response
            ranking_data = json.loads(cleaned_response)
            rankings = ranking_data.get("rankings", [])

            # Create a mapping of video_id to ranking info
            ranking_map = {}
            for ranking in rankings:
                video_id = ranking.get("video_id", "")
                ranking_map[video_id] = {
                    "relevance_score": ranking.get("relevance_score", 5.0),
                    "relevance_reasoning": ranking.get(
                        "relevance_reasoning", "No reasoning provided"
                    ),
                }

            # Apply rankings to original videos
            enhanced_videos = []
            for video in original_videos:
                video_id = video.get("id", "")
                enhanced_video = video.copy()

                if video_id in ranking_map:
                    enhanced_video.update(ranking_map[video_id])
                else:
                    # Default values if ranking not found
                    enhanced_video["relevance_score"] = 5.0
                    enhanced_video["relevance_reasoning"] = "No ranking provided"

                enhanced_videos.append(enhanced_video)

            # Sort by relevance score (highest first)
            enhanced_videos.sort(
                key=lambda x: x.get("relevance_score", 5.0), reverse=True
            )

            return enhanced_videos

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse ranking response as JSON: {e}")
            logger.error(f"Response was: {response}")
            # Return original videos with default scores
            return self._add_default_rankings(original_videos)

        except Exception as e:
            logger.error(f"Error parsing ranking response: {e}")
            return self._add_default_rankings(original_videos)

    def _add_default_rankings(
        self, videos: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Add default ranking information to videos when parsing fails."""
        for video in videos:
            video["relevance_score"] = 5.0
            video["relevance_reasoning"] = "Ranking failed, using default score"
        return videos
