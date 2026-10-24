import type { ConversationList, ConversationSummary, Error as ApiError, MessageIntent, MessagePage, MessagePageRequest,
  MessageSubmission, ReadCursorIntent } from '../contracts/generated/gapp-api-v1.ts';
import { validateConversationList, validateConversationSummary, validateMessagePage, validateMessagePageRequest,
  validateMessageSubmission } from '../contracts/generated/validators.js';
import { parseApiError, parseAppIntent, parseAppResponse } from '../contracts/production.ts';
import type { ChatTransport } from './transport.ts';

/**
 * Why a chat request did not give the screens a result. The screens show Glow's own wording
 * for each code; none of them carries a response's text, a provider's text or a reason why
 * a conversation ended.
 */
export type ChatFailureCode = 'unavailable' | 'signed_out' | 'stale' | 'temporary' | 'conflict' | 'invalid_request' | 'invalid_response' | 'offline';
export class ChatFailure extends Error {
  readonly code: ChatFailureCode;
  readonly retryable: boolean;
  constructor(code: ChatFailureCode, retryable = false) {
    super('The chat request did not complete.');
    this.name = 'ChatFailure'; this.code = code; this.retryable = retryable;
  }
}
/** Glow's error codes, mapped to what the screens can say (the production contracts' error table). */
function failureFor(error: ApiError): ChatFailure {
  switch (error.code) {
    case 'not_found': case 'forbidden': return new ChatFailure('unavailable');
    case 'unauthenticated': return new ChatFailure('signed_out');
    case 'stale_version': return new ChatFailure('stale');
    case 'provider_unavailable': case 'rate_limited': case 'state_conflict': return new ChatFailure('temporary', error.retryable);
    case 'idempotency_conflict': return new ChatFailure('conflict');
    default: return new ChatFailure('invalid_request');
  }
}
const freeze = <T>(value: T): T => { if (value && typeof value === 'object') { Object.values(value).forEach(freeze); Object.freeze(value); } return value; };
const unique = (values: readonly string[]) => new Set(values).size === values.length;
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

/**
 * The boundary between the chat transport and the screens (P06.2 Stage C2). A response
 * reaches the screens only if the generated validators accept it: the `AppResponse`
 * envelope with the shared key-uniqueness rule (`parseAppResponse`), then the DTO's own
 * validator, the expected kind and the request's match. Anything else, including a body
 * carrying any provider field, is refused whole as `invalid_response`: no part of it is
 * kept, shown or logged. Every intent passes `parseAppIntent` before it is sent.
 */
export class ChatClient {
  private readonly transport: ChatTransport;
  constructor(transport: ChatTransport) { this.transport = transport; }
  private async call(request: () => Promise<unknown>): Promise<unknown> {
    try { return await request(); } catch { throw new ChatFailure('offline', true); }
  }
  private accept<T>(body: unknown, kind: string, validate: (value: unknown) => boolean, check: (data: T) => boolean): T {
    let data: unknown;
    try { data = parseAppResponse(body).data; } catch {
      let error: ApiError;
      try { error = parseApiError(body); } catch { throw new ChatFailure('invalid_response', true); }
      throw failureFor(error);
    }
    if ((data as { kind?: unknown }).kind !== kind || !validate(data) || !check(data as T)) throw new ChatFailure('invalid_response', true);
    return freeze(clone(data as T));
  }
  async conversations(): Promise<ConversationList> {
    const body = await this.call(() => this.transport.conversations());
    return this.accept<ConversationList>(body, 'conversation_list', validateConversationList,
      list => unique(list.conversations.map(conversation => conversation.match_id)));
  }
  async messages(matchId: string, cursor: string | null, limit: number): Promise<MessagePage> {
    const request: MessagePageRequest = { match_id: matchId, cursor, limit };
    if (!validateMessagePageRequest(request)) throw new ChatFailure('invalid_request');
    const body = await this.call(() => this.transport.messages(freeze({ ...request })));
    // The app keys messages on `submission_id`, so a page naming one twice is refused whole.
    return this.accept<MessagePage>(body, 'message_page', validateMessagePage,
      page => page.match_id === matchId && unique(page.messages.map(message => message.submission_id)));
  }
  messageIntent(matchId: string, text: string, expectedVersion: number, idempotencyKey: string): MessageIntent {
    const intent: MessageIntent = { operation: 'message', match_id: matchId, text, meta: { expected_version: expectedVersion, idempotency_key: idempotencyKey } };
    try { parseAppIntent(intent); } catch { throw new ChatFailure('invalid_request'); }
    return freeze(intent);
  }
  async send(intent: MessageIntent): Promise<MessageSubmission> {
    try { parseAppIntent(intent); } catch { throw new ChatFailure('invalid_request'); }
    const body = await this.call(() => this.transport.send(intent));
    return this.accept<MessageSubmission>(body, 'message', validateMessageSubmission, () => true);
  }
  readCursorIntent(matchId: string, submissionId: string): ReadCursorIntent {
    const intent: ReadCursorIntent = { operation: 'read_cursor', match_id: matchId, submission_id: submissionId };
    try { parseAppIntent(intent); } catch { throw new ChatFailure('invalid_request'); }
    return freeze(intent);
  }
  async readCursor(intent: ReadCursorIntent): Promise<ConversationSummary> {
    try { parseAppIntent(intent); } catch { throw new ChatFailure('invalid_request'); }
    const body = await this.call(() => this.transport.readCursor(intent));
    return this.accept<ConversationSummary>(body, 'conversation', validateConversationSummary, summary => summary.match_id === intent.match_id);
  }
}
