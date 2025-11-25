"""
Gemini AI service for LLM interactions.
"""
import google.generativeai as genai
from typing import Optional, Dict, Any
import json

from utils.config import settings
from utils.logging import logger


class GeminiService:
    """Service for interacting with Google Gemini AI."""
    
    def __init__(self):
        """Initialize Gemini service."""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
        logger.info("Gemini service initialized")
    
    async def generate_text(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text using Gemini.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        try:
            generation_config = {
                "temperature": temperature or settings.LLM_TEMPERATURE,
            }
            
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini generation error: {str(e)}")
            raise
    
    async def generate_json(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Generate structured JSON using Gemini.
        
        Args:
            prompt: Input prompt
            schema: JSON schema for validation
            temperature: Sampling temperature
            
        Returns:
            Parsed JSON response
        """
        try:
            # Add JSON formatting instruction to prompt
            json_prompt = f"{prompt}\n\nRespond with valid JSON only."
            
            if schema:
                json_prompt += f"\n\nFollow this schema:\n{json.dumps(schema, indent=2)}"
            
            response_text = await self.generate_text(json_prompt, temperature)
            
            # Extract JSON from response (handle markdown code blocks)
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Gemini JSON generation error: {str(e)}")
            raise


# Global Gemini service instance
gemini_service = GeminiService()
