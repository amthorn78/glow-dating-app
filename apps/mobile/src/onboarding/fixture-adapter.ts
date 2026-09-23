import type { AccountAccess, BirthInputIntent, OwnBirthInput } from '../contracts/generated/gapp-api-v1.ts';
import { validateBirthInputIntent, validateOwnBirthInput } from '../contracts/generated/validators.js';
import { birthInputValid, FIXTURE_CLOCK, type FixtureClock } from './policy.ts';

export type FixtureOutcome = 'success' | 'invalid' | 'expired' | 'wrong_context' | 'replayed' | 'error' | 'rate_limited';
export type BirthOutcome = 'pending' | 'ambiguous' | 'unavailable' | 'unsupported';
export type AccountMode = 'sign_in' | 'register';
export type AccountContext = Readonly<{ generation: number; accountId: string }>;
export const FIXTURE_PASSWORD = 'fixture-passphrase';
export const RECOVERY_MESSAGE = 'If this address can receive a recovery message, the next steps are available through the configured service. This preview sends no email.';
export const FIXTURE_ACCOUNT_IDS = Object.freeze({
  alex: '11111111-1111-4111-8111-111111111111',
  sam: '22222222-2222-4222-8222-222222222222',
});

export class FixtureFailure extends Error {
  code: 'invalid' | 'expired' | 'unavailable' | 'rate_limited' | 'stale' | 'cancelled';
  constructor(code: FixtureFailure['code']) {
    super(code === 'rate_limited' ? 'Too many fixture attempts. Retry when the fixture becomes available.' :
      code === 'expired' ? 'This synthetic challenge expired. Request a new one.' :
      code === 'stale' ? 'The fixture changed. Reload its current state and try again.' :
      code === 'unavailable' ? 'The fixture adapter is unavailable. You can retry.' :
      'The synthetic request could not be completed. Check the fixture and try again.');
    this.name = 'FixtureFailure';
    this.code = code;
  }
}

/** Adapter is app-local development substitution. It defines no allauth endpoints or credentials. */
export interface OnboardingAdapter {
  readonly kind: 'fixture';
  account(mode: AccountMode, email: string, password: string, generation: number, outcome: FixtureOutcome): Promise<AccountAccess>;
  verify(context: AccountContext, outcome: FixtureOutcome): Promise<AccountAccess>;
  resend(context: AccountContext, outcome: FixtureOutcome): Promise<void>;
  requestRecovery(email: string, generation: number, outcome: FixtureOutcome): Promise<void>;
  resetPassword(password: string, generation: number, outcome: FixtureOutcome): Promise<void>;
  saveBirth(context: AccountContext, intent: BirthInputIntent, outcome: BirthOutcome): Promise<OwnBirthInput>;
  retryBirth(context: AccountContext, expectedVersion: number, outcome: BirthOutcome): Promise<OwnBirthInput>;
  acknowledgeBirth(context: AccountContext, version: number): void;
  cancelPending(): void;
  discardBirth(context: AccountContext): void;
  invalidate(): void;
  seed(account: AccountAccess | null, generation: number): void;
}

type Challenge = { generation: number; accountId: string | null; expires: number; used: boolean };
type Session = { account: AccountAccess; generation: number; birth: OwnBirthInput | null };
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

export function createFixtureAdapter(options: {
  isDevelopment: boolean; mode: string | undefined; clock?: FixtureClock; pause?: () => Promise<void>;
}): OnboardingAdapter {
  if (!options.isDevelopment || options.mode !== 'fixture') throw new Error('Synthetic onboarding requires an explicit development fixture runtime.');
  const clock = options.clock ?? FIXTURE_CLOCK;
  const pause = options.pause ?? (() => Promise.resolve());
  let epoch = 0;
  let session: Session | null = null;
  // Scenario restrictions outlive session invalidation, but only in this fixture instance.
  let restrictedFixture: AccountAccess | null = null;
  let verification: Challenge | null = null;
  let recovery: Challenge | null = null;
  const birthReceipts = new Map<string, { intent: string; result: OwnBirthInput }>();
  let unacceptedBirth: { previous: OwnBirthInput | null; receipts: typeof birthReceipts } | null = null;
  const beginBirth = () => {
    if (unacceptedBirth) throw new FixtureFailure('stale');
    unacceptedBirth = { previous: clone(session!.birth), receipts: new Map(birthReceipts) };
  };
  const cancelBirth = () => {
    if (unacceptedBirth) {
      if (session) session.birth = unacceptedBirth.previous;
      birthReceipts.clear();
      unacceptedBirth.receipts.forEach((receipt, key) => birthReceipts.set(key, receipt));
      unacceptedBirth = null;
    }
  };
  const now = () => clock().getTime();
  const challenge = (generation: number, accountId: string | null): Challenge => ({ generation, accountId, expires: now() + 60_000, used: false });
  const delay = async () => {
    const started = epoch;
    await pause();
    if (started !== epoch) throw new FixtureFailure('cancelled');
  };
  const outcomeCheck = (outcome: FixtureOutcome) => {
    if (outcome === 'error') throw new FixtureFailure('unavailable');
    if (outcome === 'rate_limited') throw new FixtureFailure('rate_limited');
    if (outcome === 'expired') throw new FixtureFailure('expired');
    if (outcome !== 'success') throw new FixtureFailure('invalid');
  };
  const requireSession = (context: AccountContext) => {
    if (!session || session.generation !== context.generation || session.account.account_id !== context.accountId ||
        session.account.session_state !== 'valid' || !['unverified', 'active'].includes(session.account.state)) {
      throw new FixtureFailure('stale');
    }
    return session;
  };
  const consume = (value: Challenge | null, generation: number, accountId: string | null, outcome: FixtureOutcome) => {
    if (!value || value.used || value.generation !== generation || value.accountId !== accountId) throw new FixtureFailure('invalid');
    if (outcome === 'expired' || !Number.isFinite(now()) || now() >= value.expires) {
      value.expires = -Infinity;
      throw new FixtureFailure('expired');
    }
    outcomeCheck(outcome);
    value.used = true;
  };
  const adapter: OnboardingAdapter = {
    kind: 'fixture',
    async account(_mode, email, password, generation, outcome) {
      await delay();
      outcomeCheck(outcome);
      if (password !== FIXTURE_PASSWORD || !/^(alex|sam)@example\.invalid$/.test(email)) throw new FixtureFailure('invalid');
      const accountId = email.startsWith('alex@') ? FIXTURE_ACCOUNT_IDS.alex : FIXTURE_ACCOUNT_IDS.sam;
      const restriction = restrictedFixture?.account_id === accountId ? restrictedFixture : null;
      const account: AccountAccess = { kind: 'account_access', account_id: accountId,
        version: restriction ? restriction.version + 1 : 1, state: restriction?.state ?? 'unverified', session_state: 'valid' };
      unacceptedBirth = null; birthReceipts.clear();
      session = { account, generation, birth: null };
      verification = account.state === 'unverified' ? challenge(generation, account.account_id) : null;
      recovery = null;
      return clone(account);
    },
    async verify(context, outcome) {
      const pendingChallenge = verification;
      await delay();
      const current = requireSession(context);
      if (pendingChallenge !== verification) throw new FixtureFailure('stale');
      consume(pendingChallenge, context.generation, context.accountId, outcome);
      if (current.account.state !== 'unverified') throw new FixtureFailure('invalid');
      current.account = { ...current.account, version: current.account.version + 1, state: 'active' };
      return clone(current.account);
    },
    async resend(context, outcome) {
      await delay(); outcomeCheck(outcome);
      const current = requireSession(context);
      if (current.account.state !== 'unverified') throw new FixtureFailure('invalid');
      verification = challenge(context.generation, context.accountId);
    },
    async requestRecovery(email, generation, outcome) {
      await delay(); outcomeCheck(outcome);
      // Every syntactically accepted fixture address has the same receipt and synthetic flow.
      if (!/^[a-z0-9._+-]{1,64}@example\.invalid$/.test(email)) throw new FixtureFailure('invalid');
      recovery = challenge(generation, null);
    },
    async resetPassword(password, generation, outcome) {
      const pendingChallenge = recovery;
      await delay();
      if (password !== FIXTURE_PASSWORD) throw new FixtureFailure('invalid');
      if (pendingChallenge !== recovery) throw new FixtureFailure('stale');
      consume(pendingChallenge, generation, null, outcome);
      unacceptedBirth = null; birthReceipts.clear();
      session = null; verification = null;
      // Recovery never creates an authenticated session. A fresh sign-in is required.
    },
    async saveBirth(context, intent, outcome) {
      await delay();
      const current = requireSession(context);
      if (current.account.state !== 'active' || !['pending', 'ambiguous', 'unavailable', 'unsupported'].includes(outcome) ||
          !validateBirthInputIntent(intent) || !birthInputValid(intent.input, clock)) throw new FixtureFailure('invalid');
      const receiptKey = `${context.generation}:${context.accountId}:${intent.meta.idempotency_key}`;
      const canonical = JSON.stringify([intent.meta.expected_version, intent.input.birth_date, intent.input.local_time,
        intent.input.time_precision, intent.input.place_label, intent.input.timezone_name, intent.input.timezone_provenance]);
      const prior = birthReceipts.get(receiptKey);
      if (prior) {
        if (prior.intent !== canonical || current.birth?.version !== prior.result.version) throw new FixtureFailure('stale');
        return clone(prior.result);
      }
      if (intent.meta.expected_version !== (current.birth?.version ?? 0)) throw new FixtureFailure('stale');
      beginBirth();
      const birth: OwnBirthInput = { kind: 'birth_input', input_id: context.accountId === FIXTURE_ACCOUNT_IDS.alex ?
        '33333333-3333-4333-8333-333333333333' : '44444444-4444-4444-8444-444444444444',
      version: (current.birth?.version ?? 0) + 1, input: clone(intent.input), resolution: 'pending', mapping_version: null };
      if (!validateOwnBirthInput(birth)) throw new FixtureFailure('invalid');
      current.birth = birth;
      // Submit/correct invalidates mapping first. The controlled fixture resolver then supplies a non-ready result.
      current.birth = { ...birth, resolution: outcome };
      birthReceipts.set(receiptKey, { intent: canonical, result: clone(current.birth) });
      return clone(current.birth);
    },
    async retryBirth(context, expectedVersion, outcome) {
      await delay();
      const current = requireSession(context);
      if (!current.birth || current.birth.version !== expectedVersion || current.birth.resolution !== 'unavailable' ||
          !['pending', 'ambiguous', 'unavailable', 'unsupported'].includes(outcome)) throw new FixtureFailure('stale');
      beginBirth();
      current.birth = { ...current.birth, version: current.birth.version + 1, resolution: 'pending', mapping_version: null };
      current.birth = { ...current.birth, resolution: outcome };
      return clone(current.birth);
    },
    acknowledgeBirth(context, version) {
      const current = requireSession(context);
      if (current.birth?.version !== version) throw new FixtureFailure('stale');
      unacceptedBirth = null;
    },
    cancelPending() { epoch += 1; cancelBirth(); },
    discardBirth(context) { const current = requireSession(context); epoch += 1; cancelBirth(); current.birth = null; birthReceipts.clear(); },
    invalidate() { epoch += 1; unacceptedBirth = null; session = null; verification = null; recovery = null; birthReceipts.clear(); },
    seed(account, generation) {
      adapter.invalidate();
      restrictedFixture = account && ['suspended', 'deletion_pending', 'deleted'].includes(account.state) ? clone(account) : null;
      if (!account) return;
      session = { account: clone(account), generation, birth: null };
      verification = account.state === 'unverified' ? challenge(generation, account.account_id) : null;
    },
  };
  return adapter;
}
