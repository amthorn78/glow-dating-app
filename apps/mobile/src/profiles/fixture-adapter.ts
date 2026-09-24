import type { MediaCollection, OwnPreferences, OwnProfile, PreferencesIntent, ProfileIntent, VisibilityIntent } from '../contracts/generated/gapp-api-v1.ts';
import { parseAppIntent, parseAppResponse } from '../contracts/production.ts';
import { activeOwner, canonicalSelections, EMPTY_EVIDENCE, FIXTURE_MEDIA_ID, FIXTURE_PREFERENCE_POLICY,
  PROFILE_IDS, PROFILE_REQUEST_ID, requirements, selectionsValid,
  type FictionalEvidence, type PreferencePolicy, type ProfileAuthority } from './policy.ts';

export type ProfileOutcome = 'success' | 'error' | 'malformed' | 'stale';
export type ProfileContext = Readonly<{ ownerId: string; generation: number; authorityRevision: number; profileId: string }>;
export type ProfileRecords = { profile: OwnProfile | null; preferences: OwnPreferences | null };
export type DevelopmentChange = 'profile' | 'preferences' | 'policy' | 'media' | 'reciprocal';
export type FixtureProfileState = ProfileRecords & { policy: PreferencePolicy | null; evidence: FictionalEvidence };
export class ProfileFailure extends Error {
  readonly code: 'invalid_request' | 'unauthenticated' | 'forbidden' | 'state_conflict' | 'stale_version' |
    'idempotency_conflict' | 'policy_unresolved' | 'provider_unavailable';
  constructor(code: ProfileFailure['code']) {
    super(({ invalid_request: 'Check the profile or preference fields.', unauthenticated: 'Sign in again to continue.',
      forbidden: 'This action is unavailable for the current account.', state_conflict: 'This action is unavailable in the current state.',
      stale_version: 'The saved information changed. Reload current values, review your draft, then save again.',
      idempotency_conflict: 'This request changed during retry. Review your draft and save again.',
      policy_unresolved: 'The current preference policy is unavailable. Your profile cannot become visible.',
      provider_unavailable: 'The preview could not save. Your draft is kept; try again.' })[code]);
    this.name = 'ProfileFailure';
    this.code = code;
  }
}

/** Local fixture port using existing logical DTOs; no routes, credentials or production protocol. */
export interface ProfileAdapter {
  readonly kind: 'fixture';
  synchronize(authority: ProfileAuthority): void;
  inspect(): FixtureProfileState;
  context(): ProfileContext;
  read(context: ProfileContext, outcome?: ProfileOutcome): Promise<ProfileRecords>;
  saveProfile(context: ProfileContext, intent: ProfileIntent, outcome?: ProfileOutcome): Promise<OwnProfile>;
  savePreferences(context: ProfileContext, intent: PreferencesIntent, outcome?: ProfileOutcome): Promise<OwnPreferences>;
  visibility(context: ProfileContext, intent: VisibilityIntent, outcome?: ProfileOutcome): Promise<OwnProfile>;
  acknowledge(context: ProfileContext, result: OwnProfile | OwnPreferences): void;
  cancelPending(): void;
  synchronizeMedia(collection: MediaCollection): void;
  seedEligible(): void;
  developmentChange(change: DevelopmentChange): void;
}
const copy = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
const blankAuthority = (): ProfileAuthority => ({ ownerId: null, generation: 0, accountVersion: 0,
  accountState: 'none', sessionState: 'none', adult: false, consentCurrent: false, sourceRevision: 0, consentRevision: 'none' });

export function createProfileAdapter(options: { isDevelopment: boolean; mode: string | undefined; pause?: () => Promise<void> }): ProfileAdapter {
  if (!options.isDevelopment || options.mode !== 'fixture') throw new Error('Profiles require the explicit development fixture runtime.');
  const pause = options.pause ?? (() => Promise.resolve());
  let authority = blankAuthority(), authorityRevision = 0, epoch = 0;
  let state: FixtureProfileState = { profile: null, preferences: null, policy: FIXTURE_PREFERENCE_POLICY, evidence: EMPTY_EVIDENCE };
  type Receipt = { canonical: string; result: OwnProfile | OwnPreferences };
  const receipts = new Map<string, Receipt>();
  let staged: { state: FixtureProfileState; receiptKey: string; receipt: Receipt } | null = null;
  const profileId = () => authority.ownerId === '11111111-1111-4111-8111-111111111111' ? PROFILE_IDS.alex : PROFILE_IDS.sam;
  const records = (): ProfileRecords => ({ profile: copy(state.profile), preferences: copy(state.preferences) });
  const check = (context: ProfileContext) => {
    if (!activeOwner(authority)) throw new ProfileFailure('unauthenticated');
    if (context.ownerId !== authority.ownerId || context.generation !== authority.generation || context.profileId !== profileId()) throw new ProfileFailure('forbidden');
    if (context.authorityRevision !== authorityRevision) throw new ProfileFailure('stale_version');
  };
  const delay = async (context: ProfileContext, outcome: ProfileOutcome) => {
    check(context);
    const started = epoch;
    await pause();
    if (epoch !== started) throw new ProfileFailure('stale_version');
    check(context);
    if (outcome === 'error') throw new ProfileFailure('provider_unavailable');
    if (outcome === 'stale') throw new ProfileFailure('stale_version');
  };
  const validateProjection = (result: OwnProfile | OwnPreferences) => {
    parseAppResponse({ contract_version: 'gapp-api-v1', request_id: PROFILE_REQUEST_ID, data: result });
  };
  const resultFor = <T extends OwnProfile | OwnPreferences>(result: T, outcome: ProfileOutcome): T =>
    outcome === 'malformed' ? { ...copy(result), private_email: 'synthetic' } as T : copy(result);
  const prepare = <T extends OwnProfile | OwnPreferences>(context: ProfileContext, intent: ProfileIntent | PreferencesIntent | VisibilityIntent,
    canonical: string, next: FixtureProfileState, result: T, outcome: ProfileOutcome): T => {
    check(context);
    if (staged) throw new ProfileFailure('state_conflict');
    validateProjection(result);
    const receiptKey = `${context.ownerId}:${context.generation}:${intent.operation}:${context.profileId}:${intent.meta.idempotency_key}`;
    staged = { state: copy(next), receiptKey, receipt: { canonical, result: copy(result) } };
    return resultFor(result, outcome);
  };
  const replay = (context: ProfileContext, intent: ProfileIntent | PreferencesIntent | VisibilityIntent, canonical: string) => {
    parseAppIntent(intent);
    check(context);
    const key = `${context.ownerId}:${context.generation}:${intent.operation}:${context.profileId}:${intent.meta.idempotency_key}`;
    const prior = receipts.get(key);
    if (!prior) return null;
    if (prior.canonical !== canonical) throw new ProfileFailure('idempotency_conflict');
    const current = prior.result.kind === 'own_profile' ? state.profile : state.preferences;
    // A previous receipt is not a grant to recreate a now-stale projection or transition.
    if (JSON.stringify(current) !== JSON.stringify(prior.result)) throw new ProfileFailure('stale_version');
    return copy(prior.result);
  };
  const eligibility = (next: FixtureProfileState) => requirements(next.profile, next.preferences, authority, next.policy, next.evidence).length === 0;
  const retract = () => {
    if (state.profile?.visibility === 'visible' && !eligibility(state)) {
      state.profile = { ...state.profile, version: state.profile.version + 1, visibility: 'incomplete' };
    }
  };
  const adapter: ProfileAdapter = {
    kind: 'fixture',
    synchronize(next) {
      if (JSON.stringify(next) === JSON.stringify(authority)) return;
      adapter.cancelPending(); authorityRevision += 1;
      if (next.ownerId !== authority.ownerId || next.generation !== authority.generation) {
        state = { profile: null, preferences: null, policy: FIXTURE_PREFERENCE_POLICY, evidence: EMPTY_EVIDENCE }; receipts.clear();
      } else if (next.sourceRevision !== authority.sourceRevision) {
        // Any accepted/corrected birth facts revoke the fictional chart provenance.
        state.evidence = { ...state.evidence, chart: false };
      }
      authority = copy(next);
      if (state.profile && ['incomplete', 'visible', 'paused', 'restricted'].includes(state.profile.visibility) &&
          ['deletion_pending', 'deleted'].includes(next.accountState)) {
        state.profile = { ...state.profile, version: state.profile.version + 1, visibility: 'removed' };
      }
      // F01 restriction revokes access without inventing an unlisted F04 transition.
      // Source eligibility changes deny projection independently of saved visibility.
    },
    inspect: () => copy(state),
    context: () => {
      if (!activeOwner(authority)) throw new ProfileFailure('unauthenticated');
      return { ownerId: authority.ownerId!, generation: authority.generation, authorityRevision, profileId: profileId() };
    },
    async read(context, outcome = 'success') {
      context = copy(context);
      await delay(context, outcome);
      const result = records();
      if (outcome === 'malformed') {
        // Absence is a valid read, so return an invalid projection even before
        // profile creation. This corrupts only the response, never saved state.
        result.profile = result.profile ? resultFor(result.profile, outcome) : { kind: 'own_profile' } as OwnProfile;
      }
      return result;
    },
    async saveProfile(context, intent, outcome = 'success') {
      if (intent.operation !== 'profile') throw new ProfileFailure('invalid_request');
      parseAppIntent(intent);
      intent = copy(intent); context = copy(context);
      await delay(context, outcome);
      const canonical = JSON.stringify([intent.operation, intent.meta.expected_version, intent.display_name, intent.summary]);
      const previous = replay(context, intent, canonical);
      if (previous) return resultFor(previous as OwnProfile, outcome);
      if (intent.meta.expected_version !== (state.profile?.version ?? 0)) throw new ProfileFailure('stale_version');
      if (state.profile && !['incomplete', 'visible', 'paused'].includes(state.profile.visibility)) throw new ProfileFailure('state_conflict');
      const profile: OwnProfile = { kind: 'own_profile', profile_id: profileId(), version: (state.profile?.version ?? 0) + 1,
        display_name: intent.display_name, summary: intent.summary, visibility: state.profile?.visibility ?? 'incomplete', media_ids: [...state.profile?.media_ids ?? []] };
      const next = { ...state, profile };
      if (profile.visibility !== 'paused') profile.visibility = eligibility(next) ? 'visible' : 'incomplete';
      return prepare(context, intent, canonical, next, profile, outcome);
    },
    async savePreferences(context, intent, outcome = 'success') {
      if (intent.operation !== 'preferences') throw new ProfileFailure('invalid_request');
      parseAppIntent(intent);
      intent = copy(intent); context = copy(context);
      await delay(context, outcome);
      const canonical = JSON.stringify([intent.operation, intent.meta.expected_version, intent.policy_version, canonicalSelections(intent.selections)]);
      const previous = replay(context, intent, canonical);
      if (previous) return resultFor(previous as OwnPreferences, outcome);
      if (!state.policy || intent.policy_version !== state.policy.version) throw new ProfileFailure('policy_unresolved');
      if (!selectionsValid(intent.selections, state.policy)) throw new ProfileFailure('invalid_request');
      if (intent.meta.expected_version !== (state.preferences?.version ?? 0)) throw new ProfileFailure('stale_version');
      const preferences: OwnPreferences = { kind: 'own_preferences', version: (state.preferences?.version ?? 0) + 1,
        policy_version: intent.policy_version, selections: copy(intent.selections) };
      const next = { ...state, preferences, evidence: { ...state.evidence, reciprocalPreferencesVersion: null, reciprocalPolicyVersion: null } };
      if (next.profile?.visibility === 'visible' && !eligibility(next)) next.profile = { ...next.profile, version: next.profile.version + 1, visibility: 'incomplete' };
      return prepare(context, intent, canonical, next, preferences, outcome);
    },
    async visibility(context, intent, outcome = 'success') {
      if (intent.operation !== 'visibility') throw new ProfileFailure('invalid_request');
      parseAppIntent(intent);
      intent = copy(intent); context = copy(context);
      await delay(context, outcome);
      const canonical = JSON.stringify([intent.operation, intent.meta.expected_version, intent.action]);
      const previous = replay(context, intent, canonical);
      if (previous) return resultFor(previous as OwnProfile, outcome);
      if (!state.profile || intent.meta.expected_version !== state.profile.version) throw new ProfileFailure('stale_version');
      if ((intent.action === 'pause' && state.profile.visibility !== 'visible') ||
          (intent.action === 'resume' && state.profile.visibility !== 'paused')) throw new ProfileFailure('state_conflict');
      if (intent.action === 'resume') {
        if (!state.policy) throw new ProfileFailure('policy_unresolved');
        if (!eligibility(state)) throw new ProfileFailure('forbidden');
      }
      const profile: OwnProfile = { ...state.profile, version: state.profile.version + 1, visibility: intent.action === 'pause' ? 'paused' : 'visible' };
      return prepare(context, intent, canonical, { ...state, profile }, profile, outcome);
    },
    acknowledge(context, result) {
      check(context);
      validateProjection(result);
      if (!staged) {
        const current = result.kind === 'own_profile' ? state.profile : state.preferences;
        if (JSON.stringify(current) !== JSON.stringify(result)) throw new ProfileFailure('stale_version');
        return;
      }
      if (JSON.stringify(staged.receipt.result) !== JSON.stringify(result)) throw new ProfileFailure('invalid_request');
      state = staged.state; receipts.set(staged.receiptKey, staged.receipt); staged = null;
    },
    cancelPending() { epoch += 1; staged = null; },
    synchronizeMedia(collection) {
      const ids = collection.items.filter(item => item.state === 'approved' && item.approved_delivery_ref !== null).map(item => item.asset_id);
      adapter.cancelPending(); authorityRevision += 1;
      state.evidence = { ...state.evidence, media: ids.length > 0 };
      if (state.profile) {
        const profile = { ...state.profile, version: state.profile.version + 1, media_ids: ids };
        state = { ...state, profile };
        // Media evidence changes effective disclosure, not a new F04/F06 actor
        // transition. Explicit owner completion/resume still uses its own gate.
      }
    },
    seedEligible() {
      if (!activeOwner(authority) || !authority.adult || !authority.consentCurrent) throw new ProfileFailure('forbidden');
      adapter.cancelPending(); authorityRevision += 1; receipts.clear();
      state = { policy: FIXTURE_PREFERENCE_POLICY,
        profile: { kind: 'own_profile', profile_id: profileId(), version: 1, display_name: 'Alex',
          summary: 'A fictional profile for the visibility demonstration.', visibility: 'visible', media_ids: [FIXTURE_MEDIA_ID] },
        preferences: { kind: 'own_preferences', version: 1, policy_version: FIXTURE_PREFERENCE_POLICY.version,
          selections: [{ dimension: 'demo_connection', accepted_option_ids: ['demo_a'] }] },
        evidence: { media: true, chart: true, moderation: true, reciprocalPreferencesVersion: 1, reciprocalPolicyVersion: FIXTURE_PREFERENCE_POLICY.version } };
    },
    developmentChange(change) {
      if (!activeOwner(authority)) throw new ProfileFailure('unauthenticated');
      adapter.cancelPending(); authorityRevision += 1;
      if (change === 'profile' && state.profile) state.profile = { ...state.profile, version: state.profile.version + 1,
        display_name: 'Alex current', summary: 'A newer fictional biography.' };
      if (change === 'preferences' && state.preferences) state.preferences = { ...state.preferences, version: state.preferences.version + 1,
        selections: [{ dimension: 'demo_connection', accepted_option_ids: ['demo_b'] }] };
      if (change === 'policy') state.policy = state.policy ? { ...state.policy, version: `${state.policy.version}-new` } : null;
      if (change === 'media') state.evidence = { ...state.evidence, media: false };
      if (change === 'reciprocal') state.evidence = { ...state.evidence, reciprocalPreferencesVersion: null, reciprocalPolicyVersion: null };
      if (change === 'profile' || change === 'preferences') retract();
    },
  };
  return adapter;
}
