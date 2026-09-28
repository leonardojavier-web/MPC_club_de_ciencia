import os
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from services.llm_service import OllamaService
from services.mcp_service import MCPToolService

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_SCRIPT = os.path.join(BASE_DIR, "backend", "server.py")
llm_service = OllamaService()
mcp_service = MCPToolService(SERVER_SCRIPT)

SYSTEM_PROMPT = """
Eres el Asistente Historiador de Las Varillas. 
OBLIGATORIEDAD: Para CUALQUIER pregunta relacionada con la historia, fundación, documentos o datos de Las Varillas, DEBES utilizar la herramienta MCP disponible. 
Responde de forma amable, clara y narrativamente atractiva basándote estrictamente en los resultados de la herramienta.
"""

@app.get("/api/fundacion")
async def get_fundacion():
    json_path = os.path.join(BASE_DIR, "backend", "fundacion.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"error": "Archivo no encontrado"}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        async with mcp_service.connection() as (session, ollama_tools):
            await websocket.send_json({
                "type": "ready",
                "message": "Servicios MCP y Ollama conectados",
            })
            messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]

            while True:
                data = await websocket.receive_text()
                messages.append({'role': 'user', 'content': data})

                try:
                    response = await llm_service.chat_async(messages, ollama_tools)
                    message = response['message']

                    if message.get('tool_calls'):
                        for tool_call in message['tool_calls']:
                            tool_name = tool_call['function']['name']
                            tool_args = tool_call['function']['arguments']

                            await websocket.send_json({
                                "type": "status",
                                "message": f"🔍 Consultando archivo histórico ({tool_name})..."
                            })

                            result = await session.call_tool(tool_name, tool_args)
                            tool_content = mcp_service.content_as_text(result)

                            messages.append(message)
                            messages.append({
                                'role': 'tool',
                                'content': tool_content
                            })

                        final_response = await llm_service.chat_async(messages)
                        bot_reply = final_response['message']['content']
                        messages.append({'role': 'assistant', 'content': bot_reply})
                        await websocket.send_json({
                            "type": "response",
                            "content": bot_reply
                        })
                    else:
                        bot_reply = message['content']
                        messages.append({'role': 'assistant', 'content': bot_reply})
                        await websocket.send_json({
                            "type": "response",
                            "content": bot_reply
                        })

                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })

    except WebSocketDisconnect:
        print("🔌 Cliente desconectado")
    except Exception as e:
        print(f"Error en servidor MCP: {e}")