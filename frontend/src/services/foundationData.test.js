import assert from 'node:assert/strict';
import test from 'node:test';
import { normalizeFoundationResponse } from './foundationData.js';

test('accepts a list of historical records', () => {
  const records = [{ titulo: 'Origen' }];
  assert.deepEqual(normalizeFoundationResponse(records), records);
});

test('accepts the legacy raw envelope', () => {
  const records = [{ titulo: 'Origen' }];
  assert.deepEqual(normalizeFoundationResponse({ raw: records }), records);
});

test('rejects backend error envelopes instead of reporting a connection', () => {
  assert.throws(
    () => normalizeFoundationResponse({ error: 'Archivo no encontrado' }),
    /Archivo no encontrado/,
  );
});

test('rejects unexpected payload shapes', () => {
  assert.throws(() => normalizeFoundationResponse({ data: [] }), /formato de documentos no válido/);
});