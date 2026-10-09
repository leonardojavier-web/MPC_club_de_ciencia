from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/api/fundacion")
async def get_fundacion(request: Request):
    records = request.app.state.history_repository.get_records()
    if records is None:
        return {"error": "Archivo no encontrado"}
    return records