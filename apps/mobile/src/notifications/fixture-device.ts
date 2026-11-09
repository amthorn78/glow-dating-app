import type { TokenSource } from './store.ts';

/**
 * This installation's identity and push token source in the development preview (P06.3, D6). Both
 * are synthetic: no native module, platform or push service is involved, and the tokens are
 * obviously not a device's. P09.2 replaces them with the platform's own.
 */
export const FIXTURE_INSTALLATION_ID = '6f12d000-0000-4000-8000-000000000001';
export const SYNTHETIC_TOKEN_PREFIX = 'SYNTHETIC-FIXTURE-PUSH-TOKEN-';

export function syntheticTokenSource(): TokenSource {
  let serial = 0;
  return Object.freeze({ next: () => `${SYNTHETIC_TOKEN_PREFIX}${++serial}-NOT-A-REAL-DEVICE-TOKEN` });
}
