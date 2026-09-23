import { useState } from 'react';
import { router } from 'expo-router';
import { Text } from 'react-native';
import { Button, Field, styles } from '../components/ui';
import { useOnboarding } from '../onboarding/context';
import { FixtureOutcomeControl, OnboardingScreen } from '../onboarding/shell';
import { FIXTURE_PASSWORD, type FixtureOutcome } from '../onboarding/store';

export default function ResetPasswordScreen() {
  const { state, store } = useOnboarding();
  const [password, setPassword] = useState('');
  const [outcome, setOutcome] = useState<FixtureOutcome>('success');
  async function submit() {
    const submitted = password;
    setPassword('');
    await store.resetPassword(submitted, outcome);
  }
  return <OnboardingScreen title="Reset the fixture password." testID="screen-reset-password">
    <Text style={styles.body}>This synthetic recovery step changes no real password. A successful result returns you to sign-in; it does not bypass verification or onboarding.</Text>
    <Field label="New fixture password" value={password} onChangeText={setPassword} secureTextEntry autoComplete="off" editable={!state.busy} hint={`Use the synthetic value: ${FIXTURE_PASSWORD}`} testID="reset-password" />
    <Button label="Complete fixture reset" testID="reset-submit" disabled={state.busy} onPress={() => void submit()} />
    <Button label="Cancel reset" secondary testID="reset-cancel" onPress={() => { store.logout(); router.replace('/account'); }} />
    <FixtureOutcomeControl value={outcome} onChange={setOutcome} />
  </OnboardingScreen>;
}
