import { useState } from 'react';
import { router } from 'expo-router';
import { Text } from 'react-native';
import { Button, Field, styles } from '../components/ui';
import { ProfileOutcomeControl, ProfileScreen } from '../components/profile-controls';
import { useProfiles } from '../onboarding/context';
import type { ProfileOutcome } from '../profiles/store';

export default function ProfileEditScreen() {
  const { state, profiles } = useProfiles();
  const [outcome, setOutcome] = useState<ProfileOutcome>('success');
  const { profileDraft: draft, profileDraftRevision: revision } = state;
  const dirty = draft.display_name !== (state.profile?.display_name ?? '') || draft.summary !== (state.profile?.summary ?? '');
  return <ProfileScreen title="Tell a little of your story." testID="screen-profile-edit">
    <Text style={styles.body}>Choose the name and biography you would like to share. You can leave your biography empty and come back later.</Text>
    <Field label="Display name" hint="Required. Up to 80 characters." testID="profile-name" value={draft.display_name}
      editable={!state.busy} onChangeText={display_name => profiles.editProfileDraft({ display_name }, revision)} />
    <Field label="Biography" hint="Up to 500 characters. A visible profile needs a nonblank biography." testID="profile-summary" value={draft.summary}
      multiline style={[styles.input, { minHeight: 144, textAlignVertical: 'top' }]} editable={!state.busy}
      onChangeText={summary => profiles.editProfileDraft({ summary }, revision)} />
    <Text style={styles.small} testID="profile-draft-status">{dirty ? 'Unsaved edits' : state.profile ? 'Matches your saved profile' : 'No saved profile yet'}</Text>
    <Button label="Save profile" testID="profile-save" disabled={state.busy} onPress={() => void profiles.saveProfile(revision, outcome)} />
    <Button label="Refresh saved details" testID="profile-edit-reload" secondary disabled={state.busy} onPress={() => void profiles.reload(outcome)} />
    <Button label="Cancel edits" testID="profile-cancel" secondary onPress={() => { profiles.cancelProfileEdit(revision); router.replace('/profile'); }} />
    <Button label="Leave and keep draft" testID="profile-leave" secondary onPress={() => router.push('/profile')} />
    <Text style={styles.small}>Leaving keeps unfinished edits for this session. Cancel returns to the latest saved details. Saving does not change photos or private preferences.</Text>
    <ProfileOutcomeControl value={outcome} onChange={setOutcome} />
  </ProfileScreen>;
}
