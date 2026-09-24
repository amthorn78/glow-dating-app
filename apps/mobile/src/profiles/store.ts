import type { CandidateProfile, MediaCollection, OwnPreferences, OwnProfile, PreferenceSelection, PreferencesIntent, ProfileIntent, VisibilityIntent } from '../contracts/generated/gapp-api-v1.ts';
import { parseAppIntent, parseAppResponse } from '../contracts/production.ts';
import { createProfileAdapter, fixtureProfileRevision, fixtureProfileGuard, ProfileFailure, type DevelopmentChange, type ProfileAdapter,
  type ProfileContext, type ProfileOutcome, type ProfileRecords } from './fixture-adapter.ts';
import { activeOwner, canonicalSelections, PROFILE_REQUEST_ID, projectCandidate, requirements,
  type ProfileAuthority } from './policy.ts';
import { capturePairVersion, FIXTURE_PAIR_POLICY, FixturePairRepository, type ParticipantFacts, type PairVersion } from '../eligibility/facts.ts';
import { FIXTURE_CLOCK, type FixtureClock } from '../onboarding/policy.ts';

export type { ProfileOutcome } from './fixture-adapter.ts';
export type DiscoveryViewerCapture = Readonly<{ facts: ParticipantFacts; policy: typeof FIXTURE_PAIR_POLICY | null; sessionId: string }>;
const discoveryCaptures = new WeakMap<object, readonly Readonly<{ cell: Readonly<{ revision: number }>; revision: number }>[]>();
/** No clock, provider, media reader, adapter method, equality or user getter is invoked here. */
export function discoveryViewerIsCurrent(capture: object): boolean {
  const guards = discoveryCaptures.get(capture);
  return guards !== undefined && guards.every(guard => guard.cell.revision === guard.revision);
}
export type DiscoveryViewerToken = Readonly<{ viewerId: string; sessionId: string }>;
export function discoveryViewerToken(capture: DiscoveryViewerCapture): DiscoveryViewerToken {
  const token = Object.freeze({ viewerId: capture.facts.account_id, sessionId: capture.sessionId });
  const guards = discoveryCaptures.get(capture);
  if (guards) discoveryCaptures.set(token, guards);
  return token;
}
export type ProfileDraft = Pick<ProfileIntent, 'display_name' | 'summary'>;
export type CandidateViewContext = Readonly<{ viewerId: string; candidateProfileId: string; generation: number; discoveryRevision: number; version: PairVersion }>;
export interface ProfileSnapshot {
  readonly ownerKey: string;
  readonly profile: OwnProfile | null;
  readonly preferences: OwnPreferences | null;
  readonly profileDraft: ProfileDraft;
  readonly preferencesDraft: PreferenceSelection[];
  readonly profileDraftRevision: number;
  readonly preferencesDraftRevision: number;
  readonly discoveryRevision: number;
  readonly policyVersion: string | null;
  readonly busy: boolean;
  readonly error: string | null;
  readonly message: string | null;
  readonly requirements: string[];
  readonly canDiscover: boolean;
}
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
const freeze = <T>(value: T): T => {
  if (value && typeof value === 'object') { Object.values(value).forEach(freeze); Object.freeze(value); }
  return value;
};
const blankDraft = (): ProfileDraft => ({ display_name: '', summary: '' });
const equal = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);
const FIXTURE_VIEWER_ID = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
const contextFields = ['viewerId', 'candidateProfileId', 'generation', 'discoveryRevision', 'version'] as const;
function captureCandidateContext(value: CandidateViewContext | null): CandidateViewContext | null {
  if (value === null) return null;
  if (typeof value !== 'object' || Array.isArray(value) || Reflect.ownKeys(value).length !== contextFields.length) {
    throw new TypeError('Invalid fixture candidate precondition.');
  }
  const fields = Object.getOwnPropertyDescriptors(value);
  if (contextFields.some(field => !Object.hasOwn(fields, field) || !Object.hasOwn(fields[field]!, 'value') || !fields[field]!.enumerable)) {
    throw new TypeError('Invalid fixture candidate precondition.');
  }
  const captured = Object.fromEntries(contextFields.map(field => [field, fields[field]!.value])) as CandidateViewContext;
  if (typeof captured.viewerId !== 'string' || !captured.viewerId.trim() ||
      typeof captured.candidateProfileId !== 'string' || !captured.candidateProfileId.trim() ||
      !Number.isSafeInteger(captured.generation) || captured.generation < 1 ||
      !Number.isSafeInteger(captured.discoveryRevision) || captured.discoveryRevision < 0 || captured.version === undefined) {
    throw new TypeError('Invalid fixture candidate precondition.');
  }
  return Object.freeze({ ...captured, version: capturePairVersion(captured.version)! });
}

/** Same-session owner presentation; the fixture adapter remains the mutation authority. */
export class ProfileStore {
  private authority: ProfileAuthority = { ownerId: null, generation: 0, accountVersion: 0,
    accountState: 'none', sessionState: 'none', adult: false, consentCurrent: false, sourceRevision: 0, consentRevision: 'none' };
  private listeners = new Set<() => void>();
  private operation = 0;
  private sequence = 0;
  private adapter: ProfileAdapter;
  private mediaSource: (() => MediaCollection) | null = null;
  private mediaRevoker: (() => void) | null = null;
  private mediaBindingRevision = 0;
  private readonly discoveryCell = { revision: 0 };
  private pauseRequested = false;
  private pendingIntents = new Map<string, { signature: string; intent: ProfileIntent | PreferencesIntent | VisibilityIntent }>();
  private fictionalViewer: ParticipantFacts | null = null;
  private readonly pairs: FixturePairRepository;
  private readonly clock: FixtureClock;
  private pairSource = '';
  private pairPolicy = '';
  private candidateAttribute: string = 'demo_a';
  private snapshot: ProfileSnapshot = freeze({ ownerKey: 'none:0', profile: null, preferences: null,
    profileDraft: blankDraft(), preferencesDraft: [], profileDraftRevision: 0, preferencesDraftRevision: 0,
    discoveryRevision: 0, policyVersion: null, busy: false, error: null, message: null, requirements: [], canDiscover: false });

  constructor(adapter: ProfileAdapter, options: { isDevelopment: boolean; mode: string | undefined; clock?: FixtureClock }) {
    if (!options.isDevelopment || options.mode !== 'fixture' || adapter.kind !== 'fixture') throw new Error('Profiles require the explicit development fixture runtime.');
    this.adapter = adapter;
    this.clock = options.clock ?? FIXTURE_CLOCK; this.pairs = new FixturePairRepository(this.clock);
  }
  readonly getSnapshot = () => this.snapshot;
  readonly subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  private publish(patch: Partial<ProfileSnapshot>): void {
    this.discoveryCell.revision += 1;
    const state = this.adapter.inspect();
    const missing = requirements(state.profile, state.preferences, this.authority, state.policy, state.evidence);
    this.snapshot = freeze({ ...this.snapshot, ...clone(patch), policyVersion: state.policy?.version ?? null,
      requirements: missing, canDiscover: !this.pauseRequested && activeOwner(this.authority) && missing.length === 0 && state.profile?.visibility === 'visible' });
    this.listeners.forEach(listener => listener());
  }
  /** Merge independently per field; source changes never overwrite unrelated deliberate edits. */
  private adopt(records: ProfileRecords, reset = false, patch: Partial<ProfileSnapshot> = {}): void {
    const prior = this.snapshot;
    const profileChanged = !equal(prior.profile, records.profile);
    const preferencesChanged = !equal(prior.preferences, records.preferences);
    const oldDraft = prior.profile ? { display_name: prior.profile.display_name, summary: prior.profile.summary } : blankDraft();
    const source = records.profile ? { display_name: records.profile.display_name, summary: records.profile.summary } : blankDraft();
    const profileDraft = reset ? source : {
      display_name: prior.profileDraft.display_name === oldDraft.display_name ? source.display_name : prior.profileDraft.display_name,
      summary: prior.profileDraft.summary === oldDraft.summary ? source.summary : prior.profileDraft.summary,
    };
    const previousSelections = prior.preferences?.selections ?? [];
    const nextSelections = records.preferences?.selections ?? [];
    const preferencesDraft = reset || equal(prior.preferencesDraft, previousSelections) ? nextSelections : prior.preferencesDraft;
    this.publish({ profile: records.profile, preferences: records.preferences, profileDraft, preferencesDraft,
      profileDraftRevision: prior.profileDraftRevision + (profileChanged || reset ? 1 : 0),
      preferencesDraftRevision: prior.preferencesDraftRevision + (preferencesChanged || reset ? 1 : 0),
      discoveryRevision: prior.discoveryRevision + (profileChanged || preferencesChanged || reset ? 1 : 0), ...patch });
  }
  synchronize(authority: ProfileAuthority): void {
    if (equal(authority, this.authority)) return;
    const boundary = authority.ownerId !== this.authority.ownerId || authority.generation !== this.authority.generation ||
      !activeOwner(authority);
    this.adapter.cancelPending(); this.operation += 1;
    this.adapter.synchronize(authority); this.authority = clone(authority);
    this.pendingIntents.clear();
    if (boundary) { this.fictionalViewer = null; this.pauseRequested = false; }
    const state = this.adapter.inspect();
    this.adopt(activeOwner(authority) ? state : { profile: null, preferences: null }, boundary,
      { ownerKey: `${authority.ownerId ?? 'none'}:${authority.generation}`, busy: false, error: null, message: null,
        profileDraftRevision: this.snapshot.profileDraftRevision + 1,
        preferencesDraftRevision: this.snapshot.preferencesDraftRevision + 1,
        discoveryRevision: this.snapshot.discoveryRevision + 1 });
  }
  private owns(revision: number, kind: 'profile' | 'preferences'): boolean {
    return activeOwner(this.authority) && revision === this.snapshot[kind === 'profile' ? 'profileDraftRevision' : 'preferencesDraftRevision'];
  }
  editProfileDraft(patch: Partial<ProfileDraft>, revision: number): void {
    if (!this.owns(revision, 'profile') || Object.keys(patch).some(key => !['display_name', 'summary'].includes(key))) return;
    this.publish({ profileDraft: { ...this.snapshot.profileDraft, ...patch }, error: null, message: null });
  }
  editPreferencesDraft(selections: PreferenceSelection[], revision: number): void {
    if (!this.owns(revision, 'preferences')) return;
    this.publish({ preferencesDraft: selections, error: null, message: null });
  }
  cancelProfileEdit(revision: number): void {
    if (!this.owns(revision, 'profile')) return;
    this.cancel();
    const profile = this.snapshot.profile;
    this.publish({ profileDraft: profile ? { display_name: profile.display_name, summary: profile.summary } : blankDraft(),
      profileDraftRevision: this.snapshot.profileDraftRevision + 1, message: 'Profile edits cancelled.', error: null });
  }
  cancelPreferencesEdit(revision: number): void {
    if (!this.owns(revision, 'preferences')) return;
    this.cancel();
    this.publish({ preferencesDraft: this.snapshot.preferences?.selections ?? [],
      preferencesDraftRevision: this.snapshot.preferencesDraftRevision + 1, message: 'Preference edits cancelled.', error: null });
  }
  private cancel(): void {
    this.adapter.cancelPending(); this.operation += 1; this.publish({ busy: false });
  }
  private intent<T extends ProfileIntent | PreferencesIntent | VisibilityIntent>(operation: T['operation'], signature: unknown, build: (key: string) => T): T {
    const encoded = JSON.stringify(signature);
    const prior = this.pendingIntents.get(operation);
    if (prior?.signature === encoded) return clone(prior.intent) as T;
    this.sequence += 1;
    const intent = build(`profile-command:${this.sequence}`);
    parseAppIntent(intent);
    this.pendingIntents.set(operation, { signature: encoded, intent: clone(intent) });
    return intent;
  }
  private async run<T>(work: (context: ProfileContext) => Promise<T>, accept: (context: ProfileContext, value: T) => void): Promise<void> {
    if (this.snapshot.busy) return;
    let context: ProfileContext;
    try { context = this.adapter.context(); } catch (error) { this.failure(error); return; }
    const operation = ++this.operation, ownerKey = this.snapshot.ownerKey;
    this.publish({ busy: true, error: null, message: null });
    try {
      const result = await work(context);
      if (operation !== this.operation || ownerKey !== this.snapshot.ownerKey) return;
      accept(context, result);
    } catch (error) {
      if (operation !== this.operation || ownerKey !== this.snapshot.ownerKey) return;
      this.adapter.cancelPending(); this.failure(error);
    } finally {
      if (operation === this.operation && ownerKey === this.snapshot.ownerKey) this.publish({ busy: false });
    }
  }
  private failure(error: unknown): void {
    this.publish({ error: error instanceof ProfileFailure ? error.message : 'The response could not be accepted. Your draft is kept; reload current values before retrying.', message: null });
  }
  private validate(result: OwnProfile | OwnPreferences): void {
    parseAppResponse({ contract_version: 'gapp-api-v1', request_id: PROFILE_REQUEST_ID, data: result });
  }
  async saveProfile(revision: number, outcome: ProfileOutcome = 'success'): Promise<void> {
    if (!this.owns(revision, 'profile')) return;
    const draft = clone(this.snapshot.profileDraft), expected = this.snapshot.profile?.version ?? 0;
    let intent: ProfileIntent;
    try {
      intent = this.intent('profile', [expected, draft.display_name, draft.summary], key => ({ operation: 'profile',
        meta: { expected_version: expected, idempotency_key: key }, ...draft }));
    } catch { this.failure(new ProfileFailure('invalid_request')); return; }
    await this.run(context => this.adapter.saveProfile(context, intent, outcome), (context, result) => {
      this.validate(result);
      if (result.kind !== 'own_profile' || result.profile_id !== context.profileId || result.display_name !== draft.display_name ||
          result.summary !== draft.summary || result.version !== expected + 1) throw new ProfileFailure('invalid_request');
      this.adapter.acknowledge(context, result);
      this.adopt(this.adapter.inspect());
      this.publish({ message: 'Profile saved for this session.' });
    });
  }
  async savePreferences(revision: number, outcome: ProfileOutcome = 'success'): Promise<void> {
    if (!this.owns(revision, 'preferences')) return;
    const selections = clone(this.snapshot.preferencesDraft), expected = this.snapshot.preferences?.version ?? 0, policyVersion = this.snapshot.policyVersion;
    if (!policyVersion) { this.failure(new ProfileFailure('policy_unresolved')); return; }
    let intent: PreferencesIntent;
    try {
      intent = this.intent('preferences', [expected, policyVersion, canonicalSelections(selections)], key => ({ operation: 'preferences',
        meta: { expected_version: expected, idempotency_key: key }, policy_version: policyVersion, selections }));
    } catch { this.failure(new ProfileFailure('invalid_request')); return; }
    await this.run(context => this.adapter.savePreferences(context, intent, outcome), (context, result) => {
      this.validate(result);
      if (result.kind !== 'own_preferences' || result.version !== expected + 1 || result.policy_version !== policyVersion ||
          !equal(result.selections, selections)) throw new ProfileFailure('invalid_request');
      this.adapter.acknowledge(context, result);
      this.adopt(this.adapter.inspect());
      this.publish({ message: 'Preferences saved for this session.' });
    });
  }
  async setVisibility(action: 'pause' | 'resume', outcome: ProfileOutcome = 'success'): Promise<void> {
    const profile = this.snapshot.profile;
    if (!profile || !activeOwner(this.authority)) { this.failure(new ProfileFailure('forbidden')); return; }
    // A pause must cancel a delayed edit/resume instead of waiting behind it.
    if (action === 'pause') {
      this.pauseRequested = true;
      this.cancel();
      this.publish({ discoveryRevision: this.snapshot.discoveryRevision + 1 });
    }
    const intent = this.intent<VisibilityIntent>('visibility', [profile.version, action], key => ({ operation: 'visibility',
      meta: { expected_version: profile.version, idempotency_key: key }, action }));
    await this.run(context => this.adapter.visibility(context, intent, outcome), (context, result) => {
      this.validate(result);
      if (result.kind !== 'own_profile' || result.profile_id !== context.profileId || result.version !== profile.version + 1 ||
          result.visibility !== (action === 'pause' ? 'paused' : 'visible')) throw new ProfileFailure('invalid_request');
      this.adapter.acknowledge(context, result);
      if (action === 'resume') this.pauseRequested = false;
      this.adopt(this.adapter.inspect());
      this.publish({ message: action === 'pause' ? 'Your profile is paused.' : 'Your profile is visible in the fictional scenario.' });
    });
  }
  async reload(outcome: ProfileOutcome = 'success'): Promise<void> {
    await this.run(context => this.adapter.read(context, outcome), (_context, records) => {
      if (records.profile) this.validate(records.profile);
      if (records.preferences) this.validate(records.preferences);
      const current = this.adapter.inspect();
      if (!equal(records, { profile: current.profile, preferences: current.preferences })) throw new ProfileFailure('invalid_request');
      this.adopt(records);
      this.publish({ message: 'Current saved values loaded. Review your draft before saving.' });
    });
  }
  seedEligible(): void {
    this.cancel(); this.adapter.seedEligible(); this.pauseRequested = false;
    this.fictionalViewer = this.fixtureViewer(); this.candidateAttribute = 'demo_a';
    this.pairs.put(this.fictionalViewer);
    this.pairs.observeBlock(FIXTURE_VIEWER_ID, this.authority.ownerId!, 'clear');
    this.pairs.observeBlock(this.authority.ownerId!, FIXTURE_VIEWER_ID, 'clear');
    this.adopt(this.adapter.inspect(), true);
    if (this.mediaSource) this.synchronizeMedia(this.mediaSource());
    this.publish({ message: 'Fictional profile, media, chart and independent pair facts loaded. No real service was used.' });
  }
  developmentChange(change: DevelopmentChange): void {
    if (change === 'media' && this.mediaRevoker) { this.mediaRevoker(); return; }
    try {
      this.cancel(); this.adapter.developmentChange(change); this.pendingIntents.clear();
      if (change === 'reciprocal' && this.fictionalViewer) {
        this.fictionalViewer = freeze({ ...this.fictionalViewer, accepted_options: ['demo_b'] });
        this.pairs.put(this.fictionalViewer);
      }
      this.adopt(this.adapter.inspect());
      this.publish({ discoveryRevision: this.snapshot.discoveryRevision + 1,
        ...(change === 'policy' ? { profileDraftRevision: this.snapshot.profileDraftRevision + 1,
          preferencesDraftRevision: this.snapshot.preferencesDraftRevision + 1 } : {}), error: null,
        message: 'Saved source changed. Untouched fields refreshed; your deliberate edits remain. Review your draft before saving.' });
    } catch (error) { this.failure(error); }
  }
  private fixtureViewer(): ParticipantFacts {
    const profile = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
    return freeze({ account_id: FIXTURE_VIEWER_ID, source_id: 'development-viewer-record', generation: this.authority.generation,
      profile_id: profile, birth_date: '1988-02-29', account_state: 'active', session_state: 'valid', verified: true,
      consent_state: 'accepted', consent_version: 'development-consent-1', display_name: 'Fictional viewer', summary: 'Independent fictional viewer.',
      visibility: 'visible', moderation: 'approved', chart_state: 'resolved', attribute: 'demo_a',
      preference_dimension: 'demo_connection', preference_version: 'development-preferences-1', accepted_options: ['demo_a'],
      approved_media: [{ asset_id: 'cccccccc-cccc-4ccc-8ccc-cccccccccccc', owner_id: FIXTURE_VIEWER_ID, profile_id: profile,
        generation: this.authority.generation, state: 'approved', policy_version: 'development-media-1', delivery_ref: 'fixture:viewer-approved' }] });
  }
  /** Map app-owned fixture sources afresh. Public profile/preferences DTOs cannot supply independent viewer facts. */
  private currentPair(): ReturnType<FixturePairRepository['evaluate']> | null {
    const profile = this.snapshot.profile, owner = this.authority.ownerId;
    if (!profile || !owner || !this.fictionalViewer) return null;
    const sourceSnapshot = this.snapshot, sourceAuthority = this.authority;
    const sourceRevision = fixtureProfileRevision(this.adapter), mediaRevision = this.mediaBindingRevision;
    if (sourceRevision === null) return null;
    const records = this.adapter.inspect(), preferences = records.preferences;
    const media = this.mediaSource?.();
    if (sourceSnapshot !== this.snapshot || sourceAuthority !== this.authority ||
        sourceRevision !== fixtureProfileRevision(this.adapter) || mediaRevision !== this.mediaBindingRevision ||
        !equal(records.profile, profile) || !equal(preferences, this.snapshot.preferences)) return null;
    const ids = media?.items.map(item => item.asset_id) ?? profile.media_ids;
    const validMedia = equal(ids, profile.media_ids) && records.evidence.media;
    const selection = preferences?.selections.length === 1 ? preferences.selections[0] : undefined;
    const candidate: ParticipantFacts = {
      account_id: owner, source_id: `development-owner-record:${owner}`, generation: this.authority.generation,
      profile_id: profile.profile_id, birth_date: this.authority.birthDate ?? null,
      account_state: this.authority.accountState, session_state: this.authority.sessionState,
      verified: this.authority.accountState === 'unverified' ? false : this.authority.accountState === 'none' ? null : true,
      consent_state: this.authority.consentState ?? null, consent_version: this.authority.consentVersion ?? null,
      display_name: profile.display_name, summary: profile.summary, visibility: this.pauseRequested ? 'paused' : profile.visibility,
      moderation: records.evidence.moderation ? 'approved' : 'pending', chart_state: records.evidence.chart ? 'resolved' : 'pending',
      attribute: this.candidateAttribute, preference_dimension: selection?.dimension ?? null,
      preference_version: preferences?.policy_version ?? null, accepted_options: selection?.accepted_option_ids ?? null,
      approved_media: validMedia ? ids.map(asset_id => ({ asset_id, owner_id: owner, profile_id: profile.profile_id,
        generation: this.authority.generation, state: media ? media.items.find(item => item.asset_id === asset_id)?.state ?? null : 'approved', policy_version: 'development-media-1',
        delivery_ref: media ? media.items.find(item => item.asset_id === asset_id)?.approved_delivery_ref ?? null : 'fixture:standalone-approved' })) : [],
    };
    // Aggregate signature includes every source revision, even a same-value write or A→B→A restoration.
    const signature = JSON.stringify([candidate, this.authority, profile.version, preferences?.version,
      this.snapshot.discoveryRevision, media?.version, sourceRevision, mediaRevision]);
    if (signature !== this.pairSource) { this.pairSource = signature; this.pairs.put(candidate); }
    const policySignature = JSON.stringify([records.policy, this.authority.consentVersion]);
    if (policySignature !== this.pairPolicy) {
      this.pairPolicy = policySignature;
      this.pairs.setPolicy(records.policy?.version === 'development-preferences-1' ? FIXTURE_PAIR_POLICY : null);
    }
    const result = this.pairs.evaluate(FIXTURE_VIEWER_ID, owner);
    return sourceSnapshot === this.snapshot && sourceAuthority === this.authority &&
      sourceRevision === fixtureProfileRevision(this.adapter) && mediaRevision === this.mediaBindingRevision ? result : null;
  }
  /** Current owner facts for the separate discovery composition, never the preview viewer's grant. */
  captureDiscoveryViewer(): DiscoveryViewerCapture | null {
    const revision = this.discoveryCell.revision, guard = fixtureProfileGuard(this.adapter);
    if (!guard || !this.snapshot.canDiscover || !this.authority.ownerId) return null;
    const pair = this.currentPair();
    const facts = this.pairs.inspect(this.authority.ownerId);
    if (!pair || !facts || revision !== this.discoveryCell.revision || guard.cell.revision !== guard.revision) return null;
    const capture = freeze({ facts, policy: this.pairPolicy && this.snapshot.policyVersion === 'development-preferences-1' ? FIXTURE_PAIR_POLICY : null,
      sessionId: `fixture-session-${this.authority.generation}` });
    discoveryCaptures.set(capture, [{ cell: this.discoveryCell, revision }, guard, this.pairs.captureGuard()]);
    return capture;
  }
  /** Session authority for safety revocation is independent of discovery/consent readiness. */
  captureInteractionOwner(): Readonly<{ ownerId: string; sessionId: string; profileId: string | null }> | null {
    if (!activeOwner(this.authority) || !this.authority.ownerId) return null;
    const token = Object.freeze({ ownerId: this.authority.ownerId,
      sessionId: `fixture-session-${this.authority.generation}`, profileId: this.snapshot.profile?.profile_id ?? null });
    const guard = fixtureProfileGuard(this.adapter);
    if (!guard) return null;
    discoveryCaptures.set(token, [{ cell: this.discoveryCell, revision: this.discoveryCell.revision }, guard]);
    return token;
  }
  candidateContext(): CandidateViewContext | null {
    const pair = this.currentPair();
    if (!this.snapshot.profile || !pair?.version) return null;
    return freeze({ viewerId: FIXTURE_VIEWER_ID, candidateProfileId: this.snapshot.profile.profile_id,
      generation: this.authority.generation, discoveryRevision: this.snapshot.discoveryRevision, version: pair.version });
  }
  candidatePreview(context: CandidateViewContext | null = this.candidateContext()): CandidateProfile | null {
    context = captureCandidateContext(context);
    const current = this.candidateContext();
    if (!context || !current || !equal(context, current) || !this.snapshot.canDiscover || !this.snapshot.profile) return null;
    const sourceSnapshot = this.snapshot, sourceAuthority = this.authority;
    const sourceRevision = fixtureProfileRevision(this.adapter), mediaRevision = this.mediaBindingRevision;
    const decision = this.pairs.evaluate(FIXTURE_VIEWER_ID, this.authority.ownerId!, context.version);
    if (decision.state !== 'ready' || sourceSnapshot !== this.snapshot || sourceAuthority !== this.authority) return null;
    const profile = clone(this.snapshot.profile), facts = this.pairs.inspect(this.authority.ownerId!);
    // Age and media come from the evaluation's immutable inputs, never separate unbound dependency reads.
    const age = decision.candidateAge;
    if (age === null || age === undefined) return null;
    const references = this.mediaSource ? facts?.approved_media?.filter(item => item.state === 'approved' &&
      item.policy_version === 'development-media-1' && item.delivery_ref !== null).map(item => item.delivery_ref!) ?? [] : [];
    let projection: CandidateProfile;
    try { projection = projectCandidate(profile, age, references); } catch { return null; }
    // Source/clock callbacks are external reads too: finish by checking their exact captured version.
    const finalContext = this.candidateContext();
    if (!equal(context, finalContext)) return null;
    const finalResult = this.pairs.evaluate(FIXTURE_VIEWER_ID, this.authority.ownerId!, context.version);
    // Callback-free revision checks are the last acceptance boundary; no source read follows them.
    if (finalResult.state !== 'ready' || sourceSnapshot !== this.snapshot || sourceAuthority !== this.authority ||
        sourceRevision === null || sourceRevision !== fixtureProfileRevision(this.adapter) || mediaRevision !== this.mediaBindingRevision) return null;
    return projection;
  }
  /** Existing synthetic source controls; never a client/server evidence endpoint or contact operation. */
  developmentPairChange(change: 'block_viewer' | 'block_candidate' | 'clear_blocks' | 'viewer_preferences' | 'restore_viewer_preferences' |
    'viewer_pause' | 'viewer_resume' | 'candidate_attribute'): void {
    if (!activeOwner(this.authority) || !this.fictionalViewer) return;
    if (change === 'block_viewer') this.pairs.observeBlock(FIXTURE_VIEWER_ID, this.authority.ownerId!, 'blocked');
    if (change === 'block_candidate') this.pairs.observeBlock(this.authority.ownerId!, FIXTURE_VIEWER_ID, 'blocked');
    if (change === 'clear_blocks') {
      this.pairs.observeBlock(FIXTURE_VIEWER_ID, this.authority.ownerId!, 'clear');
      this.pairs.observeBlock(this.authority.ownerId!, FIXTURE_VIEWER_ID, 'clear');
    }
    if (change === 'candidate_attribute') this.candidateAttribute = this.candidateAttribute === 'demo_a' ? 'demo_b' : 'demo_a';
    if (['viewer_preferences', 'restore_viewer_preferences', 'viewer_pause', 'viewer_resume'].includes(change)) {
      this.fictionalViewer = freeze({ ...this.fictionalViewer,
        ...(change === 'viewer_preferences' ? { accepted_options: ['demo_b'] } : {}),
        ...(change === 'restore_viewer_preferences' ? { accepted_options: ['demo_a'] } : {}),
        ...(change === 'viewer_pause' ? { visibility: 'paused' } : {}), ...(change === 'viewer_resume' ? { visibility: 'visible' } : {}) });
      this.pairs.put(this.fictionalViewer);
    }
    this.publish({ discoveryRevision: this.snapshot.discoveryRevision + 1 });
  }
  bindMedia(source: () => MediaCollection, revoke: () => void): void {
    this.mediaBindingRevision += 1; this.discoveryCell.revision += 1;
    this.mediaSource = source; this.mediaRevoker = revoke;
  }
  synchronizeMedia(collection: MediaCollection): void {
    this.cancel(); this.pendingIntents.clear(); this.adapter.synchronizeMedia(collection);
    this.adopt(this.adapter.inspect());
    this.publish({ discoveryRevision: this.snapshot.discoveryRevision + 1 });
  }
}

export function createFixtureProfileStore(options: { isDevelopment: boolean; mode: string | undefined; pause?: () => Promise<void>; clock?: FixtureClock }): ProfileStore {
  return new ProfileStore(createProfileAdapter(options), options);
}
