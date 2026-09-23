import assert from 'node:assert/strict';
import test from 'node:test';
import { ContractError, parseDevelopmentRecommendations } from './recommendations.ts';

const payload = () => ({ mode: 'fixture', contract_version: 'gapp-dev-v1', items: [
  { profile_id: 'fictional-alex', display_name: 'Alex', age: 32, summary: 'A fictional adult.', compatibility: { status: 'pending', source: 'fixture' } },
] });

test('accepts a bounded closed fixture projection and an empty result', () => {
  assert.equal(parseDevelopmentRecommendations(payload()).items[0]?.display_name, 'Alex');
  assert.deepEqual(parseDevelopmentRecommendations({ ...payload(), items: [] }).items, []);
});

test('rejects private fields, numeric scores, or fabricated compatibility', () => {
  for (const extra of [{ birth_date: '1990-01-01' }, { email: 'private@example.test' }, { chart_id: 'private' }]) {
    const body = payload(); Object.assign(body.items[0]!, extra);
    assert.throws(() => parseDevelopmentRecommendations(body), ContractError);
  }
  const scored = payload(); Object.assign(scored.items[0]!.compatibility, { score: 95 });
  assert.throws(() => parseDevelopmentRecommendations(scored), ContractError);
  const ready = payload(); ready.items[0]!.compatibility.status = 'ready';
  assert.throws(() => parseDevelopmentRecommendations(ready), ContractError);
});

test('rejects unknown versions, modes, underage adults, duplicates and invalid shapes', () => {
  const duplicate = payload(); duplicate.items.push(duplicate.items[0]!);
  const young = payload(); young.items[0]!.age = 17;
  for (const body of [null, [], {}, { ...payload(), mode: 'production' }, { ...payload(), contract_version: 'future-v2' }, young, duplicate, { ...payload(), items: Array(51).fill(payload().items[0]) }]) {
    assert.throws(() => parseDevelopmentRecommendations(body), ContractError);
  }
});
