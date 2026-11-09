import assert from 'node:assert/strict';
import test from 'node:test';
import type { DeviceIntent, NotificationIntent } from '../contracts/generated/gapp-api-v1.ts';
import { FixtureNotificationAdapter } from './fixture-adapter.ts';
import { FIXTURE_INSTALLATION_ID } from './fixture-device.ts';

/** P06.3, Outcome 3: the fixture follows F12 per installation, as `glow_domain/notifications.py` does (DM-44 1.1 and 1.2's cases). */
const A = Object.freeze({ accountId: '00000000-0000-4000-8000-00000000000a', sessionId: 'fixture-session-a' });
const B = Object.freeze({ accountId: '00000000-0000-4000-8000-00000000000b', sessionId: 'fixture-session-b' });
const OTHER_DEVICE = '6f12d000-0000-4000-8000-000000000002';
const device = (action: 'register' | 'revoke', version: number, key: string, token: string | null = action === 'register' ? `SYNTHETIC-${key}` : null,
  deviceId = FIXTURE_INSTALLATION_ID): DeviceIntent => ({ operation: 'device', meta: { expected_version: version, idempotency_key: key }, device_id: deviceId, action, provider_token: token });
const settings = (match: boolean, message: boolean, version: number, key: string): NotificationIntent => ({ operation: 'notifications',
  meta: { expected_version: version, idempotency_key: key }, match_notifications: match, message_notifications: message });
type Body = { data?: { version: number; device_state: string; match_notifications: boolean }; code?: string };
const body = (value: unknown) => value as Body;

function adapter() {
  const fixture = new FixtureNotificationAdapter();
  fixture.started(A); fixture.started(B);
  return fixture;
}

test('register, rotate, revoke and register again, per installation', async () => {
  const fixture = adapter();
  assert.equal(body(await fixture.settings(A, FIXTURE_INSTALLATION_ID)).code, 'not_found');
  assert.equal(body(await fixture.device(A, FIXTURE_INSTALLATION_ID, device('register', 0, 'r1'))).data?.version, 1);
  assert.equal(body(await fixture.device(A, FIXTURE_INSTALLATION_ID, device('register', 1, 'r2'))).data?.version, 2);
  assert.equal(fixture.heldTokens, 1, 'rotate drops the old token');
  assert.equal(body(await fixture.device(A, FIXTURE_INSTALLATION_ID, device('revoke', 2, 'r3'))).data?.device_state, 'revoked');
  assert.equal(fixture.heldTokens, 0);
  assert.equal(body(await fixture.device(A, FIXTURE_INSTALLATION_ID, device('revoke', 3, 'r4'))).code, 'state_conflict');
  assert.equal(body(await fixture.device(A, FIXTURE_INSTALLATION_ID, device('register', 3, 'r5'))).data?.device_state, 'active');
  assert.deepEqual(fixture.events().filter(event => ['register', 'rotate', 'revoke'].includes(event.kind)).map(event => event.kind),
    ['register', 'rotate', 'revoke', 'register']);
});

test('settings need this installation\'s active registration and advance every installation of the account', async () => {
  const fixture = adapter();
  assert.equal(body(await fixture.notifications(A, FIXTURE_INSTALLATION_ID, settings(true, false, 0, 's1'))).code, 'state_conflict');
  await fixture.device(A, FIXTURE_INSTALLATION_ID, device('register', 0, 'r1'));
  await fixture.device(A, OTHER_DEVICE, device('register', 0, 'r2', 'SYNTHETIC-2', OTHER_DEVICE));
  assert.equal(body(await fixture.notifications(A, FIXTURE_INSTALLATION_ID, settings(true, false, 1, 's2'))).data?.match_notifications, true);
  assert.equal(body(await fixture.notifications(A, OTHER_DEVICE, settings(false, false, 1, 's3'))).code, 'stale_version');
  assert.equal(body(await fixture.settings(A, OTHER_DEVICE)).data?.version, 2);
  await fixture.device(A, FIXTURE_INSTALLATION_ID, device('revoke', 2, 'r3'));
  assert.equal(body(await fixture.notifications(A, FIXTURE_INSTALLATION_ID, settings(true, true, 3, 's4'))).code, 'state_conflict');
});

test('stale versions, conflicting keys and replays follow CommandMeta', async () => {
  const fixture = adapter();
  assert.equal(body(await fixture.device(A, FIXTURE_INSTALLATION_ID, device('register', 2, 'k'))).code, 'stale_version');
  const intent = device('register', 0, 'k1');
  await fixture.device(A, FIXTURE_INSTALLATION_ID, intent);
  assert.equal(body(await fixture.device(A, FIXTURE_INSTALLATION_ID, intent)).data?.version, 1, 'a replay changes nothing');
  assert.equal(fixture.heldTokens, 1);
  assert.equal(body(await fixture.device(A, FIXTURE_INSTALLATION_ID, device('register', 0, 'k1', 'SYNTHETIC-other'))).code, 'idempotency_conflict');
  assert.equal(body(await fixture.device(A, FIXTURE_INSTALLATION_ID, device('register', 0, 'k2', 'SYNTHETIC-x', OTHER_DEVICE))).code, 'forbidden');
  assert.equal(body(await fixture.device(A, FIXTURE_INSTALLATION_ID, { ...device('register', 1, 'k3'), platform: 'ios' } as DeviceIntent)).code, 'invalid_request');
});

test('another account registering an active installation revokes the earlier registration first', async () => {
  const fixture = adapter();
  await fixture.device(A, FIXTURE_INSTALLATION_ID, device('register', 0, 'a1'));
  await fixture.device(B, FIXTURE_INSTALLATION_ID, device('register', 0, 'b1'));
  const rows = fixture.registrationsView();
  assert.deepEqual(rows.map(row => [row.accountId, row.state, row.endedBy]), [[A.accountId, 'revoked', 'transfer'], [B.accountId, 'active', null]]);
  assert.equal(fixture.heldTokens, 1);
  assert.equal(body(await fixture.settings(A, FIXTURE_INSTALLATION_ID)).data?.device_state, 'revoked');
  assert.equal(body(await fixture.settings(B, FIXTURE_INSTALLATION_ID)).data?.device_state, 'active');
});

test('a session\'s end is the system\'s logout of the registrations it made, and no others', async () => {
  const fixture = adapter();
  const later = Object.freeze({ ...A, sessionId: 'fixture-session-a2' });
  fixture.started(later);
  await fixture.device(A, FIXTURE_INSTALLATION_ID, device('register', 0, 'a1'));
  await fixture.device(later, OTHER_DEVICE, device('register', 0, 'a2', 'SYNTHETIC-a2', OTHER_DEVICE));
  fixture.ended(A);
  assert.deepEqual(fixture.registrationsView().map(row => [row.deviceId, row.state, row.endedBy]),
    [[FIXTURE_INSTALLATION_ID, 'revoked', 'logout'], [OTHER_DEVICE, 'active', null]]);
  assert.equal(body(await fixture.device(A, FIXTURE_INSTALLATION_ID, device('register', 2, 'a3'))).code, 'unauthenticated');
  assert.equal(body(await fixture.settings(A, FIXTURE_INSTALLATION_ID)).code, 'unauthenticated');
  assert.equal(body(await fixture.settings({ ...later, accountId: B.accountId }, OTHER_DEVICE)).code, 'unauthenticated');
});
