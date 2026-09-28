import asyncio

import ollama


class OllamaService:
    """Cliente asíncrono para el modelo local de Ollama."""

    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name

    async def chat_async(self, messages, tools=None):
        return await asyncio.to_thread(
            ollama.chat,
            model=self.model_name,
            messages=messages,
            tools=tools,
        )