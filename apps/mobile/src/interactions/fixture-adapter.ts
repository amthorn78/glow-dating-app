import corpus from '../../../../packages/contracts/fixtures/interactions-v1.json' with { type: 'json' };
import flows from '../../../../packages/contracts/production/flows-v1.json' with { type: 'json' };
import type { BlockIntent, CommandReceipt, InteractionCommandResult, InteractionIntent, MatchProjection, UnmatchIntent } from '../contracts/generated/gapp-api-v1.ts';
import type { DevelopmentDiscoveryPage, DevelopmentDiscoveryProfile } from '../contracts/generated/gapp-dev-v1.ts';
import { parseAppIntent } from '../contracts/production.ts';
import { FixtureDiscoveryAdapter, interactionAccountIsCurrent, interactionPairIsCurrent, type InteractionPairCapture } from '../discovery/fixture-adapter.ts';
import { validateInteractionCommandResult } from '../contracts/generated/validators.js';
import type { DevelopmentInteractionEvent } from '../contracts/generated/gapp-dev-v1.ts';
import { parseDevelopmentDiscoveryPage } from '../contracts/discovery.ts';
import { discoveryViewerIsCurrent, type ProfileStore } from '../profiles/store.ts';

const freeze = <T>(value: T): T => { if (value && typeof value === 'object') { Object.values(value).forEach(freeze); Object.freeze(value); } return value; };
const uuid = (kind: number, value: number) => `${kind.toString(16).padStart(8, '0')}-0000-4000-8000-${value.toString(16).padStart(12, '0')}`;
const direction = (actor: string, target: string) => `${actor}:${target}`;
const pairKey = (actor: string, target: string) => [actor, target].sort().join(':');
const canonical = (value: unknown): string => JSON.stringify(value, (_key, item: unknown) => item && typeof item === 'object' && !Array.isArray(item) ? Object.fromEntries(Object.entries(item).sort(([a], [b]) => a.localeCompare(b))) : item);
export type InteractionErrorCode = 'unavailable' | 'stale' | 'conflict' | 'policy_unresolved' | 'invalid_request' | 'capacity' | 'pending' | 'offline';
export class InteractionFailure extends Error {
  readonly code: InteractionErrorCode;
  constructor(code: InteractionErrorCode) { super(({ unavailable: 'This action is unavailable. Reload current people.', stale: 'This action is out of date. Reload current people.',
    conflict: 'This request conflicts with an earlier action. Reload current people.', policy_unresolved: 'This action is not available under the current fixture policy.',
    invalid_request: 'This request could not be accepted.', capacity: 'The fixture session is full. Start a new fixture session.', pending: 'This action is already pending.',
    offline: 'The response was not received. Retry the same request to reconcile its outcome.' })[code]); this.code = code; }
}
type Intent = InteractionIntent | UnmatchIntent | BlockIntent;
type Session = Readonly<{ actor: string; sessionId: string; profileId: string }>;
type Identity = Readonly<{ account_id: string; profile_id: string; account_uuid: string; profile_uuid: string }>;
type Action = Readonly<{ id: string; actor: string; target: string; state: 'liked' | 'passed'; version: number; source: InteractionPairCapture; matchable: boolean }>;
type Match = Readonly<{ id: string; first: string; second: string; state: 'active' | 'restricted' | 'unmatched'; version: number; contactVersion: number; source: InteractionPairCapture }>;
type Block = Readonly<{ id: string; actor: string; target: string; state: 'active' | 'removed'; version: number }>;
export type LogicalEvent = DevelopmentInteractionEvent;
type ReceiptRecord = Readonly<{ digest: string; receipt: CommandReceipt; target: string; operation: Intent['operation'] }>;
type State = Readonly<{ discretionaryEvents: number; revision: number; actions: ReadonlyMap<string, Action>; matches: ReadonlyMap<string, Match>;
  blocks: ReadonlyMap<string, Block>; receipts: ReadonlyMap<string, ReceiptRecord>; events: readonly LogicalEvent[] }>;
type Batch = Readonly<{ page: DevelopmentDiscoveryPage; actor: string; sessionId: string; profileId: string; pair: InteractionPairCapture }>;
export type MatchView = MatchProjection & Readonly<{ profile: DevelopmentDiscoveryProfile | null }>;
const sessions = new WeakMap<object, { authority: object; pair?: InteractionPairCapture; reverse: boolean }>();
function transition(flow: string, event: string, from: string, to: string, policies: readonly string[] = []) {
  const rule = flows.flows.find(value => value.id === flow)?.transitions.find(value => value.event === event && value.from === from && value.to === to);
  if (!rule) throw new InteractionFailure('conflict');
  if (!rule.policies.every(policy => policies.includes(policy))) throw new InteractionFailure('policy_unresolved');
}
/** In-process presentation substitute; Python owns production domain semantics. No route/network/provider. */
export class FixtureInteractionAdapter {
  private state: State = { discretionaryEvents: 0, revision: 0, actions: new Map(), matches: new Map(), blocks: new Map(), receipts: new Map(), events: [] };
  private readonly identities: readonly Identity[] = freeze(corpus.identities.map(identity => ({ ...identity })));
  private readonly batches = new Map<string, Batch>();
  private readonly pending = new Map<string, string>();
  private readonly listeners = new Set<() => void>();
  private serial = 0;
  private batchSerial = 0;
  private policy = true;
  private reconciling = false;
  private beforeCommit: (() => void) | null;
  private readonly matchProjectionGuards = new WeakMap<MatchProjection, { owner: object; target: object | null; match: Match }>();
  readonly profiles: ProfileStore;
  readonly discovery: FixtureDiscoveryAdapter;
  constructor(profiles: ProfileStore, discovery: FixtureDiscoveryAdapter, options: { beforeCommit?: () => void } = {}) {
    this.profiles = profiles; this.discovery = discovery; this.beforeCommit = options.beforeCommit ?? null;
    discovery.bindConsumption((owner, profile) => this.consumed(owner, profile));
    profiles.subscribe(() => this.sourceChanged()); discovery.subscribe(() => this.sourceChanged());
  }
  readonly subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  private emit() { this.listeners.forEach(listener => listener()); }
  private owner() { const current = this.profiles.captureInteractionOwner(); if (!current) throw new InteractionFailure('unavailable'); return current; }
  private target(profile: string): Identity {
    const rows = this.identities.filter(value => value.profile_uuid === profile || value.profile_id === profile);
    if (rows.length !== 1) throw new InteractionFailure('unavailable');
    const identity = rows[0]!;
    const record = this.discovery.inspect(identity.account_id);
    // Current registry source must still have exactly that ownership; missing or substituted rows fail closed.
    if (!record?.facts || record.account_id !== identity.account_id || record.facts.account_id !== identity.account_id || record.facts.profile_id !== identity.profile_id || record.facts.account_state === 'deleted') throw new InteractionFailure('unavailable');
    return identity;
  }
  session(): Session {
    const authority = this.owner();
    if (!authority.profileId) throw new InteractionFailure('unavailable');
    const session = freeze({ actor: authority.ownerId, sessionId: authority.sessionId, profileId: authority.profileId });
    sessions.set(session, { authority, reverse: false }); return session;
  }
  private validateSession(session: Session) {
    const registered = sessions.get(session);
    if (!registered) throw new InteractionFailure('unavailable');
    const current = this.owner();
    if (current.sessionId !== session.sessionId ||
      (!registered.reverse && current.ownerId !== session.actor)) throw new InteractionFailure('unavailable');
    const reverse = registered.reverse ? this.discovery.captureAccountSession(this.target(session.profileId).account_id) : null;
    if (registered.reverse && !reverse) throw new InteractionFailure('unavailable');
    return { owner: current, reverse };
  }
  productionProfile(profileHandle: string) { return this.target(profileHandle).profile_uuid; }
  prepare(page: DevelopmentDiscoveryPage, profile: string, action: 'like' | 'pass', key: string): { session: Session; intent: InteractionIntent } {
    const session = this.session(), target = this.target(profile), pair = this.discovery.authorizeInteraction(page, profile);
    if (!pair || pair.viewerId !== session.actor || pair.targetAccountId !== target.account_id || this.consumed(session.actor, profile)) throw new InteractionFailure('stale');
    if (this.batches.size >= 200) throw new InteractionFailure('capacity');
    const batchId = uuid(0x81, ++this.batchSerial);
    this.batches.set(batchId, { page, actor: session.actor, sessionId: session.sessionId, profileId: target.profile_uuid, pair });
    const intent: InteractionIntent = { operation: 'interaction', target_profile_id: target.profile_uuid, batch_id: batchId, batch_version: 1,
      action, meta: { expected_version: this.state.actions.get(direction(session.actor, target.account_uuid))?.version ?? 0, idempotency_key: key } };
    parseAppIntent(intent); return { session, intent: freeze(intent) };
  }
  consumed(owner: string, profile: string): boolean {
    let target: Identity; try { target = this.target(profile); } catch { return true; }
    return this.state.actions.has(direction(owner, target.account_uuid)) || this.state.matches.has(pairKey(owner, target.account_uuid)) ||
      this.state.blocks.get(direction(owner, target.account_uuid))?.state === 'active' || this.state.blocks.get(direction(target.account_uuid, owner))?.state === 'active';
  }
  private pair(target: Identity): InteractionPairCapture | null {
    const owner = this.profiles.captureInteractionOwner();
    if (!owner || this.state.blocks.get(direction(owner.ownerId, target.account_uuid))?.state === 'active' ||
      this.state.blocks.get(direction(target.account_uuid, owner.ownerId))?.state === 'active') return null;
    return this.discovery.captureInteractionPair(target.profile_id);
  }
  private sourceChanged(notify = true) {
    if (this.reconciling) return;
    this.reconciling = true;
    try {
      const prior = this.state, matches = new Map(prior.matches), events = [...prior.events]; let changed = false;
      for (const [key, match] of matches) {
        if (match.state !== 'active') continue;
        const target = this.identities.find(value => [match.first, match.second].includes(value.account_uuid));
        let pair: InteractionPairCapture | null = null;
        try { if (target) { this.target(target.profile_uuid); pair = this.pair(target); } } catch { /* Lost authority stays generic. */ }
        if (!pair || !interactionPairIsCurrent(pair) || !interactionPairIsCurrent(match.source)) {
          const next = freeze({ ...match, state: 'restricted' as const, version: match.version + 1, contactVersion: match.contactVersion + 1 });
          matches.set(key, next); events.push(this.event(next, 'match.revoked')); changed = true;
        }
      }
      if (changed && this.state === prior) this.state = { ...prior, revision: prior.revision + 1, matches, events: freeze(events) };
    } finally { this.reconciling = false; }
    if (notify) this.emit();
  }
  private event(match: Match, type: 'match.created' | 'match.revoked'): LogicalEvent {
    return freeze({ event_id: uuid(0x84, ++this.serial), kind: type === 'match.created' ? 'match_created' : 'contact_revoked', contract_version: 'gapp-interactions-fixture-v1',
      aggregate_id: match.id, aggregate_version: match.version });
  }
  private projection(session: Session, record: ReceiptRecord): InteractionCommandResult['current_projection'] {
    if (record.operation === 'unmatch') {
      const match = [...this.state.matches.values()].find(value => value.id === record.receipt.object_ref);
      return match ? this.projectMatch(session, match) : null;
    }
    if (record.operation === 'block') {
      const block = this.state.blocks.get(direction(session.actor, record.target));
      const identity = this.identities.find(value => value.account_uuid === record.target);
      if (identity) { try { this.target(identity.profile_uuid); } catch { return null; } }
      return block && identity ? { kind: 'block', target_profile_id: identity.profile_uuid, version: block.version, state: block.state } : null;
    }
    const identity = this.identities.find(value => value.account_uuid === record.target);
    const pair = identity ? this.pair(identity) : null;
    const action = this.state.actions.get(direction(session.actor, record.target));
    if (!identity || !pair || !interactionPairIsCurrent(pair) || !action || !action.matchable || !interactionPairIsCurrent(action.source)) return null;
    const match = this.state.matches.get(pairKey(session.actor, record.target));
    if (match && match.state !== 'active') return null;
    return { kind: 'interaction', target_profile_id: identity.profile_uuid, version: action.version, state: action.state,
      match_id: match?.state === 'active' && interactionPairIsCurrent(match.source) ? match.id : null };
  }
  private result(session: Session, record: ReceiptRecord, replayed: boolean, targetGuard: object | null): InteractionCommandResult {
    this.sourceChanged(false);
    const authority = this.validateSession(session), current = this.state;
    const projection = this.projection(session, record);
    const permitted = (projection?.kind !== 'match' || this.matchProjectionCurrent(projection)) && (!targetGuard || interactionAccountIsCurrent(targetGuard)) && this.state === current && discoveryViewerIsCurrent(authority.owner) && (!authority.reverse || interactionAccountIsCurrent(authority.reverse));
    const result: InteractionCommandResult = { kind: 'interaction_command_result', receipt: record.receipt, replayed, current_projection: permitted ? projection : null };
    if (!validateInteractionCommandResult(result)) throw new InteractionFailure('invalid_request'); return freeze(result);
  }
  /** Capture intent before any callback; own-property data JSON excludes accessors/prototypes. */
  private captureIntent(value: Intent): Intent {
    const capture = (input: unknown): unknown => {
      if (input === null || typeof input !== 'object') return input;
      if (Array.isArray(input) || Object.getPrototypeOf(input) !== Object.prototype) throw new InteractionFailure('invalid_request');
      const descriptors = Object.getOwnPropertyDescriptors(input);
      if (Reflect.ownKeys(input).some(key => typeof key !== 'string') || Object.values(descriptors).some(field => !field.enumerable || !Object.hasOwn(field, 'value'))) throw new InteractionFailure('invalid_request');
      return Object.fromEntries(Object.entries(descriptors).map(([key, field]) => [key, capture(field.value)]));
    };
    try { const intent = capture(value) as Intent; parseAppIntent(intent); if (!['interaction', 'unmatch', 'block'].includes(intent.operation)) throw new Error(); return freeze(intent); }
    catch { throw new InteractionFailure('invalid_request'); }
  }
  execute(session: Session, submitted: Intent): InteractionCommandResult {
    const intent = this.captureIntent(submitted);
    const commandAuthority = this.validateSession(session);
    const submittedTarget = intent.operation !== 'unmatch' && !sessions.get(session)!.reverse ? this.target(intent.target_profile_id) : null;
    const targetGuard = submittedTarget ? this.discovery.captureAccountRecord(submittedTarget.account_id) : null;
    if (submittedTarget && !targetGuard) throw new InteractionFailure('unavailable');
    const key = `${session.actor}:${intent.operation}:${intent.meta.idempotency_key}`, digest = canonical({ ...intent, meta: { expected_version: intent.meta.expected_version } });
    const receipt = this.state.receipts.get(key);
    if (receipt) { if (receipt.digest !== digest) throw new InteractionFailure('conflict'); return this.result(session, receipt, true, targetGuard); }
    if (this.pending.has(key)) throw new InteractionFailure(this.pending.get(key) === digest ? 'pending' : 'conflict');
    if (this.pending.size >= 20 || this.state.receipts.size + this.pending.size >= corpus.limits.max_receipts) throw new InteractionFailure('capacity');
    this.pending.set(key, digest);
    try {
      const initial = this.state, actions = new Map(initial.actions), matches = new Map(initial.matches), blocks = new Map(initial.blocks), events = [...initial.events];
      let object: Action | Match | Block, targetId: string, outcome: CommandReceipt['outcome_code'], pair: InteractionPairCapture | null = null, durablePair: InteractionPairCapture | null = null, batchPair: InteractionPairCapture | null = null;
      const registered = sessions.get(session)!;
      if (intent.operation === 'unmatch') {
        const found = [...matches.entries()].find(([, value]) => value.id === intent.match_id);
        if (!found || ![found[1].first, found[1].second].includes(session.actor)) throw new InteractionFailure('unavailable');
        const [canonical, prior] = found; targetId = prior.first === session.actor ? prior.second : prior.first;
        if (intent.meta.expected_version !== prior.version) throw new InteractionFailure('stale');
        transition('F10', 'unmatch', prior.state, 'unmatched');
        object = prior.state === 'unmatched' ? prior : freeze({ ...prior, state: 'unmatched', version: prior.version + 1, contactVersion: prior.contactVersion + 1 });
        matches.set(canonical, object as Match); if (prior.state !== 'unmatched') events.push(this.event(object as Match, 'match.revoked')); outcome = 'unmatched';
      } else {
        const owner = this.owner();
        let target: Identity;
        if (registered.reverse) {
          target = { account_id: owner.ownerId, profile_id: owner.profileId!, account_uuid: owner.ownerId, profile_uuid: owner.profileId! };
          if (intent.target_profile_id !== target.profile_uuid) throw new InteractionFailure('unavailable');
        } else target = this.target(intent.target_profile_id);
        targetId = target.account_uuid;
        if (targetId === session.actor || intent.target_profile_id === session.profileId) throw new InteractionFailure('unavailable');
        const directional = direction(session.actor, targetId), canonical = pairKey(session.actor, targetId);
        if (intent.operation === 'block') {
          const prior = blocks.get(directional), next = intent.action === 'block' ? 'active' : 'removed';
          if (intent.meta.expected_version !== (prior?.version ?? 0)) throw new InteractionFailure('stale');
          transition('F13', intent.action, prior?.state ?? 'none', next);
          object = prior?.state === next ? prior : freeze({ id: prior?.id ?? uuid(0x85, ++this.serial), actor: session.actor, target: targetId, state: next, version: (prior?.version ?? 0) + 1 });
          blocks.set(directional, object as Block); outcome = next === 'active' ? 'blocked' : 'unblocked';
          // Only this blocked pair loses old reciprocal-like authority. Unblock cannot restore it.
          if (next === 'active') {
            for (const key of [directional, direction(targetId, session.actor)]) {
              const previous = actions.get(key);
              if (previous) actions.set(key, freeze({ ...previous, matchable: false }));
            }
          }
          if (object !== prior) events.push(freeze({ event_id: uuid(0x84, ++this.serial), kind: 'block_changed', aggregate_id: object.id, aggregate_version: object.version, contract_version: 'gapp-interactions-fixture-v1' }));
          const match = matches.get(canonical);
          if (next === 'active' && match?.state === 'active') { const revoked = freeze({ ...match, state: 'restricted' as const, version: match.version + 1, contactVersion: match.contactVersion + 1 }); matches.set(canonical, revoked); events.push(this.event(revoked, 'match.revoked')); }
        } else {
          const existing = actions.get(directional);
          if (existing) transition('F08', intent.action, existing.state, intent.action === 'like' ? 'liked' : 'passed');
          const batch = this.batches.get(intent.batch_id);
          if (!this.policy) throw new InteractionFailure('policy_unresolved');
          if (!batch || batch.actor !== session.actor || batch.sessionId !== session.sessionId || batch.profileId !== intent.target_profile_id || intent.batch_version !== 1 || !interactionPairIsCurrent(batch.pair)) throw new InteractionFailure('stale');
          batchPair = batch.pair;
          pair = registered.reverse ? this.discovery.captureInteractionPair(registered.pair!.profileHandle) : this.discovery.authorizeInteraction(batch.page, target.profile_id);
          if (!pair || !interactionPairIsCurrent(pair) || blocks.get(directional)?.state === 'active' || blocks.get(direction(targetId, session.actor))?.state === 'active') throw new InteractionFailure('unavailable');
          durablePair = this.discovery.captureInteractionPair(pair.profileHandle);
          if (!durablePair) throw new InteractionFailure('unavailable');
          const prior = actions.get(directional), next = intent.action === 'like' ? 'liked' : 'passed';
          if (intent.meta.expected_version !== (prior?.version ?? 0)) throw new InteractionFailure('stale');
          transition('F08', intent.action, prior?.state ?? 'none', next);
          const match = matches.get(canonical);
          if (match && match.state !== 'active') throw new InteractionFailure('policy_unresolved');
          object = prior?.state === next ? prior : freeze({ id: prior?.id ?? uuid(0x82, ++this.serial), actor: session.actor, target: targetId, state: next, version: (prior?.version ?? 0) + 1, source: durablePair, matchable: true });
          actions.set(directional, object as Action); outcome = next;
          if (!match && next === 'liked' && actions.get(directional)!.matchable && interactionPairIsCurrent(actions.get(directional)!.source) &&
            actions.get(direction(targetId, session.actor))?.state === 'liked' &&
            interactionPairIsCurrent(actions.get(direction(targetId, session.actor))!.source) && actions.get(direction(targetId, session.actor))!.matchable) {
            transition('F09', 'reciprocal', 'none', 'active', ['reciprocal_likes']);
            const [first, second] = [session.actor, targetId].sort();
            const created: Match = freeze({ id: uuid(0x83, ++this.serial), first: first!, second: second!, state: 'active', version: 1, contactVersion: 1, source: this.discovery.captureInteractionPair(pair.profileHandle)! });
            matches.set(canonical, created); events.push(this.event(created, 'match.created'));
          }
        }
      }
      const record: ReceiptRecord = freeze({ digest, target: targetId, operation: intent.operation,
        receipt: { outcome_code: outcome, object_ref: object.id, committed_version: object.version } });
      const receipts = new Map(initial.receipts); receipts.set(key, record);
      if (initial.discretionaryEvents + events.length - initial.events.length > corpus.limits.max_events) throw new InteractionFailure('capacity');
      this.beforeCommit?.();
      // Finish every callback-capable authority read, then compare captured concrete cells and owned state.
      this.validateSession(session);
      if (targetGuard && !interactionAccountIsCurrent(targetGuard) || !discoveryViewerIsCurrent(commandAuthority.owner) || commandAuthority.reverse && !interactionAccountIsCurrent(commandAuthority.reverse) || pair && !interactionPairIsCurrent(pair) || durablePair && !interactionPairIsCurrent(durablePair) || batchPair && !interactionPairIsCurrent(batchPair) || this.state !== initial) throw new InteractionFailure('stale');
      this.state = { discretionaryEvents: initial.discretionaryEvents + events.length - initial.events.length, revision: initial.revision + 1, actions, matches, blocks, receipts, events: freeze(events) };
      // Notifications follow the indivisible owned-state publication. Consumption invalidates both modes.
      if (!registered.reverse || intent.operation !== 'interaction' || matches.size !== initial.matches.size) this.discovery.interactionsChanged(); this.emit();
      return this.result(session, record, false, targetGuard);
    } finally { this.pending.delete(key); }
  }
  private matchProjectionCurrent(projection: MatchProjection): boolean {
    const guard = this.matchProjectionGuards.get(projection);
    return !!guard && discoveryViewerIsCurrent(guard.owner) && (!guard.target || interactionAccountIsCurrent(guard.target)) &&
      this.state.matches.get(pairKey(guard.match.first, guard.match.second)) === guard.match;
  }
  /** Reading a match needs current target disclosure authority; cleanup does not. */
  private projectMatch(session: Session, match: Match): MatchProjection | null {
    if (![match.first, match.second].includes(session.actor)) return null;
    const target = match.first === session.actor ? match.second : match.first;
    const identity = this.identities.find(value => value.account_uuid === target);
    // Capture the concrete record revision before any callback-capable target/owner read.
    const targetGuard = identity ? this.discovery.captureAccountRecord(identity.account_id) : null;
    if (identity && !targetGuard) return null;
    const owner = this.profiles.captureInteractionOwner();
    if (!owner) return null;
    if (identity) { try { this.target(identity.profile_uuid); } catch { return null; } }
    const otherProfile = identity?.profile_uuid ?? (owner.ownerId === target ? owner.profileId : null);
    if (!otherProfile) return null;
    const projection: MatchProjection = freeze({ kind: 'match', match_id: match.id, version: match.version, other_profile_id: otherProfile, state: match.state });
    this.matchProjectionGuards.set(projection, { owner, target: targetGuard, match });
    return this.matchProjectionCurrent(projection) ? projection : null;
  }
  matches(): readonly MatchView[] {
    let session: Session; try { session = this.session(); } catch { return []; }
    this.sourceChanged(false);
    const initial = this.state, authority = this.validateSession(session), captures: InteractionPairCapture[] = [], projections: MatchProjection[] = [];
    const result = [...initial.matches.values()].flatMap(match => {
      const projection = this.projectMatch(session, match); if (!projection) return [];
      projections.push(projection);
      const identity = this.identities.find(value => value.profile_uuid === projection.other_profile_id);
      const pair = identity && match.state === 'active' ? this.pair(identity) : null;
      if (pair) captures.push(pair);
      const facts = pair?.targetFacts;
      const card = facts && pair && interactionPairIsCurrent(pair) ? {
        profile_id: identity!.profile_id, display_name: facts.display_name!, age: pair.candidateAge, summary: facts.summary!,
        compatibility: { status: 'pending' as const, source: 'fixture' as const },
        media_delivery_refs: facts.approved_media!.filter(media => media.state === 'approved' && media.policy_version === 'development-media-1' &&
          media.owner_id === facts.account_id && media.profile_id === facts.profile_id && media.generation === facts.generation &&
          media.delivery_ref !== null && /^fixture-approved-[A-Za-z0-9_-]+$/.test(media.delivery_ref)).map(media => media.delivery_ref!) as [string, ...string[]],
      } : null;
      let safe = card;
      if (safe) {
        try { parseDevelopmentDiscoveryPage({mode:'fixture',contract_version:'gapp-dev-v1',kind:'discovery_page',viewer_id:session.actor,session_id:session.sessionId,discovery_mode:'recommended',queue_id:'match-projection',request_id:'match-projection',state:'ready',items:[safe],next_cursor:null}); } catch { safe = null; }
      }
      return [{ ...projection, profile: safe }];
    });
    // Projection reads may invoke a clock callback that revokes an earlier match.
    if (this.state !== initial || !discoveryViewerIsCurrent(authority.owner) || !captures.every(interactionPairIsCurrent) || !projections.every(projection => this.matchProjectionCurrent(projection)) ||
      [...initial.matches.values()].some(match => match.state === 'active' && !interactionPairIsCurrent(match.source))) return [];
    return freeze(result);
  }
  unmatchIntent(matchId: string, key: string): { session: Session; intent: UnmatchIntent } {
    const session = this.session(), match = [...this.state.matches.values()].find(value => value.id === matchId);
    if (!match || ![match.first, match.second].includes(session.actor)) throw new InteractionFailure('unavailable');
    return { session, intent: { operation: 'unmatch', match_id: matchId, meta: { expected_version: match.version, idempotency_key: key } } };
  }
  block(profile: string, blocked: boolean, key: string): InteractionCommandResult {
    const session = this.session(), target = this.target(profile);
    return this.execute(session, { operation: 'block', target_profile_id: target.profile_uuid, action: blocked ? 'block' : 'unblock',
      meta: { expected_version: this.state.blocks.get(direction(session.actor, target.account_uuid))?.version ?? 0, idempotency_key: key } });
  }
  /** Internal composition only: valid synthetic session, independent of discovery eligibility for revocation. */
  developmentSession(profile: string): Session {
    const authority = this.owner(), target = this.target(profile), facts = this.discovery.inspect(target.account_id)!.facts!;
    if (facts.account_state !== 'active' || facts.session_state !== 'valid') throw new InteractionFailure('unavailable');
    const session = freeze({ actor: target.account_uuid, profileId: target.profile_uuid, sessionId: authority.sessionId });
    sessions.set(session, { authority, reverse: true }); return session;
  }
  /** Labeled test composition acquires the fictional person's own session and executes the same service. */
  reciprocal(profile: string, key: string): InteractionCommandResult {
    const authority = this.owner(), target = this.target(profile), pair = this.pair(target);
    if (!pair || !authority.profileId) throw new InteractionFailure('unavailable');
    const session = this.developmentSession(profile);
    sessions.set(session, { authority, reverse: true, pair });
    if (this.batches.size >= 200) throw new InteractionFailure('capacity');
    const batchId = uuid(0x81, ++this.batchSerial);
    this.batches.set(batchId, { page: null as unknown as DevelopmentDiscoveryPage, actor: session.actor, sessionId: session.sessionId, profileId: authority.profileId, pair });
    return this.execute(session, { operation: 'interaction', action: 'like', target_profile_id: authority.profileId,
      batch_id: batchId, batch_version: 1, meta: { expected_version: this.state.actions.get(direction(session.actor, authority.ownerId))?.version ?? 0, idempotency_key: key } });
  }
  contact(matchId: string): Readonly<{ matchVersion: number; contactVersion: number; eligible: boolean; providerReady: false; canSend: false }> | null {
    this.sourceChanged(false);
    let session: Session; try { session = this.session(); } catch { return null; }
    const match = [...this.state.matches.values()].find(value => value.id === matchId);
    const projection = match ? this.projectMatch(session, match) : null;
    if (!match || !projection || !this.matchProjectionCurrent(projection)) return null;
    const current = this.state.matches.get(pairKey(match.first, match.second));
    return freeze({ matchVersion: current?.version ?? match.version, contactVersion: current?.contactVersion ?? match.contactVersion, eligible: current === match && match.state === 'active' && interactionPairIsCurrent(match.source), providerReady: false, canSend: false });
  }
  inspect() { return freeze({ actions: [...this.state.actions.values()].map(action => ({ id: action.id, actor: action.actor, target: action.target, state: action.state, version: action.version })), matches: [...this.state.matches.values()].map(match => ({ id: match.id, first: match.first, second: match.second, state: match.state, version: match.version, contactVersion: match.contactVersion })), receipts: [...this.state.receipts.values()].map(value => value.receipt), events: [...this.state.events] }); }
  setPolicy(resolved: boolean) { this.policy = resolved; this.discovery.invalidate(); }
  setBeforeCommit(callback: (() => void) | null) { this.beforeCommit = callback; }
}
