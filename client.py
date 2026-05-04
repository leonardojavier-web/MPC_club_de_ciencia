import asyncio
import requests
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2"

PYTHON_PATH = r".\venv\Scripts\python.exe"
SERVER_SCRIPT = r"server.py"

SYSTEM_PROMPT = """Sos un asistente experto en la historia de Las Varillas, Argentina.
REGLAS ESTRICTAS:
1. SIEMPRE usá la herramienta 'consultar_fundacion_las_varillas' antes de responder cualquier pregunta.
2. Respondé ÚNICAMENTE con la información que devuelve la herramienta. No agregues nada más.
3. Si la herramienta no tiene información sobre algo, decí exactamente: 'No tengo información sobre eso en mis datos locales.'
4. NUNCA inventes ni agregues información que no venga de la herramienta."""

async def chat_loop():
    server_params = StdioServerParameters(
        command=PYTHON_PATH,
        args=[SERVER_SCRIPT]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.inputSchema
                    }
                }
                for t in tools_result.tools
            ]

            print("✅ Conectado a HistoriaVarillas. Escribí 'salir' para terminar.\n")

            while True:
                pregunta = input("Vos: ").strip()
                if pregunta.lower() == "salir":
                    print("¡Hasta luego!")
                    break
                if not pregunta:
                    continue

                # Cada pregunta empieza con el system prompt fresco
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": pregunta}
                ]

                try:
                    while True:
                        print("⏳ Pensando...")
                        response = requests.post(OLLAMA_URL, json={
                            "model": MODEL,
                            "messages": messages,
                            "tools": tools,
                            "stream": False
                        }, timeout=120)

                        msg = response.json()["message"]
                        messages.append(msg)

                        if msg.get("tool_calls"):
                            for call in msg["tool_calls"]:
                                nombre = call["function"]["name"]
                                args = call["function"].get("arguments", {})
                                print(f"🔧 Usando herramienta: {nombre}")
                                resultado = await session.call_tool(nombre, args)
                                messages.append({
                                    "role": "tool",
                                    "content": resultado.content[0].text
                                })
                        else:
                            print(f"\nIA: {msg['content']}\n")
                            break

                except Exception as e:
                    print(f"❌ Error: {e}\n")

asyncio.run(chat_loop())