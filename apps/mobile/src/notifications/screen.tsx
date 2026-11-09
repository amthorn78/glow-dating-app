import { useCallback } from 'react';
import { router, useFocusEffect } from 'expo-router';
import { Text, View } from 'react-native';
import { Button, styles } from '../components/ui';
import { OnboardingScreen } from '../onboarding/shell';
import { useNotifications } from './context';
import { NotificationFixtureControls } from './controls';
import { DENIED, FAILURE_COPY, INTRO, KINDS, KIND_LABEL, KIND_SENDS, LOADING, SCREEN_TITLE, STATUS_OFF, STATUS_ON, TURN_OFF, TURN_ON } from './copy';

/**
 * The notification settings screen (P06.3, Outcome 3), at `/notifications`, opened from the
 * profile screen. Before any request it says what each kind sends. Turning a kind on is the only
 * thing that asks for the permission; with the permission declined, Glow works as before.
 */
export function NotificationSettingsScreen() {
  const { store, state } = useNotifications();
  useFocusEffect(useCallback(() => { void store.load(); }, [store]));
  const ready = state.status === 'ready';
  return <OnboardingScreen title={SCREEN_TITLE} testID="screen-notifications">
    <Text style={styles.body}>{INTRO}</Text>
    {state.status === 'loading' && <Text style={styles.body} accessibilityRole="progressbar">{LOADING}</Text>}
    <View style={styles.group} testID="notification-kinds">
      {KINDS.map(kind => <View key={kind} style={styles.notice} testID={`notification-kind-${kind}`}>
        <Text style={styles.subtitle} accessibilityRole="header">{KIND_LABEL[kind]}</Text>
        <Text style={styles.body} testID={`notification-sends-${kind}`}>{KIND_SENDS[kind]}</Text>
        <Text style={styles.body} testID={`notification-status-${kind}`}>{state[kind] ? STATUS_ON : STATUS_OFF}</Text>
        <Button label={state[kind] ? TURN_OFF[kind] : TURN_ON[kind]} testID={`notification-toggle-${kind}`} secondary={state[kind]}
          disabled={!ready || state.busy} onPress={() => void store.setKind(kind, !state[kind])} />
      </View>)}
    </View>
    {state.denied && <Text style={styles.body} accessibilityRole="alert" testID="notifications-denied">{DENIED}</Text>}
    {state.error && <Text style={styles.error} accessibilityRole="alert" testID="notifications-error">{FAILURE_COPY[state.error]}</Text>}
    {state.status === 'error' && <Button label="Load notification settings again" testID="notifications-reload" secondary onPress={() => void store.load()} />}
    <NotificationFixtureControls />
    <Button label="Return to your profile" testID="notifications-profile" secondary onPress={() => router.push('/profile')} />
  </OnboardingScreen>;
}
