import assert from 'node:assert/strict';
import test from 'node:test';
import { createFixtureOnboardingStore } from '../onboarding/store.ts';
import { createFixtureProfileStore } from './store.ts';
import type { ProfileAuthority } from './policy.ts';
const options = { isDevelopment: true, mode: 'fixture' };
function eligible() {
  const store = createFixtureOnboardingStore(options); store.scenario('eligible'); return store;
}
for (const [change, restore] of [['block_viewer', 'clear_blocks'], ['block_candidate', 'clear_blocks'],
  ['viewer_preferences', 'restore_viewer_preferences'], ['viewer_pause', 'viewer_resume'], ['candidate_attribute', 'candidate_attribute']] as const) {
  test(`current ${change} facts revoke pair immediately; ${restore} does not revive retained context`, () => {
    const { profiles } = eligible();
    const captured = profiles.candidateContext()!;
    assert.ok(profiles.candidatePreview(captured)); assert.ok(Object.isFrozen(captured.version));
    profiles.developmentPairChange(change);
    assert.equal(profiles.getSnapshot().canDiscover, true, 'Own completeness is independent of the other person.');
    assert.equal(profiles.candidatePreview(captured), null); assert.equal(profiles.candidatePreview(), null);
    profiles.developmentPairChange(restore);
    assert.ok(profiles.candidatePreview()); assert.equal(profiles.candidatePreview(captured), null);
    const newer = profiles.candidateContext()!;
    profiles.developmentPairChange(change); profiles.developmentPairChange(restore);
    assert.equal(profiles.candidatePreview(newer), null, 'Repeated A→B→A cannot reuse an earlier version.');
    assert.ok(profiles.candidatePreview());
  });
}

test('own preferences independently accept the viewer attribute and do not change either attribute', async () => {
  const { profiles } = eligible(), retained = profiles.candidateContext();
  profiles.editPreferencesDraft([{ dimension: 'demo_connection', accepted_option_ids: ['demo_b'] }], profiles.getSnapshot().preferencesDraftRevision);
  await profiles.savePreferences(profiles.getSnapshot().preferencesDraftRevision);
  assert.equal(profiles.getSnapshot().canDiscover, true); assert.equal(profiles.candidatePreview(), null);
  profiles.developmentPairChange('viewer_preferences'); profiles.developmentPairChange('candidate_attribute');
  assert.equal(profiles.candidatePreview(), null, 'Viewer accepts candidate B, but candidate accepts B while viewer remains A.');
  profiles.editPreferencesDraft([{ dimension: 'demo_connection', accepted_option_ids: ['demo_a'] }], profiles.getSnapshot().preferencesDraftRevision);
  await profiles.savePreferences(profiles.getSnapshot().preferencesDraftRevision);
  assert.ok(profiles.candidatePreview(), 'Opposite attributes can be reciprocal with independently selected accepted sets.');
  assert.equal(profiles.candidatePreview(retained), null);
});

test('pair projection derives age from birth and clock and rejects old clock epochs after restoration', () => {
  let day = '2026-09-23';
  const store = createFixtureOnboardingStore({ ...options, clock: () => new Date(`${day}T12:00:00Z`) });
  store.scenario('eligible');
  const retained = store.profiles.candidateContext();
  assert.equal(store.profiles.candidatePreview(retained)?.age, 36);
  day = '2027-09-23';
  assert.equal(store.profiles.candidatePreview(retained), null); assert.equal(store.profiles.candidatePreview()?.age, 37);
  day = '2026-09-23';
  assert.equal(store.profiles.candidatePreview(retained), null); assert.equal(store.profiles.candidatePreview()?.age, 36);
});

test('asserted adult and consent booleans without the underlying facts cannot grant a pair projection', () => {
  const profiles = createFixtureProfileStore(options);
  profiles.synchronize({ ownerId: '11111111-1111-4111-8111-111111111111', generation: 1, accountVersion: 1,
    accountState: 'active', sessionState: 'valid', adult: true, consentCurrent: true, sourceRevision: 1, consentRevision: '1' });
  profiles.seedEligible(); assert.equal(profiles.getSnapshot().canDiscover, true);
  assert.equal(profiles.candidatePreview(), null);
});

test('age beyond the closed projection range is denied without clamping or leaking an exception', () => {
  const profiles = createFixtureProfileStore(options);
  profiles.synchronize({ ownerId: '11111111-1111-4111-8111-111111111111', generation: 1, accountVersion: 1,
    accountState: 'active', sessionState: 'valid', adult: true, consentCurrent: true, sourceRevision: 1, consentRevision: '1',
    birthDate: '0001-01-01', consentState: 'accepted', consentVersion: 'development-consent-1' });
  profiles.seedEligible(); assert.equal(profiles.candidatePreview(), null);
});

for (const revokeAt of [1, 2]) {
  test(`projection source read ${revokeAt} cannot publish a candidate revoked synchronously by that dependency`, () => {
    const subject = eligible(), retained = subject.profiles.candidateContext();
    let reads = 0;
    subject.profiles.bindMedia(() => {
      const collection = subject.media.approvedCollection();
      if (++reads === revokeAt) subject.profiles.developmentPairChange('block_viewer');
      return collection;
    }, () => subject.media.restrictApproved());
    assert.equal(subject.profiles.candidatePreview(retained), null);
    assert.equal(subject.profiles.candidatePreview(), null);
  });
}

test('revocation from the final injected clock read denies the captured projection', () => {
  let armed = false, calls = 0;
  const profiles = createFixtureProfileStore({ ...options, clock: () => {
    if (armed && ++calls === 4) profiles.synchronize({ ...authority, consentCurrent: false, consentState: 'withdrawn', consentRevision: '2' });
    return new Date('2026-09-23T12:00:00Z');
  } });
  const authority: ProfileAuthority = { ownerId: '11111111-1111-4111-8111-111111111111', generation: 1,
    accountVersion: 1, accountState: 'active', sessionState: 'valid', adult: true, consentCurrent: true,
    sourceRevision: 1, consentRevision: '1', birthDate: '1990-06-15', consentState: 'accepted', consentVersion: 'development-consent-1' };
  profiles.synchronize(authority); profiles.seedEligible();
  const retained = profiles.candidateContext(); armed = true;
  assert.equal(profiles.candidatePreview(retained), null);
  assert.equal(calls, 4, 'The callback revoked during the final read, after projection construction.');
});

test('missing delivery evidence from a combined media source never receives standalone fallback', () => {
  const { profiles, media } = eligible();
  profiles.bindMedia(() => ({ ...media.approvedCollection(), items: media.approvedCollection().items.map(item => ({ ...item, approved_delivery_ref: null })) }), () => {});
  assert.equal(profiles.candidatePreview(), null);
});


test('a nonapproved lifecycle with a retained delivery reference cannot become approved pair media', () => {
  const { profiles, media } = eligible();
  profiles.bindMedia(() => ({ ...media.approvedCollection(), items: media.approvedCollection().items.map(item => ({ ...item, state: 'rejected' as const })) }), () => {});
  assert.equal(profiles.candidatePreview(), null);
});


test('a changing media dependency cannot inject an uncaptured delivery reference into the projection', () => {
  const { profiles, media } = eligible();
  const retained = profiles.candidateContext(); let reads = 0;
  profiles.bindMedia(() => ({ ...media.approvedCollection(), items: media.approvedCollection().items.map(item => ({ ...item,
    approved_delivery_ref: ++reads === 2 ? 'fixture:uncaptured' : item.approved_delivery_ref })) }), () => {});
  assert.equal(profiles.candidatePreview(retained), null);
});


test('a clock that changes only during a projection read cannot supply an unbound candidate age', () => {
  let armed = false, calls = 0;
  const profiles = createFixtureProfileStore({ ...options, clock: () => new Date(armed && ++calls === 3 ? '2027-09-23T12:00:00Z' : '2026-09-23T12:00:00Z') });
  profiles.synchronize({ ownerId: '11111111-1111-4111-8111-111111111111', generation: 1, accountVersion: 1,
    accountState: 'active', sessionState: 'valid', adult: true, consentCurrent: true, sourceRevision: 1, consentRevision: '1',
    birthDate: '1990-06-15', consentState: 'accepted', consentVersion: 'development-consent-1' });
  profiles.seedEligible(); const retained = profiles.candidateContext(); armed = true;
  assert.equal(profiles.candidatePreview(retained), null, 'The altered read is evaluated and invalidates the captured epoch.');
});


test('mixed lifecycle facts never project a nonapproved delivery reference', () => {
  const { profiles, media } = eligible();
  const accepted = media.approvedCollection();
  // Distinct second fictional asset also belongs to the profile source; only the current approved one may be projected.
  const mixed = { ...accepted, version: accepted.version + 1, items: [...accepted.items,
    { ...accepted.items[0]!, asset_id: 'dddddddd-dddd-4ddd-8ddd-dddddddddddd', state: 'quarantined' as const, approved_delivery_ref: 'fixture:private-quarantined' }] };
  profiles.bindMedia(() => mixed, () => {});
  profiles.synchronizeMedia({ ...mixed, items: mixed.items.map(item => ({ ...item, state: 'approved' as const })) });
  const candidate = profiles.candidatePreview();
  assert.ok(candidate);
  assert.deepEqual(candidate.media_delivery_refs, accepted.items.map(item => item.approved_delivery_ref));
  assert.equal(JSON.stringify(candidate).includes('fixture:private-quarantined'), false);
});
