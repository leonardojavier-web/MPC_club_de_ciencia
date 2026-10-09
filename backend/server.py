from mcp.server.fastmcp import FastMCP
import json

if __package__:
    from backend.history_repository import JsonHistoryRepository
else:
    from history_repository import JsonHistoryRepository

# Inicializar FastMCP
mcp = FastMCP("Historial Las Varillas")

history_repository = JsonHistoryRepository()

@mcp.tool()
def consultar_fundacion_las_varillas() -> str:
    """Consulta los registros históricos oficiales sobre la fundación de Las Varillas."""
    try:
        data = history_repository.get_records()
        if data is None:
            return "El archivo de registros de fundación no está disponible."
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error al leer los datos históricos: {str(e)}"

if __name__ == "__main__":
    mcp.run()