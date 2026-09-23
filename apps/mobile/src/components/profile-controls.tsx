import { useState, type PropsWithChildren } from 'react';
import { Text, View } from 'react-native';
import { Button, Choice, Feedback, styles } from './ui';
import { useProfiles } from '../onboarding/context';
import { OnboardingScreen } from '../onboarding/shell';
import type { ProfileOutcome } from '../profiles/store';

export function ProfileScreen({ children, title, testID }: PropsWithChildren<{ title: string; testID: string }>) {
  const { state } = useProfiles();
  return <OnboardingScreen title={title} testID={testID}>
    <Feedback error={state.error} message={state.message} busy={state.busy} />
    {children}
  </OnboardingScreen>;
}

/** Saved lifecycle state and permission to disclose are separate facts. */
export function ProfileVisibility() {
  const { state } = useProfiles();
  const saved = state.profile?.visibility ?? 'incomplete';
  const blocked = saved === 'visible' && !state.canDiscover;
  return <View style={styles.group} testID="profile-effective-visibility">
    <Text style={styles.body}>Visibility: {blocked ? 'blocked' : saved}</Text>
    {blocked && <Text style={styles.small}>Your profile is currently unavailable to others. Wait for any current update, then review the remaining requirements.</Text>}
  </View>;
}

export function ProfileOutcomeControl({ value, onChange }: { value: ProfileOutcome; onChange: (value: ProfileOutcome) => void }) {
  const [expanded, setExpanded] = useState(false);
  const labels: Record<ProfileOutcome, string> = { success: 'Success', error: 'Temporary error', malformed: 'Invalid response', stale: 'Version conflict' };
  return <View style={styles.notice}>
    <Text style={styles.eyebrow}>SYNTHETIC TEST CONTROLS</Text>
    <Button secondary label={expanded ? 'Hide profile fixture outcomes' : 'Choose profile fixture outcome'} testID="profile-outcomes" onPress={() => setExpanded(!expanded)} />
    <Text style={styles.small}>Development only. Selected result: {labels[value]}.</Text>
    {expanded && (Object.keys(labels) as ProfileOutcome[]).map(outcome => <Choice key={outcome} label={`Profile fixture outcome: ${labels[outcome]}`}
      selected={outcome === value} onPress={() => onChange(outcome)} testID={`profile-outcome-${outcome}`} />)}
  </View>;
}
