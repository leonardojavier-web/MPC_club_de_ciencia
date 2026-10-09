export function normalizeFoundationResponse(payload) {
  if (payload && typeof payload === 'object' && payload.error) {
    throw new Error(payload.error);
  }

  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.raw)) return payload.raw;

  throw new Error('El backend devolvió un formato de documentos no válido.');
}