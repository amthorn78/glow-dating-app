import type { DeviceIntent, NotificationIntent } from '../contracts/generated/gapp-api-v1.ts';

/**
 * The request's context: the member's current session and this installation. On Glow's API they
 * travel as the request's authentication and installation headers, never as intent fields (F12:
 * the actor is the session's account). In this fixture the session is the onboarding fixture's.
 */
export type SessionHandle = Readonly<{ accountId: string; sessionId: string }>;

/**
 * The interface the notification settings screen reads and writes through (P06.3, Outcome 3).
 * Each method sends one request to Glow's API and resolves with the untrusted response body: an
 * `AppResponse` envelope or an `Error`. The client boundary (`client.ts`) validates every body.
 *
 * The only implementation is the in-process fixture (`fixture-adapter.ts`). There is no network
 * client, API URL, provider or native module here: SV4 serves F12 and P11 connects the app to it.
 */
export interface NotificationTransport {
  settings(session: SessionHandle, deviceId: string): Promise<unknown>;
  device(session: SessionHandle, deviceId: string, intent: DeviceIntent): Promise<unknown>;
  notifications(session: SessionHandle, deviceId: string, intent: NotificationIntent): Promise<unknown>;
}

/** Glow's API learning that a session ended: the stand-in for the sign-out request reaching it. */
export interface SessionRelay {
  started(session: SessionHandle): void;
  ended(session: SessionHandle, reason: 'logout' | 'expired'): void;
}

/** A request that produced no response: not sent, or its response was lost. */
export class NotificationTransportError extends Error {
  constructor() {
    super('The request did not complete.');
    this.name = 'NotificationTransportError';
  }
}
