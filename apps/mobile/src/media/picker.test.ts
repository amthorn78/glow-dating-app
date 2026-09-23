import assert from 'node:assert/strict';
import test from 'node:test';
import { readPickerSelection } from './picker-core.ts';
import { FIXTURE_MEDIA_POLICY, inspectSelection, syntheticSelection } from './policy.ts';

test('bounded picker reads actual File bytes without retaining local/private metadata', async () => {
  const source = syntheticSelection('valid');
  const bytes = new Uint8Array(source.bytes);
  const result = await readPickerSelection({ canceled: false, assets: [{ file: { size: bytes.length, arrayBuffer: async () => bytes.buffer } }] }, 'web-selection');
  assert.equal(result.kind, 'selected');
  if (result.kind !== 'selected') return;
  assert.deepEqual(result.selection.bytes, source.bytes);
  assert.equal(result.selection.name, 'Selected photo');
  assert.equal(result.selection.selectionId, 'web-selection');
  assert.doesNotThrow(() => inspectSelection(result.selection));
  assert.deepEqual(Object.keys(result.selection).sort(), ['bytes', 'declaredMime', 'name', 'selectionId']);
});

test('picker cancellation, absent native reader, multiple assets and oversize fail closed before reading', async () => {
  let reads = 0;
  const oversized = { size: FIXTURE_MEDIA_POLICY.maxEncodedBytes + 1, arrayBuffer: async () => { reads += 1; return new ArrayBuffer(1); } };
  assert.deepEqual(await readPickerSelection({ canceled: true, assets: null }, 'cancel'), { kind: 'cancelled' });
  assert.deepEqual(await readPickerSelection({ canceled: false, assets: [{}] }, 'native'), { kind: 'unsupported' });
  assert.deepEqual(await readPickerSelection({ canceled: false, assets: [{}, {}] }, 'many'), { kind: 'unsupported' });
  assert.deepEqual(await readPickerSelection({ canceled: false, assets: [{ file: oversized }] }, 'large'), { kind: 'unsupported' });
  assert.equal(reads, 0);
});

test('unreadable or changed-length selected files cannot enter a selection', async () => {
  for (const file of [
    { size: 1, arrayBuffer: async () => { throw new Error('synthetic read failure'); } },
    { size: 1, arrayBuffer: async () => new ArrayBuffer(2) },
  ]) assert.deepEqual(await readPickerSelection({ canceled: false, assets: [{ file }] }, 'invalid'), { kind: 'unsupported' });
});
