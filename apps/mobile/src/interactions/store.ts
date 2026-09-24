import type { InteractionCommandResult } from '../contracts/generated/gapp-api-v1.ts';
import type { DiscoveryMode } from '../discovery/fixture-adapter.ts';
import type { DiscoveryStore } from '../discovery/store.ts';
import { discoveryViewerIsCurrent, type ProfileStore } from '../profiles/store.ts';
import { FixtureInteractionAdapter, InteractionFailure, type CleanupMatchView, type MatchView } from './fixture-adapter.ts';
export type InteractionScenario = 'normal' | 'offline' | 'lost_response' | 'delayed';
export type InteractionState = Readonly<{ status: 'idle' | 'pending' | 'error' | 'committed';
  pending: Readonly<{ profileId: string; action: 'like' | 'pass' | 'unmatch' | 'block' | 'unblock' }> | null;
  error: string | null; message: string | null; canRetry: boolean; matches: readonly MatchView[]; cleanupMatches: readonly CleanupMatchView[];
  selectedMatchId: string | null; scenario: InteractionScenario }>;
type Prepared = ReturnType<FixtureInteractionAdapter['prepare']> | ReturnType<FixtureInteractionAdapter['unmatchIntent']>;
type Submission = { prepared: Prepared; mode: DiscoveryMode | null; profileId: string; action: 'like' | 'pass' | 'unmatch'; owner: string; generation: number };
export class InteractionStore {
  private state: InteractionState = Object.freeze({ status: 'idle', pending: null, error: null, message: null, canRetry: false, matches: [], cleanupMatches: [], selectedMatchId: null, scenario: 'normal' });
  private listeners = new Set<() => void>();
  private sequence = 0;
  private generation = 0;
  private refreshRevision = 0;
  private pending: Submission | null = null;
  private retryable: Submission | null = null;
  private release: (() => void) | null = null;
  private ownerKey: string;
  readonly profiles: ProfileStore;
  readonly discovery: DiscoveryStore;
  readonly adapter: FixtureInteractionAdapter;
  private readonly pause: () => Promise<void>;
  constructor(profiles: ProfileStore, discovery: DiscoveryStore, adapter: FixtureInteractionAdapter,
    pause: () => Promise<void> = () => Promise.resolve()) {
    this.profiles = profiles; this.discovery = discovery; this.adapter = adapter; this.pause = pause;
    this.ownerKey = profiles.getSnapshot().ownerKey;
    profiles.subscribe(() => {
      const key = profiles.getSnapshot().ownerKey;
      if (key !== this.ownerKey || !profiles.captureInteractionOwner()) {
        this.ownerKey = key; this.generation += 1; this.pending = null; this.retryable = null; this.releaseDelayed();
        this.publish({ status: 'idle', pending: null, error: null, message: null, canRetry: false, selectedMatchId: null });
      }
      this.refresh();
    });
    adapter.subscribe(() => this.refresh());
  }
  readonly subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  readonly getSnapshot = () => this.state;
  private publish(patch: Partial<InteractionState>) { this.state = Object.freeze({ ...this.state, ...patch }); this.listeners.forEach(listener => listener()); }
  refresh() {
    const revision = ++this.refreshRevision, authority = this.profiles.captureInteractionCleanupOwner();
    // Acquire private projections last; a nested revocation refresh supersedes this publication.
    const cleanupMatches = authority ? this.adapter.cleanupMatches() : [], matches = authority ? this.adapter.matches() : [];
    if (revision !== this.refreshRevision || authority && !discoveryViewerIsCurrent(authority)) return;
    this.publish({ matches, cleanupMatches, ...(this.state.message === 'Mutual match confirmed.' && !matches.some(match => match.state === 'active') ? { message: 'New contact is unavailable.' } : {}), selectedMatchId: cleanupMatches.some(match => match.match_id === this.state.selectedMatchId) ? this.state.selectedMatchId : null });
  }
  selectMatch(matchId: string) { this.refresh(); this.publish({ selectedMatchId: this.state.cleanupMatches.some(match => match.match_id === matchId) ? matchId : null }); }
  canAct(mode: DiscoveryMode, profileId: string): boolean {
    const page = this.discovery.getSnapshot(mode).page;
    return this.state.status !== 'pending' && !!page && page.items.some(item => item.profile_id === profileId) &&
      this.discovery.adapter.isCurrent(page) && !this.adapter.consumed(page.viewer_id, profileId);
  }
  private key() { return `interaction-command:${++this.sequence}`; }
  async submit(mode: DiscoveryMode, profileId: string, action: 'like' | 'pass') {
    if (this.state.status === 'pending') return;
    const page = this.discovery.getSnapshot(mode).page;
    if (!page) { this.failure(new InteractionFailure('stale')); return; }
    try { const prepared = this.adapter.prepare(page, profileId, action, this.key()); this.retryable = null;
      await this.run({ prepared, mode, profileId, action, owner: this.ownerKey, generation: ++this.generation });
    } catch (error) { this.failure(error); }
  }
  async unmatch(matchId: string) {
    if (this.state.status === 'pending') return;
    try { const prepared = this.adapter.unmatchIntent(matchId, this.key()); this.retryable = null;
      await this.run({ prepared, mode: null, profileId: matchId, action: 'unmatch', owner: this.ownerKey, generation: ++this.generation });
    } catch (error) { this.failure(error); }
  }
  async retry() {
    if (this.state.status === 'pending' || !this.retryable) return;
    if (this.retryable.mode !== null && this.retryable.mode !== this.discovery.currentMode()) {
      this.publish({ status: 'error', error: 'Return to the original discovery mode to retry this request.', pending: null, canRetry: true }); return;
    }
    await this.run({ ...this.retryable, generation: ++this.generation });
  }
  cancelPending() { if (!this.pending) return; this.generation += 1; this.pending = null; this.retryable = null; this.releaseDelayed();
    this.publish({ status: 'idle', pending: null, canRetry: false, error: null, message: null }); }
  private current(submission: Submission) { return this.generation === submission.generation && this.ownerKey === submission.owner && this.pending === submission && (submission.mode === null || submission.mode === this.discovery.currentMode()); }
  private async run(submission: Submission) {
    this.pending = submission;
    this.publish({ status: 'pending', pending: { profileId: submission.profileId, action: submission.action }, error: null, message: null, canRetry: false });
    const scenario = this.state.scenario;
    try {
      if (scenario === 'delayed') await new Promise<void>(resolve => { this.release = resolve; }); else await this.pause();
      if (!this.current(submission)) return;
      if (scenario === 'offline') throw new InteractionFailure('offline');
      const result = this.adapter.execute(submission.prepared.session, submission.prepared.intent);
      if (scenario === 'lost_response') throw new InteractionFailure('offline');
      if (!this.current(submission)) return;
      this.accept(result); this.retryable = null;
    } catch (error) {
      if (!this.current(submission)) return;
      this.retryable = error instanceof InteractionFailure && error.code === 'offline' ? submission : null; this.failure(error);
    } finally {
      if (this.pending === submission) { const current = this.current(submission); this.pending = null;
        this.publish({ pending: null, canRetry: this.retryable !== null, ...(!current ? { status: 'idle' as const } : {}) }); this.refresh(); }
    }
  }
  private accept(result: InteractionCommandResult) {
    const projection = result.current_projection;
    let message = result.receipt.outcome_code === 'unmatched' ? 'Unmatched. New contact is unavailable.' : result.receipt.outcome_code === 'liked' ? 'Like saved.' : 'Pass saved.';
    if (projection?.kind === 'interaction' && projection.match_id) message = 'Mutual match confirmed.';
    if (!projection && result.receipt.outcome_code !== 'unmatched') message = 'Your request was committed. Current access is unavailable.';
    this.publish({ status: 'committed', error: null, message });
  }
  private failure(error: unknown) { this.publish({ status: 'error', error: error instanceof InteractionFailure ? error.message : 'The action could not be confirmed. Reload current state.', message: null, canRetry: this.retryable !== null }); }
  setScenario(scenario: InteractionScenario) { this.publish({ scenario }); }
  releaseDelayed() { const release = this.release; this.release = null; release?.(); }
  developmentReciprocal(profileId: string) {
    try { this.adapter.reciprocal(profileId, this.key()); this.refresh(); this.publish({ status: 'committed', error: null,
      message: this.state.matches.some(match => match.state === 'active') ? 'Mutual match confirmed.' : 'Fictional scenario updated. Only mutual matches are displayed.' });
    } catch (error) { this.failure(error); }
  }
  developmentBlock(profileId: string, blocked: boolean) {
    try { this.adapter.block(profileId, blocked, this.key()); this.refresh(); this.publish({ status: 'committed', error: null,
      message: blocked ? 'Block saved. New contact is unavailable.' : 'Block removed. Previous connections remain unavailable.' });
    } catch (error) { this.failure(error); }
  }
}
