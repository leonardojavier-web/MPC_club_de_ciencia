import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPToolService:
    """Administra la sesión MCP y adapta sus herramientas al formato de Ollama."""

    def __init__(self, server_script_path: str):
        self.server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script_path],
            env=None,
        )

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[tuple[ClientSession, list[dict]]]:
        """Abre una sesión MCP y la mantiene viva durante el WebSocket."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                yield session, self._format_tools(tools.tools)

    @staticmethod
    def _format_tools(tools) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in tools
        ]

    @staticmethod
    def content_as_text(result) -> str:
        return str(result.content[0].text) if result.content else ""