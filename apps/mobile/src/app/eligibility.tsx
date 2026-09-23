import { useState } from 'react';
import { router } from 'expo-router';
import { Pressable, Text, View } from 'react-native';
import { Button, Field, styles } from '../components/ui';
import { useOnboarding } from '../onboarding/context';
import { OnboardingScreen } from '../onboarding/shell';
import { FIXTURE_POLICY } from '../onboarding/store';

export default function EligibilityScreen() {
  const { state } = useOnboarding();
  const owner = `${state.account?.account_id ?? 'none'}:${state.account?.session_state ?? 'none'}:${state.generation}`;
  // Reset only private form state when scenarios/accounts change. The navigator
  // and signed-out recovery form retain their own independent lifetimes.
  return <EligibilityForm key={owner} />;
}

function EligibilityForm() {
  const { state, store } = useOnboarding();
  const consentSource = `${state.consent.version}:${state.consent.state}:${state.consent.policy_version}`;
  const currentAccepted = state.consent.state === 'accepted' && state.consent.policy_version === FIXTURE_POLICY.version;
  const [dateField, setDateField] = useState({ source: state.adultBirthDate, value: state.adultBirthDate ?? '' });
  const [consentField, setConsentField] = useState({ source: consentSource, value: currentAccepted });
  // The stack can retain this screen. Reconcile each authoritative field before
  // rendering children, preserving local edits to the other unchanged field.
  const date = dateField.source === state.adultBirthDate ? dateField.value : state.adultBirthDate ?? '';
  const accepted = consentField.source === consentSource ? consentField.value : currentAccepted;
  if (dateField.source !== state.adultBirthDate) setDateField({ source: state.adultBirthDate, value: date });
  if (consentField.source !== consentSource) setConsentField({ source: consentSource, value: accepted });
  const setDate = (value: string) => { if (isCurrentOwner()) setDateField({ source: state.adultBirthDate, value }); };
  const setAccepted = (value: boolean) => { if (isCurrentOwner()) setConsentField({ source: consentSource, value }); };
  function isCurrentOwner() {
    const current = store.getSnapshot();
    return current.generation === state.generation && current.account?.account_id === state.account?.account_id &&
      current.birthDraftRevision === state.birthDraftRevision && current.consent.version === state.consent.version &&
      current.account?.state === 'active' && current.account.session_state === 'valid';
  }
  function continueOnboarding() {
    if (!isCurrentOwner()) return;
    store.setAdultDate(date);
    if (store.getSnapshot().error) return;
    store.setConsent(accepted);
    if (store.getSnapshot().error) return;
    router.replace('/');
  }
  return <OnboardingScreen title="A clear start, together." step="STEP 3 OF 4 · ELIGIBILITY AND CONSENT" testID="screen-eligibility">
    <Text style={styles.body}>Glow is for adults. This preview checks age 18 or older against 23 September 2026, using March 1 for leap-day birthdays in non-leap years. Your date stays private.</Text>
    <Text style={styles.small}>The development policy is not an approved launch rule. Geography, final terms, privacy information and consent wording remain an owner decision under A05.</Text>
    <Field label="Eligibility birth date" value={date} onChangeText={setDate} placeholder="YYYY-MM-DD" keyboardType="numbers-and-punctuation" maxLength={10} hint="Use a fictional civil date. Format: YYYY-MM-DD." testID="adult-date" />
    <View style={styles.notice}>
      <Text style={styles.subtitle} accessibilityRole="header">Development consent material</Text>
      <Text style={styles.body}>For this synthetic journey only: allow the fixture to retain your fictional account and private birth input in memory while the preview is open. No chart is calculated or shared. Logging out clears the session.</Text>
      <Text style={styles.small}>This material demonstrates versioned consent. It is not the public Terms of Service or Privacy Policy.</Text>
      <Pressable accessibilityRole="checkbox" accessibilityLabel="Accept development consent" accessibilityState={{ checked: accepted }} aria-checked={accepted} testID="consent-checkbox"
        onPress={() => setAccepted(!accepted)} style={styles.choice}>
        <Text style={styles.choiceText}>{accepted ? '☑ ' : '☐ '}I accept this development consent for fictional information.</Text>
      </Pressable>
    </View>
    <Text style={styles.small}>Current age check: {state.adult}. Consent: {state.consent.state}. Discovery stays unavailable until every requirement is met.</Text>
    <Button label="Save eligibility and continue" testID="eligibility-submit" onPress={continueOnboarding} />
    <Button label="Withdraw development consent" testID="consent-withdraw" secondary onPress={() => { if (!isCurrentOwner()) return; setAccepted(false); store.setConsent(false); }} />
    <Button label="Save session checkpoint" testID="checkpoint-save" secondary onPress={() => store.saveCheckpoint()} />
  </OnboardingScreen>;
}
