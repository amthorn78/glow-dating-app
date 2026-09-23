/** After closed JSON Schema validation: key uniqueness absent from standard JSON Schema. */
export function assertUniqueKeys(value: unknown): boolean {
  if (Array.isArray(value)) return value.every(assertUniqueKeys);
  if (value !== null && typeof value === 'object') {
    const object = value as Record<string, unknown>;
    const itemKey = object.kind === 'media_collection' ? 'asset_id' : 'profile_id';
    for (const [collection, key] of [['items', itemKey], ['selections', 'dimension']] as const) {
      const entries = object[collection];
      if (Array.isArray(entries)) {
        const keys = entries.map(entry => (entry as Record<string, unknown>)[key]);
        if (new Set(keys).size !== keys.length) return false;
      }
    }
    return Object.values(object).every(assertUniqueKeys);
  }
  return true;
}
