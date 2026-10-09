import ollama


class OllamaService:
    """Cliente asíncrono para el modelo local de Ollama."""

    def __init__(self, model_name: str = "llama3.2") -> None:
        self.model_name = model_name
        self.client = ollama.AsyncClient()

    async def chat_async(self, messages, tools=None):
        return await self.client.chat(
            model=self.model_name,
            messages=messages,
            tools=tools,
        )

    async def close(self):
        await self.client.close()