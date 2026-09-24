import { colors } from '../components/ui';
import type { ActionButtonProps } from './action-button';

/** Retain keyboard focus during a delayed submission. The store also rejects
 * duplicate commands; disabled presentation is never command authority. */
export function ActionButton({ label, testID, disabled, onPress, secondary = false }: ActionButtonProps) {
  return <button type="button" data-testid={testID} aria-label={label} aria-disabled={disabled}
    onClick={() => { if (!disabled) onPress(); }}
    style={{ minHeight: 52, padding: '15px 20px', border: secondary ? `1px solid ${colors.border}` : 0,
      borderRadius: 14, backgroundColor: secondary ? colors.raised : colors.accent,
      color: secondary ? colors.text : colors.accentInk, fontFamily: 'inherit', fontSize: 17,
      fontWeight: 700, textAlign: 'center', opacity: disabled ? 0.55 : 1,
      cursor: disabled ? 'default' : 'pointer', overflowWrap: 'anywhere' }}>{label}</button>;
}
