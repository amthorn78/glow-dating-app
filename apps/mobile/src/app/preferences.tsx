import { useState } from 'react';
import { router } from 'expo-router';
import { Pressable, Text, View } from 'react-native';
import { Button, styles } from '../components/ui';
import { ProfileOutcomeControl, ProfileScreen } from '../components/profile-controls';
import { useProfiles } from '../onboarding/context';
import { FIXTURE_PREFERENCE_POLICY } from '../profiles/policy';
import type { ProfileOutcome } from '../profiles/store';

export default function PreferencesScreen() {
  const { state, profiles } = useProfiles();
  const [outcome, setOutcome] = useState<ProfileOutcome>('success');
  const revision = state.preferencesDraftRevision;
  const dirty = JSON.stringify(state.preferencesDraft) !== JSON.stringify(state.preferences?.selections ?? []);
  const policyCurrent = state.policyVersion === FIXTURE_PREFERENCE_POLICY.version;
  function toggle(dimension: string, option: string) {
    const current = state.preferencesDraft.find(selection => selection.dimension === dimension)?.accepted_option_ids ?? [];
    const accepted_option_ids = current.includes(option) ? current.filter(id => id !== option) : [...current, option];
    const selections = state.preferencesDraft.filter(selection => selection.dimension !== dimension);
    if (accepted_option_ids.length) selections.push({ dimension, accepted_option_ids });
    profiles.editPreferencesDraft(selections, revision);
  }
  return <ProfileScreen title="A little about what fits." testID="screen-preferences">
    <Text style={styles.body}>These choices are private. Choose all the options that fit; they are not shown on your profile.</Text>
    <View style={styles.notice}>
      <Text style={styles.eyebrow}>PROVISIONAL PREVIEW CHOICES</Text>
      <Text style={styles.small}>These fictional examples let you try editing. Launch preferences and matching rules have not been selected.</Text>
      {!policyCurrent && <Text style={styles.error} accessibilityRole="alert">The preference choices have changed or are unavailable. Refresh before saving. Discovery remains unavailable.</Text>}
    </View>
    {FIXTURE_PREFERENCE_POLICY.dimensions.map(dimension => <View key={dimension.id} style={styles.group}>
      <Text style={styles.subtitle} accessibilityRole="header">{dimension.label}</Text>
      {dimension.options.map(option => {
        const checked = state.preferencesDraft.some(selection => selection.dimension === dimension.id && selection.accepted_option_ids.includes(option.id));
        return <Pressable key={option.id} testID={`pref-${dimension.id}-${option.id}`} accessibilityRole="checkbox" accessibilityLabel={option.label}
          accessibilityState={{ checked, disabled: state.busy || !policyCurrent }} aria-checked={checked} disabled={state.busy || !policyCurrent}
          onPress={() => toggle(dimension.id, option.id)} style={[styles.choice, checked && styles.choiceSelected]}>
          <Text style={styles.choiceText}>{checked ? '✓ ' : '○ '}{option.label}</Text>
        </Pressable>;
      })}
    </View>)}
    <Text style={styles.small} testID="preferences-draft-status">{dirty ? 'Unsaved edits' : state.preferences ? 'Matches your saved preferences' : 'No saved preferences yet'}</Text>
    <Button label="Save preferences" testID="preferences-save" disabled={state.busy || !policyCurrent} onPress={() => void profiles.savePreferences(revision, outcome)} />
    <Button label="Cancel edits" testID="preferences-cancel" secondary onPress={() => { profiles.cancelPreferencesEdit(revision); router.replace('/profile'); }} />
    <Button label="Leave and keep draft" testID="preferences-leave" secondary onPress={() => router.push('/profile')} />
    <Button label="Refresh saved details" testID="preferences-reload" secondary disabled={state.busy} onPress={() => void profiles.reload(outcome)} />
    <Text style={styles.small}>Saving preferences rechecks eligibility. It cannot create a match or approve discovery on its own.</Text>
    <ProfileOutcomeControl value={outcome} onChange={setOutcome} />
  </ProfileScreen>;
}
