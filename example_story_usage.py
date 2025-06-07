"""
Example usage of the story generation system.
This file demonstrates how to use the OpenAI client and story generator.
"""

import os
from llm.get_story import StoryGenerator, generate_story_for_narrative


def example_story_generation():
    """Example of generating a story from a narrative."""
    
    # Example narrative
    narrative = "The importance of authentic human connection in a digital world"
    
    print("🎬 Video Story Generator Example")
    print("=" * 50)
    print(f"Hidden Narrative: {narrative}")
    print()
    
    try:
        # Method 1: Using the convenience function
        print("📝 Generating story using convenience function...")
        story_result = generate_story_for_narrative(
            narrative=narrative,
            style="engaging"
        )
        
        print("✅ Story generated successfully!")
        print(f"Story length: {story_result['metadata']['word_count']} words")
        print()
        print("Generated Story:")
        print("-" * 30)
        print(story_result['story'])
        print("-" * 30)
        print()
        
        # Method 2: Using the StoryGenerator class directly
        print("📝 Generating alternative version...")
        generator = StoryGenerator()
        
        alternative_story = generator.get_story(
            narrative=narrative,
            style="dramatic",
            additional_context="Focus on a young protagonist's journey"
        )
        
        print("✅ Alternative story generated!")
        print(f"Story length: {alternative_story['metadata']['word_count']} words")
        print()
        print("Alternative Story:")
        print("-" * 30)
        print(alternative_story['story'])
        print("-" * 30)
        print()
        
        # Method 3: Generate multiple variants
        print("📝 Generating multiple story variants...")
        variants = generator.get_multiple_story_variants(
            narrative=narrative,
            count=2,
            style="humorous"
        )
        
        for i, variant in enumerate(variants, 1):
            print(f"✅ Variant {i} generated! ({variant['metadata']['word_count']} words)")
        
    except Exception as e:
        print(f"❌ Error generating story: {str(e)}")
        print("💡 Make sure to set your OPENAI_API_KEY environment variable")


def test_openai_connection():
    """Test the OpenAI connection."""
    print("🔗 Testing OpenAI Connection...")
    
    try:
        from clients.openai_client import OpenAIClient
        
        client = OpenAIClient()
        if client.validate_connection():
            print("✅ OpenAI connection successful!")
            return True
        else:
            print("❌ OpenAI connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {str(e)}")
        return False


if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key before running this example:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print()
    
    # Test connection first
    if test_openai_connection():
        print()
        example_story_generation()
    else:
        print("\n💡 Please check your OpenAI API key and try again.")
