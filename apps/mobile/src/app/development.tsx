import { router } from 'expo-router';
import { Text, View } from 'react-native';
import { Button, styles } from '../components/ui';
import { useOnboarding, useProfiles } from '../onboarding/context';
import { OnboardingScreen } from '../onboarding/shell';

export default function DevelopmentScreen() {
  const { state, store } = useOnboarding();
  const { profiles } = useProfiles();
  const scenarios = [
    ['new', 'New signed-out journey'], ['eligible', 'Eligible recommendation preview'], ['underage', 'Underage fixture'],
    ['unknown_policy', 'Unknown policy fixture'], ['stale_consent', 'Stale consent fixture'], ['withdrawn_consent', 'Withdrawn consent fixture'],
    ['suspended', 'Suspended account fixture'], ['deletion_pending', 'Deletion-pending fixture'],
  ] as const;
  return <OnboardingScreen title="Development scenarios" testID="screen-development">
    <Text style={styles.body}>These synthetic states are test controls, available only in the guarded development runtime. They do not create accounts, verify people, or grant production access.</Text>
    <Text style={styles.small}>Selecting a scenario replaces the current synthetic session and clears its private drafts. The eligible preview is a separate fixture, never a reward for unfinished onboarding.</Text>
    <View style={styles.group}>{scenarios.map(([name, label]) => <Button key={name} label={label} testID={`scenario-${name}`} secondary
      onPress={() => { store.scenario(name); router.replace('/'); }} />)}</View>
    {state.account?.state === 'active' && state.account.session_state === 'valid' && <View style={styles.notice}>
      <Text style={styles.eyebrow}>PROFILE SOURCE CHANGES</Text>
      <Text style={styles.small}>These test controls change current authority while retaining navigation and deliberate edits. They are not product controls.</Text>
      {(['profile', 'preferences', 'policy', 'media', 'reciprocal'] as const).map(change => <Button key={change}
        label={`Change synthetic ${change} source`} testID={`dev-${change}-change`} secondary onPress={() => profiles.developmentChange(change)} />)}
      {(['block_viewer', 'block_candidate', 'clear_blocks', 'viewer_preferences', 'restore_viewer_preferences', 'viewer_pause', 'viewer_resume', 'candidate_attribute'] as const).map(change => <Button key={change}
        label={`Change synthetic pair: ${change.replaceAll('_', ' ')}`} testID={`dev-pair-${change}`} secondary onPress={() => profiles.developmentPairChange(change)} />)}
      <Button label="Return to your profile" testID="dev-profile-return" secondary onPress={() => router.push('/profile')} />
    </View>}
    <Button label="Save session checkpoint" testID="checkpoint-save" secondary disabled={!state.account || state.account.session_state !== 'valid'} onPress={() => store.saveCheckpoint()} />
    <Button label="Restore session checkpoint" testID="checkpoint-restore" secondary disabled={!state.checkpointAvailable} onPress={() => { store.restoreCheckpoint(); router.replace('/'); }} />
    <Button label="Expire fixture session" testID="session-expire" secondary disabled={!state.account || state.account.session_state !== 'valid'} onPress={() => { store.expire(); router.replace('/'); }} />
    <Button label="Return to current step" testID="return-current" onPress={() => router.replace('/')} />
  </OnboardingScreen>;
}
