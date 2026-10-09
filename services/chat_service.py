import json
from typing import Any

from services.contracts import ChatMessage, ChatModel, ToolExecutor, ToolStatusCallback


SYSTEM_PROMPT = """
Eres el Asistente Historiador de Las Varillas.
OBLIGATORIEDAD: Para CUALQUIER pregunta relacionada con la historia, fundación, documentos o datos de Las Varillas, DEBES utilizar la herramienta MCP disponible.
Responde de forma amable, clara y narrativamente atractiva basándote estrictamente en los resultados de la herramienta.
""".strip()


class ChatService:
    """Coordina una conversación sin depender del transporte ni del proveedor concreto."""

    def __init__(
        self,
        chat_model: ChatModel,
        tool_executor: ToolExecutor,
        tools: list[dict[str, Any]],
    ) -> None:
        self._chat_model = chat_model
        self._tool_executor = tool_executor
        self._tools = tools

    def new_conversation(self) -> list[ChatMessage]:
        return [{"role": "system", "content": SYSTEM_PROMPT}]

    async def respond(
        self,
        messages: list[ChatMessage],
        user_message: str,
        status_callback: ToolStatusCallback | None = None,
    ) -> str:
        messages.append({"role": "user", "content": user_message})
        response = await self._chat_model.chat_async(messages, self._tools)
        message = response["message"]
        tool_calls = message.get("tool_calls") or []

        if tool_calls:
            messages.append(message)
            for tool_call in tool_calls:
                function = tool_call["function"]
                tool_name = function["name"]
                arguments = function.get("arguments", {})
                if isinstance(arguments, str):
                    arguments = json.loads(arguments)
                if not isinstance(arguments, dict):
                    raise TypeError("Los argumentos de la herramienta deben ser un objeto JSON.")
                if status_callback is not None:
                    await status_callback(tool_name)

                result = await self._tool_executor.call_tool(tool_name, arguments)
                messages.append({"role": "tool", "content": result})

            final_response = await self._chat_model.chat_async(messages)
            reply = final_response["message"]["content"]
        else:
            reply = message["content"]

        messages.append({"role": "assistant", "content": reply})
        return reply