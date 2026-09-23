import { createContext, useContext, useState, useSyncExternalStore, type PropsWithChildren } from 'react';
import type { BirthInput } from '../contracts/generated/gapp-api-v1';
import { createFixtureOnboardingStore, type OnboardingSnapshot, type OnboardingStore } from './store';

const StoreContext = createContext<OnboardingStore | null>(null);
type Draft = BirthInput;
const emptyDraft: Draft = { birth_date: '', local_time: null, time_precision: 'unknown', place_label: '', timezone_name: null, timezone_provenance: null };
const DraftContext = createContext<{ draft: Draft; setDraft: (draft: Draft) => void } | null>(null);

function draftOwner(state: OnboardingSnapshot): string {
  return `${state.account?.account_id ?? 'signed-out'}:${state.account?.state ?? 'none'}:${state.account?.session_state ?? 'none'}:${state.generation}`;
}

function DraftProvider({ children }: PropsWithChildren) {
  const { state, store } = useOnboarding();
  const owner = draftOwner(state);
  const initialDraft = state.account?.state === 'active' && state.account.session_state === 'valid'
    ? state.birth?.input ?? emptyDraft : emptyDraft;
  const [saved, setSaved] = useState(() => ({ owner, draft: initialDraft }));
  // Adjust only this provider's state before its children render. A React key
  // here would also remount the navigator, clearing recovery forms and history.
  const draft = saved.owner === owner ? saved.draft : initialDraft;
  if (saved.owner !== owner) setSaved({ owner, draft: initialDraft });
  function setDraft(next: Draft) {
    const current = store.getSnapshot();
    // A callback retained by an older screen cannot write into a new session.
    if (draftOwner(current) !== owner || current.account?.state !== 'active' || current.account.session_state !== 'valid') return;
    setSaved({ owner, draft: next });
  }
  return <DraftContext.Provider value={{ draft, setDraft }}>{children}</DraftContext.Provider>;
}

export function OnboardingProvider({ children }: PropsWithChildren) {
  const [store] = useState(() => createFixtureOnboardingStore({ isDevelopment: __DEV__, mode: process.env.EXPO_PUBLIC_GLOW_MODE, pause: () => new Promise((resolve) => setTimeout(resolve, 250)) }));
  return <StoreContext.Provider value={store}><DraftProvider>{children}</DraftProvider></StoreContext.Provider>;
}

export function useOnboarding() {
  const store = useContext(StoreContext);
  if (!store) throw new Error('Onboarding provider is required.');
  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
  return { store, state };
}

export function useBirthDraft() {
  const context = useContext(DraftContext);
  if (!context) throw new Error('Private draft provider is required.');
  return context;
}
