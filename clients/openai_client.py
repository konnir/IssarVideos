"""
OpenAI API client for handling GPT-4 interactions.
Provides a generic client interface for OpenAI API calls.
"""

import os
from typing import Optional, Dict, Any, List
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Generic OpenAI client for GPT-4 interactions."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key. If None, will use OPENAI_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        self.client = OpenAI(api_key=self.api_key)

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        **kwargs,
    ) -> str:
        """
        Generate a completion using OpenAI's chat API.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: OpenAI model to use (default: gpt-4o)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            presence_penalty: Presence penalty (-2.0 to 2.0)
            **kwargs: Additional parameters for the API call

        Returns:
            Generated text response

        Raises:
            Exception: If API call fails
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                **kwargs,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise Exception(f"Failed to generate completion: {str(e)}")

    def generate_simple_completion(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> str:
        """
        Generate a simple completion with a user prompt and optional system prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt to set context
            **kwargs: Additional parameters for generate_completion

        Returns:
            Generated text response
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        return self.generate_completion(messages, **kwargs)

    def validate_connection(self) -> bool:
        """
        Validate the OpenAI API connection.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Simple test call
            self.generate_simple_completion("Say 'Hello'", max_tokens=10)
            return True
        except Exception as e:
            logger.error(f"OpenAI connection validation failed: {str(e)}")
            return False
