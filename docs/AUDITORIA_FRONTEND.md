# Auditoría SOLID - Frontend

**Proyecto:** Historia MCP - Las Varillas
**Fecha:** 2026-10-09
**Tipo de revisión:** inspección estática y pruebas unitarias de normalización de datos

## Resumen ejecutivo

El frontend tiene límites reconocibles entre composición de pantalla, componentes, hooks y acceso HTTP. Esta revisión encontró problemas concretos de validación de respuesta, estado de conexión, uso en pantallas pequeñas y acceso por teclado; se corrigieron en esta rama. La composición sigue siendo sustituible en los hooks, aunque la capa visual no cuenta todavía con pruebas automatizadas de interacción.

| Principio | Evaluación | Lectura breve |
|---|---|---|
| SRP - Responsabilidad única | Aplicado | `App.jsx` compone; componentes presentan; hooks coordinan estado y servicios encapsulan HTTP/datos. |
| OCP - Abierto/cerrado | Parcial | Los paneles y hooks reciben callbacks y dependencias; nuevos formatos de API requieren ampliar explícitamente el normalizador. |
| LSP - Sustitución de Liskov | No aplicable directamente | No hay clases ni jerarquías frontend propias; las funciones API pueden sustituirse al inyectarlas en hooks. |
| ISP - Segregación de interfaces | Aplicado | Props de componentes y retornos de hooks se limitan a capacidades concretas. |
| DIP - Inversión de dependencias | Parcial, mejorado | Los hooks aceptan loaders/acciones sustituibles; las implementaciones por defecto siguen siendo funciones del cliente HTTP. |

## Devolución: qué se corrigió

| Hallazgo | Cambio aplicado | Dónde encontrarlo |
|---|---|---|
| Un objeto `{error: ...}` con HTTP 200 se convertía en una lista vacía y el estado podía marcar backend conectado. | Se normaliza y valida la respuesta; los errores y formatos inesperados se rechazan y se muestra “Sin conexión”. | `frontend/src/services/foundationData.js`, `api.js`, `hooks/useFoundationData.js`, `components/ReadingPane.jsx` |
| El panel lateral podía ocupar demasiado espacio en móviles y superponerse a la lectura. | El chat se presenta como panel fijo con fondo de cierre en móvil; el estado inicial depende del ancho de pantalla. | `frontend/src/App.jsx`, `components/ChatPanel.jsx` |
| El control de redimensionado solo respondía al puntero. | El separador tiene rol y valores ARIA, foco de teclado y ajuste con flechas; los límites se acotan también en pantallas estrechas. | `frontend/src/components/ChatPanel.jsx`, `hooks/useChatPanelWidth.js` |
| Los hooks dependían directamente de funciones de red, lo que dificultaba sustituirlas. | `useChat` acepta `postMessage` y `useFoundationData` acepta `loadFoundation`, manteniendo el cliente real como valor predeterminado. | `frontend/src/hooks/useChat.js`, `useFoundationData.js` |
| No había una prueba fácil de ejecutar para validar los formatos del endpoint. | Se agregaron cuatro pruebas nativas de Node y el comando `npm test`, sin nuevas dependencias. | `frontend/src/services/foundationData.test.js`, `frontend/package.json` |

## Hallazgos por principio

### S - Responsabilidad única (SRP): aplicado

`frontend/src/App.jsx` compone el layout y conecta los hooks con las vistas. `components/` contiene `HistorySidebar`, `ReadingPane` y `ChatPanel`; `hooks/` gestiona datos, conversación y ancho del panel; `services/api.js` concentra las solicitudes HTTP y `services/foundationData.js` valida el formato de registros.

### O - Abierto/cerrado (OCP): parcial

Los componentes reciben acciones mediante props y los hooks reciben funciones API sustituibles, por lo que se pueden extender o probar sin cambiar su presentación. El normalizador acepta deliberadamente una lista directa o el sobre legado `{raw: [...]}`; si el backend adopta otro formato, hay que añadirlo de forma explícita y cubrirlo con prueba. Esto evita aceptar silenciosamente respuestas desconocidas.

### L - Sustitución de Liskov (LSP): no aplicable directamente

El frontend no define jerarquías de clases ni subtipos. La sustitución relevante es funcional: las dependencias `loadFoundation` y `postMessage` admiten funciones alternativas con la misma forma. No se atribuye cumplimiento de LSP clásico sin jerarquías que evaluar.

### I - Segregación de interfaces (ISP): aplicado

Los componentes reciben solamente sus datos y acciones. `useFoundationData` expone registros/estado de conexión/carga; `useChat` expone mensajes/entrada/envío; `useChatPanelWidth` expone ancho y controles de redimensionado. No se creó una API de frontend única que mezcle esas responsabilidades.

### D - Inversión de dependencias (DIP): parcial, mejorado

`useChat({ postMessage })` y `useFoundationData({ loadFoundation })` dependen de funciones y permiten inyectar alternativas; `api.js` encapsula Axios y permite configurar la URL mediante `VITE_API_BASE_URL`. La aplicación normal sigue utilizando los valores predeterminados, y aún no hay pruebas de renderizado que verifiquen la sustitución a nivel de hooks/componentes.

## Pruebas y límites

Se añadieron cuatro pruebas de `normalizeFoundationResponse`: lista directa, sobre legado, error del backend y formato inesperado. Se ejecutan con `npm test`. También pasan `npm run lint` y `npm run build`.

No se agregaron pruebas de interacción con DOM ni se verificó el diseño con navegador en diferentes tamaños; el comportamiento responsive y teclado se ha validado por lint y build, no mediante una sesión visual automatizada. La conexión real con el backend tampoco forma parte de estas pruebas.

Para localizar símbolos backend/frontend, consultar [MAPA_SOLID.md](MAPA_SOLID.md).