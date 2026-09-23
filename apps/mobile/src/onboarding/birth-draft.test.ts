import assert from 'node:assert/strict';
import test from 'node:test';
import { bindBirthDraftAction, initialBirthDraft } from './birth-draft.ts';
import { createFixtureOnboardingStore, FIXTURE_PASSWORD } from './store.ts';
import type { BirthInput } from '../contracts/generated/gapp-api-v1.ts';

const input: BirthInput = { birth_date: '1990-06-15', local_time: null, time_precision: 'unknown',
  place_label: 'Discarded Fictional Harbor', timezone_name: null, timezone_provenance: null };
async function ready() {
  const store = createFixtureOnboardingStore({ isDevelopment: true, mode: 'fixture' });
  await store.account('register', 'alex@example.invalid', FIXTURE_PASSWORD);
  await store.verify();
  store.setAdultDate(input.birth_date);
  store.setConsent(true);
  return store;
}

for (const accepted of [true, false]) {
  test(`obsolete ${accepted ? 'accepted' : 'unsaved'} callbacks cannot restore discarded birth facts`, async () => {
    const store = await ready();
    if (accepted) await store.saveBirth(input);
    let draft: BirthInput;
    const oldState = store.getSnapshot();
    const staleEdit = bindBirthDraftAction(store, oldState, () => { draft = input; });
    const staleSubmit = bindBirthDraftAction(store, oldState, () => store.saveBirth(input));
    store.setAdultDate('1992-07-16');
    draft = initialBirthDraft(store.getSnapshot());
    staleEdit();
    await staleSubmit();
    assert.equal(draft.birth_date, '1992-07-16');
    assert.equal(draft.place_label, '');
    assert.equal(store.getSnapshot().adultBirthDate, '1992-07-16');
    assert.equal(store.getSnapshot().birth, null);
    // Returning to the original date still cannot revive an older callback.
    store.setAdultDate(input.birth_date);
    await staleSubmit();
    assert.equal(store.getSnapshot().birth, null);
    const currentInput = { ...input, place_label: 'Deliberately entered current place' };
    await bindBirthDraftAction(store, store.getSnapshot(), () => store.saveBirth(currentInput))();
    assert.deepEqual(store.getSnapshot().birth?.input, currentInput);
  });
}

test('ordinary publications, same-date saves and resolution retry preserve deliberate unsaved edits', async () => {
  const store = await ready();
  await store.saveBirth(input, 'unavailable');
  const edited = { ...input, place_label: 'Unsaved Fictional Island' };
  let draft = input;
  const update = bindBirthDraftAction(store, store.getSnapshot(), () => { draft = edited; });
  store.saveCheckpoint();
  store.setAdultDate(input.birth_date);
  store.setConsent(true);
  await store.retryBirth();
  update();
  assert.deepEqual(draft, edited);
  assert.equal(store.getSnapshot().birth?.resolution, 'pending');
});

test('an accepted replacement rejects a callback captured before that replacement', async () => {
  const store = await ready();
  await store.saveBirth(input);
  const staleSubmit = bindBirthDraftAction(store, store.getSnapshot(), () => store.saveBirth(input));
  const currentInput = { ...input, place_label: 'Replacement Fictional Island' };
  await store.saveBirth(currentInput);
  await staleSubmit();
  assert.deepEqual(store.getSnapshot().birth?.input, currentInput);
  assert.deepEqual(initialBirthDraft(store.getSnapshot()), currentInput);
});
