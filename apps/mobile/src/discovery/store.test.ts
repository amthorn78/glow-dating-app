import assert from 'node:assert/strict';
import test from 'node:test';
import { createFixtureOnboardingStore } from '../onboarding/store.ts';
import { FIXTURE_PAIR_POLICY } from '../eligibility/facts.ts';
import { DISCOVERY_LIMITS, FixtureDiscoveryAdapter, FixtureDiscoveryTime } from './fixture-adapter.ts';
import { createProfileAdapter } from '../profiles/fixture-adapter.ts';
import { ProfileStore } from '../profiles/store.ts';
import { DiscoveryStore } from './store.ts';
const options = { isDevelopment: true, mode: 'fixture' };
function owner() { const source = createFixtureOnboardingStore(options); source.scenario('eligible'); return source; }
const ids = (page: { items: { profile_id: string }[] }) => page.items.map(item => item.profile_id);
const tick = async () => { await Promise.resolve(); await Promise.resolve(); await Promise.resolve(); };

test('overlapping reads reuse one page/cursor and invoke the bounded provider only once', async () => {
  const waiting: (() => void)[] = [];
  const adapter = new FixtureDiscoveryAdapter(owner().profiles, { ...options, pause: () => new Promise(resolve => waiting.push(resolve)) });
  const reads = Array.from({ length: 40 }, (_, i) => adapter.request('recommended', `r-${i}`, null));
  waiting.splice(0).forEach(resolve => resolve());
  const pages = await Promise.all(reads);
  assert.equal(new Set(pages.map(page => page.next_cursor)).size, 1);
  pages.forEach(page => assert.deepEqual(ids(page), ['profile-jules', 'profile-morgan']));
  assert.equal(adapter.calls.provider, 4); assert.equal(adapter.calls.scans, 14);
});

test('malformed, wrong-mode, expired, stale-session and replaced continuation handles fail closed', async () => {
  const time = new FixtureDiscoveryTime(0), source = owner(), adapter = new FixtureDiscoveryAdapter(source.profiles, { ...options, time });
  const first = await adapter.request('recommended', 'first', null);
  assert.equal((await adapter.request('broader', 'wrong-mode', first.next_cursor)).state, 'reload_required');
  await assert.rejects(adapter.request('recommended', 'malformed', '../private?data'), TypeError);
  assert.equal((await adapter.request('recommended', 'unknown', 'cursor-unknown')).state, 'reload_required');
  const refreshed = await adapter.request('recommended', 'refresh', null, true);
  assert.notEqual(refreshed.queue_id, first.queue_id); assert.equal(adapter.isCurrent(first), false);
  assert.equal((await adapter.request('recommended', 'old-cursor', first.next_cursor)).state, 'reload_required');
  time.set(DISCOVERY_LIMITS.lifetimeMs);
  assert.equal(adapter.isCurrent(refreshed), false);
  assert.equal((await adapter.request('recommended', 'expired', refreshed.next_cursor)).state, 'reload_required');
  const recent = await adapter.request('recommended', 'newer', null, true);
  source.scenario('eligible');
  assert.equal(adapter.isCurrent(recent), false);
  assert.equal((await adapter.request('recommended', 'wrong-session', recent.next_cursor)).state, 'reload_required');
});

test('logout during async pause prevents provider and mapping work', async () => {
  let release = () => {};
  const source = owner(), adapter = new FixtureDiscoveryAdapter(source.profiles, { ...options, pause: () => new Promise(resolve => { release = resolve; }) });
  const pending = adapter.request('recommended', 'pending', null);
  source.logout(); release();
  const page = await pending;
  assert.equal(page.state, 'reload_required'); assert.deepEqual(page.items, []); assert.equal(adapter.calls.provider, 0); assert.equal(adapter.calls.mappings, 0);
});

for (const mutation of ['candidate', 'mapping'] as const) test(`later candidate ${mutation} mutation preserves only unchanged current output and retires continuation`, async () => {
  const adapter = new FixtureDiscoveryAdapter(owner().profiles, { ...options, afterCandidate: id => {
    if (id !== 'discovery-morgan') return;
    const row = adapter.inspect('discovery-jules')!;
    adapter.replace({ ...row, ...(mutation === 'candidate' ? { facts: { ...row.facts!, visibility: 'paused' } }
      : { mapping: { ...row.mapping!, engine_reference: 'changed-fixture-reference' } }) });
  } });
  const page = await adapter.request('recommended', 'later', null);
  assert.equal(page.state, 'partial'); assert.deepEqual(ids(page), ['profile-morgan']); assert.equal(page.next_cursor, null);
  assert.equal(adapter.isCurrent(page), true); assert.equal(adapter.calls.provider, 4);
  assert.equal((await adapter.request('recommended', 'retired', null)).state, 'reload_required');
});

for (const mutation of ['viewer', 'policy', 'media', 'time'] as const) test(`later candidate ${mutation} mutation discards every dependent card`, async () => {
  const source = owner(), time = new FixtureDiscoveryTime(0);
  const adapter = new FixtureDiscoveryAdapter(source.profiles, { ...options, time, afterCandidate: id => {
    if (id !== 'discovery-morgan') return;
    if (mutation === 'viewer') source.logout();
    else if (mutation === 'policy') adapter.setPolicy(FIXTURE_PAIR_POLICY);
    else if (mutation === 'media') source.media.restrictApproved();
    else time.set(300001);
  } });
  const page = await adapter.request('recommended', 'later', null);
  assert.equal(page.state, 'reload_required'); assert.deepEqual(page.items, []); assert.equal(page.next_cursor, null);
  assert.equal(adapter.calls.provider, 4);
});

test('viewer revoked during first projection prevents later candidate mapping/provider reads', async () => {
  const source = owner();
  const adapter = new FixtureDiscoveryAdapter(source.profiles, { ...options, afterCandidate: () => source.logout() });
  const page = await adapter.request('recommended', 'first', null);
  assert.equal(page.state, 'reload_required'); assert.equal(adapter.calls.mappings, 2); assert.equal(adapter.calls.provider, 1);
});

for (const field of ['candidate_id', 'viewer_birth_input_version', 'candidate_engine_reference', 'eligibility_policy_version'] as const) test(`wrong provider ${field} cannot publish`, async () => {
  const adapter = new FixtureDiscoveryAdapter(owner().profiles, { ...options, provider: request => ({ ...request, [field]: 'wrong', state: 'ready' }) });
  const page = await adapter.request('recommended', 'wrong', null);
  assert.equal(page.state, 'partial'); assert.deepEqual(page.items, []);
});

test('same-value participant/media writes, policy restoration and clock return cannot revive pages', async () => {
  let day = '2026-09-23T12:00:00Z';
  const source = createFixtureOnboardingStore({ ...options, clock: () => new Date(day) }); source.scenario('eligible');
  const adapter = new FixtureDiscoveryAdapter(source.profiles, { ...options, clock: () => new Date(day) });
  let page = await adapter.request('recommended', 'start', null);
  adapter.replace(adapter.inspect('discovery-jules')!); assert.equal(adapter.isCurrent(page), false);
  page = await adapter.request('recommended', 'fresh', null, true);
  source.media.seedEligible(); assert.equal(adapter.isCurrent(page), false);
  page = await adapter.request('recommended', 'again', null, true);
  day = '2027-09-23T12:00:00Z'; assert.equal(adapter.isCurrent(page), false);
  day = '2026-09-23T12:00:00Z'; assert.equal(adapter.isCurrent(page), false);
  page = await adapter.request('recommended', 'policy', null, true);
  adapter.setPolicy(null); adapter.setPolicy(FIXTURE_PAIR_POLICY); assert.equal(adapter.isCurrent(page), false);
});

test('final profile-clock callback updates same-day concrete lifetime cell and cannot leak expired page', async () => {
  let armed = false; const time = new FixtureDiscoveryTime(0);
  const source = createFixtureOnboardingStore({ ...options, clock: () => {
    if (armed) time.set(300001); return new Date('2026-09-23T12:00:00Z');
  } }); source.scenario('eligible');
  const adapter = new FixtureDiscoveryAdapter(source.profiles, { ...options, time, afterCandidate: id => { if (id === 'discovery-morgan') armed = true; } });
  const page = await adapter.request('recommended', 'expiry', null);
  assert.equal(page.state, 'reload_required'); assert.equal(page.items.length, 0);
});

test('store preserves both mode positions, finite exhaustion and explicit refresh', async () => {
  const source = owner(), adapter = new FixtureDiscoveryAdapter(source.profiles, options), store = new DiscoveryStore(source.profiles, adapter);
  store.enter('recommended'); await tick(); assert.deepEqual(ids(store.getSnapshot('recommended').page!), ['profile-jules', 'profile-morgan']);
  await store.next(); assert.deepEqual(ids(store.getSnapshot('recommended').page!), ['profile-iris', 'profile-kai']);
  store.enter('broader'); await tick(); assert.deepEqual(ids(store.getSnapshot('broader').page!), ['profile-iris', 'profile-jules']);
  store.enter('recommended'); await tick(); assert.equal(store.getSnapshot('recommended').pageNumber, 2);
  await store.next(); assert.equal(store.getSnapshot('recommended').complete, true); assert.equal(store.getSnapshot('recommended').pageNumber, 3);
  await store.next(); assert.equal(store.getSnapshot('recommended').pageNumber, 3);
  await store.refresh(); assert.equal(store.getSnapshot('recommended').pageNumber, 1); assert.equal(store.getSnapshot('broader').pageNumber, 1);
});

test('switch during page two delay resumes exact cursor and ignores late prior request', async () => {
  const waiting: (() => void)[] = [], source = owner();
  const adapter = new FixtureDiscoveryAdapter(source.profiles, { ...options, pause: () => new Promise(resolve => waiting.push(resolve)) });
  const store = new DiscoveryStore(source.profiles, adapter);
  store.enter('recommended'); waiting.shift()!(); await tick();
  const next = store.next(); store.enter('broader'); waiting.pop()!(); await tick();
  store.enter('recommended'); waiting.pop()!(); await tick();
  assert.deepEqual(ids(store.getSnapshot('recommended').page!), ['profile-iris', 'profile-kai']);
  waiting.shift()!(); await next; assert.equal(store.getSnapshot('recommended').pageNumber, 2);
});

test('refresh race accepts only new queue and hides a later revoked retained page', async () => {
  const waiting: (() => void)[] = [], source = owner();
  const adapter = new FixtureDiscoveryAdapter(source.profiles, { ...options, pause: () => new Promise(resolve => waiting.push(resolve)) });
  const store = new DiscoveryStore(source.profiles, adapter);
  store.enter('recommended'); const refresh = store.refresh(); waiting.pop()!(); await refresh;
  const accepted = store.getSnapshot('recommended').page!;
  waiting.shift()!(); await tick(); assert.equal(store.getSnapshot('recommended').page, accepted);
  adapter.replace(adapter.inspect('discovery-jules')!);
  assert.equal(store.getSnapshot('recommended').status, 'reload_required'); assert.equal(store.getSnapshot('recommended').page, null);
});

test('viewer mapping removal/restoration and birth-reference writes with same mapping version revoke output', async () => {
  const source = owner(); let armed = false;
  const adapter = new FixtureDiscoveryAdapter(source.profiles, { ...options, provider: request => {
    if (armed) adapter.replaceViewerMapping({ ...adapter.inspectViewerMapping()!, birth_input_version: 'changed-input' });
    return { ...request, state: 'ready' };
  } });
  const first = await adapter.request('recommended', 'first', null);
  const original = adapter.inspectViewerMapping(); adapter.replaceViewerMapping(null); adapter.replaceViewerMapping(original);
  assert.equal(adapter.isCurrent(first), false);
  armed = true; const changed = await adapter.request('recommended', 'second', null, true);
  assert.equal(changed.state, 'reload_required'); assert.deepEqual(changed.items, []);
});

for (const field of ['birth_input_version', 'mapping_version'] as const) test(`blank ${field} mapping versions fail before provider work`, async () => {
  const adapter = new FixtureDiscoveryAdapter(owner().profiles, options);
  for (const id of ['discovery-jules', 'discovery-morgan']) {
    const row = adapter.inspect(id)!; adapter.replace({ ...row, mapping: { ...row.mapping!, [field]: '  ' } });
  }
  const result = await adapter.request('recommended', 'blank', null);
  assert.equal(result.state, 'partial'); assert.equal(result.items.length, 0); assert.equal(adapter.calls.provider, 0);
});

test('null acquisition without a source-cell write cannot retain or publish an earlier page', async () => {
  const port = createProfileAdapter(options), profiles = new ProfileStore(port, options);
  profiles.synchronize({ ownerId: '11111111-1111-4111-8111-111111111111', generation: 1, accountVersion: 1,
    accountState: 'active', sessionState: 'valid', adult: true, consentCurrent: true, sourceRevision: 1, consentRevision: '1',
    birthDate: '1990-06-15', consentState: 'accepted', consentVersion: 'development-consent-1' });
  profiles.seedEligible();
  const adapter = new FixtureDiscoveryAdapter(profiles, options), page = await adapter.request('recommended', 'start', null);
  assert.equal(page.items.length, 2); assert.equal(adapter.isCurrent(page), true);
  const inspect = port.inspect; port.inspect = () => ({ ...inspect(), profile: null });
  assert.equal(profiles.captureDiscoveryViewer(), null); assert.equal(adapter.isCurrent(page), false);
  assert.equal((await adapter.request('recommended', 'later', page.next_cursor)).state, 'reload_required');
});

test('one expiry notification removes mounted pages and does not schedule an expired timer loop', async context => {
  context.mock.timers.enable({ apis: ['setTimeout'] });
  const source = owner(), time = new FixtureDiscoveryTime(0);
  const adapter = new FixtureDiscoveryAdapter(source.profiles, { ...options, time }), store = new DiscoveryStore(source.profiles, adapter);
  store.enter('recommended'); await tick(); assert.equal(store.getSnapshot('recommended').page?.items.length, 2);
  let notifications = 0; store.subscribe(() => { notifications += 1; });
  time.set(300001); context.mock.timers.tick(300001);
  assert.equal(notifications, 1); assert.equal(store.getSnapshot('recommended').status, 'reload_required');
  assert.equal(store.getSnapshot('recommended').page, null);
  context.mock.timers.tick(600000); assert.equal(notifications, 1);
});
