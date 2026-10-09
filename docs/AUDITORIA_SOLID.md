# Auditoría SOLID - Backend

**Proyecto:** Historia MCP - Las Varillas
**Fecha:** 2026-10-09
**Tipo de revisión:** inspección estática del código disponible

## Resumen ejecutivo

La orquestación está en un servicio de aplicación, las rutas son adaptadores, el acceso histórico comparte un repositorio y las implementaciones externas se inyectan desde la composición de FastAPI. La auditoría del frontend está en [AUDITORIA_FRONTEND.md](AUDITORIA_FRONTEND.md).

| Principio | Evaluación | Lectura breve |
|---|---|---|
| SRP - Responsabilidad única | Aplicado | Chat, transporte, persistencia y vistas tienen módulos identificables. |
| OCP - Abierto/cerrado | Parcial | Las dependencias se pueden reemplazar tras contratos existentes; nuevos comportamientos que cambien esos contratos sí requieren editar el servicio. |
| LSP - Sustitución de Liskov | Parcial / sin herencia | Los dobles sustituyen a las implementaciones en pruebas; no hay jerarquías de clases propias que evaluar. |
| ISP - Segregación de interfaces | Aplicado | Los contratos separan modelo de chat, ejecución de herramientas, conexión MCP y consulta histórica. |
| DIP - Inversión de dependencias | Aplicado en la composición | `create_app()` recibe fábricas y repositorio; el servicio de chat consume protocolos, no los SDK concretos. |

## Devolución: qué se arregló

| Hallazgo inicial | Cambio aplicado | Dónde encontrarlo |
|---|---|---|
| La coordinación del chat mezclaba proveedor LLM, llamadas MCP y transporte. | Se extrajo `ChatService`; HTTP y WebSocket delegan en él. | `services/chat_service.py`, `backend/app/routers/chat.py` |
| La aplicación creaba integraciones como globales y no permitía sustituirlas con facilidad. | Se añadió `create_app()` con fábricas para LLM/MCP y repositorio inyectable. | `client.py` |
| API y herramienta MCP abrían el JSON desde sus propias rutas. | Ambos consultan el mismo repositorio JSON. | `backend/history_repository.py`, `backend/app/routers/foundation.py`, `backend/server.py` |
| No había pruebas focalizadas para flujos de chat ni sustitución de dependencias. | Se añadieron nueve pruebas unitarias, de integración HTTP y del adaptador MCP usando dobles. | `tests/test_chat_service.py` |

## Hallazgos por principio

### S - Responsabilidad única (SRP): aplicado

`services/chat_service.py` coordina conversación y uso de herramientas. `backend/app/routers/chat.py` y `foundation.py` adaptan HTTP/WebSocket y consulta histórica; `backend/history_repository.py` concentra lectura JSON. Cada módulo mantiene un motivo principal para cambiar.

### O - Abierto/cerrado (OCP): parcial

`MCPToolService._format_tools()` adapta cualquier lista de herramientas sin ramas por nombre. Las fábricas de `create_app()` permiten añadir implementaciones de modelo y conexión MCP respetando `services/contracts.py`; el repositorio también puede sustituirse. Se mantiene parcial porque una nueva semántica de herramientas o cambios incompatibles en los formatos de Ollama/MCP requieren modificar `ChatService` o sus adaptadores.

### L - Sustitución de Liskov (LSP): parcial / sin herencia

No hay jerarquías de clases propias; por eso LSP clásico no es directamente aplicable. Las implementaciones falsas satisfacen estructuralmente `ChatModel` y `ToolExecutor` y se inyectan en `create_app()` para probar el mismo flujo que usan los adaptadores reales. Esto verifica sustituibilidad básica en pruebas, no garantiza equivalencia de todos los proveedores en producción.

### I - Segregación de interfaces (ISP): aplicado

`services/contracts.py` define contratos pequeños e independientes: `ChatModel`, `ToolExecutor`, `ToolConnectionProvider` y `HistoryRepository`. Cada consumidor depende de la capacidad que necesita, evitando una interfaz general que mezcle chat, MCP y lectura histórica.

### D - Inversión de dependencias (DIP): aplicado en la composición

`client.create_app()` es la raíz de composición: recibe `llm_factory`, `mcp_service_factory` y `history_repository`, y construye `ChatService` durante el ciclo de vida de FastAPI. `ChatService` depende de `ChatModel` y `ToolExecutor`; los routers acceden a servicios preparados en `app.state`. Las clases concretas quedan en la configuración por defecto y pueden cambiarse por dobles en pruebas.

## Estado de recomendaciones

1. **Orquestación:** implementada en `ChatService`; rutas HTTP y WebSocket son adaptadores.
2. **Contratos e inyección:** implementados en `services/contracts.py` y `create_app()`.
3. **Repositorio histórico:** implementado en `backend/history_repository.py`, compartido por la API y el servidor MCP.
4. **Pruebas:** nueve pruebas con `unittest`: respuesta directa, herramienta única/múltiple, fallo de integración, repositorio, inyección HTTP y contrato del adaptador MCP.

Para encontrar cada principio por archivo y símbolo, consultar [docs/MAPA_SOLID.md](MAPA_SOLID.md).

## Alcance y límites

La revisión cubrió los contratos y servicios en `services/`, la factoría `client.py`, adaptadores y repositorio en `backend/` y pruebas en `tests/test_chat_service.py`. Las pruebas verifican el comportamiento con dobles, no la conexión real con Ollama/MCP ni el comportamiento en producción; las calificaciones no representan una certificación formal.
