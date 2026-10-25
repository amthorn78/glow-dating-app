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
/** The submission IDs of the shown messages whose texts are given, as the screen reports what is in view. */
const idsOf = (fixture: Setup, ...wanted: string[]) => fixture.store.getSnapshot().conversation.messages
  .filter(message => message.text !== null && wanted.includes(message.text)).map(message => message.submission_id);
const viewAll = (fixture: Setup) => fixture.store.viewed(fixture.store.getSnapshot().conversation.messages.map(message => message.submission_id));
const history = (...numbers: number[]) => numbers.map(number => `Fictional history message ${number}.`);

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
  viewAll(fixture); await settle();
  assert.equal(unread(fixture), 0, 'the member saw it, so the cursor moved');
  fixture.store.closeConversation();
  fixture.fixture.developmentDeliverHeld();
  fixture.store.refreshList(); await settle();
  assert.equal(unread(fixture), 1);
  fixture.store.openConversation(); await settle();
  assert.deepEqual(texts(fixture), ['Written second, accepted first.', 'Written first, accepted late.']);
  assert.equal(unread(fixture), 1, 'shown, but not yet in view');
  viewAll(fixture); await settle();
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

/** Records each read-cursor command's target, and how many were in flight at once (DM-23 2.3). */
function cursorLog() {
  const targets: string[] = [];
  let inFlight = 0, most = 0;
  return { targets, most: () => most, wrap: (transport: ChatTransport): ChatTransport => ({ ...transport,
    conversations: () => transport.conversations(), messages: request => transport.messages(request), send: intent => transport.send(intent),
    readCursor: async intent => {
      targets.push((intent as { submission_id: string }).submission_id); most = Math.max(most, ++inFlight);
      try { await settle(); return await transport.readCursor(intent); } finally { inFlight -= 1; }
    } }) };
}

test('a page that arrives in the foreground while the conversation is shown, with nothing reported as viewed, sends no cursor command (CX8; DM-23 2.1)', async () => {
  const fixture = await chatSetup();
  julesSends(fixture, 'Arrived on opening.');
  fixture.store.showList(); await open(fixture);
  julesSends(fixture, 'Arrived by polling.');
  await fixture.timers.advance(CONVERSATION_POLL_MS);
  assert.deepEqual(texts(fixture), ['Arrived on opening.', 'Arrived by polling.']);
  assert.equal(count(fixture, 'read_cursor'), 0, 'a fetch is never evidence that a message was seen');
  fixture.store.refreshList(); await settle();
  assert.equal(unread(fixture), 2);
});

test('reporting a viewed message moves the cursor to it and no further; one command at a time (DM-23 2.1, 2.3)', async () => {
  const log = cursorLog(), fixture = await chatSetup(log.wrap);
  for (const text of ['First.', 'Second.', 'Third.']) julesSends(fixture, text);
  fixture.store.showList(); await open(fixture);
  fixture.store.viewed(idsOf(fixture, 'First.', 'Second.')); await settle(); await settle();
  assert.deepEqual(log.targets, idsOf(fixture, 'Second.'), 'the newest viewed message, not the newest fetched');
  assert.equal(unread(fixture), 1);
  // The member scrolls on while a command is in flight: one at a time, then the newest viewed.
  const [third] = idsOf(fixture, 'Third.');
  julesSends(fixture, 'Fourth.'); julesSends(fixture, 'Fifth.');
  await fixture.timers.advance(CONVERSATION_POLL_MS);
  const [fourth, fifth] = idsOf(fixture, 'Fourth.', 'Fifth.');
  fixture.store.viewed([third!]); fixture.store.viewed([third!, fourth!]); fixture.store.viewed([fourth!]);
  await settle(); await settle(); await settle();
  assert.deepEqual(log.targets.slice(1), [third, fourth]);
  assert.equal(log.most(), 1, 'at most one cursor command in flight');
  assert.equal(unread(fixture), 1, 'the fifth message was never in view');
  assert.ok(fifth);
});

test('reporting an older or the same message, or only the member\'s own newer ones, moves nothing, however often it is reported (DM-23 2.3)', async () => {
  const log = cursorLog(), fixture = await chatSetup(log.wrap);
  for (const text of ['First.', 'Second.', 'Third.']) julesSends(fixture, text);
  await open(fixture);
  fixture.store.viewed(idsOf(fixture, 'Third.')); await settle(); await settle();
  assert.equal(log.targets.length, 1);
  for (let index = 0; index < 20; index++) {
    fixture.store.viewed(idsOf(fixture, 'First.')); fixture.store.viewed(idsOf(fixture, 'Second.', 'Third.')); fixture.store.viewed([]);
  }
  await settle(); await settle();
  assert.equal(log.targets.length, 1, 'never backward, and never on each report');
  // The member's own newer messages in view pass no message from the other member.
  fixture.store.setDraft('Mine.'); await fixture.store.send(); await settle();
  fixture.store.viewed(idsOf(fixture, 'Third.', 'Mine.')); await settle(); await settle();
  assert.equal(log.targets.length, 1, 'a command only when the position passes a message from the other member');
});

test('a cursor command that fails is tried again after the next read, not on each report (DM-23 2.3)', async () => {
  const log = cursorLog(), fixture = await chatSetup(log.wrap);
  julesSends(fixture, 'Seen while offline.');
  fixture.store.showList(); await open(fixture);
  fixture.fixture.setScenario('offline');
  fixture.store.viewed(idsOf(fixture, 'Seen while offline.')); await settle(); await settle();
  for (let index = 0; index < 10; index++) fixture.store.viewed(idsOf(fixture, 'Seen while offline.'));
  await fixture.timers.advance(CONVERSATION_POLL_MS);
  assert.equal(log.targets.length, 1, 'one failed command; reports and failed reads send no more');
  fixture.fixture.setScenario('normal');
  await fixture.timers.advance(CONVERSATION_POLL_MS); await settle();
  assert.deepEqual(log.targets, [...idsOf(fixture, 'Seen while offline.'), ...idsOf(fixture, 'Seen while offline.')]);
  fixture.store.refreshList(); await settle();
  assert.equal(unread(fixture), 0);
});

test('the read cursor moves only over the messages that were in view: 25 messages, 13 unread (CX8; DM-23 2.1, 2.2)', async () => {
  const fixture = await chatSetup();
  assert.equal(fixture.fixture.developmentSeed('profile-jules', fixture.matchId, 25), true);
  fixture.store.showList(); await settle();
  assert.equal(unread(fixture), 13);
  await open(fixture);
  assert.equal(texts(fixture).length, CONVERSATION_PAGE_LIMIT);
  assert.equal(count(fixture, 'read_cursor'), 0);
  assert.equal(unread(fixture), 13, 'opening the conversation clears nothing');
  // The top of the newest page is in view: messages 6 to 10 (7 and 9 are Jules's).
  fixture.store.viewed(idsOf(fixture, ...history(6, 7, 8, 9, 10))); await settle();
  assert.equal(count(fixture, 'read_cursor'), 1);
  assert.equal(unread(fixture), 8, 'only the viewed messages clear');
  // Older pages, the member's own messages and polls never move it.
  await fixture.store.loadOlder();
  fixture.store.viewed(idsOf(fixture, ...history(1, 2, 3, 4, 5))); await settle();
  fixture.store.setDraft('Mine.'); await fixture.store.send(); await settle();
  await fixture.timers.advance(3 * CONVERSATION_POLL_MS);
  assert.equal(count(fixture, 'read_cursor'), 1);
  assert.equal(unread(fixture), 8);
  // Scrolled down to message 23, short of the newest: one unread remains.
  fixture.store.viewed(idsOf(fixture, ...history(21, 22, 23))); await settle();
  assert.equal(count(fixture, 'read_cursor'), 2);
  assert.equal(unread(fixture), 1);
  // Not shown: a report is ignored. In the background: nothing is sent until the foreground.
  fixture.store.closeConversation();
  julesSends(fixture, 'Unseen.');
  fixture.adapter.reciprocal('profile-iris', 'other-match:1'); await settle(); // A match change elsewhere: a read, but not shown.
  assert.deepEqual(texts(fixture).at(-1), 'Unseen.');
  viewAll(fixture); await settle();
  assert.equal(count(fixture, 'read_cursor'), 2);
  fixture.activity.set('background'); fixture.store.openConversation(); viewAll(fixture); await settle();
  assert.equal(count(fixture, 'read_cursor'), 2, 'no request in the background');
  fixture.activity.set('active'); await settle();
  assert.equal(count(fixture, 'read_cursor'), 3, 'still in view in the foreground');
  fixture.store.refreshList(); await settle();
  assert.equal(unread(fixture), 0);
  assert.equal(Object.values(fixture.fixture.inspect().readCursors).length, 1);
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
