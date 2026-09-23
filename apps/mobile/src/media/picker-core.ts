import { FIXTURE_MEDIA_POLICY, type MediaSelection } from './policy.ts';

/** Minimal injected picker boundary. No device URI, EXIF, filename or library ID is retained. */
export type PickerAsset = {
  file?: { size: number; arrayBuffer(): Promise<ArrayBuffer> };
};
export type PickerResult = { canceled: boolean; assets: readonly PickerAsset[] | null };
export type SelectionResult =
  | { kind: 'selected'; selection: MediaSelection }
  | { kind: 'cancelled' | 'unsupported' | 'denied' };

export async function readPickerSelection(result: PickerResult, selectionId: string): Promise<SelectionResult> {
  if (result.canceled) return { kind: 'cancelled' };
  if (!result.assets || result.assets.length !== 1) return { kind: 'unsupported' };
  const file = result.assets[0]!.file;
  // Expo exposes File on web only. Native bytes require a separately verified
  // bounded reader. Never fetch arbitrary provider/content/file URIs.
  if (!file || !Number.isSafeInteger(file.size) || file.size < 1 || file.size > FIXTURE_MEDIA_POLICY.maxEncodedBytes) return { kind: 'unsupported' };
  try {
    const buffer = await file.arrayBuffer();
    if (buffer.byteLength !== file.size || buffer.byteLength > FIXTURE_MEDIA_POLICY.maxEncodedBytes) return { kind: 'unsupported' };
    return { kind: 'selected', selection: {
      selectionId, name: 'Selected photo', declaredMime: 'image/png', bytes: Array.from(new Uint8Array(buffer)),
    } };
  } catch { return { kind: 'unsupported' }; }
}
