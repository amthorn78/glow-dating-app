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

/** The member's own accepted messages, sent through the transport before the conversation is opened (DM-25 3.5). */
async function ownSends(fixture: Setup, total: number) {
  const version = fixture.adapter.matches().find(match => match.match_id === fixture.matchId)!.version;
  for (let index = 1; index <= total; index++) {
    await fixture.fixture.send(fixture.client.messageIntent(fixture.matchId, `Mine ${index}.`, version, `own-through-transport:${index}`));
  }
}
const INCOMING = 'Unread, before the newest page.';
/** One incoming message, then a full newest page of the member's own: the incoming one lies outside the loaded window (CX10). */
async function incomingOutsideWindow(fixture: Setup) {
  julesSends(fixture, INCOMING);
  await ownSends(fixture, CONVERSATION_PAGE_LIMIT);
}
const newest = (fixture: Setup) => idsOf(fixture, `Mine ${CONVERSATION_PAGE_LIMIT}.`);

test('(a) an incoming message outside the window, with the list read first: viewing the newest sends one command, to it, and the count clears (CX10; DM-25 3.1)', async () => {
  const log = cursorLog(), fixture = await chatSetup(log.wrap);
  await incomingOutsideWindow(fixture);
  fixture.store.showList(); await settle();
  assert.equal(unread(fixture), 1);
  fixture.store.hideList(); await open(fixture);
  assert.equal(texts(fixture).includes(INCOMING), false, 'the incoming message is outside the newest page');
  fixture.store.viewed(newest(fixture)); await settle(); await settle();
  assert.deepEqual(log.targets, newest(fixture));
  assert.equal(unread(fixture), 0, 'the command\'s summary clears the list\'s count');
  fixture.store.refreshList(); await settle();
  assert.equal(unread(fixture), 0);
});

test('(b) the same with no list read: the conversation opened with no summary held sends one command (CX10; DM-25 3.1)', async () => {
  const log = cursorLog(), fixture = await chatSetup(log.wrap);
  await incomingOutsideWindow(fixture);
  await open(fixture); // As the match's "Open conversation" does: no list read.
  assert.deepEqual(fixture.store.getSnapshot().list.conversations, []);
  fixture.store.viewed(newest(fixture)); await settle(); await settle();
  assert.deepEqual(log.targets, newest(fixture));
  fixture.store.showList(); await settle();
  assert.equal(unread(fixture), 0);
});

for (const trigger of ['an older page', 'a list read'] as const) test(`(c) a summary out of date at 0 holds the move back until ${trigger} supplies the evidence (CX10; DM-25 3.1, 3.2)`, async () => {
  const log = cursorLog(), fixture = await chatSetup(log.wrap);
  fixture.store.showList(); await settle();
  assert.equal(unread(fixture), 0, 'read before the incoming message and the member\'s own arrived');
  fixture.store.hideList();
  await incomingOutsideWindow(fixture);
  await open(fixture);
  fixture.store.viewed(newest(fixture)); await settle(); await settle();
  assert.deepEqual(log.targets, [], 'the summary held shows 0 and the window holds no incoming message');
  if (trigger === 'an older page') {
    await fixture.store.loadOlder(); await settle(); await settle();
    assert.equal(texts(fixture)[0], INCOMING);
  } else {
    fixture.store.refreshList(); await settle(); await settle();
  }
  assert.deepEqual(log.targets, newest(fixture), 'one command, to `seen`');
  fixture.store.refreshList(); await settle();
  assert.equal(unread(fixture), 0);
});

test('(d) nothing unread: a summary at 0 and no incoming message in the window send no command, however often the messages are reported (CX10; DM-25 3.1)', async () => {
  const log = cursorLog(), fixture = await chatSetup(log.wrap);
  await ownSends(fixture, 3);
  fixture.store.showList(); await settle();
  assert.equal(unread(fixture), 0);
  await open(fixture);
  for (let index = 0; index < 20; index++) {
    viewAll(fixture); fixture.store.viewed(idsOf(fixture, 'Mine 1.')); fixture.store.viewed([]); fixture.store.viewed(idsOf(fixture, 'Mine 3.'));
  }
  await fixture.timers.advance(3 * CONVERSATION_POLL_MS);
  fixture.store.refreshList(); await settle();
  assert.deepEqual(log.targets, []);
  assert.equal(count(fixture, 'read_cursor'), 0);
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

type Operation = keyof ChatTransport;
const refusal = { contract_version: 'gapp-api-v1', request_id: '00000090-0000-4000-8000-0000000000ff', code: 'not_found', retryable: false };
/**
 * CX9's wrapper (DM-24 1.4): holds a chosen request's response until released, and answers a
 * chosen request with Glow's refusal, as the server answers once access has ended. A held
 * request reaches the fixture at once, so its response is the one built before the revocation.
 */
function gate() {
  const holding = new Map<Operation, 'succeed' | 'fail'>(), refusing = new Set<Operation>();
  let releases: (() => void)[] = [];
  const pass = async (operation: Operation, call: () => Promise<unknown>) => {
    if (refusing.delete(operation)) return refusal;
    const outcome = holding.get(operation);
    if (!outcome) return call();
    holding.delete(operation);
    const body = await call();
    await new Promise<void>(resolve => { releases.push(resolve); });
    if (outcome === 'fail') throw new Error('The request did not complete.'); // Offline: access has not ended.
    return body;
  };
  return {
    hold: (operation: Operation, outcome: 'succeed' | 'fail' = 'succeed') => { holding.set(operation, outcome); },
    refuse: (operation: Operation) => { refusing.add(operation); },
    held: () => releases.length,
    release: async () => { const pending = releases; releases = []; pending.forEach(release => release()); await settle(); await settle(); },
    wrap: (transport: ChatTransport): ChatTransport => ({
      conversations: () => pass('conversations', () => transport.conversations()),
      messages: request => pass('messages', () => transport.messages(request)),
      send: intent => pass('send', () => transport.send(intent)),
      readCursor: intent => pass('readCursor', () => transport.readCursor(intent)),
    }),
  };
}
type Gate = ReturnType<typeof gate>;
const PRIVATE = 'Private history.';
/** The ways a request outstanding can meet a revocation: a send's refusal, a cursor command's, or a head read's. */
const revokeThrough = {
  'a send\'s refusal': async (fixture: Setup, gated: Gate) => {
    gated.refuse('send'); fixture.store.setDraft('Refused.'); await fixture.store.send(); await settle();
  },
  'a cursor command\'s refusal': async (fixture: Setup, gated: Gate) => {
    gated.refuse('readCursor'); fixture.store.setDraft('Unsent words.'); fixture.store.viewed(idsOf(fixture, PRIVATE)); await settle();
  },
  'a head read\'s refusal': async (fixture: Setup, gated: Gate) => {
    gated.refuse('messages'); fixture.store.setDraft('Unsent words.'); await fixture.timers.advance(CONVERSATION_POLL_MS);
  },
} as const;
type Revocation = keyof typeof revokeThrough;
/** A shown conversation with one unviewed message from Jules, and the list read. */
async function revocable(gated: Gate) {
  const fixture = await chatSetup(gated.wrap);
  julesSends(fixture, PRIVATE);
  fixture.store.showList(); await open(fixture);
  assert.deepEqual(texts(fixture), [PRIVATE]);
  assert.equal(unread(fixture), 1);
  return fixture;
}
async function revoke(fixture: Setup, gated: Gate, through: Revocation) {
  await revokeThrough[through](fixture, gated);
  assertRevoked(fixture);
}
function assertRevoked(fixture: Setup) {
  const snapshot = fixture.store.getSnapshot();
  assert.deepEqual([snapshot.conversation.status, snapshot.conversation.error, snapshot.conversation.messages, snapshot.conversation.hasOlder,
    snapshot.conversation.older], ['revoked', 'unavailable', [], false, 'idle']);
  assert.deepEqual([snapshot.draft, snapshot.send], ['', { status: 'idle', error: null, canRetry: false }], 'no draft, no pending send, no retry (DM-24 1.2)');
  assert.equal(snapshot.list.conversations.some(entry => entry.match_id === fixture.matchId), false);
  assert.equal(JSON.stringify(snapshot).includes(PRIVATE), false);
}
const requested = (fixture: Setup) => fixture.fixture.requests().length;
const both = ['a send\'s refusal', 'a cursor command\'s refusal'] as const satisfies readonly Revocation[];

for (const through of both) test(`CX9: a head read held across a revocation through ${through} changes nothing when it succeeds (DM-24 1.1, 1.2)`, async () => {
  const gated = gate(), fixture = await revocable(gated);
  gated.hold('messages'); await fixture.timers.advance(CONVERSATION_POLL_MS);
  assert.equal(gated.held(), 1);
  fixture.store.retryRead(); // Queued behind the read in flight: invalidated with it.
  await revoke(fixture, gated, through);
  const before = requested(fixture), snapshot = fixture.store.getSnapshot();
  await gated.release();
  await fixture.timers.advance(3 * CONVERSATION_POLL_MS); // Before the list's 30-second read, which, made after, is 1.3's.
  assert.equal(fixture.store.getSnapshot(), snapshot, 'nothing published');
  assertRevoked(fixture);
  assert.equal(requested(fixture), before, 'no new read and no cursor command');
});

for (const through of both) test(`CX9: an older page held across a revocation through ${through} leaves the messages empty when it succeeds (DM-24 1.1)`, async () => {
  const gated = gate(), fixture = await chatSetup(gated.wrap);
  assert.equal(fixture.fixture.developmentSeed('profile-jules', fixture.matchId, 25), true);
  fixture.store.showList(); await open(fixture);
  gated.hold('messages');
  const older = fixture.store.loadOlder(); await settle();
  assert.equal(gated.held(), 1);
  if (through === 'a send\'s refusal') await revokeThrough[through](fixture, gated);
  else { gated.refuse('readCursor'); fixture.store.viewed(idsOf(fixture, ...history(25))); await settle(); }
  assertRevoked(fixture);
  const before = requested(fixture), snapshot = fixture.store.getSnapshot();
  await gated.release(); await older;
  assert.equal(fixture.store.getSnapshot(), snapshot, 'nothing published');
  assert.deepEqual(fixture.store.getSnapshot().conversation.messages, []);
  assert.equal(requested(fixture), before);
});

for (const through of both) test(`CX9: a head read held across a revocation through ${through} that then fails without ending access leaves it revoked, not in error (DM-24 1.1)`, async () => {
  const gated = gate(), fixture = await revocable(gated);
  gated.hold('messages', 'fail'); await fixture.timers.advance(CONVERSATION_POLL_MS);
  await revoke(fixture, gated, through);
  const before = requested(fixture);
  await gated.release();
  await fixture.timers.advance(3 * CONVERSATION_POLL_MS); // Before the list's 30-second read, which, made after, is 1.3's.
  assertRevoked(fixture);
  assert.equal(requested(fixture), before);
});

for (const through of ['a cursor command\'s refusal', 'a head read\'s refusal'] as const) test(`CX9: a send held across a revocation through ${through} is no longer pending, and its success shows no "sent" and reads nothing (DM-24 1.1, 1.2)`, async () => {
  const gated = gate(), fixture = await revocable(gated);
  gated.hold('send');
  fixture.store.setDraft('Held.'); const pending = fixture.store.send(); await settle();
  assert.equal(fixture.store.getSnapshot().send.status, 'pending');
  await revoke(fixture, gated, through);
  const before = requested(fixture), snapshot = fixture.store.getSnapshot();
  await gated.release(); await pending;
  assert.equal(fixture.store.getSnapshot(), snapshot, 'no "sent" state');
  assert.equal(requested(fixture), before, 'no head read after the send');
});

for (const through of ['a send\'s refusal', 'a head read\'s refusal'] as const) test(`CX9: a cursor command held across a revocation through ${through} changes neither the cursor nor the list when it succeeds (DM-24 1.1)`, async () => {
  const gated = gate(), fixture = await revocable(gated);
  gated.hold('readCursor');
  fixture.store.viewed(idsOf(fixture, PRIVATE)); await settle();
  assert.equal(gated.held(), 1);
  await revoke(fixture, gated, through);
  const snapshot = fixture.store.getSnapshot();
  await gated.release();
  assert.equal(fixture.store.getSnapshot(), snapshot, 'nothing published: the list is unchanged');
  // The cursor position the store holds is unchanged too: once readable again, viewing the
  // same message sends a command, which a late `lastRead` would have suppressed.
  fixture.activity.set('background'); fixture.activity.set('active'); await settle();
  assert.deepEqual(texts(fixture), [PRIVATE]);
  const commands = count(fixture, 'read_cursor');
  fixture.store.viewed(idsOf(fixture, PRIVATE)); await settle(); await settle();
  assert.equal(count(fixture, 'read_cursor'), commands + 1);
});

for (const through of both) test(`CX9: a list read held across a revocation through ${through} does not put the conversation's row back (DM-24 1.1)`, async () => {
  const gated = gate(), fixture = await revocable(gated);
  gated.hold('conversations'); fixture.store.refreshList(); await settle();
  assert.equal(gated.held(), 1);
  await revoke(fixture, gated, through);
  const before = requested(fixture), snapshot = fixture.store.getSnapshot();
  await gated.release();
  assert.equal(fixture.store.getSnapshot(), snapshot, 'nothing published');
  assert.equal(unread(fixture), undefined, 'the row stays absent');
  assert.equal(requested(fixture), before, 'and nothing is started');
});

for (const through of both) test(`CX9: requests made after a revocation through ${through} keep today's behaviour, beside held ones made before it (DM-24 1.3)`, async () => {
  const gated = gate(), fixture = await revocable(gated);
  gated.hold('messages'); await fixture.timers.advance(CONVERSATION_POLL_MS);
  gated.hold('conversations'); fixture.store.refreshList(); await settle();
  assert.equal(gated.held(), 2);
  await revoke(fixture, gated, through);
  const reads = count(fixture, 'messages'), lists = count(fixture, 'conversations');
  // A return to the foreground: a read issued now, which Glow decides. The fixture still serves
  // the match (the refusal was one request's), as a resumed match may (DM-22 3.1).
  fixture.activity.set('background'); fixture.activity.set('active'); await settle();
  assert.equal(count(fixture, 'messages'), reads + 1, 'not held back by the read made before the revocation');
  assert.equal(count(fixture, 'conversations'), lists + 1, 'nor the list read');
  let snapshot = fixture.store.getSnapshot();
  assert.deepEqual([snapshot.conversation.status, texts(fixture)], ['ready', [PRIVATE]]);
  assert.equal(unread(fixture), 1, 'the row is back from a list read made after the revocation');
  snapshot = fixture.store.getSnapshot();
  await gated.release();
  assert.equal(fixture.store.getSnapshot(), snapshot, 'the held responses still change nothing');
  // And when Glow refuses the read made afterwards, the conversation is revoked again.
  fixture.adapter.block('profile-jules', true, 'block:after-revocation'); await settle();
  assertRevoked(fixture);
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

const stale = { contract_version: 'gapp-api-v1', request_id: '00000090-0000-4000-8000-0000000000fe', code: 'stale_version', retryable: false };
/**
 * F1's transport (DM-27 1.2): answers the next head read made with a newer cursor with Glow's
 * `stale_version`, as C1 answers a cursor whose boundary it cannot place. The store then reloads
 * the newest page alone, which replaces the loaded window.
 */
function staleOnce() {
  let armed = false, answered = 0;
  return { arm: () => { armed = true; }, answered: () => answered, wrap: (transport: ChatTransport): ChatTransport => ({ ...transport,
    conversations: () => transport.conversations(), send: intent => transport.send(intent), readCursor: intent => transport.readCursor(intent),
    messages: async request => {
      if (!armed || request.cursor === null) return transport.messages(request);
      armed = false; answered += 1; return stale;
    } }) };
}
const A = 'A, viewed.', B = 'B, never viewed.';
type Reload = Readonly<{ own: number; listFirst?: boolean; sendB?: boolean }>;
/**
 * Jules sends A (with `listFirst`, the list is read then); A is viewed and its command succeeds;
 * then Jules sends B (unless `sendB` is false) and the member `own` messages; then one head read
 * is answered `stale`.
 */
async function staleReload(fixture: Setup, log: ReturnType<typeof cursorLog>, stalled: ReturnType<typeof staleOnce>, { own, listFirst = false, sendB = true }: Reload) {
  julesSends(fixture, A);
  if (listFirst) { fixture.store.refreshList(); await settle(); assert.equal(unread(fixture), 1); }
  await open(fixture);
  fixture.store.viewed(idsOf(fixture, A)); await settle(); await settle();
  assert.deepEqual(log.targets, idsOf(fixture, A), 'the command to A succeeded');
  if (sendB) julesSends(fixture, B);
  await ownSends(fixture, own);
  stalled.arm(); await fixture.timers.advance(CONVERSATION_POLL_MS); await settle();
  assert.equal(stalled.answered(), 1, 'one head read answered `stale`');
  assert.equal(fixture.fixture.requests().filter(request => request.operation === 'messages').at(-1)!.cursor, null, 'then the newest page alone');
  assert.equal(texts(fixture).includes(B), false, 'B lies before the reloaded window');
}

test('F1 (a): after a `stale` reload leaves `lastRead` outside the window, with no summary held, viewing the newest sends one command, to `seen`, and the count clears (DM-27 1.1, 1.2)', async () => {
  const log = cursorLog(), stalled = staleOnce(), fixture = await chatSetup(transport => log.wrap(stalled.wrap(transport)));
  await staleReload(fixture, log, stalled, { own: CONVERSATION_PAGE_LIMIT });
  assert.equal(texts(fixture).includes(A), false, '`lastRead` lies before the reloaded window');
  assert.deepEqual(fixture.store.getSnapshot().list.conversations, [], 'no summary held');
  fixture.store.viewed(newest(fixture)); await settle(); await settle();
  assert.deepEqual(log.targets.slice(1), newest(fixture), 'one command, to `seen`');
  fixture.store.showList(); await settle();
  assert.equal(unread(fixture), 0);
});

test('F1 (b): the same with a summary held at 0: viewing the newest sends nothing, and the next list read sends one command, to `seen`, and the count clears (DM-27 1.2; DM-25 3.4 (c))', async () => {
  const log = cursorLog(), stalled = staleOnce(), fixture = await chatSetup(transport => log.wrap(stalled.wrap(transport)));
  await staleReload(fixture, log, stalled, { own: CONVERSATION_PAGE_LIMIT, listFirst: true });
  assert.equal(unread(fixture), 0, 'the earlier command\'s response left the summary at 0');
  fixture.store.viewed(newest(fixture)); await settle(); await settle();
  assert.equal(log.targets.length, 1, 'the summary held shows 0 and the window holds no incoming message');
  fixture.store.refreshList(); await settle(); await settle();
  assert.deepEqual(log.targets.slice(1), newest(fixture), 'one command, to `seen`');
  assert.equal(unread(fixture), 0);
  fixture.store.refreshList(); await settle();
  assert.equal(unread(fixture), 0);
});

test('F1 (c): a `stale` reload that keeps `lastRead` within the newest page, with no summary held: the member\'s own newer messages in view send nothing (DM-27 1.2; DM-23 2.3)', async () => {
  const log = cursorLog(), stalled = staleOnce(), fixture = await chatSetup(transport => log.wrap(stalled.wrap(transport)));
  await staleReload(fixture, log, stalled, { own: CONVERSATION_PAGE_LIMIT - 1, sendB: false });
  assert.equal(texts(fixture)[0], A, '`lastRead` is the oldest message of the reloaded window');
  assert.deepEqual(fixture.store.getSnapshot().list.conversations, [], 'no summary held');
  for (let index = 0; index < 5; index++) { viewAll(fixture); fixture.store.viewed(idsOf(fixture, `Mine ${CONVERSATION_PAGE_LIMIT - 1}.`)); }
  await fixture.timers.advance(3 * CONVERSATION_POLL_MS);
  assert.equal(log.targets.length, 1, 'only the known position holds the move back');
});
