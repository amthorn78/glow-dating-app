import assert from 'node:assert/strict';
import test from 'node:test';
import type { OwnProfile, ProfileIntent } from '../contracts/generated/gapp-api-v1.ts';
import { parseAppIntent, parseAppResponse, ProductionContractError } from '../contracts/production.ts';
import { canonicalSelections, FIXTURE_PREFERENCE_POLICY, PROFILE_IDS, PROFILE_REQUEST_ID,
  selectionsValid, type PreferencePolicy } from './policy.ts';

const intent = (display_name: string, summary = ''): ProfileIntent => ({
  operation: 'profile', meta: { idempotency_key: 'profile-policy-test', expected_version: 0 }, display_name, summary,
});
const own = (summary: string, visibility: OwnProfile['visibility'] = 'incomplete'): OwnProfile => ({
  kind: 'own_profile', profile_id: PROFILE_IDS.alex, version: 1, display_name: 'Alex', summary, visibility, media_ids: [],
});
const response = (data: unknown) => ({ contract_version: 'gapp-api-v1', request_id: PROFILE_REQUEST_ID, data });

test('profile limits count Unicode scalars, including astral characters and combining marks', () => {
  for (const [name, summary] of [
    ['A'.repeat(80), 'B'.repeat(500)],
    ['😀'.repeat(80), '😀'.repeat(500)],
    ['e\u0301'.repeat(40), 'e\u0301'.repeat(250)],
  ]) {
    assert.doesNotThrow(() => parseAppIntent(intent(name!, summary)));
    assert.doesNotThrow(() => parseAppResponse(response({ ...own(summary!), display_name: name })));
    assert.throws(() => parseAppIntent(intent(`${name}a`, summary)), ProductionContractError);
    assert.throws(() => parseAppIntent(intent(name!, `${summary}a`)), ProductionContractError);
  }
});

test('empty biography is a valid draft but whitespace-only fields and empty names are rejected', () => {
  assert.doesNotThrow(() => parseAppIntent(intent('Alex')));
  assert.doesNotThrow(() => parseAppResponse(response(own(''))));
  assert.throws(() => parseAppIntent(intent('')), ProductionContractError);
  for (const whitespace of [' ', '\t\n\r', '\u0085\u00a0\u1680\u2000\u2028\u202f\u205f\u3000\ufeff']) {
    assert.throws(() => parseAppIntent(intent(whitespace)), ProductionContractError);
    assert.throws(() => parseAppIntent(intent('Alex', whitespace)), ProductionContractError);
    assert.throws(() => parseAppResponse(response(own(whitespace))), ProductionContractError);
  }
});

test('profile decoding preserves submitted spacing and does not normalize Unicode', () => {
  const value = intent('  A\u0301lex\u00a0', '\n A biography. \n');
  assert.deepEqual(parseAppIntent(value), value);
  const profile = { ...own(value.summary), display_name: value.display_name };
  assert.deepEqual(parseAppResponse(response(profile)).data, profile);
});

test('lone UTF-16 surrogates and oversized profile fields cannot enter saved projections', () => {
  for (const bad of ['\ud800', '\udfff', 'A\ud800B', 'A\udfffB']) {
    assert.throws(() => parseAppIntent(intent(bad)), ProductionContractError);
    assert.throws(() => parseAppIntent(intent('Alex', bad)), ProductionContractError);
    assert.throws(() => parseAppResponse(response(own(bad))), ProductionContractError);
  }
  assert.throws(() => parseAppResponse(response({ ...own('Biography'), display_name: '😀'.repeat(81) })), ProductionContractError);
  assert.throws(() => parseAppResponse(response(own('😀'.repeat(501)))), ProductionContractError);
});

test('profile commands cannot grant visibility, completion, approval or private owner fields', () => {
  for (const extra of [{ visibility: 'visible' }, { complete: true }, { profile_complete: true },
    { media_ids: [] }, { chart_resolved: true }, { moderation: 'approved' }, { owner_id: PROFILE_IDS.alex }]) {
    assert.throws(() => parseAppIntent({ ...intent('Alex', 'Biography'), ...extra }), ProductionContractError);
  }
  assert.throws(() => parseAppIntent({ ...intent('Alex'), meta: { ...intent('Alex').meta, complete: true } }), ProductionContractError);
  assert.throws(() => parseAppResponse(response({ ...own('Biography'), private_email: 'alex@example.invalid' })), ProductionContractError);
});

test('a visible own-profile projection requires a nonempty biography', () => {
  assert.doesNotThrow(() => parseAppResponse(response(own('Biography', 'visible'))));
  assert.throws(() => parseAppResponse(response(own('', 'visible'))), ProductionContractError);
  assert.throws(() => parseAppResponse(response(own('\u00a0', 'visible'))), ProductionContractError);
  for (const state of ['incomplete', 'paused', 'restricted', 'removed'] as const) {
    assert.doesNotThrow(() => parseAppResponse(response(own('', state))));
  }
});

test('preference selections reject duplicate dimensions/options and unknown vocabulary', () => {
  const selection = { dimension: 'demo_connection', accepted_option_ids: ['demo_a'] };
  assert.equal(selectionsValid([selection], FIXTURE_PREFERENCE_POLICY), true);
  assert.equal(selectionsValid([selection, selection], FIXTURE_PREFERENCE_POLICY), false);
  assert.equal(selectionsValid([{ ...selection, accepted_option_ids: ['demo_a', 'demo_a'] }], FIXTURE_PREFERENCE_POLICY), false);
  assert.equal(selectionsValid([{ ...selection, dimension: 'unknown_dimension' }], FIXTURE_PREFERENCE_POLICY), false);
  assert.equal(selectionsValid([{ ...selection, accepted_option_ids: ['unknown_option'] }], FIXTURE_PREFERENCE_POLICY), false);
  assert.equal(selectionsValid([selection], null), false);
  assert.equal(selectionsValid([], FIXTURE_PREFERENCE_POLICY), true);
  assert.equal(selectionsValid([{ ...selection, accepted_option_ids: [] }], FIXTURE_PREFERENCE_POLICY), true);
});

test('preference wire ceilings admit 20 dimensions and 50 options but reject 21 and 51', () => {
  const options = Array.from({ length: 51 }, (_, index) => ({ id: `option_${index}`, label: `Option ${index}` }));
  const policy: PreferencePolicy = { version: 'boundary-policy',
    dimensions: Array.from({ length: 21 }, (_, index) => ({ id: `dimension_${index}`, label: `Dimension ${index}`, options })) };
  const selections = policy.dimensions.map(dimension => ({ dimension: dimension.id,
    accepted_option_ids: options.slice(0, 50).map(option => option.id) }));
  assert.equal(selectionsValid(selections.slice(0, 20), policy), true);
  assert.equal(selectionsValid(selections, policy), false);
  assert.equal(selectionsValid([{ dimension: 'dimension_0', accepted_option_ids: options.map(option => option.id) }], policy), false);
});

test('canonical selections ignore object insertion order while retaining dimension and option order', () => {
  const selections = [{ dimension: 'one', accepted_option_ids: ['a', 'b'] },
    { dimension: 'two', accepted_option_ids: ['c'] }];
  const reorderedObjects = [{ accepted_option_ids: ['a', 'b'], dimension: 'one' },
    { accepted_option_ids: ['c'], dimension: 'two' }];
  assert.deepEqual(canonicalSelections(selections), canonicalSelections(reorderedObjects));
  assert.notDeepEqual(canonicalSelections(selections), canonicalSelections([...selections].reverse()));
  assert.notDeepEqual(canonicalSelections(selections), canonicalSelections([
    { dimension: 'one', accepted_option_ids: ['b', 'a'] }, selections[1]!,
  ]));
  const canonical = canonicalSelections(selections);
  selections[0]!.accepted_option_ids.push('later');
  assert.deepEqual(canonical, [['one', ['a', 'b']], ['two', ['c']]]);
});
