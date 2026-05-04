import json
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("HistoriaVarillas")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "fundacion.json")

@mcp.tool()
def consultar_fundacion_las_varillas() -> str:
    """Devuelve información histórica sobre la fundación de Las Varillas. Úsala para responder cualquier pregunta sobre la historia, fundación o ferrocarril de Las Varillas."""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return json.dumps(data, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run()
    