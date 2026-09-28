from mcp.server.fastmcp import FastMCP
import json
import os

# Inicializar FastMCP
mcp = FastMCP("Historial Las Varillas")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "fundacion.json")

@mcp.tool()
def consultar_fundacion_las_varillas() -> str:
    """Consulta los registros históricos oficiales sobre la fundación de Las Varillas."""
    if not os.path.exists(JSON_PATH):
        return "El archivo de registros de fundación no está disponible."
    
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error al leer los datos históricos: {str(e)}"

if __name__ == "__main__":
    mcp.run()