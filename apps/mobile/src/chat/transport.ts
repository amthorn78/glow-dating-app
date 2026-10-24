import type { MessageIntent, MessagePageRequest, ReadCursorIntent } from '../contracts/generated/gapp-api-v1.ts';

/**
 * The interface the chat screens read through (P06.2 Stage C2, OD-45). Each method sends
 * one request to Glow's API and resolves with the untrusted response body: an
 * `AppResponse` envelope or an `Error`. The client boundary (`client.ts`) validates every
 * body before the screens see it. The actor is the authenticated session, never a field.
 *
 * C2's only implementation is the in-process fixture (`fixture-adapter.ts`). There is no
 * network client, API URL, socket or event stream here: P11 connects this interface to
 * Glow's API, with `fetch` only.
 */
export interface ChatTransport {
  conversations(): Promise<unknown>;
  messages(request: MessagePageRequest): Promise<unknown>;
  send(intent: MessageIntent): Promise<unknown>;
  readCursor(intent: ReadCursorIntent): Promise<unknown>;
}

/** A request that produced no response: not sent, or its response was lost. */
export class ChatTransportError extends Error {
  constructor() {
    super('The request did not complete.');
    this.name = 'ChatTransportError';
  }
}
