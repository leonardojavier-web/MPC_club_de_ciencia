from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/api/chat")
async def post_chat(request: ChatRequest, http_request: Request):
    user_message = request.message.strip()
    if not user_message:
        raise HTTPException(status_code=422, detail="El mensaje no puede estar vacío.")

    chat_service = http_request.app.state.chat_service
    messages = chat_service.new_conversation()
    try:
        reply = await chat_service.respond(messages, user_message)
        return {"response": reply}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    chat_service = websocket.app.state.chat_service
    messages = chat_service.new_conversation()

    try:
        await websocket.send_json({
            "type": "ready",
            "message": "Servicios MCP y Ollama conectados",
        })

        async def send_tool_status(tool_name: str) -> None:
            await websocket.send_json({
                "type": "status",
                "message": f"🔍 Consultando archivo histórico ({tool_name})...",
            })

        while True:
            user_message = await websocket.receive_text()
            try:
                reply = await chat_service.respond(messages, user_message, send_tool_status)
                await websocket.send_json({"type": "response", "content": reply})
            except Exception as exc:
                await websocket.send_json({"type": "error", "message": str(exc)})
    except WebSocketDisconnect:
        return