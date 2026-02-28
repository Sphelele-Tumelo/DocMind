from google import genai
from api.config import settings
from api.services.providers.base_provider import BaseLLMProvider
import logging 

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL
        self.system_prompt = (
            "You are M3LO, you specialise in cleaning up OCR extracted text. "
            "Correct spelling errors, caused by OCR misreads, and format the text in a structured way. "
            "Do not invent any information that is not present in the text. Focus on accuracy and clarity. "
            "Make sure you preserve all the original information, but correct any mistakes and format it nicely. "
            "Output should be in a clear, structured format that is easy to read. "
            "Return only the cleaned text, without any explanations or additional commentary."
        )
    
    async def clean_text(self, text: str) -> str:
        try:
            prompt = self.system_prompt + "\n\n" + text
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error in GeminiProvider.clean_text: {str(e)}")
            raise ValueError(f"Failed to clean text: {str(e)}")