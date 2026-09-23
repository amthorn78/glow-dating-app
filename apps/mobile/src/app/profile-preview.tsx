import { router } from 'expo-router';
import { Text, View } from 'react-native';
import { Button, styles } from '../components/ui';
import { ProfileScreen, ProfileVisibility } from '../components/profile-controls';
import { useProfiles } from '../onboarding/context';

export default function ProfilePreviewScreen() {
  const { state, profiles } = useProfiles();
  const candidate = profiles.candidatePreview();
  return <ProfileScreen title="Your saved profile preview." testID="screen-profile-preview">
    <Text style={styles.body}>This preview is for you. It shows saved details, not unfinished edits, and does not make your profile public.</Text>
    {state.profile ? <View style={styles.notice} testID="owner-preview">
      <Text style={styles.subtitle} accessibilityRole="header">{state.profile.display_name}</Text>
      <Text style={styles.body}>{state.profile.summary || 'Your biography is still empty.'}</Text>
      <ProfileVisibility />
      <Text style={styles.small}>Photos are a separate step.</Text>
    </View> : <Text style={styles.body}>Save a profile to see your owner preview.</Text>}
    {candidate ? <View style={styles.notice} testID="candidate-preview">
      <Text style={styles.eyebrow}>FICTIONAL ELIGIBLE VIEWER PREVIEW</Text>
      <Text style={styles.subtitle} accessibilityRole="header">{candidate.display_name}, {candidate.age}</Text>
      <Text style={styles.body}>{candidate.summary}</Text>
      <Text style={styles.small}>Compatibility: {candidate.compatibility.status}. No Human Design result has been calculated.</Text>
      <Text style={styles.small}>Public fields only. Photos and eligibility are synthetic examples.</Text>
    </View> : <Text style={styles.body} testID="candidate-unavailable">An eligible viewer preview is unavailable in your current state.</Text>}
    <Button label="Back to your profile" testID="preview-back" onPress={() => router.replace('/profile')} />
  </ProfileScreen>;
}
