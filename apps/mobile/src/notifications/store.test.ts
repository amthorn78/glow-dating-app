import assert from 'node:assert/strict';
import test from 'node:test';
import { createFixtureOnboardingStore } from '../onboarding/store.ts';
import { NotificationClient } from './client.ts';
import { FixtureNotificationAdapter } from './fixture-adapter.ts';
import { FIXTURE_INSTALLATION_ID, SYNTHETIC_TOKEN_PREFIX, syntheticTokenSource } from './fixture-device.ts';
import { FixturePermissionSeam } from './permission.ts';
import { currentSession, NotificationStore } from './store.ts';

/** P06.3, Outcome 3: the settings screen's store over the fixture adapter, the permission seam and the onboarding fixture. */
const settle = async () => { for (let index = 0; index < 5; index++) await new Promise(resolve => setImmediate(resolve)); };

function setup(scenario: 'eligible' | 'new' = 'eligible') {
  const owner = createFixtureOnboardingStore({ isDevelopment: true, mode: 'fixture' });
  if (scenario === 'eligible') owner.scenario('eligible');
  const adapter = new FixtureNotificationAdapter();
  const permission = new FixturePermissionSeam();
  const store = new NotificationStore({ owner, client: new NotificationClient(adapter), permission, tokens: syntheticTokenSource(),
    sessions: adapter, installation: FIXTURE_INSTALLATION_ID });
  return { owner, adapter, permission, store };
}
async function enabled(kind: 'match' | 'message' = 'match') {
  const fixture = setup();
  await fixture.store.load();
  await fixture.store.setKind(kind, true);
  assert.equal(fixture.store.getSnapshot()[kind], true);
  return fixture;
}
const kinds = (adapter: FixtureNotificationAdapter) => adapter.events().map(event => event.kind);
const registration = (adapter: FixtureNotificationAdapter) => adapter.registrationsView().find(row => row.deviceId === FIXTURE_INSTALLATION_ID);

test('both kinds start off, and a read from an installation with no registration is an explicit absence', async () => {
  const { store, adapter } = setup();
  assert.equal(store.getSnapshot().status, 'idle');
  await store.load();
  assert.deepEqual(store.getSnapshot(), { status: 'ready', match: false, message: false, deviceActive: false, denied: false, busy: false, error: null });
  assert.deepEqual(adapter.events().filter(event => event.kind === 'refused'), [{ kind: 'refused', operation: 'settings_read', code: 'not_found' }]);
});

test('nothing asks for the permission at launch, at sign-in, on a read or on any other change', async () => {
  const { owner, store, permission } = setup('new');
  await store.load();
  owner.scenario('eligible');
  await store.load();
  await store.setKind('match', false);
  owner.scenario('suspended');
  owner.scenario('eligible');
  owner.expire();
  owner.scenario('eligible');
  owner.logout();
  await settle();
  assert.equal(permission.requests, 0);
});

test('turning a kind on asks once while undetermined, registers this installation, then saves only that kind', async () => {
  const { store, adapter, permission, owner } = setup();
  await store.load();
  await store.setKind('match', true);
  assert.equal(permission.requests, 1);
  assert.deepEqual(kinds(adapter).filter(kind => kind !== 'refused'), ['session_started', 'register', 'settings']);
  const account = currentSession(owner.getSnapshot())!.accountId;
  assert.deepEqual(adapter.settingsOf(account), { match: true, message: false });
  assert.deepEqual(store.getSnapshot(), { status: 'ready', match: true, message: false, deviceActive: true, denied: false, busy: false, error: null });
  await store.setKind('message', true);
  assert.equal(permission.requests, 1, 'granted is not asked again');
  assert.equal(kinds(adapter).filter(kind => kind === 'register').length, 1, 'an active registration is not registered again');
  assert.deepEqual(adapter.settingsOf(account), { match: true, message: true });
  await store.setKind('match', false);
  assert.deepEqual(adapter.settingsOf(account), { match: false, message: true });
  assert.deepEqual([store.getSnapshot().match, store.getSnapshot().message], [false, true]);
  assert.equal(permission.requests, 1);
});

test('an already granted permission is not asked for', async () => {
  const { store, permission } = setup();
  permission.set('granted');
  await store.load();
  await store.setKind('message', true);
  assert.equal(permission.requests, 0);
  assert.equal(store.getSnapshot().message, true);
});

test('a denied permission saves nothing and registers no device; turning on again asks only while undetermined', async () => {
  const { store, adapter, permission, owner } = setup();
  permission.set('undetermined_deny');
  await store.load();
  await store.setKind('match', true);
  assert.equal(permission.requests, 1);
  assert.deepEqual(store.getSnapshot(), { status: 'ready', match: false, message: false, deviceActive: false, denied: true, busy: false, error: null });
  assert.deepEqual(adapter.registrationsView(), []);
  assert.equal(adapter.heldTokens, 0);
  assert.deepEqual(kinds(adapter).filter(kind => kind === 'register' || kind === 'settings'), []);
  assert.deepEqual(adapter.settingsOf(currentSession(owner.getSnapshot())!.accountId), { match: false, message: false });
  await store.setKind('match', true);
  assert.equal(permission.requests, 1, 'a decided answer is not asked again');
  assert.equal(store.getSnapshot().denied, true);
  assert.deepEqual(adapter.registrationsView(), []);
  permission.set('denied');
  await store.setKind('message', true);
  assert.equal(permission.requests, 1);
  assert.deepEqual(adapter.registrationsView(), []);
  permission.set('undetermined_allow');
  await store.setKind('match', true);
  assert.equal(permission.requests, 2);
  assert.equal(store.getSnapshot().match, true);
  assert.equal(store.getSnapshot().denied, false);
});

test('the screen shows both kinds off unless this installation\'s registration is active', async () => {
  const { store, adapter, owner } = await enabled('match');
  await store.setKind('message', true);
  const session = currentSession(owner.getSnapshot())!;
  adapter.ended(session);
  owner.logout();
  owner.scenario('eligible');
  await settle();
  await store.load();
  const account = currentSession(owner.getSnapshot())!.accountId;
  assert.deepEqual(adapter.settingsOf(account), { match: true, message: true });
  assert.equal(registration(adapter)?.state, 'revoked');
  assert.deepEqual(store.getSnapshot(), { status: 'ready', match: false, message: false, deviceActive: false, denied: false, busy: false, error: null });
  assert.deepEqual(await store.setKind('match', false), undefined);
  assert.deepEqual(adapter.settingsOf(account), { match: true, message: true }, 'turning off with no active registration saves nothing');
});

test('logout revokes this installation through the adapter while the session is current, then clears the screen', async () => {
  const { store, adapter, owner } = await enabled('match');
  const session = currentSession(owner.getSnapshot())!;
  owner.logout();
  await settle();
  assert.deepEqual(store.getSnapshot(), { status: 'idle', match: false, message: false, deviceActive: false, denied: false, busy: false, error: null });
  const ended = registration(adapter)!;
  assert.equal(ended.state, 'revoked');
  assert.equal(ended.endedBy, 'revoke', 'the owner\'s revoke, not the system\'s logout');
  const order = kinds(adapter);
  assert.ok(order.lastIndexOf('revoke') < order.lastIndexOf('session_ended'), order.join(','));
  assert.deepEqual(adapter.events().slice(order.indexOf('register')).filter(event => event.kind === 'refused'), [], 'the revoke was not refused');
  assert.equal(adapter.isCurrent(session.sessionId), false);
  assert.equal(adapter.heldTokens, 0);
});

test('an account change revokes the earlier session\'s registration first, and the new account starts clear', async () => {
  const { store, adapter, owner } = await enabled('message');
  const first = currentSession(owner.getSnapshot())!;
  owner.scenario('eligible');
  await settle();
  assert.equal(store.getSnapshot().status, 'idle');
  assert.equal(registration(adapter)?.endedBy, 'revoke');
  assert.equal(adapter.isCurrent(first.sessionId), false);
  const second = currentSession(owner.getSnapshot())!;
  assert.notEqual(second.sessionId, first.sessionId);
  assert.equal(adapter.isCurrent(second.sessionId), true);
  await store.load();
  assert.deepEqual([store.getSnapshot().match, store.getSnapshot().message, store.getSnapshot().deviceActive], [false, false, false]);
});

// Correction C1, item 1 (F-1): a register in flight when the session ends. In the same task the adapter refuses it
// (it re-checks the session after its await); in a later task it has committed, and the owner's revoke ends it.
for (const preset of ['granted', 'undetermined_allow'] as const) {
  for (const change of ['logout', 'account change'] as const) {
    for (const timing of ['same task', 'later task'] as const) {
      test(`a register in flight at ${change === 'logout' ? 'a logout' : 'an account change'} in the ${timing} (${preset}) leaves nothing active on the ended session and no token held`, async () => {
        const { store, adapter, permission, owner } = setup();
        permission.set(preset);
        await store.load();
        const ended = currentSession(owner.getSnapshot())!;
        const turning = store.setKind('match', true);
        if (timing === 'later task') await new Promise(resolve => setImmediate(resolve));
        if (change === 'logout') owner.logout(); else owner.scenario('eligible');
        await turning;
        await settle();
        assert.equal(adapter.isCurrent(ended.sessionId), false);
        assert.deepEqual(adapter.registrationsView().filter(row => row.sessionId === ended.sessionId && row.state === 'active'), [], kinds(adapter).join(','));
        assert.equal(adapter.heldTokens, 0);
        assert.equal(store.getSnapshot().status, 'idle');
        if (timing === 'same task') {
          assert.deepEqual(adapter.registrationsView(), [], kinds(adapter).join(','));
          assert.deepEqual(adapter.events().filter(event => event.kind === 'refused' && event.operation === 'device'),
            [{ kind: 'refused', operation: 'device', code: 'unauthenticated' }], 'the in-flight register reached the adapter and was refused');
        } else {
          assert.equal(registration(adapter)?.endedBy, 'revoke', 'the committed register is ended by the owner\'s revoke');
        }
      });
    }
  }
}

test('the server\'s logout event covers a revoke that did not reach it', async () => {
  const { adapter, owner } = await enabled('match');
  adapter.setScenario('offline');
  owner.logout();
  await settle();
  const ended = registration(adapter)!;
  assert.equal(ended.state, 'revoked');
  assert.equal(ended.endedBy, 'logout');
  adapter.setScenario('normal');
});

test('an expired session sends no revoke; its end alone ends its registration', async () => {
  const { store, adapter, owner } = await enabled('match');
  owner.expire();
  await settle();
  assert.equal(store.getSnapshot().status, 'idle');
  assert.equal(kinds(adapter).includes('revoke'), false);
  assert.equal(registration(adapter)?.endedBy, 'logout');
});

test('a command from a session Glow no longer holds as current is refused', async () => {
  const { adapter, owner } = await enabled('match');
  const session = currentSession(owner.getSnapshot())!;
  const client = new NotificationClient(adapter);
  adapter.ended(session);
  await assert.rejects(client.save(session, FIXTURE_INSTALLATION_ID, client.settingsIntent(true, true, 3, 'late')), { code: 'signed_out' });
  await assert.rejects(client.read(session, FIXTURE_INSTALLATION_ID), { code: 'signed_out' });
});

test('a response for an earlier session changes nothing', async () => {
  const { store, owner } = setup();
  const loading = store.load();
  owner.logout();
  await loading;
  await settle();
  assert.equal(store.getSnapshot().status, 'idle');
});

test('a lost register response is retried with the same intent, so one registration results', async () => {
  const { store, adapter } = setup();
  await store.load();
  adapter.setScenario('lost_response');
  await store.setKind('match', true);
  assert.equal(store.getSnapshot().error, 'offline');
  adapter.setScenario('normal');
  await store.setKind('match', true);
  assert.equal(store.getSnapshot().match, true);
  assert.equal(kinds(adapter).filter(kind => kind === 'register').length, 1);
  assert.equal(registration(adapter)?.version, 2);
});

test('the token never reaches the store\'s state, the adapter\'s records or a refusal', async () => {
  const { store, adapter, owner } = await enabled('match');
  await store.setKind('message', true);
  owner.logout();
  await settle();
  const seen = JSON.stringify([store.getSnapshot(), adapter.events(), adapter.registrationsView()]);
  assert.equal(seen.includes(SYNTHETIC_TOKEN_PREFIX), false);
  assert.equal(seen.includes('fixture-notification-ref'), false);
});
