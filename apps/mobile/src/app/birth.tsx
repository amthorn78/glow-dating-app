import { useState } from 'react';
import { router } from 'expo-router';
import { Text, View } from 'react-native';
import { Button, Choice, Field, styles } from '../components/ui';
import { useBirthDraft, useOnboarding } from '../onboarding/context';
import { OnboardingScreen } from '../onboarding/shell';
import type { BirthInput } from '../contracts/generated/gapp-api-v1';
import type { BirthOutcome } from '../onboarding/store';

export default function BirthScreen() {
  const { state, store } = useOnboarding();
  const { draft, setDraft, updateDraft, saveDraft } = useBirthDraft();
  const [outcome, setOutcome] = useState<BirthOutcome>('pending');
  const [showOutcomes, setShowOutcomes] = useState(false);
  function update(input: Partial<BirthInput>) {
    updateDraft(input);
  }
  async function save() {
    const generation = state.generation;
    const owner = store.getSnapshot();
    if (owner.generation !== generation || owner.account?.account_id !== state.account?.account_id) return;
    const request = saveDraft(outcome);
    if (!request) return;
    await request;
    const current = store.getSnapshot();
    if (current.generation === generation && !current.error && current.stage === 'remaining') router.replace('/remaining');
  }
  return <OnboardingScreen title="Your story starts privately." step="STEP 4 OF 4 · PRIVATE BIRTH INPUT" testID="screen-birth">
    <Text style={styles.body}>These facts are for your own chart request, never your public dating profile. Use fictional information in this preview. No Human Design calculation or place lookup is connected.</Text>
    <Field label="Private birth date" value={draft.birth_date} onChangeText={(birth_date) => update({ birth_date })} placeholder="YYYY-MM-DD" keyboardType="numbers-and-punctuation" maxLength={10} editable={!state.busy} testID="birth-date" />
    <Field label="Private birth place" value={draft.place_label} onChangeText={(place_label) => update({ place_label })} maxLength={200} editable={!state.busy} testID="birth-place" hint="Enter the civil place as known. No device location is used." />
    <View style={styles.group} accessibilityLabel="Birth time precision">
      <Text style={styles.fieldLabel}>How well do you know the time?</Text>
      {(['known', 'approximate', 'unknown'] as const).map((precision) => <Choice key={precision}
        label={precision === 'known' ? 'Known birth time' : precision === 'approximate' ? 'Approximate birth time' : 'Unknown birth time'}
        selected={draft.time_precision === precision} disabled={state.busy} testID={`time-${precision}`}
        onPress={() => update({ time_precision: precision })} />)}
    </View>
    {draft.time_precision !== 'unknown' && <Field label="Private local birth time" value={draft.local_time ?? ''} onChangeText={(local_time) => update({ local_time })}
      placeholder="HH:MM:SS" maxLength={8} keyboardType="numbers-and-punctuation" editable={!state.busy} testID="birth-time" hint="24-hour local civil time with seconds: HH:MM:SS. Approximate stays approximate." />}
    <View style={styles.notice}>
      <Text style={styles.body}>{draft.time_precision === 'unknown' ? 'Unknown time is kept empty. We never substitute noon.' : 'Your entered time and precision are preserved.'}</Text>
      <Text style={styles.small}>Historical timezone: unresolved. The device timezone is not used. A completed form does not create a chart or engine identity.</Text>
    </View>
    {state.birth && <Text style={styles.body}>Current resolution: {state.birth.resolution}. Changes invalidate earlier mapping assumptions.</Text>}
    <Button label="Save private fixture input" testID="birth-submit" disabled={state.busy} onPress={() => void save()} />
    <Button label="Back to eligibility" testID="birth-back" secondary disabled={state.busy} onPress={() => router.push('/eligibility')} />
    <Button label="Cancel changes" testID="birth-cancel" secondary disabled={state.busy} onPress={() => { setDraft(state.birth?.input ?? { birth_date: '', local_time: null, time_precision: 'unknown', place_label: '', timezone_name: null, timezone_provenance: null }); router.replace('/'); }} />
    <View style={styles.notice}>
      <Button label={showOutcomes ? 'Hide resolution fixtures' : 'Choose resolution fixture'} testID="birth-outcomes" secondary onPress={() => setShowOutcomes(!showOutcomes)} />
      <Text style={styles.small}>Synthetic resolution outcome: {outcome}. There is no resolved chart option.</Text>
      {showOutcomes && (['pending', 'ambiguous', 'unavailable', 'unsupported'] as const).map((value) => <Choice key={value} label={`Resolution fixture: ${value}`} testID={`resolution-${value}`} selected={outcome === value} onPress={() => setOutcome(value)} />)}
    </View>
  </OnboardingScreen>;
}
