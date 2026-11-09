import type { NotificationSettings } from '../contracts/generated/gapp-api-v1.ts';
import type { OnboardingSnapshot } from '../onboarding/store.ts';
import { NotificationFailure, type NotificationClient, type NotificationFailureCode } from './client.ts';
import type { NotificationKind } from './copy.ts';
import type { PermissionSeam } from './permission.ts';
import type { SessionHandle, SessionRelay } from './transport.ts';

/** The onboarding account the store follows: its snapshot and changes (P06.3, D7). */
export type OwnerSource = Readonly<{ getSnapshot: () => OnboardingSnapshot; subscribe: (listener: () => void) => () => void }>;
/** Where this installation's push token comes from. Its only implementation is a synthetic fixture source (D6). */
export type TokenSource = Readonly<{ next: () => string }>;

export type NotificationState = Readonly<{
  status: 'idle' | 'loading' | 'ready' | 'error';
  /** What the screen shows for this device: both off unless this installation's registration is active. */
  match: boolean;
  message: boolean;
  deviceActive: boolean;
  /** The member's last attempt to turn a kind on was met by a denied permission. */
  denied: boolean;
  busy: boolean;
  error: NotificationFailureCode | null;
}>;
type Options = Readonly<{ owner: OwnerSource; client: NotificationClient; permission: PermissionSeam; tokens: TokenSource;
  sessions: SessionRelay; installation: string }>;

const idle: NotificationState = Object.freeze({ status: 'idle', match: false, message: false, deviceActive: false, denied: false, busy: false, error: null });
const codeOf = (error: unknown): NotificationFailureCode => error instanceof NotificationFailure ? error.code : 'invalid_response';
let keySerial = 0;

/** The current session of an active account, as the onboarding fixture holds it; `null` for any other state. */
export function currentSession(snapshot: OnboardingSnapshot): SessionHandle | null {
  const account = snapshot.account;
  if (!account || account.state !== 'active' || account.session_state !== 'valid') return null;
  return Object.freeze({ accountId: account.account_id, sessionId: `fixture-session-${snapshot.generation}` });
}
const same = (a: SessionHandle | null, b: SessionHandle | null) => a?.accountId === b?.accountId && a?.sessionId === b?.sessionId;

/**
 * The notification settings screen's presentation state (P06.3, Outcome 3). Every result comes
 * through the client boundary; nothing here authorizes anything.
 *
 * - **Turning a kind on** is the only thing that consults the permission seam. While the answer is
 *   undetermined the seam asks once. Granted: the app registers this installation with a synthetic
 *   token unless its registration is already active (F12's register), then saves the settings with
 *   only that kind changed (F12's settings). Denied: nothing is saved and nothing is registered; the
 *   kind stays off and the screen says so in Glow's wording. Turning a kind off saves only that kind.
 * - **Reads.** The screen shows both kinds off unless this installation's registration is active;
 *   an explicit absence means no registration.
 * - **The account** (D7). The store follows the onboarding account, as chat's store does. When the
 *   session it acts for ends by a logout or an account change, it sends this installation's revoke
 *   while Glow's API still holds that session as current, then clears the screen's state; Glow's API
 *   learns of the session's end once the revoke has settled, and its `logout` event revokes whatever
 *   the revoke did not reach. An expired session cannot revoke: its end alone ends its registrations.
 *   A response to a request made for an earlier session changes nothing.
 * - **Custody.** A token exists only inside the register intent it was minted for, kept only to retry
 *   that same intent; it is never in the state, shown or logged.
 */
export class NotificationStore {
  private state: NotificationState = idle;
  private readonly listeners = new Set<() => void>();
  private readonly owner: OwnerSource;
  private readonly client: NotificationClient;
  private readonly permission: PermissionSeam;
  private readonly tokens: TokenSource;
  private readonly sessions: SessionRelay;
  readonly installation: string;
  private session: SessionHandle | null;
  /** Advanced by each change of session: a response to an earlier request is never used. */
  private epoch = 0;
  /** This installation's registration as Glow last answered: its state and view revision. */
  private registration: 'none' | 'active' | 'revoked' = 'none';
  private version = 0;
  private settings: Readonly<{ match: boolean; message: boolean }> = Object.freeze({ match: false, message: false });
  /** A register intent whose response was not received: retried as is, same key and token. */
  private retryRegister: ReturnType<NotificationClient['deviceIntent']> | null = null;
  private ownerScheduled = false;
  constructor(options: Options) {
    this.owner = options.owner; this.client = options.client; this.permission = options.permission; this.tokens = options.tokens;
    this.sessions = options.sessions; this.installation = options.installation;
    this.session = currentSession(this.owner.getSnapshot());
    if (this.session) this.sessions.started(this.session);
    this.owner.subscribe(() => this.ownerChanged());
  }
  readonly subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  readonly getSnapshot = () => this.state;
  private publish(patch: Partial<NotificationState>) { this.state = Object.freeze({ ...this.state, ...patch }); this.listeners.forEach(listener => listener()); }
  private key() { keySerial += 1; return `notifications-${Date.now().toString(36)}-${keySerial}`; }

  /** Adopts a validated answer about this installation. */
  private adopt(settings: NotificationSettings | null) {
    if (!settings) {
      this.registration = 'none'; this.version = 0; this.settings = Object.freeze({ match: false, message: false });
    } else {
      this.registration = settings.device_state; this.version = settings.version;
      this.settings = Object.freeze({ match: settings.match_notifications, message: settings.message_notifications });
    }
    const active = this.registration === 'active';
    this.publish({ status: 'ready', deviceActive: active, match: active && this.settings.match, message: active && this.settings.message });
  }
  private failed(error: unknown) {
    const code = codeOf(error);
    this.publish({ busy: false, error: code, status: this.state.status === 'loading' ? 'error' : this.state.status });
    if (code === 'stale' || code === 'not_active') void this.load(false);
  }

  /** Reads this installation's settings: when the screen is shown, and after a stale answer. */
  async load(clearError = true): Promise<void> {
    const session = this.session, epoch = this.epoch;
    if (!session) { this.publish(idle); return; }
    this.publish({ status: this.state.status === 'ready' ? 'ready' : 'loading', ...(clearError ? { error: null } : {}) });
    try {
      const read = await this.client.read(session, this.installation);
      if (epoch !== this.epoch) return;
      this.adopt(read.status === 'present' ? read.settings : null);
    } catch (error) {
      if (epoch !== this.epoch) return;
      this.publish({ status: 'error', error: codeOf(error) });
    }
  }

  /** The member turns one kind on or off. */
  async setKind(kind: NotificationKind, on: boolean): Promise<void> {
    const session = this.session, epoch = this.epoch;
    if (!session || this.state.busy || this.state.status !== 'ready') return;
    if (!on) {
      // Off: nothing to save while this installation's registration is not active; both already show off.
      if (this.registration !== 'active') return;
      this.publish({ busy: true, error: null, denied: false });
      await this.save(session, epoch, kind, false);
      return;
    }
    this.publish({ busy: true, error: null, denied: false });
    // The only place the permission is consulted: the member's own action of turning a kind on.
    let permission = this.permission.status();
    if (permission === 'undetermined') permission = await this.permission.request();
    if (epoch !== this.epoch) return;
    if (permission !== 'granted') {
      // Denied: nothing is saved and nothing is registered.
      this.publish({ busy: false, denied: true });
      return;
    }
    if (this.registration !== 'active' && !await this.register(session, epoch)) return;
    await this.save(session, epoch, kind, true);
  }

  private async register(session: SessionHandle, epoch: number): Promise<boolean> {
    let intent: ReturnType<NotificationClient['deviceIntent']>;
    try {
      intent = this.retryRegister ?? this.client.deviceIntent(this.installation, 'register', this.tokens.next(), this.version, this.key());
    } catch (error) { this.failed(error); return false; }
    this.retryRegister = intent;
    try {
      const settings = await this.client.device(session, this.installation, intent);
      if (epoch !== this.epoch) return false;
      this.retryRegister = null;
      this.adopt(settings);
      if (settings.device_state === 'active') return true;
      this.publish({ busy: false });
      return false;
    } catch (error) {
      if (epoch !== this.epoch) return false;
      if (!(error instanceof NotificationFailure && error.retryable)) this.retryRegister = null;
      this.failed(error);
      return false;
    }
  }

  private async save(session: SessionHandle, epoch: number, kind: NotificationKind, on: boolean): Promise<void> {
    const next = { ...this.settings, [kind]: on };
    try {
      const intent = this.client.settingsIntent(next.match, next.message, this.version, this.key());
      const settings = await this.client.save(session, this.installation, intent);
      if (epoch !== this.epoch) return;
      this.adopt(settings);
      this.publish({ busy: false });
    } catch (error) {
      if (epoch !== this.epoch) return;
      this.failed(error);
    }
  }

  // -- the account -----------------------------------------------------------------------------

  private ownerChanged() {
    if (this.ownerScheduled) return;
    this.ownerScheduled = true;
    // A sign-out or an expiry reaches the store as two synchronous publications (cleared, then
    // expired), so the store decides on the settled account one microtask later, before any render.
    void Promise.resolve().then(() => { this.ownerScheduled = false; this.followOwner(); });
  }
  private followOwner() {
    const snapshot = this.owner.getSnapshot();
    const next = currentSession(snapshot);
    if (same(next, this.session)) return;
    const previous = this.session;
    const expired = previous !== null && snapshot.account?.account_id === previous.accountId && snapshot.account.session_state === 'expired';
    let revoke: ReturnType<NotificationClient['deviceIntent']> | null = null;
    if (previous !== null && !expired && this.registration === 'active') {
      try { revoke = this.client.deviceIntent(this.installation, 'revoke', null, this.version, this.key()); } catch { revoke = null; }
    }
    this.session = next; this.epoch += 1;
    if (previous && revoke) {
      // Sent now, while Glow's API still holds the session as current; it learns of the end once this settles.
      void this.client.device(previous, this.installation, revoke).catch(() => undefined)
        .finally(() => this.sessions.ended(previous, 'logout'));
    } else if (previous) {
      this.sessions.ended(previous, expired ? 'expired' : 'logout');
    }
    // Then the screen's state is cleared: nothing of the earlier session is retained.
    this.clear();
    if (next) this.sessions.started(next);
  }
  private clear() {
    this.registration = 'none'; this.version = 0; this.settings = Object.freeze({ match: false, message: false }); this.retryRegister = null;
    this.publish(idle);
  }
}
