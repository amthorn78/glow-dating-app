import assert from 'node:assert/strict';
import test from 'node:test';
import { FIXTURE_MEDIA_POLICY, inspectSelection, MediaSelectionFailure, pngCrc, syntheticSelection } from './policy.ts';

test('media policy checks actual PNG bytes independently of filename and declared MIME', () => {
  const selection = syntheticSelection();
  assert.deepEqual(inspectSelection({ ...selection, name: 'wrong.jpg', declaredMime: 'image/jpeg' }),
    { width: 1, height: 1, contentType: 'image/png', encodedBytes: selection.bytes.length });
  assert.throws(() => inspectSelection({ ...syntheticSelection('unsupported'), name: 'safe.png', declaredMime: 'image/png' }), MediaSelectionFailure);
});
for (const kind of ['invalid', 'truncated', 'oversize', 'pixels', 'unsupported'] as const) {
  test(`media policy rejects ${kind} synthetic input`, () => assert.throws(() => inspectSelection(syntheticSelection(kind)), MediaSelectionFailure));
}
test('PNG CRC, chunk framing, terminal IEND and byte integer bounds are checked', () => {
  const input = syntheticSelection(), bytes = [...input.bytes];
  bytes[29] = (bytes[29]! + 1) % 256;
  for (const invalid of [bytes, [...input.bytes, 0], input.bytes.slice(8), [NaN, ...input.bytes.slice(1)],
    [256, ...input.bytes.slice(1)], [0.5, ...input.bytes.slice(1)]]) {
    assert.throws(() => inspectSelection({ ...input, bytes: invalid }), MediaSelectionFailure);
  }
});
test('obsolete policy and malformed selection cannot validate a file', () => {
  assert.throws(() => inspectSelection(syntheticSelection(), { ...FIXTURE_MEDIA_POLICY, version: 'obsolete' }));
  assert.throws(() => inspectSelection({ ...syntheticSelection(), selectionId: '' }));
  assert.throws(() => inspectSelection({ ...syntheticSelection(), name: 'a'.repeat(257) }));
});
test('PNG container screening explicitly does not certify DEFLATE decoding or strip metadata', () => {
  const input = syntheticSelection(), bytes = [...input.bytes];
  // Keep valid PNG framing/CRC but corrupt the compressed stream: no pixel decoder is claimed.
  bytes[41] = 0;
  const crc = pngCrc(bytes.slice(37, 51));
  bytes.splice(51, 4, (crc >>> 24) & 255, (crc >>> 16) & 255, (crc >>> 8) & 255, crc & 255);
  assert.equal(inspectSelection({ ...input, bytes }).width, 1);
  assert.notDeepEqual(bytes, input.bytes);
});
