import { useState } from 'react';
import { router } from 'expo-router';
import { Text, View } from 'react-native';
import { Button, Choice, Field, styles } from '../components/ui';
import { useOnboarding } from '../onboarding/context';
import { FixtureOutcomeControl, OnboardingScreen } from '../onboarding/shell';
import { FIXTURE_PASSWORD, type FixtureOutcome } from '../onboarding/store';

export default function AccountScreen() {
  const { state, store } = useOnboarding();
  const [mode, setMode] = useState<'register' | 'sign_in'>('register');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [outcome, setOutcome] = useState<FixtureOutcome>('success');
  async function submit() {
    const submitted = password;
    setPassword('');
    await store.account(mode, email, submitted, outcome);
  }
  return <OnboardingScreen title="Start with a little trust." step="STEP 1 OF 4 · ACCOUNT" testID="screen-account">
    <Text style={styles.body}>Create a fictional account to explore the onboarding journey. Use alex@example.invalid or sam@example.invalid and the synthetic password shown below. Do not enter real credentials.</Text>
    <View style={styles.group}>
      <Choice label="Create an account" selected={mode === 'register'} onPress={() => setMode('register')} disabled={state.busy} testID="mode-register" />
      <Choice label="Sign in" selected={mode === 'sign_in'} onPress={() => setMode('sign_in')} disabled={state.busy} testID="mode-sign-in" />
    </View>
    <Field label="Fixture email address" value={email} onChangeText={setEmail} keyboardType="email-address" autoComplete="off" editable={!state.busy} testID="account-email" hint="For example: alex@example.invalid" />
    <Field label="Fixture password" value={password} onChangeText={setPassword} secureTextEntry autoComplete="off" editable={!state.busy} testID="account-password" hint={`Synthetic password: ${FIXTURE_PASSWORD}`} onSubmitEditing={() => { if (!state.busy) void submit(); }} />
    <Button label={mode === 'register' ? 'Create fixture account' : 'Sign in to fixture'} testID="account-submit" disabled={state.busy} onPress={() => void submit()} />
    <Button label="Recover access" secondary testID="recover-access" disabled={state.busy} onPress={() => router.push('/recovery')} />
    <FixtureOutcomeControl value={outcome} onChange={setOutcome} outcomes={['success', 'invalid', 'error', 'rate_limited']} />
  </OnboardingScreen>;
}
