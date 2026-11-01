import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { ChatClient, ChatFailure } from './client.ts';
import * as copy from './copy.ts';
import { LIST_COPY, READ_COPY, SEND_COPY, UNAVAILABLE_MESSAGE } from './copy.ts';
import { PROVIDER_FIELD_CASES, PROVIDER_SENTINEL, plantProviderField } from './fixture-adapter.ts';
import type { ChatTransport } from './transport.ts';
import { chatSetup, settle } from './testing.ts';

/**
 * The display rule (ADR 0003; the brief's point g; item 10): a response carrying any
 * provider field is refused by the generated validators and gives Glow's own error state;
 * nothing of it reaches the store, which is all the screens render.
 */
const MESSAGE_KEYS = ['at', 'author', 'content', 'delivery', 'submission_id', 'text'];
/** A provider's name, its objects or its wording (ADR 0003, decision 3). */
const PROVIDER_TERMS = /\b(provider|stream|getstream|channel|member|custom|ai)\b/i;
const state = (fixture: Awaited<ReturnType<typeof chatSetup>>) => JSON.stringify(fixture.store.getSnapshot());

for (const field of PROVIDER_FIELD_CASES) test(`a response carrying ${field.replaceAll('_', ' ')} is refused and shows Glow's error state`, async () => {
  const fixture = await chatSetup();
  fixture.fixture.developmentOtherSend('profile-jules', fixture.matchId, 'Glow sent this.');
  fixture.store.select(fixture.matchId); fixture.store.openConversation(); fixture.store.showList(); await settle();
  const before = fixture.store.getSnapshot().conversation.messages;
  assert.deepEqual(before.map(message => message.text), ['Glow sent this.']);
  fixture.fixture.setProviderField(field);
  fixture.fixture.developmentOtherSend('profile-jules', fixture.matchId, 'Arrived with the planted field.');
  // The open conversation's poll and the list's.
  await fixture.timers.advance(30_000);
  let snapshot = fixture.store.getSnapshot();
  assert.equal(snapshot.conversation.status, 'error');
  assert.equal(snapshot.conversation.error, 'invalid_response');
  assert.deepEqual(snapshot.conversation.messages, before, 'no part of a refused page is used');
  assert.deepEqual([snapshot.list.status, snapshot.list.error], ['error', 'invalid_response']);
  // A send whose response carries the field is not confirmed, and may be retried with the same intent.
  fixture.store.setDraft('Mine.'); await fixture.store.send();
  snapshot = fixture.store.getSnapshot();
  assert.deepEqual([snapshot.send.status, snapshot.send.error, snapshot.send.canRetry], ['error', 'invalid_response', true]);
  assert.equal(state(fixture).includes(PROVIDER_SENTINEL), false);
  assert.equal(state(fixture).includes('Arrived with the planted field.'), false);
  // Glow's wording for that state names no provider and gives no reason.
  for (const text of [READ_COPY.invalid_response, LIST_COPY.invalid_response, SEND_COPY.invalid_response]) assert.doesNotMatch(text, PROVIDER_TERMS);
  // Back to Glow's own data: the messages it shows carry only the contract's fields.
  fixture.fixture.setProviderField(null); await fixture.timers.advance(3_000);
  snapshot = fixture.store.getSnapshot();
  assert.equal(snapshot.conversation.status, 'ready');
  assert.ok(snapshot.conversation.messages.some(message => message.text === 'Arrived with the planted field.'));
  for (const message of snapshot.conversation.messages) assert.deepEqual(Object.keys(message).sort(), MESSAGE_KEYS);
});

test('a conversation whose first page carries a provider field shows only Glow\'s error state', async () => {
  const fixture = await chatSetup();
  fixture.fixture.developmentOtherSend('profile-jules', fixture.matchId, 'Never shown.');
  fixture.fixture.setProviderField('user_object');
  fixture.store.select(fixture.matchId); fixture.store.openConversation(); await settle();
  const { conversation } = fixture.store.getSnapshot();
  assert.deepEqual([conversation.status, conversation.error, conversation.messages.length], ['error', 'invalid_response', 0]);
  assert.equal(state(fixture).includes('Never shown.'), false);
});

test('each provider field, planted in every response kind, is refused by the client', async () => {
  const fixture = await chatSetup();
  fixture.fixture.developmentOtherSend('profile-jules', fixture.matchId, 'Hello.');
  const page = await fixture.fixture.messages({ match_id: fixture.matchId, cursor: null, limit: 20 }) as object;
  const list = await fixture.fixture.conversations() as object;
  const submission = await fixture.fixture.send({ operation: 'message', match_id: fixture.matchId, text: 'Hi.', meta: { expected_version: 1, idempotency_key: 'k' } }) as object;
  const messageId = (page as { data: { messages: { submission_id: string }[] } }).data.messages[0]!.submission_id;
  const summary = await fixture.fixture.readCursor({ operation: 'read_cursor', match_id: fixture.matchId, submission_id: messageId }) as object;
  for (const field of PROVIDER_FIELD_CASES) {
    for (const [name, body, call] of [
      ['page', page, (client: ChatClient) => client.messages(fixture.matchId, null, 20)],
      ['list', list, (client: ChatClient) => client.conversations()],
      ['submission', submission, (client: ChatClient) => client.send(client.messageIntent(fixture.matchId, 'Hi.', 1, 'k'))],
      ['summary', summary, (client: ChatClient) => client.readCursor(client.readCursorIntent(fixture.matchId, messageId))],
    ] as const) {
      const planted = plantProviderField(body, field, '00000090-0000-4000-8000-0000000000aa');
      const transport: ChatTransport = { conversations: async () => planted, messages: async () => planted, send: async () => planted, readCursor: async () => planted };
      await assert.rejects(call(new ChatClient(transport)), (error: unknown) => error instanceof ChatFailure && error.code === 'invalid_response', `${field} in a ${name}`);
    }
  }
});

test('"unavailable" is Glow\'s own wording with no reason (DM-22 7.2, 6.2)', async () => {
  const fixture = await chatSetup();
  fixture.fixture.developmentOtherSend('profile-jules', fixture.matchId, 'Changed later.');
  fixture.fixture.developmentAlterLatest(fixture.matchId);
  fixture.store.select(fixture.matchId); fixture.store.openConversation(); await settle();
  const [message] = fixture.store.getSnapshot().conversation.messages;
  assert.deepEqual([message!.content, message!.text], ['unavailable', null]);
  assert.equal(UNAVAILABLE_MESSAGE, 'This message is unavailable.');
  assert.equal(state(fixture).includes('Changed later'), false);
});

test('every copy table and label in copy.ts names no provider (M05 finding 18; ADR 0003, decision 3)', () => {
  const texts: string[] = [];
  for (const [name, value] of Object.entries(copy)) {
    if (typeof value === 'string') texts.push(value);
    else if (name === 'timeLabel') texts.push(copy.timeLabel('2026-09-23T12:00:05Z'));
    else if (name === 'unreadLabel') texts.push(...[0, 1, 2].map(count => copy.unreadLabel(count)));
    else for (const entry of Object.values(value as Record<string, string>)) texts.push(entry);
  }
  // Every export is read: the six tables and constants and the two labels.
  assert.deepEqual(Object.keys(copy).sort(), ['DELIVERY_COPY', 'LIST_COPY', 'READ_COPY', 'REVOKED_DETAIL', 'SEND_COPY', 'UNAVAILABLE_MESSAGE', 'timeLabel', 'unreadLabel']);
  assert.equal(texts.length, 3 * 8 + 3 + 2 + 1 + 3);
  for (const text of texts) {
    assert.equal(typeof text, 'string');
    assert.doesNotMatch(text, PROVIDER_TERMS, text);
  }
});

/**
 * The render rule (M05 finding 18): the screens show only contract fields, whatever a response
 * carried, so a provider-shaped field (a message's `name`, a member, custom data) is never read
 * even if a validator let it through. Nothing renders `screen.tsx` in Node, so its source is
 * read: every property it reads from a message, a conversation, the list, the store's state or a
 * match is one this list names, and no cast, spread or reflective read can reach another.
 */
const RENDERED_PATHS = new Set([
  // ConversationMessage: the contract's six fields.
  'message.submission_id', 'message.author', 'message.delivery', 'message.content', 'message.text', 'message.at',
  // ConversationSummary, as a list row.
  'conversation.match_id', 'conversation.unread_count', 'conversation.latest', 'conversation.latest.at',
  // The store's conversation state.
  'conversation.status', 'conversation.error', 'conversation.hasOlder', 'conversation.older', 'conversation.messages',
  'conversation.messages.length', 'conversation.messages.map',
  'list.status', 'list.error', 'list.conversations', 'list.conversations.length', 'list.conversations.map', 'list.conversations.match_id',
  'state.draft', 'state.send', 'state.send.status', 'state.send.error', 'state.send.canRetry', 'state.matches', 'state.matches.filter',
  // Glow's own match projection, for names (ADR 0003, decision 1).
  'match.match_id', 'match.state', 'match.profile', 'match.profile.display_name',
]);
const ROOTS = /\b(message|conversation|list|state|match)((?:!?\??\.[A-Za-z_$][\w$]*|\[\d+\]\??)*)/g;
function readSource(path: string) {
  return readFileSync(new URL(path, import.meta.url), 'utf8').replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '').replace(/\{\/\*.*?\*\/\}/g, '');
}
function renderedPaths(source: string) {
  const paths = new Set<string>();
  for (const [, root, chain] of source.matchAll(ROOTS)) {
    const segments = chain!.replace(/\[\d+\]/g, '').replace(/[!?]/g, '').split('.').filter(Boolean);
    for (let index = 1; index <= segments.length; index++) paths.add([root, ...segments.slice(0, index)].join('.'));
  }
  return paths;
}
function renderRuleViolations(source: string) {
  const violations = [...renderedPaths(source)].filter(path => !RENDERED_PATHS.has(path));
  if (/[\w)\]!]\s+as\s+(?!const\b)/.test(source)) violations.push('a type cast');
  if (/\bany\b/.test(source.replace(/'[^'\n]*'|`[^`\n]*`/g, ''))) violations.push('an any type');
  if (/\b(Object|Reflect|JSON)\s*\./.test(source)) violations.push('a reflective read');
  if (/\.\.\.\s*(message|conversation|list|state|match)\b/.test(source)) violations.push('a spread');
  if (/\b(message|conversation|list|state|match)\s*\[\s*(?!\d+\s*\])/.test(source)) violations.push('a computed read');
  return violations;
}

test('the chat screens render only the contract\'s fields: no provider-shaped field is read, whatever the validators let through (M05 finding 18)', () => {
  const source = readSource('./screen.tsx');
  assert.deepEqual(renderRuleViolations(source), []);
  // Each message field the screen reads is one of the contract's.
  const read = [...renderedPaths(source)].filter(path => path.startsWith('message.')).map(path => path.slice('message.'.length));
  assert.deepEqual(read.filter(key => !MESSAGE_KEYS.includes(key)), []);
  // The checker itself refuses the forms a provider field would take.
  for (const planted of ['{message.name}', '{(message as { name?: string }).name}', '{String(message[\'name\'])}', '<Text {...message} />',
    '{Object.values(message).join()}', '{conversation.member?.name}', '{(message as any).user}']) {
    assert.notDeepEqual(renderRuleViolations(`${source}\n${planted}`), [], planted);
  }
});
