import assert from 'node:assert/strict';
import test from 'node:test';
import type { MessageIntent } from '../contracts/generated/gapp-api-v1.ts';
import { CONVERSATION_LIST_POLL_MS, CONVERSATION_PAGE_LIMIT, CONVERSATION_POLL_MS } from './store.ts';
import type { ChatTransport } from './transport.ts';
import { chatSetup, settle } from './testing.ts';

type Setup = Awaited<ReturnType<typeof chatSetup>>;
const count = (fixture: Setup, operation: string) => fixture.fixture.requests().filter(request => request.operation === operation).length;
const texts = (fixture: Setup) => fixture.store.getSnapshot().conversation.messages.map(message => message.text);
const julesSends = (fixture: Setup, text: string, delivery: 'accept' | 'hold' = 'accept') =>
  assert.equal(fixture.fixture.developmentOtherSend('profile-jules', fixture.matchId, text, delivery), true);
async function open(fixture: Setup) { fixture.store.select(fixture.matchId); fixture.store.openConversation(); await settle(); }
const unread = (fixture: Setup) => fixture.store.getSnapshot().list.conversations.find(entry => entry.match_id === fixture.matchId)?.unread_count;

test('point d\'s intervals are constants in code', () => {
  assert.equal(CONVERSATION_POLL_MS, 3_000);
  assert.equal(CONVERSATION_LIST_POLL_MS, 30_000);
  assert.ok(CONVERSATION_PAGE_LIMIT >= 1 && CONVERSATION_PAGE_LIMIT <= 50);
});

test('an open conversation asks for newer messages every 3 seconds, with the page\'s own newer cursor', async () => {
  const fixture = await chatSetup();
  julesSends(fixture, 'One.');
  await open(fixture);
  assert.equal(count(fixture, 'messages'), 1);
  assert.deepEqual(fixture.timers.intervals(), [CONVERSATION_POLL_MS]);
  await fixture.timers.advance(CONVERSATION_POLL_MS - 1);
  assert.equal(count(fixture, 'messages'), 1);
  await fixture.timers.advance(1);
  assert.equal(count(fixture, 'messages'), 2);
  const [first, second] = fixture.fixture.requests().filter(request => request.operation === 'messages');
  assert.equal(first!.cursor, null);
  assert.match(second!.cursor!, /^c1\.n\./, 'the newer cursor the page gave, never one the app built');
  julesSends(fixture, 'Two.');
  await fixture.timers.advance(CONVERSATION_POLL_MS);
  assert.equal(count(fixture, 'messages'), 3);
  assert.deepEqual(texts(fixture), ['One.', 'Two.']);
});

test('the list is read when shown and every 30 seconds while it stays shown', async () => {
  const fixture = await chatSetup();
  fixture.store.showList(); await settle();
  assert.equal(count(fixture, 'conversations'), 1);
  await fixture.timers.advance(CONVERSATION_LIST_POLL_MS - 1);
  assert.equal(count(fixture, 'conversations'), 1);
  await fixture.timers.advance(1);
  assert.equal(count(fixture, 'conversations'), 2);
  fixture.store.hideList();
  await fixture.timers.advance(10 * CONVERSATION_LIST_POLL_MS);
  assert.equal(count(fixture, 'conversations'), 2);
  assert.equal(fixture.timers.active, 0);
});

for (const state of ['background', 'inactive'] as const) test(`nothing is requested while the app is ${state}; the foreground resumes polling (DM-22 7.2)`, async () => {
  const fixture = await chatSetup();
  julesSends(fixture, 'Before.');
  await open(fixture); fixture.store.showList(); await settle();
  const before = fixture.fixture.requests().length;
  fixture.activity.set(state);
  assert.equal(fixture.timers.active, 0);
  await fixture.timers.advance(10 * CONVERSATION_LIST_POLL_MS);
  // A match change in the background waits for the foreground too.
  fixture.adapter.block('profile-jules', true, 'block:background');
  await fixture.timers.advance(CONVERSATION_POLL_MS);
  assert.equal(fixture.fixture.requests().length, before, 'no request in the background');
  assert.deepEqual(texts(fixture), ['Before.'], 'nothing changed without a request');
  fixture.activity.set('active'); await settle();
  assert.equal(count(fixture, 'messages'), 2);
  assert.equal(count(fixture, 'conversations'), 2);
  assert.equal(fixture.store.getSnapshot().conversation.status, 'revoked');
  assert.deepEqual(texts(fixture), []);
});

test('polling stops when the screen is left and resumes, with one read, on return', async () => {
  const fixture = await chatSetup();
  await open(fixture);
  fixture.store.closeConversation();
  await fixture.timers.advance(20 * CONVERSATION_POLL_MS);
  assert.equal(count(fixture, 'messages'), 1);
  julesSends(fixture, 'While away.');
  fixture.store.openConversation(); await settle();
  assert.equal(count(fixture, 'messages'), 2);
  assert.deepEqual(texts(fixture), ['While away.']);
  await fixture.timers.advance(CONVERSATION_POLL_MS);
  assert.equal(count(fixture, 'messages'), 3);
});

test('a message accepted after a later one reaches the reader\'s next poll and counts as unread (DM-22 2.2)', async () => {
  const fixture = await chatSetup();
  julesSends(fixture, 'Written first, accepted late.', 'hold');
  julesSends(fixture, 'Written second, accepted first.');
  fixture.store.showList(); await open(fixture);
  assert.deepEqual(texts(fixture), ['Written second, accepted first.']);
  assert.equal(unread(fixture), 0, 'the member saw it, so the cursor moved');
  fixture.store.closeConversation();
  fixture.fixture.developmentDeliverHeld();
  fixture.store.refreshList(); await settle();
  assert.equal(unread(fixture), 1);
  fixture.store.openConversation(); await settle();
  assert.deepEqual(texts(fixture), ['Written second, accepted first.', 'Written first, accepted late.']);
  assert.equal(unread(fixture), 0);
});

test('messages are keyed on submission_id: a pending message accepted later is one message, whatever its time', async () => {
  const fixture = await chatSetup();
  await open(fixture);
  fixture.fixture.setDelivery('hold');
  fixture.store.setDraft('Mine, held.'); await fixture.store.send(); await settle();
  julesSends(fixture, 'Theirs.');
  await fixture.timers.advance(CONVERSATION_POLL_MS);
  let messages = fixture.store.getSnapshot().conversation.messages;
  assert.deepEqual(messages.map(message => [message.text, message.delivery]), [['Theirs.', null], ['Mine, held.', 'pending']]);
  const pending = messages[1]!;
  fixture.fixture.developmentDeliverHeld();
  await fixture.timers.advance(CONVERSATION_POLL_MS);
  messages = fixture.store.getSnapshot().conversation.messages;
  assert.deepEqual(messages.map(message => [message.text, message.delivery]), [['Theirs.', null], ['Mine, held.', 'accepted']]);
  assert.equal(messages[1]!.submission_id, pending.submission_id);
  assert.notEqual(messages[1]!.at, pending.at, 'its time changed on acceptance; its key did not');
  fixture.fixture.setDelivery('fail');
  fixture.store.setDraft('Mine, failed.'); await fixture.store.send(); await settle();
  assert.deepEqual(texts(fixture).at(-1), 'Mine, failed.');
  assert.equal(fixture.store.getSnapshot().conversation.messages.at(-1)!.delivery, 'failed');
});

test('older pages come with the page\'s older cursor and keep the page order', async () => {
  const fixture = await chatSetup();
  assert.equal(fixture.fixture.developmentSeed('profile-jules', fixture.matchId, 25), true);
  await open(fixture);
  assert.equal(texts(fixture).length, CONVERSATION_PAGE_LIMIT);
  assert.equal(fixture.store.getSnapshot().conversation.hasOlder, true);
  await fixture.store.loadOlder();
  const all = texts(fixture);
  assert.equal(all.length, 25);
  assert.deepEqual(all, Array.from({ length: 25 }, (_, index) => `Fictional history message ${index + 1}.`));
  assert.equal(fixture.store.getSnapshot().conversation.hasOlder, false);
  assert.match(fixture.fixture.requests().filter(request => request.operation === 'messages').at(-1)!.cursor!, /^c1\.o\./);
});

test('the read cursor moves forward only, after the member has seen the other member\'s newer messages', async () => {
  const fixture = await chatSetup();
  assert.equal(fixture.fixture.developmentSeed('profile-jules', fixture.matchId, 25), true);
  fixture.store.showList(); await settle();
  assert.equal(unread(fixture), 13);
  await open(fixture);
  assert.equal(count(fixture, 'read_cursor'), 1);
  assert.equal(unread(fixture), 0);
  // Older pages, polls with nothing new and the member's own messages never move it.
  await fixture.store.loadOlder();
  await fixture.timers.advance(3 * CONVERSATION_POLL_MS);
  fixture.store.setDraft('Mine.'); await fixture.store.send(); await settle();
  await fixture.timers.advance(CONVERSATION_POLL_MS);
  assert.equal(count(fixture, 'read_cursor'), 1);
  // Not shown, or in the background, the member has not seen it.
  fixture.store.closeConversation();
  julesSends(fixture, 'Unseen.');
  fixture.adapter.reciprocal('profile-iris', 'other-match:1'); await settle(); // A match change elsewhere: a read, but not shown.
  assert.deepEqual(texts(fixture).at(-1), 'Unseen.');
  fixture.activity.set('background'); fixture.store.openConversation(); await settle();
  assert.equal(count(fixture, 'read_cursor'), 1);
  fixture.activity.set('active'); await settle();
  assert.equal(count(fixture, 'read_cursor'), 2);
  const cursor = Object.values(fixture.fixture.inspect().readCursors);
  assert.equal(cursor.length, 1);
});

/** Records every send intent the store passes to the transport. */
function recording() {
  const sent: MessageIntent[] = [];
  return { sent, wrap: (transport: ChatTransport): ChatTransport => ({
    conversations: () => transport.conversations(), messages: request => transport.messages(request), readCursor: intent => transport.readCursor(intent),
    send: intent => { sent.push(intent); return transport.send(intent); },
  }) };
}

for (const scenario of ['offline', 'lost_response'] as const) test(`${scenario.replaceAll('_', ' ')}: a retried send reuses the same key and payload and shows one message`, async () => {
  const spy = recording(), fixture = await chatSetup(spy.wrap);
  await open(fixture);
  fixture.fixture.setScenario(scenario);
  fixture.store.setDraft('Only once.'); await fixture.store.send();
  let snapshot = fixture.store.getSnapshot();
  assert.deepEqual([snapshot.send.status, snapshot.send.error, snapshot.send.canRetry, snapshot.draft], ['error', 'offline', true, '']);
  assert.equal(fixture.fixture.inspect().submissions.length, scenario === 'lost_response' ? 1 : 0);
  fixture.fixture.setScenario('normal');
  await fixture.timers.advance(CONVERSATION_POLL_MS);
  assert.equal(texts(fixture).filter(text => text === 'Only once.').length, scenario === 'lost_response' ? 1 : 0);
  await fixture.store.retrySend(); await settle();
  snapshot = fixture.store.getSnapshot();
  assert.equal(snapshot.send.status, 'sent');
  assert.equal(spy.sent.length, 2);
  assert.deepEqual(spy.sent[1], spy.sent[0]);
  assert.equal(fixture.fixture.inspect().submissions.length, 1);
  assert.equal(texts(fixture).filter(text => text === 'Only once.').length, 1);
  const ids = snapshot.conversation.messages.map(message => message.submission_id);
  assert.equal(new Set(ids).size, ids.length);
});

test('delayed: one pending send at a time; it completes after release', async () => {
  const spy = recording(), fixture = await chatSetup(spy.wrap);
  await open(fixture);
  fixture.fixture.setScenario('delayed');
  fixture.store.setDraft('Delayed.');
  const pending = fixture.store.send(); await settle();
  assert.equal(fixture.store.getSnapshot().send.status, 'pending');
  fixture.store.setDraft('Second.'); await Promise.race([fixture.store.send(), settle()]);
  assert.equal(spy.sent.length, 1);
  fixture.fixture.releaseDelayed(); await pending; await settle();
  assert.equal(fixture.store.getSnapshot().send.status, 'sent');
  assert.deepEqual(texts(fixture), ['Delayed.']);
});

test('a revocation in the foreground drops the history, draft and polling at once; another account retains nothing', async () => {
  const fixture = await chatSetup();
  julesSends(fixture, 'Private history.');
  await open(fixture); fixture.store.showList(); await settle();
  fixture.store.setDraft('Unsent words.');
  fixture.store.closeConversation(); // A retained, hidden screen is revoked too.
  fixture.adapter.block('profile-jules', true, 'block:1'); await settle();
  const snapshot = fixture.store.getSnapshot();
  assert.deepEqual([snapshot.conversation.status, snapshot.conversation.error, snapshot.conversation.messages.length, snapshot.draft], ['revoked', 'unavailable', 0, '']);
  assert.deepEqual(snapshot.list.conversations, []);
  assert.equal(JSON.stringify(snapshot).includes('Private history.'), false);
  fixture.store.openConversation(); await settle();
  const requests = count(fixture, 'messages');
  await fixture.timers.advance(10 * CONVERSATION_POLL_MS);
  assert.equal(count(fixture, 'messages'), requests, 'a revoked conversation is not polled');
  fixture.owner.logout(); await settle();
  assert.deepEqual([fixture.store.getSnapshot().selectedMatchId, fixture.store.getSnapshot().list.conversations], [null, []]);
});

test('another account replaces the session: nothing private survives and late results are not adopted', async () => {
  const fixture = await chatSetup();
  julesSends(fixture, 'Before the switch.');
  fixture.fixture.setScenario('delayed');
  await open(fixture);
  fixture.store.setDraft('Late.'); const pending = fixture.store.send(); await settle();
  fixture.owner.scenario('eligible'); await settle();
  fixture.fixture.releaseDelayed(); await pending; await settle();
  const snapshot = fixture.store.getSnapshot();
  assert.deepEqual([snapshot.selectedMatchId, snapshot.conversation.messages.length, snapshot.send.status, snapshot.draft], [null, 0, 'idle', '']);
  assert.equal(JSON.stringify(snapshot).includes('Before the switch.'), false);
});

test('two messages with the same time are two messages; keys are submission_id, never at', async () => {
  const at = '2026-09-23T12:00:05Z', matchId = '00000083-0000-4000-8000-000000000003';
  const envelope = (data: object) => ({ contract_version: 'gapp-api-v1', request_id: '00000090-0000-4000-8000-000000000001', data });
  const message = (id: number, text: string) => ({ submission_id: `00000091-0000-4000-8000-${id.toString(16).padStart(12, '0')}`, author: 'other', at, content: 'text', text, delivery: null });
  const pages = [
    { kind: 'message_page', match_id: matchId, messages: [message(1, 'First.')], older_cursor: null, newer_cursor: 'c1.n.first' },
    { kind: 'message_page', match_id: matchId, messages: [message(2, 'Second, same second.')], older_cursor: null, newer_cursor: 'c1.n.second' },
  ];
  const fixture = await chatSetup(transport => ({ ...transport, conversations: () => transport.conversations(), send: intent => transport.send(intent),
    readCursor: async () => envelope({ kind: 'conversation', match_id: matchId, state: 'open', unread_count: 0, latest: null }),
    messages: async () => envelope(pages.shift() ?? { kind: 'message_page', match_id: matchId, messages: [], older_cursor: null, newer_cursor: 'c1.n.second' }) }));
  fixture.store.select(matchId); fixture.store.openConversation(); await settle();
  await fixture.timers.advance(CONVERSATION_POLL_MS);
  assert.deepEqual(texts(fixture), ['First.', 'Second, same second.']);
});
