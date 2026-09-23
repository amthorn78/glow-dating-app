import assert from 'node:assert/strict';
import test from 'node:test';
import { createFixtureOnboardingStore, FIXTURE_PASSWORD } from '../onboarding/store.ts';
import { createMediaAdapter } from './fixture-adapter.ts';
import { MediaStore } from './store.ts';
import { FIXTURE_MEDIA_POLICY, syntheticSelection } from './policy.ts';
import type { ProfileAuthority } from '../profiles/policy.ts';

const options = { isDevelopment: true, mode: 'fixture' };
const authority: ProfileAuthority = { ownerId: '11111111-1111-4111-8111-111111111111', generation: 1,
  accountVersion: 1, accountState: 'active', sessionState: 'valid', adult: true, consentCurrent: true,
  sourceRevision: 0, consentRevision: '1:development-consent-1' };
function store() { const subject = new MediaStore(options); subject.synchronize(authority); return subject; }
async function pending(subject: MediaStore): Promise<string> {
  subject.select(syntheticSelection()); await subject.requestUpload();
  assert.equal(subject.getSnapshot().error, null);
  return subject.getSnapshot().collection.items.at(-1)!.asset_id;
}
async function approve(subject: MediaStore): Promise<string> {
  const id = await pending(subject); await subject.upload(id); await subject.developerEvent(id, 'review'); await subject.developerEvent(id, 'approve');
  assert.equal(subject.getSnapshot().collection.items.find(item => item.asset_id === id)?.state, 'approved');
  return id;
}
function holdOne() {
  let held = false, release = () => {};
  return { pause: () => !held ? Promise.resolve() : (held = false, new Promise<void>(resolve => { release = resolve; })),
    hold() { held = true; }, release() { release(); } };
}

test('media UI snapshot never exposes selected bytes, upload capabilities or private adapter context', async () => {
  const subject = store(); subject.select(syntheticSelection());
  assert.deepEqual(Object.keys(subject.getSnapshot()).sort(), ['ownerKey', 'collection', 'transports', 'selection', 'selectionRevision', 'policyVersion', 'busy', 'error', 'message'].sort());
  assert.deepEqual(Object.keys(subject.getSnapshot().selection!).sort(), ['selectionId', 'name', 'declaredMime', 'byteLength'].sort());
  await subject.requestUpload();
  assert.equal(subject.getSnapshot().selection, null);
  assert.doesNotMatch(JSON.stringify(subject.getSnapshot()), /grant_ref|expires_at|storage_key|bytes":|engine_id/);
});

test('picker completion bound to old revision or owner cannot restore private selection', () => {
  const subject = store(), old = subject.getSnapshot();
  subject.selectionResult('cancelled'); subject.select(syntheticSelection(), old.selectionRevision, old.ownerKey);
  assert.equal(subject.getSnapshot().selection, null);
  subject.synchronize({ ...authority, ownerId: '22222222-2222-4222-8222-222222222222', generation: 2 });
  subject.select(syntheticSelection(), old.selectionRevision, old.ownerKey);
  assert.equal(subject.getSnapshot().selection, null);
});

test('cancelling selection while a grant is delayed prevents asset creation and hidden reload adoption', async () => {
  const deferred = holdOne(), subject = new MediaStore({ ...options, pause: deferred.pause }); subject.synchronize(authority);
  subject.select(syntheticSelection()); deferred.hold(); const preparing = subject.requestUpload();
  subject.selectionResult('cancelled'); deferred.release(); await preparing;
  assert.equal(subject.getSnapshot().collection.items.length, 0);
  assert.equal(subject.getSnapshot().selection, null);
  assert.equal(subject.getSnapshot().busy, false);
  await subject.reload(); assert.equal(subject.getSnapshot().collection.items.length, 0);
});

test('malformed and wrong-object grant/read responses leave no hidden accepted assets', async () => {
  for (const outcome of ['malformed', 'wrong_object'] as const) {
    const subject = store(); subject.select(syntheticSelection()); await subject.requestUpload(outcome);
    assert.ok(subject.getSnapshot().error); assert.equal(subject.getSnapshot().collection.items.length, 0);
    await subject.reload(); assert.equal(subject.getSnapshot().collection.items.length, 0);
    await subject.reload(outcome); assert.ok(subject.getSnapshot().error);
    await subject.reload(); assert.equal(subject.getSnapshot().collection.items.length, 0);
    const id = await pending(subject), before = subject.getSnapshot().collection;
    await subject.reload(outcome); assert.ok(subject.getSnapshot().error);
    await subject.reload(); assert.deepEqual(subject.getSnapshot().collection, before);
    await subject.upload(id, outcome); assert.ok(subject.getSnapshot().error);
    await subject.reload(); assert.equal(subject.getSnapshot().collection.items[0]!.state, 'upload_pending');
    await subject.upload(id); assert.equal(subject.getSnapshot().collection.items[0]!.state, 'quarantined');
  }
});

test('interruption retries the same asset and terminal expiry requires a new grant identity', async () => {
  const subject = store(), id = await pending(subject);
  await subject.upload(id, 'interrupted');
  assert.equal(subject.getSnapshot().collection.items[0]!.state, 'upload_pending');
  assert.equal(subject.getSnapshot().transports[0]!.status, 'interrupted');
  subject.advanceClock(FIXTURE_MEDIA_POLICY.grantDurationMs + 1);
  await subject.upload(id); assert.match(subject.getSnapshot().error!, /expired/);
  await subject.upload(id); assert.match(subject.getSnapshot().error!, /expired/);
  await subject.remove(id); const replacement = await pending(subject);
  assert.notEqual(replacement, id); await subject.upload(replacement);
  assert.equal(subject.getSnapshot().collection.items.find(item => item.asset_id === id)!.state, 'removal_pending');
  assert.equal(subject.getSnapshot().collection.items.find(item => item.asset_id === replacement)!.state, 'quarantined');
});

test('cancelling a delayed upload revokes its attempt before owner removal and stale completion', async () => {
  const deferred = holdOne(), subject = new MediaStore({ ...options, pause: deferred.pause }); subject.synchronize(authority);
  const id = await pending(subject); deferred.hold(); const upload = subject.upload(id);
  assert.equal(subject.getSnapshot().transports[0]!.status, 'uploading');
  await subject.cancel(id); deferred.release(); await upload;
  assert.equal(subject.getSnapshot().collection.items[0]!.state, 'removal_pending');
  assert.equal(subject.approvedCollection().items.length, 0);
});

test('owner replacement clears every emitted private media snapshot and rejects late work', async () => {
  const deferred = holdOne(), subject = new MediaStore({ ...options, pause: deferred.pause }); subject.synchronize(authority);
  const id = await pending(subject); deferred.hold(); const upload = subject.upload(id);
  const seen: string[] = []; subject.subscribe(() => seen.push(JSON.stringify(subject.getSnapshot())));
  subject.synchronize({ ...authority, ownerId: '22222222-2222-4222-8222-222222222222', generation: 2 });
  deferred.release(); await upload;
  assert.ok(seen.length); seen.forEach(value => assert.equal(value.includes(id), false));
  assert.equal(subject.getSnapshot().collection.items.length, 0);
});

test('removal denies delivery while awaiting acknowledgment; failed purge stays pending', async () => {
  const deferred = holdOne(), subject = new MediaStore({ ...options, pause: deferred.pause }); subject.synchronize(authority);
  const id = await approve(subject); deferred.hold(); const removal = subject.remove(id);
  assert.equal(subject.approvedCollection().items.length, 0);
  deferred.release(); await removal;
  await subject.developerEvent(id, 'purged', 'error');
  assert.equal(subject.getSnapshot().collection.items[0]!.state, 'removal_pending');
  await subject.developerEvent(id, 'purged');
  assert.equal(subject.getSnapshot().collection.items[0]!.state, 'removed');
});

test('malformed removal is not accepted on reload and local delivery remains revoked', async () => {
  const subject = store(), id = await approve(subject);
  await subject.remove(id, 'malformed'); assert.ok(subject.getSnapshot().error);
  await subject.reload(); assert.equal(subject.getSnapshot().collection.items[0]!.state, 'approved');
  assert.equal(subject.approvedCollection().items.length, 0);
  await subject.remove(id); assert.equal(subject.getSnapshot().collection.items[0]!.state, 'removal_pending');
});

test('approved-only order is reflected in candidate delivery and last-photo loss revokes retained preview', async () => {
  const subject = createFixtureOnboardingStore(options); subject.scenario('eligible');
  const first = subject.media.getSnapshot().collection.items[0]!.asset_id;
  const second = await approve(subject.media);
  assert.equal(subject.profiles.candidatePreview()!.media_delivery_refs.length, 2);
  await subject.media.move(second, -1);
  assert.match(subject.profiles.candidatePreview()!.media_delivery_refs[0]!, new RegExp(second));
  const oldContext = subject.profiles.candidateContext();
  await subject.media.remove(second);
  assert.equal(subject.profiles.candidatePreview(oldContext), null);
  assert.equal(subject.profiles.getSnapshot().canDiscover, true);
  await subject.media.remove(first);
  assert.equal(subject.profiles.getSnapshot().canDiscover, false);
  assert.ok(subject.profiles.getSnapshot().requirements.includes('Approved photos'));
  assert.equal(subject.profiles.candidatePreview(), null);
});

test('media changes preserve accepted pause and invalidate a pending resume', async () => {
  const deferred = holdOne(), subject = createFixtureOnboardingStore({ ...options, pause: deferred.pause }); subject.scenario('eligible');
  await subject.profiles.setVisibility('pause'); deferred.hold(); const resuming = subject.profiles.setVisibility('resume');
  subject.media.restrictApproved(); deferred.release(); await resuming;
  assert.equal(subject.profiles.getSnapshot().profile!.visibility, 'paused');
  assert.equal(subject.profiles.getSnapshot().canDiscover, false);
  await subject.profiles.setVisibility('resume'); assert.ok(subject.profiles.getSnapshot().error);
});

test('late or failed approval cannot clear a newer delivery revocation with a reused scenario asset ID', async () => {
  const deferred = holdOne(), subject = new MediaStore({ ...options, pause: deferred.pause }); subject.synchronize(authority);
  subject.seedEligible(); const id = subject.getSnapshot().collection.items[0]!.asset_id;
  await subject.developerEvent(id, 'restrict_media'); deferred.hold(); const approval = subject.developerEvent(id, 'approve');
  subject.synchronize({ ...authority, generation: 2 }); subject.seedEligible(); subject.restrictApproved();
  deferred.release(); await approval;
  assert.equal(subject.approvedCollection().items.length, 0);
  await subject.developerEvent(id, 'approve'); assert.ok(subject.getSnapshot().error);
  assert.equal(subject.approvedCollection().items.length, 0);
});

test('photo approval cannot supply chart, moderation or reciprocal preference evidence', async () => {
  const subject = createFixtureOnboardingStore(options);
  await subject.account('register', 'alex@example.invalid', FIXTURE_PASSWORD); await subject.verify();
  subject.setAdultDate('1990-06-15'); subject.setConsent(true);
  subject.profiles.editProfileDraft({ display_name: 'Fiction', summary: 'Synthetic biography' }, subject.profiles.getSnapshot().profileDraftRevision);
  await subject.profiles.saveProfile(subject.profiles.getSnapshot().profileDraftRevision);
  await approve(subject.media);
  for (const missing of ['A resolved chart', 'Profile review', 'Current reciprocal preference evidence']) assert.ok(subject.profiles.getSnapshot().requirements.includes(missing));
  assert.equal(subject.profiles.getSnapshot().canDiscover, false);
});

test('policy, consent and expiry deny delivery and stale retained media drafts', async () => {
  const subject = createFixtureOnboardingStore(options); subject.scenario('eligible');
  subject.media.select(syntheticSelection()); subject.media.invalidatePolicy();
  assert.equal(subject.profiles.candidatePreview(), null); assert.equal(subject.media.getSnapshot().selection, null);
  subject.scenario('eligible'); subject.setConsent(false);
  assert.equal(subject.profiles.candidatePreview(), null);
  subject.scenario('eligible'); subject.expire();
  assert.equal(subject.media.getSnapshot().collection.items.length, 0);
  assert.equal(subject.profiles.candidatePreview(), null);
});

test('wrong-owner adapter responses fail staged acknowledgment without future adoption', async () => {
  const adapter = createMediaAdapter(options);
  const subject = new MediaStore(options, undefined, { ...adapter, requestUpload: async (context, intent, selection, outcome) => {
    const result = await adapter.requestUpload(context, intent, selection, outcome);
    return { ...result, collection: { ...result.collection, items: result.collection.items.map(item => ({ ...item, asset_id: '99999999-9999-4999-8999-999999999999' })) } };
  } });
  subject.synchronize(authority); subject.select(syntheticSelection()); await subject.requestUpload();
  assert.ok(subject.getSnapshot().error); await subject.reload(); assert.equal(subject.getSnapshot().collection.items.length, 0);
});
