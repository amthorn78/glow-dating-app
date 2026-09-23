import type { AccountAccess, BirthInput, BirthInputIntent, ConsentIntent, OnboardingEligibility, OwnBirthInput } from '../contracts/generated/gapp-api-v1.ts';
import { validateAccountAccess, validateConsentIntent, validateOnboardingEligibility, validateOwnBirthInput } from '../contracts/generated/validators.js';
import { createFixtureAdapter, FixtureFailure, RECOVERY_MESSAGE, FIXTURE_ACCOUNT_IDS,
  type OnboardingAdapter, type FixtureOutcome, type BirthOutcome, type AccountMode } from './fixture-adapter.ts';
import { adultOutcome, birthInputValid, FIXTURE_CLOCK, FIXTURE_POLICY, validCivilDate,
  type AdultPolicy, type FixtureClock, type PredicateOutcome } from './policy.ts';
import { createFixtureProfileStore, type ProfileStore } from '../profiles/store.ts';
import { MediaStore } from '../media/store.ts';

export { FIXTURE_PASSWORD, RECOVERY_MESSAGE } from './fixture-adapter.ts';
export { FIXTURE_POLICY } from './policy.ts';
export type { FixtureOutcome, BirthOutcome } from './fixture-adapter.ts';
export type Stage = 'account' | 'verification' | 'eligibility' | 'birth' | 'remaining' | 'restricted' | 'eligible';
export type Scenario = 'new' | 'eligible' | 'underage' | 'unknown_policy' | 'stale_consent' | 'withdrawn_consent' | 'suspended' | 'deletion_pending';
export interface OnboardingSnapshot {
  readonly generation: number;
  readonly birthDraftRevision: number;
  readonly account: AccountAccess | null;
  readonly email: string | null;
  readonly busy: boolean;
  readonly error: string | null;
  readonly message: string | null;
  readonly stage: Stage;
  readonly adult: PredicateOutcome;
  readonly adultBirthDate: string | null;
  readonly consent: OnboardingEligibility;
  readonly birth: OwnBirthInput | null;
  readonly checkpointAvailable: boolean;
  readonly recoveryReady: boolean;
}
type Checkpoint = { format: 'gapp-synthetic-onboarding-1'; generation: number; revision: number;
  accountId: string; accountVersion: number; adultBirthDate: string | null;
  consent: OnboardingEligibility; birth: OwnBirthInput | null };
type StoreOptions = { isDevelopment: boolean; mode: string | undefined; clock?: FixtureClock; pause?: () => Promise<void> };
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
function freeze<T>(value: T): T {
  if (value && typeof value === 'object') {
    Object.values(value).forEach(freeze);
    Object.freeze(value);
  }
  return value;
}
const blankConsent = (): OnboardingEligibility => ({ kind: 'onboarding', version: 1, state: 'required',
  requirements: ['verify_identity', 'adult_policy', 'consent', 'profile'], policy_version: null });

/** Owner-only in-memory presentation state. It is never a server authorization source. */
export class OnboardingStore {
  readonly profiles: ProfileStore;
  readonly media: MediaStore;
  private synchronizingProfiles = false;
  private adapter: OnboardingAdapter;
  private clock: FixtureClock;
  private policy: AdultPolicy | null = FIXTURE_POLICY;
  private generation = 0;
  private birthDraftRevision = 0;
  private revision = 0;
  private operation = 0;
  private sequence = 0;
  private checkpoint: Checkpoint | null = null;
  private listeners = new Set<() => void>();
  private snapshot: OnboardingSnapshot;

  constructor(adapter: OnboardingAdapter, options: StoreOptions) {
    if (!options.isDevelopment || options.mode !== 'fixture' || adapter.kind !== 'fixture') {
      throw new Error('Synthetic onboarding requires an explicit development fixture runtime.');
    }
    this.adapter = adapter;
    this.clock = options.clock ?? FIXTURE_CLOCK;
    this.snapshot = this.empty();
    this.profiles = createFixtureProfileStore(options);
    this.media = new MediaStore({ ...options, now: () => this.clock().getTime() }, collection => this.profiles.synchronizeMedia(collection));
    this.profiles.bindMedia(() => this.media.approvedCollection(), () => this.media.restrictApproved());
    this.profiles.subscribe(() => {
      if (this.synchronizingProfiles) return;
      // Profile/preference/visibility changes cannot restore an older checkpoint
      // or accept a pending onboarding permission based on an earlier revision.
      this.checkpoint = null; this.revision += 1; this.operation += 1;
      this.adapter.cancelPending();
      this.publish({ busy: false });
    });
  }

  private empty(): OnboardingSnapshot {
    return freeze({ generation: this.generation, birthDraftRevision: this.birthDraftRevision, account: null, email: null, busy: false, error: null,
      message: null, stage: 'account', adult: 'unknown', adultBirthDate: null, consent: blankConsent(),
      birth: null, checkpointAvailable: false, recoveryReady: false });
  }
  readonly getSnapshot = (): OnboardingSnapshot => this.snapshot;
  readonly subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener);
    return () => { this.listeners.delete(listener); };
  };

  private derive(value: OnboardingSnapshot): OnboardingSnapshot {
    const account = value.account;
    let stage: Stage = 'account';
    const adult = adultOutcome(value.adultBirthDate, this.policy, this.clock);
    const consentCurrent = this.policy !== null && value.consent.state === 'accepted' && value.consent.policy_version === this.policy.version;
    const requirements: OnboardingEligibility['requirements'] = [];
    if (!account || account.state === 'unverified') requirements.push('verify_identity');
    if (adult !== 'pass') requirements.push('adult_policy');
    if (!consentCurrent) requirements.push('consent');
    if (!this.policy) requirements.push('region_policy');
    if (!this.profiles.getSnapshot().canDiscover) requirements.push('profile');
    if (account?.session_state === 'valid') {
      if (['suspended', 'deletion_pending', 'deleted'].includes(account.state)) stage = 'restricted';
      else if (account.state === 'unverified') stage = 'verification';
      else if (adult !== 'pass' || !consentCurrent) stage = 'eligibility';
      else if (this.profiles.getSnapshot().canDiscover) stage = 'eligible';
      else stage = value.birth ? 'remaining' : 'birth';
    }
    return { ...value, stage, adult, consent: { ...value.consent, requirements }, checkpointAvailable: this.checkpoint !== null };
  }

  private publish(patch: Partial<OnboardingSnapshot>): void {
    const next = { ...this.snapshot, ...clone(patch), generation: this.generation, birthDraftRevision: this.birthDraftRevision };
    this.synchronizeProfiles(next);
    this.snapshot = freeze(this.derive(next));
    this.listeners.forEach(listener => listener());
  }
  private synchronizeProfiles(value: OnboardingSnapshot): void {
    this.synchronizingProfiles = true;
    try {
      const authority = { ownerId: value.account?.account_id ?? null, generation: this.generation,
        accountVersion: value.account?.version ?? 0, accountState: value.account?.state ?? 'none',
        sessionState: value.account?.session_state ?? 'none', adult: adultOutcome(value.adultBirthDate, this.policy, this.clock) === 'pass',
        consentCurrent: this.policy !== null && value.consent.state === 'accepted' && value.consent.policy_version === this.policy.version,
        sourceRevision: this.birthDraftRevision, consentRevision: `${value.consent.version}:${value.consent.policy_version ?? 'none'}` };
      this.profiles.synchronize(authority);
      this.media.synchronize(authority);
    } finally { this.synchronizingProfiles = false; }
  }
  private mutate(patch: Partial<OnboardingSnapshot>): void {
    this.adapter.cancelPending();
    this.revision += 1; this.operation += 1; this.checkpoint = null;
    this.publish({ busy: false, error: null, message: null, ...patch });
  }
  private fail(message: string): void { this.publish({ error: message, message: null }); }
  private ownerReady(): boolean {
    return this.snapshot.account?.state === 'active' && this.snapshot.account.session_state === 'valid';
  }
  private context() {
    if (!this.snapshot.account) throw new FixtureFailure('stale');
    return { generation: this.generation, accountId: this.snapshot.account.account_id };
  }
  private key(): string { this.sequence += 1; return `55555555-5555-4555-8555-${this.sequence.toString().padStart(12, '0')}`; }
  private async run<T>(work: () => Promise<T>, accept: (value: T) => void, failure?: (error: unknown) => void): Promise<void> {
    if (this.snapshot.busy) return;
    const generation = this.generation, revision = this.revision, operation = ++this.operation;
    this.publish({ busy: true, error: null, message: null });
    try {
      const result = await work();
      if (generation !== this.generation || revision !== this.revision || operation !== this.operation) return;
      accept(result);
    } catch (error) {
      if (generation !== this.generation || revision !== this.revision || operation !== this.operation) return;
      this.adapter.cancelPending();
      failure?.(error);
      this.publish({ error: error instanceof FixtureFailure ? error.message : 'The adapter could not complete this request. Retry when available.' });
    } finally {
      if (generation === this.generation && operation === this.operation) this.publish({ busy: false });
    }
  }
  private clear(): void {
    this.adapter.invalidate(); this.generation += 1; this.revision += 1; this.operation += 1;
    this.checkpoint = null; this.policy = FIXTURE_POLICY;
    this.snapshot = this.empty();
    this.synchronizeProfiles(this.snapshot);
    this.listeners.forEach(listener => listener());
  }

  async account(mode: AccountMode, email: string, password: string, outcome: FixtureOutcome = 'success'): Promise<void> {
    this.clear();
    const generation = this.generation;
    await this.run(() => this.adapter.account(mode, email, password, generation, outcome), value => {
      if (!validateAccountAccess(value) || !['unverified', 'suspended', 'deletion_pending', 'deleted'].includes(value.state) ||
          value.session_state !== 'valid') throw new FixtureFailure('invalid');
      this.mutate({ account: value, email });
    });
  }
  async verify(outcome: FixtureOutcome = 'success'): Promise<void> {
    if (this.snapshot.account?.state !== 'unverified' || this.snapshot.account.session_state !== 'valid') {
      this.fail('Start a current unverified fixture account first.'); return;
    }
    const context = this.context();
    await this.run(() => this.adapter.verify(context, outcome), value => {
      if (!validateAccountAccess(value) || value.account_id !== context.accountId || value.state !== 'active' || value.session_state !== 'valid') throw new FixtureFailure('invalid');
      this.mutate({ account: value, message: 'Synthetic email verification completed. Continue with development eligibility.' });
    });
  }
  async resend(outcome: FixtureOutcome = 'success'): Promise<void> {
    if (!this.snapshot.account || this.snapshot.account.state !== 'unverified') { this.fail('Start an unverified fixture account first.'); return; }
    const context = this.context();
    await this.run(() => this.adapter.resend(context, outcome), () => this.publish({ message: 'A fresh synthetic verification challenge is available. No email was sent.' }));
  }
  async requestRecovery(email: string, outcome: FixtureOutcome = 'success'): Promise<void> {
    this.clear();
    const generation = this.generation;
    await this.run(() => this.adapter.requestRecovery(email, generation, outcome), () => this.publish({ recoveryReady: true, message: RECOVERY_MESSAGE }));
  }
  async resetPassword(password: string, outcome: FixtureOutcome = 'success'): Promise<boolean> {
    if (!this.snapshot.recoveryReady) { this.fail('Request a synthetic recovery challenge first.'); return false; }
    const generation = this.generation;
    let accepted = false;
    await this.run(() => this.adapter.resetPassword(password, generation, outcome), () => {
      this.clear(); this.publish({ message: 'Synthetic password reset completed. Sign in again. No real password was changed.' });
      accepted = true;
    }, error => {
      if (error instanceof FixtureFailure && ['expired', 'invalid'].includes(error.code)) this.publish({ recoveryReady: false });
    });
    return accepted && this.generation === generation + 1 && this.snapshot.account === null && !this.snapshot.recoveryReady;
  }
  logout(): void { this.clear(); this.publish({ message: 'Signed out. Private fixture drafts and synthetic challenges were cleared.' }); }
  expire(): void {
    const account = this.snapshot.account;
    this.clear();
    if (account) this.publish({ account: { ...account, version: account.version + 1, session_state: 'expired' }, message: 'The synthetic session expired. Sign in again.' });
  }
  setAdultDate(date: string): void {
    if (!this.ownerReady()) { this.fail('Verify a current account before eligibility.'); return; }
    if (!validCivilDate(date) || !Number.isFinite(this.clock().getTime()) || date > this.clock().toISOString().slice(0, 10)) {
      this.fail('Enter a real civil date that is not in the future.'); return;
    }
    // Invalidate accepted and unsaved forms only when authoritative birth facts change.
    if (this.snapshot.adultBirthDate !== date) this.birthDraftRevision += 1;
    // A changed eligibility date cannot retain a conflicting private birth draft or its mapping.
    if (this.snapshot.birth && this.snapshot.birth.input.birth_date !== date) {
      this.adapter.discardBirth(this.context());
      this.mutate({ adultBirthDate: date, birth: null, message: 'The date changed. Re-enter private birth input; its previous mapping was cleared.' });
      return;
    }
    this.mutate({ adultBirthDate: date });
  }
  setConsent(accepted: boolean): void {
    if (!this.ownerReady()) { this.fail('Verify a current account before consent.'); return; }
    if (!this.policy) { this.fail('Development policy is unresolved. Discovery remains unavailable.'); return; }
    if (accepted && this.snapshot.consent.state === 'accepted') {
      if (this.snapshot.consent.policy_version === this.policy.version) this.publish({ message: 'The current development consent is already accepted.' });
      else this.fail('Consent for the current policy must be requested before acceptance.');
      return;
    }
    const intent: ConsentIntent = { operation: 'consent', meta: { expected_version: this.snapshot.consent.version, idempotency_key: this.key() },
      policy_version: this.policy.version, decision: accepted ? 'accepted' : 'withdrawn' };
    if (!validateConsentIntent(intent)) { this.fail('The consent request is invalid.'); return; }
    if (!accepted && this.snapshot.consent.state !== 'accepted') { this.fail('There is no accepted consent to withdraw.'); return; }
    const consent: OnboardingEligibility = { ...this.snapshot.consent, version: this.snapshot.consent.version + 1,
      state: intent.decision, policy_version: intent.policy_version };
    if (!validateOnboardingEligibility(consent)) { this.fail('The consent response is invalid.'); return; }
    this.mutate({ consent });
  }
  async saveBirth(input: BirthInput, outcome: BirthOutcome = 'pending'): Promise<void> {
    if (!this.ownerReady() || this.snapshot.adult !== 'pass' || this.snapshot.consent.state !== 'accepted' ||
        !this.policy || this.snapshot.consent.policy_version !== this.policy.version) { this.fail('Complete current adult eligibility and consent first.'); return; }
    if (!birthInputValid(input, this.clock)) { this.fail('Check the civil birth date, time precision and place. Future dates are unavailable.'); return; }
    const context = this.context();
    const intent: BirthInputIntent = { operation: 'birth_input', meta: { idempotency_key: this.key(), expected_version: this.snapshot.birth?.version ?? 0 }, input };
    await this.run(() => this.adapter.saveBirth(context, intent, outcome), value => {
      if (!validateOwnBirthInput(value) || value.resolution === 'resolved' || value.mapping_version !== null ||
          !birthInputValid(value.input, this.clock) || JSON.stringify(value.input) !== JSON.stringify(input)) throw new FixtureFailure('invalid');
      this.adapter.acknowledgeBirth(context, value.version);
      this.birthDraftRevision += 1;
      this.mutate({ birth: value, adultBirthDate: value.input.birth_date,
        message: 'Private synthetic birth input saved. Chart resolution and profile completion remain separate.' });
    });
  }
  async retryBirth(outcome: BirthOutcome = 'pending'): Promise<void> {
    if (!this.ownerReady() || this.snapshot.adult !== 'pass' || this.snapshot.consent.state !== 'accepted' ||
        !this.policy || this.snapshot.consent.policy_version !== this.policy.version || this.snapshot.birth?.resolution !== 'unavailable') {
      this.fail('Retry requires current eligibility and an unavailable birth resolution.'); return;
    }
    const context = this.context(), version = this.snapshot.birth.version;
    await this.run(() => this.adapter.retryBirth(context, version, outcome), value => {
      if (!validateOwnBirthInput(value) || value.mapping_version !== null || value.resolution === 'resolved') throw new FixtureFailure('invalid');
      this.adapter.acknowledgeBirth(context, value.version);
      this.mutate({ birth: value, message: 'Synthetic resolution retried. No engine was contacted.' });
    });
  }

  saveCheckpoint(): unknown {
    if (!this.ownerReady() || this.snapshot.busy || this.profiles.getSnapshot().busy) { this.fail('A current verified fixture session is required to save a navigation checkpoint.'); return null; }
    this.checkpoint = { format: 'gapp-synthetic-onboarding-1', generation: this.generation, revision: this.revision,
      accountId: this.snapshot.account!.account_id, accountVersion: this.snapshot.account!.version,
      adultBirthDate: this.snapshot.adultBirthDate, consent: clone(this.snapshot.consent), birth: clone(this.snapshot.birth) };
    this.publish({ message: 'Synthetic checkpoint saved in this session only. Closing the process clears it.' });
    return clone(this.checkpoint);
  }
  restoreCheckpoint(candidate: unknown = this.checkpoint): boolean {
    // A parsed serialized copy is accepted only if it matches a checkpoint issued by this live instance.
    // It cannot grant identity, reinstate an old consent, or restore an old input/mapping revision.
    const saved = this.checkpoint;
    let matches = false;
    try { matches = JSON.stringify(candidate) === JSON.stringify(saved); } catch { /* Invalid serialized input is rejected below. */ }
    if (!saved || !this.ownerReady() || this.snapshot.busy || saved.generation !== this.generation || saved.revision !== this.revision ||
        saved.accountId !== this.snapshot.account!.account_id || saved.accountVersion !== this.snapshot.account!.version ||
        !matches || !validateOnboardingEligibility(saved.consent) ||
        (saved.birth !== null && (!validateOwnBirthInput(saved.birth) || !birthInputValid(saved.birth.input, this.clock))) ||
        (saved.consent.state === 'accepted' && saved.consent.policy_version !== this.policy?.version)) {
      this.fail('This synthetic checkpoint is stale, invalid, or belongs to another session. Continue from current state.'); return false;
    }
    this.publish({ adultBirthDate: saved.adultBirthDate, consent: clone(saved.consent), birth: clone(saved.birth),
      message: 'Validated synthetic checkpoint restored within this account and session.' });
    return true;
  }
  scenario(name: Scenario): void {
    this.clear();
    if (name === 'new') { this.adapter.seed(null, this.generation); return; }
    const account: AccountAccess = { kind: 'account_access', account_id: FIXTURE_ACCOUNT_IDS.alex, version: 1,
      state: name === 'suspended' ? 'suspended' : name === 'deletion_pending' ? 'deletion_pending' : 'active', session_state: 'valid' };
    this.adapter.seed(account, this.generation);
    this.policy = name === 'unknown_policy' ? null : FIXTURE_POLICY;
    const consent: OnboardingEligibility = { kind: 'onboarding', version: 1,
      state: name === 'withdrawn_consent' ? 'withdrawn' : name === 'stale_consent' ? 'required' : 'accepted',
      policy_version: name === 'stale_consent' ? 'development-consent-old' : this.policy?.version ?? null, requirements: [] };
    this.mutate({ account, email: 'alex@example.invalid', adultBirthDate: name === 'underage' ? '2010-09-23' : '1990-06-15',
      consent, message: 'Explicit development scenario loaded. This is synthetic state, not a production permission.' });
    if (name === 'eligible') { this.media.seedEligible(); this.profiles.seedEligible(); }
  }
}

export function createFixtureOnboardingStore(options: StoreOptions & { pause?: () => Promise<void> }): OnboardingStore {
  return new OnboardingStore(createFixtureAdapter(options), options);
}
