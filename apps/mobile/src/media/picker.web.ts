import { readPickerSelection, type SelectionResult } from './picker-core';

/** Browser fixture byte-selection seam. Expo's web picker decodes image metadata
 * before returning File, so this seam applies encoded-byte bounds before any
 * application read and performs no image decoding or object-URL construction.
 * This is not native picker/device evidence.
 */
export function pickPhoto(selectionId: string, signal?: AbortSignal): Promise<SelectionResult> {
  if (typeof document === 'undefined' || signal?.aborted) return Promise.resolve({ kind: 'cancelled' });
  const input = document.createElement('input');
  input.type = 'file'; input.accept = 'image/png'; input.multiple = false;
  input.style.display = 'none'; input.setAttribute('data-testid', 'media-file-input');
  document.body.appendChild(input);
  return new Promise(resolve => {
    let settled = false;
    const cleanup = () => {
      input.removeEventListener('change', onChange); input.removeEventListener('cancel', onCancel);
      signal?.removeEventListener('abort', onCancel);
      input.value = ''; input.remove();
    };
    const finish = (result: SelectionResult) => {
      if (settled) return;
      settled = true; cleanup(); resolve(result);
    };
    const onCancel = () => finish({ kind: 'cancelled' });
    const onChange = () => {
      const files = input.files;
      const file = files?.length === 1 ? files[0] : undefined;
      // Drop the DOM file handle immediately. Only a bounded read may continue.
      input.value = ''; input.remove();
      if (!file) { finish({ kind: 'cancelled' }); return; }
      void readPickerSelection({ canceled: false, assets: [{ file }] }, selectionId).then(finish);
    };
    input.addEventListener('change', onChange); input.addEventListener('cancel', onCancel);
    signal?.addEventListener('abort', onCancel, { once: true });
    try { input.click(); } catch { finish({ kind: 'unsupported' }); }
  });
}
