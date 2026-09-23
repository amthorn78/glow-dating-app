import assert from 'node:assert/strict';
import test from 'node:test';
import type { PreferencesIntent, ProfileIntent, VisibilityIntent } from '../contracts/generated/gapp-api-v1.ts';
import { parseAppResponse, ProductionContractError } from '../contracts/production.ts';
import { createProfileAdapter, ProfileFailure, type ProfileAdapter, type ProfileContext } from './fixture-adapter.ts';
import { FIXTURE_PREFERENCE_POLICY, PROFILE_IDS, PROFILE_REQUEST_ID, type ProfileAuthority } from './policy.ts';

const options = { isDevelopment: true, mode: 'fixture' };
const authority: ProfileAuthority = { ownerId: '11111111-1111-4111-8111-111111111111',
  generation: 1, accountVersion: 1, accountState: 'active', sessionState: 'valid', adult: true,
  consentCurrent: true, consentRevision: '1:development-consent-1', sourceRevision: 0 };
const failure = (code: ProfileFailure['code']) => (error: unknown) => error instanceof ProfileFailure && error.code === code;
const profileIntent = (expected_version = 0, key = 'profile-request'): ProfileIntent => ({
  operation: 'profile', meta: { idempotency_key: key, expected_version }, display_name: 'Alex', summary: 'A fictional biography.',
});
const preferencesIntent = (expected_version = 0, key = 'preferences-request'): PreferencesIntent => ({
  operation: 'preferences', meta: { idempotency_key: key, expected_version }, policy_version: FIXTURE_PREFERENCE_POLICY.version,
  selections: [{ dimension: 'demo_connection', accepted_option_ids: ['demo_a', 'demo_b'] }],
});
const visibilityIntent = (action: VisibilityIntent['action'], expected_version: number, key: string = action): VisibilityIntent => ({
  operation: 'visibility', meta: { idempotency_key: key, expected_version }, action,
});
function adapter() {
  const port = createProfileAdapter(options);
  port.synchronize(authority);
  return port;
}
async function commitProfile(port: ProfileAdapter, intent = profileIntent()) {
  const context = port.context();
  const result = await port.saveProfile(context, intent);
  port.acknowledge(context, result);
  return result;
}
async function commitVisibility(port: ProfileAdapter, action: VisibilityIntent['action']) {
  const context = port.context();
  const version = port.inspect().profile!.version;
  const result = await port.visibility(context, visibilityIntent(action, version, `${action}-${version}`));
  port.acknowledge(context, result);
  return result;
}
function delayOne() {
  let held = false;
  let release = () => {};
  return { pause: () => {
    if (!held) return Promise.resolve();
    held = false;
    return new Promise<void>(resolve => { release = resolve; });
  }, hold() { held = true; }, release() { release(); } };
}

test('profile fixture refuses non-development or non-fixture construction', () => {
  for (const invalid of [{ isDevelopment: false, mode: 'fixture' }, { isDevelopment: true, mode: 'production' },
    { isDevelopment: true, mode: undefined }]) assert.throws(() => createProfileAdapter(invalid));
});

test('profile adapter denies wrong owner, generation and object before reads or writes', async () => {
  const port = adapter();
  const context = port.context();
  const wrong: ProfileContext[] = [{ ...context, ownerId: '22222222-2222-4222-8222-222222222222' },
    { ...context, generation: context.generation + 1 }, { ...context, profileId: PROFILE_IDS.sam }];
  for (const supplied of wrong) {
    await assert.rejects(port.read(supplied), failure('forbidden'));
    await assert.rejects(port.saveProfile(supplied, profileIntent()), failure('forbidden'));
    await assert.rejects(port.savePreferences(supplied, preferencesIntent()), failure('forbidden'));
  }
  assert.deepEqual(await port.read(context), { profile: null, preferences: null });
});

test('profile creation uses version zero once, and stale replacement never overwrites accepted text', async () => {
  const port = adapter();
  await assert.rejects(port.saveProfile(port.context(), profileIntent(1)), failure('stale_version'));
  const accepted = await commitProfile(port);
  assert.equal(accepted.visibility, 'incomplete');
  assert.equal(accepted.version, 1);
  await assert.rejects(port.saveProfile(port.context(), { ...profileIntent(0, 'new-request'), display_name: 'Obsolete' }), failure('stale_version'));
  assert.deepEqual((await port.read(port.context())).profile, accepted);
});

test('malformed profile, preferences and visibility responses cannot leave accepted hidden state', async () => {
  for (const operation of ['profile', 'preferences', 'visibility'] as const) {
    const port = adapter();
    if (operation === 'visibility') port.seedEligible();
    const before = port.inspect();
    const context = port.context();
    const result = operation === 'profile' ? await port.saveProfile(context, profileIntent(), 'malformed')
      : operation === 'preferences' ? await port.savePreferences(context, preferencesIntent(), 'malformed')
        : await port.visibility(context, visibilityIntent('pause', 1), 'malformed');
    assert.deepEqual(port.inspect(), before, 'unacknowledged responses must not publish fixture state');
    assert.throws(() => parseAppResponse({ contract_version: 'gapp-api-v1', request_id: PROFILE_REQUEST_ID, data: result }), ProductionContractError);
    assert.throws(() => port.acknowledge(context, result), ProductionContractError);
    port.cancelPending();
    assert.deepEqual(await port.read(port.context()), { profile: before.profile, preferences: before.preferences });
    const retried = operation === 'profile' ? await port.saveProfile(context, profileIntent())
      : operation === 'preferences' ? await port.savePreferences(context, preferencesIntent())
        : await port.visibility(context, visibilityIntent('pause', 1));
    port.acknowledge(context, retried);
    assert.equal(retried.version, operation === 'visibility' ? 2 : 1);
  }
});

test('idempotent profile replay ignores object insertion order, but changed content conflicts', async () => {
  const port = adapter();
  const request = profileIntent();
  const accepted = await commitProfile(port, request);
  const reordered: ProfileIntent = { summary: request.summary, display_name: request.display_name,
    meta: { expected_version: 0, idempotency_key: request.meta.idempotency_key }, operation: 'profile' };
  const replay = await port.saveProfile(port.context(), reordered);
  port.acknowledge(port.context(), replay);
  assert.deepEqual(replay, accepted);
  await assert.rejects(port.saveProfile(port.context(), { ...request, summary: 'Changed during retry' }), failure('idempotency_conflict'));
  assert.deepEqual(port.inspect().profile, accepted);
});

test('preference idempotency preserves array ordering and isolates operation identities', async () => {
  const port = adapter();
  await commitProfile(port, profileIntent(0, 'shared-key'));
  const request = preferencesIntent(0, 'shared-key');
  const accepted = await port.savePreferences(port.context(), request);
  port.acknowledge(port.context(), accepted);
  const reordered: PreferencesIntent = { selections: [{ accepted_option_ids: ['demo_a', 'demo_b'], dimension: 'demo_connection' }],
    policy_version: request.policy_version, meta: { expected_version: 0, idempotency_key: 'shared-key' }, operation: 'preferences' };
  assert.deepEqual(await port.savePreferences(port.context(), reordered), accepted);
  await assert.rejects(port.savePreferences(port.context(), { ...request,
    selections: [{ dimension: 'demo_connection', accepted_option_ids: ['demo_b', 'demo_a'] }] }), failure('idempotency_conflict'));
  assert.equal(port.inspect().preferences?.version, 1);
  assert.equal(port.inspect().profile?.version, 1);
});

test('old receipts cannot revive stale profile projections or bypass current authorization', async () => {
  const port = adapter();
  const request = profileIntent();
  await commitProfile(port, request);
  port.developmentChange('profile');
  await assert.rejects(port.saveProfile(port.context(), request), failure('stale_version'));
  const current = port.inspect().profile;
  port.synchronize({ ...authority, sessionState: 'expired' });
  await assert.rejects(port.saveProfile({ ownerId: authority.ownerId!, generation: 1, authorityRevision: 1,
    profileId: PROFILE_IDS.alex }, request), failure('unauthenticated'));
  assert.deepEqual(port.inspect().profile, current);
});

test('duplicate concurrent submissions cannot both stage a mutation', async () => {
  const port = adapter();
  const context = port.context();
  const results = await Promise.allSettled([port.saveProfile(context, profileIntent()), port.saveProfile(context, profileIntent())]);
  const accepted = results.find(result => result.status === 'fulfilled');
  const rejected = results.find(result => result.status === 'rejected');
  assert.equal(accepted?.status, 'fulfilled');
  assert.equal(rejected?.status, 'rejected');
  assert.ok(rejected && failure('state_conflict')(rejected.reason));
  if (accepted?.status !== 'fulfilled') throw new Error('Missing successful response.');
  port.acknowledge(context, accepted.value);
  assert.equal(port.inspect().profile?.version, 1);
});

test('delayed mutation and pre-adoption acknowledgment are revoked by authority changes', async () => {
  for (const next of [{ ...authority, consentCurrent: false }, { ...authority, consentRevision: '2:development-consent-1' }, { ...authority, generation: 2 },
    { ...authority, ownerId: '22222222-2222-4222-8222-222222222222' }, { ...authority, accountState: 'suspended' }]) {
    const latch = delayOne();
    const port = createProfileAdapter({ ...options, pause: latch.pause });
    port.synchronize(authority);
    const context = port.context();
    latch.hold();
    const delayed = port.saveProfile(context, profileIntent());
    port.synchronize(next);
    latch.release();
    await assert.rejects(delayed, failure('stale_version'));
    assert.equal(port.inspect().profile, null);
    port.synchronize(authority);
    const fresh = port.context();
    const pending = await port.saveProfile(fresh, profileIntent());
    port.synchronize(next);
    assert.throws(() => port.acknowledge(fresh, pending), ProfileFailure);
    assert.equal(port.inspect().profile, null);
  }
});

test('visible pause is explicit, paused edits stay paused, and resume rechecks current evidence', async () => {
  const port = adapter();
  port.seedEligible();
  await assert.rejects(port.visibility(port.context(), visibilityIntent('resume', 1)), failure('state_conflict'));
  await commitVisibility(port, 'pause');
  const edited = await commitProfile(port, { ...profileIntent(2, 'paused-edit'), summary: 'Paused biography' });
  assert.equal(edited.visibility, 'paused');
  assert.equal((await commitVisibility(port, 'resume')).visibility, 'visible');
  await commitVisibility(port, 'pause');
  port.developmentChange('media');
  await assert.rejects(port.visibility(port.context(), visibilityIntent('resume', port.inspect().profile!.version, 'resume-current')), failure('forbidden'));
  assert.equal(port.inspect().profile?.visibility, 'paused');
});

test('preference changes retract visible eligibility and never manufacture reciprocal evidence', async () => {
  const port = adapter();
  port.seedEligible();
  const context = port.context();
  const result = await port.savePreferences(context, preferencesIntent(1));
  port.acknowledge(context, result);
  assert.equal(port.inspect().profile?.visibility, 'incomplete');
  assert.equal(port.inspect().evidence.reciprocalPreferencesVersion, null);
  const edited = await commitProfile(port, profileIntent(port.inspect().profile!.version, 'text-only'));
  assert.equal(edited.visibility, 'incomplete');
});

test('new preference policy refuses stale catalog writes and cannot resume a paused profile', async () => {
  const port = adapter();
  port.seedEligible();
  await commitVisibility(port, 'pause');
  port.developmentChange('policy');
  await assert.rejects(port.savePreferences(port.context(), preferencesIntent(1)), failure('policy_unresolved'));
  await assert.rejects(port.visibility(port.context(), visibilityIntent('resume', 2)), failure('forbidden'));
  assert.equal(port.inspect().profile?.visibility, 'paused');
});

test('profile failure diagnostics do not contain private submitted text', async () => {
  const port = adapter();
  const value = 'Private fictional phrase';
  await assert.rejects(port.saveProfile(port.context(), { ...profileIntent(), summary: value }, 'error'), error => {
    assert.ok(error instanceof ProfileFailure);
    assert.equal(error.code, 'provider_unavailable');
    assert.equal(error.message.includes(value), false);
    assert.equal(JSON.stringify(error).includes(value), false);
    return true;
  });
});

test('method-specific validation rejects valid DTOs supplied to the wrong mutation operation', async () => {
  const port = adapter();
  const context = port.context();
  await assert.rejects(port.saveProfile(context, preferencesIntent() as unknown as ProfileIntent), failure('invalid_request'));
  await assert.rejects(port.savePreferences(context, profileIntent() as unknown as PreferencesIntent), failure('invalid_request'));
  await assert.rejects(port.visibility(context, profileIntent() as unknown as VisibilityIntent), failure('invalid_request'));
  assert.equal(port.inspect().profile, null);
  assert.equal(port.inspect().preferences, null);
});

test('profile request and nested command metadata are snapshotted before awaiting', async () => {
  const latch = delayOne();
  const port = createProfileAdapter({ ...options, pause: latch.pause });
  port.synchronize(authority);
  const context = port.context();
  const request = profileIntent();
  latch.hold();
  const pending = port.saveProfile(context, request);
  request.display_name = 'Changed while waiting';
  request.summary = 'Changed while waiting';
  request.meta.expected_version = 100;
  request.meta.idempotency_key = 'substituted-key';
  latch.release();
  const result = await pending;
  port.acknowledge(context, result);
  assert.equal(result.display_name, 'Alex');
  assert.equal(result.summary, 'A fictional biography.');
  assert.equal(result.version, 1);
  assert.deepEqual(await port.saveProfile(context, profileIntent()), result);
});

test('preference request nested selections are snapshotted before awaiting', async () => {
  const latch = delayOne();
  const port = createProfileAdapter({ ...options, pause: latch.pause });
  port.synchronize(authority);
  const context = port.context();
  const request = preferencesIntent();
  latch.hold();
  const pending = port.savePreferences(context, request);
  request.selections[0]!.accepted_option_ids.reverse();
  request.policy_version = 'unknown-policy';
  request.meta.expected_version = 100;
  latch.release();
  const result = await pending;
  port.acknowledge(context, result);
  assert.deepEqual(result.selections[0]!.accepted_option_ids, ['demo_a', 'demo_b']);
  assert.equal(result.policy_version, FIXTURE_PREFERENCE_POLICY.version);
  assert.deepEqual(await port.savePreferences(context, preferencesIntent()), result);
});

test('changing a pending visibility request into a profile DTO cannot bypass resume state or eligibility', async () => {
  const latch = delayOne();
  const port = createProfileAdapter({ ...options, pause: latch.pause });
  port.synchronize(authority);
  await commitProfile(port);
  const before = port.inspect();
  const context = port.context();
  const request = visibilityIntent('resume', 1);
  latch.hold();
  const pending = port.visibility(context, request);
  const mutable = request as unknown as Record<string, unknown>;
  delete mutable.action;
  Object.assign(mutable, { operation: 'profile', display_name: 'Alex', summary: 'Nonblank biography' });
  latch.release();
  await assert.rejects(pending, failure('state_conflict'));
  assert.deepEqual(port.inspect(), before);
  assert.equal(port.inspect().profile?.visibility, 'incomplete');
});

test('mutable read and write contexts cannot change the authority captured when a request starts', async () => {
  const latch = delayOne();
  const port = createProfileAdapter({ ...options, pause: latch.pause });
  port.synchronize(authority);
  const original = port.context();
  const writeContext = { ...original };
  latch.hold();
  const pendingWrite = port.saveProfile(writeContext, profileIntent());
  writeContext.profileId = PROFILE_IDS.sam;
  writeContext.ownerId = '22222222-2222-4222-8222-222222222222';
  writeContext.generation = 2;
  latch.release();
  const accepted = await pendingWrite;
  port.acknowledge(original, accepted);
  assert.equal(accepted.profile_id, PROFILE_IDS.alex);
  const readContext = { ...original };
  latch.hold();
  const pendingRead = port.read(readContext);
  readContext.ownerId = writeContext.ownerId;
  readContext.profileId = PROFILE_IDS.sam;
  latch.release();
  assert.deepEqual((await pendingRead).profile, accepted);
});
