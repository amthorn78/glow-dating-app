import { colors } from '../components/ui';
import type { NextPageButtonProps } from './next-page-button';

/** Keep keyboard focus on the browse control through loading and exhaustion.
 * Native disabled buttons blur on web. ARIA-disabled preserves discoverability;
 * every activation still passes this handler and the store's current-state guard.
 */
export function NextPageButton({ disabled, onPress }: NextPageButtonProps) {
  return <button type="button" data-testid="discovery-next" aria-label="Next page" aria-disabled={disabled}
    onClick={() => { if (!disabled) onPress(); }}
    style={{ minHeight: 52, padding: '15px 20px', border: 0, borderRadius: 14,
      backgroundColor: colors.accent, color: colors.accentInk, fontFamily: 'inherit', fontSize: 17,
      fontWeight: 700, textAlign: 'center', opacity: disabled ? 0.55 : 1, cursor: disabled ? 'default' : 'pointer' }}>
    Next page
  </button>;
}
