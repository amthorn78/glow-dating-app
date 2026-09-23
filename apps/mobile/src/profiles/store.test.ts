import assert from 'node:assert/strict';
import test from 'node:test';
import type { OwnProfile, PreferencesIntent, ProfileIntent } from '../contracts/generated/gapp-api-v1.ts';
import { createProfileAdapter, type ProfileAdapter } from './fixture-adapter.ts';
import { PROFILE_IDS, type ProfileAuthority } from './policy.ts';
import { createFixtureProfileStore, ProfileStore } from './store.ts';
import { createFixtureOnboardingStore, FIXTURE_PASSWORD } from '../onboarding/store.ts';

const options = { isDevelopment: true, mode: 'fixture' };
const authority: ProfileAuthority = { ownerId: '11111111-1111-4111-8111-111111111111',
  generation: 1, accountVersion: 1, accountState: 'active', sessionState: 'valid', adult: true,
  consentCurrent: true, consentRevision: '1:development-consent-1', sourceRevision: 0 };
const selected = [{ dimension: 'demo_connection', accepted_option_ids: ['demo_a'] }];
function store(port?: ProfileAdapter) {
  const result = port ? new ProfileStore(port, options) : createFixtureProfileStore(options);
  result.synchronize(authority);
  return result;
}
function edit(subject: ProfileStore, display_name = 'Alex', summary = 'A fictional biography.') {
  subject.editProfileDraft({ display_name, summary }, subject.getSnapshot().profileDraftRevision);
}
async function save(subject: ProfileStore) { await subject.saveProfile(subject.getSnapshot().profileDraftRevision); }
function delayOne() {
  let held = false;
  let release = () => {};
  return { pause: () => {
    if (!held) return Promise.resolve();
    held = false;
    return new Promise<void>(resolve => { release = resolve; });
  }, hold() { held = true; }, release() { release(); } };
}

test('ordinary profile and preference saves remain incomplete without fictional external evidence', async () => {
  const subject = store();
  edit(subject, 'Alex', '');
  await save(subject);
  assert.equal(subject.getSnapshot().profile?.summary, '');
  assert.equal(subject.getSnapshot().profile?.visibility, 'incomplete');
  subject.editPreferencesDraft(selected, subject.getSnapshot().preferencesDraftRevision);
  await subject.savePreferences(subject.getSnapshot().preferencesDraftRevision);
  edit(subject);
  await save(subject);
  assert.equal(subject.getSnapshot().error, null);
  assert.equal(subject.getSnapshot().profile?.visibility, 'incomplete');
  assert.equal(subject.getSnapshot().canDiscover, false);
  assert.equal(subject.candidatePreview(), null);
  for (const missing of ['Approved photos', 'A resolved chart', 'Profile review', 'Current reciprocal preference evidence']) {
    assert.ok(subject.getSnapshot().requirements.includes(missing));
  }
});

test('same-session navigation retains deliberate drafts; cancel restores accepted values independently', async () => {
  const subject = store();
  edit(subject);
  await save(subject);
  const accepted = subject.getSnapshot().profile;
  edit(subject, 'Uncommitted name', 'Uncommitted biography');
  subject.editPreferencesDraft(selected, subject.getSnapshot().preferencesDraftRevision);
  const removeListener = subject.subscribe(() => {});
  removeListener();
  subject.subscribe(() => {});
  await subject.reload();
  assert.equal(subject.getSnapshot().profileDraft.summary, 'Uncommitted biography');
  assert.deepEqual(subject.getSnapshot().preferencesDraft, selected);
  subject.cancelProfileEdit(subject.getSnapshot().profileDraftRevision);
  assert.deepEqual(subject.getSnapshot().profile, accepted);
  assert.equal(subject.getSnapshot().profileDraft.summary, accepted?.summary);
  assert.deepEqual(subject.getSnapshot().preferencesDraft, selected);
  subject.cancelPreferencesEdit(subject.getSnapshot().preferencesDraftRevision);
  assert.deepEqual(subject.getSnapshot().preferencesDraft, []);
});

test('failed retries retain the same command identity until content or expected version changes', async () => {
  const port = createProfileAdapter(options);
  const requests: ProfileIntent[] = [];
  const subject = store({ ...port, saveProfile: (context, intent, outcome) => {
    requests.push(structuredClone(intent));
    return port.saveProfile(context, intent, outcome);
  } });
  edit(subject);
  await subject.saveProfile(subject.getSnapshot().profileDraftRevision, 'error');
  assert.equal(subject.getSnapshot().profile, null);
  assert.equal(subject.getSnapshot().profileDraft.summary, 'A fictional biography.');
  await save(subject);
  assert.deepEqual(requests[0], requests[1]);
  assert.equal(subject.getSnapshot().profile?.version, 1);
  edit(subject, 'Alex', 'A revised biography');
  await save(subject);
  assert.notEqual(requests[1]!.meta.idempotency_key, requests[2]!.meta.idempotency_key);
  assert.equal(requests[2]!.meta.expected_version, 1);
  assert.equal(subject.getSnapshot().profile?.version, 2);
});

test('preference retry preserves expected version, policy and idempotency metadata', async () => {
  const port = createProfileAdapter(options);
  const requests: PreferencesIntent[] = [];
  const subject = store({ ...port, savePreferences: (context, intent, outcome) => {
    requests.push(structuredClone(intent));
    return port.savePreferences(context, intent, outcome);
  } });
  subject.editPreferencesDraft(selected, subject.getSnapshot().preferencesDraftRevision);
  await subject.savePreferences(subject.getSnapshot().preferencesDraftRevision, 'error');
  await subject.savePreferences(subject.getSnapshot().preferencesDraftRevision);
  assert.deepEqual(requests[0], requests[1]);
  assert.equal(requests[1]!.meta.expected_version, 0);
  assert.equal(subject.getSnapshot().preferences?.version, 1);
});

test('source changes refresh untouched fields while retained deliberate edits require current revisions', async () => {
  const subject = store();
  edit(subject);
  await save(subject);
  edit(subject, 'Alex', 'My unsaved biography');
  const oldRevision = subject.getSnapshot().profileDraftRevision;
  subject.developmentChange('profile');
  assert.equal(subject.getSnapshot().profileDraft.display_name, 'Alex current');
  assert.equal(subject.getSnapshot().profileDraft.summary, 'My unsaved biography');
  assert.equal(subject.getSnapshot().profile?.summary, 'A newer fictional biography.');
  subject.editProfileDraft({ display_name: 'Obsolete callback' }, oldRevision);
  await subject.saveProfile(oldRevision);
  assert.equal(subject.getSnapshot().profileDraft.display_name, 'Alex current');
  assert.equal(subject.getSnapshot().profile?.version, 2);
  await save(subject);
  assert.equal(subject.getSnapshot().profile?.summary, 'My unsaved biography');
  assert.equal(subject.getSnapshot().profile?.version, 3);
});

test('version-conflict reload preserves the draft without applying a stale write', async () => {
  const port = createProfileAdapter(options);
  const subject = store(port);
  edit(subject);
  await save(subject);
  edit(subject, 'Alex', 'Preserve this correction');
  port.developmentChange('profile');
  await save(subject);
  assert.match(subject.getSnapshot().error!, /changed/);
  assert.equal(port.inspect().profile?.summary, 'A newer fictional biography.');
  await subject.reload();
  assert.equal(subject.getSnapshot().profileDraft.display_name, 'Alex current');
  assert.equal(subject.getSnapshot().profileDraft.summary, 'Preserve this correction');
  await save(subject);
  assert.equal(subject.getSnapshot().profile?.summary, 'Preserve this correction');
});

test('schema-invalid and mismatched profile responses are rejected before acknowledgment and later reload', async () => {
  for (const mutate of [
    (value: OwnProfile) => ({ ...value, profile_id: PROFILE_IDS.sam }),
    (value: OwnProfile) => ({ ...value, version: value.version + 10 }),
    (value: OwnProfile) => ({ ...value, summary: 'Response from another request' }),
    (value: OwnProfile) => ({ ...value, private_email: 'alex@example.invalid' }),
  ]) {
    const port = createProfileAdapter(options);
    const subject = store({ ...port, saveProfile: async (context, intent, outcome) => mutate(await port.saveProfile(context, intent, outcome)) });
    edit(subject);
    await save(subject);
    assert.ok(subject.getSnapshot().error);
    assert.equal(subject.getSnapshot().profile, null);
    assert.equal(port.inspect().profile, null);
    await subject.reload();
    assert.equal(subject.getSnapshot().profile, null);
    assert.equal(subject.getSnapshot().profileDraft.summary, 'A fictional biography.');
  }
});

test('malformed preference and pause replies leave no hidden accepted mutation', async () => {
  const port = createProfileAdapter(options);
  const subject = store(port);
  subject.seedEligible();
  const before = port.inspect();
  subject.editPreferencesDraft([{ dimension: 'demo_connection', accepted_option_ids: ['demo_b'] }], subject.getSnapshot().preferencesDraftRevision);
  await subject.savePreferences(subject.getSnapshot().preferencesDraftRevision, 'malformed');
  assert.deepEqual(port.inspect(), before);
  await subject.reload();
  assert.deepEqual(subject.getSnapshot().preferences, before.preferences);
  await subject.setVisibility('pause', 'malformed');
  assert.equal(port.inspect().profile?.visibility, 'visible');
  assert.equal(subject.getSnapshot().canDiscover, false);
  await subject.reload();
  assert.equal(subject.getSnapshot().canDiscover, false);
  assert.equal(subject.candidatePreview(), null);
  await subject.setVisibility('pause');
  assert.equal(subject.getSnapshot().profile?.visibility, 'paused');
});

test('duplicate saves are bounded and a later deliberate edit survives the first save completion', async () => {
  const latch = delayOne();
  const port = createProfileAdapter({ ...options, pause: latch.pause });
  let calls = 0;
  const subject = store({ ...port, saveProfile: (...args) => { calls += 1; return port.saveProfile(...args); } });
  edit(subject);
  latch.hold();
  const pending = subject.saveProfile(subject.getSnapshot().profileDraftRevision);
  await subject.saveProfile(subject.getSnapshot().profileDraftRevision);
  edit(subject, 'Alex', 'A newer unsaved edit');
  assert.equal(subject.getSnapshot().busy, true);
  latch.release();
  await pending;
  assert.equal(calls, 1);
  assert.equal(subject.getSnapshot().profile?.summary, 'A fictional biography.');
  assert.equal(subject.getSnapshot().profileDraft.summary, 'A newer unsaved edit');
});

test('cancel during an outstanding save revokes the response and prevents a later read reviving it', async () => {
  const latch = delayOne();
  const port = createProfileAdapter({ ...options, pause: latch.pause });
  const subject = store(port);
  edit(subject);
  latch.hold();
  const pending = subject.saveProfile(subject.getSnapshot().profileDraftRevision);
  subject.cancelProfileEdit(subject.getSnapshot().profileDraftRevision);
  latch.release();
  await pending;
  await subject.reload();
  assert.equal(subject.getSnapshot().profile, null);
  assert.equal(port.inspect().profile, null);
  assert.deepEqual(subject.getSnapshot().profileDraft, { display_name: '', summary: '' });
});

for (const [name, next] of [
  ['logout', { ...authority, ownerId: null, generation: 2, accountState: 'none', sessionState: 'none' }],
  ['account switch', { ...authority, ownerId: '22222222-2222-4222-8222-222222222222', generation: 2 }],
  ['session expiry', { ...authority, sessionState: 'expired' }],
  ['restriction', { ...authority, accountState: 'suspended' }],
  ['deletion', { ...authority, accountState: 'deletion_pending' }],
] as const) {
  test(`${name} clears private drafts and rejects delayed profile completion and old callbacks`, async () => {
    const latch = delayOne();
    const port = createProfileAdapter({ ...options, pause: latch.pause });
    const subject = store(port);
    edit(subject, 'Private fictional name', 'Private fictional biography');
    subject.editPreferencesDraft(selected, subject.getSnapshot().preferencesDraftRevision);
    const revision = subject.getSnapshot().profileDraftRevision;
    latch.hold();
    const pending = subject.saveProfile(revision);
    subject.synchronize(next);
    subject.editProfileDraft({ summary: 'Stale callback' }, revision);
    latch.release();
    await pending;
    assert.equal(subject.getSnapshot().profile, null);
    assert.deepEqual(subject.getSnapshot().profileDraft, { display_name: '', summary: '' });
    assert.deepEqual(subject.getSnapshot().preferencesDraft, []);
    assert.equal(subject.getSnapshot().busy, false);
    assert.equal(subject.candidatePreview(), null);
    assert.equal(JSON.stringify(subject.getSnapshot()).includes('Private fictional'), false);
  });
}

test('pause immediately revokes retained candidate context and cancels a delayed profile edit', async () => {
  const latch = delayOne();
  const subject = store(createProfileAdapter({ ...options, pause: latch.pause }));
  subject.seedEligible();
  const context = subject.candidateContext();
  assert.ok(subject.candidatePreview(context));
  edit(subject, 'Alex', 'Delayed profile edit');
  latch.hold();
  const pending = subject.saveProfile(subject.getSnapshot().profileDraftRevision);
  const paused = subject.setVisibility('pause');
  assert.equal(subject.getSnapshot().canDiscover, false);
  assert.equal(subject.candidatePreview(context), null);
  await paused;
  latch.release();
  await pending;
  assert.equal(subject.getSnapshot().profile?.visibility, 'paused');
  assert.notEqual(subject.getSnapshot().profile?.summary, 'Delayed profile edit');
  await subject.setVisibility('resume');
  assert.equal(subject.getSnapshot().profile?.visibility, 'visible');
  assert.ok(subject.candidatePreview());
  assert.equal(subject.candidatePreview(context), null, 'resuming cannot authorize a historical candidate context');
});

test('pause during delayed resume keeps permission revoked even when the old resume completes', async () => {
  const latch = delayOne();
  const subject = store(createProfileAdapter({ ...options, pause: latch.pause }));
  subject.seedEligible();
  await subject.setVisibility('pause');
  latch.hold();
  const resume = subject.setVisibility('resume');
  await subject.setVisibility('pause');
  latch.release();
  await resume;
  assert.equal(subject.getSnapshot().profile?.visibility, 'paused');
  assert.equal(subject.getSnapshot().canDiscover, false);
  assert.equal(subject.candidatePreview(), null);
});

test('consent and adult eligibility loss revoke visible projections and deny resume', async () => {
  for (const next of [{ ...authority, consentCurrent: false }, { ...authority, adult: false }]) {
    const subject = store();
    subject.seedEligible();
    const context = subject.candidateContext();
    await subject.setVisibility('pause');
    subject.synchronize(next);
    await subject.setVisibility('resume');
    assert.ok(subject.getSnapshot().error);
    assert.equal(subject.getSnapshot().profile?.visibility, 'paused');
    assert.equal(subject.getSnapshot().canDiscover, false);
    assert.equal(subject.candidatePreview(context), null);
  }
});

test('source policy, preferences, media and reciprocal evidence changes invalidate retained candidates', () => {
  for (const change of ['preferences', 'policy', 'media', 'reciprocal'] as const) {
    const subject = store();
    subject.seedEligible();
    const context = subject.candidateContext();
    assert.ok(subject.candidatePreview(context));
    subject.developmentChange(change);
    assert.equal(subject.getSnapshot().profile?.visibility, change === 'preferences' ? 'incomplete' : 'visible');
    assert.equal(subject.getSnapshot().canDiscover, false);
    assert.equal(subject.candidatePreview(context), null);
    assert.equal(subject.candidatePreview(), null);
  }
});

test('owner-boundary subscribers never observe prior-owner private drafts after synchronization', async () => {
  const subject = store();
  edit(subject, 'Private previous owner', 'Private previous biography');
  await save(subject);
  const observed: ReturnType<ProfileStore['getSnapshot']>[] = [];
  subject.subscribe(() => { observed.push(subject.getSnapshot()); });
  subject.synchronize({ ...authority, ownerId: '22222222-2222-4222-8222-222222222222', generation: 2 });
  assert.ok(observed.length > 0);
  for (const value of observed) {
    assert.equal(value.ownerKey, '22222222-2222-4222-8222-222222222222:2');
    assert.equal(value.profile, null);
    assert.deepEqual(value.profileDraft, { display_name: '', summary: '' });
    assert.equal(JSON.stringify(value).includes('Private previous'), false);
  }
});

test('onboarding account switches publish no cross-owner profile data and profile changes invalidate checkpoints', async () => {
  const onboarding = createFixtureOnboardingStore(options);
  onboarding.scenario('eligible');
  const checkpoint = onboarding.saveCheckpoint();
  assert.ok(checkpoint);
  edit(onboarding.profiles, 'Private Alex', 'Private Alex biography');
  assert.equal(onboarding.getSnapshot().checkpointAvailable, false);
  assert.equal(onboarding.restoreCheckpoint(checkpoint), false);
  await save(onboarding.profiles);
  const observed: { account: string | null; owner: string; serialized: string }[] = [];
  const observe = () => observed.push({ account: onboarding.getSnapshot().account?.account_id ?? null,
    owner: onboarding.profiles.getSnapshot().ownerKey, serialized: JSON.stringify(onboarding.profiles.getSnapshot()) });
  onboarding.subscribe(observe);
  onboarding.profiles.subscribe(observe);
  await onboarding.account('sign_in', 'sam@example.invalid', FIXTURE_PASSWORD);
  assert.ok(observed.length > 0);
  for (const value of observed) assert.equal(value.serialized.includes('Private Alex'), false);
  assert.equal(onboarding.profiles.getSnapshot().profile, null);
});

test('ordinary onboarding text completion preserves unknown birth time and never opens discovery', async () => {
  const onboarding = createFixtureOnboardingStore(options);
  await onboarding.account('register', 'alex@example.invalid', FIXTURE_PASSWORD);
  await onboarding.verify();
  onboarding.setAdultDate('1990-06-15');
  onboarding.setConsent(true);
  await onboarding.saveBirth({ birth_date: '1990-06-15', local_time: null, time_precision: 'unknown',
    place_label: 'Fictional Harbor', timezone_name: null, timezone_provenance: null });
  edit(onboarding.profiles);
  await save(onboarding.profiles);
  onboarding.profiles.editPreferencesDraft(selected, onboarding.profiles.getSnapshot().preferencesDraftRevision);
  await onboarding.profiles.savePreferences(onboarding.profiles.getSnapshot().preferencesDraftRevision);
  assert.equal(onboarding.getSnapshot().stage, 'remaining');
  assert.equal(onboarding.getSnapshot().birth?.input.local_time, null);
  assert.equal(onboarding.getSnapshot().birth?.input.timezone_name, null);
  assert.equal(onboarding.getSnapshot().birth?.input.timezone_provenance, null);
  assert.equal(onboarding.profiles.getSnapshot().canDiscover, false);
});

test('unresolved preference policy fails before mutation and cannot grant discoverability', async () => {
  const port = createProfileAdapter(options);
  let calls = 0;
  const subject = store({ ...port, inspect: () => ({ ...port.inspect(), policy: null }),
    savePreferences: (...args) => { calls += 1; return port.savePreferences(...args); } });
  subject.editPreferencesDraft(selected, subject.getSnapshot().preferencesDraftRevision);
  await subject.savePreferences(subject.getSnapshot().preferencesDraftRevision);
  assert.equal(calls, 0);
  assert.equal(subject.getSnapshot().preferences, null);
  assert.match(subject.getSnapshot().error!, /policy/);
  assert.equal(subject.getSnapshot().canDiscover, false);
});

test('current-consent revision changes cancel pending resume and invalidate stale edit callbacks', async () => {
  const latch = delayOne();
  const subject = store(createProfileAdapter({ ...options, pause: latch.pause }));
  subject.seedEligible();
  await subject.setVisibility('pause');
  const revision = subject.getSnapshot().profileDraftRevision;
  latch.hold();
  const pending = subject.setVisibility('resume');
  subject.synchronize({ ...authority, consentRevision: '2:development-consent-1' });
  subject.editProfileDraft({ summary: 'Stale consent callback' }, revision);
  latch.release();
  await pending;
  assert.equal(subject.getSnapshot().profile?.visibility, 'paused');
  assert.notEqual(subject.getSnapshot().profileDraft.summary, 'Stale consent callback');
  assert.equal(subject.getSnapshot().canDiscover, false);
  await subject.setVisibility('resume');
  assert.equal(subject.getSnapshot().profile?.visibility, 'visible');
});

test('candidate projection is a closed allowlist bound to viewer, object, generation and current discovery revision', () => {
  const subject = store();
  assert.equal(subject.candidatePreview(), null);
  subject.seedEligible();
  const context = subject.candidateContext()!;
  const candidate = subject.candidatePreview(context)!;
  assert.deepEqual(Object.keys(candidate).sort(), ['age', 'compatibility', 'display_name', 'media_delivery_refs', 'profile_id', 'summary']);
  assert.deepEqual(candidate.media_delivery_refs, []);
  assert.deepEqual(candidate.compatibility, { status: 'unavailable' });
  for (const wrong of [{ ...context, viewerId: authority.ownerId! }, { ...context, candidateProfileId: PROFILE_IDS.sam },
    { ...context, generation: context.generation + 1 }, { ...context, discoveryRevision: context.discoveryRevision + 1 }]) {
    assert.equal(subject.candidatePreview(wrong), null);
  }
  for (const privateField of ['email', 'birth_date', 'local_time', 'place_label', 'preferences', 'engine_id', 'visibility', 'media_ids', 'policy_version']) {
    assert.equal(Object.hasOwn(candidate, privateField), false);
  }
});

test('public UI snapshots never include adapter policy catalogs or fictional authority evidence', async () => {
  const subject = store();
  const expected = ['ownerKey', 'profile', 'preferences', 'profileDraft', 'preferencesDraft',
    'profileDraftRevision', 'preferencesDraftRevision', 'discoveryRevision', 'policyVersion',
    'busy', 'error', 'message', 'requirements', 'canDiscover'].sort();
  const observed: ReturnType<ProfileStore['getSnapshot']>[] = [subject.getSnapshot()];
  subject.subscribe(() => { observed.push(subject.getSnapshot()); });
  subject.seedEligible();
  edit(subject, 'Alex', 'A changed fictional biography.');
  await save(subject);
  await subject.setVisibility('pause');
  subject.developmentChange('policy');
  await subject.reload();
  for (const value of observed) {
    assert.deepEqual(Object.keys(value).sort(), expected);
    assert.equal(Object.hasOwn(value, 'policy'), false);
    assert.equal(Object.hasOwn(value, 'evidence'), false);
    assert.equal(Object.hasOwn(value, 'fictionalViewer'), false);
  }
});

test('malformed reloads never report success before profile creation or with partial saved records, and keep both drafts for retry', async () => {
  for (const scenario of ['empty', 'preferences-only', 'profile-only', 'profile-and-preferences'] as const) {
    const port = createProfileAdapter(options);
    const subject = store(port);
    if (scenario === 'profile-only' || scenario === 'profile-and-preferences') {
      edit(subject);
      await save(subject);
    }
    if (scenario === 'preferences-only' || scenario === 'profile-and-preferences') {
      subject.editPreferencesDraft(selected, subject.getSnapshot().preferencesDraftRevision);
      await subject.savePreferences(subject.getSnapshot().preferencesDraftRevision);
    }
    edit(subject, 'Unsaved fictional name', 'Keep this draft after an invalid read.');
    subject.editPreferencesDraft([{ dimension: 'demo_connection', accepted_option_ids: ['demo_b'] }], subject.getSnapshot().preferencesDraftRevision);
    const before = subject.getSnapshot(), accepted = port.inspect();
    await subject.reload('malformed');
    const failed = subject.getSnapshot();
    assert.ok(failed.error, scenario);
    assert.equal(failed.message, null, scenario);
    assert.equal(failed.busy, false, scenario);
    assert.deepEqual(failed.profile, before.profile, scenario);
    assert.deepEqual(failed.preferences, before.preferences, scenario);
    assert.deepEqual(failed.profileDraft, before.profileDraft, scenario);
    assert.deepEqual(failed.preferencesDraft, before.preferencesDraft, scenario);
    assert.deepEqual(port.inspect(), accepted, scenario);
    await subject.reload();
    assert.equal(subject.getSnapshot().error, null, scenario);
    assert.equal(subject.getSnapshot().message, 'Current saved values loaded. Review your draft before saving.', scenario);
    assert.deepEqual(subject.getSnapshot().profileDraft, before.profileDraft, scenario);
    assert.deepEqual(subject.getSnapshot().preferencesDraft, before.preferencesDraft, scenario);
  }
});
