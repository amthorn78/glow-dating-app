import * as ImagePicker from 'expo-image-picker';
import { readPickerSelection, type SelectionResult } from './picker-core';

/** SDK 57 Images-only system picker, invoked synchronously from a user gesture.
 * Modern photo selection needs no blanket library permission. Simulated denied /
 * limited outcomes exercise our fixture seam; they are not device permission proof.
 * Native bounded file reading and Android activity-restoration proof remain N01.
 */
export async function pickPhoto(selectionId: string, signal?: AbortSignal): Promise<SelectionResult> {
  if (signal?.aborted) return { kind: 'cancelled' };
  try {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'], allowsMultipleSelection: false, allowsEditing: false,
      quality: 1, base64: false, exif: false,
    });
    if (signal?.aborted) return { kind: 'cancelled' };
    return await readPickerSelection(result, selectionId);
  } catch { return { kind: 'unsupported' }; }
}
