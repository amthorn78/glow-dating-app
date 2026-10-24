import assert from 'node:assert/strict';
import test from 'node:test';
import type { Error as ApiError, MessagePage } from '../contracts/generated/gapp-api-v1.ts';
import { validateAppIntent } from '../contracts/generated/validators.js';
import { ChatClient, ChatFailure } from './client.ts';
import type { ChatTransport } from './transport.ts';

const MATCH = '00000083-0000-4000-8000-000000000003';
const OTHER_MATCH = '00000083-0000-4000-8000-000000000007';
const SUBMISSION = '00000091-0000-4000-8000-000000000001';
const REQUEST = '00000090-0000-4000-8000-000000000001';
const envelope = (data: object) => ({ contract_version: 'gapp-api-v1', request_id: REQUEST, data });
const message = (id = SUBMISSION) => ({ submission_id: id, author: 'other', at: '2026-09-23T12:00:01Z', content: 'text', text: 'Hello.', delivery: null });
const pageBody = (overrides: Partial<MessagePage> = {}) => envelope({ kind: 'message_page', match_id: MATCH, messages: [message()], older_cursor: null, newer_cursor: 'c1.n.x', ...overrides });
const summary = { kind: 'conversation', match_id: MATCH, state: 'open', unread_count: 0, latest: null };

/** A transport that answers one fixed body and records what it was sent. */
function transport(body: unknown) {
  const sent: unknown[] = [];
  const answer = async (request?: unknown) => { sent.push(request); if (body instanceof Error) throw body; return body; };
  const value: ChatTransport = { conversations: () => answer(), messages: answer, send: answer, readCursor: answer };
  return { value, sent };
}
async function failure(promise: Promise<unknown>): Promise<ChatFailure> {
  try { await promise; } catch (error) { assert.ok(error instanceof ChatFailure); return error; }
  assert.fail('expected a refusal');
}

test('a valid response reaches the caller frozen, after the generated validators', async () => {
  const page = await new ChatClient(transport(pageBody()).value).messages(MATCH, null, 20);
  assert.equal(page.messages[0]!.text, 'Hello.');
  assert.ok(Object.isFrozen(page) && Object.isFrozen(page.messages[0]));
  const list = await new ChatClient(transport(envelope({ kind: 'conversation_list', conversations: [summary] })).value).conversations();
  assert.equal(list.conversations.length, 1);
  const submission = await new ChatClient(transport(envelope({ kind: 'message', submission_id: SUBMISSION, version: 1, state: 'pending' })).value)
    .send({ operation: 'message', match_id: MATCH, text: 'Hi.', meta: { expected_version: 1, idempotency_key: 'k' } });
  assert.equal(submission.state, 'pending');
});

test('a response the validators refuse is refused whole, never partly used', async () => {
  const cases: Record<string, unknown> = {
    'another kind': envelope(summary),
    'another match': pageBody({ match_id: OTHER_MATCH }),
    'a submission twice': pageBody({ messages: [message(), message()] as MessagePage['messages'] }),
    'an extra field': { ...pageBody(), extra: true },
    'a nested extra field': pageBody({ messages: [{ ...message(), reactions: [] }] as unknown as MessagePage['messages'] }),
    'unavailable with a reason': pageBody({ messages: [{ ...message(), content: 'unavailable', text: null, reason: 'retention' }] as unknown as MessagePage['messages'] }),
    'another member\'s delivery state': pageBody({ messages: [{ ...message(), delivery: 'pending' }] as unknown as MessagePage['messages'] }),
    'a time with milliseconds': pageBody({ messages: [{ ...message(), at: '2026-09-23T12:00:01.000Z' }] as unknown as MessagePage['messages'] }),
    'no envelope': { kind: 'message_page', match_id: MATCH, messages: [], older_cursor: null, newer_cursor: null },
    'text': 'Hello.', 'null': null,
  };
  for (const [name, body] of Object.entries(cases)) {
    const refused = await failure(new ChatClient(transport(body).value).messages(MATCH, null, 20));
    assert.equal(refused.code, 'invalid_response', name);
  }
  const duplicateList = envelope({ kind: 'conversation_list', conversations: [summary, summary] });
  assert.equal((await failure(new ChatClient(transport(duplicateList).value).conversations())).code, 'invalid_response');
  const cursorOther = envelope({ ...summary, match_id: OTHER_MATCH });
  assert.equal((await failure(new ChatClient(transport(cursorOther).value).readCursor({ operation: 'read_cursor', match_id: MATCH, submission_id: SUBMISSION }))).code, 'invalid_response');
});

test('Glow\'s error codes map to Glow\'s own states; a lost request is offline', async () => {
  const expected: Record<ApiError['code'], string> = {
    not_found: 'unavailable', forbidden: 'unavailable', unauthenticated: 'signed_out', stale_version: 'stale', provider_unavailable: 'temporary',
    rate_limited: 'temporary', state_conflict: 'temporary', idempotency_conflict: 'conflict', invalid_request: 'invalid_request',
    policy_unresolved: 'invalid_request', unsupported_contract: 'invalid_request',
  };
  for (const [code, state] of Object.entries(expected)) {
    const refused = await failure(new ChatClient(transport({ contract_version: 'gapp-api-v1', request_id: REQUEST, code, retryable: code === 'provider_unavailable' }).value).conversations());
    assert.equal(refused.code, state, code);
    assert.equal(refused.retryable, code === 'provider_unavailable');
  }
  const lost = await failure(new ChatClient(transport(new Error('socket hang up')).value).conversations());
  assert.deepEqual([lost.code, lost.retryable, lost.message.includes('socket')], ['offline', true, false]);
});

test('every intent passes parseAppIntent before it is sent; an invalid one never reaches the transport', async () => {
  const spy = transport(envelope({ kind: 'message', submission_id: SUBMISSION, version: 1, state: 'pending' }));
  const client = new ChatClient(spy.value);
  for (const text of ['', '   ', ' \n', 'x'.repeat(4001)]) assert.throws(() => client.messageIntent(MATCH, text, 1, 'k'), ChatFailure);
  assert.throws(() => client.messageIntent('not-a-match', 'Hi.', 1, 'k'), ChatFailure);
  assert.throws(() => client.readCursorIntent(MATCH, 'not-a-submission'), ChatFailure);
  await assert.rejects(client.send({ operation: 'message', match_id: MATCH, text: '', meta: { expected_version: 1, idempotency_key: 'k' } }), ChatFailure);
  await assert.rejects(client.messages(MATCH, 'has space', 20), ChatFailure);
  await assert.rejects(client.messages(MATCH, null, 51), ChatFailure);
  assert.equal(spy.sent.length, 0);
  await client.send(client.messageIntent(MATCH, 'Hi.', 1, 'k'));
  await client.readCursor(client.readCursorIntent(MATCH, SUBMISSION)).catch(() => undefined);
  assert.equal(spy.sent.length, 2);
  for (const intent of spy.sent) assert.equal(validateAppIntent(intent), true);
});
