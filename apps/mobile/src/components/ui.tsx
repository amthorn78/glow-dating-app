import { useCallback, useEffect, useRef, type PropsWithChildren } from 'react';
import { useFocusEffect } from 'expo-router';
import { AccessibilityInfo, KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View, type TextInputProps } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import type { DevelopmentProfile } from '../contracts/recommendations';

export const colors = {
  background: '#17151E', surface: '#24212D', raised: '#302B3B', text: '#F9F5FF',
  muted: '#C2BCCC', border: '#504859', accent: '#DBC4F9', accentInk: '#251431',
  gold: '#F1DBA4',
};

export function Page({ children, testID }: PropsWithChildren<{ testID?: string }>) {
  return <SafeAreaView style={styles.safe} testID={testID}><KeyboardAvoidingView style={styles.flex}
    behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
    <ScrollView keyboardShouldPersistTaps="handled" keyboardDismissMode="on-drag" contentContainerStyle={styles.page}>{children}</ScrollView>
  </KeyboardAvoidingView></SafeAreaView>;
}

function focusText(node: Text | null) {
  if (!node) return;
  if (Platform.OS === 'web') {
    // React Native Web exposes its host element through the ref. Keep DOM-only
    // focus behavior here; native TextProps has no tabIndex in a clean checkout.
    if (typeof HTMLElement !== 'undefined' && node instanceof HTMLElement) {
      node.tabIndex = -1;
      node.focus();
    }
  } else AccessibilityInfo.sendAccessibilityEvent(node, 'focus');
}

export function ScreenTitle({ children }: { children: string }) {
  const ref = useRef<Text>(null);
  useFocusEffect(useCallback(() => {
    const frame = requestAnimationFrame(() => focusText(ref.current));
    return () => cancelAnimationFrame(frame);
  }, []));
  return <Text ref={ref} style={styles.title} accessibilityRole="header" accessible>{children}</Text>;
}

export function Feedback({ error, message, busy }: { error: string | null; message: string | null; busy: boolean }) {
  const ref = useRef<Text>(null);
  useEffect(() => {
    if (!error) return;
    const frame = requestAnimationFrame(() => focusText(ref.current));
    return () => cancelAnimationFrame(frame);
  }, [error]);
  if (!error && !message && !busy) return null;
  return <View style={styles.notice} accessibilityLiveRegion="polite" testID="feedback">
    {busy && <Text style={styles.body} accessibilityRole="progressbar">Working on this fixture…</Text>}
    {error && <Text ref={ref} accessible accessibilityRole="alert" style={styles.error}>{error}</Text>}
    {!error && message && <Text style={styles.body}>{message}</Text>}
  </View>;
}

export function Field({ label, hint, ...props }: TextInputProps & { label: string; hint?: string }) {
  return <View style={styles.fieldGroup}>
    <Text style={styles.fieldLabel}>{label}</Text>
    {hint && <Text style={styles.small}>{hint}</Text>}
    <TextInput accessibilityLabel={label} accessibilityHint={hint} autoCorrect={false} autoCapitalize="none"
      placeholderTextColor={colors.muted} selectionColor={colors.accent} style={styles.input} {...props} />
  </View>;
}

export function Choice({ label, selected, onPress, disabled = false, testID }: {
  label: string; selected: boolean; onPress: () => void; disabled?: boolean; testID?: string;
}) {
  return <Pressable accessibilityRole="radio" accessibilityLabel={label} accessibilityState={{ selected, checked: selected, disabled }}
    testID={testID} disabled={disabled} onPress={onPress} style={[styles.choice, selected && styles.choiceSelected]}>
    <Text style={styles.choiceText}>{selected ? '● ' : '○ '}{label}</Text>
  </Pressable>;
}

export function Button({ label, onPress, secondary = false, disabled = false, hint, testID }: {
  label: string; onPress?: () => void; secondary?: boolean; disabled?: boolean; hint?: string; testID?: string;
}) {
  return <Pressable testID={testID} accessibilityRole="button" accessibilityLabel={label} accessibilityHint={hint}
    accessibilityState={{ disabled }} disabled={disabled} onPress={onPress}
    style={({ pressed }) => [styles.button, secondary && styles.secondary, disabled && styles.disabled, pressed && styles.pressed]}>
    <Text style={[styles.buttonText, secondary && styles.secondaryText]}>{label}</Text>
  </Pressable>;
}

export function PreviewNotice() {
  return <View style={styles.notice}>
    <Text style={styles.eyebrow}>DEVELOPMENT PREVIEW</Text>
    <Text style={styles.noticeText}>Fictional people. No live compatibility, likes, matches, or messaging.</Text>
  </View>;
}

export function ProfileCard({ profile }: { profile: DevelopmentProfile }) {
  return <View style={styles.card}>
    <View style={styles.portrait} accessibilityElementsHidden importantForAccessibility="no-hide-descendants">
      <View style={styles.orbit} /><View style={styles.orbitSmall} />
      <Text style={styles.initial}>{profile.display_name.slice(0, 1)}</Text>
      <Text style={styles.portraitLabel}>FICTIONAL PROFILE</Text>
    </View>
    <View style={styles.cardBody}>
      <Text style={styles.cardTitle} accessibilityRole="header">{profile.display_name}, {profile.age}</Text>
      <Text style={styles.body}>{profile.summary}</Text>
      <View style={styles.pending}>
        <Text style={styles.pendingTitle}>Compatibility pending</Text>
        <Text style={styles.small}>No Human Design result has been calculated.</Text>
      </View>
    </View>
  </View>;
}

export const styles = StyleSheet.create({
  flex: { flex: 1 },
  fieldGroup: { gap: 8 },
  fieldLabel: { color: colors.text, fontSize: 17, fontWeight: '600' },
  input: { color: colors.text, backgroundColor: colors.surface, borderColor: colors.border, borderWidth: 1, borderRadius: 12, padding: 14, fontSize: 18, minHeight: 54 },
  error: { color: '#FFCECB', fontSize: 17, lineHeight: 25 },
  choice: { minHeight: 48, borderWidth: 1, borderColor: colors.border, padding: 12, borderRadius: 12, justifyContent: 'center' },
  choiceSelected: { borderColor: colors.accent, backgroundColor: colors.raised },
  choiceText: { fontSize: 16, lineHeight: 24, color: colors.text },
  safe: { flex: 1, backgroundColor: colors.background },
  page: { padding: 24, paddingBottom: 40, gap: 22, width: '100%', maxWidth: 640, alignSelf: 'center' },
  brand: { fontSize: 38, fontWeight: '800', color: colors.text, letterSpacing: -1.5 },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 },
  tag: { fontSize: 13, color: colors.gold, fontWeight: '700' },
  eyebrow: { color: colors.gold, fontSize: 12, fontWeight: '700', letterSpacing: 1.5 },
  title: { color: colors.text, fontSize: 32, lineHeight: 39, fontWeight: '700' },
  subtitle: { color: colors.text, fontSize: 23, lineHeight: 29, fontWeight: '600' },
  body: { color: colors.muted, fontSize: 17, lineHeight: 25 },
  small: { color: colors.muted, fontSize: 14, lineHeight: 21 },
  notice: { backgroundColor: colors.surface, padding: 16, gap: 7, borderRadius: 16, borderWidth: 1, borderColor: colors.border },
  noticeText: { color: colors.text, fontSize: 14, lineHeight: 21 },
  card: { backgroundColor: colors.surface, borderRadius: 24, overflow: 'hidden', borderWidth: 1, borderColor: colors.border },
  portrait: { minHeight: 220, backgroundColor: colors.accent, alignItems: 'center', justifyContent: 'center', overflow: 'hidden' },
  orbit: { position: 'absolute', width: 220, height: 220, borderWidth: 1, borderRadius: 110, borderColor: '#AA88C7', left: -25, top: 50 },
  orbitSmall: { position: 'absolute', width: 160, height: 160, borderWidth: 1, borderRadius: 80, borderColor: '#AA88C7', right: -35, top: -45 },
  initial: { fontSize: 82, fontWeight: '300', color: colors.accentInk },
  portraitLabel: { color: colors.accentInk, fontSize: 12, letterSpacing: 1.6, marginTop: 8 },
  cardBody: { padding: 22, gap: 13 },
  cardTitle: { color: colors.text, fontSize: 28, fontWeight: '700' },
  pending: { borderTopWidth: 1, borderTopColor: colors.border, paddingTop: 16, gap: 5, marginTop: 5 },
  pendingTitle: { color: colors.gold, fontSize: 15, fontWeight: '700' },
  button: { minHeight: 52, paddingVertical: 15, paddingHorizontal: 20, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.accent, borderRadius: 14 },
  buttonText: { color: colors.accentInk, fontSize: 17, fontWeight: '700', textAlign: 'center' },
  secondary: { backgroundColor: colors.raised, borderWidth: 1, borderColor: colors.border },
  secondaryText: { color: colors.text },
  disabled: { opacity: 0.55 },
  pressed: { opacity: 0.8 },
  group: { gap: 12 },
  status: { paddingVertical: 24, gap: 15 },
});
