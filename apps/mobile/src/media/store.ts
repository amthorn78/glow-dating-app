import type { MediaCollection, MediaIntent } from '../contracts/generated/gapp-api-v1.ts';
import { parseAppIntent, parseAppResponse } from '../contracts/production.ts';
import { activeOwner, PROFILE_REQUEST_ID, type ProfileAuthority } from '../profiles/policy.ts';
import { createMediaAdapter, type MediaAdapter, type MediaContext, type MediaOutcome,
  type MediaResult, type MediaTransport } from './fixture-adapter.ts';
import { FIXTURE_MEDIA_POLICY, inspectSelection, type MediaSelection } from './policy.ts';

export interface MediaSnapshot {
  readonly ownerKey: string;
  readonly collection: MediaCollection;
  readonly transports: MediaTransport[];
  readonly selection: { selectionId: string; name: string; declaredMime: string; byteLength: number } | null;
  readonly selectionRevision: number;
  readonly policyVersion: string | null;
  readonly busy: boolean;
  readonly error: string | null;
  readonly message: string | null;
}
const copy = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
const equal = (a: unknown, b: unknown): boolean => JSON.stringify(a) === JSON.stringify(b);
function freeze<T>(value: T): T {
  if (value && typeof value === 'object') { Object.values(value).forEach(freeze); Object.freeze(value); }
  return value;
}
const emptyCollection = (): MediaCollection => ({ kind: 'media_collection', version: 1, items: [] });
type Options = { isDevelopment: boolean; mode: string | undefined; pause?: () => Promise<void>; now?: () => number };

/** Owner presentation around the staged fixture authority. No bytes or grants enter UI snapshots. */
export class MediaStore {
  private authority: ProfileAuthority = { ownerId: null, generation: 0, accountVersion: 0,
    accountState: 'none', sessionState: 'none', adult: false, consentCurrent: false, sourceRevision: 0, consentRevision: 'none' };
  private adapter: MediaAdapter;
  private listeners = new Set<() => void>();
  private sequence = 0;
  private operation = 0;
  private selection: MediaSelection | null = null;
  private clockOffset = 0;
  private pending = new Map<string, { signature: string; intent: MediaIntent }>();
  private ownerRemovalRevocations = new Set<string>();
  private moderationRevocations = new Set<string>();
  private evidenceSignature = '';
  private onEvidence: (collection: MediaCollection, policyVersion: string | null) => void;
  private snapshot: MediaSnapshot = freeze({ ownerKey: 'none:0', collection: emptyCollection(), transports: [],
    selection: null, selectionRevision: 0, policyVersion: null, busy: false, error: null, message: null });

  constructor(options: Options, onEvidence: (collection: MediaCollection, policyVersion: string | null) => void = () => {}, adapter?: MediaAdapter) {
    if (!options.isDevelopment || options.mode !== 'fixture') throw new Error('Media requires the explicit development fixture runtime.');
    const now = options.now ?? (() => Date.parse('2026-09-23T12:00:00Z'));
    this.adapter = adapter ?? createMediaAdapter({ ...options, now: () => now() + this.clockOffset });
    this.onEvidence = onEvidence;
  }
  readonly getSnapshot = () => this.snapshot;
  readonly subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  private policyVersion(): string | null {
    try { return this.adapter.context().policyVersion; } catch { return null; }
  }
  private publish(patch: Partial<MediaSnapshot> = {}): void {
    const records = this.adapter.inspect();
    const accessible = activeOwner(this.authority);
    this.snapshot = freeze({ ...this.snapshot, ...copy(patch),
      collection: accessible ? records.collection : emptyCollection(), transports: accessible ? records.transports : [],
      policyVersion: accessible ? this.policyVersion() : null });
    const evidence = this.approvedCollection();
    const signature = JSON.stringify([this.snapshot.ownerKey, evidence, this.snapshot.policyVersion]);
    if (signature !== this.evidenceSignature) {
      this.evidenceSignature = signature;
      this.onEvidence(evidence, this.snapshot.policyVersion);
    }
    this.listeners.forEach(listener => listener());
  }
  /** Pending removal revokes delivery immediately, even if its acknowledgment fails. */
  approvedCollection(): MediaCollection {
    return { ...copy(this.snapshot.collection), items: this.snapshot.policyVersion === FIXTURE_MEDIA_POLICY.version &&
      activeOwner(this.authority) && this.authority.adult && this.authority.consentCurrent ?
      this.snapshot.collection.items.filter(item => item.state === 'approved' && item.approved_delivery_ref &&
        !this.ownerRemovalRevocations.has(item.asset_id) && !this.moderationRevocations.has(item.asset_id)).map(copy) : [] };
  }
  synchronize(authority: ProfileAuthority): void {
    if (equal(authority, this.authority)) return;
    const replaced = authority.ownerId !== this.authority.ownerId || authority.generation !== this.authority.generation;
    this.adapter.cancelPending(); this.operation += 1;
    this.adapter.synchronize(authority); this.authority = copy(authority); this.pending.clear();
    this.selection = null;
    // The adapter retains asset identity through same-owner/generation authority
    // loss. Keep its outstanding revocations until that identity is replaced.
    if (replaced) { this.ownerRemovalRevocations.clear(); this.moderationRevocations.clear(); }
    this.publish({ ownerKey: `${authority.ownerId ?? 'none'}:${authority.generation}`, selection: null,
      selectionRevision: this.snapshot.selectionRevision + 1, busy: false, error: null, message: null });
  }
  private owns(revision: number, ownerKey: string): boolean {
    return activeOwner(this.authority) && revision === this.snapshot.selectionRevision && ownerKey === this.snapshot.ownerKey;
  }
  select(selection: MediaSelection, revision = this.snapshot.selectionRevision, ownerKey = this.snapshot.ownerKey): void {
    if (!this.owns(revision, ownerKey) || this.snapshot.busy) return;
    try {
      inspectSelection(selection);
      this.selection = copy(selection);
      this.publish({ selection: { selectionId: selection.selectionId, name: selection.name,
        declaredMime: selection.declaredMime, byteLength: selection.bytes.length },
      selectionRevision: this.snapshot.selectionRevision + 1, error: null, message: 'Photo selected for this session. It is private and has not been uploaded.' });
    } catch { this.selection = null; this.publish({ selection: null, selectionRevision: this.snapshot.selectionRevision + 1,
      error: 'This image is unsupported, invalid or exceeds the development limits.', message: null }); }
  }
  selectionResult(result: 'denied' | 'limited' | 'cancelled' | 'unsupported', revision = this.snapshot.selectionRevision, ownerKey = this.snapshot.ownerKey): void {
    if (!this.owns(revision, ownerKey)) return;
    // The same control remains available while a grant is being prepared.
    // Cancelling must invalidate that captured selection, not just its label.
    this.operation += 1; this.adapter.cancelPending();
    this.selection = null;
    this.publish({ selection: null, selectionRevision: this.snapshot.selectionRevision + 1, busy: false, error: null,
      message: { denied: 'Photo access was denied. You can try the picker again.', limited: 'Photo access is limited to the items you choose.',
        cancelled: 'Photo selection cancelled.', unsupported: 'This selection cannot be processed in the current development runtime.' }[result] });
  }
  private intent(action: MediaIntent['action'], version: number, assetId: string | null, order: string[], binding: unknown = null): MediaIntent {
    const signature = JSON.stringify([action, version, assetId, order, binding]);
    const slot = `${action}:${assetId ?? 'collection'}`;
    const prior = this.pending.get(slot);
    if (prior?.signature === signature) return copy(prior.intent);
    const intent: MediaIntent = { operation: 'media', action, asset_id: assetId, ordered_asset_ids: [...order],
      meta: { idempotency_key: `media-command:${++this.sequence}`, expected_version: version } };
    parseAppIntent(intent); this.pending.set(slot, { signature, intent: copy(intent) }); return intent;
  }
  private validate(result: MediaResult): void {
    parseAppResponse({ contract_version: 'gapp-api-v1', request_id: PROFILE_REQUEST_ID, data: result.collection });
    if (result.grant) parseAppResponse({ contract_version: 'gapp-api-v1', request_id: PROFILE_REQUEST_ID, data: result.grant });
    if (Object.keys(result).some(key => !['collection', 'transports', 'grant'].includes(key)) || !Array.isArray(result.transports)) throw new Error('Invalid media records');
  }
  private async run(work: (context: MediaContext) => Promise<MediaResult>, message: string, read = false, accepted?: () => void): Promise<void> {
    if (this.snapshot.busy) return;
    let context: MediaContext;
    try { context = this.adapter.context(); } catch { this.publish({ error: 'A current account is required.', message: null }); return; }
    const operation = ++this.operation, ownerKey = this.snapshot.ownerKey;
    this.publish({ busy: true, error: null, message: null });
    try {
      const promise = work(context);
      this.publish(); // Transport starts synchronously; lifecycle remains staged.
      const result = await promise;
      if (operation !== this.operation || ownerKey !== this.snapshot.ownerKey) return;
      this.validate(result);
      if (read) {
        const actual = this.adapter.inspect();
        if (!equal(result.collection, actual.collection) || !equal(result.transports, actual.transports) || result.grant !== null) throw new Error('Invalid read');
      } else this.adapter.acknowledge(context, result);
      accepted?.();
      this.publish({ message });
    } catch (error) {
      if (operation !== this.operation || ownerKey !== this.snapshot.ownerKey) return;
      this.adapter.cancelPending();
      this.publish({ error: error instanceof Error && error.name === 'MediaFailure' ? error.message :
        'The media response could not be accepted. Reload current photo status before retrying.', message: null });
    } finally { if (operation === this.operation && ownerKey === this.snapshot.ownerKey) this.publish({ busy: false }); }
  }
  async requestUpload(outcome: MediaOutcome = 'success'): Promise<void> {
    if (!this.selection || this.snapshot.busy) return;
    const selection = copy(this.selection), intent = this.intent('request_upload', this.snapshot.collection.version, null, [], selection);
    await this.run(context => this.adapter.requestUpload(context, intent, selection, outcome), 'Private upload prepared. Choose Upload photo to transfer the synthetic bytes.', false, () => {
      this.selection = null; this.snapshot = freeze({ ...this.snapshot, selection: null, selectionRevision: this.snapshot.selectionRevision + 1 });
    });
  }
  async upload(assetId: string, outcome: MediaOutcome = 'success'): Promise<void> {
    await this.run(context => this.adapter.upload(context, assetId, outcome), 'Upload received in quarantine. Review is still required.');
  }
  async cancel(assetId: string): Promise<void> {
    try { this.adapter.cancelUpload(this.adapter.context(), assetId); } catch { return; }
    this.operation += 1; this.adapter.cancelPending(); this.publish({ busy: false });
    await this.remove(assetId);
  }
  async remove(assetId: string, outcome: MediaOutcome = 'success'): Promise<void> {
    const asset = this.snapshot.collection.items.find(item => item.asset_id === assetId);
    if (!asset || asset.state === 'removed' || asset.state === 'removal_pending') return;
    this.operation += 1; this.adapter.cancelPending(); this.ownerRemovalRevocations.add(assetId); this.publish({ busy: false });
    const intent = this.intent('remove', asset.version, assetId, []);
    await this.run(context => this.adapter.remove(context, intent, outcome), 'Photo removed from delivery. Provider purge is pending.');
  }
  async move(assetId: string, direction: -1 | 1, outcome: MediaOutcome = 'success'): Promise<void> {
    const order = this.snapshot.collection.items.filter(item => item.state === 'approved').map(item => item.asset_id);
    const index = order.indexOf(assetId), next = index + direction;
    if (index < 0 || next < 0 || next >= order.length) return;
    [order[index], order[next]] = [order[next]!, order[index]!];
    const intent = this.intent('reorder', this.snapshot.collection.version, null, order);
    await this.run(context => this.adapter.reorder(context, intent, outcome), 'Approved photo order saved for this session.');
  }
  async developerEvent(assetId: string, event: 'review' | 'approve' | 'reject' | 'restrict_media' | 'purged', outcome: MediaOutcome = 'success'): Promise<void> {
    const asset = this.snapshot.collection.items.find(item => item.asset_id === assetId);
    if (!asset) return;
    if (event === 'restrict_media') { this.operation += 1; this.adapter.cancelPending(); this.moderationRevocations.add(assetId); this.publish({ busy: false }); }
    const actor = event === 'review' ? 'system' : event === 'purged' ? 'provider' : 'moderator';
    const policyVersion = this.snapshot.policyVersion ?? 'unknown';
    await this.run(context => this.adapter.event(context, { event, actor, assetId, expectedVersion: asset.version,
      eventId: `media-event-${++this.sequence}`, policyVersion }, outcome), `Synthetic ${actor} event: ${event}.`, false,
    () => { if (event === 'approve') this.moderationRevocations.delete(assetId); });
  }
  async reload(outcome: MediaOutcome = 'success'): Promise<void> { await this.run(context => this.adapter.read(context, outcome), 'Current photo status loaded.', true); }
  seedEligible(): void { this.operation += 1; this.adapter.seedEligible(); this.ownerRemovalRevocations.clear(); this.moderationRevocations.clear();
    this.publish({ busy: false, error: null, message: null }); }
  invalidatePolicy(): void { this.operation += 1; this.adapter.invalidatePolicy(); this.selection = null; this.publish({ busy: false, selection: null,
    selectionRevision: this.snapshot.selectionRevision + 1, message: 'Synthetic media policy changed. Delivery and new uploads are unavailable.' }); }
  advanceClock(milliseconds: number): void {
    if (!Number.isFinite(milliseconds) || milliseconds <= 0) return;
    this.clockOffset += milliseconds; this.publish({ message: 'The synthetic media clock advanced.' });
  }
  restrictApproved(): void {
    // This synchronous synthetic source revocation also defeats retained previews and pending resume.
    this.snapshot.collection.items.filter(item => item.state === 'approved').forEach(item => this.moderationRevocations.add(item.asset_id));
    this.operation += 1; this.adapter.cancelPending(); this.publish({ busy: false });
  }
}
