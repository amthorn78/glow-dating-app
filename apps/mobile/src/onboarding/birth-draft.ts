import type { BirthInput } from '../contracts/generated/gapp-api-v1.ts';
import type { OnboardingSnapshot, OnboardingStore } from './store.ts';

export function birthDraftOwner(state: OnboardingSnapshot): string {
  return `${state.account?.account_id ?? 'signed-out'}:${state.account?.state ?? 'none'}:${state.account?.session_state ?? 'none'}:${state.generation}:${state.birthDraftRevision}`;
}

export function initialBirthDraft(state: OnboardingSnapshot): BirthInput {
  const active = state.account?.state === 'active' && state.account.session_state === 'valid';
  return active && state.birth ? state.birth.input : {
    birth_date: active ? state.adultBirthDate ?? '' : '', local_time: null, time_precision: 'unknown',
    place_label: '', timezone_name: null, timezone_provenance: null,
  };
}

/** Capture the authority revision when creating an edit/submit callback. */
export function bindBirthDraftAction<T>(store: OnboardingStore, state: OnboardingSnapshot, action: () => T): () => T | undefined {
  const owner = birthDraftOwner(state);
  return () => {
    const current = store.getSnapshot();
    if (birthDraftOwner(current) !== owner || current.account?.state !== 'active' || current.account.session_state !== 'valid') return;
    return action();
  };
}
