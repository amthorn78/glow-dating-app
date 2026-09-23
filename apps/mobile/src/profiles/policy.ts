import type { CandidateProfile, OwnPreferences, OwnProfile, PreferenceSelection } from '../contracts/generated/gapp-api-v1.ts';
import { parseAppIntent, parseAppResponse } from '../contracts/production.ts';

export type PreferencePolicy = Readonly<{ version: string; dimensions: readonly Readonly<{
  id: string; label: string; options: readonly Readonly<{ id: string; label: string }>[];
}>[] }>;

/** Test vocabulary only. This selects no launch market, gender or orientation taxonomy. */
export const FIXTURE_PREFERENCE_POLICY: PreferencePolicy = Object.freeze({
  version: 'development-preferences-1',
  dimensions: Object.freeze([Object.freeze({ id: 'demo_connection', label: 'Demonstration connection preference',
    options: Object.freeze([Object.freeze({ id: 'demo_a', label: 'Demo option A' }), Object.freeze({ id: 'demo_b', label: 'Demo option B' })]),
  })]),
});

export type ProfileAuthority = Readonly<{
  ownerId: string | null; generation: number; accountVersion: number;
  accountState: string; sessionState: string; adult: boolean; consentCurrent: boolean;
  sourceRevision: number; consentRevision: string;
}>;
export type FictionalEvidence = Readonly<{ media: boolean; chart: boolean; moderation: boolean;
  reciprocalPreferencesVersion: number | null; reciprocalPolicyVersion: string | null }>;
export const EMPTY_EVIDENCE: FictionalEvidence = Object.freeze({ media: false, chart: false,
  moderation: false, reciprocalPreferencesVersion: null, reciprocalPolicyVersion: null });
export const PROFILE_IDS = Object.freeze({
  alex: '66666666-6666-4666-8666-666666666666', sam: '77777777-7777-4777-8777-777777777777',
});
export const FIXTURE_MEDIA_ID = '88888888-8888-4888-8888-888888888888';
export const PROFILE_REQUEST_ID = '99999999-9999-4999-8999-999999999999';
export const activeOwner = (authority: ProfileAuthority): boolean => authority.ownerId !== null &&
  authority.accountState === 'active' && authority.sessionState === 'valid';

export function selectionsValid(selections: readonly PreferenceSelection[], policy: PreferencePolicy | null): boolean {
  if (!policy) return false;
  try {
    parseAppIntent({ operation: 'preferences', meta: { idempotency_key: 'validation', expected_version: 0 },
      policy_version: policy.version, selections });
  } catch { return false; }
  return selections.every(selection => {
    const dimension = policy.dimensions.find(item => item.id === selection.dimension);
    return dimension !== undefined && selection.accepted_option_ids.every(id => dimension.options.some(option => option.id === id));
  });
}

/** Wire decoding never trims/normalizes text. Canonical command fields have explicit order. */
export function canonicalSelections(selections: readonly PreferenceSelection[]): unknown {
  // Collections retain their submitted order: the contract does not authorize set sorting.
  return selections.map(selection => [selection.dimension, [...selection.accepted_option_ids]]);
}

export function requirements(profile: OwnProfile | null, preferences: OwnPreferences | null,
  authority: ProfileAuthority, policy: PreferencePolicy | null, evidence: FictionalEvidence): string[] {
  const missing: string[] = [];
  if (!activeOwner(authority)) missing.push('A current verified account');
  if (!authority.adult) missing.push('Current adult eligibility');
  if (!authority.consentCurrent) missing.push('Current consent');
  if (!profile) missing.push('A saved profile');
  if (!profile?.summary) missing.push('A biography');
  if (!policy) missing.push('A resolved preference policy');
  if (!preferences || preferences.policy_version !== policy?.version || !selectionsValid(preferences.selections, policy) ||
      !policy?.dimensions.every(dimension => preferences.selections.some(selection => selection.dimension === dimension.id && selection.accepted_option_ids.length > 0))) {
    missing.push('Preferences for the current policy');
  }
  if (!evidence.media || !profile?.media_ids.length) missing.push('Approved photos');
  if (!evidence.chart) missing.push('A resolved chart');
  if (!evidence.moderation) missing.push('Profile review');
  if (!preferences || evidence.reciprocalPreferencesVersion !== preferences.version ||
      evidence.reciprocalPolicyVersion !== policy?.version) missing.push('Current reciprocal preference evidence');
  return missing;
}

/** Explicit allowlist. This function does not independently authorize disclosure. */
export function projectCandidate(profile: OwnProfile, deliveryRefs: string[] = []): CandidateProfile {
  const candidate: CandidateProfile = { profile_id: profile.profile_id, display_name: profile.display_name,
    age: 36, summary: profile.summary, media_delivery_refs: [...deliveryRefs], compatibility: { status: 'unavailable' } };
  // The fictional media reference is never a live grant or provider URL.
  const value = parseAppResponse({ contract_version: 'gapp-api-v1', request_id: PROFILE_REQUEST_ID,
    data: { kind: 'recommendations', batch_id: PROFILE_REQUEST_ID, version: 1,
      state: 'ready', expires_at: '2026-09-23T13:00:00Z', items: [candidate], next_cursor: null } });
  if (value.data.kind !== 'recommendations') throw new Error('Invalid candidate projection.');
  return candidate;
}
