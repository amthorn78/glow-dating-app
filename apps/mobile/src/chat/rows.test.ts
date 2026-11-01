import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import type { ConversationSummary } from '../contracts/generated/gapp-api-v1.ts';
import { validateConversationSummary } from '../contracts/generated/validators.js';
import { READ_COPY } from './copy.ts';
import { conversationRow } from './rows.ts';

const matchId = '00000083-0000-4000-8000-000000000001';
const names = new Map([[matchId, 'Fictional Jules']]);
const summary = (state: 'open' | 'closed', unread = 0): ConversationSummary => ({ kind: 'conversation', match_id: matchId, state, unread_count: unread,
  latest: state === 'open' ? { submission_id: '00000091-0000-4000-8000-000000000001', at: '2026-09-23T12:00:05Z' } : null });

test('an open conversation is an openable row with its count and latest time', () => {
  assert.equal(validateConversationSummary(summary('open', 2)), true);
  assert.deepEqual(conversationRow(summary('open', 2), names), { matchId, name: 'Fictional Jules', openable: true, status: '2 unread messages', latest: 'Latest message 2026-09-23 12:00 UTC' });
});

test('a closed conversation is not an openable row: Glow\'s unavailable wording, no count, time or reason (M05 finding 20)', () => {
  assert.equal(validateConversationSummary(summary('closed')), true, 'the contract\'s closed summary');
  assert.deepEqual(conversationRow(summary('closed'), names), { matchId, name: 'Fictional Jules', openable: false, status: READ_COPY.unavailable, latest: null });
});

test('the list screen renders its rows from conversationRow and offers "Open conversation" only on an openable row (M05 finding 20)', () => {
  // The screen cannot render in Node, so its source is read.
  const source = readFileSync(new URL('./screen.tsx', import.meta.url), 'utf8');
  const list = source.slice(source.indexOf('export function ConversationsScreen()'), source.indexOf('function MessageRow('));
  assert.match(list, /list\.conversations\.map\(conversation => conversationRow\(conversation, names\)\)\.map\(row =>/);
  assert.equal(list.match(/conversation-open-/g)?.length, 1, 'one open control');
  assert.match(list, /\{row\.openable && <Button label=\{`Open conversation with \$\{row\.name\}`\} testID=\{`conversation-open-\$\{row\.matchId\}`\}/);
  assert.equal(/store\.select\(/.test(list.replace(/\{row\.openable && <Button[^]*?\/>\}/, '')), false, 'no other path selects a listed conversation');
});
