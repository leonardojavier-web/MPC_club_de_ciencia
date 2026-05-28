import json
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("HistoriaVarillas")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FUNDACION_FILE = os.path.join(BASE_DIR, "fundacion.json")


@mcp.tool()
def consultar_fundacion_las_varillas() -> str:
    """
    Devuelve toda la información histórica de Las Varillas.
    """
    with open(FUNDACION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def buscar_debates_origen(consulta) -> str:
    """
    Búsqueda inteligente + modo narrador (PRO FINAL)
    Devuelve explicación histórica en texto humano.
    """

    with open(FUNDACION_FILE, "r", encoding="utf-8") as f:
        debates = json.load(f)

    # ----------------------------
    # NORMALIZAR CONSULTA (FIX OLLAMA)
    # ----------------------------
    if isinstance(consulta, dict):

        if "default" in consulta:
            consulta = consulta["default"]

        elif "value" in consulta:
            consulta = consulta["value"]

        elif "object" in consulta:
            consulta = consulta["object"]

        elif "content" in consulta:
            consulta = consulta["content"]

        else:
            consulta = str(consulta)

    consulta = str(consulta).lower().strip()
    palabras = consulta.split()

    resultados = []

    # ----------------------------
    # BUSQUEDA INTELIGENTE
    # ----------------------------
    if isinstance(debates, list):

        for item in debates:

            texto = (
                str(item.get("titulo", "")) + " " +
                str(item.get("contenido", "")) + " " +
                " ".join(item.get("tags", [])) + " " +
                str(item.get("metadata", {}).get("criterio", ""))
            ).lower()

            score = 0

            # coincidencia por palabras
            for palabra in palabras:
                if palabra in texto:
                    score += 2

            # coincidencia fuerte
            if consulta in texto:
                score += 5

            # bonus por tags
            for tag in item.get("tags", []):
                if tag.lower() in consulta:
                    score += 3

            if score > 0:
                resultados.append((score, item))

    elif isinstance(debates, dict):

        texto = json.dumps(debates, ensure_ascii=False).lower()

        if consulta in texto:
            resultados.append((10, debates))

    # ----------------------------
    # SIN RESULTADOS
    # ----------------------------
    if not resultados:
        return "No se encontraron resultados sobre el tema consultado."

    # ----------------------------
    # MEJOR RESULTADO
    # ----------------------------
    resultados.sort(key=lambda x: x[0], reverse=True)

    score, item = resultados[0]

    titulo = item.get("titulo", "Sin título")
    contenido = item.get("contenido", "")
    tags = item.get("tags", [])
    criterio = item.get("metadata", {}).get("criterio", "no especificado")

    # ----------------------------
    # MODO NARRADOR FINAL
    # ----------------------------
    narracion = f"""
📜 RELATO HISTÓRICO

A partir del análisis de las fuentes disponibles sobre el origen de Las Varillas, la interpretación más relevante encontrada en los registros es la siguiente:

📌 {titulo}

{contenido}

Esta postura se enmarca dentro del criterio historiográfico: {criterio}.

Los conceptos relacionados con este enfoque incluyen: {", ".join(tags)}.

Según el análisis de coincidencias en las fuentes, esta interpretación obtuvo un nivel de relevancia de {score} puntos, lo que la posiciona como una de las respuestas más sólidas dentro del debate histórico sobre el origen de la ciudad.

📖 CONCLUSIÓN:
El origen de Las Varillas no puede reducirse a una única fecha, sino que forma parte de un proceso histórico complejo donde conviven distintas interpretaciones (demográfica, jurídica y económica), todas con fundamentos válidos dentro del análisis historiográfico.
""".strip()

    return narracion


if __name__ == "__main__":
    mcp.run()