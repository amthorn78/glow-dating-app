import assert from 'node:assert/strict';
import test from 'node:test';
import { bindBirthDraftAction, BirthDraftStore, initialBirthDraft } from './birth-draft.ts';
import { createFixtureOnboardingStore, FIXTURE_PASSWORD } from './store.ts';
import type { BirthInput } from '../contracts/generated/gapp-api-v1.ts';

const input: BirthInput = { birth_date: '1990-06-15', local_time: null, time_precision: 'unknown',
  place_label: 'Discarded Fictional Harbor', timezone_name: null, timezone_provenance: null };
async function ready(pause: () => Promise<void> = () => Promise.resolve()) {
  const store = createFixtureOnboardingStore({ isDevelopment: true, mode: 'fixture', pause });
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

test('successive edits and immediate submit from one rendered authority preserve both fields', async () => {
  const store = await ready(), drafts = new BirthDraftStore(store);
  // A text replacement may start from a blank field; a retained render must not
  // put that blank value back when the following place event is handled.
  drafts.update({ birth_date: '' }, drafts.getSnapshot().owner);
  const rendered = drafts.getSnapshot();
  const editDate = (birth_date: string) => drafts.update({ birth_date }, rendered.owner);
  const editPlace = (place_label: string) => drafts.update({ place_label }, rendered.owner);
  const submit = () => drafts.save('pending', rendered.owner);
  // No new callback or render is created between these input events and submit.
  editDate('2010-09-23');
  editPlace('Underage Fictional Harbor');
  await submit();
  assert.equal(store.getSnapshot().birth?.input.birth_date, '2010-09-23');
  assert.equal(store.getSnapshot().birth?.input.place_label, 'Underage Fictional Harbor');
  assert.equal(store.getSnapshot().adultBirthDate, '2010-09-23');
  assert.equal(store.getSnapshot().stage, 'eligibility');
  assert.equal(store.getSnapshot().adult, 'fail');
});

test('current draft survives unrelated publications and subscriptions are disposed', async () => {
  const store = await ready(), drafts = new BirthDraftStore(store);
  const owner = drafts.getSnapshot().owner;
  let notifications = 0;
  const unsubscribe = drafts.subscribe(() => { notifications += 1; });
  drafts.update({ place_label: 'Unsaved Fictional Island' }, owner);
  const edited = drafts.getSnapshot();
  store.saveCheckpoint();
  store.setAdultDate(input.birth_date);
  store.setConsent(true);
  assert.equal(drafts.getSnapshot(), edited);
  assert.equal(drafts.getSnapshot().draft.place_label, 'Unsaved Fictional Island');
  assert.ok(notifications > 1);
  unsubscribe();
  const previous = notifications;
  drafts.update({ place_label: 'Another Fictional Island' }, owner);
  store.saveCheckpoint();
  assert.equal(notifications, previous);
});

test('source replacement rejects retained edit, replacement and submit before another render', async () => {
  const store = await ready(), drafts = new BirthDraftStore(store);
  const owner = drafts.getSnapshot().owner;
  drafts.update({ place_label: input.place_label }, owner);
  store.setAdultDate('1992-07-16');
  drafts.update({ birth_date: input.birth_date, place_label: input.place_label }, owner);
  drafts.replace(input, owner);
  assert.equal(drafts.save('pending', owner), undefined);
  assert.equal(drafts.getSnapshot().draft.birth_date, '1992-07-16');
  assert.equal(drafts.getSnapshot().draft.place_label, '');
  assert.equal(store.getSnapshot().birth, null);
  store.setAdultDate(input.birth_date);
  drafts.update({ place_label: input.place_label }, owner);
  assert.equal(drafts.save('pending', owner), undefined);
  assert.equal(drafts.getSnapshot().draft.place_label, '');
  const replacementOwner = drafts.getSnapshot().owner;
  drafts.update({ place_label: 'Current Fictional Harbor' }, replacementOwner);
  await drafts.save('pending', replacementOwner);
  assert.equal(store.getSnapshot().birth?.input.place_label, 'Current Fictional Harbor');
  assert.notEqual(drafts.getSnapshot().owner, replacementOwner);
});

test('logout and account replacement clear private drafts and reject retained callbacks', async () => {
  const store = await ready(), drafts = new BirthDraftStore(store);
  const owner = drafts.getSnapshot().owner;
  drafts.replace(input, owner);
  store.logout();
  drafts.update({ place_label: input.place_label }, owner);
  drafts.replace(input, owner);
  assert.equal(drafts.save('pending', owner), undefined);
  assert.equal(drafts.getSnapshot().draft.birth_date, '');
  assert.equal(drafts.getSnapshot().draft.place_label, '');
  await store.account('sign_in', 'sam@example.invalid', FIXTURE_PASSWORD);
  await store.verify();
  store.setAdultDate('1995-03-10');
  store.setConsent(true);
  drafts.replace(input, owner);
  assert.equal(drafts.save('pending', owner), undefined);
  assert.equal(drafts.getSnapshot().draft.birth_date, '1995-03-10');
  assert.equal(drafts.getSnapshot().draft.place_label, '');
});

test('submit captures current draft before awaiting and caller mutation cannot change it', async () => {
  let delayed = false, release: (() => void) | undefined;
  const store = await ready(() => delayed ? new Promise<void>(resolve => { release = resolve; }) : Promise.resolve());
  const drafts = new BirthDraftStore(store), owner = drafts.getSnapshot().owner;
  const replacement = { ...input, place_label: 'Submitted Fictional Harbor' };
  drafts.replace(replacement, owner);
  replacement.place_label = 'Mutated caller value';
  delayed = true;
  const pending = drafts.save('pending', owner);
  drafts.update({ place_label: 'Later Unsaved Harbor' }, owner);
  release!();
  await pending;
  assert.equal(store.getSnapshot().birth?.input.place_label, 'Submitted Fictional Harbor');
  assert.equal(drafts.getSnapshot().draft.place_label, 'Submitted Fictional Harbor');
});

test('successive precision and time edits merge current values and keep unknown time empty', async () => {
  const store = await ready(), drafts = new BirthDraftStore(store);
  const owner = drafts.getSnapshot().owner;
  const edit = (patch: Partial<BirthInput>) => drafts.update(patch, owner);
  edit({ time_precision: 'known' });
  edit({ local_time: '08:09:10' });
  edit({ time_precision: 'approximate' });
  assert.equal(drafts.getSnapshot().draft.local_time, '08:09:10');
  assert.equal(drafts.getSnapshot().draft.time_precision, 'approximate');
  edit({ time_precision: 'unknown' });
  edit({ local_time: '11:12:13' });
  assert.equal(drafts.getSnapshot().draft.local_time, null);
  edit({ time_precision: 'known' });
  assert.equal(drafts.getSnapshot().draft.local_time, '');
  assert.equal(drafts.getSnapshot().draft.timezone_name, null);
  assert.equal(drafts.getSnapshot().draft.timezone_provenance, null);
});
