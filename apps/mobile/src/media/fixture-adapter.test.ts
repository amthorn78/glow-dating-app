import assert from 'node:assert/strict';
import test from 'node:test';
import type { MediaIntent } from '../contracts/generated/gapp-api-v1.ts';
import { ProductionContractError } from '../contracts/production.ts';
import type { ProfileAuthority } from '../profiles/policy.ts';
import { createMediaAdapter, MediaFailure, type MediaAdapter, type MediaEvent, type MediaResult } from './fixture-adapter.ts';
import { FIXTURE_MEDIA_POLICY as POLICY, syntheticSelection } from './policy.ts';

const authority: ProfileAuthority = { ownerId: '11111111-1111-4111-8111-111111111111', generation: 1, accountVersion: 1,
  accountState: 'active', sessionState: 'valid', adult: true, consentCurrent: true, consentRevision: 'current', sourceRevision: 0 };
const options = { isDevelopment: true, mode: 'fixture' };
const failure = (code: MediaFailure['code']) => (error: unknown) => error instanceof MediaFailure && error.code === code;
function make(extra: Partial<Parameters<typeof createMediaAdapter>[0]> = {}) {
  const port = createMediaAdapter({ ...options, ...extra }); port.synchronize(authority); return port;
}
const intent = (action: MediaIntent['action'], version: number, id: string | null = null, ids: string[] = [], key = `${action}-${version}`): MediaIntent =>
  ({ operation: 'media', action, asset_id: id, ordered_asset_ids: ids, meta: { expected_version: version, idempotency_key: key } });
const commit = (port: MediaAdapter, response: MediaResult) => { port.acknowledge(port.context(), response); return response; };
const item = (port: MediaAdapter, id: string) => port.inspect().collection.items.find(asset => asset.asset_id === id)!;
async function add(port: MediaAdapter, key?: string) {
  const response = await port.requestUpload(port.context(), intent('request_upload', port.inspect().collection.version, null, [], key), syntheticSelection());
  commit(port, response); return response.grant!.asset_id;
}
async function event(port: MediaAdapter, id: string, action: MediaEvent['event'], outcome: 'success' | 'error' | 'interrupted' = 'success') {
  const definition: MediaEvent = { event: action, actor: action === 'review' ? 'system' : action === 'purged' ? 'provider' : 'moderator',
    assetId: id, expectedVersion: item(port, id).version, eventId: `${action}-${item(port, id).version}-${id}`, policyVersion: POLICY.version };
  const response = await port.event(port.context(), definition, outcome); return commit(port, response);
}
async function approve(port: MediaAdapter, id: string) {
  commit(port, await port.upload(port.context(), id)); await event(port, id, 'review'); await event(port, id, 'approve');
}
async function remove(port: MediaAdapter, id: string) {
  return commit(port, await port.remove(port.context(), intent('remove', item(port, id).version, id, [], `remove-${id}-${item(port, id).version}`)));
}
function delayed() {
  let hold = false, release = () => {};
  return { pause: () => { if (!hold) return Promise.resolve(); hold = false; return new Promise<void>(resolve => { release = resolve; }); },
    hold: () => { hold = true; }, release: () => release() };
}

test('media fixture refuses production construction and exposes empty versioned collection', async () => {
  assert.throws(() => createMediaAdapter({ ...options, isDevelopment: false }));
  assert.throws(() => createMediaAdapter({ ...options, mode: 'production' }));
  const port = make();
  assert.deepEqual((await port.read(port.context())).collection, { kind: 'media_collection', version: 1, items: [] });
});
test('media reads, grants and events reject other owner and generation', async () => {
  const port = make();
  for (const context of [{ ...port.context(), ownerId: 'other' }, { ...port.context(), generation: 2 }]) {
    await assert.rejects(port.read(context), failure('forbidden'));
    await assert.rejects(port.requestUpload(context, intent('request_upload', 1), syntheticSelection()), failure('forbidden'));
  }
  assert.equal(port.inspect().collection.items.length, 0);
});
test('request captures selected bytes and payload before awaiting and stages until acknowledged', async () => {
  const gate = delayed(), port = make(gate), selection = { ...syntheticSelection(), bytes: [...syntheticSelection().bytes] };
  const request = intent('request_upload', 1); gate.hold();
  const pending = port.requestUpload(port.context(), request, selection);
  selection.bytes[0] = 0; request.meta.expected_version = 999;
  gate.release(); const response = await pending;
  assert.equal(port.inspect().collection.items.length, 0);
  commit(port, response); commit(port, await port.upload(port.context(), response.grant!.asset_id));
  assert.equal(item(port, response.grant!.asset_id).state, 'quarantined');
});
test('same-key grant replay is stable without count inflation; changed bytes or policy metadata conflicts', async () => {
  const port = make(), request = intent('request_upload', 1, null, [], 'retry-grant'), selection = syntheticSelection();
  const first = commit(port, await port.requestUpload(port.context(), request, selection));
  assert.deepEqual(await port.requestUpload(port.context(), request, selection), first);
  await assert.rejects(port.requestUpload(port.context(), request, { ...selection, name: 'other.png' }), failure('idempotency_conflict'));
  assert.equal(port.inspect().collection.items.length, 1);
});
test('invalid action shapes, stale collection version and wrong asset never create accepted state', async () => {
  const port = make();
  await assert.rejects(port.requestUpload(port.context(), intent('request_upload', 0), syntheticSelection()), failure('stale_version'));
  await assert.rejects(port.requestUpload(port.context(), intent('request_upload', 1, authority.ownerId), syntheticSelection()), ProductionContractError);
  await assert.rejects(port.remove(port.context(), intent('remove', 1, authority.ownerId)), failure('forbidden'));
  assert.equal(port.inspect().collection.version, 1);
});
test('malformed or valid-shape wrong-object responses never become hidden accepted state at zero or partial collection', async () => {
  for (const partial of [false, true]) for (const outcome of ['malformed', 'wrong_object'] as const) {
    const port = make(); if (partial) await add(port);
    const before = port.inspect();
    const response = await port.requestUpload(port.context(), intent('request_upload', before.collection.version), syntheticSelection(), outcome);
    assert.throws(() => commit(port, response)); port.cancelPending();
    assert.deepEqual(port.inspect(), before);
    const read = await port.read(port.context(), outcome);
    assert.throws(() => commit(port, read)); port.cancelPending();
    assert.deepEqual((await port.read(port.context())).collection, before.collection);
  }
});
test('complete F05 upload quarantine review approval restriction rejection removal and purge path', async () => {
  const port = make(), id = await add(port);
  assert.equal(item(port, id).state, 'upload_pending'); assert.equal(item(port, id).approved_delivery_ref, null);
  commit(port, await port.upload(port.context(), id)); assert.equal(item(port, id).state, 'quarantined');
  await event(port, id, 'review'); assert.equal(item(port, id).state, 'review_pending');
  await event(port, id, 'approve'); assert.equal(item(port, id).state, 'approved'); assert.match(item(port, id).approved_delivery_ref!, /^fixture-approved-/);
  await event(port, id, 'restrict_media'); assert.equal(item(port, id).state, 'review_pending'); assert.equal(item(port, id).approved_delivery_ref, null);
  await event(port, id, 'reject'); assert.equal(item(port, id).state, 'rejected');
  await remove(port, id); assert.equal(item(port, id).state, 'removal_pending');
  await event(port, id, 'purged'); assert.equal(item(port, id).state, 'removed');
});
for (const state of ['upload_pending', 'quarantined', 'review_pending', 'approved', 'rejected'] as const) {
  test(`owner can remove ${state}; only independent provider purge finishes`, async () => {
    const port = make(), id = await add(port);
    if (state !== 'upload_pending') commit(port, await port.upload(port.context(), id));
    if (['review_pending', 'approved', 'rejected'].includes(state)) await event(port, id, 'review');
    if (state === 'approved') await event(port, id, 'approve');
    if (state === 'rejected') await event(port, id, 'reject');
    await remove(port, id);
    assert.equal(item(port, id).approved_delivery_ref, null);
    assert.equal(item(port, id).state, 'removal_pending');
    await event(port, id, 'purged'); assert.equal(item(port, id).state, 'removed');
  });
}
test('owner cannot approve or purge; upload cannot skip quarantine/review; unknown moderator policy denied', async () => {
  const port = make(), id = await add(port);
  const approval: MediaEvent = { event: 'approve', actor: 'owner', assetId: id, expectedVersion: 1, eventId: 'owner-approve', policyVersion: POLICY.version };
  await assert.rejects(port.event(port.context(), approval), failure('forbidden'));
  await assert.rejects(port.event(port.context(), { ...approval, actor: 'moderator' }), failure('state_conflict'));
  commit(port, await port.upload(port.context(), id)); await event(port, id, 'review');
  await assert.rejects(port.event(port.context(), { ...approval, actor: 'moderator', expectedVersion: item(port, id).version, policyVersion: 'unknown' }), failure('policy_unresolved'));
  await remove(port, id);
  await assert.rejects(port.event(port.context(), { ...approval, event: 'purged', expectedVersion: item(port, id).version }), failure('forbidden'));
});
test('transport retry and interruption preserve asset lifecycle and stop at bounded attempts', async () => {
  const port = make(), id = await add(port);
  for (const outcome of ['error', 'interrupted', 'error'] as const) {
    await assert.rejects(port.upload(port.context(), id, outcome));
    assert.equal(item(port, id).state, 'upload_pending');
  }
  await assert.rejects(port.upload(port.context(), id), failure('retry_limit'));
  assert.equal(port.inspect().collection.items.length, 1);
  assert.equal(port.inspect().transports[0]!.attempts, 3);
});
test('an interrupted attempt can succeed on bounded retry and a duplicate upload cannot advance review', async () => {
  const port = make(), id = await add(port);
  await assert.rejects(port.upload(port.context(), id, 'interrupted'), failure('interrupted'));
  commit(port, await port.upload(port.context(), id));
  assert.equal(port.inspect().transports[0]!.attempts, 2);
  await assert.rejects(port.upload(port.context(), id), failure('state_conflict'));
  assert.equal(item(port, id).state, 'quarantined');
});
test('forced grant expiry is terminal even after outcome changes to success', async () => {
  const port = make(), id = await add(port);
  await assert.rejects(port.upload(port.context(), id, 'expired'), failure('grant_expired'));
  await assert.rejects(port.upload(port.context(), id), failure('grant_expired'));
  assert.equal(item(port, id).state, 'upload_pending');
});
test('real fixture clock expiry before transfer and during transfer never revives a grant', async () => {
  for (const during of [false, true]) {
    let time = Date.parse('2026-09-23T12:00:00Z');
    const gate = delayed(), port = make({ pause: gate.pause, now: () => time }), id = await add(port);
    if (!during) time += POLICY.grantDurationMs;
    if (during) gate.hold();
    const transfer = port.upload(port.context(), id);
    if (during) { time += POLICY.grantDurationMs; gate.release(); }
    await assert.rejects(transfer, failure('grant_expired'));
    time -= POLICY.grantDurationMs;
    await assert.rejects(port.upload(port.context(), id), failure('grant_expired'));
  }
});
test('grant expires between staged upload and acknowledgement without accepted quarantine', async () => {
  let time = Date.parse('2026-09-23T12:00:00Z'); const port = make({ now: () => time }), id = await add(port);
  const response = await port.upload(port.context(), id); time += POLICY.grantDurationMs;
  assert.throws(() => commit(port, response), failure('grant_expired'));
  assert.equal(item(port, id).state, 'upload_pending');
  await assert.rejects(port.upload(port.context(), id), failure('grant_expired'));
});
test('cancel and replacement bind new asset/grant; late prior completion cannot consume replacement', async () => {
  const gate = delayed(), port = make(gate), old = await add(port);
  gate.hold(); const pending = port.upload(port.context(), old);
  port.cancelUpload(port.context(), old); await remove(port, old);
  const replacement = await add(port);
  assert.notEqual(replacement, old);
  gate.release(); await assert.rejects(pending, failure('stale_version'));
  commit(port, await port.upload(port.context(), replacement));
  assert.equal(item(port, replacement).state, 'quarantined'); assert.equal(item(port, old).state, 'removal_pending');
});
test('rejected staged upload reconciles uploading observation as interrupted and never survives reload', async () => {
  const port = make(), id = await add(port), response = await port.upload(port.context(), id, 'malformed');
  assert.throws(() => commit(port, response)); port.cancelPending();
  assert.equal(port.inspect().transports[0]!.status, 'interrupted');
  assert.equal((await port.read(port.context())).collection.items[0]!.state, 'upload_pending');
});
test('logout, account replacement, expiry and consent/source changes defeat delayed upload', async () => {
  for (const next of [{ ...authority, ownerId: null, sessionState: 'none' }, { ...authority, ownerId: '22222222-2222-4222-8222-222222222222' },
    { ...authority, sessionState: 'expired' }, { ...authority, consentCurrent: false }, { ...authority, sourceRevision: 2 }]) {
    const gate = delayed(), port = make(gate), id = await add(port);
    gate.hold(); const pending = port.upload(port.context(), id); port.synchronize(next); gate.release();
    await assert.rejects(pending, failure('stale_version'));
    assert.ok(port.inspect().collection.items.every(asset => asset.state !== 'quarantined'));
  }
});
test('current unknown policy cannot grant upload or approve; obsolete captured context is denied', async () => {
  const port = make(), context = port.context(); port.invalidatePolicy();
  await assert.rejects(port.requestUpload(context, intent('request_upload', 1), syntheticSelection()), failure('stale_version'));
  await assert.rejects(port.requestUpload(port.context(), intent('request_upload', 1), syntheticSelection()), failure('policy_unresolved'));
});
test('reorder requires complete current approved set and aggregate revision', async () => {
  const port = make(), first = await add(port), second = await add(port), pending = await add(port);
  await approve(port, first); await approve(port, second);
  const version = port.inspect().collection.version;
  for (const order of [[first], [first, first], [first, pending], [first, authority.ownerId!]]) {
    await assert.rejects(port.reorder(port.context(), intent('reorder', version, null, order)));
  }
  await assert.rejects(port.reorder(port.context(), intent('reorder', version - 1, null, [second, first])), failure('stale_version'));
  commit(port, await port.reorder(port.context(), intent('reorder', version, null, [second, first])));
  assert.deepEqual(port.inspect().collection.items.filter(asset => asset.state === 'approved').map(asset => asset.asset_id), [second, first]);
  assert.equal(item(port, pending).state, 'upload_pending');
});
test('concurrent accepted remove defeats stale order response and cannot resurrect an asset', async () => {
  const gate = delayed(), port = make(gate), first = await add(port), second = await add(port);
  await approve(port, first); await approve(port, second);
  gate.hold(); const reorder = port.reorder(port.context(), intent('reorder', port.inspect().collection.version, null, [second, first]));
  await remove(port, first); gate.release();
  await assert.rejects(reorder, failure('stale_version')); assert.equal(item(port, first).state, 'removal_pending');
});
test('provider purge failure stays pending/retryable; duplicate and changed/out-of-order events cannot fake deletion', async () => {
  const port = make(), id = await add(port); await remove(port, id);
  await assert.rejects(event(port, id, 'purged', 'error'), failure('provider_unavailable'));
  assert.equal(item(port, id).state, 'removal_pending');
  const definition: MediaEvent = { event: 'purged', actor: 'provider', assetId: id, expectedVersion: item(port, id).version,
    eventId: 'purge-final', policyVersion: POLICY.version };
  const response = commit(port, await port.event(port.context(), definition));
  assert.deepEqual(await port.event(port.context(), definition), response);
  await assert.rejects(port.event(port.context(), { ...definition, assetId: authority.ownerId! }), failure('idempotency_conflict'));
  await assert.rejects(port.event(port.context(), { ...definition, eventId: 'late', expectedVersion: 1 }), failure('stale_version'));
  assert.equal(item(port, id).state, 'removed');
});
test('purge retry exhaustion remains removal_pending rather than claiming deletion', async () => {
  const port = make(), id = await add(port); await remove(port, id);
  for (let attempt = 0; attempt < POLICY.maxPurgeAttempts; attempt += 1) await assert.rejects(event(port, id, 'purged', 'error'));
  await assert.rejects(event(port, id, 'purged'), failure('retry_limit'));
  assert.equal(item(port, id).state, 'removal_pending');
});
test('four live photos and twenty retained lifecycle entries bound fixture resources', async () => {
  const port = make();
  for (let n = 0; n < POLICY.maxPhotos; n += 1) await add(port);
  await assert.rejects(add(port), failure('count_limit'));
  const first = port.inspect().collection.items[0]!.asset_id; await remove(port, first);
  await add(port); // A removed-from-delivery photo does not consume a live-photo slot.
  for (const asset of port.inspect().collection.items.filter(asset => asset.state !== 'removal_pending')) await remove(port, asset.asset_id);
  while (port.inspect().collection.items.length < POLICY.maxCollection) { const id = await add(port); await remove(port, id); }
  await assert.rejects(add(port), failure('count_limit'));
  assert.equal(port.inspect().collection.items.length, 20);
});

test('exhausted discretionary receipt capacity preserves reserved owner removal and provider purge capacity', async () => {
  const port = make(); port.seedEligible();
  const id = port.inspect().collection.items[0]!.asset_id;
  for (let receipt = 0; receipt < POLICY.maxReceipts; receipt += 1) {
    commit(port, await port.reorder(port.context(), intent('reorder', port.inspect().collection.version, null, [id], `fill-${receipt}`)));
  }
  await assert.rejects(port.reorder(port.context(), intent('reorder', port.inspect().collection.version, null, [id], 'over-limit')), failure('count_limit'));
  await assert.rejects(add(port, 'over-limit-upload'), failure('count_limit'));
  assert.equal(item(port, id).state, 'approved');
  await remove(port, id);
  assert.equal(item(port, id).state, 'removal_pending');
  assert.equal(item(port, id).approved_delivery_ref, null);
  await event(port, id, 'purged');
  assert.equal(item(port, id).state, 'removed');
  await assert.rejects(add(port, 'still-over-limit-upload'), failure('count_limit'));
  assert.equal(port.inspect().collection.items.length, 1);
});
