import population from '../../../../packages/contracts/fixtures/discovery-v1.json' with { type: 'json' };
import { FixturePairRepository, FIXTURE_PAIR_POLICY, type BlockState, type ParticipantFacts, type PairPolicy } from '../eligibility/facts.ts';
import { FIXTURE_CLOCK, type FixtureClock } from '../onboarding/policy.ts';
import { discoveryViewerIsCurrent, discoveryViewerToken, type DiscoveryViewerToken, type DiscoveryViewerCapture, type ProfileStore } from '../profiles/store.ts';
import { parseDevelopmentDiscoveryPage } from '../contracts/discovery.ts';
import type { DevelopmentDiscoveryPage, DevelopmentDiscoveryProfile } from '../contracts/generated/gapp-dev-v1.ts';

export type InteractionPairCapture = Readonly<{ viewerId: string; sessionId: string; targetAccountId: string;
  profileHandle: string; candidateAge: number; viewerFacts: ParticipantFacts; targetFacts: ParticipantFacts }>;
const accountGuards = new WeakMap<object, { cell: { revision: number }; revision: number }>();
export function interactionAccountIsCurrent(token: object) { const guard = accountGuards.get(token); return !!guard && guard.cell.revision === guard.revision; }
const interactionGuards = new WeakMap<object, { viewer: object; cell: { revision: number }; revision: number;
  candidate: Guard; identity: Guard; publication: readonly Guard[];
  time: { revision: number }; timeRevision: number; expires: number | null }>();
/** Final comparison invokes no caller-supplied callback or source accessor. */
export function interactionPairIsCurrent(capture: object): boolean {
  const guard = interactionGuards.get(capture);
  return guard !== undefined && guard.cell.revision === guard.revision && currentGuard(guard.candidate) && currentGuard(guard.identity) &&
    guard.publication.every(currentGuard) && guard.time.revision === guard.timeRevision &&
    discoveryViewerIsCurrent(guard.viewer) && (guard.expires === null || nativeNow() < guard.expires);
}
export type DiscoveryMode = 'recommended' | 'broader';
export type DiscoveryScenario = 'normal' | 'empty' | 'pending' | 'unavailable' | 'error' | 'offline';
type Mapping = Readonly<{ account_id: string; state: string; engine_reference: string | null; birth_input_version: string; mapping_version: string }>;
export type DiscoveryRecord = Readonly<{ account_id: string; facts: ParticipantFacts | null; mapping: Mapping | null;
  recommendation_priority: number; provider_state: string; blocks: Readonly<{ viewer: BlockState; candidate: BlockState }> }>;
export const DISCOVERY_LIMITS = Object.freeze({ pageSize: 2, maxCandidates: 20, maxQueues: 2, lifetimeMs: 300_000, attempts: 3 });
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
const freeze = <T>(value: T): T => {
  if (value && typeof value === 'object') { Object.values(value).forEach(freeze); Object.freeze(value); }
  return value;
};
let handleSerial = 0;
// Opaque process-local lookup keys, not credentials or a production signature/encryption scheme.
const handle = (kind: string) => `${kind}-${++handleSerial}-${Math.random().toString(36).slice(2, 10)}`;
const validHandle = (value: unknown): value is string => typeof value === 'string' && !/[\r\n]/.test(value) && /^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$/.test(value);
type Cell = { revision: number };
type Guard = Readonly<{ cell: Cell; revision: number }>;
const currentGuard = (guard: Guard) => guard.cell.revision === guard.revision;
const nativeNow = Date.now;
const timeCells = new WeakMap<FixtureDiscoveryTime, { value: number | null; revision: number }>();
/** Concrete fixture clock: controlled writes participate in the final callback-free comparison. */
export class FixtureDiscoveryTime {
  constructor(milliseconds?: number) { timeCells.set(this, { value: milliseconds ?? null, revision: 0 }); }
  set(milliseconds: number) {
    if (!Number.isFinite(milliseconds)) throw new TypeError('Invalid fixture time.');
    const cell = timeCells.get(this)!; cell.value = milliseconds; cell.revision += 1;
  }
}
const timeValue = (source: FixtureDiscoveryTime) => timeCells.get(source)!.value ?? nativeNow();
type Queue = { cell: Cell; id: string; mode: DiscoveryMode; viewer: DiscoveryViewerToken; revision: number; sharedRevision: number; timeRevision: number; guards: Map<string, Guard>; created: number;
  members: readonly string[]; cursors: Map<string, number>; pages: Map<number, DevelopmentDiscoveryPage> };
export type FixtureProviderRequest = Readonly<{ viewer_id: string; candidate_id: string; viewer_mapping_version: string; candidate_mapping_version: string;
  viewer_birth_input_version: string; candidate_birth_input_version: string; viewer_engine_reference: string; candidate_engine_reference: string;
  eligibility_policy_version: string; fixture_set_version: string; adapter_version: string; engine_contract_version: string; engine_version: string; port_version: string }>;
export type FixtureProviderResult = FixtureProviderRequest & Readonly<{ state: string }>;
type Options = { isDevelopment: boolean; mode: string | undefined; clock?: FixtureClock; time?: FixtureDiscoveryTime;
  pause?: () => Promise<void>; afterMapping?: (accountId: string) => void; provider?: (request: FixtureProviderRequest) => FixtureProviderResult; afterCandidate?: (accountId: string) => void };

/** Presentation substitute for Python's guarded discovery composition; no network or production authority. */
export class FixtureDiscoveryAdapter {
  private readonly profiles: ProfileStore;
  private readonly clock: FixtureClock;
  private readonly timeSource: FixtureDiscoveryTime;
  private readonly pause: () => Promise<void>;
  private readonly afterMapping: (accountId: string) => void;
  private readonly provider: ((request: FixtureProviderRequest) => FixtureProviderResult) | undefined;
  private readonly afterCandidate: (accountId: string) => void;
  private records = new Map<string, DiscoveryRecord>();
  private viewerLink: Mapping | null = null;
  private viewerLinkIdentity: string | null = null;
  private queues = new Map<DiscoveryMode, Queue>();
  private revision = 0;
  private readonly publicationCell = { revision: 0 };
  private readonly profileCells = new Map<string, Cell>();
  private readonly interactionCell = { revision: 0 };
  private consumed: (viewerId: string, profileId: string) => boolean = () => false;
  private sharedRevision = 0;
  private readonly recordCells = new Map<string, Cell>();
  private observedDay: string | null = null;
  private lastNow = -Infinity;
  private policy: PairPolicy | null = FIXTURE_PAIR_POLICY;
  private scenario: DiscoveryScenario = 'normal';
  private listeners = new Set<() => void>();
  private publications = new WeakMap<DevelopmentDiscoveryPage, { queue: Queue; guards: readonly Guard[]; revision: number; queueRevision: number }>();
  readonly calls = { scans: 0, mappings: 0, provider: 0 };
  constructor(profiles: ProfileStore, options: Options) {
    if (!options.isDevelopment || options.mode !== 'fixture') throw new Error('Discovery requires the development fixture runtime.');
    this.profiles = profiles; this.clock = options.clock ?? FIXTURE_CLOCK; this.timeSource = options.time ?? new FixtureDiscoveryTime();
    if (!timeCells.has(this.timeSource)) throw new TypeError('Unregistered fixture clock.');
    this.pause = options.pause ?? (() => Promise.resolve()); this.afterCandidate = options.afterCandidate ?? (() => {});
    this.afterMapping = options.afterMapping ?? (() => {}); this.provider = options.provider;
    for (const record of population.candidates) { this.records.set(record.account_id, freeze(clone(record)) as DiscoveryRecord); this.recordCells.set(record.account_id, { revision: 0 });
      if (record.facts?.profile_id && !this.profileCells.has(record.facts.profile_id)) this.profileCells.set(record.facts.profile_id, { revision: 0 }); }
    let ownerKey = profiles.getSnapshot().ownerKey;
    profiles.subscribe(() => {
      const state = profiles.getSnapshot();
      if (state.ownerKey !== ownerKey || !state.canDiscover) {
        ownerKey = state.ownerKey; this.retireQueues(); this.publications = new WeakMap();
        this.viewerLink = null; this.viewerLinkIdentity = null; this.changed();
      }
    });
  }
  readonly subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  private changed(accountId?: string) { this.revision += 1; this.publicationCell.revision += 1;
    if (accountId) { const cell = this.recordCells.get(accountId) ?? { revision: 0 }; cell.revision += 1; this.recordCells.set(accountId, cell); }
    else { this.sharedRevision += 1; this.interactionCell.revision += 1; }
    for (const queue of this.queues.values()) { queue.pages.clear(); queue.cursors.clear(); }
    this.listeners.forEach(listener => listener()); }
  /** Presentation/filter changes retire discovery work without revoking durable pair authority. */
  private queuesChanged() { this.revision += 1; this.publicationCell.revision += 1; this.sharedRevision += 1;
    for (const queue of this.queues.values()) { queue.pages.clear(); queue.cursors.clear(); }
    this.listeners.forEach(listener => listener()); }
  private retireQueues() { for (const queue of this.queues.values()) queue.cell.revision += 1; this.queues.clear(); }
  /** Synthetic source writers advance even on replacement/restoration with identical values. */
  replace(record: DiscoveryRecord): void {
    if (!this.records.has(record.account_id) && this.records.size >= DISCOVERY_LIMITS.maxCandidates) throw new RangeError('Fixture population is full.');
    const previousProfile = this.records.get(record.account_id)?.facts?.profile_id ?? null;
    const next = freeze(clone(record)), nextProfile = next.facts?.profile_id ?? null;
    this.records.set(record.account_id, next);
    // Ownership changes retire only the old/new profile identities. Removed cells stay invalid
    // through retained captures; the live map contains at most the bounded population's profiles.
    if (previousProfile !== nextProfile) {
      if (previousProfile) {
        const previous = this.profileCells.get(previousProfile); if (previous) previous.revision += 1;
        if (![...this.records.values()].some(row => row.facts?.profile_id === previousProfile)) this.profileCells.delete(previousProfile);
      }
      if (nextProfile) { const cell = this.profileCells.get(nextProfile) ?? { revision: 0 }; cell.revision += 1; this.profileCells.set(nextProfile, cell); }
    }
    this.changed(record.account_id); }
  inspect(accountId: string): DiscoveryRecord | undefined { return this.records.get(accountId); }
  replaceViewerMapping(mapping: Mapping | null) { this.viewerLink = freeze(clone(mapping)); this.changed(); }
  inspectViewerMapping(): Mapping | null { return this.viewerLink; }
  setPolicy(policy: PairPolicy | null) { this.policy = freeze(clone(policy)); this.changed(); }
  setScenario(value: DiscoveryScenario) { this.scenario = value; this.queuesChanged(); }
  invalidate() { this.queuesChanged(); }
  interactionsChanged() { this.queuesChanged(); }
  interactionPolicyChanged() { this.changed(); }
  clear() { this.retireQueues(); this.queuesChanged(); }
  private time() {
    const timestamp = this.clock().getTime(), now = timeValue(this.timeSource);
    const day = Number.isFinite(timestamp) ? new Date(timestamp).toISOString().slice(0, 10) : 'invalid';
    if (day !== this.observedDay || !Number.isFinite(now) || now < this.lastNow) { this.revision += 1; this.publicationCell.revision += 1; this.interactionCell.revision += 1; this.sharedRevision += 1; this.observedDay = day; }
    this.lastNow = now;
    return { timestamp, now };
  }
  private authorityCurrent(queue: Queue, now: number): boolean {
    const latest = timeValue(this.timeSource);
    return this.queues.get(queue.mode) === queue && this.sharedRevision === queue.sharedRevision &&
      timeCells.get(this.timeSource)!.revision === queue.timeRevision && discoveryViewerIsCurrent(queue.viewer) &&
      Number.isFinite(now) && now >= queue.created && latest >= queue.created && latest - queue.created < DISCOVERY_LIMITS.lifetimeMs;
  }
  private pureCurrent(queue: Queue, now: number): boolean { return this.revision === queue.revision && this.authorityCurrent(queue, now); }
  private candidateCurrent(queue: Queue, accountId: string, now: number) {
    const guard = queue.guards.get(accountId);
    return guard !== undefined && currentGuard(guard) && this.authorityCurrent(queue, now);
  }
  remainingLifetime(page: DevelopmentDiscoveryPage): number {
    const publication = this.publications.get(page);
    return publication ? Math.max(0, DISCOVERY_LIMITS.lifetimeMs - (timeValue(this.timeSource) - publication.queue.created)) : 0;
  }
  /** Finish all callback-capable time/source reads before the pure retained-cell comparison. */
  isCurrent(page: DevelopmentDiscoveryPage): boolean {
    const publication = this.publications.get(page);
    if (!publication) return false;
    const { queue, guards, revision } = publication;
    const time = this.time();
    const fresh = this.profiles.captureDiscoveryViewer();
    return fresh !== null && fresh.facts.account_id === queue.viewer.viewerId && fresh.sessionId === queue.viewer.sessionId && this.authorityCurrent(queue, time.now) && guards.every(currentGuard) &&
      revision === this.revision;
  }
  /** Retained source guard for target existence; safety commands do not require target eligibility. */
  captureAccountRecord(accountId: string): object | null {
    const row = this.records.get(accountId), cell = this.recordCells.get(accountId);
    if (!cell || row?.facts?.account_id !== accountId) return null;
    const token = Object.freeze({}); accountGuards.set(token, { cell, revision: cell.revision }); return token;
  }
  captureAccountSession(accountId: string): object | null {
    const row = this.records.get(accountId), cell = this.recordCells.get(accountId);
    if (!cell || row?.facts?.account_id !== accountId || row.facts.account_state !== 'active' || row.facts.session_state !== 'valid') return null;
    const token = Object.freeze({}); accountGuards.set(token, { cell, revision: cell.revision }); return token;
  }
  bindConsumption(source: (viewerId: string, profileId: string) => boolean) { this.consumed = source; this.queuesChanged(); }
  /** App-owned mapping acquisition and eligibility, without chart/provider evaluation. */
  captureInteractionPair(profileHandle: string): InteractionPairCapture | null {
    const current = this.time();
    const revision = this.interactionCell.revision, timeRevision = timeCells.get(this.timeSource)!.revision;
    const viewer = this.profiles.captureDiscoveryViewer();
    if (!viewer || !viewer.policy || !this.policy) return null;
    const rows = [...this.records.values()].filter(row => row.facts?.profile_id === profileHandle);
    if (rows.length !== 1 || !rows[0]!.facts) return null;
    const row = rows[0]!, candidateCell = this.recordCells.get(row.account_id), identityCell = this.profileCells.get(profileHandle);
    if (!candidateCell || !identityCell) return null;
    const candidate = { cell: candidateCell, revision: candidateCell.revision }, identity = { cell: identityCell, revision: identityCell.revision };
    const repository = new FixturePairRepository(() => new Date(current.timestamp));
    repository.setPolicy(this.policy); repository.put(viewer.facts); repository.put(row.facts!);
    repository.observeBlock(viewer.facts.account_id, row.account_id, row.blocks.viewer);
    repository.observeBlock(row.account_id, viewer.facts.account_id, row.blocks.candidate);
    const decision = repository.evaluate(viewer.facts.account_id, row.account_id);
    if (decision.state !== 'ready' || decision.candidateAge == null || !currentGuard(candidate) || !currentGuard(identity) ||
      revision !== this.interactionCell.revision || timeRevision !== timeCells.get(this.timeSource)!.revision || !discoveryViewerIsCurrent(viewer)) return null;
    const capture = freeze({ viewerId: viewer.facts.account_id, sessionId: viewer.sessionId, targetAccountId: row.account_id,
      profileHandle, candidateAge: decision.candidateAge, viewerFacts: viewer.facts, targetFacts: row.facts! });
    interactionGuards.set(capture, { viewer, cell: this.interactionCell, revision, candidate, identity, publication: [], time: timeCells.get(this.timeSource)!, timeRevision, expires: null });
    return capture;
  }
  authorizeInteraction(page: DevelopmentDiscoveryPage, profileHandle: string): InteractionPairCapture | null {
    if (!this.isCurrent(page) || !page.items.some(item => item.profile_id === profileHandle)) return null;
    const capture = this.captureInteractionPair(profileHandle), publication = this.publications.get(page);
    if (!capture || !publication || page.viewer_id !== capture.viewerId || page.session_id !== capture.sessionId) return null;
    const guard = interactionGuards.get(capture)!;
    guard.publication = [{ cell: this.publicationCell, revision: publication.revision }, { cell: publication.queue.cell, revision: publication.queueRevision }];
    // Native clock captures wall-clock expiry; controlled test clocks bind their retained revision.
    const source = timeCells.get(this.timeSource)!;
    if (source.value === null) guard.expires = publication.queue.created + DISCOVERY_LIMITS.lifetimeMs;
    return capture;
  }
  private response(mode: DiscoveryMode, requestId: string, viewer: DiscoveryViewerCapture | null,
    state: DevelopmentDiscoveryPage['state'], queue: Queue | null = null, items: DevelopmentDiscoveryProfile[] = [], cursor: string | null = null): DevelopmentDiscoveryPage {
    const result = freeze(parseDevelopmentDiscoveryPage({ mode: 'fixture', contract_version: 'gapp-dev-v1', kind: 'discovery_page',
      viewer_id: viewer?.facts.account_id ?? 'unavailable-viewer', session_id: viewer?.sessionId ?? 'unavailable-session',
      discovery_mode: mode, queue_id: queue?.id ?? null, request_id: requestId, state, items, next_cursor: cursor }));
    if (queue) this.publications.set(result, { queue, revision: this.revision, queueRevision: queue.cell.revision, guards: items.map(item => queue.guards.get(queue.members.find(id => this.records.get(id)?.facts?.profile_id === item.profile_id)!)!).filter(Boolean) });
    return result;
  }
  async request(mode: DiscoveryMode, requestId: string, cursor: string | null, refresh = false): Promise<DevelopmentDiscoveryPage> {
    if (!['recommended', 'broader'].includes(mode) || !validHandle(requestId) ||
      cursor !== null && !validHandle(cursor) || typeof refresh !== 'boolean' || refresh && cursor !== null) {
      throw new TypeError('Invalid discovery request.');
    }
    const opening = this.time(), viewer = this.profiles.captureDiscoveryViewer();
    if (!viewer || !viewer.policy || !this.policy || !discoveryViewerIsCurrent(viewer)) return this.response(mode, requestId, viewer, 'reload_required');
    // Bind the corpus's fixed fictional link explicitly to this synthetic owner/session.
    // Removal/restoration is a writer event. Reads never repair a removed link in that session.
    const linkIdentity = `${viewer.facts.account_id}:${viewer.sessionId}:${viewer.facts.source_id}`;
    if (linkIdentity !== this.viewerLinkIdentity) {
      this.viewerLinkIdentity = linkIdentity;
      this.viewerLink = freeze({ ...population.viewer.mapping, account_id: viewer.facts.account_id });
      this.revision += 1; this.publicationCell.revision += 1; this.sharedRevision += 1;
    }
    const revision = this.revision;
    if (this.scenario === 'error' || this.scenario === 'offline') {
      await this.pause();
      return this.response(mode, requestId, viewer, 'error');
    }
    let queue = this.queues.get(mode), offset = 0;
    if (refresh || !queue && cursor === null) {
      const repository = new FixturePairRepository(() => new Date(opening.timestamp));
      repository.setPolicy(this.policy); repository.put(viewer.facts);
      // Selection inspects at most twenty records, without refill or all-pairs work.
      const selected: DiscoveryRecord[] = [];
      for (const row of this.records.values()) { selected.push(row); if (selected.length === DISCOVERY_LIMITS.maxCandidates) break; }
      const eligible: DiscoveryRecord[] = [];
      for (const record of selected) {
        this.calls.scans += 1;
        if (record.facts) repository.put(record.facts);
        repository.observeBlock(viewer.facts.account_id, record.account_id, record.blocks.viewer);
        repository.observeBlock(record.account_id, viewer.facts.account_id, record.blocks.candidate);
        if (repository.evaluate(viewer.facts.account_id, record.account_id).state === 'ready' && !this.consumed(viewer.facts.account_id, record.facts!.profile_id!)) eligible.push(record);
      }
      eligible.sort((a, b) => (mode === 'recommended' ? a.recommendation_priority - b.recommendation_priority : 0) ||
        (a.facts!.profile_id! < b.facts!.profile_id! ? -1 : a.facts!.profile_id! > b.facts!.profile_id! ? 1 : 0));
      if (revision !== this.revision || !discoveryViewerIsCurrent(viewer)) return this.response(mode, requestId, viewer, 'reload_required');
      if (queue) queue.cell.revision += 1;
      queue = { cell: { revision: 0 }, id: handle('queue'), mode, viewer: discoveryViewerToken(viewer), revision, sharedRevision: this.sharedRevision, timeRevision: timeCells.get(this.timeSource)!.revision,
        guards: new Map(eligible.map(row => { const cell = this.recordCells.get(row.account_id)!; return [row.account_id, { cell, revision: cell.revision }]; })), created: opening.now,
        members: this.scenario === 'empty' ? [] : eligible.map(record => record.account_id), cursors: new Map(), pages: new Map() };
      this.queues.set(mode, queue);
    } else if (!queue || !this.pureCurrent(queue, opening.now) || queue.viewer.viewerId !== viewer.facts.account_id ||
      queue.viewer.sessionId !== viewer.sessionId || cursor !== null && !queue.cursors.has(cursor)) {
      return this.response(mode, requestId, viewer, 'reload_required');
    }
    if (!queue) return this.response(mode, requestId, viewer, 'reload_required');
    if (cursor !== null) offset = queue.cursors.get(cursor)!;
    await this.pause();
    const resumed = this.time(), fresh = this.profiles.captureDiscoveryViewer();
    if (!fresh || fresh.facts.account_id !== queue.viewer.viewerId || fresh.sessionId !== queue.viewer.sessionId || !this.pureCurrent(queue, resumed.now)) return this.response(mode, requestId, viewer, 'reload_required');
    const retained = queue.pages.get(offset);
    if (retained) {
      if (!this.isCurrent(retained)) return this.response(mode, requestId, viewer, 'reload_required');
      return this.response(mode, requestId, viewer, retained.state, queue, [...retained.items], retained.next_cursor);
    }
    const repository = new FixturePairRepository(() => new Date(resumed.timestamp));
    repository.setPolicy(this.policy); repository.put(viewer.facts);
    let items: DevelopmentDiscoveryProfile[] = [];
    const projected = new Map<string, string>();
    let partial = false;
    for (const accountId of queue.members.slice(offset, offset + DISCOVERY_LIMITS.pageSize)) {
      if (!this.authorityCurrent(queue, resumed.now)) break;
      if (!this.candidateCurrent(queue, accountId, resumed.now)) { partial = true; continue; }
      const row = this.records.get(accountId);
      if (!row?.facts) { partial = true; continue; }
      repository.put(row.facts); repository.observeBlock(viewer.facts.account_id, accountId, row.blocks.viewer);
      repository.observeBlock(accountId, viewer.facts.account_id, row.blocks.candidate);
      const pair = repository.evaluate(viewer.facts.account_id, accountId);
      if (pair.state !== 'ready') { partial = true; continue; }
      // Eligibility precedes mapping/provider work. No engine request or real chart reference is generated.
      const mapping = (target: string): Mapping | null => {
        this.calls.mappings += 1;
        const found = target === viewer.facts.account_id
          ? this.viewerLink
          : this.records.get(target)?.mapping ?? null;
        this.afterMapping(target);
        return found;
      };
      const left = mapping(viewer.facts.account_id), right = mapping(accountId);
      if (!left || !right || left.account_id !== viewer.facts.account_id || right.account_id !== accountId ||
        left.state !== 'resolved' || right.state !== 'resolved' || !left.engine_reference || !right.engine_reference ||
        left.engine_reference === right.engine_reference ||
        [left.birth_input_version, right.birth_input_version, left.mapping_version, right.mapping_version, left.engine_reference, right.engine_reference]
          .some(value => typeof value !== 'string' || value.length > 128 || !value.trim()) || !this.candidateCurrent(queue, accountId, resumed.now)) { partial = true; continue; }
      const request = freeze({ viewer_id: viewer.facts.account_id, candidate_id: accountId,
        viewer_mapping_version: left.mapping_version, candidate_mapping_version: right.mapping_version,
        viewer_birth_input_version: left.birth_input_version, candidate_birth_input_version: right.birth_input_version,
        viewer_engine_reference: left.engine_reference, candidate_engine_reference: right.engine_reference,
        eligibility_policy_version: pair.version!.policy_version, fixture_set_version: population.version,
        adapter_version: 'development-discovery-1', engine_contract_version: 'fixture-only', engine_version: 'synthetic-engine-1', port_version: 'fixture-provider-1' });
      let outcome = 'unavailable';
      for (let attempt = 0; attempt < DISCOVERY_LIMITS.attempts; attempt += 1) {
        if (!this.candidateCurrent(queue, accountId, resumed.now)) break;
        this.calls.provider += 1;
        const result = this.provider ? this.provider(request) : { ...request,
          state: this.scenario === 'unavailable' ? 'unavailable' : this.scenario === 'pending' ? 'pending' : row.provider_state };
        if (Object.keys(request).some(key => result[key as keyof FixtureProviderRequest] !== request[key as keyof FixtureProviderRequest])) {
          outcome = 'invalid'; break;
        }
        outcome = result.state;
        if (outcome !== 'error') break;
        // Reacquire mappings and eligibility before a transient retry; original queue guards remain bound.
        if (attempt + 1 < DISCOVERY_LIMITS.attempts && this.candidateCurrent(queue, accountId, resumed.now)) {
          const retryLeft = mapping(viewer.facts.account_id), retryRight = mapping(accountId);
          if (!retryLeft || !retryRight || retryLeft.mapping_version !== left.mapping_version || retryRight.mapping_version !== right.mapping_version ||
            retryLeft.engine_reference !== left.engine_reference || retryRight.engine_reference !== right.engine_reference ||
            retryLeft.birth_input_version !== left.birth_input_version || retryRight.birth_input_version !== right.birth_input_version ||
            repository.evaluate(viewer.facts.account_id, accountId).state !== 'ready' || !this.candidateCurrent(queue, accountId, resumed.now)) break;
        }
      }
      partial ||= outcome !== 'ready' && outcome !== 'pending';
      if (!['ready', 'pending', 'unavailable', 'error'].includes(outcome)) continue;
      const age = pair.candidateAge;
      if (age === null || age === undefined || age < 18 || age > 120 || !row.facts.profile_id || !row.facts.display_name || !row.facts.summary) { partial = true; continue; }
      const mediaRefs = row.facts.approved_media!.filter(media => media.state === 'approved' &&
        media.policy_version === 'development-media-1' && media.owner_id === accountId && media.profile_id === row.facts!.profile_id &&
        media.generation === row.facts!.generation && media.delivery_ref !== null && media.delivery_ref.length <= 128 &&
        !/[\r\n]/.test(media.delivery_ref) && /^fixture-approved-[A-Za-z0-9_-]+$/.test(media.delivery_ref)).map(media => media.delivery_ref!);
      if (!mediaRefs.length || mediaRefs.length > 4 || new Set(mediaRefs).size !== mediaRefs.length) { partial = true; continue; }
      items.push({ profile_id: row.facts.profile_id, display_name: row.facts.display_name, age, summary: row.facts.summary,
        compatibility: { status: 'pending', source: 'fixture' }, media_delivery_refs: mediaRefs as [string, ...string[]] });
      projected.set(row.facts.profile_id, accountId);
      this.afterCandidate(accountId);
    }
    const closing = this.time();
    const finalViewer = this.profiles.captureDiscoveryViewer();
    // No source/clock/provider callback follows this final guard, including later candidate callbacks.
    if (!finalViewer || finalViewer.facts.account_id !== queue.viewer.viewerId || finalViewer.sessionId !== queue.viewer.sessionId || !this.authorityCurrent(queue, closing.now)) return this.response(mode, requestId, viewer, 'reload_required');
    const originalCount = items.length;
    items = items.filter(item => this.candidateCurrent(queue!, projected.get(item.profile_id)!, closing.now));
    partial ||= originalCount !== items.length || this.revision !== queue.revision;
    let next: string | null = null;
    if (queue.revision === this.revision && offset + DISCOVERY_LIMITS.pageSize < queue.members.length) { next = handle('cursor'); queue.cursors.set(next, offset + DISCOVERY_LIMITS.pageSize); }
    const state = queue.members.length === 0 ? 'empty' : offset >= queue.members.length ? 'exhausted' : partial ? 'partial' : 'ready';
    const page = this.response(mode, requestId, viewer, state, queue, items, next);
    queue.pages.set(offset, page);
    return page;
  }
}
