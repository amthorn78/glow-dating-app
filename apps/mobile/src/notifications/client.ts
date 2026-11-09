import type { DeviceIntent, Error as ApiError, NotificationIntent, NotificationSettings } from '../contracts/generated/gapp-api-v1.ts';
import { validateNotificationSettings } from '../contracts/generated/validators.js';
import { parseApiError, parseAppIntent, parseAppResponse } from '../contracts/production.ts';
import type { NotificationTransport, SessionHandle } from './transport.ts';

/**
 * Why a notification request did not give the screen a result. The screen shows Glow's own
 * wording for each code (`copy.ts`); none carries a response's text.
 */
export type NotificationFailureCode = 'signed_out' | 'stale' | 'not_active' | 'conflict' | 'temporary' | 'invalid_request'
  | 'invalid_response' | 'offline' | 'unavailable';
export class NotificationFailure extends Error {
  readonly code: NotificationFailureCode;
  readonly retryable: boolean;
  constructor(code: NotificationFailureCode, retryable = false) {
    super('The notification request did not complete.');
    this.name = 'NotificationFailure'; this.code = code; this.retryable = retryable;
  }
}
/** A settings read: this installation's settings, or an explicit absence (no registration; the contract's `device_state` has no `none`). */
export type SettingsRead = Readonly<{ status: 'absent' }> | Readonly<{ status: 'present'; settings: NotificationSettings }>;

function failureFor(error: ApiError): NotificationFailure {
  switch (error.code) {
    case 'unauthenticated': return new NotificationFailure('signed_out');
    case 'stale_version': return new NotificationFailure('stale');
    case 'state_conflict': return new NotificationFailure('not_active');
    case 'idempotency_conflict': return new NotificationFailure('conflict');
    case 'provider_unavailable': case 'rate_limited': return new NotificationFailure('temporary', error.retryable);
    case 'not_found': case 'forbidden': return new NotificationFailure('unavailable');
    default: return new NotificationFailure('invalid_request');
  }
}
const freeze = <T>(value: T): T => { if (value && typeof value === 'object') { Object.values(value).forEach(freeze); Object.freeze(value); } return value; };
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

/**
 * The boundary between the notification transport and the screen (P06.3, Outcome 3). A response
 * reaches the screen only if the generated validators accept it: the `AppResponse` envelope with
 * the shared key-uniqueness rule, then `NotificationSettings`' own validator. Anything else is
 * refused whole as `invalid_response`. A settings read answered with `not_found` is the explicit
 * absence of a registration for this installation. Every intent passes `parseAppIntent` before
 * the transport takes it, as chat's client does. No token is ever kept, shown or logged here.
 */
export class NotificationClient {
  private readonly transport: NotificationTransport;
  constructor(transport: NotificationTransport) { this.transport = transport; }
  private async call(request: () => Promise<unknown>): Promise<unknown> {
    try { return await request(); } catch { throw new NotificationFailure('offline', true); }
  }
  private settingsFrom(body: unknown): NotificationSettings {
    let data: unknown;
    try { data = parseAppResponse(body).data; } catch {
      let error: ApiError;
      try { error = parseApiError(body); } catch { throw new NotificationFailure('invalid_response', true); }
      throw failureFor(error);
    }
    if ((data as { kind?: unknown }).kind !== 'notifications' || !validateNotificationSettings(data)) throw new NotificationFailure('invalid_response', true);
    return freeze(clone(data as NotificationSettings));
  }
  async read(session: SessionHandle, deviceId: string): Promise<SettingsRead> {
    const body = await this.call(() => this.transport.settings(session, deviceId));
    try { return freeze({ status: 'present', settings: this.settingsFrom(body) }); } catch (failure) {
      if (failure instanceof NotificationFailure && failure.code === 'unavailable' && parseApiError(body).code === 'not_found') return freeze({ status: 'absent' });
      throw failure;
    }
  }
  deviceIntent(deviceId: string, action: 'register' | 'revoke', token: string | null, expectedVersion: number, idempotencyKey: string): DeviceIntent {
    const intent: DeviceIntent = { operation: 'device', meta: { expected_version: expectedVersion, idempotency_key: idempotencyKey },
      device_id: deviceId, action, provider_token: token };
    try { parseAppIntent(intent); } catch { throw new NotificationFailure('invalid_request'); }
    return freeze(intent);
  }
  settingsIntent(match: boolean, message: boolean, expectedVersion: number, idempotencyKey: string): NotificationIntent {
    const intent: NotificationIntent = { operation: 'notifications', meta: { expected_version: expectedVersion, idempotency_key: idempotencyKey },
      match_notifications: match, message_notifications: message };
    try { parseAppIntent(intent); } catch { throw new NotificationFailure('invalid_request'); }
    return freeze(intent);
  }
  async device(session: SessionHandle, deviceId: string, intent: DeviceIntent): Promise<NotificationSettings> {
    try { parseAppIntent(intent); } catch { throw new NotificationFailure('invalid_request'); }
    return this.settingsFrom(await this.call(() => this.transport.device(session, deviceId, intent)));
  }
  async save(session: SessionHandle, deviceId: string, intent: NotificationIntent): Promise<NotificationSettings> {
    try { parseAppIntent(intent); } catch { throw new NotificationFailure('invalid_request'); }
    return this.settingsFrom(await this.call(() => this.transport.notifications(session, deviceId, intent)));
  }
}
