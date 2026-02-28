
from api.services.providers.gemini_provider import GeminiProvider

class LLMService:
    def __init__(self):
        self.provider = GeminiProvider()
    
    async def clean_text(self, text: str) -> str:
        return await self.provider.clean_text(text)