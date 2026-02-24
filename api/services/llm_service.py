from api.services.providers.openai_provider import OpenAIProvider

class LLMService:
    def __init__(self):
        self.provider = OpenAIProvider()
    
    async def clean_text(self, text: str) -> str:
        return await self.provider.clean_text(text)