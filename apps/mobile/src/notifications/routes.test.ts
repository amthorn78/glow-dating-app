import assert from 'node:assert/strict';
import test from 'node:test';
import { createFixtureOnboardingStore, FIXTURE_PASSWORD, type OnboardingSnapshot } from '../onboarding/store.ts';
import { canAccessRoute, sanitizeDestination, SAFE_ROUTES } from '../onboarding/routes.ts';

/** P06.3, Outcome 4 (D7): `/notifications` has `/profile`'s rule, an active account with a valid session, in every state. */
const create = () => createFixtureOnboardingStore({ isDevelopment: true, mode: 'fixture' });

function states(): [string, OnboardingSnapshot][] {
  const store = create();
  const found: [string, OnboardingSnapshot][] = [['signed out', store.getSnapshot()]];
  store.scenario('eligible');
  const active = store.getSnapshot();
  found.push(['active, valid session', active]);
  found.push(['deleted', { ...active, account: { ...active.account!, state: 'deleted' } }]);
  found.push(['revoked session', { ...active, account: { ...active.account!, session_state: 'revoked' } }]);
  store.setConsent(false);
  found.push(['active, consent withdrawn', store.getSnapshot()]);
  for (const scenario of ['suspended', 'deletion_pending', 'underage', 'unknown_policy'] as const) {
    store.scenario(scenario);
    found.push([scenario, store.getSnapshot()]);
  }
  store.scenario('eligible');
  store.expire();
  found.push(['expired session', store.getSnapshot()]);
  return found;
}

test('/notifications is guarded like /profile in every state', () => {
  for (const [name, state] of states()) {
    assert.equal(canAccessRoute('/notifications', state), canAccessRoute('/profile', state), name);
    const active = state.account?.state === 'active' && state.account.session_state === 'valid';
    assert.equal(canAccessRoute('/notifications', state), active, name);
  }
});

test('/notifications rejects anonymous, unverified, expired, suspended and deletion-pending sessions', async () => {
  const store = create();
  assert.equal(canAccessRoute('/notifications', store.getSnapshot()), false);
  await store.account('register', 'alex@example.invalid', FIXTURE_PASSWORD);
  assert.equal(canAccessRoute('/notifications', store.getSnapshot()), false);
  await store.verify();
  assert.equal(canAccessRoute('/notifications', store.getSnapshot()), true);
  store.expire();
  assert.equal(canAccessRoute('/notifications', store.getSnapshot()), false);
  for (const scenario of ['suspended', 'deletion_pending'] as const) {
    store.scenario(scenario);
    assert.equal(canAccessRoute('/notifications', store.getSnapshot()), false, scenario);
  }
  store.scenario('eligible');
  store.logout();
  assert.equal(canAccessRoute('/notifications', store.getSnapshot()), false);
});

test('/notifications is a fixed, query-free destination and the only new safe route', () => {
  assert.equal(sanitizeDestination('/notifications'), '/notifications');
  assert.equal(sanitizeDestination('glow-development://notifications'), '/notifications');
  for (const forged of ['/notifications?kind=match', '/notifications#private', '/notifications%3F', '/notifications/x']) {
    assert.equal(sanitizeDestination(forged), '/', forged);
  }
  assert.deepEqual([...SAFE_ROUTES], ['/account', '/verify', '/eligibility', '/birth', '/remaining', '/restricted',
    '/recommended', '/explore', '/recovery', '/reset-password', '/development',
    '/profile', '/profile-edit', '/preferences', '/profile-preview', '/media', '/matches', '/match',
    '/conversations', '/conversation', '/notifications']);
});
