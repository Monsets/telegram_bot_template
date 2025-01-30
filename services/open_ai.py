from openai import AsyncOpenAI
from config.config import Config
from database.models import ChatHistory
from typing import List
import logging

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
    
    def create_messages_from_history(self, history: List[ChatHistory]) -> List[dict]:
        """Convert chat history to OpenAI messages format"""
        messages = [{"role": "system", "content": Config.SYSTEM_MESSAGE}]
        
        for entry in history:
            messages.append({
                "role": entry.role,
                "content": entry.content
            })
        
        return messages
    
    async def get_response(self, messages: List[dict]) -> str:
        """Get response from OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return f"Error getting OpenAI response: {str(e)}"
