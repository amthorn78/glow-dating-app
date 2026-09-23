import { useState } from 'react';
import { Text } from 'react-native';
import { Button, styles } from '../components/ui';
import { useOnboarding } from '../onboarding/context';
import { FixtureOutcomeControl, OnboardingScreen } from '../onboarding/shell';
import type { FixtureOutcome } from '../onboarding/store';

export default function VerificationScreen() {
  const { state, store } = useOnboarding();
  const [outcome, setOutcome] = useState<FixtureOutcome>('success');
  return <OnboardingScreen title="Check your address." step="STEP 2 OF 4 · VERIFICATION" testID="screen-verify">
    <Text style={styles.body}>In the live flow, you will confirm your email using the maintained account provider. No email has been sent in this preview.</Text>
    <Text style={styles.small}>This development action asks the synthetic adapter to process a fixture verification result. It cannot verify a real person or grant real access.</Text>
    <Button label="Process fixture verification" testID="verify-submit" disabled={state.busy} onPress={() => void store.verify(outcome)} />
    <Button label="Resend fixture verification" testID="verify-resend" secondary disabled={state.busy} onPress={() => void store.resend(outcome)} />
    <FixtureOutcomeControl value={outcome} onChange={setOutcome} />
  </OnboardingScreen>;
}
