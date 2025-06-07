#!/usr/bin/env python3
"""
Unit Tests for Story Generation Components
==========================================

Tests the individual components of the story generation system.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
import os

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestOpenAIClient:
    """Unit tests for OpenAI client wrapper"""
    
    def test_openai_client_initialization(self):
        """Test OpenAI client initialization"""
        from clients.openai_client import OpenAIClient
        
        # Test with no API key
        client = OpenAIClient()
        assert client is not None
        assert hasattr(client, 'client')
        
        # Test with custom API key
        client_with_key = OpenAIClient(api_key="test-key")
        assert client_with_key is not None

    @patch('clients.openai_client.OpenAI')
    def test_generate_completion_success(self, mock_openai):
        """Test successful completion generation"""
        from clients.openai_client import OpenAIClient
        
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Generated story content"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test
        client = OpenAIClient()
        messages = [{"role": "user", "content": "Generate a story"}]
        
        response = client.generate_completion(messages)
        
        assert response == "Generated story content"
        mock_client.chat.completions.create.assert_called_once()

    @patch('clients.openai_client.OpenAI')
    def test_generate_completion_with_parameters(self, mock_openai):
        """Test completion generation with custom parameters"""
        from clients.openai_client import OpenAIClient
        
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Short story"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test
        client = OpenAIClient()
        messages = [{"role": "user", "content": "Generate a story"}]
        
        response = client.generate_completion(
            messages,
            model="gpt-4",
            max_tokens=100,
            temperature=0.7
        )
        
        assert response == "Short story"
        # Verify the mock was called with the right parameters
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['model'] == "gpt-4"
        assert call_args[1]['max_tokens'] == 100
        assert call_args[1]['temperature'] == 0.7

    @patch('clients.openai_client.OpenAI')
    def test_generate_simple_completion(self, mock_openai):
        """Test simple completion generation"""
        from clients.openai_client import OpenAIClient
        
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Hello!"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test
        client = OpenAIClient()
        response = client.generate_simple_completion("Say hello")
        
        assert response == "Hello!"

    @patch('clients.openai_client.OpenAI')
    def test_validate_connection_success(self, mock_openai):
        """Test successful connection validation"""
        from clients.openai_client import OpenAIClient
        
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Hello!"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test
        client = OpenAIClient()
        is_connected = client.validate_connection()
        
        assert is_connected is True

    @patch('clients.openai_client.OpenAI')
    def test_validate_connection_failure(self, mock_openai):
        """Test connection validation failure"""
        from clients.openai_client import OpenAIClient
        
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        # Test
        client = OpenAIClient()
        is_connected = client.validate_connection()
        
        assert is_connected is False


class TestStoryGenerator:
    """Unit tests for story generator"""
    
    @patch('llm.get_story.OpenAIClient')
    def test_story_generator_initialization(self, mock_openai_client):
        """Test story generator initialization"""
        from llm.get_story import StoryGenerator
        
        generator = StoryGenerator()
        assert generator is not None
        assert hasattr(generator, 'openai_client')

    @patch('llm.get_story.OpenAIClient')
    def test_get_story_success(self, mock_openai_client):
        """Test successful story generation"""
        from llm.get_story import StoryGenerator
        
        # Setup mock
        mock_client = MagicMock()
        mock_client.generate_simple_completion.return_value = "A mysterious package arrives at Sarah's door containing an old family photo. When she investigates, she discovers her grandmother had a secret twin sister. The photo leads her to uncover decades of family mysteries."
        mock_openai_client.return_value = mock_client
        
        # Test
        generator = StoryGenerator()
        result = generator.get_story(
            narrative="A mysterious package arrives",
            style="suspenseful"
        )
        
        assert result is not None
        assert isinstance(result, dict)
        assert "story" in result
        assert "narrative" in result
        assert "metadata" in result
        assert isinstance(result["story"], str)
        assert len(result["story"]) > 0

    @patch('llm.get_story.OpenAIClient')
    def test_get_story_with_additional_context(self, mock_openai_client):
        """Test story generation with additional context"""
        from llm.get_story import StoryGenerator
        
        # Setup mock
        mock_client = MagicMock()
        mock_client.generate_simple_completion.return_value = "A family drama unfolds when an old photo reveals hidden secrets."
        mock_openai_client.return_value = mock_client
        
        # Test
        generator = StoryGenerator()
        result = generator.get_story(
            narrative="An old photo is found",
            style="dramatic",
            additional_context="Focus on family relationships"
        )
        
        assert result is not None
        assert isinstance(result, dict)
        assert "story" in result
        assert result["narrative"] == "An old photo is found"

    @patch('llm.get_story.OpenAIClient') 
    def test_refine_story(self, mock_openai_client):
        """Test story refinement"""
        from llm.get_story import StoryGenerator
        
        # Setup mock
        mock_client = MagicMock()
        mock_client.generate_simple_completion.return_value = "A refined story with more suspense and better character development."
        mock_openai_client.return_value = mock_client
        
        # Test
        generator = StoryGenerator()
        result = generator.refine_story(
            original_story="A simple story about finding something.",
            refinement_request="Add more suspense and character development",
            narrative="A mysterious discovery"
        )
        
        assert result is not None
        assert isinstance(result, dict)
        assert "story" in result
        assert "original_story" in result
        assert "narrative" in result
        assert isinstance(result["story"], str)

    @patch('llm.get_story.OpenAIClient')
    def test_story_generator_error_handling(self, mock_openai_client):
        """Test story generator error handling"""
        from llm.get_story import StoryGenerator
        
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_client.generate_simple_completion.side_effect = Exception("API Error")
        mock_openai_client.return_value = mock_client
        
        # Test
        generator = StoryGenerator()
        
        with pytest.raises(Exception):
            generator.get_story("Test narrative")

    def test_story_generator_prompt_methods(self):
        """Test that prompt creation methods exist and work"""
        from llm.get_story import StoryGenerator
        
        generator = StoryGenerator.__new__(StoryGenerator)  # Create without __init__
        
        # Test system prompt creation
        system_prompt = generator._create_system_prompt("dramatic")
        assert isinstance(system_prompt, str)
        assert "dramatic" in system_prompt
        
        # Test user prompt creation  
        user_prompt = generator._create_user_prompt("test narrative", "test context")
        assert isinstance(user_prompt, str)
        assert "test narrative" in user_prompt
        assert "test context" in user_prompt


class TestStoryDataModels:
    """Unit tests for story generation data models"""
    
    def test_story_generation_request_model(self):
        """Test StoryGenerationRequest model"""
        from data.video_record import StoryGenerationRequest
        
        # Test valid request
        request = StoryGenerationRequest(
            narrative="Test narrative",
            style="dramatic",
            additional_context="Test context"
        )
        
        assert request.narrative == "Test narrative"
        assert request.style == "dramatic"
        assert request.additional_context == "Test context"
        
        # Test with optional fields
        minimal_request = StoryGenerationRequest(narrative="Test")
        assert minimal_request.narrative == "Test"
        assert minimal_request.style == "engaging"  # default value
        assert minimal_request.additional_context is None

    def test_story_variants_request_model(self):
        """Test StoryVariantsRequest model"""
        from data.video_record import StoryVariantsRequest
        
        request = StoryVariantsRequest(
            narrative="Test narrative",
            count=5,
            style="suspenseful"
        )
        
        assert request.narrative == "Test narrative"
        assert request.count == 5
        assert request.style == "suspenseful"
        
        # Test default count
        default_request = StoryVariantsRequest(narrative="Test")
        assert default_request.count == 3  # default value

    def test_story_refinement_request_model(self):
        """Test StoryRefinementRequest model"""
        from data.video_record import StoryRefinementRequest
        
        request = StoryRefinementRequest(
            original_story="Old story",
            refinement_request="Make it better",
            narrative="Test narrative"
        )
        
        assert request.original_story == "Old story"
        assert request.refinement_request == "Make it better"
        assert request.narrative == "Test narrative"

    def test_story_response_model(self):
        """Test StoryResponse model"""
        from data.video_record import StoryResponse
        
        metadata = {"word_count": 25, "character_count": 150}
        response = StoryResponse(
            story="Generated story content",
            narrative="Test narrative",
            metadata=metadata
        )
        
        assert response.story == "Generated story content"
        assert response.narrative == "Test narrative"
        assert response.metadata == metadata

    def test_model_validation(self):
        """Test model validation"""
        from data.video_record import StoryGenerationRequest, StoryVariantsRequest
        from pydantic import ValidationError
        
        # Test that empty narrative is allowed (will be caught by business logic)
        request = StoryGenerationRequest(narrative="")
        assert request.narrative == ""
        
        # Test that negative count is handled 
        request = StoryVariantsRequest(narrative="Test", count=0)
        assert request.count == 0  # Pydantic allows 0, business logic should handle this


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])
