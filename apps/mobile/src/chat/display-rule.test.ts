import assert from 'node:assert/strict';
import test from 'node:test';
import { ChatClient, ChatFailure } from './client.ts';
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
  for (const copy of [READ_COPY.invalid_response, LIST_COPY.invalid_response, SEND_COPY.invalid_response]) assert.doesNotMatch(copy, /\b(provider|stream|channel|member|custom|ai)\b/i);
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
