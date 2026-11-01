import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { MediaStore } from '../media/store.ts';
import { syntheticSelection } from '../media/policy.ts';
import type { ProfileAuthority } from '../profiles/policy.ts';

/**
 * ADR 0003, decision 3 outside chat (M05 finding 19): the member screens say what the preview
 * does without naming a provider, its objects or its wording. The screens cannot render in
 * Node, so their source (comments removed) is read; the media store's feedback, which the
 * media screen shows, is read from the store itself.
 */
const PROVIDER_TERMS = /\b(providers?|stream|getstream|cloudflare|allauth|channels?)\b/i;
const SCREENS = [
  '../interactions/screen.tsx', // the match screen's messaging line
  '../app/media.tsx', // the photo screen, its lifecycle notes and its developer panel
  '../app/verify.tsx', // email verification
  '../onboarding/shell.tsx', // the fixture outcome panel the onboarding screens show
];
const withoutComments = (source: string) => source.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\{\/\*[\s\S]*?\*\/\}/g, '').replace(/(^|[^:'"`])\/\/.*$/gm, '$1');

for (const screen of SCREENS) test(`${screen.slice(3)} names no provider in what members see (M05 finding 19; ADR 0003, decision 3)`, () => {
  const source = withoutComments(readFileSync(new URL(screen, import.meta.url), 'utf8'));
  const lines = source.split('\n').filter(line => PROVIDER_TERMS.test(line)).map(line => line.trim());
  assert.deepEqual(lines, []);
});

test('the media store\'s removal and purge feedback names no provider (M05 finding 19)', async () => {
  const authority: ProfileAuthority = { ownerId: '11111111-1111-4111-8111-111111111111', generation: 1,
    accountVersion: 1, accountState: 'active', sessionState: 'valid', adult: true, consentCurrent: true,
    sourceRevision: 0, consentRevision: '1:development-consent-1' };
  const media = new MediaStore({ isDevelopment: true, mode: 'fixture' }); media.synchronize(authority);
  media.select(syntheticSelection()); await media.requestUpload();
  const id = media.getSnapshot().collection.items.at(-1)!.asset_id;
  const feedback: (string | null)[] = [];
  await media.upload(id);
  for (const event of ['review', 'approve'] as const) { await media.developerEvent(id, event); feedback.push(media.getSnapshot().message); }
  await media.remove(id); feedback.push(media.getSnapshot().message);
  await media.developerEvent(id, 'purged'); feedback.push(media.getSnapshot().message);
  assert.equal(media.getSnapshot().collection.items.find(item => item.asset_id === id)?.state, 'removed');
  assert.equal(feedback.length, 4);
  for (const message of feedback) {
    assert.equal(typeof message, 'string');
    assert.doesNotMatch(message!, PROVIDER_TERMS, message!);
  }
});
