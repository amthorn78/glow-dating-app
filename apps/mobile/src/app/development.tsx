import { router } from 'expo-router';
import { Text, View } from 'react-native';
import { Button, styles } from '../components/ui';
import { useOnboarding } from '../onboarding/context';
import { OnboardingScreen } from '../onboarding/shell';

export default function DevelopmentScreen() {
  const { state, store } = useOnboarding();
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
    <Button label="Save session checkpoint" testID="checkpoint-save" secondary disabled={!state.account || state.account.session_state !== 'valid'} onPress={() => store.saveCheckpoint()} />
    <Button label="Restore session checkpoint" testID="checkpoint-restore" secondary disabled={!state.checkpointAvailable} onPress={() => { store.restoreCheckpoint(); router.replace('/'); }} />
    <Button label="Expire fixture session" testID="session-expire" secondary disabled={!state.account || state.account.session_state !== 'valid'} onPress={() => { store.expire(); router.replace('/'); }} />
    <Button label="Return to current step" testID="return-current" onPress={() => router.replace('/')} />
  </OnboardingScreen>;
}
