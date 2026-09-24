import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { ageAt, derivePair, FixturePairRepository, type ParticipantFacts, type PairPolicy, type PairState, type PairVersion, type Predicates, type BlockState } from './facts.ts';

type Case = { id: string; viewer?: Partial<ParticipantFacts>; candidate?: Partial<ParticipantFacts>; policy?: Partial<PairPolicy> | null;
  blocks?: { viewer?: BlockState | null; candidate?: BlockState | null }; clock?: string | null;
  missing_participant?: 'viewer' | 'candidate'; self_pair?: boolean;
  expected: { state: PairState; viewer?: Partial<Predicates>; candidate?: Partial<Predicates>;
    viewer_accepts_candidate?: string; candidate_accepts_viewer?: string } };
const corpus = JSON.parse(readFileSync(new URL('../../../../packages/contracts/fixtures/reciprocal-eligibility-v1.json', import.meta.url), 'utf8')) as {
  base: { viewer: ParticipantFacts; candidate: ParticipantFacts; policy: PairPolicy; clock: string; blocks: { viewer: BlockState; candidate: BlockState } }; cases: Case[] };
const pass: Predicates = { adult: 'pass', consent: 'pass', verified: 'pass', active: 'pass', complete: 'pass', visible: 'pass', moderation: 'pass' };
for (const entry of corpus.cases) {
  test(`shared raw-fact truth table: ${entry.id}`, () => {
    const viewer = entry.missing_participant === 'viewer' ? null : { ...structuredClone(corpus.base.viewer), ...entry.viewer };
    let candidate = entry.missing_participant === 'candidate' ? null : { ...structuredClone(corpus.base.candidate), ...entry.candidate };
    if (entry.self_pair) candidate = viewer;
    const policy = entry.policy === null ? null : { ...corpus.base.policy, ...entry.policy };
    const day = Object.hasOwn(entry, 'clock') ? entry.clock : corpus.base.clock;
    const clock = () => new Date(day ? `${day}T12:00:00Z` : NaN);
    const blocks = { ...corpus.base.blocks, ...entry.blocks };
    const result = derivePair(viewer, candidate, policy, blocks.viewer ?? 'unknown', blocks.candidate ?? 'unknown', clock);
    assert.equal(result.state, entry.expected.state, entry.id);
    if (result.state === 'rejected' || entry.self_pair) return;
    assert.deepEqual(result.viewer, { ...pass, ...entry.expected.viewer }, `${entry.id} viewer`);
    assert.deepEqual(result.candidate, { ...pass, ...entry.expected.candidate }, `${entry.id} candidate`);
    assert.equal(result.viewer_accepts_candidate, entry.expected.viewer_accepts_candidate ?? 'pass');
    assert.equal(result.candidate_accepts_viewer, entry.expected.candidate_accepts_viewer ?? 'pass');
  });
}
function repository() {
  let day = corpus.base.clock;
  const clock = () => new Date(`${day}T12:00:00Z`);
  const repo = new FixturePairRepository(clock);
  const viewer = structuredClone(corpus.base.viewer), candidate = structuredClone(corpus.base.candidate);
  repo.put(viewer); repo.put(candidate);
  repo.observeBlock(viewer.account_id, candidate.account_id, 'clear'); repo.observeBlock(candidate.account_id, viewer.account_id, 'clear');
  return { repo, viewer, candidate, clock, setDay: (value: string) => { day = value; },
    evaluate: (expected?: NonNullable<ReturnType<FixturePairRepository['evaluate']>['version']>) => repo.evaluate(viewer.account_id, candidate.account_id, expected) };
}

test('pair evidence includes exact ordered identities and rejects every stale vector component', () => {
  const { evaluate } = repository(), current = evaluate();
  assert.equal(current.state, 'ready'); assert.ok(current.version);
  for (const field of Object.keys(current.version) as (keyof PairVersion)[]) {
    const changed: PairVersion = { ...current.version, [field]: 'obsolete' };
    assert.equal(evaluate(changed).state, field.endsWith('_id') ? 'rejected' : 'reload_required');
  }
});

test('put captures immutable nested raw facts and does not trust subsequent caller mutation', () => {
  const { repo, viewer, evaluate } = repository();
  const context = evaluate().version!;
  (viewer.accepted_options as string[]).splice(0, viewer.accepted_options!.length, 'demo_b');
  assert.equal(evaluate(context).state, 'ready');
  const held = repo.inspect(viewer.account_id)!;
  assert.ok(Object.isFrozen(held)); assert.ok(Object.isFrozen(held.approved_media));
  assert.throws(() => { (held.accepted_options as string[]).push('demo_b'); }, TypeError);
});

test('same-value writes, sources, generations and A→B→A restoration never revive an old token', () => {
  for (const side of ['viewer', 'candidate'] as const) {
    const subject = repository(), original = subject.evaluate().version!, person = subject[side];
    subject.repo.put({ ...person, visibility: 'paused' });
    assert.equal(subject.evaluate(original).state, 'excluded');
    subject.repo.put(person);
    assert.equal(subject.evaluate(original).state, 'reload_required');
    const restored = subject.evaluate().version!;
    subject.repo.put(person);
    assert.equal(subject.evaluate(restored).state, 'reload_required');
    const same = subject.evaluate().version!;
    subject.repo.put({ ...person, source_id: `${person.source_id}:replacement` });
    assert.equal(subject.evaluate(same).state, 'reload_required');
    subject.repo.put({ ...person, generation: person.generation + 1, approved_media: person.approved_media!.map(item => ({ ...item, generation: person.generation + 1 })) });
    assert.equal(subject.evaluate(same).state, 'reload_required');
  }
});

test('both absent-block observations carry revisions, and unblock never revives retained permission', () => {
  const { repo, viewer, candidate, evaluate } = repository();
  for (const [actor, target] of [[viewer.account_id, candidate.account_id], [candidate.account_id, viewer.account_id]] as const) {
    const original = evaluate().version!;
    repo.observeBlock(actor, target, 'blocked'); assert.equal(evaluate(original).state, 'excluded');
    repo.observeBlock(actor, target, 'clear'); assert.equal(evaluate(original).state, 'reload_required');
    const cleared = evaluate().version!;
    repo.observeBlock(actor, target, 'clear'); assert.equal(evaluate(cleared).state, 'reload_required');
  }
});

test('clock and policy are re-evaluated without a record edit, including restoration', () => {
  const { repo, setDay, evaluate, clock } = repository();
  const original = evaluate().version!;
  assert.equal(ageAt('1990-06-15', clock), 36);
  setDay('2027-09-23'); assert.equal(evaluate(original).state, 'reload_required');
  setDay('2026-09-23'); assert.equal(evaluate(original).state, 'reload_required');
  const current = evaluate().version!;
  repo.setPolicy(null); assert.equal(evaluate(current).state, 'rejected');
  repo.setPolicy(corpus.base.policy); assert.equal(evaluate(current).state, 'reload_required');
});


test('invalid programming inputs fail closed instead of accepting truthy flags or malformed nested facts', () => {
  const subject = repository();
  for (const patch of [{ verified: 'false' }, { generation: true }, { accepted_options: 'demo_b' },
    { approved_media: [null] }, { consent_state: 1 }, { source_id: '' }]) {
    assert.throws(() => subject.repo.put({ ...subject.viewer, ...patch } as ParticipantFacts), TypeError);
  }
  assert.equal(subject.evaluate().state, 'ready', 'Invalid writes cannot replace accepted source state.');
});

test('an outgoing block write against another person still advances the actor aggregate revision', () => {
  const subject = repository(), retained = subject.evaluate().version!;
  subject.repo.observeBlock(subject.viewer.account_id, 'another-fictional-account', 'clear');
  assert.equal(subject.evaluate(retained).state, 'reload_required');
  assert.equal(subject.evaluate().state, 'ready');
});


test('expected versions are copied before an injected dependency can mutate a stale precondition', () => {
  let patchExpected = () => {};
  const repo = new FixturePairRepository(() => { patchExpected(); return new Date('2026-09-23T12:00:00Z'); });
  const { viewer, candidate } = corpus.base;
  repo.put(viewer); repo.put(candidate);
  repo.observeBlock(viewer.account_id, candidate.account_id, 'clear'); repo.observeBlock(candidate.account_id, viewer.account_id, 'clear');
  const current = repo.evaluate(viewer.account_id, candidate.account_id).version!;
  const stale = { ...current, candidate_snapshot_version: 'obsolete' };
  patchExpected = () => { Object.assign(stale, current); };
  assert.equal(repo.evaluate(viewer.account_id, candidate.account_id, stale).state, 'reload_required');
});
