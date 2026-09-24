import assert from 'node:assert/strict';
import test from 'node:test';
import { createFixtureOnboardingStore } from '../onboarding/store.ts';
import { FixtureDiscoveryAdapter, FixtureDiscoveryTime } from '../discovery/fixture-adapter.ts';
import { FixtureInteractionAdapter, InteractionFailure } from './fixture-adapter.ts';
const options = { isDevelopment: true, mode: 'fixture' };
function setup() {
  const owner = createFixtureOnboardingStore(options); owner.scenario('eligible');
  const time = new FixtureDiscoveryTime(0), discovery = new FixtureDiscoveryAdapter(owner.profiles, { ...options, time });
  const adapter = new FixtureInteractionAdapter(owner.profiles, discovery);
  return { owner, time, discovery, adapter };
}
async function command(fixture: ReturnType<typeof setup>, action: 'like' | 'pass' = 'like', key = 'interaction-test:1') {
  const page = await fixture.discovery.request('recommended', 'test', null, true);
  return fixture.adapter.prepare(page, 'profile-jules', action, key);
}
function execute(fixture: ReturnType<typeof setup>, prepared: ReturnType<FixtureInteractionAdapter['prepare']>) {
  return fixture.adapter.execute(prepared.session, prepared.intent);
}
test('current composition maps UUIDs, persists private own action and consumes both queues without provider work', async () => {
  const fixture = setup(), prepared = await command(fixture);
  assert.match(prepared.intent.target_profile_id, /^[0-9a-f-]{36}$/);
  const calls = { ...fixture.discovery.calls }, result = execute(fixture, prepared);
  assert.equal(result.receipt.outcome_code, 'liked'); assert.equal(result.current_projection?.kind, 'interaction');
  assert.equal(fixture.adapter.inspect().matches.length, 0); assert.equal(fixture.adapter.inspect().events.length, 0);
  assert.deepEqual(fixture.discovery.calls, calls);
  for (const mode of ['recommended', 'broader'] as const) {
    const page = await fixture.discovery.request(mode, 'fresh', null, true);
    assert.equal(page.items.some(item => item.profile_id === 'profile-jules'), false);
  }
  assert.equal(JSON.stringify(result).includes('birth'), false);
});
test('one canonical reciprocal match in either arrival order, no unilateral projection or extra creation event', async () => {
  for (const first of ['owner', 'other'] as const) {
    const fixture = setup();
    if (first === 'other') fixture.adapter.reciprocal('profile-jules', 'other:1');
    const prepared = await command(fixture); execute(fixture, prepared);
    if (first === 'owner') fixture.adapter.reciprocal('profile-jules', 'other:1');
    const state = fixture.adapter.inspect(); assert.equal(state.actions.length, 2); assert.equal(state.matches.length, 1);
    assert.equal(state.events.filter(event => event.kind === 'match_created').length, 1);
    assert.ok(state.matches[0]!.first < state.matches[0]!.second);
    assert.equal(fixture.adapter.matches()[0]?.state, 'active'); assert.equal(fixture.adapter.matches()[0]?.profile?.display_name, 'Fictional Jules');
    assert.equal(fixture.adapter.contact(state.matches[0]!.id)?.canSend, false);
  }
});
test('immutable receipt replay precedes consumed batch checks; canonical property ordering and conflict', async () => {
  const fixture = setup(), prepared = await command(fixture), first = execute(fixture, prepared);
  const reordered = { action: prepared.intent.action, target_profile_id: prepared.intent.target_profile_id, batch_version: 1, batch_id: prepared.intent.batch_id,
    meta: { idempotency_key: prepared.intent.meta.idempotency_key, expected_version: 0 }, operation: 'interaction' as const };
  const replay = fixture.adapter.execute(prepared.session, reordered);
  assert.deepEqual(replay.receipt, first.receipt); assert.equal(replay.replayed, true); assert.equal(fixture.adapter.inspect().actions.length, 1);
  assert.throws(() => fixture.adapter.execute(prepared.session, { ...prepared.intent, action: 'pass' }), InteractionFailure);
  assert.throws(() => fixture.adapter.execute(prepared.session, { ...prepared.intent, meta: { ...prepared.intent.meta, idempotency_key: 'fresh:key' } }), InteractionFailure);
});
test('block and unmatch permanently revoke contact; replay never returns active match grant', async () => {
  const fixture = setup(); fixture.adapter.reciprocal('profile-jules', 'other:1'); const prepared = await command(fixture);
  const first = execute(fixture, prepared), match = fixture.adapter.inspect().matches[0]!;
  fixture.adapter.block('profile-jules', true, 'block:1'); fixture.adapter.block('profile-jules', false, 'unblock:1');
  assert.equal(fixture.adapter.matches()[0]?.state, 'restricted');
  const replay = execute(fixture, prepared); assert.deepEqual(replay.receipt, first.receipt);
  assert.ok(replay.current_projection?.kind !== 'interaction' || replay.current_projection.match_id === null);
  await fixture.owner.profiles.setVisibility('pause');
  const unmatch = fixture.adapter.unmatchIntent(match.id, 'unmatch:1'); const result = fixture.adapter.execute(unmatch.session, unmatch.intent);
  assert.equal(result.receipt.outcome_code, 'unmatched'); assert.equal(fixture.adapter.matches()[0]?.state, 'unmatched');
  assert.equal(fixture.adapter.inspect().events.filter(event => event.kind === 'block_changed').length, 2);
});
test('same-value source replacements revoke retained match projections and restore cannot rematch', async () => {
  const fixture = setup(); fixture.adapter.reciprocal('profile-jules', 'other:1'); execute(fixture, await command(fixture));
  fixture.discovery.replace(fixture.discovery.inspect('discovery-jules')!);
  assert.equal(fixture.adapter.matches()[0]?.state, 'restricted'); assert.equal(fixture.adapter.matches()[0]?.profile, null);
  fixture.discovery.replace(fixture.discovery.inspect('discovery-jules')!);
  assert.throws(() => fixture.adapter.reciprocal('profile-jules', 'other:2'), InteractionFailure);
});
for (const revoke of ['replace', 'block', 'logout', 'time', 'abort'] as const) test(`precommit ${revoke} leaves no partial command/event/receipt`, async () => {
  const fixture = setup(), prepared = await command(fixture);
  fixture.adapter.setBeforeCommit(() => {
    fixture.adapter.setBeforeCommit(null);
    if (revoke === 'replace') fixture.discovery.replace(fixture.discovery.inspect('discovery-jules')!);
    if (revoke === 'block') fixture.adapter.block('profile-jules', true, 'interleaved:block');
    if (revoke === 'logout') fixture.owner.logout();
    if (revoke === 'time') fixture.time.set(300001);
    if (revoke === 'abort') throw new Error('Controlled abort');
  });
  assert.throws(() => execute(fixture, prepared));
  const state = fixture.adapter.inspect(); assert.equal(state.actions.length, 0); assert.equal(state.matches.length, 0);
  assert.equal(state.receipts.length, revoke === 'block' ? 1 : 0);
  assert.equal(state.events.length, revoke === 'block' ? 1 : 0);
});
test('closed malformed intents and forged sessions cannot write; expired and substituted mappings deny', async () => {
  const fixture = setup(), prepared = await command(fixture);
  assert.throws(() => fixture.adapter.execute({ ...prepared.session }, prepared.intent), InteractionFailure);
  for (const patch of [{ reciprocal: true }, { target_profile_id: 'profile-jules' }, { batch_version: true }, { actor: 'forged' }]) {
    assert.throws(() => fixture.adapter.execute(prepared.session, { ...prepared.intent, ...patch } as typeof prepared.intent), InteractionFailure);
  }
  fixture.time.set(300001); assert.throws(() => execute(fixture, prepared), InteractionFailure);
  assert.equal(fixture.adapter.inspect().actions.length, 0);
});
test('match display excludes pending media and replay discovers time-source revocation before returning a match', async () => {
  const fixture = setup(), row = fixture.discovery.inspect('discovery-jules')!;
  fixture.discovery.replace({ ...row, facts: { ...row.facts!, approved_media: [...row.facts!.approved_media!,
    { ...row.facts!.approved_media![0]!, asset_id: 'private-pending-media', state: 'pending', delivery_ref: 'fixture-approved-private-pending' }] } });
  fixture.adapter.reciprocal('profile-jules', 'other:1'); const prepared = await command(fixture); execute(fixture, prepared);
  assert.deepEqual(fixture.adapter.matches()[0]?.profile?.media_delivery_refs, ['fixture-approved-jules']);
  fixture.time.set(1);
  const replay = execute(fixture, prepared); assert.equal(replay.replayed, true);
  assert.ok(replay.current_projection?.kind !== 'interaction' || replay.current_projection.match_id === null);
  assert.equal(fixture.adapter.matches()[0]?.state, 'restricted');
});
test('a stale unilateral like cannot form a match after source restoration', async () => {
  const fixture = setup(); execute(fixture, await command(fixture));
  fixture.discovery.replace(fixture.discovery.inspect('discovery-jules')!);
  fixture.adapter.reciprocal('profile-jules', 'other:1');
  assert.equal(fixture.adapter.inspect().actions.length, 2); assert.equal(fixture.adapter.inspect().matches.length, 0);
});
test('reverse synthetic participant can unmatch while paused but revoked synthetic session cannot act or replay', async () => {
  const fixture = setup(); fixture.adapter.reciprocal('profile-jules', 'other:1'); execute(fixture, await command(fixture));
  const session = fixture.adapter.developmentSession('profile-jules'), row = fixture.discovery.inspect('discovery-jules')!;
  fixture.discovery.replace({ ...row, facts: { ...row.facts!, visibility: 'paused' } });
  const match = fixture.adapter.inspect().matches[0]!;
  const intent = { operation: 'unmatch' as const, match_id: match.id, meta: { expected_version: match.version, idempotency_key: 'other:unmatch' } };
  assert.equal(fixture.adapter.execute(session, intent).receipt.outcome_code, 'unmatched');
  fixture.discovery.replace({ ...row, facts: { ...row.facts!, account_state: 'deleted', session_state: 'expired' } });
  assert.throws(() => fixture.adapter.execute(session, intent), InteractionFailure);
});
test('duplicate pending submission cannot execute twice during the commit callback', async () => {
  const fixture = setup(), prepared = await command(fixture); let code = '';
  fixture.adapter.setBeforeCommit(() => { try { execute(fixture, prepared); } catch (error) { code = (error as InteractionFailure).code; } });
  execute(fixture, prepared); assert.equal(code, 'pending'); assert.equal(fixture.adapter.inspect().actions.length, 1);
  assert.equal(fixture.adapter.inspect().receipts.length, 1);
});
for (const at of [3, 4]) test(`final match projection clock callback ${at} cannot publish an earlier active projection`, async () => {
  let armed = false, reads = 0;
  const clock = () => { if (armed && ++reads === at) { armed = false; discovery.replace(discovery.inspect('discovery-jules')!); }
    return new Date('2026-09-23T12:00:00Z'); };
  const owner = createFixtureOnboardingStore({ ...options, clock }); owner.scenario('eligible');
  const discovery = new FixtureDiscoveryAdapter(owner.profiles, { ...options, clock });
  const adapter = new FixtureInteractionAdapter(owner.profiles, discovery), fixture = { owner, discovery, adapter, time: new FixtureDiscoveryTime(0) };
  adapter.reciprocal('profile-jules', 'other:1'); execute(fixture, await command(fixture));
  armed = true;
  const views = adapter.matches(); assert.equal(views.some(view => view.state === 'active' || view.profile !== null), false);
  assert.equal(adapter.inspect().matches[0]?.state, 'restricted');
});
for (const safety of ['block', 'unblock', 'unmatch'] as const) test(`unrelated ${safety} preserves a current unilateral like for reciprocal matching`, async () => {
  const fixture = setup();
  if (safety === 'unmatch') {
    fixture.adapter.reciprocal('profile-iris', 'iris:like');
    const page = await fixture.discovery.request('broader', 'iris-page', null, true);
    execute(fixture, fixture.adapter.prepare(page, 'profile-iris', 'like', 'owner:iris-like'));
  }
  execute(fixture, await command(fixture));
  if (safety === 'unmatch') {
    const prior = fixture.adapter.inspect().matches[0]!;
    const unmatch = fixture.adapter.unmatchIntent(prior.id, 'iris:unmatch');
    fixture.adapter.execute(unmatch.session, unmatch.intent);
  } else {
    fixture.adapter.block('profile-iris', true, 'iris:block');
    if (safety === 'unblock') fixture.adapter.block('profile-iris', false, 'iris:unblock');
  }
  fixture.adapter.reciprocal('profile-jules', 'jules:like');
  const active = fixture.adapter.matches().filter(match => match.state === 'active');
  assert.equal(active.length, 1); assert.equal(active[0]?.profile?.profile_id, 'profile-jules');
  assert.equal(fixture.adapter.inspect().events.filter(event => event.kind === 'match_created').length, safety === 'unmatch' ? 2 : 1);
});
for (const blocker of ['owner', 'other'] as const) test(`same-pair ${blocker} block and unblock cannot revive a unilateral like`, async () => {
  const fixture = setup(); execute(fixture, await command(fixture));
  if (blocker === 'owner') {
    fixture.adapter.block('profile-jules', true, 'jules:block'); fixture.adapter.block('profile-jules', false, 'jules:unblock');
  } else {
    const session = fixture.adapter.developmentSession('profile-jules');
    const target = fixture.owner.profiles.getSnapshot().profile!.profile_id;
    fixture.adapter.execute(session, { operation: 'block', target_profile_id: target, action: 'block', meta: { expected_version: 0, idempotency_key: 'other:block' } });
    fixture.adapter.execute(session, { operation: 'block', target_profile_id: target, action: 'unblock', meta: { expected_version: 1, idempotency_key: 'other:unblock' } });
  }
  fixture.adapter.reciprocal('profile-jules', 'jules:like');
  assert.equal(fixture.adapter.inspect().actions.length, 2); assert.equal(fixture.adapter.inspect().matches.length, 0);
  assert.equal(fixture.adapter.inspect().events.filter(event => event.kind === 'match_created').length, 0);
});
test('a repeated tombstoned submitting like cannot match a fresh opposite like', async () => {
  const fixture = setup(); fixture.adapter.reciprocal('profile-jules', 'jules:original');
  fixture.adapter.block('profile-jules', true, 'jules:block'); fixture.adapter.block('profile-jules', false, 'jules:unblock');
  execute(fixture, await command(fixture));
  assert.equal(fixture.adapter.inspect().matches.length, 0);
  fixture.adapter.reciprocal('profile-jules', 'jules:repeat');
  assert.equal(fixture.adapter.inspect().actions.length, 2); assert.equal(fixture.adapter.inspect().matches.length, 0);
  assert.equal(fixture.adapter.inspect().events.filter(event => event.kind === 'match_created').length, 0);
});
test('a repeated submitting like with a stale source cannot match a fresh opposite like', async () => {
  const fixture = setup(); fixture.adapter.reciprocal('profile-jules', 'jules:original');
  fixture.discovery.replace(fixture.discovery.inspect('discovery-jules')!);
  execute(fixture, await command(fixture));
  assert.equal(fixture.adapter.inspect().matches.length, 0);
  fixture.adapter.reciprocal('profile-jules', 'jules:repeat');
  assert.equal(fixture.adapter.inspect().actions.length, 2); assert.equal(fixture.adapter.inspect().matches.length, 0);
  assert.equal(fixture.adapter.inspect().events.filter(event => event.kind === 'match_created').length, 0);
});
