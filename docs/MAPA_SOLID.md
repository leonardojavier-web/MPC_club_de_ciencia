# Mapa rápido de SOLID

Índice de los puntos de entrada para localizar cada principio sin buscar por todo el proyecto. Consulta [la auditoría backend](AUDITORIA_SOLID.md) y [la auditoría frontend](AUDITORIA_FRONTEND.md).

| Principio | Dónde mirar | Qué representa |
|---|---|---|
| SRP | `services/chat_service.py` - `ChatService.respond()` | Orquesta una conversación y llamadas a herramientas, sin gestionar HTTP ni abrir conexiones. |
| SRP | `backend/app/routers/chat.py` y `foundation.py` | Adaptadores de transporte: validan solicitudes y delegan en servicios/repositorio. |
| SRP | `backend/history_repository.py` - `JsonHistoryRepository` | Único punto de lectura del JSON histórico, compartido por API y MCP. |
| SRP | `frontend/src/App.jsx` | Composición de pantalla; no ejecuta solicitudes ni contiene el estado de dominio del chat. |
| SRP | `frontend/src/hooks/` y `frontend/src/components/` | Lógica de datos/chat/redimensionado y vistas aisladas, respectivamente. |
| OCP | `services/contracts.py` - protocolos | Puntos de extensión para modelo, ejecutor de herramientas, conexión MCP y repositorio. |
| OCP | `services/mcp_service.py` - `MCPToolService._format_tools()` | Adapta dinámicamente herramientas anunciadas por MCP sin condiciones por nombre. |
| LSP | `tests/test_chat_service.py` - `FakeChatModel`, `FakeToolExecutor`, `FakeMCPService` | Implementaciones sustituibles usadas para probar los contratos en el flujo de aplicación. No hay jerarquías propias. |
| ISP | `services/contracts.py` - `ChatModel`, `ToolExecutor`, `ToolConnectionProvider`, `HistoryRepository` | Contratos pequeños por capacidad, sin una interfaz única que agrupe responsabilidades. |
| DIP | `client.py` - `create_app()` | Recibe fábricas y repositorio; el ciclo de vida construye las implementaciones y el servicio de aplicación. |
| DIP | `services/chat_service.py` - constructor de `ChatService` | Consume `ChatModel` y `ToolExecutor`, no los clientes Ollama/MCP directamente. |
| DIP | `frontend/src/services/api.js` | Centraliza la dependencia HTTP y permite cambiar la URL base con `VITE_API_BASE_URL`. |
| SRP | `frontend/src/services/foundationData.js` - `normalizeFoundationResponse()` | Valida y normaliza las variantes admitidas por el endpoint histórico. |
| OCP / DIP | `frontend/src/hooks/useChat.js`, `useFoundationData.js` | Reciben las funciones `postMessage` y `loadFoundation` como dependencias sustituibles. |
| A11y / responsive | `frontend/src/components/ChatPanel.jsx` - `role="separator"` | Redimensionado con puntero y teclado, con propiedades ARIA. |

## Pruebas relacionadas

Las pruebas están en `tests/test_chat_service.py`:

- `test_replies_without_tools`: respuesta directa del modelo.
- `test_runs_a_single_tool`: ejecución de una herramienta.
- `test_runs_multiple_tools_and_reports_status`: varias herramientas y callback de estado.
- `test_propagates_tool_integration_error`: fallo del ejecutor MCP.
- `test_executor_maps_session_result_to_text_contract`: el adaptador MCP satisface el contrato de resultado de texto.
- `test_formats_announced_tools_without_name_specific_logic`: adapta herramientas sin lógica por nombre.
- `test_http_chat_uses_injected_providers`: sustitución de proveedores en la aplicación.
- `test_http_chat_rejects_blank_messages`: validación del adaptador HTTP.
- `test_reads_json_records_from_configured_path`: lectura del repositorio JSON.

Pruebas frontend en `frontend/src/services/foundationData.test.js`, ejecutadas mediante `npm test` desde `frontend/`.

## Búsqueda puntual

Desde la raíz del repositorio, buscar los símbolos anteriores en VS Code con `Ctrl+Shift+F`, o ejecutar:

```powershell
rg -n "ChatService|ChatModel|ToolExecutor|ToolConnectionProvider|HistoryRepository|create_app|_format_tools" client.py services backend tests
```