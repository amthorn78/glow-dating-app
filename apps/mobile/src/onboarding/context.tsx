import { createContext, useContext, useState, useSyncExternalStore, type PropsWithChildren } from 'react';
import type { BirthInput } from '../contracts/generated/gapp-api-v1';
import { createFixtureOnboardingStore, type OnboardingStore } from './store';

const StoreContext = createContext<OnboardingStore | null>(null);
type Draft = BirthInput;
const emptyDraft: Draft = { birth_date: '', local_time: null, time_precision: 'unknown', place_label: '', timezone_name: null, timezone_provenance: null };
const DraftContext = createContext<{ draft: Draft; setDraft: (draft: Draft) => void } | null>(null);

function DraftProvider({ children }: PropsWithChildren) {
  const { state } = useOnboarding();
  const [draft, setDraft] = useState<Draft>(state.birth?.input ?? emptyDraft);
  return <DraftContext.Provider value={{ draft, setDraft }}>{children}</DraftContext.Provider>;
}

function SessionDraft({ children }: PropsWithChildren) {
  const { state } = useOnboarding();
  const key = `${state.account?.account_id ?? 'signed-out'}:${state.account?.session_state ?? 'none'}:${state.generation}`;
  return <DraftProvider key={key}>{children}</DraftProvider>;
}

export function OnboardingProvider({ children }: PropsWithChildren) {
  const [store] = useState(() => createFixtureOnboardingStore({ isDevelopment: __DEV__, mode: process.env.EXPO_PUBLIC_GLOW_MODE, pause: () => new Promise((resolve) => setTimeout(resolve, 250)) }));
  return <StoreContext.Provider value={store}><SessionDraft>{children}</SessionDraft></StoreContext.Provider>;
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
