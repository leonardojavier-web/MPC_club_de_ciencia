import os
import json
import re
import unicodedata
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
Para cualquier pregunta relacionada con la historia, fundación, documentos o datos de Las Varillas, utiliza el resultado MCP consultado para esta respuesta.
Responde de forma amable, clara y narrativamente atractiva basándote estrictamente en los resultados de la herramienta.
Desarrolla las respuestas con claridad y contexto suficiente, normalmente en 3 o 4 oraciones y unas 50 a 75 palabras. En preguntas sencillas, responde de forma más directa; evita extenderte o repetir ideas y agrega más detalle solo si el usuario lo pide.
No mezcles datos de documentos distintos ni atribuyas a una postura la evidencia de otra. Si las fuentes se contradicen, explica la discrepancia sin resolverla por tu cuenta. En el debate sobre el origen, distingue 1900 (presencia poblacional previa y referencia simbólica), 1903 (donación de tierras y organización del poblado) y 1904 (llegada y funcionamiento del ferrocarril). Una ficha inicial menciona el ferrocarril junto a 1900; preséntala como una afirmación separada que contradice la postura detallada sobre 1904. No inventes detalles para reconciliarlas.
"""

STOP_WORDS = {
    "las", "los", "una", "uno", "unos", "unas", "del", "por", "para",
    "con", "como", "que", "cual", "cuando", "donde", "sobre", "entre",
    "desde", "hasta", "esta", "este", "esto", "tiene", "fue", "son",
    "hay", "era", "sus", "historia", "varillas", "importancia", "importa",
    "explica", "explicar", "pueblo", "poblado", "ciudad", "formar",
}


def _search_terms(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFD", text.lower())
    unaccented = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    terms = set()
    for term in re.findall(r"[a-z0-9]+", unaccented):
        if term.endswith("es") and len(term) > 6:
            term = term[:-2]
        elif term.endswith("s") and len(term) > 4:
            term = term[:-1]
        if len(term) > 2 and term not in STOP_WORDS:
            terms.add(term)
    return terms


def _relevant_mcp_content(tool_content: str, question: str) -> str:
    try:
        records = json.loads(tool_content)
    except json.JSONDecodeError:
        return tool_content

    if not isinstance(records, list) or not records:
        return tool_content

    question_terms = _search_terms(question)
    ranked_records = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        title_and_tags = " ".join(
            str(record.get(field, ""))
            for field in ("titulo", "documento", "tags")
        )
        searchable_content = " ".join(
            str(record.get(field, ""))
            for field in ("contenido", "texto")
        )
        score = (
            5 * len(question_terms & _search_terms(title_and_tags))
            + len(question_terms & _search_terms(searchable_content))
        )
        ranked_records.append((score, index, record))

    if not ranked_records:
        return tool_content

    ranked_records.sort(key=lambda item: (-item[0], item[1]))
    if (
        ranked_records[0][0] >= 12
        and (len(ranked_records) == 1 or ranked_records[0][0] - ranked_records[1][0] >= 5)
    ):
        relevant_records = [ranked_records[0][2]]
    else:
        relevant_records = [
            record for score, _, record in ranked_records[:4] if score > 0
        ]
    if not relevant_records:
        relevant_records = [record for _, _, record in ranked_records[:4]]

    compact_records = [
        {
            field: record[field]
            for field in ("titulo", "documento", "contenido", "texto", "autor")
            if field in record
        }
        for record in relevant_records
    ]
    return json.dumps(compact_records, ensure_ascii=False, indent=2)


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
            ollama_available = await llm_service.is_available()
            await websocket.send_json({
                "type": "ready",
                "mcpAvailable": True,
                "ollamaAvailable": ollama_available,
            })
            messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
            historical_tool = next(
                (
                    tool for tool in ollama_tools
                    if tool['function']['name'] == 'consultar_fundacion_las_varillas'
                ),
                None,
            )
            if historical_tool is None:
                raise RuntimeError("No se encontró la herramienta MCP de consulta histórica.")

            while True:
                data = await websocket.receive_text()
                if not ollama_available:
                    await websocket.send_json({
                        "type": "error",
                        "message": "El archivo histórico está disponible, pero Ollama no está iniciado. Inicia Ollama con el modelo llama3.2 para usar el chat.",
                    })
                    continue
                messages = [messages[0], *messages[1:][-4:]]
                messages.append({'role': 'user', 'content': data})

                try:
                    await websocket.send_json({
                        "type": "status",
                        "message": "🔍 Consultando archivo histórico..."
                    })

                    result = await session.call_tool(
                        historical_tool['function']['name'],
                        {},
                    )
                    tool_content = _relevant_mcp_content(
                        mcp_service.content_as_text(result),
                        data,
                    )
                    request_messages = [
                        {
                            'role': 'system',
                            'content': (
                                f"{SYSTEM_PROMPT}\n\n"
                                "Resultado de la consulta MCP para esta respuesta:\n"
                                f"{tool_content}"
                            ),
                        },
                        *messages[1:],
                    ]
                    response = await llm_service.chat_async(request_messages)
                    bot_reply = response['message']['content']
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