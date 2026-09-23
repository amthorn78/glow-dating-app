/** Provisional test inputs, never launch policy or a provider guarantee. */
export const FIXTURE_MEDIA_POLICY = Object.freeze({ version: 'development-media-1', supportedType: 'image/png',
  maxEncodedBytes: 1_048_576, maxDimension: 2048, maxPixels: 4_194_304, maxPhotos: 4,
  maxCollection: 20, grantDurationMs: 60_000, maxUploadAttempts: 3, maxPurgeAttempts: 3, maxReceipts: 128,
  maxRemovalReceipts: 20, maxPurgeReceipts: 20 });
export type MediaSelection = Readonly<{ selectionId: string; name: string; declaredMime: string; bytes: readonly number[] }>;
export type SyntheticImage = 'valid' | 'invalid' | 'oversize' | 'pixels' | 'unsupported' | 'truncated';
export class MediaSelectionFailure extends Error {
  constructor(message = 'Choose a supported, structurally valid PNG within the development limits.') { super(message); this.name = 'MediaSelectionFailure'; }
}
const signature = [137, 80, 78, 71, 13, 10, 26, 10];
const u32 = (n: number) => [(n >>> 24) & 255, (n >>> 16) & 255, (n >>> 8) & 255, n & 255];
const read32 = (bytes: readonly number[], offset: number) => bytes[offset]! * 16_777_216 + bytes[offset + 1]! * 65_536 + bytes[offset + 2]! * 256 + bytes[offset + 3]!;
export function pngCrc(bytes: readonly number[]): number {
  let crc = 0xffffffff;
  for (const byte of bytes) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit += 1) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
  }
  return (crc ^ 0xffffffff) >>> 0;
}
const chunk = (type: string, body: number[]) => {
  const data = [...Array.from(type, char => char.charCodeAt(0)), ...body];
  return [...u32(body.length), ...data, ...u32(pngCrc(data))];
};
/** Actual tiny PNG container. Its pixels/metadata are not decoded by this mobile fixture. */
export function syntheticSelection(kind: SyntheticImage = 'valid'): MediaSelection {
  const dimension = kind === 'pixels' ? 2049 : 1;
  const bytes = [...signature, ...chunk('IHDR', [...u32(dimension), ...u32(dimension), 8, 0, 0, 0, 0]),
    ...chunk('IDAT', [120, 156, 99, 96, 0, 0, 0, 2, 0, 1]), ...chunk('IEND', [])];
  return { selectionId: `synthetic-${kind}`, name: `Synthetic ${kind}.png`, declaredMime: 'image/png',
    bytes: kind === 'oversize' ? Array(FIXTURE_MEDIA_POLICY.maxEncodedBytes + 1).fill(0) :
      kind === 'invalid' ? [137, 80, 78] : kind === 'unsupported' ? [255, 216, 255, 217] :
        kind === 'truncated' ? bytes.slice(0, -5) : bytes };
}
/** Container validation only: no DEFLATE/pixel decoder, metadata removal or malware proof. */
export function inspectSelection(selection: MediaSelection, policy: Readonly<{ version: string }> = FIXTURE_MEDIA_POLICY):
Readonly<{ width: number; height: number; contentType: 'image/png'; encodedBytes: number }> {
  const fail = () => { throw new MediaSelectionFailure(); };
  if (policy.version !== FIXTURE_MEDIA_POLICY.version) fail();
  if (!selection || !/^[A-Za-z0-9._-]{1,96}$/.test(selection.selectionId) || typeof selection.name !== 'string' ||
      selection.name.length > 256 || typeof selection.declaredMime !== 'string' || selection.declaredMime.length > 128 ||
      !Array.isArray(selection.bytes)) fail();
  const bytes = selection.bytes;
  if (bytes.length < 57 || bytes.length > FIXTURE_MEDIA_POLICY.maxEncodedBytes ||
      bytes.some(byte => !Number.isInteger(byte) || byte < 0 || byte > 255) || signature.some((byte, i) => bytes[i] !== byte)) fail();
  let offset = 8, width = 0, height = 0, imageData = false, ended = false, chunks = 0;
  while (offset < bytes.length) {
    if (offset + 12 > bytes.length || chunks++ > 128) fail();
    const length = read32(bytes, offset), end = offset + 12 + length;
    if (end > bytes.length) fail();
    const type = String.fromCharCode(...bytes.slice(offset + 4, offset + 8));
    if (!/^[A-Za-z]{4}$/.test(type) || pngCrc(bytes.slice(offset + 4, end - 4)) !== read32(bytes, end - 4)) fail();
    if (offset === 8 && type !== 'IHDR') fail();
    if (type === 'IHDR') {
      if (offset !== 8 || length !== 13) fail();
      width = read32(bytes, offset + 8); height = read32(bytes, offset + 12);
      if (!width || !height || width > FIXTURE_MEDIA_POLICY.maxDimension || height > FIXTURE_MEDIA_POLICY.maxDimension ||
          width * height > FIXTURE_MEDIA_POLICY.maxPixels || bytes[offset + 16] !== 8 ||
          ![0, 2, 6].includes(bytes[offset + 17]!) || bytes[offset + 18] !== 0 || bytes[offset + 19] !== 0 || bytes[offset + 20] !== 0) fail();
    } else if (type === 'IDAT') {
      if (!length) fail();
      imageData = true;
    } else if (type === 'IEND') {
      if (length || !imageData || end !== bytes.length) fail();
      ended = true;
    } else if (type[0] === type[0]!.toUpperCase() && type !== 'PLTE') fail();
    offset = end;
  }
  if (!ended) fail();
  return { width, height, contentType: 'image/png', encodedBytes: bytes.length };
}
