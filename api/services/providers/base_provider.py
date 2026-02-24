from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    @abstractmethod
    async def clean_text(self, text: str) -> str:
        pass