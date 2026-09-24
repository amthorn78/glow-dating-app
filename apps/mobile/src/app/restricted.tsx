import { router } from 'expo-router';
import { Text } from 'react-native';
import { Button, styles } from '../components/ui';
import { useOnboarding } from '../onboarding/context';
import { OnboardingScreen } from '../onboarding/shell';
import { canAccessRoute } from '../onboarding/routes';

export default function RestrictedScreen() {
  const { state } = useOnboarding();
  return <OnboardingScreen title="This journey is paused." testID="screen-restricted">
    <Text style={styles.body}>This fixture account cannot continue to discovery. Restricted, suspended and deletion states do not grant discovery access, and missing eligibility information never counts as approval.</Text>
    {state.account?.state === 'active' && <Button label="Review eligibility" testID="restricted-review" secondary onPress={() => router.replace('/eligibility')} />}
    {canAccessRoute('/matches', state) && <>
      <Text style={styles.body}>You can still end an existing connection. Profile details, discovery and messaging remain unavailable while your account is restricted.</Text>
      <Button label="Your matches" testID="open-matches" secondary onPress={() => router.push('/matches')} />
    </>}
    <Text style={styles.small}>This preview does not implement moderation appeals or a live support service.</Text>
  </OnboardingScreen>;
}
