import asyncio

import ollama


class OllamaService:
    """Cliente asíncrono para el modelo local de Ollama."""

    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name

    async def is_available(self):
        try:
            await asyncio.to_thread(ollama.list)
            return True
        except Exception:
            return False

    async def chat_async(self, messages, tools=None):
        return await asyncio.to_thread(
            ollama.chat,
            model=self.model_name,
            messages=messages,
            tools=tools,
            options={
                "num_ctx": 1536,
                "num_predict": 140,
            },
            keep_alive="30m",
        )