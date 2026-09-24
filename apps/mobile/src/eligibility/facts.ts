import { adultOutcome, validCivilDate, type FixtureClock, type PredicateOutcome } from '../onboarding/policy.ts';

export type MediaFact = Readonly<{ asset_id: string; owner_id: string; profile_id: string; generation: number;
  state: string | null; policy_version: string | null; delivery_ref: string | null }>;
export type ParticipantFacts = Readonly<{ account_id: string; generation: number; source_id: string;
  profile_id: string | null; birth_date: string | null; account_state: string | null; session_state: string | null;
  verified: boolean | null; consent_state: string | null; consent_version: string | null;
  display_name: string | null; summary: string | null; visibility: string | null; moderation: string | null;
  chart_state: string | null; attribute: string | null; preference_dimension: string | null;
  preference_version: string | null; accepted_options: readonly string[] | null; approved_media: readonly MediaFact[] | null }>;
export type PairPolicy = Readonly<{ version: string; consent_version: string; preference_version: string; media_version: string;
  minimum_age: number; leap_birthday: string; effective_from: string; effective_until: string | null; readiness: string }>;
export const FIXTURE_PAIR_POLICY: PairPolicy = Object.freeze({ version: 'development-eligibility-1',
  consent_version: 'development-consent-1', preference_version: 'development-preferences-1', media_version: 'development-media-1',
  minimum_age: 18, leap_birthday: 'march_1', effective_from: '2026-01-01', effective_until: null, readiness: 'resolved' });
export type BlockState = 'clear' | 'blocked' | 'unknown';
export type Predicates = Readonly<Record<'adult' | 'consent' | 'verified' | 'active' | 'complete' | 'visible' | 'moderation', PredicateOutcome>>;
export type PairState = 'ready' | 'excluded' | 'reload_required' | 'rejected';
export type PairVersion = Readonly<{ viewer_id: string; candidate_id: string; viewer_snapshot_version: string;
  candidate_snapshot_version: string; policy_version: string; viewer_preference_version: string;
  candidate_preference_version: string; viewer_block_version: string; candidate_block_version: string }>;
const copy = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
function freeze<T>(value: T): T {
  if (value && typeof value === 'object') { Object.values(value).forEach(freeze); Object.freeze(value); }
  return value;
}
const same = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);
const whitespace = new Set([0x20, 0x85, 0xa0, 0x1680, 0x2028, 0x2029, 0x202f, 0x205f, 0x3000, 0xfeff]);
const nonblank = (value: unknown): value is string => typeof value === 'string' && [...value].some(character => {
  const code = character.codePointAt(0)!;
  return !whitespace.has(code) && !(code >= 9 && code <= 13) && !(code >= 0x2000 && code <= 0x200a);
});
const versionFields = ['viewer_id', 'candidate_id', 'viewer_snapshot_version', 'candidate_snapshot_version',
  'policy_version', 'viewer_preference_version', 'candidate_preference_version', 'viewer_block_version',
  'candidate_block_version'] as const satisfies readonly (keyof PairVersion)[];
/** A defined malformed precondition is a programming error, never an omitted constraint. */
export function capturePairVersion(value: PairVersion | undefined): PairVersion | undefined {
  if (value === undefined) return undefined;
  if (value === null || typeof value !== 'object' || Array.isArray(value) ||
      Reflect.ownKeys(value).length !== versionFields.length) throw new TypeError('Invalid fixture pair precondition.');
  const descriptors = Object.getOwnPropertyDescriptors(value);
  if (versionFields.some(field => !Object.hasOwn(descriptors, field) || !Object.hasOwn(descriptors[field]!, 'value') ||
      !descriptors[field]!.enumerable || !nonblank(descriptors[field]!.value))) throw new TypeError('Invalid fixture pair precondition.');
  // Copy exact data properties in canonical order without invoking getters or toJSON callbacks.
  return Object.freeze(Object.fromEntries(versionFields.map(field => [field, descriptors[field]!.value])) as PairVersion);
}
function validatePerson(person: ParticipantFacts): void {
  if (!person || typeof person !== 'object' || !nonblank(person.account_id) || !nonblank(person.source_id) ||
      !Number.isSafeInteger(person.generation) || person.generation < 1) throw new TypeError('Invalid fixture participant identity.');
  const strings = ['profile_id', 'birth_date', 'account_state', 'session_state', 'consent_state', 'consent_version',
    'display_name', 'summary', 'visibility', 'moderation', 'chart_state', 'attribute', 'preference_dimension', 'preference_version'] as const;
  if (strings.some(field => person[field] !== null && typeof person[field] !== 'string') ||
      person.verified !== null && typeof person.verified !== 'boolean' ||
      person.accepted_options !== null && (!Array.isArray(person.accepted_options) || person.accepted_options.some(value => typeof value !== 'string')) ||
      person.approved_media !== null && !Array.isArray(person.approved_media)) throw new TypeError('Invalid fixture participant facts.');
  for (const item of person.approved_media ?? []) {
    if (!item || !nonblank(item.asset_id) || !nonblank(item.owner_id) || !nonblank(item.profile_id) ||
        !Number.isSafeInteger(item.generation) || item.generation < 1 ||
        ['state', 'policy_version', 'delivery_ref'].some(field => {
          const value = item[field as 'state' | 'policy_version' | 'delivery_ref'];
          return value !== null && typeof value !== 'string';
        })) throw new TypeError('Invalid fixture media facts.');
  }
}
const conjunction = (...values: PredicateOutcome[]): PredicateOutcome => values.includes('fail') ? 'fail' : values.includes('unknown') ? 'unknown' : 'pass';
const state = (value: string | null, pass: string, failures: readonly string[]): PredicateOutcome =>
  value === pass ? 'pass' : value !== null && failures.includes(value) ? 'fail' : 'unknown';
const required = (value: string | null): PredicateOutcome => value === null ? 'unknown' : nonblank(value) ? 'pass' : 'fail';

export function policyResolved(policy: PairPolicy | null, clock: FixtureClock): policy is PairPolicy {
  const now = clock();
  if (!policy || !Number.isFinite(now.getTime())) return false;
  const day = now.toISOString().slice(0, 10);
  return policy.version === FIXTURE_PAIR_POLICY.version && policy.consent_version === FIXTURE_PAIR_POLICY.consent_version &&
    policy.preference_version === FIXTURE_PAIR_POLICY.preference_version && policy.media_version === FIXTURE_PAIR_POLICY.media_version &&
    policy.minimum_age === 18 && policy.leap_birthday === 'march_1' && policy.readiness === 'resolved' &&
    validCivilDate(policy.effective_from) && policy.effective_from <= day &&
    (policy.effective_until === null || validCivilDate(policy.effective_until) && policy.effective_from < policy.effective_until && day < policy.effective_until);
}
export function ageAt(date: string | null, clock: FixtureClock): number | null {
  const now = clock();
  if (!date || !validCivilDate(date) || !Number.isFinite(now.getTime())) return null;
  const today = now.toISOString().slice(0, 10);
  if (date > today) return null;
  return Number(today.slice(0, 4)) - Number(date.slice(0, 4)) - (today.slice(5) < date.slice(5) ? 1 : 0);
}
export function participantPredicates(person: ParticipantFacts, policy: PairPolicy, clock: FixtureClock): Predicates {
  validatePerson(person);
  let media: PredicateOutcome = person.approved_media === null ? 'unknown' : 'fail';
  if (person.approved_media?.length) {
    const seen = new Set<string>();
    const outcomes: PredicateOutcome[] = [];
    let inconsistent = false;
    for (const item of person.approved_media) {
      if (seen.has(item.asset_id) || item.owner_id !== person.account_id || item.profile_id !== person.profile_id ||
          item.generation !== person.generation || [person.account_id, person.profile_id].includes(item.asset_id)) inconsistent = true;
      seen.add(item.asset_id);
      outcomes.push(conjunction(state(item.state, 'approved', ['selected', 'uploading', 'quarantined', 'pending', 'removed', 'restricted', 'rejected']),
        item.policy_version === null ? 'unknown' : item.policy_version === policy.media_version ? 'pass' : 'fail', required(item.delivery_ref)));
    }
    media = inconsistent ? 'unknown' : outcomes.includes('pass') ? 'pass' : outcomes.includes('unknown') ? 'unknown' : 'fail';
  }
  const consent = conjunction(state(person.consent_state, 'accepted', ['withdrawn', 'declined', 'required']),
    person.consent_version === null ? 'unknown' : person.consent_version === policy.consent_version ? 'pass' : 'fail');
  return Object.freeze({ adult: adultOutcome(person.birth_date, { version: policy.consent_version, minimumAge: policy.minimum_age,
    leapBirthday: 'march_1' }, clock), consent,
    verified: person.verified === null ? 'unknown' : person.verified ? 'pass' : 'fail',
    active: conjunction(state(person.account_state, 'active', ['unverified', 'inactive', 'suspended', 'deletion_pending', 'deleted']),
      state(person.session_state, 'valid', ['none', 'expired', 'revoked', 'restricted'])),
    complete: conjunction(person.profile_id === person.account_id ? 'unknown' : required(person.profile_id), required(person.display_name), required(person.summary), media,
      state(person.chart_state, 'resolved', ['unavailable', 'unresolved', 'pending'])),
    visible: state(person.visibility, 'visible', ['paused', 'hidden', 'incomplete']),
    moderation: state(person.moderation, 'approved', ['restricted', 'rejected', 'suspended']) });
}
export function accepts(actor: ParticipantFacts, target: ParticipantFacts, policy: PairPolicy): PredicateOutcome {
  validatePerson(actor); validatePerson(target);
  if (actor.preference_version !== policy.preference_version || actor.preference_dimension !== 'demo_connection' ||
      actor.accepted_options === null || target.attribute === null) return 'unknown';
  if (!['demo_a', 'demo_b'].includes(target.attribute) || actor.accepted_options.some(option => !['demo_a', 'demo_b'].includes(option)) ||
      new Set(actor.accepted_options).size !== actor.accepted_options.length) return 'unknown';
  return actor.accepted_options.includes(target.attribute) ? 'pass' : 'fail';
}
export function derivePair(viewer: ParticipantFacts | null, candidate: ParticipantFacts | null, policy: PairPolicy | null,
  viewerBlock: BlockState, candidateBlock: BlockState, clock: FixtureClock): Readonly<{ state: PairState;
  viewer?: Predicates; candidate?: Predicates; viewer_accepts_candidate?: PredicateOutcome; candidate_accepts_viewer?: PredicateOutcome }> {
  if (!viewer || !candidate || !policyResolved(policy, clock)) return Object.freeze({ state: 'rejected' });
  validatePerson(viewer); validatePerson(candidate);
  if (viewer.account_id !== candidate.account_id) {
    const identities = (person: ParticipantFacts) => [person.account_id, ...(person.profile_id === null ? [] : [person.profile_id]),
      ...(person.approved_media?.map(item => item.asset_id) ?? [])];
    if (viewer.source_id === candidate.source_id || identities(viewer).some(id => identities(candidate).includes(id))) return Object.freeze({ state: 'rejected' });
  }
  const left = participantPredicates(viewer, policy, clock), right = participantPredicates(candidate, policy, clock);
  const forward = accepts(viewer, candidate, policy), reverse = accepts(candidate, viewer, policy);
  return Object.freeze({ state: viewer.account_id !== candidate.account_id && [...Object.values(left), ...Object.values(right), forward, reverse].every(value => value === 'pass') &&
      viewerBlock === 'clear' && candidateBlock === 'clear' ? 'ready' : 'excluded',
    viewer: left, candidate: right, viewer_accepts_candidate: forward, candidate_accepts_viewer: reverse });
}

/** Private, non-atomic development composition. Neither DTOs nor expected versions are evidence. */
export class FixturePairRepository {
  private people = new Map<string, { facts: ParticipantFacts; revision: number }>();
  private blocks = new Map<string, { state: BlockState; revision: number }>();
  private blockRevisions = new Map<string, number>();
  private serial = 0;
  private policy: PairPolicy | null = FIXTURE_PAIR_POLICY;
  private policyRevision = 0;
  private clockRevision = 0;
  private day: string | null = null;
  private readonly clock: FixtureClock;
  constructor(clock: FixtureClock) { this.clock = clock; }
  put(person: ParticipantFacts): void {
    validatePerson(person);
    this.people.set(person.account_id, { facts: freeze(copy(person)), revision: ++this.serial });
  }
  inspect(accountId: string): ParticipantFacts | null { return this.people.get(accountId)?.facts ?? null; }
  setPolicy(policy: PairPolicy | null): void { this.policy = freeze(copy(policy)); this.policyRevision = ++this.serial; }
  observeBlock(actorId: string, targetId: string, value: BlockState): void {
    if (!nonblank(actorId) || !nonblank(targetId) || !['clear', 'blocked', 'unknown'].includes(value)) throw new TypeError('Invalid fixture block observation.');
    this.blocks.set(JSON.stringify([actorId, targetId]), { state: value, revision: ++this.serial });
    this.blockRevisions.set(actorId, this.serial);
  }
  evaluate(viewerId: string, candidateId: string, expected?: PairVersion): Readonly<{ state: PairState; version: PairVersion | null; candidateAge?: number | null }> {
    if (!nonblank(viewerId) || !nonblank(candidateId)) throw new TypeError('Invalid fixture pair identity.');
    expected = capturePairVersion(expected);
    // A supplied Date can itself carry callbacks. Finish its one numeric read before source capture.
    const suppliedTime = this.clock().getTime(), timestamp = Number.isFinite(suppliedTime) ? suppliedTime : NaN;
    const day = Number.isFinite(timestamp) ? new Date(timestamp).toISOString().slice(0, 10) : 'invalid';
    if (day !== this.day) { this.day = day; this.clockRevision = ++this.serial; }
    const viewer = this.people.get(viewerId), candidate = this.people.get(candidateId);
    const leftBlock = this.blocks.get(JSON.stringify([viewerId, candidateId])), rightBlock = this.blocks.get(JSON.stringify([candidateId, viewerId]));
    const capturedClock = () => new Date(timestamp);
    if (expected !== undefined && (expected.viewer_id !== viewerId || expected.candidate_id !== candidateId)) return { state: 'rejected', version: null };
    const result = derivePair(viewer?.facts ?? null, candidate?.facts ?? null, this.policy,
      leftBlock?.state ?? 'unknown', rightBlock?.state ?? 'unknown', capturedClock);
    if (!viewer || !candidate || result.state === 'rejected') return { state: 'rejected', version: null };
    const token = (person: typeof viewer, blockRevision: number) => JSON.stringify([person.facts.source_id, person.facts.generation, person.revision, blockRevision, this.clockRevision]);
    const version: PairVersion = freeze({ viewer_id: viewerId, candidate_id: candidateId,
      viewer_snapshot_version: token(viewer, this.blockRevisions.get(viewerId) ?? 0), candidate_snapshot_version: token(candidate, this.blockRevisions.get(candidateId) ?? 0),
      policy_version: JSON.stringify([this.policyRevision, this.policy?.version, this.clockRevision]),
      viewer_preference_version: String(viewer.revision), candidate_preference_version: String(candidate.revision),
      viewer_block_version: String(this.blockRevisions.get(viewerId) ?? 0), candidate_block_version: String(this.blockRevisions.get(candidateId) ?? 0) });
    return freeze({ state: result.state === 'excluded' ? 'excluded' : expected !== undefined && !same(expected, version) ? 'reload_required' : 'ready', version, candidateAge: ageAt(candidate.facts.birth_date, capturedClock) });
  }
}
