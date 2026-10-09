import json
import tempfile
import unittest
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from fastapi.testclient import TestClient

from backend.history_repository import JsonHistoryRepository
from client import create_app
from services.chat_service import ChatService
from services.mcp_service import MCPToolExecutor, MCPToolService


def model_response(content, tool_calls=None):
    message = {"role": "assistant", "content": content}
    if tool_calls is not None:
        message["tool_calls"] = tool_calls
    return {"message": message}


class FakeChatModel:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.closed = False

    async def chat_async(self, messages, tools=None):
        self.calls.append((list(messages), tools))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    async def close(self):
        self.closed = True


class FakeToolExecutor:
    def __init__(self, results=None, error=None):
        self.results = results or {}
        self.error = error
        self.calls = []

    async def call_tool(self, tool_name, arguments):
        self.calls.append((tool_name, arguments))
        if self.error:
            raise self.error
        return self.results.get(tool_name, "resultado")


class FakeMCPService:
    def __init__(self, tool_executor):
        self.tool_executor = tool_executor

    @asynccontextmanager
    async def connection(self):
        yield self.tool_executor, [{"type": "function", "function": {"name": "buscar"}}]


class ChatServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_replies_without_tools(self):
        model = FakeChatModel([model_response("Respuesta directa")])
        executor = FakeToolExecutor()
        service = ChatService(model, executor, [])
        messages = service.new_conversation()

        reply = await service.respond(messages, "Hola")

        self.assertEqual(reply, "Respuesta directa")
        self.assertEqual(executor.calls, [])
        self.assertEqual(messages[-1], {"role": "assistant", "content": "Respuesta directa"})

    async def test_runs_multiple_tools_and_reports_status(self):
        calls = [
            {"function": {"name": "buscar_a", "arguments": '{"consulta": "A"}'}},
            {"function": {"name": "buscar_b", "arguments": {"consulta": "B"}}},
        ]
        model = FakeChatModel([model_response(None, calls), model_response("Respuesta final")])
        executor = FakeToolExecutor({"buscar_a": "dato A", "buscar_b": "dato B"})
        service = ChatService(model, executor, [{"name": "buscar"}])
        messages = service.new_conversation()
        statuses = []

        async def on_status(name):
            statuses.append(name)

        reply = await service.respond(messages, "Busca ambos", on_status)

        self.assertEqual(reply, "Respuesta final")
        self.assertEqual(executor.calls, [
            ("buscar_a", {"consulta": "A"}),
            ("buscar_b", {"consulta": "B"}),
        ])
        self.assertEqual(statuses, ["buscar_a", "buscar_b"])
        self.assertEqual([message["content"] for message in messages if message["role"] == "tool"], ["dato A", "dato B"])

    async def test_runs_a_single_tool(self):
        calls = [{"function": {"name": "buscar", "arguments": {"consulta": "1903"}}}]
        model = FakeChatModel([model_response(None, calls), model_response("Dato encontrado")])
        executor = FakeToolExecutor({"buscar": "Acta de 1903"})
        service = ChatService(model, executor, [{"name": "buscar"}])

        reply = await service.respond(service.new_conversation(), "Busca 1903")

        self.assertEqual(reply, "Dato encontrado")
        self.assertEqual(executor.calls, [("buscar", {"consulta": "1903"})])

    async def test_propagates_tool_integration_error(self):
        model = FakeChatModel([model_response(None, [{"function": {"name": "buscar", "arguments": {}}}])])
        executor = FakeToolExecutor(error=RuntimeError("MCP no disponible"))
        service = ChatService(model, executor, [])

        with self.assertRaisesRegex(RuntimeError, "MCP no disponible"):
            await service.respond(service.new_conversation(), "Consulta")


class RepositoryTests(unittest.TestCase):
    def test_reads_json_records_from_configured_path(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "records.json"
            file_path.write_text(json.dumps([{"titulo": "Historia"}]), encoding="utf-8")

            repository = JsonHistoryRepository(file_path)

            self.assertEqual(repository.get_records(), [{"titulo": "Historia"}])


class MCPAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_executor_maps_session_result_to_text_contract(self):
        session = Mock()
        session.call_tool = AsyncMock(return_value=SimpleNamespace(
            content=[SimpleNamespace(text="Acta histórica")],
        ))
        executor = MCPToolExecutor(session)

        result = await executor.call_tool("consultar", {"tema": "fundación"})

        self.assertEqual(result, "Acta histórica")
        session.call_tool.assert_awaited_once_with("consultar", {"tema": "fundación"})

    def test_formats_announced_tools_without_name_specific_logic(self):
        tool = SimpleNamespace(
            name="buscar_documento",
            description="Busca un documento histórico",
            inputSchema={"type": "object", "properties": {"consulta": {"type": "string"}}},
        )

        result = MCPToolService._format_tools([tool])

        self.assertEqual(result[0]["function"]["name"], "buscar_documento")
        self.assertEqual(result[0]["function"]["parameters"], tool.inputSchema)


class ApplicationTests(unittest.TestCase):
    def test_http_chat_uses_injected_providers(self):
        model = FakeChatModel([model_response("Hola desde el doble")])
        executor = FakeToolExecutor()
        app = create_app(
            llm_factory=lambda: model,
            mcp_service_factory=lambda _path: FakeMCPService(executor),
            history_repository=JsonHistoryRepository(Path(__file__).parent / "missing.json"),
        )

        with TestClient(app) as client:
            response = client.post("/api/chat", json={"message": "Hola"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"response": "Hola desde el doble"})
        self.assertTrue(model.closed)

    def test_http_chat_rejects_blank_messages(self):
        model = FakeChatModel([])
        app = create_app(
            llm_factory=lambda: model,
            mcp_service_factory=lambda _path: FakeMCPService(FakeToolExecutor()),
        )

        with TestClient(app) as client:
            response = client.post("/api/chat", json={"message": "   "})

        self.assertEqual(response.status_code, 422)
        self.assertEqual(model.calls, [])


if __name__ == "__main__":
    unittest.main()