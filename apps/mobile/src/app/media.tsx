import { useEffect, useRef, useState } from 'react';
import { router } from 'expo-router';
import { Text, View } from 'react-native';
import { Button, Choice, Feedback, styles } from '../components/ui';
import { useMedia } from '../onboarding/context';
import { OnboardingScreen } from '../onboarding/shell';
import { pickPhoto } from '../media/picker';
import { FIXTURE_MEDIA_POLICY, syntheticSelection, type SyntheticImage } from '../media/policy';
import type { MediaOutcome } from '../media/fixture-adapter';

const stateLabels = {
  upload_pending: 'Upload pending', quarantined: 'Quarantined', review_pending: 'Review pending',
  approved: 'Approved', rejected: 'Rejected', removal_pending: 'Removal pending', removed: 'Removed',
} as const;
const selectionFixtures: ReadonlyArray<readonly [SyntheticImage, string]> = [
  ['valid', 'Valid synthetic PNG'], ['invalid', 'Invalid image bytes'], ['unsupported', 'Unsupported JPEG'],
  ['truncated', 'Truncated PNG'], ['oversize', 'Oversized bytes'], ['pixels', 'Excessive image dimensions'],
];

export default function MediaScreen() {
  const { state, media } = useMedia();
  const [expanded, setExpanded] = useState(false);
  const [outcome, setOutcome] = useState<MediaOutcome>('success');
  const [pickerPending, setPickerPending] = useState(false);
  const pickerSequence = useRef(0);
  const pickerAbort = useRef<AbortController | null>(null);
  useEffect(() => () => { pickerAbort.current?.abort(); }, [state.ownerKey, state.selectionRevision]);
  const approved = state.collection.items.filter(item => item.state === 'approved');
  async function choose() {
    const owner = state.ownerKey, revision = state.selectionRevision, sequence = ++pickerSequence.current;
    pickerAbort.current?.abort();
    const controller = new AbortController(); pickerAbort.current = controller;
    setPickerPending(true);
    try {
      const result = await pickPhoto(`picker-${sequence}`, controller.signal);
      if (result.kind === 'selected') media.select(result.selection, revision, owner);
      else media.selectionResult(result.kind, revision, owner);
    } finally { if (sequence === pickerSequence.current) setPickerPending(false); }
  }
  function cancelSelection() {
    pickerAbort.current?.abort();
    pickerSequence.current += 1; setPickerPending(false);
    media.selectionResult('cancelled', state.selectionRevision, state.ownerKey);
  }
  return <OnboardingScreen title="Your photos, kept private." testID="screen-media">
    <Feedback error={state.error} message={state.message} busy={state.busy} />
    <Text style={styles.body}>Photos stay private while uploading and awaiting review. Only approved photos can support a visible profile.</Text>
    <Text style={styles.small}>Development policy: PNG only, up to 1 MiB, 2048 pixels per side and {FIXTURE_MEDIA_POLICY.maxPhotos} current photos. These are provisional preview limits.</Text>
    <Text style={styles.small}>Private originals use a safe placeholder. This preview checks PNG structure, not decoded pixels or metadata removal. Provider processing and native file access remain unverified.</Text>
    <View style={styles.group} testID="media-owner-controls">
      <Button label="Choose a test photo" testID="media-picker" disabled={state.busy || pickerPending} onPress={() => void choose()} />
      <Text style={styles.small}>Use synthetic test files only. Browser PNG files can be read with a size bound. Native selection cannot upload until its bounded reader is verified.</Text>
      {(pickerPending || state.selection) && <Button label="Cancel selection" testID="media-selection-cancel" secondary onPress={cancelSelection} />}
      {state.selection && <View style={styles.notice} testID="media-selection">
        <Text style={styles.subtitle}>Private selection</Text>
        <Text style={styles.body}>{state.selection.name}</Text>
        <Text style={styles.small}>{state.selection.byteLength} encoded bytes. No upload has started.</Text>
        <Button label="Prepare private upload" testID="media-prepare" disabled={state.busy} onPress={() => void media.requestUpload(outcome)} />
      </View>}
    </View>
    {!state.collection.items.length && <Text style={styles.body} testID="media-empty">No photos yet. Choose a test photo to begin.</Text>}
    <View style={styles.group} testID="media-collection">
      {state.collection.items.map((item, index) => {
        const transport = state.transports.find(entry => entry.assetId === item.asset_id);
        const approvedIndex = approved.findIndex(entry => entry.asset_id === item.asset_id);
        return <View key={item.asset_id} style={styles.notice} testID={`media-item-${item.asset_id}`}>
          <Text style={styles.subtitle} accessibilityRole="header">Photo {index + 1}</Text>
          <Text style={styles.small}>Private photo placeholder</Text>
          <Text style={styles.body} accessibilityLiveRegion="polite" testID={`media-status-${item.asset_id}`}>{stateLabels[item.state]}</Text>
          {transport && <View style={styles.group}>
            <Text style={styles.small} testID={`media-transport-${item.asset_id}`}>Transfer: {transport.status}; attempt {transport.attempts} of {FIXTURE_MEDIA_POLICY.maxUploadAttempts}.</Text>
            {transport.status === 'uploading' && <Text style={styles.body} accessibilityRole="progressbar"
              accessibilityValue={{ min: 0, max: 100, now: transport.progress }} testID={`media-progress-${item.asset_id}`}>Upload progress: {transport.progress}%</Text>}
          </View>}
          {item.state === 'upload_pending' && <View style={styles.group}>
            <Button label={transport && transport.attempts > 0 ? `Retry photo ${index + 1} upload` : `Upload photo ${index + 1}`}
              testID={`media-upload-${item.asset_id}`} disabled={state.busy} onPress={() => void media.upload(item.asset_id, outcome)} />
            <Button label={`Cancel photo ${index + 1} upload`} testID={`media-cancel-${item.asset_id}`} secondary onPress={() => void media.cancel(item.asset_id)} />
          </View>}
          {transport?.status === 'expired' && <Text style={styles.small}>This grant has expired permanently. Remove this pending photo, then select it again to prepare a replacement.</Text>}
          {item.state === 'quarantined' && <Text style={styles.small}>Upload received. Processing and review must finish before this photo can be approved.</Text>}
          {item.state === 'review_pending' && <Text style={styles.small}>This photo is waiting for review and is unavailable to other people.</Text>}
          {item.state === 'rejected' && <Text style={styles.small}>This photo was not approved. Remove it, then choose another test photo.</Text>}
          {item.state === 'approved' && <View style={styles.group}>
            <Text style={styles.small} testID={`media-position-${item.asset_id}`}>Approved position {approvedIndex + 1}</Text>
            <Button label={`Move photo ${index + 1} earlier`} testID={`media-earlier-${item.asset_id}`} secondary disabled={state.busy || approvedIndex <= 0} onPress={() => void media.move(item.asset_id, -1, outcome)} />
            <Button label={`Move photo ${index + 1} later`} testID={`media-later-${item.asset_id}`} secondary disabled={state.busy || approvedIndex >= approved.length - 1} onPress={() => void media.move(item.asset_id, 1, outcome)} />
          </View>}
          {!['removal_pending', 'removed'].includes(item.state) && <Button label={`Remove photo ${index + 1}`} testID={`media-remove-${item.asset_id}`} secondary onPress={() => void media.remove(item.asset_id, outcome)} />}
          {item.state === 'removal_pending' && <Text style={styles.small}>Unavailable for delivery. Provider deletion is still pending. A failed or timed-out purge does not mean the bytes are deleted.</Text>}
          {item.state === 'removed' && <Text style={styles.small}>Synthetic provider purge confirmed. This fixture is not evidence of real storage deletion.</Text>}
        </View>;
      })}
    </View>
    <Button label="Refresh photo status" testID="media-reload" secondary disabled={state.busy} onPress={() => void media.reload(outcome)} />
    <Button label="Return to your profile" testID="media-profile" secondary onPress={() => router.push('/profile')} />
    <Text style={styles.small}>Work remains only in this session. Navigating away can retain pending work; signing out clears private presentation. A full app reload clears this fixture.</Text>
    <View style={styles.notice} testID="media-developer-controls">
      <Text style={styles.eyebrow}>SYNTHETIC DEVELOPER CONTROLS</Text>
      <Text style={styles.small}>These controls simulate picker permissions and separate provider, system and moderator actors. They are not owner approval or deletion permissions.</Text>
      <Button label={expanded ? 'Hide media fixture controls' : 'Show media fixture controls'} testID="media-fixtures" secondary onPress={() => setExpanded(!expanded)} />
      {expanded && <View style={styles.group}>
        {selectionFixtures.map(([kind, label]) => <Button key={kind} label={`Select fixture: ${label}`} testID={`media-select-${kind}`} secondary disabled={state.busy}
          onPress={() => media.select({ ...syntheticSelection(kind), selectionId: `fixture-${++pickerSequence.current}` })} />)}
        {(['denied', 'limited', 'cancelled', 'unsupported'] as const).map(result => <Button key={result} label={`Simulate picker: ${result}`}
          testID={`media-picker-${result}`} secondary onPress={() => media.selectionResult(result)} />)}
        {(['success', 'error', 'malformed', 'stale', 'expired', 'interrupted', 'wrong_object'] as const).map(result => <Choice key={result} label={`Media fixture outcome: ${result}`}
          testID={`media-outcome-${result}`} selected={outcome === result} onPress={() => setOutcome(result)} />)}
        <Button label="Advance synthetic clock past grant expiry" testID="media-clock-expire" secondary onPress={() => media.advanceClock(FIXTURE_MEDIA_POLICY.grantDurationMs + 1)} />
        <Button label="Invalidate synthetic media policy" testID="media-policy-change" secondary onPress={() => media.invalidatePolicy()} />
        {state.collection.items.map((item, index) => <View key={item.asset_id} style={styles.group} testID={`media-actors-${item.asset_id}`}>
          <Text style={styles.body}>Synthetic actor events for Photo {index + 1}</Text>
          {item.state === 'quarantined' && <Button label={`System: send Photo ${index + 1} to review`} testID={`media-review-${item.asset_id}`} secondary disabled={state.busy} onPress={() => void media.developerEvent(item.asset_id, 'review', outcome)} />}
          {item.state === 'review_pending' && <>
            <Button label={`Moderator: approve Photo ${index + 1}`} testID={`media-approve-${item.asset_id}`} secondary disabled={state.busy} onPress={() => void media.developerEvent(item.asset_id, 'approve', outcome)} />
            <Button label={`Moderator: reject Photo ${index + 1}`} testID={`media-reject-${item.asset_id}`} secondary disabled={state.busy} onPress={() => void media.developerEvent(item.asset_id, 'reject', outcome)} />
          </>}
          {item.state === 'approved' && <Button label={`Moderator: restrict Photo ${index + 1}`} testID={`media-restrict-${item.asset_id}`} secondary onPress={() => void media.developerEvent(item.asset_id, 'restrict_media', outcome)} />}
          {item.state === 'removal_pending' && <Button label={`Provider: retry or confirm Photo ${index + 1} purge`} testID={`media-purge-${item.asset_id}`} secondary disabled={state.busy} onPress={() => void media.developerEvent(item.asset_id, 'purged', outcome)} />}
        </View>)}
      </View>}
    </View>
  </OnboardingScreen>;
}
