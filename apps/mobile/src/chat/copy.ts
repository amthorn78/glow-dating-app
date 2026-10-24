import type { ConversationMessage } from '../contracts/generated/gapp-api-v1.ts';
import type { ChatFailureCode } from './client.ts';

/**
 * Glow's own wording for every chat state (ADR 0003, decision 3). Keyed by Glow's codes,
 * never by a response's text: no provider name, identifier, error text or reason reaches it.
 */
export const UNAVAILABLE_MESSAGE = 'This message is unavailable.';
export const REVOKED_DETAIL = 'Its messages are not shown. Return to your conversations to check current access.';
export const LIST_COPY: Readonly<Record<ChatFailureCode, string>> = Object.freeze({
  unavailable: 'Your conversations are unavailable.',
  signed_out: 'Your session has ended. Sign in again to continue.',
  stale: 'Your conversations changed. Refresh them to continue.',
  temporary: 'Your conversations could not be loaded right now. Try again.',
  conflict: 'Your conversations could not be loaded right now. Try again.',
  invalid_request: 'Your conversations could not be loaded. Try again.',
  invalid_response: 'Your conversations could not be shown. Try again.',
  offline: 'The response was not received. Try again.',
});
export const READ_COPY: Readonly<Record<ChatFailureCode, string>> = Object.freeze({
  unavailable: 'This conversation is unavailable.',
  signed_out: 'Your session has ended. Sign in again to continue.',
  stale: 'This conversation changed. Try again to reload it.',
  temporary: 'Messages could not be loaded right now. Try again.',
  conflict: 'Messages could not be loaded right now. Try again.',
  invalid_request: 'Messages could not be loaded. Try again.',
  invalid_response: 'Messages could not be shown. Try again.',
  offline: 'The response was not received. Try again.',
});
export const SEND_COPY: Readonly<Record<ChatFailureCode, string>> = Object.freeze({
  unavailable: 'This conversation is unavailable. Your message was not sent.',
  signed_out: 'Your session has ended. Sign in again to continue.',
  stale: 'This conversation changed. Your message was not sent.',
  temporary: 'Your message could not be sent right now. Retry the same message.',
  conflict: 'This message conflicts with an earlier request and was not sent.',
  invalid_request: 'Write a message of up to 4,000 characters.',
  invalid_response: 'Your message was not confirmed. Retry to check it without sending it twice.',
  offline: 'Your message was not confirmed. Retry to check it without sending it twice.',
});
export const DELIVERY_COPY: Readonly<Record<NonNullable<ConversationMessage['delivery']>, string>> = Object.freeze({
  pending: 'Sending', accepted: 'Sent', failed: 'Not delivered',
});
/** Glow's time as a short label; display only, never an order or a key. */
export const timeLabel = (at: string) => `${at.slice(0, 10)} ${at.slice(11, 16)} UTC`;
export const unreadLabel = (count: number) => count === 0 ? 'No unread messages' : count === 1 ? '1 unread message' : `${count} unread messages`;
