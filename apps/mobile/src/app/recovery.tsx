import { useState } from 'react';
import { router } from 'expo-router';
import { Text } from 'react-native';
import { Button, Field, styles } from '../components/ui';
import { useOnboarding } from '../onboarding/context';
import { FixtureOutcomeControl, OnboardingScreen } from '../onboarding/shell';
import type { FixtureOutcome } from '../onboarding/store';

export default function RecoveryScreen() {
  const { state, store } = useOnboarding();
  const [email, setEmail] = useState('');
  const [outcome, setOutcome] = useState<FixtureOutcome>('success');
  return <OnboardingScreen title="Find your way back." testID="screen-recovery">
    <Text style={styles.body}>If an eligible account exists, recovery instructions would be sent. This preview sends no email and does not disclose account existence.</Text>
    <Field label="Recovery fixture email" value={email} onChangeText={setEmail} keyboardType="email-address" autoComplete="off" editable={!state.busy} hint="Use a fictional @example.invalid address." testID="recovery-email" />
    <Button label="Request fixture recovery" testID="recovery-submit" disabled={state.busy} onPress={() => void store.requestRecovery(email, outcome)} />
    {state.recoveryReady && <Button label="Open synthetic reset step" testID="open-reset" onPress={() => router.push('/reset-password')} />}
    <Button label="Cancel recovery" secondary testID="recovery-cancel" onPress={() => { store.logout(); router.replace('/account'); }} />
    <FixtureOutcomeControl value={outcome} onChange={setOutcome} />
  </OnboardingScreen>;
}
