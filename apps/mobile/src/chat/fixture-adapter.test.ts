import assert from 'node:assert/strict';
import test from 'node:test';
import type { ConversationList, MessagePage } from '../contracts/generated/gapp-api-v1.ts';
import { parseApiError, parseAppResponse } from '../contracts/production.ts';
import { ChatFailure } from './client.ts';
import { ChatTransportError } from './transport.ts';
import { chatSetup, secondMatch } from './testing.ts';

type Setup = Awaited<ReturnType<typeof chatSetup>>;
const page = (fixture: Setup, matchId = fixture.matchId, cursor: string | null = null, limit = 50) => fixture.client.messages(matchId, cursor, limit);
const send = (fixture: Setup, text: string, key: string, matchId = fixture.matchId, version = 1) =>
  fixture.client.send(fixture.client.messageIntent(matchId, text, version, key));
const other = (fixture: Setup, text: string, delivery: 'accept' | 'hold' = 'accept', matchId = fixture.matchId) =>
  assert.equal(fixture.fixture.developmentOtherSend('profile-jules', matchId, text, delivery), true);
const code = async (promise: Promise<unknown>) => { try { await promise; } catch (error) { assert.ok(error instanceof ChatFailure); return error.code; } return 'ok'; };
const texts = (value: MessagePage) => value.messages.map(message => message.text);
/** A fixture participant's body: Glow's DTO, or the error code. */
function body<T>(value: unknown): T | string {
  try { return parseAppResponse(value).data as T; } catch { return parseApiError(value).code; }
}

test('a conversation exists only for a match the interactions fixture holds, and starts empty', async () => {
  const fixture = await chatSetup();
  const list = await fixture.client.conversations();
  assert.deepEqual(list.conversations, [{ kind: 'conversation', match_id: fixture.matchId, state: 'open', unread_count: 0, latest: null }]);
  const empty = await page(fixture);
  assert.deepEqual(empty, { kind: 'message_page', match_id: fixture.matchId, messages: [], older_cursor: null, newer_cursor: null });
  assert.equal(await code(page(fixture, '00000083-0000-4000-8000-0000000000ff')), 'unavailable');
  assert.equal(await code(fixture.client.messages('not-a-match', null, 20)), 'invalid_request');
});

test('messages come in acceptance order; own unsent appear only to their sender, the other member\'s never (F11)', async () => {
  const fixture = await chatSetup();
  await send(fixture, 'Own accepted.', 'k1');
  fixture.fixture.setDelivery('hold'); await send(fixture, 'Own held.', 'k2');
  fixture.fixture.setDelivery('fail'); await send(fixture, 'Own failed.', 'k3');
  other(fixture, 'Jules accepted.'); other(fixture, 'Jules held.', 'hold');
  const viewer = await page(fixture);
  assert.deepEqual(viewer.messages.map(message => [message.author, message.text, message.delivery]), [
    ['own', 'Own accepted.', 'accepted'], ['other', 'Jules accepted.', null], ['own', 'Own held.', 'pending'], ['own', 'Own failed.', 'failed']]);
  const julesView = body<MessagePage>(fixture.jules.messages({ match_id: fixture.matchId, cursor: null, limit: 50 }));
  assert.ok(typeof julesView !== 'string');
  assert.deepEqual(julesView.messages.map(message => [message.author, message.text]), [['other', 'Own accepted.'], ['own', 'Jules accepted.'], ['own', 'Jules held.']]);
  // A message the provider holds that Glow never sent reaches no page.
  fixture.fixture.developmentPlantProviderMessage('Planted text.');
  assert.equal(JSON.stringify(await page(fixture)).includes('Planted text.'), false);
});

test('a text the provider altered by one character is unavailable, one state with no reason (DM-22 2.1, 6.2)', async () => {
  const fixture = await chatSetup();
  other(fixture, 'Exactly this.');
  assert.equal(fixture.fixture.developmentAlterLatest(fixture.matchId), true);
  const [message] = (await page(fixture)).messages;
  assert.deepEqual(Object.keys(message!).sort(), ['at', 'author', 'content', 'delivery', 'submission_id', 'text']);
  assert.equal(message!.content, 'unavailable'); assert.equal(message!.text, null);
  assert.equal(JSON.stringify(await page(fixture)).includes('Exactly thi'), false);
});

test('the late-accepted message reaches the next newer page and counts as unread (DM-22 2.2, 6.3)', async () => {
  const fixture = await chatSetup();
  other(fixture, 'First, held.', 'hold'); other(fixture, 'Second, accepted.');
  const first = await page(fixture);
  assert.deepEqual(texts(first), ['Second, accepted.']);
  await fixture.client.readCursor(fixture.client.readCursorIntent(fixture.matchId, first.messages[0]!.submission_id));
  assert.equal((await fixture.client.conversations()).conversations[0]!.unread_count, 0);
  assert.equal(fixture.fixture.developmentDeliverHeld(), 1);
  const next = await page(fixture, fixture.matchId, first.newer_cursor);
  assert.deepEqual(texts(next), ['First, held.']);
  assert.equal((await fixture.client.conversations()).conversations[0]!.unread_count, 1);
  assert.deepEqual(texts(await page(fixture)), ['Second, accepted.', 'First, held.']);
});

test('unread counts only the other member\'s accepted messages after the cursor; the marker has no text (6.1, 6.3)', async () => {
  const fixture = await chatSetup();
  await send(fixture, 'Mine.', 'k1');
  other(fixture, 'Theirs, held.', 'hold');
  let list: ConversationList = await fixture.client.conversations();
  const own = (await page(fixture)).messages[0]!;
  // The other member's pending submission neither counts nor moves the viewer's marker.
  assert.deepEqual(list.conversations[0], { kind: 'conversation', match_id: fixture.matchId, state: 'open', unread_count: 0, latest: { submission_id: own.submission_id, at: own.at } });
  // The sender's own marker does follow their pending submission.
  const julesList = body<ConversationList>(fixture.jules.conversations());
  assert.ok(typeof julesList !== 'string');
  assert.notEqual(julesList.conversations[0]!.latest!.submission_id, own.submission_id);
  fixture.fixture.developmentDeliverHeld(); other(fixture, 'Theirs, two.');
  list = await fixture.client.conversations();
  assert.equal(list.conversations[0]!.unread_count, 2);
  assert.deepEqual(Object.keys(list.conversations[0]!.latest!).sort(), ['at', 'submission_id']);
});

test('the read cursor moves only forward, only to an accepted message of that match (point e)', async () => {
  const fixture = await chatSetup();
  other(fixture, 'One.'); other(fixture, 'Two.'); other(fixture, 'Held.', 'hold');
  fixture.fixture.setDelivery('hold'); await send(fixture, 'Mine, pending.', 'k1');
  const [one, two, pending] = (await page(fixture)).messages;
  const move = (id: string, matchId = fixture.matchId) => fixture.client.readCursor(fixture.client.readCursorIntent(matchId, id));
  assert.equal((await move(two!.submission_id)).unread_count, 0);
  assert.equal((await move(one!.submission_id)).unread_count, 0, 'an earlier target changes nothing');
  assert.equal(await code(move(pending!.submission_id)), 'unavailable', 'a pending submission is not a cursor target');
  const second = await secondMatch(fixture);
  assert.equal(await code(move(two!.submission_id, second)), 'unavailable', 'another match\'s message is not this match\'s');
  const held = fixture.fixture.inspect().submissions.find(row => row.text === 'Held.')!;
  assert.equal(await code(move(held.id)), 'unavailable');
});

test('a page cursor is opaque, bound to its match, and names an accepted message (6.4)', async () => {
  const fixture = await chatSetup();
  for (let index = 1; index <= 5; index++) other(fixture, `Message ${index}.`);
  const newest = await page(fixture, fixture.matchId, null, 2);
  assert.deepEqual(texts(newest), ['Message 4.', 'Message 5.']);
  const older = await page(fixture, fixture.matchId, newest.older_cursor, 2);
  assert.deepEqual(texts(older), ['Message 2.', 'Message 3.']);
  assert.deepEqual(texts(await page(fixture, fixture.matchId, older.older_cursor, 2)), ['Message 1.']);
  assert.equal((await page(fixture, fixture.matchId, newest.newer_cursor, 2)).newer_cursor, newest.newer_cursor, 'nothing new: poll again from the same place');
  const second = await secondMatch(fixture);
  assert.equal(await code(page(fixture, second, newest.newer_cursor)), 'stale');
  assert.equal(await code(page(fixture, second, newest.older_cursor)), 'stale');
  // The binding alone: a boundary that is the requested match's message, under another match's field.
  assert.equal(fixture.fixture.developmentOtherSend('profile-iris', second, 'Iris here.'), true);
  const irisId = (await page(fixture, second)).messages[0]!.submission_id;
  assert.equal(await code(page(fixture, second, `c1.n.${fixture.matchId.replaceAll('-', '')}.${irisId.replaceAll('-', '')}`)), 'stale');
  assert.equal((await page(fixture, second, `c1.o.${second.replaceAll('-', '')}.${irisId.replaceAll('-', '')}`)).messages.length, 0);
  fixture.fixture.setDelivery('hold'); await send(fixture, 'Pending.', 'k1');
  const pendingId = (await page(fixture)).messages.at(-1)!.submission_id;
  assert.equal(await code(page(fixture, fixture.matchId, `c1.n.${fixture.matchId.replaceAll('-', '')}.${pendingId.replaceAll('-', '')}`)), 'stale');
  assert.equal(await code(page(fixture, fixture.matchId, 'cursor-not-issued')), 'stale');
});

test('a retried send with the same key and payload is one message; a changed payload conflicts; authorize first', async () => {
  const fixture = await chatSetup();
  const intent = fixture.client.messageIntent(fixture.matchId, 'Hello.', 1, 'same-key');
  const first = await fixture.client.send(intent), again = await fixture.client.send(intent);
  assert.equal(again.submission_id, first.submission_id);
  assert.equal(fixture.fixture.inspect().submissions.length, 1);
  assert.equal(await code(fixture.client.send(fixture.client.messageIntent(fixture.matchId, 'Changed.', 1, 'same-key'))), 'conflict');
  assert.equal(await code(fixture.client.send(fixture.client.messageIntent(fixture.matchId, 'Stale.', 7, 'other-key'))), 'stale');
  // A lost response commits once; the retry recovers the same submission.
  fixture.fixture.setScenario('lost_response');
  const lost = fixture.client.messageIntent(fixture.matchId, 'Lost.', 1, 'lost-key');
  assert.equal(await code(fixture.client.send(lost)), 'offline');
  fixture.fixture.setScenario('normal');
  const recovered = await fixture.client.send(lost);
  assert.equal(fixture.fixture.inspect().submissions.filter(row => row.text === 'Lost.').length, 1);
  assert.equal((await page(fixture)).messages.filter(message => message.submission_id === recovered.submission_id).length, 1);
  // Offline never reaches the adapter's state.
  fixture.fixture.setScenario('offline');
  await assert.rejects(fixture.fixture.send(fixture.client.messageIntent(fixture.matchId, 'Offline.', 1, 'off-key')), ChatTransportError);
  assert.equal(fixture.fixture.inspect().submissions.some(row => row.text === 'Offline.'), false);
  // After a revocation, even an exact replay is refused.
  fixture.fixture.setScenario('normal');
  fixture.adapter.block('profile-jules', true, 'block:1');
  assert.equal(await code(fixture.client.send(intent)), 'unavailable');
});

test('the text read failing fails a page with accepted messages; an empty page reads no text (DM-22 2.4)', async () => {
  const fixture = await chatSetup();
  fixture.fixture.setOutage(true);
  assert.equal((await page(fixture)).messages.length, 0);
  other(fixture, 'Hello.');
  await assert.rejects(page(fixture), (error: unknown) => error instanceof ChatFailure && error.code === 'temporary' && error.retryable);
});

const revocations: Record<string, (fixture: Setup) => Promise<void> | void> = {
  'an unmatch by the member': fixture => { const prepared = fixture.adapter.unmatchIntent(fixture.matchId, 'unmatch:1'); fixture.adapter.execute(prepared.session, prepared.intent); },
  'an unmatch by fictional Jules': fixture => { fixture.adapter.execute(fixture.adapter.developmentSession('profile-jules'), { operation: 'unmatch', match_id: fixture.matchId, meta: { expected_version: 1, idempotency_key: 'unmatch:2' } }); },
  'a block by the member': fixture => { fixture.adapter.block('profile-jules', true, 'block:1'); },
  'a block by fictional Jules': fixture => { assert.equal(fixture.fixture.developmentOtherBlock('profile-jules'), true); },
  'the member\'s pause': async fixture => { await fixture.owner.profiles.setVisibility('pause'); },
  'fictional Jules\'s deletion': fixture => {
    const record = fixture.discovery.adapter.inspect('discovery-jules')!;
    fixture.discovery.adapter.replace({ ...record, facts: { ...record.facts!, account_state: 'deleted' } });
  },
  'fictional Jules\'s suspension': fixture => {
    const record = fixture.discovery.adapter.inspect('discovery-jules')!;
    fixture.discovery.adapter.replace({ ...record, facts: { ...record.facts!, account_state: 'suspended' } });
  },
  'the member\'s consent withdrawal': fixture => { fixture.owner.setConsent(false); },
  'a change of the member\'s preference policy source': fixture => { fixture.owner.profiles.developmentChange('policy'); },
};
for (const [name, revoke] of Object.entries(revocations)) test(`${name} refuses every read and send, for each member the fixture can show (point c)`, async () => {
  const fixture = await chatSetup();
  other(fixture, 'Before.'); await send(fixture, 'Mine before.', 'k1');
  const before = await page(fixture);
  await revoke(fixture);
  assert.deepEqual((await fixture.client.conversations()).conversations, []);
  assert.equal(await code(page(fixture)), 'unavailable');
  assert.equal(await code(page(fixture, fixture.matchId, before.older_cursor ?? before.newer_cursor)), 'unavailable');
  assert.equal(await code(send(fixture, 'After.', 'k2')), 'unavailable');
  assert.equal(await code(fixture.client.readCursor(fixture.client.readCursorIntent(fixture.matchId, before.messages[0]!.submission_id))), 'unavailable');
  // The refusal is Glow's generic code and says nothing about why.
  const raw = await fixture.fixture.messages({ match_id: fixture.matchId, cursor: null, limit: 20 }) as Record<string, unknown>;
  assert.deepEqual(Object.keys(raw).sort(), ['code', 'contract_version', 'request_id', 'retryable']);
  assert.equal(raw.code, 'not_found');
  for (const reply of [fixture.jules.messages({ match_id: fixture.matchId, cursor: null, limit: 20 }),
    fixture.jules.send({ operation: 'message', match_id: fixture.matchId, text: 'Jules after.', meta: { expected_version: 1, idempotency_key: 'j1' } }),
    fixture.jules.readCursor({ operation: 'read_cursor', match_id: fixture.matchId, submission_id: before.messages[0]!.submission_id })]) {
    assert.equal(body(reply), 'not_found');
  }
  const julesList = body<ConversationList>(fixture.jules.conversations());
  assert.ok(typeof julesList === 'string' || julesList.conversations.length === 0);
  assert.equal(fixture.fixture.inspect().submissions.some(row => row.text.endsWith('after.') || row.text === 'After.'), false);
});

for (const scenario of ['suspended', 'deletion_pending'] as const) test(`the member's own ${scenario} account sees no conversation, generically`, async () => {
  const fixture = await chatSetup();
  other(fixture, 'Before.');
  fixture.owner.scenario(scenario);
  assert.equal(await code(fixture.client.conversations()), 'unavailable');
  assert.equal(await code(page(fixture)), 'unavailable');
});

test('a signed-out member is unauthenticated; no request reaches a network', async () => {
  const fixture = await chatSetup();
  const original = globalThis.fetch;
  globalThis.fetch = () => { throw new Error('No network in the chat fixture.'); };
  try {
    other(fixture, 'Hello.'); await page(fixture); await fixture.client.conversations();
    fixture.owner.logout();
    assert.equal(await code(fixture.client.conversations()), 'signed_out');
    assert.equal(await code(page(fixture)), 'signed_out');
  } finally { globalThis.fetch = original; }
});

test('a fictional member without a valid session of their own can neither read nor send; the fixture closes it for both', async () => {
  const fixture = await chatSetup();
  other(fixture, 'Before.');
  const record = fixture.discovery.adapter.inspect('discovery-jules')!;
  fixture.discovery.adapter.replace({ ...record, facts: { ...record.facts!, session_state: 'revoked' } });
  assert.equal(body(fixture.jules.messages({ match_id: fixture.matchId, cursor: null, limit: 20 })), 'not_found');
  assert.equal(body(fixture.jules.send({ operation: 'message', match_id: fixture.matchId, text: 'Signed out.', meta: { expected_version: 1, idempotency_key: 'j1' } })), 'not_found');
  assert.equal(fixture.fixture.developmentOtherSend('profile-jules', fixture.matchId, 'Signed out too.'), false);
  // The interactions fixture's pair check treats the other member's revoked session as ineligible too (a recorded limit).
  assert.equal(await code(page(fixture)), 'unavailable');
});

test('a member of another match can neither read nor send in this one', async () => {
  const fixture = await chatSetup();
  const second = await secondMatch(fixture);
  other(fixture, 'Private to Jules and the member.');
  const iris = fixture.fixture.developmentMember('profile-iris');
  assert.equal(body(iris.messages({ match_id: fixture.matchId, cursor: null, limit: 20 })), 'not_found');
  assert.equal(fixture.fixture.developmentOtherSend('profile-iris', fixture.matchId, 'Not my conversation.'), false);
  const irisList = body<ConversationList>(iris.conversations());
  assert.ok(typeof irisList !== 'string');
  assert.deepEqual(irisList.conversations.map(entry => entry.match_id), [second]);
  assert.equal(fixture.fixture.inspect().submissions.some(row => row.text === 'Not my conversation.'), false);
});
