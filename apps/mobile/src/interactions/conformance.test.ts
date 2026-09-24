import assert from 'node:assert/strict';
import test from 'node:test';
import corpus from '../../../../packages/contracts/fixtures/interactions-v1.json' with { type: 'json' };
import { createFixtureOnboardingStore } from '../onboarding/store.ts';
import { FixtureDiscoveryAdapter } from '../discovery/fixture-adapter.ts';
import { FixtureInteractionAdapter, InteractionFailure } from './fixture-adapter.ts';
import type { InteractionIntent, UnmatchIntent, BlockIntent } from '../contracts/generated/gapp-api-v1.ts';
const options = { isDevelopment: true, mode: 'fixture' };
for (const scenario of corpus.cases) test(`shared interaction trace: ${scenario.name}`, async () => {
  const owner = createFixtureOnboardingStore(options); owner.scenario('eligible');
  const discovery = new FixtureDiscoveryAdapter(owner.profiles, options), adapter = new FixtureInteractionAdapter(owner.profiles, discovery);
  type Prepared = { session: ReturnType<FixtureInteractionAdapter['session']>; intent: InteractionIntent | UnmatchIntent | BlockIntent };
  const originals = new Map<string, Prepared>(); let last: Prepared | null = null;
  for (const step of scenario.steps) {
    const key = `${step.actor}:${['like','pass'].includes(step.action) ? 'interaction' : step.action}:${step.idempotency_key}`;
    let prepared: Prepared;
    try {
      if ('replay_intent' in step && step.replay_intent) prepared = originals.get(key)!;
      else if (['like', 'pass'].includes(step.action)) {
        if (step.actor === 'discovery-jules') {
          const result = adapter.reciprocal('profile-jules', step.idempotency_key);
          assert.equal(result.receipt.outcome_code, step.expected.outcome_code); continue;
        }
        const prior = originals.get(key);
        if (prior || step.expected_version > 0) {
          const previous = (prior ?? last)!;
          prepared = { session: adapter.session(), intent: { ...previous.intent as InteractionIntent,
            target_profile_id: adapter.productionProfile(step.target_profile_id), action: step.action as 'like' | 'pass',
            meta: { expected_version: step.expected_version, idempotency_key: step.idempotency_key } } };
        } else {
          const page = await discovery.request('recommended', 'shared-case', null, true);
          prepared = adapter.prepare(page, step.target_profile_id, step.action as 'like' | 'pass', step.idempotency_key);
        }
      } else {
        const session = step.actor === 'discovery-jules' ? adapter.developmentSession('profile-jules') : adapter.session();
        if (step.action === 'unmatch') prepared = { session, intent: { operation: 'unmatch', match_id: adapter.inspect().matches[0]!.id,
          meta: { expected_version: step.expected_version, idempotency_key: step.idempotency_key } } };
        else prepared = { session, intent: { operation: 'block', target_profile_id: step.actor === 'discovery-jules' ? owner.profiles.getSnapshot().profile!.profile_id : adapter.productionProfile(step.target_profile_id),
          action: step.action as 'block' | 'unblock', meta: { expected_version: step.expected_version, idempotency_key: step.idempotency_key } } };
      }
      if (!originals.has(key)) originals.set(key, prepared); last = prepared;
      const result = adapter.execute(prepared.session, prepared.intent);
      assert.equal('error' in step.expected, false); assert.equal(result.receipt.outcome_code, step.expected.outcome_code);
    } catch (error) {
      assert.ok(error instanceof InteractionFailure); assert.ok('error' in step.expected);
      assert.equal(error.code, step.expected.error === 'idempotency_conflict' ? 'conflict' : step.expected.error);
    }
  }
  const state = adapter.inspect();
  assert.deepEqual({ directional_count: state.actions.length, match_count: state.matches.length, active_match_count: state.matches.filter(match => match.state === 'active').length,
    match_created_events: state.events.filter(event => event.kind === 'match_created').length,
    contact_revoked_events: state.events.filter(event => event.kind === 'contact_revoked').length,
    block_changed_events: state.events.filter(event => event.kind === 'block_changed').length }, scenario.expected);
});
