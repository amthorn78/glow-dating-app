import type { DevelopmentDiscoveryPage } from '../contracts/generated/gapp-dev-v1.ts';
import { FixtureDiscoveryAdapter, type DiscoveryMode, type DiscoveryScenario } from './fixture-adapter.ts';
import type { ProfileStore } from '../profiles/store.ts';

export type DiscoveryState = Readonly<{ status: 'idle' | 'loading' | 'ready' | 'partial' | 'empty' | 'exhausted' | 'reload_required' | 'error';
  page: DevelopmentDiscoveryPage | null; pageNumber: number; complete: boolean }>;
const initial = (): DiscoveryState => Object.freeze({ status: 'idle', page: null, pageNumber: 0, complete: false });

/** At most two finite queues. Screen navigation resumes accepted pages without replaying a browse action. */
export class DiscoveryStore {
  private mode: DiscoveryMode = 'recommended';
  private generation = 0;
  private requestSequence = 0;
  private states: Record<DiscoveryMode, DiscoveryState> = { recommended: initial(), broader: initial() };
  private accepted: Record<DiscoveryMode, DiscoveryState> = { recommended: initial(), broader: initial() };
  private pending: Record<DiscoveryMode, { refresh: boolean; cursor: string | null } | null> = { recommended: null, broader: null };
  private seen: Record<DiscoveryMode, Set<string>> = { recommended: new Set(), broader: new Set() };
  private timer: ReturnType<typeof setTimeout> | null = null;
  private listeners = new Set<() => void>();
  readonly adapter: FixtureDiscoveryAdapter;
  constructor(profiles: ProfileStore, adapter: FixtureDiscoveryAdapter) {
    this.adapter = adapter;
    const invalidate = () => {
      this.generation += 1;
      for (const mode of ['recommended', 'broader'] as const) {
        const current = this.states[mode];
        if (current.status !== 'idle' && (current.status === 'loading' || !current.page || !adapter.isCurrent(current.page))) {
          this.states[mode] = Object.freeze({ status: 'reload_required', page: null, pageNumber: 0, complete: false });
          this.seen[mode].clear(); this.accepted[mode] = initial(); this.pending[mode] = null;
        }
      }
      this.scheduleExpiry(); this.emit();
    };
    profiles.subscribe(invalidate); adapter.subscribe(invalidate);
  }
  readonly subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  private scheduleExpiry() {
    if (this.timer) clearTimeout(this.timer);
    this.timer = null;
    const pages = Object.values(this.states).flatMap(state => state.page ? [state.page] : []);
    if (!pages.length) return;
    const remaining = Math.min(...pages.map(page => this.adapter.remainingLifetime(page)));
    this.timer = setTimeout(() => {
      this.timer = null;
      this.getSnapshot('recommended'); this.getSnapshot('broader');
      this.scheduleExpiry(); this.emit();
    }, Math.max(1, remaining + 1));
    // Node fixture tests must not stay alive solely for a presentation expiration timer.
    if (typeof this.timer === 'object' && 'unref' in this.timer) this.timer.unref();
  }
  private emit() { this.listeners.forEach(listener => listener()); }
  getSnapshot = (mode: DiscoveryMode): DiscoveryState => {
    const state = this.states[mode];
    if (state.page && !this.adapter.isCurrent(state.page)) {
      this.generation += 1;
      this.states[mode] = Object.freeze({ status: 'reload_required', page: null, pageNumber: 0, complete: false });
      this.seen[mode].clear(); this.accepted[mode] = initial(); this.pending[mode] = null;
    }
    return this.states[mode];
  };
  currentMode() { return this.mode; }
  enter(mode: DiscoveryMode) {
    if (this.mode !== mode) { this.generation += 1; this.mode = mode; }
    // Cancelled loading screens can start their same finite first page again when revisited.
    if (this.states[mode].status === 'idle') void this.load(false);
    else if (this.states[mode].status === 'loading') { const pending = this.pending[mode]; void this.load(pending?.refresh ?? false, pending?.cursor ?? null); }
  }
  async refresh() { await this.load(true); }
  async next() {
    const current = this.getSnapshot(this.mode);
    if (!current.page?.next_cursor || current.status === 'loading') return;
    await this.load(false, current.page.next_cursor);
  }
  scenario(value: DiscoveryScenario) { this.adapter.setScenario(value); }
  invalidate() { this.adapter.invalidate(); }
  private async load(refresh: boolean, cursor: string | null = null) {
    const mode = this.mode, previous = this.accepted[mode], generation = ++this.generation;
    this.pending[mode] = { refresh, cursor };
    const requestId = `request-${++this.requestSequence}`;
    this.states[mode] = Object.freeze({ status: 'loading', page: null, pageNumber: previous.pageNumber, complete: false });
    if (refresh) this.seen[mode].clear();
    this.emit();
    try {
      const page = await this.adapter.request(mode, requestId, cursor, refresh);
      if (this.mode !== mode || this.generation !== generation) return;
      if (page.request_id !== requestId || page.discovery_mode !== mode ||
        cursor !== null && previous.page?.queue_id !== page.queue_id ||
        previous.page && !refresh && (previous.page.viewer_id !== page.viewer_id || previous.page.session_id !== page.session_id)) {
        throw new Error('Discovery response identity changed.');
      }
      if (page.state === 'error' || page.state === 'reload_required') {
        this.states[mode] = Object.freeze({ status: page.state, page: null, pageNumber: 0, complete: false });
      } else if (!this.adapter.isCurrent(page)) {
        this.states[mode] = Object.freeze({ status: 'reload_required', page: null, pageNumber: 0, complete: false });
      } else {
        if (page.items.some(item => this.seen[mode].has(item.profile_id))) throw new Error('Repeated discovery membership.');
        for (const item of page.items) this.seen[mode].add(item.profile_id);
        this.states[mode] = Object.freeze({ status: page.state, page, pageNumber: cursor ? previous.pageNumber + 1 : 1,
          complete: page.next_cursor === null && page.state !== 'empty' });
      }
    } catch {
      if (this.mode !== mode || this.generation !== generation) return;
      this.states[mode] = Object.freeze({ status: 'error', page: null, pageNumber: 0, complete: false });
    }
    this.accepted[mode] = this.states[mode]; this.pending[mode] = null;
    this.scheduleExpiry(); this.emit();
  }
}
