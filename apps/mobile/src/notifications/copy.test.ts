import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import corpus from '../../../../packages/contracts/fixtures/interactions-v1.json' with { type: 'json' };
import { ALL_COPY, DENIED, FAILURE_COPY, INTRO, KINDS, KIND_SENDS, PUSH_WORDING } from './copy.ts';

/**
 * P06.3, Outcome 3: the new copy names no provider, Expo, Apple or Google push service (ADR 0003,
 * decision 3), and says what each kind sends in Glow's wording, with no name, photo or message text.
 */
const PROVIDER_TERMS = /expo|apple|google|apns|fcm|firebase|android|\bios\b|onesignal|pusher|amazon|\bsns\b|stream|push service|token|provider/i;

test('the new copy names no provider, platform or push service', () => {
  assert.ok(ALL_COPY.length > 20);
  for (const sentence of ALL_COPY) assert.doesNotMatch(sentence, PROVIDER_TERMS, sentence);
});

test('each kind says what it sends, in the server\'s exact wording, before any request', () => {
  for (const kind of KINDS) {
    assert.ok(KIND_SENDS[kind].includes(`“${PUSH_WORDING[kind]}”`), kind);
    assert.match(KIND_SENDS[kind], /nothing else\.$/);
  }
  // The wording the composer sends (glow_domain/notifications.py, WORDING) is the wording shown here.
  const server = readFileSync(new URL('../../../../services/api/glow_domain/notifications.py', import.meta.url), 'utf8');
  for (const kind of KINDS) assert.ok(server.includes(`"${kind}": "${PUSH_WORDING[kind]}"`), kind);
  assert.match(INTRO, /only when you turn one on/);
});

test('the copy carries no name, photo or message text, and denial says Glow works without notifications', () => {
  const names = corpus.identities.map(identity => identity.profile_id.replace(/^profile-/, ''));
  assert.ok(names.length > 0);
  for (const sentence of ALL_COPY) {
    for (const name of names) assert.doesNotMatch(sentence, new RegExp(`\\b${name}\\b`, 'i'), sentence);
    assert.doesNotMatch(sentence, /https?:|\.png|\.jpg|\{|\}/, sentence);
  }
  assert.equal(DENIED, 'Notifications are off in this device’s settings. Glow works without them.');
  assert.ok(Object.values(FAILURE_COPY).every(sentence => !/\d/.test(sentence)));
});
