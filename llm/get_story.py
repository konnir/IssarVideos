"""
Story generation module for creating video stories based on narratives.
Uses OpenAI GPT-4 to generate creative stories for video content.
"""

import logging
from typing import Optional, Dict, Any, List
from clients.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class StoryGenerator:
    """Generate stories based on hidden narratives for video content."""

    def __init__(self, openai_client: Optional[OpenAIClient] = None):
        """
        Initialize the story generator.

        Args:
            openai_client: Optional OpenAI client instance. If None, creates a new one.
        """
        self.openai_client = openai_client or OpenAIClient()

    def get_story(
        self,
        narrative: str,
        style: str = "engaging",
        additional_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a story based on a hidden narrative.

        Args:
            narrative: The hidden narrative to base the story on
            style: Story style (engaging, dramatic, educational, humorous, etc.)
            additional_context: Optional additional context or requirements

        Returns:
            Dictionary containing:
            - story: The generated story
            - narrative: The original narrative
            - metadata: Additional information about the story

        Raises:
            Exception: If story generation fails
        """
        try:
            # Create system prompt
            system_prompt = self._create_system_prompt(style)

            # Create user prompt
            user_prompt = self._create_user_prompt(narrative, additional_context)

            # Generate story
            story = self.openai_client.generate_simple_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.8,  # Higher creativity
                max_tokens=150,  # Much shorter for brief concepts
            )

            return {
                "story": story,
                "narrative": narrative,
                "metadata": {
                    "style": style,
                    "word_count": len(story.split()),
                    "character_count": len(story),
                },
            }

        except Exception as e:
            logger.error(f"Story generation failed: {str(e)}")
            raise Exception(f"Failed to generate story: {str(e)}")

    def _create_system_prompt(self, style: str) -> str:
        """Create the system prompt for story generation."""

        return f"""You are a creative video storyteller specializing in short video content for public platforms.

Your task is to create a brief story concept that subtly incorporates a hidden narrative.

Requirements:
- Style: {style}
- Keep it very concise: 2-3 sentences maximum
- Focus on the core story idea that can be expanded later
- The hidden narrative should be woven naturally into the concept
- Suitable for short video platforms

Provide only a brief story concept, not a detailed outline."""

    def _create_user_prompt(
        self, narrative: str, additional_context: Optional[str]
    ) -> str:
        """Create the user prompt with the narrative and context."""

        prompt = f"""Create a brief story concept (2-3 sentences) that incorporates this hidden narrative:

Hidden Narrative: "{narrative}"

Provide only a concise story idea that:
1. Subtly includes the hidden narrative
2. Is suitable for short video content
3. Can be expanded into a full video later

Keep it short and focused on the core concept only."""

        if additional_context:
            prompt += f"\n\nAdditional Context: {additional_context}"

        return prompt

    def get_multiple_story_variants(
        self, narrative: str, count: int = 3, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple story variants for the same narrative.

        Args:
            narrative: The hidden narrative
            count: Number of variants to generate
            **kwargs: Additional parameters for get_story

        Returns:
            List of story dictionaries
        """
        stories = []

        for i in range(count):
            try:
                # Vary the temperature slightly for each variant
                variant_kwargs = kwargs.copy()

                story = self.get_story(narrative, **variant_kwargs)
                story["metadata"]["variant_number"] = i + 1
                stories.append(story)

            except Exception as e:
                logger.error(f"Failed to generate story variant {i + 1}: {str(e)}")
                continue

        return stories

    def refine_story(
        self, original_story: str, refinement_request: str, narrative: str
    ) -> Dict[str, Any]:
        """
        Refine an existing story based on feedback or requirements.

        Args:
            original_story: The original story to refine
            refinement_request: Specific refinement instructions
            narrative: The original narrative for context

        Returns:
            Dictionary with refined story and metadata
        """
        try:
            system_prompt = """You are a video story editor. Your task is to refine an existing story based on specific feedback while maintaining the core narrative and video suitability."""

            user_prompt = f"""Please refine this video story based on the following request:

Original Story:
{original_story}

Hidden Narrative: {narrative}

Refinement Request: {refinement_request}

Please provide the refined story that addresses the feedback while maintaining the hidden narrative and video format suitability."""

            refined_story = self.openai_client.generate_simple_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=800,
            )

            return {
                "story": refined_story,
                "original_story": original_story,
                "narrative": narrative,
                "refinement_request": refinement_request,
                "metadata": {
                    "word_count": len(refined_story.split()),
                    "character_count": len(refined_story),
                    "is_refinement": True,
                },
            }

        except Exception as e:
            logger.error(f"Story refinement failed: {str(e)}")
            raise Exception(f"Failed to refine story: {str(e)}")


# Convenience function for quick story generation
def generate_story_for_narrative(narrative: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to quickly generate a story for a narrative.

    Args:
        narrative: The hidden narrative
        **kwargs: Additional parameters for StoryGenerator.get_story

    Returns:
        Story dictionary
    """
    generator = StoryGenerator()
    return generator.get_story(narrative, **kwargs)
