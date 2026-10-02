import asyncio
import ollama

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


MODEL = "llama3.2"

PYTHON_PATH = r".\venv\Scripts\python.exe"
SERVER_SCRIPT = r"server.py"


SYSTEM_PROMPT = """
Sos un asistente histórico de Las Varillas.

REGLAS OBLIGATORIAS:

1. Nunca inventes información.
2. Nunca combines datos de herramientas distintas.
3. Respondé SOLAMENTE usando el contenido exacto devuelto por la herramienta.
4. No resumas.
5. No interpretes.
6. No completes información faltante.
7. Si una herramienta devuelve un JSON, explicá únicamente lo que aparece en ese JSON.
8. Si aparece un nombre de persona, no lo conviertas en un evento histórico.
9. Si no hay información suficiente, decí:
'No tengo información suficiente en los datos locales.'

Tu trabajo es actuar como un buscador documental, no como un historiador que interpreta.
"""


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

                messages = [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": pregunta
                    }
                ]

                try:

                    while True:

                        print("⏳ Pensando...")

                        response = ollama.chat(
                            model=MODEL,
                            messages=messages,
                            tools=tools
                        )

                        print("\n📦 RESPUESTA OLLAMA:")
                        print(response)

                        message = response["message"]

                        # Guardar mensaje del modelo
                        messages.append(message)

                        # --------------------------------
                        # SI EL MODELO QUIERE USAR TOOLS
                        # --------------------------------

                        if message.get("tool_calls"):

                            for tool_call in message["tool_calls"]:

                                function_name = tool_call["function"]["name"]

                                arguments = tool_call["function"].get(
                                    "arguments",
                                    {}
                                )

                                print(f"\n🔧 Ejecutando tool: {function_name}")
                                print("📥 Argumentos originales:", arguments)

                                # --------------------------------
                                # NORMALIZAR ARGUMENTOS
                                # --------------------------------

                                if not isinstance(arguments, dict):
                                    arguments = {}

                                # Compatibilidad formatos raros
                                if "key" in arguments:
                                    arguments["consulta"] = arguments["key"]

                                if "query" in arguments:
                                    arguments["consulta"] = arguments["query"]

                                # --------------------------------
                                # NORMALIZAR CONSULTA
                                # --------------------------------

                                if "consulta" in arguments:

                                    consulta = arguments["consulta"]

                                    # Si viene como dict raro
                                    if isinstance(consulta, dict):

                                        # Caso:
                                        # {"value":"texto"}

                                        if "value" in consulta:
                                            consulta = consulta["value"]

                                        # Caso:
                                        # {"object":"texto"}

                                        elif "object" in consulta:
                                            consulta = consulta["object"]

                                        # Caso:
                                        # {"content":"texto"}

                                        elif "content" in consulta:
                                            consulta = consulta["content"]

                                        else:
                                            consulta = str(consulta)

                                    consulta = str(consulta).strip()

                                    # Si viene vacío
                                    if (
                                        consulta == ""
                                        or consulta == "{'type': 'string'}"
                                        or consulta == '{"type":"string"}'
                                    ):
                                        consulta = pregunta

                                    arguments["consulta"] = consulta

                                print("📦 Argumentos normalizados:", arguments)

                                try:

                                    # Ejecutar tool MCP
                                    result = await session.call_tool(
                                        function_name,
                                        arguments
                                    )

                                    print("\n📄 RESULTADO TOOL:")
                                    print(result)

                                    texto_resultado = ""

                                    # Obtener texto resultado
                                    if hasattr(result, "content"):

                                        if (
                                            result.content
                                            and len(result.content) > 0
                                        ):
                                            texto_resultado = (
                                                result.content[0].text
                                            )

                                    print("\n📚 TEXTO RESULTADO:")
                                    print(texto_resultado)

                                    # Agregar resultado al contexto
                                    messages.append({
                                        "role": "tool",
                                        "content": texto_resultado
                                    })

                                except Exception as e:

                                    print(f"\n❌ Error ejecutando tool: {e}")

                        # --------------------------------
                        # RESPUESTA FINAL DEL MODELO
                        # --------------------------------

                        else:

                            print(f"\n🤖 IA:\n{message['content']}\n")
                            break

                except Exception as e:

                    print(f"\n❌ Error general: {e}\n")


asyncio.run(chat_loop())