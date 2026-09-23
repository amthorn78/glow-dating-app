import assert from 'node:assert/strict';
import test from 'node:test';
import type { BirthInput, BirthInputIntent } from '../contracts/generated/gapp-api-v1.ts';
import { createFixtureAdapter, FIXTURE_ACCOUNT_IDS, FIXTURE_PASSWORD, FixtureFailure,
  type FixtureOutcome, type OnboardingAdapter } from './fixture-adapter.ts';
import { adultOutcome, birthInputValid, FIXTURE_CLOCK, FIXTURE_POLICY } from './policy.ts';
import { createFixtureOnboardingStore, OnboardingStore, RECOVERY_MESSAGE } from './store.ts';
import { canAccessRoute, sanitizeDestination } from './routes.ts';

const options = { isDevelopment: true, mode: 'fixture' };
const birth = (extra: Partial<BirthInput> = {}): BirthInput => ({ birth_date: '1990-06-15', local_time: null,
  time_precision: 'unknown', place_label: 'Fictional Harbor', timezone_name: null, timezone_provenance: null, ...extra });
const intent = (extra: Partial<BirthInputIntent> = {}): BirthInputIntent => ({ operation: 'birth_input',
  meta: { idempotency_key: '55555555-5555-4555-8555-555555555555', expected_version: 0 }, input: birth(), ...extra });
async function verified(store = createFixtureOnboardingStore(options)): Promise<OnboardingStore> {
  await store.account('register', 'alex@example.invalid', FIXTURE_PASSWORD);
  await store.verify(); return store;
}
async function ready(store = createFixtureOnboardingStore(options)): Promise<OnboardingStore> {
  await verified(store); store.setAdultDate('1990-06-15'); store.setConsent(true); return store;
}
function controllable() {
  let hold = false;
  const pending: (() => void)[] = [];
  return { pause: () => hold ? new Promise<void>(resolve => pending.push(resolve)) : Promise.resolve(),
    hold() { hold = true; }, release() { hold = false; pending.splice(0).forEach(resolve => resolve()); } };
}

test('fixture factories reject release or unspecified modes and real credentials', async () => {
  for (const input of [{ isDevelopment: false, mode: 'fixture' }, { isDevelopment: true, mode: undefined }, { isDevelopment: true, mode: 'production' }]) {
    assert.throws(() => createFixtureOnboardingStore(input));
    assert.throws(() => createFixtureAdapter(input));
  }
  const store = createFixtureOnboardingStore(options);
  await store.account('register', 'person@example.com', FIXTURE_PASSWORD);
  assert.equal(store.getSnapshot().account, null);
  await store.account('sign_in', 'alex@example.invalid', 'not-the-synthetic-password');
  assert.equal(store.getSnapshot().account, null);
  assert.doesNotMatch(JSON.stringify(store.getSnapshot()), /not-the-synthetic-password|person@example.com/);
});

test('register and sign-in journeys stop at the honest profile-incomplete state', async () => {
  for (const mode of ['register', 'sign_in'] as const) {
    const store = createFixtureOnboardingStore(options);
    await store.account(mode, 'alex@example.invalid', FIXTURE_PASSWORD);
    assert.equal(store.getSnapshot().stage, 'verification');
    await store.verify(); assert.equal(store.getSnapshot().stage, 'eligibility');
    store.setAdultDate('1990-06-15'); store.setConsent(true);
    assert.equal(store.getSnapshot().stage, 'birth');
    await store.saveBirth(birth());
    assert.equal(store.getSnapshot().stage, 'remaining');
    assert.deepEqual(store.getSnapshot().consent.requirements, ['profile']);
    assert.equal(canAccessRoute('/recommended', store.getSnapshot()), false);
    assert.equal(canAccessRoute('/explore', store.getSnapshot()), false);
    assert.equal(store.getSnapshot().birth?.mapping_version, null);
    assert.doesNotMatch(JSON.stringify(store.getSnapshot()), /fixture-passphrase|engine_reference|session_token/);
  }
});

test('adult boundary uses the explicit policy and clock, including leap-day policy', () => {
  assert.equal(adultOutcome('2008-09-23', FIXTURE_POLICY, FIXTURE_CLOCK), 'pass');
  assert.equal(adultOutcome('2008-09-24', FIXTURE_POLICY, FIXTURE_CLOCK), 'fail');
  assert.equal(adultOutcome('2008-02-29', FIXTURE_POLICY, () => new Date('2026-02-28T23:59:59Z')), 'fail');
  assert.equal(adultOutcome('2008-02-29', FIXTURE_POLICY, () => new Date('2026-03-01T00:00:00Z')), 'pass');
  for (const date of [null, '2027-01-01', '2000-02-30', '0000-01-01', '1990-01-01\n']) assert.equal(adultOutcome(date, FIXTURE_POLICY, FIXTURE_CLOCK), 'unknown');
  assert.equal(adultOutcome('1990-01-01', null, FIXTURE_CLOCK), 'unknown');
  assert.equal(adultOutcome('1990-01-01', FIXTURE_POLICY, () => new Date('invalid')), 'unknown');
});

test('verification outcomes fail closed and retry/resend can succeed', async () => {
  for (const outcome of ['invalid', 'expired', 'wrong_context', 'replayed', 'error', 'rate_limited'] as FixtureOutcome[]) {
    const store = createFixtureOnboardingStore(options);
    await store.account('register', 'alex@example.invalid', FIXTURE_PASSWORD);
    await store.verify(outcome);
    assert.equal(store.getSnapshot().account?.state, 'unverified');
    assert.equal(store.getSnapshot().stage, 'verification');
    assert.ok(store.getSnapshot().error);
    await store.resend(); await store.verify();
    assert.equal(store.getSnapshot().stage, 'eligibility');
  }
});

test('actual challenge time expiry, wrong account/generation and replay are enforced by adapter', async () => {
  let now = new Date('2026-09-23T12:00:00Z');
  const adapter = createFixtureAdapter({ ...options, clock: () => now });
  await adapter.account('register', 'alex@example.invalid', FIXTURE_PASSWORD, 1, 'success');
  const context = { generation: 1, accountId: FIXTURE_ACCOUNT_IDS.alex };
  await assert.rejects(adapter.verify({ ...context, accountId: FIXTURE_ACCOUNT_IDS.sam }, 'success'), FixtureFailure);
  await assert.rejects(adapter.verify({ ...context, generation: 2 }, 'success'), FixtureFailure);
  now = new Date('2026-09-23T12:01:00Z');
  await assert.rejects(adapter.verify(context, 'success'), (error: unknown) => error instanceof FixtureFailure && error.code === 'expired');
  await adapter.resend(context, 'success');
  const account = await adapter.verify(context, 'success');
  assert.equal(account.state, 'active');
  await assert.rejects(adapter.verify(context, 'success'), FixtureFailure);
});

test('recovery receipts are neutral for configured and unrelated fictional addresses', async () => {
  const snapshots = [];
  for (const email of ['alex@example.invalid', 'not-an-account@example.invalid']) {
    const store = createFixtureOnboardingStore(options);
    await store.requestRecovery(email);
    assert.equal(store.getSnapshot().message, RECOVERY_MESSAGE);
    snapshots.push(store.getSnapshot());
    await store.resetPassword(FIXTURE_PASSWORD);
    assert.equal(store.getSnapshot().account, null);
    assert.equal(store.getSnapshot().recoveryReady, false);
    assert.equal(store.getSnapshot().stage, 'account');
  }
  assert.deepEqual(snapshots[0], snapshots[1]);
});

test('invalid or expired recovery closes challenge presentation; transport errors permit retry', async () => {
  for (const outcome of ['invalid', 'expired', 'wrong_context', 'replayed'] as FixtureOutcome[]) {
    const store = createFixtureOnboardingStore(options);
    await store.requestRecovery('alex@example.invalid');
    await store.resetPassword(FIXTURE_PASSWORD, outcome);
    assert.equal(store.getSnapshot().recoveryReady, false);
    assert.equal(canAccessRoute('/reset-password', store.getSnapshot()), false);
    await store.requestRecovery('alex@example.invalid');
    await store.resetPassword(FIXTURE_PASSWORD);
    assert.match(store.getSnapshot().message!, /Sign in again/);
  }
  const store = createFixtureOnboardingStore(options);
  await store.requestRecovery('alex@example.invalid', 'rate_limited');
  assert.equal(store.getSnapshot().recoveryReady, false);
  await store.requestRecovery('alex@example.invalid');
  await store.resetPassword(FIXTURE_PASSWORD, 'error');
  assert.equal(store.getSnapshot().recoveryReady, true);
  await store.resetPassword(FIXTURE_PASSWORD);
  assert.equal(store.getSnapshot().error, null);
});

test('actual recovery challenge rejects wrong generation, elapsed expiry and replay', async () => {
  let time = new Date('2026-09-23T12:00:00Z');
  const adapter = createFixtureAdapter({ ...options, clock: () => time });
  await adapter.requestRecovery('alex@example.invalid', 1, 'success');
  await assert.rejects(adapter.resetPassword(FIXTURE_PASSWORD, 2, 'success'), FixtureFailure);
  time = new Date('2026-09-23T12:01:00Z');
  await assert.rejects(adapter.resetPassword(FIXTURE_PASSWORD, 1, 'success'), (error: unknown) => error instanceof FixtureFailure && error.code === 'expired');
  await adapter.requestRecovery('alex@example.invalid', 1, 'success');
  await adapter.resetPassword(FIXTURE_PASSWORD, 1, 'success');
  await assert.rejects(adapter.resetPassword(FIXTURE_PASSWORD, 1, 'success'), FixtureFailure);
});

test('logout/expiry/scenario replacement discard pending verification results', async () => {
  for (const change of ['logout', 'expire', 'suspended', 'deletion_pending'] as const) {
    const gate = controllable();
    const store = createFixtureOnboardingStore({ ...options, pause: gate.pause });
    await store.account('register', 'alex@example.invalid', FIXTURE_PASSWORD);
    gate.hold(); const pending = store.verify();
    assert.equal(store.getSnapshot().busy, true);
    if (change === 'logout') store.logout(); else if (change === 'expire') store.expire(); else store.scenario(change);
    const before = store.getSnapshot(); gate.release(); await pending;
    assert.deepEqual(store.getSnapshot(), before);
    assert.equal(canAccessRoute('/birth', store.getSnapshot()), false);
  }
});

test('pending account and recovery results cannot resurrect logout or superseded identity', async () => {
  const gate = controllable();
  const store = createFixtureOnboardingStore({ ...options, pause: gate.pause });
  gate.hold(); const first = store.account('register', 'alex@example.invalid', FIXTURE_PASSWORD);
  store.logout(); gate.release(); await first;
  assert.equal(store.getSnapshot().account, null);
  gate.hold(); const old = store.account('register', 'alex@example.invalid', FIXTURE_PASSWORD);
  const next = store.account('register', 'sam@example.invalid', FIXTURE_PASSWORD);
  gate.release(); await Promise.all([old, next]);
  assert.equal(store.getSnapshot().account?.account_id, FIXTURE_ACCOUNT_IDS.sam);
  gate.hold(); const recovery = store.requestRecovery('sam@example.invalid');
  store.logout(); gate.release(); await recovery;
  assert.equal(store.getSnapshot().recoveryReady, false);
});

test('consent withdrawal cancels delayed private input without stale adapter mutations', async () => {
  const gate = controllable();
  const store = await ready(createFixtureOnboardingStore({ ...options, pause: gate.pause }));
  gate.hold(); const pending = store.saveBirth(birth(), 'unavailable');
  store.setConsent(false); gate.release(); await pending;
  assert.equal(store.getSnapshot().birth, null);
  assert.equal(store.getSnapshot().stage, 'eligibility');
  store.setConsent(true); await store.saveBirth(birth());
  assert.equal(store.getSnapshot().birth?.version, 1);
});

test('current consent repeats do not invent an accepted-to-accepted transition', async () => {
  const store = await ready();
  const version = store.getSnapshot().consent.version;
  store.setConsent(true); assert.equal(store.getSnapshot().consent.version, version);
  store.setConsent(false); assert.equal(store.getSnapshot().consent.state, 'withdrawn');
  store.setConsent(true); assert.equal(store.getSnapshot().consent.state, 'accepted');
});

test('underage, unknown, stale/withdrawn, restricted and unfinished fixtures deny discovery', () => {
  const store = createFixtureOnboardingStore(options);
  for (const scenario of ['underage', 'unknown_policy', 'stale_consent', 'withdrawn_consent', 'suspended', 'deletion_pending'] as const) {
    store.scenario(scenario);
    assert.equal(canAccessRoute('/recommended', store.getSnapshot()), false);
    assert.equal(canAccessRoute('/explore', store.getSnapshot()), false);
    assert.equal(canAccessRoute('/birth', store.getSnapshot()), false);
    if (scenario === 'unknown_policy') { store.setConsent(true); assert.equal(store.getSnapshot().adult, 'unknown'); }
  }
  store.scenario('stale_consent'); assert.equal(store.getSnapshot().consent.state, 'required');
  store.setConsent(true); assert.equal(store.getSnapshot().stage, 'birth');
  store.scenario('eligible'); assert.equal(store.getSnapshot().stage, 'eligible');
  assert.equal(canAccessRoute('/recommended', store.getSnapshot()), true);
  store.setConsent(false); assert.equal(canAccessRoute('/recommended', store.getSnapshot()), false);
});

test('known/approximate/unknown time preserves civil facts and unresolved timezone', async () => {
  for (const precision of ['known', 'approximate', 'unknown'] as const) {
    const store = await ready();
    const input = birth({ time_precision: precision, local_time: precision === 'unknown' ? null : '13:27:42' });
    await store.saveBirth(input);
    assert.deepEqual(store.getSnapshot().birth?.input, input);
    assert.equal(store.getSnapshot().birth?.mapping_version, null);
    assert.equal(store.getSnapshot().birth?.resolution, 'pending');
  }
});

test('invalid/future birth dates, malformed times and false precision are rejected', async () => {
  const store = await ready();
  for (const input of [birth({ birth_date: '2001-02-29' }), birth({ birth_date: '2026-09-24' }),
    birth({ local_time: '12:00:00' }), birth({ time_precision: 'known' }), birth({ local_time: '25:00:00', time_precision: 'approximate' }),
    birth({ place_label: '  ' }), birth({ timezone_name: 'UTC', timezone_provenance: null })]) {
    assert.equal(birthInputValid(input, FIXTURE_CLOCK), false);
    await store.saveBirth(input); assert.equal(store.getSnapshot().birth, null);
  }
});

test('birth changes invalidate resolution and version; unavailable retry remains non-ready', async () => {
  const store = await ready();
  await store.saveBirth(birth(), 'unavailable');
  assert.equal(store.getSnapshot().birth?.resolution, 'unavailable');
  await store.retryBirth('ambiguous');
  assert.equal(store.getSnapshot().birth?.resolution, 'ambiguous');
  assert.equal(store.getSnapshot().birth?.version, 2);
  await store.saveBirth(birth({ place_label: 'Another Fictional Place' }), 'unsupported');
  assert.equal(store.getSnapshot().birth?.version, 3);
  await store.saveBirth(birth({ place_label: 'Corrected Fictional Place' }));
  assert.equal(store.getSnapshot().birth?.resolution, 'pending');
  assert.equal(store.getSnapshot().birth?.mapping_version, null);
});

test('private birth age correction reevaluates adult, then supports safe correction', async () => {
  const store = await ready();
  await store.saveBirth(birth({ birth_date: '2010-06-15' }));
  assert.equal(store.getSnapshot().adult, 'fail');
  assert.equal(store.getSnapshot().stage, 'eligibility');
  assert.equal(canAccessRoute('/remaining', store.getSnapshot()), false);
  store.setAdultDate('1990-06-15');
  assert.equal(store.getSnapshot().birth, null);
  assert.match(store.getSnapshot().message!, /mapping was cleared/);
  await store.saveBirth(birth()); assert.equal(store.getSnapshot().birth?.version, 1);
});

test('retry cannot bypass consent withdrawal or account restriction', async () => {
  const store = await ready(); await store.saveBirth(birth(), 'unavailable');
  store.setConsent(false); const version = store.getSnapshot().birth?.version;
  await store.retryBirth(); assert.equal(store.getSnapshot().birth?.version, version);
  assert.equal(store.getSnapshot().birth?.resolution, 'unavailable');
  store.scenario('suspended'); await store.saveBirth(birth());
  assert.equal(store.getSnapshot().birth, null);
});

test('adapter birth intents enforce owner, expected version and idempotency identity', async () => {
  const adapter = createFixtureAdapter(options);
  await adapter.account('register', 'alex@example.invalid', FIXTURE_PASSWORD, 1, 'success');
  const context = { generation: 1, accountId: FIXTURE_ACCOUNT_IDS.alex };
  await adapter.verify(context, 'success');
  const first = await adapter.saveBirth(context, intent(), 'pending');
  adapter.acknowledgeBirth(context, first.version);
  assert.deepEqual(await adapter.saveBirth(context, intent(), 'pending'), first);
  await assert.rejects(adapter.saveBirth(context, intent({ input: birth({ place_label: 'Different' }) }), 'pending'), FixtureFailure);
  await assert.rejects(adapter.saveBirth({ ...context, accountId: FIXTURE_ACCOUNT_IDS.sam }, intent(), 'pending'), FixtureFailure);
  const second = intent({ meta: { idempotency_key: '66666666-6666-4666-8666-666666666666', expected_version: 1 }, input: birth({ place_label: 'Corrected' }) });
  const corrected = await adapter.saveBirth(context, second, 'pending');
  adapter.acknowledgeBirth(context, corrected.version);
  await assert.rejects(adapter.saveBirth(context, intent(), 'pending'), FixtureFailure);
});

test('direct adapter account replacement cannot carry private rollback state across accounts', async () => {
  const adapter = createFixtureAdapter(options);
  const alex = { generation: 1, accountId: FIXTURE_ACCOUNT_IDS.alex };
  await adapter.account('register', 'alex@example.invalid', FIXTURE_PASSWORD, 1, 'success');
  await adapter.verify(alex, 'success');
  const prior = await adapter.saveBirth(alex, intent(), 'pending');
  adapter.acknowledgeBirth(alex, prior.version);
  await adapter.saveBirth(alex, intent({ meta: { idempotency_key: '66666666-6666-4666-8666-666666666666', expected_version: 1 } }), 'unavailable');
  await adapter.account('register', 'sam@example.invalid', FIXTURE_PASSWORD, 2, 'success');
  adapter.cancelPending();
  const sam = { generation: 2, accountId: FIXTURE_ACCOUNT_IDS.sam };
  await adapter.verify(sam, 'success');
  const result = await adapter.saveBirth(sam, intent(), 'pending');
  assert.equal(result.version, 1);
  assert.equal(result.input_id, '44444444-4444-4444-8444-444444444444');
});

test('consent withdrawal between adapter result and store acceptance rolls back the synthetic mutation', async () => {
  const gate = controllable();
  const store = await ready(createFixtureOnboardingStore({ ...options, pause: gate.pause }));
  gate.hold(); const pending = store.saveBirth(birth(), 'unavailable');
  gate.release();
  queueMicrotask(() => queueMicrotask(() => store.setConsent(false)));
  await pending;
  assert.equal(store.getSnapshot().birth, null);
  assert.equal(store.getSnapshot().consent.state, 'withdrawn');
  store.setConsent(true); await store.saveBirth(birth());
  assert.equal(store.getSnapshot().birth?.version, 1);
  assert.equal(store.getSnapshot().error, null);
});

test('same-session serialized checkpoint is valid and stale/forged/cross-account copies are denied', async () => {
  const store = await ready(); await store.saveBirth(birth());
  const saved = store.saveCheckpoint();
  assert.equal(store.restoreCheckpoint(JSON.parse(JSON.stringify(saved))), true);
  const forged = JSON.parse(JSON.stringify(saved)); forged.consent.policy_version = 'future-policy';
  assert.equal(store.restoreCheckpoint(forged), false);
  assert.equal(store.restoreCheckpoint({ cyclic: 1n }), false);
  store.setConsent(false); assert.equal(store.restoreCheckpoint(saved), false);
  assert.equal(store.getSnapshot().consent.state, 'withdrawn');
  store.setConsent(true); const newer = store.saveCheckpoint();
  await store.saveBirth(birth({ place_label: 'Updated Fictional Place' }));
  assert.equal(store.restoreCheckpoint(newer), false);
  assert.equal(store.getSnapshot().birth?.input.place_label, 'Updated Fictional Place');
  await store.account('register', 'sam@example.invalid', FIXTURE_PASSWORD);
  assert.equal(store.getSnapshot().birth, null);
  assert.equal(store.restoreCheckpoint(saved), false);
  const fresh = await ready(); assert.equal(fresh.restoreCheckpoint(saved), false);
});

test('logout and session expiry erase private draft, checkpoint and recovery', async () => {
  for (const action of ['logout', 'expire'] as const) {
    const store = await ready(); await store.saveBirth(birth());
    const saved = store.saveCheckpoint(); const generation = store.getSnapshot().generation;
    store[action]();
    assert.ok(store.getSnapshot().generation > generation);
    assert.equal(store.getSnapshot().birth, null);
    assert.equal(store.getSnapshot().adultBirthDate, null);
    assert.equal(store.getSnapshot().checkpointAvailable, false);
    assert.equal(store.restoreCheckpoint(saved), false);
    assert.equal(canAccessRoute('/birth', store.getSnapshot()), false);
  }
});

test('configured adapter errors never fall back to fixture success or echo private provider errors', async () => {
  const adapter: OnboardingAdapter = { ...createFixtureAdapter(options),
    account: async () => { throw new Error('SECRET provider body: raw contact and credentials'); } };
  const store = new OnboardingStore(adapter, options);
  await store.account('sign_in', 'alex@example.invalid', FIXTURE_PASSWORD);
  assert.equal(store.getSnapshot().account, null);
  assert.match(store.getSnapshot().error!, /adapter could not/);
  assert.doesNotMatch(JSON.stringify(store.getSnapshot()), /SECRET|raw contact|credentials/);
});

test('snapshot is immutable and listeners unsubscribe', async () => {
  const store = createFixtureOnboardingStore(options);
  let updates = 0; const unsubscribe = store.subscribe(() => { updates += 1; });
  await store.account('sign_in', 'alex@example.invalid', FIXTURE_PASSWORD);
  assert.ok(updates > 0);
  assert.throws(() => { store.getSnapshot().account!.state = 'active'; });
  const previous = updates; unsubscribe(); store.logout(); assert.equal(updates, previous);
});

test('direct/back route guards deny every protected stage until its current prerequisites exist', async () => {
  const store = createFixtureOnboardingStore(options);
  for (const route of ['/verify', '/birth', '/remaining', '/recommended', '/explore', '/reset-password'] as const) {
    assert.equal(canAccessRoute(route, store.getSnapshot()), false);
  }
  await verified(store);
  assert.equal(canAccessRoute('/eligibility', store.getSnapshot()), true);
  assert.equal(canAccessRoute('/birth', store.getSnapshot()), false);
  store.setAdultDate('1990-06-15'); store.setConsent(true);
  assert.equal(canAccessRoute('/birth', store.getSnapshot()), true);
  await store.saveBirth(birth());
  assert.equal(canAccessRoute('/birth', store.getSnapshot()), true);
  assert.equal(canAccessRoute('/remaining', store.getSnapshot()), true);
  store.logout(); assert.equal(canAccessRoute('/remaining', store.getSnapshot()), false);
});

test('link sanitizer accepts only exact screen identities and removes unsafe private destinations', () => {
  assert.equal(sanitizeDestination('/birth'), '/birth');
  assert.equal(sanitizeDestination('glow-development://birth'), '/birth');
  assert.equal(sanitizeDestination('glow-development:///birth'), '/birth');
  for (const path of ['/birth?birth_date=1990-01-01', '/birth#private', '/birth/', '/birth%3Fsecret', 'https://example.com/birth',
    'glow-development://account@evil', '/unknown', '//birth', '/birth\\..', ['birth'], null, ' /birth']) {
    assert.equal(sanitizeDestination(path), '/');
  }
});
