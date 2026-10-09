from collections.abc import Awaitable, Callable
from typing import Any, AsyncContextManager, Protocol, TypeAlias


ChatMessage: TypeAlias = dict[str, Any]
ToolStatusCallback: TypeAlias = Callable[[str], Awaitable[None]]


class ChatModel(Protocol):
    async def chat_async(
        self,
        messages: list[ChatMessage],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]: ...

    async def close(self) -> None: ...


class ToolExecutor(Protocol):
    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str: ...


class ToolConnectionProvider(Protocol):
    def connection(
        self,
    ) -> AsyncContextManager[tuple[ToolExecutor, list[dict[str, Any]]]]: ...


class HistoryRepository(Protocol):
    def get_records(self) -> list[dict[str, Any]] | None: ...