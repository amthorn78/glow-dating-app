import type { PropsWithChildren } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import type { DevelopmentProfile } from '../contracts/recommendations';

export const colors = {
  background: '#17151E', surface: '#24212D', raised: '#302B3B', text: '#F9F5FF',
  muted: '#C2BCCC', border: '#504859', accent: '#DBC4F9', accentInk: '#251431',
  gold: '#F1DBA4',
};

export function Page({ children }: PropsWithChildren) {
  return <SafeAreaView style={styles.safe}><ScrollView contentContainerStyle={styles.page}>{children}</ScrollView></SafeAreaView>;
}

export function Button({ label, onPress, secondary = false, disabled = false, hint }: {
  label: string; onPress?: () => void; secondary?: boolean; disabled?: boolean; hint?: string;
}) {
  return <Pressable accessibilityRole="button" accessibilityLabel={label} accessibilityHint={hint}
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
