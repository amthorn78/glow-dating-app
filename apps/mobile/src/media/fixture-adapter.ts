import type { MediaCollection, MediaIntent, MediaLifecycle, MediaUploadGrant } from '../contracts/generated/gapp-api-v1.ts';
import { parseAppIntent, parseAppResponse } from '../contracts/production.ts';
import { activeOwner, FIXTURE_MEDIA_ID, type ProfileAuthority } from '../profiles/policy.ts';
import { FIXTURE_MEDIA_POLICY as POLICY, inspectSelection, type MediaSelection } from './policy.ts';

export type MediaOutcome = 'success' | 'error' | 'malformed' | 'stale' | 'expired' | 'interrupted' | 'wrong_object';
export type MediaContext = Readonly<{ ownerId: string; generation: number; authorityRevision: number; policyVersion: string | null }>;
export type MediaTransport = Readonly<{ assetId: string; status: 'ready' | 'uploading' | 'interrupted' | 'failed' | 'expired' | 'cancelled' | 'complete';
  attempts: number; progress: number; purgeAttempts: number }>;
export type MediaRecords = Readonly<{ collection: MediaCollection; transports: MediaTransport[] }>;
export type MediaResult = MediaRecords & Readonly<{ grant: MediaUploadGrant | null }>;
export type MediaEvent = Readonly<{ event: 'review' | 'approve' | 'reject' | 'restrict_media' | 'purged';
  actor: 'owner' | 'provider' | 'system' | 'moderator'; assetId: string; expectedVersion: number; eventId: string; policyVersion: string }>;
export class MediaFailure extends Error {
  readonly code: 'invalid_request' | 'unauthenticated' | 'forbidden' | 'state_conflict' | 'stale_version' |
    'idempotency_conflict' | 'policy_unresolved' | 'provider_unavailable' | 'grant_expired' | 'retry_limit' | 'interrupted' | 'count_limit';
  constructor(code: MediaFailure['code']) {
    super(({ invalid_request: 'Check the selected photo or action.', unauthenticated: 'Sign in again to manage photos.',
      forbidden: 'This photo action is unavailable for the current account.', state_conflict: 'This action is unavailable in the current photo state.',
      stale_version: 'The photo collection changed. Refresh and try again.', idempotency_conflict: 'This retry has different content. Start a new request.',
      policy_unresolved: 'The current media policy is unavailable.', provider_unavailable: 'The simulated transfer failed. You can retry within the displayed limit.',
      grant_expired: 'This upload grant has expired. Remove this pending photo and select it again for a new grant.',
      retry_limit: 'The development retry limit was reached.', interrupted: 'Transfer interrupted. The pending photo is kept for a retry.',
      count_limit: 'The development photo or retained-history limit was reached.' })[code]);
    this.name = 'MediaFailure';
    this.code = code;
  }
}
/** In-process port. DTOs remain closed; bytes, transport observations and synthetic actor controls are local-only. */
export interface MediaAdapter {
  readonly kind: 'fixture';
  synchronize(authority: ProfileAuthority): void;
  context(): MediaContext;
  inspect(): MediaRecords;
  read(context: MediaContext, outcome?: MediaOutcome): Promise<MediaResult>;
  requestUpload(context: MediaContext, intent: MediaIntent, selection: MediaSelection, outcome?: MediaOutcome): Promise<MediaResult>;
  upload(context: MediaContext, assetId: string, outcome?: MediaOutcome): Promise<MediaResult>;
  remove(context: MediaContext, intent: MediaIntent, outcome?: MediaOutcome): Promise<MediaResult>;
  reorder(context: MediaContext, intent: MediaIntent, outcome?: MediaOutcome): Promise<MediaResult>;
  event(context: MediaContext, event: MediaEvent, outcome?: MediaOutcome): Promise<MediaResult>;
  acknowledge(context: MediaContext, result: MediaResult): void;
  cancelPending(): void;
  cancelUpload(context: MediaContext, assetId: string): void;
  seedEligible(): void;
  invalidatePolicy(): void;
}
type Asset = { lifecycle: MediaLifecycle; selection: MediaSelection | null; grant: MediaUploadGrant | null;
  revoked: boolean; transport: MediaTransport; uploadIdentity: string | null };
type State = { version: number; assets: Asset[] };
type ReceiptClass = 'discretionary' | 'removal' | 'purge';
type Receipt = { canonical: string; result: MediaResult; receiptClass: ReceiptClass };
const copy = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
const REQUEST_ID = '33333333-3333-4333-8333-333333333333';
const blankAuthority = (): ProfileAuthority => ({ ownerId: null, generation: 0, accountVersion: 0,
  accountState: 'none', sessionState: 'none', adult: false, consentCurrent: false, sourceRevision: 0, consentRevision: 'none' });
const validate = (result: MediaResult) => {
  if (!result || Object.keys(result).sort().join(',') !== 'collection,grant,transports') throw new MediaFailure('invalid_request');
  parseAppResponse({ contract_version: 'gapp-api-v1', request_id: REQUEST_ID, data: result.collection });
  if (result.grant) parseAppResponse({ contract_version: 'gapp-api-v1', request_id: REQUEST_ID, data: result.grant });
};
export function createMediaAdapter(options: { isDevelopment: boolean; mode: string | undefined; pause?: () => Promise<void>; now?: () => number }): MediaAdapter {
  if (!options.isDevelopment || options.mode !== 'fixture') throw new Error('Media requires the explicit development fixture runtime.');
  const pause = options.pause ?? (() => Promise.resolve());
  const now = options.now ?? (() => Date.parse('2026-09-23T12:00:00Z'));
  let authority = blankAuthority(), authorityRevision = 0, epoch = 0, serial = 0;
  let policyVersion: string | null = POLICY.version, state: State = { version: 1, assets: [] };
  const receipts = new Map<string, Receipt>();
  let staged: { state: State; result: MediaResult; key: string; canonical: string; epoch: number;
    receiptClass: ReceiptClass; expiresAt?: string; expiresAssetId?: string } | null = null;
  const result = (source = state, grant: MediaUploadGrant | null = null): MediaResult => ({
    collection: { kind: 'media_collection', version: source.version, items: source.assets.map(asset => copy(asset.lifecycle)) },
    transports: source.assets.map(asset => copy(asset.transport)), grant: copy(grant) });
  const check = (context: MediaContext, permission = false) => {
    if (!activeOwner(authority)) throw new MediaFailure('unauthenticated');
    if (context.ownerId !== authority.ownerId || context.generation !== authority.generation) throw new MediaFailure('forbidden');
    if (context.authorityRevision !== authorityRevision || context.policyVersion !== policyVersion) throw new MediaFailure('stale_version');
    if (permission && (policyVersion !== POLICY.version || !authority.adult || !authority.consentCurrent)) {
      throw new MediaFailure(policyVersion !== POLICY.version ? 'policy_unresolved' : 'forbidden');
    }
  };
  const delay = async (context: MediaContext, outcome: MediaOutcome, permission = false) => {
    check(context, permission); const started = epoch;
    await pause();
    if (epoch !== started) throw new MediaFailure('stale_version');
    check(context, permission);
    if (outcome === 'error') throw new MediaFailure('provider_unavailable');
    if (outcome === 'stale') throw new MediaFailure('stale_version');
    if (outcome === 'interrupted') throw new MediaFailure('interrupted');
  };
  const find = (assetId: string, source = state) => {
    const asset = source.assets.find(item => item.lifecycle.asset_id === assetId);
    if (!asset) throw new MediaFailure('forbidden');
    return asset;
  };
  const key = (context: MediaContext, operation: string, id: string) => `${context.ownerId}:${context.generation}:${operation}:${id}`;
  const malformed = (value: MediaResult, outcome: MediaOutcome): MediaResult => {
    const output = copy(value);
    if (outcome === 'malformed') return { ...output, collection: { ...output.collection, private_original: 'forbidden' } } as MediaResult;
    if (outcome === 'wrong_object') output.collection.items = [{ kind: 'media', asset_id: '99999999-9999-4999-8999-999999999999',
      version: 1, state: 'upload_pending', approved_delivery_ref: null }, ...output.collection.items.slice(1)];
    return output;
  };
  const replay = (receiptKey: string, canonical: string, outcome: MediaOutcome) => {
    const prior = receipts.get(receiptKey);
    if (!prior) return null;
    if (prior.canonical !== canonical) throw new MediaFailure('idempotency_conflict');
    if (JSON.stringify(prior.result.collection) !== JSON.stringify(result().collection)) throw new MediaFailure('stale_version');
    if (prior.result.grant) {
      const asset = find(prior.result.grant.asset_id);
      if (asset.revoked || now() >= Date.parse(prior.result.grant.expires_at)) {
        asset.revoked = true; asset.transport = { ...asset.transport, status: 'expired', progress: 0 };
        throw new MediaFailure('grant_expired');
      }
    }
    return malformed({ ...copy(prior.result), transports: result().transports }, outcome);
  };
  const prepare = (next: State, grant: MediaUploadGrant | null, receiptKey: string, canonical: string,
    outcome: MediaOutcome, expiresAt?: string, expiresAssetId?: string, receiptClass: ReceiptClass = 'discretionary') => {
    if (staged) throw new MediaFailure('state_conflict');
    const limit = receiptClass === 'removal' ? POLICY.maxRemovalReceipts : receiptClass === 'purge' ? POLICY.maxPurgeReceipts : POLICY.maxReceipts;
    if ([...receipts.values()].filter(receipt => receipt.receiptClass === receiptClass).length >= limit) throw new MediaFailure('count_limit');
    const output = result(next, grant); validate(output);
    staged = { state: copy(next), result: copy(output), key: receiptKey, canonical, epoch, receiptClass, expiresAt, expiresAssetId };
    return malformed(output, outcome);
  };
  const transition = (asset: Asset, next: MediaLifecycle['state']) => {
    asset.lifecycle = { ...asset.lifecycle, version: asset.lifecycle.version + 1, state: next,
      approved_delivery_ref: next === 'approved' ? `fixture-approved-${asset.lifecycle.asset_id}-v${asset.lifecycle.version + 1}` : null };
  };
  const ownerIntent = (intent: MediaIntent, action: MediaIntent['action']) => {
    parseAppIntent(intent);
    if (intent.operation !== 'media' || intent.action !== action) throw new MediaFailure('invalid_request');
  };
  const canonicalIntent = (intent: MediaIntent) => [intent.operation, intent.action, intent.meta.idempotency_key,
    intent.meta.expected_version, intent.asset_id, [...intent.ordered_asset_ids]];
  const adapter: MediaAdapter = {
    kind: 'fixture',
    synchronize(next) {
      if (JSON.stringify(next) === JSON.stringify(authority)) return;
      adapter.cancelPending(); authorityRevision += 1;
      if (next.ownerId !== authority.ownerId || next.generation !== authority.generation) {
        state = { version: 1, assets: [] }; receipts.clear(); policyVersion = POLICY.version;
      } else {
        for (const asset of state.assets) if (asset.lifecycle.state === 'upload_pending') {
          asset.revoked = true; asset.transport = { ...asset.transport, status: 'cancelled', progress: 0 };
        }
      }
      authority = copy(next);
    },
    context() {
      if (!activeOwner(authority)) throw new MediaFailure('unauthenticated');
      return { ownerId: authority.ownerId!, generation: authority.generation, authorityRevision, policyVersion };
    },
    inspect() { const { collection, transports } = result(); return { collection, transports }; },
    async read(context, outcome = 'success') {
      context = copy(context); await delay(context, outcome);
      return malformed(result(), outcome);
    },
    async requestUpload(context, intent, selection, outcome = 'success') {
      ownerIntent(intent, 'request_upload'); inspectSelection(selection); check(context, true);
      context = copy(context); intent = copy(intent); selection = copy(selection);
      const canonical = JSON.stringify([canonicalIntent(intent), selection.selectionId, selection.name, selection.declaredMime, selection.bytes]),
        receiptKey = key(context, intent.action, intent.meta.idempotency_key);
      await delay(context, outcome, true);
      const prior = replay(receiptKey, canonical, outcome); if (prior) return prior;
      if (intent.meta.expected_version !== state.version) throw new MediaFailure('stale_version');
      if (state.assets.length >= POLICY.maxCollection || state.assets.filter(asset => !['removal_pending', 'removed'].includes(asset.lifecycle.state)).length >= POLICY.maxPhotos) throw new MediaFailure('count_limit');
      serial += 1;
      const assetId = `20000000-0000-4000-8000-${String(serial).padStart(12, '0')}`;
      const grant: MediaUploadGrant = { kind: 'media_upload_grant', asset_id: assetId, grant_ref: `fixture-grant-${serial}`,
        expires_at: new Date(now() + POLICY.grantDurationMs).toISOString().replace(/\.\d{3}Z$/, 'Z') };
      const asset: Asset = { lifecycle: { kind: 'media', asset_id: assetId, version: 1, state: 'upload_pending', approved_delivery_ref: null },
        selection, grant, revoked: false, uploadIdentity: null,
        transport: { assetId, status: 'ready', attempts: 0, progress: 0, purgeAttempts: 0 } };
      return prepare({ version: state.version + 1, assets: [...state.assets, asset] }, grant, receiptKey, canonical, outcome, grant.expires_at, assetId);
    },
    async upload(context, assetId, outcome = 'success') {
      context = copy(context); check(context, true);
      const asset = find(assetId);
      if (asset.lifecycle.state !== 'upload_pending') throw new MediaFailure('state_conflict');
      if (!asset.grant || asset.revoked || now() >= Date.parse(asset.grant.expires_at) || outcome === 'expired') {
        asset.revoked = true; asset.transport = { ...asset.transport, status: 'expired', progress: 0 };
        throw new MediaFailure('grant_expired');
      }
      if (asset.transport.status === 'uploading') throw new MediaFailure('state_conflict');
      if (asset.transport.attempts >= POLICY.maxUploadAttempts) throw new MediaFailure('retry_limit');
      const grant = copy(asset.grant), expectedVersion = asset.lifecycle.version, started = epoch;
      const attempt = asset.transport.attempts + 1, identity = `${grant.grant_ref}:${attempt}`;
      asset.transport = { ...asset.transport, attempts: attempt, status: 'uploading', progress: 35 };
      asset.uploadIdentity = identity;
      try {
        await delay(context, outcome, true);
        const current = find(assetId);
        if (current.uploadIdentity !== identity || current.lifecycle.version !== expectedVersion || current.revoked || current.grant?.grant_ref !== grant.grant_ref) throw new MediaFailure('stale_version');
        if (now() >= Date.parse(grant.expires_at)) { current.revoked = true; throw new MediaFailure('grant_expired'); }
        if (!current.selection) throw new MediaFailure('invalid_request');
        inspectSelection(current.selection);
        const next = copy(state), changed = find(assetId, next);
        transition(changed, 'quarantined'); next.version += 1;
        changed.transport = { ...changed.transport, status: 'complete', progress: 100 };
        changed.revoked = true;
        return prepare(next, null, key(context, 'uploaded', identity), JSON.stringify([assetId, expectedVersion, identity]), outcome, grant.expires_at, assetId);
      } catch (error) {
        if (epoch === started && asset.uploadIdentity === identity) asset.transport = { ...asset.transport,
          status: error instanceof MediaFailure && error.code === 'grant_expired' ? 'expired' : outcome === 'interrupted' ? 'interrupted' : 'failed', progress: 0 };
        throw error;
      }
    },
    async remove(context, intent, outcome = 'success') {
      ownerIntent(intent, 'remove'); context = copy(context); intent = copy(intent);
      await delay(context, outcome);
      const canonical = JSON.stringify(canonicalIntent(intent)), receiptKey = key(context, intent.action, intent.meta.idempotency_key);
      const prior = replay(receiptKey, canonical, outcome); if (prior) return prior;
      const asset = find(intent.asset_id!);
      if (asset.lifecycle.version !== intent.meta.expected_version) throw new MediaFailure('stale_version');
      if (!['upload_pending', 'quarantined', 'review_pending', 'approved', 'rejected'].includes(asset.lifecycle.state)) throw new MediaFailure('state_conflict');
      const next = copy(state), changed = find(intent.asset_id!, next);
      transition(changed, 'removal_pending'); next.version += 1;
      changed.selection = null; changed.revoked = true; changed.grant = null; changed.uploadIdentity = null;
      changed.transport = { ...changed.transport, status: 'cancelled', progress: 0 };
      return prepare(next, null, receiptKey, canonical, outcome, undefined, undefined, 'removal');
    },
    async reorder(context, intent, outcome = 'success') {
      ownerIntent(intent, 'reorder'); context = copy(context); intent = copy(intent);
      await delay(context, outcome);
      const canonical = JSON.stringify(canonicalIntent(intent)), receiptKey = key(context, intent.action, intent.meta.idempotency_key);
      const prior = replay(receiptKey, canonical, outcome); if (prior) return prior;
      if (intent.meta.expected_version !== state.version) throw new MediaFailure('stale_version');
      const approved = state.assets.filter(asset => asset.lifecycle.state === 'approved');
      if (intent.ordered_asset_ids.length !== approved.length || new Set(intent.ordered_asset_ids).size !== approved.length ||
          intent.ordered_asset_ids.some(id => !approved.some(asset => asset.lifecycle.asset_id === id))) throw new MediaFailure('forbidden');
      const next = copy(state), ordered = intent.ordered_asset_ids.map(id => find(id, next));
      for (const asset of ordered) asset.lifecycle = { ...asset.lifecycle, version: asset.lifecycle.version + 1 };
      next.assets = [...ordered, ...next.assets.filter(asset => asset.lifecycle.state !== 'approved')]; next.version += 1;
      return prepare(next, null, receiptKey, canonical, outcome);
    },
    async event(context, event, outcome = 'success') {
      context = copy(context); event = copy(event); check(context);
      if (!/^[A-Za-z0-9._-]{1,96}$/.test(event.eventId)) throw new MediaFailure('invalid_request');
      const definitions = { review: ['system', 'quarantined', 'review_pending'], approve: ['moderator', 'review_pending', 'approved'],
        reject: ['moderator', 'review_pending', 'rejected'], restrict_media: ['moderator', 'approved', 'review_pending'],
        purged: ['provider', 'removal_pending', 'removed'] } as const;
      const definition = definitions[event.event];
      if (!definition || event.actor !== definition[0]) throw new MediaFailure('forbidden');
      const canonical = JSON.stringify([event.event, event.actor, event.assetId, event.expectedVersion, event.eventId, event.policyVersion]),
        receiptKey = key(context, 'event', event.eventId);
      const prior = replay(receiptKey, canonical, outcome); if (prior) return prior;
      const asset = find(event.assetId);
      if (asset.lifecycle.version !== event.expectedVersion) throw new MediaFailure('stale_version');
      if (asset.lifecycle.state !== definition[1]) throw new MediaFailure('state_conflict');
      if (['approve', 'reject', 'restrict_media', 'review'].includes(event.event) && (policyVersion !== POLICY.version || event.policyVersion !== policyVersion)) throw new MediaFailure('policy_unresolved');
      if (event.event === 'purged') {
        if (asset.transport.purgeAttempts >= POLICY.maxPurgeAttempts) throw new MediaFailure('retry_limit');
        asset.transport = { ...asset.transport, purgeAttempts: asset.transport.purgeAttempts + 1 };
      }
      await delay(context, outcome);
      if (asset.lifecycle.version !== event.expectedVersion || asset.lifecycle.state !== definition[1]) throw new MediaFailure('stale_version');
      const next = copy(state), changed = find(event.assetId, next);
      transition(changed, definition[2]); next.version += 1;
      if (event.event === 'purged') { changed.selection = null; changed.grant = null; changed.revoked = true; }
      return prepare(next, null, receiptKey, canonical, outcome, undefined, undefined, event.event === 'purged' ? 'purge' : 'discretionary');
    },
    acknowledge(context, response) {
      check(context); validate(response);
      if (!staged) {
        const current = result();
        if (JSON.stringify(response.collection) !== JSON.stringify(current.collection) || JSON.stringify(response.transports) !== JSON.stringify(current.transports)) throw new MediaFailure('stale_version');
        if (response.grant) {
          const asset = find(response.grant.asset_id);
          if (asset.revoked || JSON.stringify(asset.grant) !== JSON.stringify(response.grant) || now() >= Date.parse(response.grant.expires_at)) throw new MediaFailure('grant_expired');
        }
        return;
      }
      if (staged.epoch !== epoch) throw new MediaFailure('stale_version');
      if (JSON.stringify(staged.result) !== JSON.stringify(response)) throw new MediaFailure('invalid_request');
      if (staged.expiresAt && now() >= Date.parse(staged.expiresAt)) {
        const asset = state.assets.find(item => item.lifecycle.asset_id === staged?.expiresAssetId);
        if (asset) { asset.revoked = true; asset.transport = { ...asset.transport, status: 'expired', progress: 0 }; }
        staged = null; throw new MediaFailure('grant_expired');
      }
      state = staged.state; receipts.set(staged.key, { canonical: staged.canonical, result: copy(staged.result), receiptClass: staged.receiptClass }); staged = null; epoch += 1;
    },
    cancelPending() {
      epoch += 1; staged = null;
      for (const asset of state.assets) if (asset.transport.status === 'uploading') asset.transport = { ...asset.transport, status: 'interrupted', progress: 0 };
    },
    cancelUpload(context, assetId) {
      check(context); const asset = find(assetId);
      if (asset.lifecycle.state !== 'upload_pending') throw new MediaFailure('state_conflict');
      adapter.cancelPending(); asset.revoked = true; asset.uploadIdentity = null;
      asset.transport = { ...asset.transport, status: 'cancelled', progress: 0 };
    },
    seedEligible() {
      check(adapter.context(), true); adapter.cancelPending(); authorityRevision += 1; receipts.clear();
      state = { version: 5, assets: [{ lifecycle: { kind: 'media', asset_id: FIXTURE_MEDIA_ID, version: 4, state: 'approved',
        approved_delivery_ref: `fixture-approved-${FIXTURE_MEDIA_ID}-v4` }, selection: null, grant: null, revoked: true, uploadIdentity: null,
        transport: { assetId: FIXTURE_MEDIA_ID, status: 'complete', attempts: 1, progress: 100, purgeAttempts: 0 } }] };
    },
    invalidatePolicy() { adapter.cancelPending(); policyVersion = null; authorityRevision += 1;
      for (const asset of state.assets) if (asset.lifecycle.state === 'upload_pending') asset.revoked = true;
    },
  };
  return adapter;
}
