import assert from 'node:assert/strict';
import test from 'node:test';
import { createFixtureOnboardingStore } from '../onboarding/store.ts';
import { createFixtureProfileStore, ProfileStore, type CandidateViewContext } from './store.ts';
import { createProfileAdapter } from './fixture-adapter.ts';
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

const readyAuthority: ProfileAuthority = { ownerId: '11111111-1111-4111-8111-111111111111', generation: 1,
  accountVersion: 1, accountState: 'active', sessionState: 'valid', adult: true, consentCurrent: true,
  sourceRevision: 1, consentRevision: '1', birthDate: '1990-06-15', consentState: 'accepted', consentVersion: 'development-consent-1' };
/** Names the existing preview phases without changing the production source or clock ports. */
function publicationClock() {
  const phases = ['opening_context', 'opening_pair', 'closing_context', 'publication'] as const;
  let pending: readonly string[] = [], onPublication = () => {}, observed: string[] = [];
  return {
    clock: () => {
      const phase = pending[0]; pending = pending.slice(1);
      if (phase) observed.push(phase);
      if (phase === 'publication') onPublication();
      return new Date('2026-09-23T12:00:00Z');
    },
    arm(callback: () => void) { pending = phases; observed = []; onPublication = callback; },
    assertBound() { assert.deepEqual(observed, phases); },
  };
}

for (const change of ['policy', 'media', 'profile', 'preferences'] as const) {
  test(`final clock ${change} source write cannot publish the earlier mobile projection`, () => {
    const source = createProfileAdapter(options), timing = publicationClock();
    const profiles = new ProfileStore(source, { ...options, clock: timing.clock });
    profiles.synchronize(readyAuthority); profiles.seedEligible();
    const retained = profiles.candidateContext();
    assert.ok(profiles.candidatePreview(retained), 'The unchanged source is a positive control.');
    timing.arm(() => source.developmentChange(change));
    assert.equal(profiles.candidatePreview(retained), null);
    timing.assertBound();
    assert.equal(profiles.candidatePreview(), null, 'Changed source records require adoption or restored eligibility.');
  });
}

for (const restore of [false, true]) {
  test(`same-value source ${restore ? 'restoration' : 'replacement'} at publication invalidates the old context`, () => {
    const source = createProfileAdapter(options), timing = publicationClock();
    const profiles = new ProfileStore(source, { ...options, clock: timing.clock });
    profiles.synchronize(readyAuthority); profiles.seedEligible();
    const retained = profiles.candidateContext();
    const original = source.inspect();
    timing.arm(() => { if (restore) source.developmentChange('policy'); source.seedEligible(); });
    assert.equal(profiles.candidatePreview(retained), null); timing.assertBound();
    assert.deepEqual(source.inspect(), original, 'Visible source values can return exactly to their starting values.');
    assert.equal(profiles.candidatePreview(retained), null);
    assert.ok(profiles.candidatePreview(), 'A fresh context can use restored facts.');
  });
}

test('a final clock media binding replacement and restoration cannot revive captured projection evidence', () => {
  const subject = eligible(), timing = publicationClock();
  const profiles = createFixtureProfileStore({ ...options, clock: timing.clock });
  profiles.synchronize(readyAuthority);
  const source = () => subject.media.approvedCollection();
  profiles.bindMedia(source, () => {}); profiles.seedEligible();
  const retained = profiles.candidateContext();
  assert.ok(profiles.candidatePreview(retained));
  timing.arm(() => { profiles.bindMedia(() => ({ ...source(), items: [] }), () => {}); profiles.bindMedia(source, () => {}); });
  assert.equal(profiles.candidatePreview(retained), null); timing.assertBound();
  assert.equal(profiles.candidatePreview(retained), null); assert.ok(profiles.candidatePreview());
});

test('the real media writer synchronously invalidates profile publication from the final clock', () => {
  const timing = publicationClock();
  const subject = createFixtureOnboardingStore({ ...options, clock: timing.clock });
  subject.scenario('eligible');
  const retained = subject.profiles.candidateContext();
  assert.ok(subject.profiles.candidatePreview(retained));
  timing.arm(() => subject.media.restrictApproved());
  assert.equal(subject.profiles.candidatePreview(retained), null); timing.assertBound();
  assert.equal(subject.profiles.candidatePreview(), null);
});

test('same-value real media reset invalidates publication and every retained context', () => {
  const timing = publicationClock();
  const subject = createFixtureOnboardingStore({ ...options, clock: timing.clock });
  subject.scenario('eligible');
  const retained = subject.profiles.candidateContext(), original = subject.media.approvedCollection();
  assert.ok(subject.profiles.candidatePreview(retained));
  timing.arm(() => subject.media.seedEligible());
  assert.equal(subject.profiles.candidatePreview(retained), null); timing.assertBound();
  assert.deepEqual(subject.media.approvedCollection(), original);
  assert.equal(subject.profiles.candidatePreview(retained), null);
  assert.ok(subject.profiles.candidatePreview());
});

test('candidate preconditions reject accessors and serialization substitution without invoking them', () => {
  let reads = 0, callbackCalls = 0;
  const profiles = createFixtureProfileStore({ ...options, clock: () => { reads += 1; return new Date('2026-09-23T12:00:00Z'); } });
  profiles.synchronize(readyAuthority); profiles.seedEligible();
  const current = profiles.candidateContext()!;
  const stale = { ...current, version: { ...current.version, candidate_snapshot_version: 'obsolete' } };
  const replace = () => { callbackCalls += 1; return current; };
  const malformed: unknown[] = [false, 0, '', [], {}, { ...stale, toJSON: replace },
    Object.defineProperty({ ...current }, 'version', { enumerable: true, get: replace }),
    { ...stale, version: { ...stale.version, toJSON: () => { callbackCalls += 1; return current.version; } } },
    { ...current, version: Object.defineProperty({ ...current.version }, 'policy_version', { enumerable: true,
      get: () => { callbackCalls += 1; return current.version.policy_version; } }) }];
  const initialReads = reads;
  for (const value of malformed) {
    assert.throws(() => profiles.candidatePreview(value as CandidateViewContext), TypeError);
    assert.equal(reads, initialReads, 'Malformed input is rejected before clock/source reads.');
  }
  assert.equal(callbackCalls, 0);
  assert.equal(profiles.candidatePreview(stale), null);
  assert.ok(profiles.candidatePreview(current));
  const inherited = Object.assign(Object.create({ toJSON: replace }), current) as CandidateViewContext;
  assert.ok(profiles.candidatePreview(inherited)); assert.equal(callbackCalls, 0);
});

test('an unregistered fixture adapter cannot assert a current publication revision', () => {
  const actual = createProfileAdapter(options);
  const profiles = new ProfileStore({ ...actual }, options);
  profiles.synchronize(readyAuthority); profiles.seedEligible();
  assert.equal(profiles.getSnapshot().canDiscover, true);
  assert.equal(profiles.candidateContext(), null); assert.equal(profiles.candidatePreview(), null);
});
