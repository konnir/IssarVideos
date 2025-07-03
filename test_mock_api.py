#!/usr/bin/env python3
"""
Mock version of the video keyword generator for testing purposes
when OpenAI quota is exhausted.
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

def test_with_mock():
    """Test the API with a mocked OpenAI response"""
    
    def mock_generate_keywords(self, story, max_keywords=10):
        """Mock keyword generation that returns a realistic response"""
        # Simple keyword extraction based on story content
        story_lower = story.lower()
        
        if "artist" in story_lower and "success" in story_lower:
            return {"search_query": "artist success story"}
        elif "cooking" in story_lower:
            return {"search_query": "cooking tutorial"}
        elif "dog" in story_lower and "training" in story_lower:
            return {"search_query": "dog training tips"}
        elif "family" in story_lower and "secret" in story_lower:
            return {"search_query": "family secret discovery"}
        else:
            # Default response based on common story themes
            return {"search_query": "inspirational life story"}
    
    print("🎭 Testing with Mock OpenAI Response")
    print("=" * 60)
    
    client = TestClient(app)
    
    test_stories = [
        "A young artist struggles with self-doubt but eventually finds success through dedication and perseverance.",
        "A woman discovers an old photograph that reveals a family secret, leading her on a journey of self-discovery.",
        "A chef learns to cook from their grandmother and opens their own restaurant.",
        "A person trains their rescue dog and they become therapy partners.",
        "Someone overcomes a major life challenge and inspires others."
    ]
    
    # Patch the VideoKeywordGenerator.generate_keywords method
    with patch('llm.get_videos.VideoKeywordGenerator.generate_keywords', mock_generate_keywords):
        for i, story in enumerate(test_stories, 1):
            print(f"\n📝 Test {i}:")
            print(f"Story: {story[:60]}...")
            
            request_data = {
                "story": story,
                "max_keywords": 10
            }
            
            response = client.post("/generate-video-keywords", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Search Query: \"{result['search_query']}\"")
            else:
                print(f"❌ Error: {response.status_code} - {response.json()}")
    
    print("\n" + "=" * 60)
    print("🎉 Mock Testing Complete!")
    print("✅ The API structure is working correctly")
    print("💡 When OpenAI quota is restored, it will generate real optimized queries")

if __name__ == "__main__":
    test_with_mock()
