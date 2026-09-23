import { useState, type PropsWithChildren } from 'react';
import { router } from 'expo-router';
import { Text, View } from 'react-native';
import { Button, Choice, Feedback, Page, PreviewNotice, ScreenTitle, styles } from '../components/ui';
import { useOnboarding } from './context';
import type { FixtureOutcome } from './store';

export function OnboardingScreen({ title, step, children, testID }: PropsWithChildren<{ title: string; step?: string; testID: string }>) {
  const { state, store } = useOnboarding();
  return <Page testID={testID}>
    <View style={styles.headerRow}><Text style={styles.brand}>glow</Text><Text style={styles.tag}>A LITTLE MORE CONNECTION</Text></View>
    <PreviewNotice />
    <View style={styles.group}>{step && <Text style={styles.eyebrow}>{step}</Text>}<ScreenTitle>{title}</ScreenTitle></View>
    <Feedback error={state.error} message={state.message} busy={state.busy} />
    {children}
    <View style={styles.group}>
      {state.account && state.account.session_state === 'valid' && <Button label="Log out" testID="logout" secondary onPress={() => { store.logout(); router.replace('/'); }} />}
      <Button label="Development scenarios" testID="development-link" secondary onPress={() => router.push('/development')} />
    </View>
  </Page>;
}

export function FixtureOutcomeControl({ value, onChange, outcomes = ['success', 'invalid', 'expired', 'wrong_context', 'replayed', 'error', 'rate_limited'] }: {
  value: FixtureOutcome; onChange: (value: FixtureOutcome) => void; outcomes?: readonly FixtureOutcome[];
}) {
  const [expanded, setExpanded] = useState(false);
  const labels: Record<FixtureOutcome, string> = { success: 'Success', invalid: 'Invalid', expired: 'Expired', wrong_context: 'Wrong context', replayed: 'Replayed', error: 'Temporary error', rate_limited: 'Rate limited' };
  return <View style={styles.notice}>
    <Button secondary label={expanded ? 'Hide fixture outcomes' : 'Choose fixture outcome'} testID="fixture-outcomes" onPress={() => setExpanded(!expanded)} />
    <Text style={styles.small}>Development adapter only. Selected result: {labels[value]}. No real provider is contacted.</Text>
    {expanded && outcomes.map((outcome) => <Choice key={outcome} label={`Fixture outcome: ${labels[outcome]}`} selected={value === outcome}
      onPress={() => onChange(outcome)} testID={`outcome-${outcome}`} />)}
  </View>;
}
