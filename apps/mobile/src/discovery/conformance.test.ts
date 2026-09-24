import assert from 'node:assert/strict';
import test from 'node:test';
import population from '../../../../packages/contracts/fixtures/discovery-v1.json' with { type: 'json' };
import { parseDevelopmentDiscoveryPage } from '../contracts/discovery.ts';
import type { DevelopmentDiscoveryPage } from '../contracts/discovery.ts';
import { derivePair, type PairPolicy, type ParticipantFacts } from '../eligibility/facts.ts';
import { createFixtureOnboardingStore } from '../onboarding/store.ts';
import { FixtureDiscoveryAdapter, type DiscoveryMode, type DiscoveryRecord, type FixtureProviderRequest } from './fixture-adapter.ts';

const options = { isDevelopment: true, mode: 'fixture', now: () => Date.parse(population.clock) };
const records = population.candidates as unknown as DiscoveryRecord[];
const expectedAttempts: Record<string, number> = population.expected.provider_attempts_by_account;
const expectedPairs: Record<string, string> = population.expected.pair_states;

function fixture(instrumentProvider = false) {
  const owner = createFixtureOnboardingStore(options);
  owner.scenario('eligible');
  const attempts: Record<string, number> = Object.fromEntries(records.map(row => [row.account_id, 0]));
  const provider = instrumentProvider ? (request: FixtureProviderRequest) => {
    const row = records.find(candidate => candidate.account_id === request.candidate_id);
    assert.ok(row, 'Only independently identified fixture candidates reach compatibility.');
    attempts[row.account_id] = (attempts[row.account_id] ?? 0) + 1;
    return { ...request, state: row.provider_state };
  } : undefined;
  const adapter = new FixtureDiscoveryAdapter(owner.profiles, { ...options, provider });
  return { owner, adapter, attempts };
}

function assertProjection(page: DevelopmentDiscoveryPage) {
  assert.deepEqual(parseDevelopmentDiscoveryPage(page), page);
  assert.deepEqual(Object.keys(page).sort(), ['contract_version', 'discovery_mode', 'items', 'kind', 'mode',
    'next_cursor', 'queue_id', 'request_id', 'session_id', 'state', 'viewer_id'].sort());
  for (const card of page.items) {
    assert.deepEqual(Object.keys(card).sort(), ['age', 'compatibility', 'display_name', 'media_delivery_refs', 'profile_id', 'summary']);
    assert.deepEqual(card.compatibility, { status: 'pending', source: 'fixture' });
    const facts = records.find(row => row.facts?.profile_id === card.profile_id)?.facts;
    assert.ok(facts);
    assert.equal(card.display_name, facts.display_name);
    assert.equal(card.summary, facts.summary);
    assert.equal(card.age, 36);
    assert.deepEqual(card.media_delivery_refs, facts.approved_media!.map(media => media.delivery_ref));
  }
  const serialized = JSON.stringify(page);
  for (const row of records) {
    if (row.mapping?.engine_reference) assert.equal(serialized.includes(row.mapping.engine_reference), false);
    if (row.facts) {
      assert.equal(serialized.includes(row.facts.source_id), false);
      assert.equal(serialized.includes(row.facts.birth_date!), false);
      for (const media of row.facts.approved_media ?? []) assert.equal(serialized.includes(media.asset_id), false);
    }
  }
}

for (const mode of ['recommended', 'broader'] as const) {
  for (const instrumentProvider of [false, true]) {
    test(`shared discovery oracle: actual ${mode} pages with ${instrumentProvider ? 'observed' : 'default'} provider`, async () => {
      const { owner, adapter, attempts } = fixture(instrumentProvider);
      const viewer = owner.profiles.captureDiscoveryViewer();
      assert.ok(viewer);
      const states: string[] = [], ids: string[] = [], cursors = new Set<string>();
      let cursor: string | null = null, queueId: string | null = null;
      const expectedStates = population.expected.page_states_by_mode[mode];
      for (let index = 0; index < expectedStates.length; index += 1) {
        const requestId = `conformance-${index}`;
        const page = await adapter.request(mode, requestId, cursor);
        assertProjection(page);
        assert.equal(page.viewer_id, viewer.facts.account_id);
        assert.equal(page.session_id, viewer.sessionId);
        assert.equal(page.request_id, requestId);
        assert.equal(page.discovery_mode, mode);
        assert.ok(page.queue_id);
        if (queueId !== null) assert.equal(page.queue_id, queueId);
        queueId = page.queue_id;
        assert.ok(adapter.isCurrent(page));
        assert.ok(page.items.length <= population.limits.page_size);
        states.push(page.state); ids.push(...page.items.map(card => card.profile_id));
        cursor = page.next_cursor;
        if (index + 1 < expectedStates.length) {
          assert.ok(cursor, 'An intermediate page must provide its bounded continuation.');
          assert.equal(cursors.has(cursor), false, 'A continuation must not loop to an earlier page.');
          cursors.add(cursor);
        } else assert.equal(cursor, null, 'The declared finite population has a last page.');
      }
      assert.deepEqual(ids, population.expected[`${mode}_profile_ids`]);
      assert.equal(new Set(ids).size, ids.length);
      assert.deepEqual(states, expectedStates);
      assert.equal(adapter.calls.scans, records.length);
      assert.ok(adapter.calls.scans <= population.limits.max_candidates);
      assert.equal(adapter.calls.provider, Object.values(expectedAttempts).reduce((sum, count) => sum + count, 0));
      if (instrumentProvider) assert.deepEqual(attempts, expectedAttempts);
    });
  }
}

test('shared participant decisions use the existing evaluator and independent raw-fact oracle', () => {
  for (const row of records) {
    const result = derivePair(population.viewer.facts as ParticipantFacts, row.facts,
      population.policy as PairPolicy, row.blocks.viewer, row.blocks.candidate, () => new Date(population.clock));
    assert.equal(result.state, expectedPairs[row.account_id], row.account_id);
  }
});

for (const [providerState, expected] of Object.entries(population.expected.provider_state_semantics)) {
  test(`shared provider oracle: ${providerState} preserves pending public cards and declared attempts`, async () => {
    const owner = createFixtureOnboardingStore(options);
    owner.scenario('eligible');
    const adapter = new FixtureDiscoveryAdapter(owner.profiles, { ...options,
      provider: request => ({ ...request, state: providerState }) });
    const page = await adapter.request('recommended', 'provider-conformance', null);
    assertProjection(page);
    assert.equal(page.state, expected.page_state);
    assert.deepEqual(page.items.map(card => card.profile_id), population.expected.recommended_profile_ids.slice(0, 2));
    assert.equal(adapter.calls.provider, expected.attempts * population.limits.page_size);
  });
}

for (const [label, mode, requestId, cursor, refresh] of [
  ['unknown mode', 'unknown', 'request-1', null, false],
  ['empty request identity', 'recommended', '', null, false],
  ['request slash', 'recommended', 'request/private', null, false],
  ['request newline', 'recommended', 'request-1\n', null, false],
  ['oversized request identity', 'recommended', 'r'.repeat(129), null, false],
  ['non-string request', 'recommended', {}, null, false],
  ['cursor newline', 'recommended', 'request-1', 'cursor-1\n', false],
  ['cursor private JSON', 'recommended', 'request-1', '{"engine_reference":"private"}', false],
  ['non-string cursor', 'recommended', 'request-1', {}, false],
  ['non-boolean refresh', 'recommended', 'request-1', null, 'yes'],
  ['refresh with continuation', 'recommended', 'request-1', 'cursor-1', true],
] as const) {
  test(`malformed discovery controls reject before work: ${label}`, async () => {
    const { adapter } = fixture();
    await assert.rejects(() => adapter.request(mode as DiscoveryMode, requestId as string,
      cursor as string | null, refresh as boolean), TypeError);
    assert.deepEqual(adapter.calls, { scans: 0, mappings: 0, provider: 0 });
  });
}

test('well-formed unknown continuation has a closed reload response and performs no candidate work', async () => {
  const { adapter } = fixture();
  const page = await adapter.request('recommended', 'request-1', 'unknown-cursor');
  assertProjection(page);
  assert.equal(page.state, 'reload_required');
  assert.deepEqual(page.items, []);
  assert.equal(page.next_cursor, null);
  assert.deepEqual(adapter.calls, { scans: 0, mappings: 0, provider: 0 });
});
