import { router } from 'expo-router';
import { Text, View } from 'react-native';
import { Button, styles } from '../components/ui';
import { useOnboarding } from '../onboarding/context';
import { OnboardingScreen } from '../onboarding/shell';

export default function RemainingScreen() {
  const { state, store } = useOnboarding();
  return <OnboardingScreen title="A good beginning. More to come." testID="screen-remaining">
    <Text style={styles.body}>Your fixture account and private input steps are saved for this session. Your profile is still incomplete, so you cannot enter discovery.</Text>
    <View style={styles.notice}>
      <Text style={styles.subtitle} accessibilityRole="header">Still needed</Text>
      <Text style={styles.body}>Profile and preferences, photos and review, and resolved launch policies are later work. This screen does not complete those requirements.</Text>
      <Text style={styles.small}>Birth resolution: {state.birth?.resolution ?? 'missing'}. No chart has been calculated.</Text>
    </View>
    <Button label="Edit private birth input" testID="edit-birth" onPress={() => router.push('/birth')} />
    <Button label="Review eligibility and consent" testID="review-eligibility" secondary onPress={() => router.push('/eligibility')} />
    {state.birth?.resolution === 'unavailable' && <Button label="Retry fixture resolution" testID="retry-resolution" secondary disabled={state.busy} onPress={() => void store.retryBirth('pending')} />}
    <Button label="Save session checkpoint" testID="checkpoint-save" secondary onPress={() => store.saveCheckpoint()} />
    <Text style={styles.small}>Checkpoints are validated synthetic memory snapshots for this session. Closing or reloading the app clears them. They are not durable storage or cross-device recovery.</Text>
  </OnboardingScreen>;
}
