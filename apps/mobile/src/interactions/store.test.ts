import assert from 'node:assert/strict';
import test from 'node:test';
import { createFixtureOnboardingStore } from '../onboarding/store.ts';
import { FixtureDiscoveryAdapter, FixtureDiscoveryTime } from '../discovery/fixture-adapter.ts';
import { DiscoveryStore } from '../discovery/store.ts';
import { FixtureInteractionAdapter } from './fixture-adapter.ts';
import { InteractionStore } from './store.ts';
const options = { isDevelopment: true, mode: 'fixture' };
const tick = async () => { for (let i = 0; i < 5; i++) await Promise.resolve(); };
async function setup(time?: FixtureDiscoveryTime) {
  const owner = createFixtureOnboardingStore(options); owner.scenario('eligible');
  const discovery = new DiscoveryStore(owner.profiles, new FixtureDiscoveryAdapter(owner.profiles, { ...options, time }));
  const adapter = new FixtureInteractionAdapter(owner.profiles, discovery.adapter), store = new InteractionStore(owner.profiles, discovery, adapter);
  discovery.enter('recommended'); await tick(); return { owner, discovery, adapter, store };
}
test('own action pending is distinct from committed; both modes require authoritative consumed reload', async () => {
  const { store, adapter, discovery } = await setup(); store.setScenario('delayed');
  const pending = store.submit('recommended', 'profile-jules', 'like');
  assert.equal(store.getSnapshot().status, 'pending'); assert.equal(store.getSnapshot().message, null);
  await store.submit('recommended', 'profile-jules', 'like'); store.releaseDelayed(); await pending;
  assert.equal(store.getSnapshot().message, 'Like saved.'); assert.equal(adapter.inspect().actions.length, 1);
  assert.equal(discovery.getSnapshot('recommended').status, 'reload_required');
  await discovery.refresh(); assert.equal(discovery.getSnapshot('recommended').page?.items.some(item => item.profile_id === 'profile-jules'), false);
});
for (const scenario of ['offline', 'lost_response'] as const) test(`${scenario} keeps the same intent/key; retry reconciles one committed action`, async () => {
  const { store, adapter, discovery } = await setup(); store.setScenario(scenario);
  await store.submit('recommended', 'profile-jules', 'pass');
  assert.equal(store.getSnapshot().canRetry, true); assert.equal(adapter.inspect().actions.length, scenario === 'lost_response' ? 1 : 0);
  store.cancelPending(); // Route cleanup of an already-finished failure preserves its retry identity.
  store.setScenario('normal'); await store.retry();
  assert.equal(store.getSnapshot().status, 'committed'); assert.equal(adapter.inspect().actions.length, 1); assert.equal(adapter.inspect().receipts.length, 1);
  await discovery.refresh(); assert.equal(store.canAct('recommended', 'profile-jules'), false);
});
for (const cancel of ['navigation', 'account', 'mode', 'source'] as const) test(`delayed ${cancel} cannot adopt or duplicate an obsolete command`, async () => {
  const { store, adapter, owner, discovery } = await setup(); store.setScenario('delayed');
  const pending = store.submit('recommended', 'profile-jules', 'like');
  if (cancel === 'navigation') store.cancelPending();
  if (cancel === 'account') owner.scenario('eligible');
  if (cancel === 'mode') { store.cancelPending(); discovery.enter('broader'); }
  if (cancel === 'source') discovery.adapter.replace(discovery.adapter.inspect('discovery-jules')!);
  store.releaseDelayed(); await pending;
  assert.equal(adapter.inspect().actions.length, 0); assert.notEqual(store.getSnapshot().message, 'Like saved.');
});
test('mutual match feedback and stored projections revoke after pause; unmatch remains available', async () => {
  const { store, owner, adapter } = await setup(); store.developmentReciprocal('profile-jules');
  await store.submit('recommended', 'profile-jules', 'like'); assert.equal(store.getSnapshot().message, 'Mutual match confirmed.');
  const match = store.getSnapshot().matches[0]!; store.selectMatch(match.match_id);
  await owner.profiles.setVisibility('pause');
  assert.notEqual(store.getSnapshot().message, 'Mutual match confirmed.'); assert.equal(store.getSnapshot().matches[0]?.state, 'restricted');
  await store.unmatch(match.match_id); assert.equal(store.getSnapshot().matches[0]?.state, 'unmatched');
  assert.equal(adapter.contact(match.match_id)?.canSend, false);
});
test('canceling a delayed request releases its promise and no stale pending work survives a new intent', async () => {
  const { store, adapter } = await setup(); store.setScenario('delayed');
  const pending = store.submit('recommended', 'profile-jules', 'like'); store.cancelPending(); await pending;
  store.setScenario('normal'); await store.submit('recommended', 'profile-jules', 'pass');
  assert.equal(adapter.inspect().actions[0]?.state, 'passed');
});
test('retry from a different discovery mode cannot strand a pending state; original mode retains same-key recovery', async () => {
  const { store, discovery, adapter } = await setup(); store.setScenario('offline');
  await store.submit('recommended', 'profile-jules', 'like'); store.cancelPending();
  discovery.enter('broader'); await tick(); store.setScenario('normal'); await store.retry();
  assert.equal(store.getSnapshot().status, 'error'); assert.equal(store.getSnapshot().pending, null);
  assert.equal(adapter.inspect().actions.length, 0);
  discovery.enter('recommended'); await store.retry();
  assert.equal(store.getSnapshot().status, 'committed'); assert.equal(adapter.inspect().actions.length, 1);
});
for (const accountState of ['suspended', 'deletion_pending'] as const)
  test(`${accountState} store offers minimal cleanup selection and same-key lost-response recovery`, async () => {
    const { store, owner, adapter } = await setup(); store.developmentReciprocal('profile-jules'); await store.submit('recommended', 'profile-jules', 'like');
    const matchId = store.getSnapshot().matches[0]!.match_id;
    owner.scenario(accountState);
    assert.deepEqual(store.getSnapshot().matches, []); assert.deepEqual(store.getSnapshot().cleanupMatches, [{ match_id: matchId, version: 2, state: 'restricted' }]);
    store.selectMatch(matchId); assert.equal(store.getSnapshot().selectedMatchId, matchId);
    store.setScenario('lost_response'); await store.unmatch(matchId);
    assert.equal(store.getSnapshot().canRetry, true); assert.equal(store.getSnapshot().cleanupMatches[0]?.state, 'unmatched');
    store.setScenario('normal'); await store.retry();
    assert.equal(store.getSnapshot().message, 'Unmatched. New contact is unavailable.'); assert.equal(adapter.inspect().receipts.length, 3);
    assert.deepEqual(store.getSnapshot().matches, []); assert.equal(adapter.contact(matchId), null);
    owner.logout(); assert.deepEqual(store.getSnapshot().cleanupMatches, []); assert.equal(store.getSnapshot().selectedMatchId, null);
  });
test('active owner can select a generic cleanup reference after target deletion', async () => {
  const { store, adapter, discovery } = await setup(); store.developmentReciprocal('profile-jules'); await store.submit('recommended', 'profile-jules', 'like');
  const matchId = store.getSnapshot().matches[0]!.match_id, target = discovery.adapter.inspect('discovery-jules')!;
  discovery.adapter.replace({ ...target, facts: { ...target.facts!, account_state: 'deleted' } });
  assert.deepEqual(store.getSnapshot().matches, []); assert.equal(store.getSnapshot().cleanupMatches[0]?.match_id, matchId);
  store.selectMatch(matchId); await store.unmatch(matchId);
  assert.equal(store.getSnapshot().selectedMatchId, matchId); assert.equal(store.getSnapshot().cleanupMatches[0]?.state, 'unmatched');
  assert.equal(adapter.contact(matchId), null);
});
for (const revoke of ['logout', 'target_delete', 'time'] as const)
  test(`a final cleanup ${revoke} callback cannot overwrite newer store revocation with retained private matches`, async () => {
    const time = new FixtureDiscoveryTime(0), { owner, store, discovery } = await setup(time); store.developmentReciprocal('profile-jules'); await store.submit('recommended', 'profile-jules', 'like');
    const capture = owner.profiles.captureInteractionCleanupOwner.bind(owner.profiles); let reads = 0, changed = false;
    owner.profiles.captureInteractionCleanupOwner = () => {
      const token = capture();
      if (++reads === 6) {
        changed = true; owner.profiles.captureInteractionCleanupOwner = capture;
        if (revoke === 'logout') owner.logout();
        else if (revoke === 'time') time.set(1);
        else { const target = discovery.adapter.inspect('discovery-jules')!; discovery.adapter.replace({ ...target, facts: { ...target.facts!, account_state: 'deleted' } }); }
      }
      return token;
    };
    store.refresh(); assert.equal(changed, true); assert.deepEqual(store.getSnapshot().matches, []);
    assert.equal(store.getSnapshot().cleanupMatches.length, revoke === 'logout' ? 0 : 1);
  });
