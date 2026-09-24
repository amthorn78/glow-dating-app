import assert from 'node:assert/strict';
import test from 'node:test';
import { createFixtureOnboardingStore, FIXTURE_PASSWORD } from './store.ts';
import { canAccessRoute, sanitizeDestination } from './routes.ts';

const routes = ['/profile', '/profile-edit', '/preferences', '/profile-preview', '/media'] as const;
const create = () => createFixtureOnboardingStore({ isDevelopment: true, mode: 'fixture' });

test('owner profile routes reject anonymous, unverified and expired sessions', async () => {
  const store = create();
  for (const route of routes) {
    assert.equal(sanitizeDestination(route), route);
    assert.equal(sanitizeDestination(`glow-development://${route.slice(1)}`), route);
    assert.equal(sanitizeDestination(`${route}?owner=untrusted`), '/');
    assert.equal(canAccessRoute(route, store.getSnapshot()), false);
  }
  await store.account('register', 'alex@example.invalid', FIXTURE_PASSWORD);
  for (const route of routes) assert.equal(canAccessRoute(route, store.getSnapshot()), false);
  await store.verify();
  for (const route of routes) assert.equal(canAccessRoute(route, store.getSnapshot()), true);
  store.expire();
  for (const route of routes) assert.equal(canAccessRoute(route, store.getSnapshot()), false);
});

test('current owners can manage profile after consent withdrawal but cannot disclose recommendations', () => {
  const store = create();
  store.scenario('eligible');
  assert.equal(canAccessRoute('/recommended', store.getSnapshot()), true);
  store.setConsent(false);
  for (const route of routes) assert.equal(canAccessRoute(route, store.getSnapshot()), true);
  assert.equal(canAccessRoute('/recommended', store.getSnapshot()), false);
  assert.equal(canAccessRoute('/explore', store.getSnapshot()), false);
  for (const scenario of ['suspended', 'deletion_pending'] as const) {
    store.scenario(scenario);
    for (const route of routes) assert.equal(canAccessRoute(route, store.getSnapshot()), false);
  }
  store.logout();
  for (const route of routes) assert.equal(canAccessRoute(route, store.getSnapshot()), false);
});

test('match revocation routes require current session authority and remain available after eligibility loss', () => {
  const store = create();
  for (const route of ['/matches', '/match'] as const) {
    assert.equal(sanitizeDestination(route), route);
    assert.equal(sanitizeDestination(`${route}?match=forged`), '/');
    assert.equal(canAccessRoute(route, store.getSnapshot()), false);
  }
  store.scenario('eligible');
  store.setConsent(false);
  assert.equal(canAccessRoute('/recommended', store.getSnapshot()), false);
  assert.equal(canAccessRoute('/matches', store.getSnapshot()), true);
  assert.equal(canAccessRoute('/match', store.getSnapshot()), true);
  store.expire();
  assert.equal(canAccessRoute('/matches', store.getSnapshot()), false);
  assert.equal(canAccessRoute('/match', store.getSnapshot()), false);
  store.scenario('suspended');
  assert.equal(canAccessRoute('/matches', store.getSnapshot()), true);
});

for (const restriction of ['suspended', 'deletion_pending'] as const) {
  test(`a current ${restriction} participant can reach cleanup but no profile or discovery route`, () => {
    const store = create();
    store.scenario(restriction);
    assert.equal(store.getSnapshot().account?.session_state, 'valid');
    for (const route of ['/matches', '/match'] as const) assert.equal(canAccessRoute(route, store.getSnapshot()), true);
    for (const route of [...routes, '/recommended', '/explore', '/birth', '/eligibility'] as const) {
      assert.equal(canAccessRoute(route, store.getSnapshot()), false, route);
    }
    store.expire();
    for (const route of ['/matches', '/match'] as const) assert.equal(canAccessRoute(route, store.getSnapshot()), false);
    store.scenario(restriction);
    store.logout();
    for (const route of ['/matches', '/match'] as const) assert.equal(canAccessRoute(route, store.getSnapshot()), false);
  });
}

test('deleted, unverified and revoked sessions cannot enter match cleanup routes', async () => {
  const store = create();
  await store.account('register', 'alex@example.invalid', FIXTURE_PASSWORD);
  for (const route of ['/matches', '/match'] as const) assert.equal(canAccessRoute(route, store.getSnapshot()), false);
  store.scenario('eligible');
  const current = store.getSnapshot();
  assert.ok(current.account);
  for (const route of ['/matches', '/match'] as const) {
    assert.equal(canAccessRoute(route, { ...current, account: { ...current.account, state: 'deleted' } }), false);
    assert.equal(canAccessRoute(route, { ...current, account: { ...current.account, session_state: 'revoked' } }), false);
  }
});
