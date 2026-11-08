import type { ConversationSummary } from '../contracts/generated/gapp-api-v1.ts';
import { READ_COPY, timeLabel, unreadLabel } from './copy.ts';

/**
 * One row of the conversation list, from Glow's summary and Glow's own match names (ADR 0003,
 * decision 1). Only an `open` conversation is openable. A `closed` one shows Glow's unavailable
 * wording with no reason, count, time or open control (M05 finding 20; the contract's closed
 * summary carries no count and no marker).
 */
export type ConversationRow = Readonly<{ matchId: string; name: string; openable: boolean; status: string; latest: string | null }>;
export function conversationRow(conversation: ConversationSummary, names: ReadonlyMap<string, string>): ConversationRow {
  const name = names.get(conversation.match_id) ?? 'Your match';
  if (conversation.state !== 'open') return Object.freeze({ matchId: conversation.match_id, name, openable: false, status: READ_COPY.unavailable, latest: null });
  return Object.freeze({ matchId: conversation.match_id, name, openable: true, status: unreadLabel(conversation.unread_count),
    latest: conversation.latest ? `Latest message ${timeLabel(conversation.latest.at)}` : 'No messages yet' });
}
