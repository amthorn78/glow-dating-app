import { useState } from 'react';
import { router } from 'expo-router';
import { Text, View } from 'react-native';
import { Button, styles } from '../components/ui';
import { ProfileOutcomeControl, ProfileScreen, ProfileVisibility } from '../components/profile-controls';
import { useOnboarding, useProfiles } from '../onboarding/context';
import { canAccessRoute } from '../onboarding/routes';
import type { ProfileOutcome } from '../profiles/store';

const requirementLabels: Readonly<Record<string, string>> = {
  'Current reciprocal preference evidence': 'A fresh check of both people’s preferences',
  'A resolved preference policy': 'Confirmed preference rules',
  'A resolved chart': 'Resolved Human Design inputs',
};

export default function ProfileScreenRoute() {
  const { state, profiles } = useProfiles();
  const { state: onboarding } = useOnboarding();
  const [outcome, setOutcome] = useState<ProfileOutcome>('success');
  const profile = state.profile;
  return <ProfileScreen title="Your profile, at your pace." testID="screen-profile">
    <View style={styles.notice} testID="profile-status">
      <Text style={styles.subtitle} accessibilityRole="header">{profile?.display_name ?? 'Start your profile'}</Text>
      <ProfileVisibility />
      <Text style={styles.body}>{profile?.summary || 'Your biography is still empty.'}</Text>
      <Text style={styles.small}>{profile ? 'These are your saved profile details.' : 'No profile has been saved yet.'}</Text>
    </View>
    <View style={styles.notice} testID="preferences-status">
      <Text style={styles.subtitle} accessibilityRole="header">Your private preferences</Text>
      <Text style={styles.body}>{state.preferences ? 'Saved for this session.' : 'Not saved yet.'}</Text>
      <Text style={styles.small}>Preferences are never included in your public profile.</Text>
    </View>
    <View style={styles.group} testID="profile-requirements">
      <Text style={styles.subtitle} accessibilityRole="header">{state.requirements.length ? 'Still needed' : 'Profile requirements met in this preview'}</Text>
      {state.requirements.map((requirement) => <Text key={requirement} style={styles.body}>{requirementLabels[requirement] ?? requirement}</Text>)}
      <Text style={styles.small}>Writing your profile does not approve photos or resolve Human Design inputs. An owner preview does not make your profile visible.</Text>
    </View>
    <Button label={profile ? 'Edit profile' : 'Create profile'} testID="profile-edit" onPress={() => router.push('/profile-edit')} />
    <Button label="Manage your photos" testID="profile-media" secondary onPress={() => router.push('/media')} />
    <Button label="Edit private preferences" testID="preferences-edit" secondary onPress={() => router.push('/preferences')} />
    <Button label="Preview saved profile" testID="profile-preview" secondary onPress={() => router.push('/profile-preview')} />
    {profile?.visibility === 'visible' && <Button label="Pause profile" testID="profile-pause" secondary onPress={() => void profiles.setVisibility('pause', outcome)} />}
    {profile?.visibility === 'paused' && <Button label="Resume profile" testID="profile-resume" disabled={state.busy} onPress={() => void profiles.setVisibility('resume', outcome)} />}
    {profile?.visibility === 'paused' && <Text style={styles.body}>Your profile is paused. Editing keeps it paused. Resuming checks your current eligibility and does not restore past contact permissions.</Text>}
    {state.canDiscover && <Button label="Open recommendation preview" testID="profile-discovery" secondary onPress={() => router.push('/recommended')} />}
    <Button label="Your matches" testID="open-matches" secondary onPress={() => router.push('/matches')} />
    {canAccessRoute('/birth', onboarding) && <Button label="Edit private birth input" testID="profile-birth" secondary onPress={() => router.push('/birth')} />}
    <Button label="Review eligibility and consent" testID="profile-eligibility" secondary onPress={() => router.push('/eligibility')} />
    <Button label="Refresh saved details" testID="profile-reload" secondary disabled={state.busy} onPress={() => void profiles.reload(outcome)} />
    <Text style={styles.small}>Saved details and unfinished edits remain only for this session. Reloading or closing the app clears them.</Text>
    <ProfileOutcomeControl value={outcome} onChange={setOutcome} />
  </ProfileScreen>;
}
