import type { DeviceIntent, Error as ApiError, NotificationIntent, NotificationSettings } from '../contracts/generated/gapp-api-v1.ts';
import { validateDeviceIntent, validateNotificationIntent } from '../contracts/generated/validators.js';
import { NotificationTransportError, type NotificationTransport, type SessionHandle, type SessionRelay } from './transport.ts';

/** P05's delivery scenarios, applied to notification requests: offline and a lost response. */
export type NotificationScenario = 'normal' | 'offline' | 'lost_response';
export type EndedBy = 'revoke' | 'logout' | 'transfer';
/** What Glow's API recorded, newest last. No token or token reference is ever recorded. */
export type NotificationEvent = Readonly<
  | { kind: 'session_started' | 'session_ended'; sessionId: string }
  | { kind: 'register' | 'rotate' | 'revoke' | 'settings'; accountId: string; deviceId: string; sessionId: string }
  | { kind: 'refused'; operation: 'settings_read' | 'device' | 'notifications'; code: ApiError['code'] }
  | { kind: 'logout' | 'transfer'; accountId: string; deviceId: string }>;
export type RegistrationView = Readonly<{ accountId: string; deviceId: string; state: 'active' | 'revoked'; version: number;
  sessionId: string; endedBy: EndedBy | null }>;

type Registration = { accountId: string; deviceId: string; state: 'active' | 'revoked'; version: number; sessionId: string;
  reference: string | null; endedBy: EndedBy | null };
type Settings = { match: boolean; message: boolean };
type Receipt = Readonly<{ digest: string; version: number }>;
type Refusal = Readonly<{ refused: ApiError['code']; retryable?: boolean }>;

const CONTRACT_VERSION = 'gapp-api-v1';
/** Bounds for one in-memory fixture session; not product limits. */
export const NOTIFICATION_FIXTURE_LIMITS = Object.freeze({ receipts: 500, events: 200 });
const uuid = (kind: number, value: number) => `${kind.toString(16).padStart(8, '0')}-0000-4000-8000-${value.toString(16).padStart(12, '0')}`;
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
/** A receipt's digest of the canonical intent; the token is folded into it, never kept (FNV-1a, a fixture digest, not cryptography). */
function digest(text: string): string {
  let hash = 0x811c9dc5;
  for (let index = 0; index < text.length; index++) { hash ^= text.charCodeAt(index); hash = Math.imul(hash, 0x01000193) >>> 0; }
  return hash.toString(16).padStart(8, '0');
}

/**
 * In-process substitute for F12 on Glow's API (P06.3, Outcome 3; the semantics of
 * `services/api/glow_domain/notifications.py`, which stays authoritative). It answers the settings
 * read, a `DeviceIntent` and a `NotificationIntent` with the JSON bodies Glow's API will return.
 *
 * - **Per installation.** Each installation's registration for an account is none, active or
 *   revoked; the settings are the account's, both off until changed. `register` from none or revoked
 *   is F12's register; from active for the same account it is F12's rotate. `revoke` needs an active
 *   registration; a settings intent needs the requesting installation's registration active. An
 *   installation active for another account is revoked first, in the same step. A read for an
 *   installation with no registration is an explicit absence (`not_found`).
 * - **Versions.** A registration's version is its installation's view revision: a `DeviceIntent`'s
 *   `expected_version` is 0 for no registration, else that revision; a settings intent's is the
 *   requesting installation's. A settings change advances every registration of the account. A stale
 *   value is `stale_version`; the same key with other content is `idempotency_conflict`; a replay
 *   changes nothing.
 * - **Sessions.** A request names its session (the request's authentication) and installation. Only
 *   a session Glow's API holds as current may act; `started` and `ended` (the `SessionRelay`) are the
 *   stand-in for the sign-in and sign-out reaching it. A session's end is F12's `logout` by the system:
 *   every registration that session made is revoked.
 * - **Custody.** The token is kept only in this fixture's token store under an opaque reference,
 *   which nothing returns, records or shows; it is dropped when its registration ends or rotates.
 *
 * No network, provider, storage or log is involved.
 */
export class FixtureNotificationAdapter implements NotificationTransport, SessionRelay {
  private readonly sessions = new Map<string, Readonly<{ accountId: string; current: boolean }>>();
  private registrations = new Map<string, Registration>();
  private readonly settingsByAccount = new Map<string, Settings>();
  private readonly receipts = new Map<string, Receipt>();
  private readonly tokenStore = new Map<string, string>();
  private readonly listeners = new Set<() => void>();
  private log: NotificationEvent[] = [];
  private serial = 0;
  private references = 0;
  private scenarioValue: NotificationScenario = 'normal';
  readonly subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  private emit() { this.listeners.forEach(listener => listener()); }
  get scenario() { return this.scenarioValue; }
  setScenario(value: NotificationScenario) { this.scenarioValue = value; this.emit(); }

  // -- the session relay: Glow's API learning of a session's start and end -------------------

  started(session: SessionHandle) {
    if (this.sessions.has(session.sessionId)) return;
    this.sessions.set(session.sessionId, Object.freeze({ accountId: session.accountId, current: true }));
    this.record({ kind: 'session_started', sessionId: session.sessionId });
  }
  ended(session: SessionHandle) {
    const known = this.sessions.get(session.sessionId);
    if (!known?.current) return;
    this.sessions.set(session.sessionId, Object.freeze({ ...known, current: false }));
    this.record({ kind: 'session_ended', sessionId: session.sessionId });
    // F12's logout, by the system: the registrations the ending session made.
    for (const registration of this.registrations.values()) {
      if (registration.state === 'active' && registration.sessionId === session.sessionId) {
        this.end(registration, 'logout');
        this.record({ kind: 'logout', accountId: registration.accountId, deviceId: registration.deviceId });
      }
    }
    this.emit();
  }

  // -- the transport: what Glow's API answers ------------------------------------------------

  // Each request resolves its session after its await, in the same step as its command, as the domain does
  // inside each command: a request whose session ended while it waited is refused and changes nothing.
  async settings(session: SessionHandle, deviceId: string): Promise<unknown> {
    await this.gate();
    const accountId = this.capture(session);
    if (!accountId) return this.respond(this.refuse('settings_read', { refused: 'unauthenticated' }));
    const view = this.view(accountId, deviceId);
    return this.respond(view ? this.success(view) : this.refuse('settings_read', { refused: 'not_found' }));
  }
  async device(session: SessionHandle, deviceId: string, intent: DeviceIntent): Promise<unknown> {
    const captured = this.copy(intent);
    await this.gate();
    return this.respond(this.deviceCommand(this.capture(session), session.sessionId, deviceId, captured));
  }
  async notifications(session: SessionHandle, deviceId: string, intent: NotificationIntent): Promise<unknown> {
    const captured = this.copy(intent);
    await this.gate();
    return this.respond(this.settingsCommand(this.capture(session), deviceId, captured));
  }

  /** The session's account if Glow's API holds the session as current now; `null` otherwise. */
  private capture(session: SessionHandle): string | null {
    const known = this.sessions.get(session?.sessionId);
    return known?.current && known.accountId === session.accountId ? known.accountId : null;
  }
  private copy(value: unknown): unknown {
    try { return clone(value); } catch { return null; }
  }
  private async gate() {
    if (this.scenarioValue === 'offline') throw new NotificationTransportError();
    await Promise.resolve();
  }
  /** A lost response commits on the server and then withholds the answer, as P05's scenario does. */
  private respond(body: object): unknown {
    if (this.scenarioValue === 'lost_response') throw new NotificationTransportError();
    return body;
  }
  private requestId() { return uuid(0xf12, ++this.serial); }
  private success(data: NotificationSettings) { return { contract_version: CONTRACT_VERSION, request_id: this.requestId(), data }; }
  private refuse(operation: 'settings_read' | 'device' | 'notifications', refusal: Refusal): ApiError {
    this.record({ kind: 'refused', operation, code: refusal.refused });
    return { contract_version: CONTRACT_VERSION, request_id: this.requestId(), code: refusal.refused, retryable: refusal.retryable ?? false };
  }
  private record(event: NotificationEvent) {
    this.log = [...this.log.slice(1 - NOTIFICATION_FIXTURE_LIMITS.events), Object.freeze(event)];
  }
  private key(accountId: string, deviceId: string) { return `${accountId}|${deviceId}`; }
  private view(accountId: string, deviceId: string): NotificationSettings | null {
    const registration = this.registrations.get(this.key(accountId, deviceId));
    if (!registration) return null;
    const settings = this.settingsByAccount.get(accountId) ?? { match: false, message: false };
    return { kind: 'notifications', version: registration.version, match_notifications: settings.match,
      message_notifications: settings.message, device_state: registration.state };
  }
  private end(registration: Registration, by: EndedBy) {
    if (registration.reference) this.tokenStore.delete(registration.reference);
    registration.state = 'revoked'; registration.version += 1; registration.reference = null; registration.endedBy = by;
  }

  private deviceCommand(accountId: string | null, sessionId: string, deviceId: string, value: unknown): object {
    if (!accountId) return this.refuse('device', { refused: 'unauthenticated' });
    if (!validateDeviceIntent(value)) return this.refuse('device', { refused: 'invalid_request' });
    const intent = value as DeviceIntent;
    if (intent.device_id !== deviceId) return this.refuse('device', { refused: 'forbidden' });
    const receiptKey = `${accountId}|device|${intent.meta.idempotency_key}`;
    const canonical = digest(JSON.stringify([intent.device_id, intent.action, intent.provider_token, intent.meta.expected_version]));
    const receipt = this.receipts.get(receiptKey);
    if (receipt) {
      if (receipt.digest !== canonical) return this.refuse('device', { refused: 'idempotency_conflict' });
      const replay = this.view(accountId, deviceId);
      return replay ? this.success(replay) : this.refuse('device', { refused: 'not_found' });
    }
    if (this.receipts.size >= NOTIFICATION_FIXTURE_LIMITS.receipts) return this.refuse('device', { refused: 'rate_limited', retryable: false });
    const current = this.registrations.get(this.key(accountId, deviceId));
    if (intent.meta.expected_version !== (current?.version ?? 0)) return this.refuse('device', { refused: 'stale_version' });
    if (intent.action === 'revoke') {
      if (!current || current.state !== 'active') return this.refuse('device', { refused: 'state_conflict' });
      this.end(current, 'revoke');
      this.receipts.set(receiptKey, { digest: canonical, version: current.version });
      this.record({ kind: 'revoke', accountId, deviceId, sessionId });
      this.emit();
      return this.success(this.view(accountId, deviceId)!);
    }
    // The token store takes the token before its reference is saved.
    const reference = `fixture-notification-ref-${++this.references}`;
    this.tokenStore.set(reference, intent.provider_token!);
    for (const other of this.registrations.values()) {
      if (other.deviceId === deviceId && other.accountId !== accountId && other.state === 'active') {
        this.end(other, 'transfer');
        this.record({ kind: 'transfer', accountId: other.accountId, deviceId });
      }
    }
    const rotate = current?.state === 'active';
    if (current && rotate && current.reference) this.tokenStore.delete(current.reference);
    const next: Registration = { accountId, deviceId, state: 'active', version: (current?.version ?? 0) + 1, sessionId, reference, endedBy: null };
    this.registrations = new Map(this.registrations).set(this.key(accountId, deviceId), next);
    this.receipts.set(receiptKey, { digest: canonical, version: next.version });
    this.record({ kind: rotate ? 'rotate' : 'register', accountId, deviceId, sessionId });
    this.emit();
    return this.success(this.view(accountId, deviceId)!);
  }

  private settingsCommand(accountId: string | null, deviceId: string, value: unknown): object {
    if (!accountId) return this.refuse('notifications', { refused: 'unauthenticated' });
    if (!validateNotificationIntent(value)) return this.refuse('notifications', { refused: 'invalid_request' });
    const intent = value as NotificationIntent;
    const receiptKey = `${accountId}|notifications|${intent.meta.idempotency_key}`;
    const canonical = digest(JSON.stringify([deviceId, intent.match_notifications, intent.message_notifications, intent.meta.expected_version]));
    const receipt = this.receipts.get(receiptKey);
    if (receipt) {
      if (receipt.digest !== canonical) return this.refuse('notifications', { refused: 'idempotency_conflict' });
      const replay = this.view(accountId, deviceId);
      return replay ? this.success(replay) : this.refuse('notifications', { refused: 'not_found' });
    }
    if (this.receipts.size >= NOTIFICATION_FIXTURE_LIMITS.receipts) return this.refuse('notifications', { refused: 'rate_limited', retryable: false });
    const current = this.registrations.get(this.key(accountId, deviceId));
    // F12 lists settings from active only.
    if (!current || current.state !== 'active') return this.refuse('notifications', { refused: 'state_conflict' });
    if (intent.meta.expected_version !== current.version) return this.refuse('notifications', { refused: 'stale_version' });
    this.settingsByAccount.set(accountId, { match: intent.match_notifications, message: intent.message_notifications });
    for (const registration of this.registrations.values()) if (registration.accountId === accountId) registration.version += 1;
    this.receipts.set(receiptKey, { digest: canonical, version: current.version });
    this.record({ kind: 'settings', accountId, deviceId, sessionId: current.sessionId });
    this.emit();
    return this.success(this.view(accountId, deviceId)!);
  }

  // -- inspection for tests and the labelled controls; no token or reference -----------------

  events(): readonly NotificationEvent[] { return this.log; }
  registrationsView(): readonly RegistrationView[] {
    return [...this.registrations.values()].map(registration => Object.freeze({ accountId: registration.accountId, deviceId: registration.deviceId,
      state: registration.state, version: registration.version, sessionId: registration.sessionId, endedBy: registration.endedBy }));
  }
  settingsOf(accountId: string): Readonly<Settings> { return Object.freeze({ ...(this.settingsByAccount.get(accountId) ?? { match: false, message: false }) }); }
  /** How many tokens the fixture's store holds. */
  get heldTokens() { return this.tokenStore.size; }
  isCurrent(sessionId: string) { return this.sessions.get(sessionId)?.current === true; }
}
