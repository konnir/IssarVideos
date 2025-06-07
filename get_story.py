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
        video_duration: int = 180,  # 3 minutes in seconds
        style: str = "engaging",
        platform: str = "general",
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a story based on a hidden narrative.
        
        Args:
            narrative: The hidden narrative to base the story on
            video_duration: Maximum video duration in seconds (default: 180 = 3 minutes)
            style: Story style (engaging, dramatic, educational, humorous, etc.)
            platform: Target platform (youtube, tiktok, instagram, general)
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
            system_prompt = self._create_system_prompt(video_duration, style, platform)
            
            # Create user prompt
            user_prompt = self._create_user_prompt(narrative, additional_context)
            
            # Generate story
            story = self.openai_client.generate_simple_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.8,  # Higher creativity
                max_tokens=800,   # Reasonable length for 3-minute video
            )
            
            return {
                "story": story,
                "narrative": narrative,
                "metadata": {
                    "video_duration": video_duration,
                    "style": style,
                    "platform": platform,
                    "word_count": len(story.split()),
                    "character_count": len(story)
                }
            }
            
        except Exception as e:
            logger.error(f"Story generation failed: {str(e)}")
            raise Exception(f"Failed to generate story: {str(e)}")
    
    def _create_system_prompt(self, video_duration: int, style: str, platform: str) -> str:
        """Create the system prompt for story generation."""
        
        duration_minutes = video_duration // 60
        
        platform_guidelines = {
            "youtube": "engaging and educational, suitable for longer-form content",
            "tiktok": "fast-paced, attention-grabbing, with quick hooks",
            "instagram": "visually appealing and shareable",
            "general": "versatile and engaging"
        }
        
        platform_guidance = platform_guidelines.get(platform, platform_guidelines["general"])
        
        return f"""You are a creative video storyteller specializing in creating compelling narratives for video content.

Your task is to create a story outline for a {duration_minutes}-minute video that subtly incorporates a hidden narrative or theme.

Story Requirements:
- Duration: Maximum {duration_minutes} minutes of video content
- Style: {style}
- Platform: {platform} ({platform_guidance})
- The story should be descriptive enough for video production
- Include visual elements, scenes, and potential dialogue
- Keep it concise but engaging
- The hidden narrative should be woven naturally into the story
- Focus on storytelling elements that work well in video format

Format your response as a clear, structured story outline that a video creator could follow."""
    
    def _create_user_prompt(self, narrative: str, additional_context: Optional[str]) -> str:
        """Create the user prompt with the narrative and context."""
        
        prompt = f"""Create a compelling video story that incorporates this hidden narrative:

Hidden Narrative: "{narrative}"

The story should:
1. Be suitable for a 3-minute video
2. Naturally incorporate the hidden narrative without being obvious
3. Include specific scenes, visual elements, and potential dialogue
4. Be engaging and suitable for public video platforms
5. Focus on storytelling that translates well to video format

Please provide a detailed story outline that includes:
- Opening hook/scene
- Main story progression
- Key visual moments
- Suggested dialogue or narration points
- Conclusion that reinforces the hidden narrative"""
        
        if additional_context:
            prompt += f"\n\nAdditional Context: {additional_context}"
        
        return prompt
    
    def get_multiple_story_variants(
        self,
        narrative: str,
        count: int = 3,
        **kwargs
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
        self,
        original_story: str,
        refinement_request: str,
        narrative: str
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
                max_tokens=800
            )
            
            return {
                "story": refined_story,
                "original_story": original_story,
                "narrative": narrative,
                "refinement_request": refinement_request,
                "metadata": {
                    "word_count": len(refined_story.split()),
                    "character_count": len(refined_story),
                    "is_refinement": True
                }
            }
            
        except Exception as e:
            logger.error(f"Story refinement failed: {str(e)}")
            raise Exception(f"Failed to refine story: {str(e)}")


# Convenience function for quick story generation
def generate_story_for_narrative(
    narrative: str,
    **kwargs
) -> Dict[str, Any]:
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
