from openai import AsyncOpenAI
from api.config import settings
from .base_provider import BaseLLMProvider
import logging 


logger = logging.getLogger(__name__)

class OpenAIProvider(BaseLLMProvider):
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPEN_API_KEY)
    
    async def clean_text(self, text):
        try:
            response = await self.client.chat.completions.create(
                
                model=settings.OPENAI_MODEL,
                message = [
                    {
                        "role": "system",
                        "content": (
                            "You are M3LO , you specialise in cleaning up OCR extracted text."
                            "Correct spelling errors, caused by OCR misreads, and format the text in a structured way. Do not invent any information that is not present in the text. Focus on accuracy and clarity."
                            "Make sure you preserve all the original information, but correct any mistakes and format it nicely. Output should be in a clear, structured format that is easy to read."
                            "Return only the cleaned text, without any explanations or additional commentary."
                        ),
                        
                    },
                    {
                        "role": "user", "content": text
                    },
                    
                ],
                temperature=0.0,
                timeout=30
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error in OpenAIProvider.clean_text: {str(e)}")
            raise ValueError(f"Failed to clean text: {str(e)}")