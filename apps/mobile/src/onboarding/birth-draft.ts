import type { BirthInput } from '../contracts/generated/gapp-api-v1.ts';
import type { BirthOutcome, OnboardingSnapshot, OnboardingStore } from './store.ts';

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

export type BirthDraftSnapshot = Readonly<{ owner: string; draft: Readonly<BirthInput> }>;
const snapshot = (owner: string, draft: BirthInput): BirthDraftSnapshot => Object.freeze({ owner, draft: Object.freeze({ ...draft }) });

/** Synchronous private form state: consecutive callbacks never merge or submit
 * a render-captured draft. Authority remains the onboarding store's source token.
 */
export class BirthDraftStore {
  private store: OnboardingStore;
  private value: BirthDraftSnapshot;
  private listeners = new Set<() => void>();

  constructor(store: OnboardingStore) {
    this.store = store;
    const state = store.getSnapshot();
    this.value = snapshot(birthDraftOwner(state), initialBirthDraft(state));
  }
  readonly getSnapshot = (): BirthDraftSnapshot => {
    const state = this.store.getSnapshot(), owner = birthDraftOwner(state);
    if (this.value.owner !== owner) this.value = snapshot(owner, initialBirthDraft(state));
    return this.value;
  };
  readonly subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener);
    const unsubscribe = this.store.subscribe(listener);
    return () => { this.listeners.delete(listener); unsubscribe(); };
  };
  private owns(owner: string): boolean {
    const state = this.store.getSnapshot();
    return owner === birthDraftOwner(state) && state.account?.state === 'active' && state.account.session_state === 'valid';
  }
  private publish(owner: string, draft: BirthInput): void {
    this.value = snapshot(owner, draft);
    this.listeners.forEach(listener => listener());
  }
  update(patch: Partial<BirthInput>, owner: string): void {
    if (!this.owns(owner)) return;
    const current = this.getSnapshot().draft;
    const next = { ...current, ...patch, timezone_name: null, timezone_provenance: null };
    // Precision changes use the latest local time, not a retained button's draft.
    next.local_time = next.time_precision === 'unknown' ? null : next.local_time ?? '';
    this.publish(owner, next);
  }
  replace(draft: BirthInput, owner: string): void {
    if (!this.owns(owner)) return;
    this.publish(owner, draft);
  }
  save(outcome: BirthOutcome, owner: string): Promise<void> | undefined {
    if (!this.owns(owner)) return;
    const input = { ...this.getSnapshot().draft };
    return this.store.saveBirth(input, outcome);
  }
}
