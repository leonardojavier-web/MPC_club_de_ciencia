from contextlib import asynccontextmanager
from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routers.chat import router as chat_router
from backend.app.routers.foundation import router as foundation_router
from backend.history_repository import JsonHistoryRepository
from services.chat_service import ChatService
from services.contracts import ChatModel, HistoryRepository, ToolConnectionProvider
from services.llm_service import OllamaService
from services.mcp_service import MCPToolService

SERVER_SCRIPT = Path(__file__).parent / "backend" / "server.py"


def create_app(
    *,
    llm_factory: Callable[[], ChatModel] = OllamaService,
    mcp_service_factory: Callable[[str], ToolConnectionProvider] = MCPToolService,
    history_repository: HistoryRepository | None = None,
) -> FastAPI:
    repository = history_repository or JsonHistoryRepository()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        llm_service = llm_factory()
        try:
            mcp_service = mcp_service_factory(str(SERVER_SCRIPT))
            async with mcp_service.connection() as (tool_executor, tools):
                app.state.chat_service = ChatService(llm_service, tool_executor, tools)
                app.state.history_repository = repository
                yield
        finally:
            await llm_service.close()

    application = FastAPI(lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(foundation_router)
    application.include_router(chat_router)
    return application


app = create_app()