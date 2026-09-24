import { useEffect, useRef } from 'react';
import { router, useIsFocused } from 'expo-router';
import { Text, View } from 'react-native';
import { Button, focusText, styles } from '../components/ui';
import type { DiscoveryMode } from '../discovery/fixture-adapter';
import { useInteractions } from './context';
import { ActionButton } from './action-button';

export function InteractionFeedback() {
  const { store, state } = useInteractions();
  const focused = useIsFocused();
  const ref = useRef<Text>(null);
  useEffect(() => {
    // Retained hidden routes must never steal focus after a shared-store update.
    if (!focused || (!state.error && !state.message)) return;
    const frame = requestAnimationFrame(() => focusText(ref.current));
    return () => cancelAnimationFrame(frame);
  }, [focused, state.error, state.message]);
  if (state.status === 'idle' && !state.message && !state.error) return null;
  return <View style={styles.notice} testID="interaction-feedback" accessibilityLiveRegion="polite">
    {state.status === 'pending' && <Text style={styles.body} accessibilityRole="progressbar">Saving your action…</Text>}
    {(state.error || state.message) && <Text ref={ref} accessible accessibilityRole={state.error ? 'alert' : undefined}
      testID="interaction-result" style={state.error ? styles.error : styles.body}>{state.error || state.message}</Text>}
    {state.canRetry && <Button label="Retry same action" testID="interaction-retry" secondary disabled={state.status === 'pending'}
      onPress={() => void store.retry()} hint="Retry this request without creating a second action." />}
    {state.scenario === 'delayed' && state.status === 'pending' && <Button label="Complete delayed fixture delivery"
      testID="interaction-release" secondary onPress={() => store.releaseDelayed()} />}
  </View>;
}

export function CandidateActions({ mode, profileId, name }: { mode: DiscoveryMode; profileId: string; name: string }) {
  const { store, state } = useInteractions();
  const disabled = state.status === 'pending' || !store.canAct(mode, profileId);
  return <View style={styles.group} testID={`interaction-actions-${profileId}`}>
    <ActionButton label={`Like ${name}`} testID={`like-${profileId}`} disabled={disabled}
      onPress={() => void store.submit(mode, profileId, 'like')} />
    <ActionButton label={`Pass ${name}`} testID={`pass-${profileId}`} secondary disabled={disabled}
      onPress={() => void store.submit(mode, profileId, 'pass')} />
  </View>;
}

export function InteractionScenarios() {
  const { store, state } = useInteractions();
  return <View style={styles.notice} testID="interaction-scenarios">
    <Text style={styles.eyebrow}>INTERACTION TEST SCENARIOS</Text>
    <Text style={styles.small}>Internal fictional setup. The reciprocal setup submits Jules’s action through the same command service. It does not set a match flag.</Text>
    <InteractionFeedback />
    <Button label="Submit fictional Jules reciprocal like" testID="interaction-reciprocal" secondary
      onPress={() => void store.developmentReciprocal('profile-jules')} />
    <Button label="Block fictional Jules" testID="interaction-block" secondary onPress={() => void store.developmentBlock('profile-jules', true)} />
    <Button label="Unblock fictional Jules" testID="interaction-unblock" secondary onPress={() => void store.developmentBlock('profile-jules', false)} />
    <Text style={styles.small}>Selected delivery fixture: {state.scenario.replaceAll('_', ' ')}.</Text>
    {(['normal', 'offline', 'lost_response', 'delayed'] as const).map(value => <Button key={value}
      label={`Interaction ${value.replaceAll('_', ' ')} fixture`} testID={`interaction-scenario-${value}`}
      secondary onPress={() => store.setScenario(value)} />)}
    <Button label="Complete delayed fixture delivery" testID="interaction-release" secondary onPress={() => store.releaseDelayed()} />
    <Button label="Your matches" testID="open-matches" secondary onPress={() => router.push('/matches')} />
  </View>;
}
