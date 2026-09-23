import { createContext, useContext, useState, useSyncExternalStore, type PropsWithChildren } from 'react';
import type { BirthInput } from '../contracts/generated/gapp-api-v1';
import { createFixtureOnboardingStore, type BirthOutcome, type OnboardingStore } from './store';
import { bindBirthDraftAction, birthDraftOwner, initialBirthDraft } from './birth-draft';

const StoreContext = createContext<OnboardingStore | null>(null);
type Draft = BirthInput;
const DraftContext = createContext<{ draft: Draft; setDraft: (draft: Draft) => void; saveDraft: (outcome: BirthOutcome) => Promise<void> | undefined } | null>(null);

function DraftProvider({ children }: PropsWithChildren) {
  const { state, store } = useOnboarding();
  const owner = birthDraftOwner(state);
  const initialDraft = initialBirthDraft(state);
  const [saved, setSaved] = useState(() => ({ owner, draft: initialDraft }));
  // Adjust only this provider's state before its children render. A React key
  // here would also remount the navigator, clearing recovery forms and history.
  const draft = saved.owner === owner ? saved.draft : initialDraft;
  if (saved.owner !== owner) setSaved({ owner, draft: initialDraft });
  function setDraft(next: Draft) {
    bindBirthDraftAction(store, state, () => setSaved({ owner, draft: next }))();
  }
  function saveDraft(outcome: BirthOutcome) {
    return bindBirthDraftAction(store, state, () => store.saveBirth(draft, outcome))();
  }
  return <DraftContext.Provider value={{ draft, setDraft, saveDraft }}>{children}</DraftContext.Provider>;
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

/** The store owns private drafts so retained screens never keep a second private copy. */
export function useProfiles() {
  const { store } = useOnboarding();
  const profiles = store.profiles;
  const state = useSyncExternalStore(profiles.subscribe, profiles.getSnapshot, profiles.getSnapshot);
  return { profiles, state };
}
