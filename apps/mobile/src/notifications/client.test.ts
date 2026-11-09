import assert from 'node:assert/strict';
import test from 'node:test';
import type { DeviceIntent, NotificationIntent } from '../contracts/generated/gapp-api-v1.ts';
import { NotificationClient, NotificationFailure } from './client.ts';
import { FIXTURE_INSTALLATION_ID } from './fixture-device.ts';
import type { NotificationTransport, SessionHandle } from './transport.ts';

/** P06.3, Outcome 3: every intent passes `parseAppIntent` before the transport takes it; every response is validated. */
const session: SessionHandle = Object.freeze({ accountId: '00000000-0000-4000-8000-000000000001', sessionId: 'fixture-session-1' });
const requestId = '00000f12-0000-4000-8000-000000000001';
const settings = { kind: 'notifications', version: 1, match_notifications: false, message_notifications: false, device_state: 'active' };

class Recording implements NotificationTransport {
  calls: string[] = [];
  body: unknown = { contract_version: 'gapp-api-v1', request_id: requestId, data: settings };
  async settings() { this.calls.push('settings'); return this.body; }
  async device(_: SessionHandle, __: string, intent: DeviceIntent) { this.calls.push(`device:${intent.action}`); return this.body; }
  async notifications() { this.calls.push('notifications'); return this.body; }
}
const failure = async (work: () => Promise<unknown>) => {
  try { await work(); } catch (error) { assert.ok(error instanceof NotificationFailure); return error.code; }
  assert.fail('no failure');
};

test('an intent that does not follow its contract never reaches the transport', async () => {
  const transport = new Recording();
  const client = new NotificationClient(transport);
  const bad: unknown[] = [
    { operation: 'device', meta: { expected_version: 0, idempotency_key: 'k' }, device_id: FIXTURE_INSTALLATION_ID, action: 'rotate', provider_token: 'x' },
    { operation: 'device', meta: { expected_version: 0, idempotency_key: 'k' }, device_id: 'not-a-uuid', action: 'register', provider_token: 'x' },
    { operation: 'device', meta: { expected_version: 0, idempotency_key: 'k' }, device_id: FIXTURE_INSTALLATION_ID, action: 'revoke', provider_token: 'x' },
    { operation: 'device', meta: { expected_version: 0, idempotency_key: 'k' }, device_id: FIXTURE_INSTALLATION_ID, action: 'register', provider_token: null },
    { operation: 'device', meta: { expected_version: -1, idempotency_key: 'k' }, device_id: FIXTURE_INSTALLATION_ID, action: 'register', provider_token: 'x' },
    { operation: 'device', meta: { expected_version: 0, idempotency_key: 'k' }, device_id: FIXTURE_INSTALLATION_ID, action: 'register', provider_token: 'x', platform: 'web' },
  ];
  for (const intent of bad) assert.equal(await failure(() => client.device(session, FIXTURE_INSTALLATION_ID, intent as DeviceIntent)), 'invalid_request');
  const badSettings: unknown[] = [
    { operation: 'notifications', meta: { expected_version: 1, idempotency_key: 'k' }, match_notifications: 'yes', message_notifications: false },
    { operation: 'notifications', meta: { expected_version: 1, idempotency_key: 'k' }, match_notifications: true, message_notifications: false, device_id: FIXTURE_INSTALLATION_ID },
  ];
  for (const intent of badSettings) assert.equal(await failure(() => client.save(session, FIXTURE_INSTALLATION_ID, intent as NotificationIntent)), 'invalid_request');
  assert.throws(() => client.deviceIntent('not-a-uuid', 'register', 'x', 0, 'k'), NotificationFailure);
  assert.throws(() => client.settingsIntent(true, false, -1, 'k'), NotificationFailure);
  assert.deepEqual(transport.calls, []);
  await client.device(session, FIXTURE_INSTALLATION_ID, client.deviceIntent(FIXTURE_INSTALLATION_ID, 'register', 'x', 0, 'k'));
  await client.save(session, FIXTURE_INSTALLATION_ID, client.settingsIntent(true, false, 1, 'k2'));
  assert.deepEqual(transport.calls, ['device:register', 'notifications']);
});

test('only a response the generated NotificationSettings contract accepts reaches the screen', async () => {
  const transport = new Recording();
  const client = new NotificationClient(transport);
  const read = await client.read(session, FIXTURE_INSTALLATION_ID);
  assert.deepEqual(read, { status: 'present', settings });
  assert.ok(Object.isFrozen(read));
  const envelope = (data: unknown) => ({ contract_version: 'gapp-api-v1', request_id: requestId, data });
  for (const body of [
    envelope({ ...settings, provider_token: 'x' }),
    envelope({ ...settings, token_reference: 'x' }),
    envelope({ ...settings, device_state: 'none' }),
    envelope({ ...settings, version: 0 }),
    envelope({ ...settings, kind: 'message' }),
    envelope({ kind: 'notifications', version: 1, match_notifications: true }),
    { ...envelope(settings), provider: 'x' },
    { contract_version: 'gapp-api-v1', request_id: requestId, code: 'provider_unavailable', retryable: true, message: 'provider text' },
    'not json',
    null,
  ]) {
    transport.body = body;
    assert.equal(await failure(() => client.read(session, FIXTURE_INSTALLATION_ID)), 'invalid_response', JSON.stringify(body));
  }
});

test('a not_found read is the explicit absence of a registration; other errors map to Glow codes', async () => {
  const transport = new Recording();
  const client = new NotificationClient(transport);
  const error = (code: string, retryable = false) => ({ contract_version: 'gapp-api-v1', request_id: requestId, code, retryable });
  transport.body = error('not_found');
  assert.deepEqual(await client.read(session, FIXTURE_INSTALLATION_ID), { status: 'absent' });
  const cases: [string, string][] = [['unauthenticated', 'signed_out'], ['stale_version', 'stale'], ['state_conflict', 'not_active'],
    ['idempotency_conflict', 'conflict'], ['provider_unavailable', 'temporary'], ['forbidden', 'unavailable']];
  for (const [code, expected] of cases) {
    transport.body = error(code);
    assert.equal(await failure(() => client.save(session, FIXTURE_INSTALLATION_ID, client.settingsIntent(true, false, 1, 'k'))), expected, code);
  }
  transport.device = async () => { throw new Error('lost'); };
  assert.equal(await failure(() => client.device(session, FIXTURE_INSTALLATION_ID, client.deviceIntent(FIXTURE_INSTALLATION_ID, 'revoke', null, 1, 'k'))), 'offline');
});
