import assert from 'node:assert/strict';
import test from 'node:test';
import { createFixtureOnboardingStore } from '../onboarding/store.ts';
import { canAccessRoute, sanitizeDestination } from '../onboarding/routes.ts';

const create = () => createFixtureOnboardingStore({ isDevelopment: true, mode: 'fixture' });
const routes = ['/conversations', '/conversation'] as const;

test('the chat routes are fixed, query-free destinations guarded like /matches but for an active account only', () => {
  const store = create();
  for (const route of routes) {
    assert.equal(sanitizeDestination(route), route);
    assert.equal(sanitizeDestination(`${route}?match=forged`), '/');
    assert.equal(sanitizeDestination(`glow-development://${route.slice(1)}`), route);
    assert.equal(canAccessRoute(route, store.getSnapshot()), false);
  }
  store.scenario('eligible');
  for (const route of routes) assert.equal(canAccessRoute(route, store.getSnapshot()), true);
  store.expire();
  for (const route of routes) assert.equal(canAccessRoute(route, store.getSnapshot()), false);
});

for (const restriction of ['suspended', 'deletion_pending'] as const) test(`a ${restriction} account can end a connection but reaches no conversation`, () => {
  const store = create();
  store.scenario(restriction);
  assert.equal(canAccessRoute('/matches', store.getSnapshot()), true);
  for (const route of routes) assert.equal(canAccessRoute(route, store.getSnapshot()), false);
});

test('a deleted account or a revoked session reaches no conversation', () => {
  const store = create();
  store.scenario('eligible');
  const current = store.getSnapshot();
  for (const route of routes) {
    assert.equal(canAccessRoute(route, { ...current, account: { ...current.account!, state: 'deleted' } }), false);
    assert.equal(canAccessRoute(route, { ...current, account: { ...current.account!, session_state: 'revoked' } }), false);
  }
});
