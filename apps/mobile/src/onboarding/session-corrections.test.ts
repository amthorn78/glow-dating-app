import assert from 'node:assert/strict';
import test from 'node:test';
import type { AccountAccess } from '../contracts/generated/gapp-api-v1.ts';
import { createFixtureAdapter, FIXTURE_ACCOUNT_IDS, FIXTURE_PASSWORD, FixtureFailure } from './fixture-adapter.ts';
import { canAccessRoute } from './routes.ts';
import { createFixtureOnboardingStore, OnboardingStore } from './store.ts';

const options = { isDevelopment: true, mode: 'fixture' };
const context = { generation: 1, accountId: FIXTURE_ACCOUNT_IDS.alex };
const failureCode = (code: FixtureFailure['code']) => (error: unknown) => error instanceof FixtureFailure && error.code === code;
const restrictedAccount = (state: 'suspended' | 'deletion_pending', session_state: AccountAccess['session_state'] = 'valid'): AccountAccess => ({
  kind: 'account_access', account_id: FIXTURE_ACCOUNT_IDS.alex, version: 1, state, session_state,
});
function delayOneRequest() {
  let hold = false;
  let release = () => {};
  return { pause: () => {
    if (!hold) return Promise.resolve();
    hold = false;
    return new Promise<void>(resolve => { release = resolve; });
  }, hold() { hold = true; }, release() { release(); } };
}

for (const restriction of ['suspended', 'deletion_pending'] as const) {
  test(`${restriction} expiry returns to account entry and clears private state`, async () => {
    const store = createFixtureOnboardingStore(options);
    await store.account('register', 'alex@example.invalid', FIXTURE_PASSWORD);
    await store.verify();
    store.setAdultDate('1990-06-15'); store.setConsent(true);
    await store.saveBirth({ birth_date: '1990-06-15', local_time: null, time_precision: 'unknown',
      place_label: 'Fictional Harbor', timezone_name: null, timezone_provenance: null });
    const checkpoint = store.saveCheckpoint();
    store.scenario(restriction);
    assert.equal(store.getSnapshot().stage, 'restricted');
    const generation = store.getSnapshot().generation;
    store.expire();
    const expired = store.getSnapshot();
    assert.equal(expired.stage, 'account');
    assert.equal(expired.account?.state, restriction);
    assert.equal(expired.account?.session_state, 'expired');
    assert.ok(expired.generation > generation);
    assert.equal(expired.birth, null);
    assert.equal(expired.adultBirthDate, null);
    assert.equal(expired.consent.state, 'required');
    assert.equal(expired.checkpointAvailable, false);
    assert.equal(expired.recoveryReady, false);
    assert.equal(store.restoreCheckpoint(checkpoint), false);
    assert.equal(canAccessRoute('/account', expired), true);
    assert.equal(canAccessRoute('/recovery', expired), true);
    for (const route of ['/restricted', '/verify', '/birth', '/remaining', '/recommended', '/explore'] as const) {
      assert.equal(canAccessRoute(route, expired), false);
    }
  });

  test(`${restriction} remains enforced after normal sign-in and recovery without scenario reselection`, async () => {
    const store = createFixtureOnboardingStore(options);
    store.scenario(restriction); store.expire();
    await store.account('sign_in', 'alex@example.invalid', FIXTURE_PASSWORD);
    assert.equal(store.getSnapshot().error, null);
    assert.equal(store.getSnapshot().account?.state, restriction);
    assert.equal(store.getSnapshot().account?.session_state, 'valid');
    assert.equal(store.getSnapshot().stage, 'restricted');
    for (const route of ['/verify', '/eligibility', '/birth', '/remaining', '/recommended', '/explore'] as const) {
      assert.equal(canAccessRoute(route, store.getSnapshot()), false);
    }
    store.expire();
    await store.requestRecovery('alex@example.invalid');
    assert.equal(await store.resetPassword(FIXTURE_PASSWORD), true);
    await store.account('sign_in', 'alex@example.invalid', FIXTURE_PASSWORD);
    assert.equal(store.getSnapshot().stage, 'restricted');
    assert.equal(store.getSnapshot().account?.state, restriction);
    store.logout();
    await store.account('register', 'alex@example.invalid', FIXTURE_PASSWORD);
    assert.equal(store.getSnapshot().account?.state, restriction);
    await store.account('sign_in', 'sam@example.invalid', FIXTURE_PASSWORD);
    assert.equal(store.getSnapshot().account?.account_id, FIXTURE_ACCOUNT_IDS.sam);
    assert.equal(store.getSnapshot().stage, 'verification');
    await store.account('sign_in', 'alex@example.invalid', FIXTURE_PASSWORD);
    assert.equal(store.getSnapshot().stage, 'restricted');
  });

  test(`${restriction} fixture only changes through an explicit scenario replacement`, async () => {
    const store = createFixtureOnboardingStore(options);
    store.scenario(restriction); store.expire();
    store.scenario('new');
    await store.account('sign_in', 'alex@example.invalid', FIXTURE_PASSWORD);
    assert.equal(store.getSnapshot().stage, 'verification');
    store.scenario(restriction); store.scenario('eligible');
    assert.equal(store.getSnapshot().stage, 'eligible');
    store.expire();
    await store.account('sign_in', 'alex@example.invalid', FIXTURE_PASSWORD);
    assert.equal(store.getSnapshot().stage, 'verification');
  });
}

test('account entry accepts a restricted fixture result but rejects an expired adapter session', async () => {
  for (const state of ['suspended', 'deletion_pending'] as const) {
    const accepted = new OnboardingStore({ ...createFixtureAdapter(options), account: async () => restrictedAccount(state) }, options);
    await accepted.account('sign_in', 'alex@example.invalid', FIXTURE_PASSWORD);
    assert.equal(accepted.getSnapshot().stage, 'restricted');
    const expired = new OnboardingStore({ ...createFixtureAdapter(options), account: async () => restrictedAccount(state, 'expired') }, options);
    await expired.account('sign_in', 'alex@example.invalid', FIXTURE_PASSWORD);
    assert.equal(expired.getSnapshot().account, null);
    assert.equal(expired.getSnapshot().stage, 'account');
    assert.ok(expired.getSnapshot().error);
  }
});

test('selected verification expiry cannot be changed to success without a resend', async () => {
  const store = createFixtureOnboardingStore(options);
  await store.account('register', 'alex@example.invalid', FIXTURE_PASSWORD);
  await store.verify('expired');
  assert.equal(store.getSnapshot().stage, 'verification');
  await store.verify('success');
  assert.equal(store.getSnapshot().stage, 'verification');
  assert.equal(store.getSnapshot().account?.state, 'unverified');
  assert.match(store.getSnapshot().error!, /expired/);
  await store.resend(); await store.verify();
  assert.equal(store.getSnapshot().stage, 'eligibility');
  assert.equal(store.getSnapshot().error, null);
});

test('wrong account or generation cannot expire the current verification challenge', async () => {
  for (const wrong of [{ ...context, generation: 2 }, { ...context, accountId: FIXTURE_ACCOUNT_IDS.sam }]) {
    const adapter = createFixtureAdapter(options);
    await adapter.account('register', 'alex@example.invalid', FIXTURE_PASSWORD, context.generation, 'success');
    await assert.rejects(adapter.verify(wrong, 'expired'), failureCode('stale'));
    assert.equal((await adapter.verify(context, 'success')).state, 'active');
  }
});

test('wrong recovery generation cannot expire the current recovery challenge', async () => {
  const adapter = createFixtureAdapter(options);
  await adapter.requestRecovery('alex@example.invalid', context.generation, 'success');
  await assert.rejects(adapter.resetPassword(FIXTURE_PASSWORD, context.generation + 1, 'expired'), failureCode('invalid'));
  await adapter.resetPassword(FIXTURE_PASSWORD, context.generation, 'success');
});

test('selected recovery expiry is terminal until a fresh challenge is requested', async () => {
  const adapter = createFixtureAdapter(options);
  await adapter.requestRecovery('alex@example.invalid', context.generation, 'success');
  await assert.rejects(adapter.resetPassword(FIXTURE_PASSWORD, context.generation, 'expired'), failureCode('expired'));
  await assert.rejects(adapter.resetPassword(FIXTURE_PASSWORD, context.generation, 'success'), failureCode('expired'));
  await adapter.requestRecovery('alex@example.invalid', context.generation, 'success');
  await adapter.resetPassword(FIXTURE_PASSWORD, context.generation, 'success');
});

test('verification rate limits and transport errors retain the current usable challenge', async () => {
  for (const outcome of ['rate_limited', 'error'] as const) {
    const store = createFixtureOnboardingStore(options);
    await store.account('register', 'alex@example.invalid', FIXTURE_PASSWORD);
    await store.verify(outcome);
    assert.equal(store.getSnapshot().stage, 'verification');
    assert.ok(store.getSnapshot().error);
    await store.verify();
    assert.equal(store.getSnapshot().stage, 'eligibility');
    assert.equal(store.getSnapshot().error, null);
  }
});

test('delayed verification cannot expire or consume a replacement challenge', async () => {
  for (const outcome of ['expired', 'success'] as const) {
    const gate = delayOneRequest();
    const adapter = createFixtureAdapter({ ...options, pause: gate.pause });
    await adapter.account('register', 'alex@example.invalid', FIXTURE_PASSWORD, context.generation, 'success');
    gate.hold();
    const stale = adapter.verify(context, outcome);
    await adapter.resend(context, 'success');
    const rejected = assert.rejects(stale, FixtureFailure);
    gate.release(); await rejected;
    assert.equal((await adapter.verify(context, 'success')).state, 'active');
  }
});

test('delayed reset cannot expire or consume a replacement recovery challenge', async () => {
  for (const outcome of ['expired', 'success'] as const) {
    const gate = delayOneRequest();
    const adapter = createFixtureAdapter({ ...options, pause: gate.pause });
    await adapter.requestRecovery('alex@example.invalid', context.generation, 'success');
    gate.hold();
    const stale = adapter.resetPassword(FIXTURE_PASSWORD, context.generation, outcome);
    await adapter.requestRecovery('alex@example.invalid', context.generation, 'success');
    const rejected = assert.rejects(stale, FixtureFailure);
    gate.release(); await rejected;
    await adapter.resetPassword(FIXTURE_PASSWORD, context.generation, 'success');
  }
});

test('elapsed verification expiry is terminal and a fresh successful challenge cannot be replayed', async () => {
  let now = new Date('2026-09-23T12:00:00Z');
  const adapter = createFixtureAdapter({ ...options, clock: () => now });
  await adapter.account('register', 'alex@example.invalid', FIXTURE_PASSWORD, context.generation, 'success');
  now = new Date('2026-09-23T12:01:00Z');
  await assert.rejects(adapter.verify(context, 'success'), failureCode('expired'));
  now = new Date('2026-09-23T12:00:30Z');
  await assert.rejects(adapter.verify(context, 'success'), failureCode('expired'));
  await adapter.resend(context, 'success');
  assert.equal((await adapter.verify(context, 'success')).state, 'active');
  await assert.rejects(adapter.verify(context, 'success'), failureCode('invalid'));
});
