import type { CandidateProfile, MediaCollection, OwnPreferences, OwnProfile, PreferenceSelection, PreferencesIntent, ProfileIntent, VisibilityIntent } from '../contracts/generated/gapp-api-v1.ts';
import { parseAppIntent, parseAppResponse } from '../contracts/production.ts';
import { createProfileAdapter, ProfileFailure, type DevelopmentChange, type ProfileAdapter,
  type ProfileContext, type ProfileOutcome, type ProfileRecords } from './fixture-adapter.ts';
import { activeOwner, canonicalSelections, PROFILE_REQUEST_ID, projectCandidate, requirements,
  type ProfileAuthority } from './policy.ts';

export type { ProfileOutcome } from './fixture-adapter.ts';
export type ProfileDraft = Pick<ProfileIntent, 'display_name' | 'summary'>;
export type CandidateViewContext = Readonly<{ viewerId: string; candidateProfileId: string; generation: number; discoveryRevision: number }>;
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
  private pauseRequested = false;
  private pendingIntents = new Map<string, { signature: string; intent: ProfileIntent | PreferencesIntent | VisibilityIntent }>();
  private fictionalViewer: { generation: number; policyVersion: string; active: true; adult: true;
    consent: true; complete: true; visible: true; moderation: true; bothBlocksClear: true } | null = null;
  private snapshot: ProfileSnapshot = freeze({ ownerKey: 'none:0', profile: null, preferences: null,
    profileDraft: blankDraft(), preferencesDraft: [], profileDraftRevision: 0, preferencesDraftRevision: 0,
    discoveryRevision: 0, policyVersion: null, busy: false, error: null, message: null, requirements: [], canDiscover: false });

  constructor(adapter: ProfileAdapter, options: { isDevelopment: boolean; mode: string | undefined }) {
    if (!options.isDevelopment || options.mode !== 'fixture' || adapter.kind !== 'fixture') throw new Error('Profiles require the explicit development fixture runtime.');
    this.adapter = adapter;
  }
  readonly getSnapshot = () => this.snapshot;
  readonly subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  private publish(patch: Partial<ProfileSnapshot>): void {
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
    this.fictionalViewer = { generation: this.authority.generation, policyVersion: this.adapter.inspect().policy!.version,
      active: true, adult: true, consent: true, complete: true, visible: true, moderation: true, bothBlocksClear: true };
    this.adopt(this.adapter.inspect(), true);
    if (this.mediaSource) this.synchronizeMedia(this.mediaSource());
    this.publish({ message: 'Fictional profile, media, chart and reciprocal eligibility evidence loaded. No real service was used.' });
  }
  developmentChange(change: DevelopmentChange): void {
    if (change === 'media' && this.mediaRevoker) { this.mediaRevoker(); return; }
    try {
      this.cancel(); this.adapter.developmentChange(change); this.pendingIntents.clear();
      this.adopt(this.adapter.inspect());
      this.publish({ discoveryRevision: this.snapshot.discoveryRevision + 1,
        ...(change === 'policy' ? { profileDraftRevision: this.snapshot.profileDraftRevision + 1,
          preferencesDraftRevision: this.snapshot.preferencesDraftRevision + 1 } : {}), error: null,
        message: 'Saved source changed. Untouched fields refreshed; your deliberate edits remain. Review your draft before saving.' });
    } catch (error) { this.failure(error); }
  }
  candidateContext(): CandidateViewContext | null {
    if (!this.snapshot.profile || !this.fictionalViewer) return null;
    return { viewerId: FIXTURE_VIEWER_ID, candidateProfileId: this.snapshot.profile.profile_id,
      generation: this.authority.generation, discoveryRevision: this.snapshot.discoveryRevision };
  }
  candidatePreview(context: CandidateViewContext | null = this.candidateContext()): CandidateProfile | null {
    const current = this.candidateContext(), viewer = this.fictionalViewer;
    if (!context || !current || !equal(context, current) || !this.snapshot.canDiscover || !this.snapshot.profile || !viewer ||
        viewer.generation !== this.authority.generation || viewer.policyVersion !== this.snapshot.policyVersion ||
        !viewer.active || !viewer.adult || !viewer.consent || !viewer.complete || !viewer.visible || !viewer.moderation || !viewer.bothBlocksClear) return null;
    const media = this.mediaSource?.();
    if (media && (media.items.length === 0 || !equal(this.snapshot.profile.media_ids, media.items.map(item => item.asset_id)))) return null;
    return projectCandidate(this.snapshot.profile, media?.items.map(item => item.approved_delivery_ref!).filter(Boolean) ?? []);
  }
  bindMedia(source: () => MediaCollection, revoke: () => void): void {
    this.mediaSource = source; this.mediaRevoker = revoke;
  }
  synchronizeMedia(collection: MediaCollection): void {
    this.cancel(); this.pendingIntents.clear(); this.adapter.synchronizeMedia(collection);
    this.adopt(this.adapter.inspect());
    this.publish({ discoveryRevision: this.snapshot.discoveryRevision + 1 });
  }
}

export function createFixtureProfileStore(options: { isDevelopment: boolean; mode: string | undefined; pause?: () => Promise<void> }): ProfileStore {
  return new ProfileStore(createProfileAdapter(options), options);
}
