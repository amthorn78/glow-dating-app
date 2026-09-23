import { createContext, useContext, useState, useSyncExternalStore, type PropsWithChildren } from 'react';
import type { BirthInput } from '../contracts/generated/gapp-api-v1';
import { createFixtureOnboardingStore, type BirthOutcome, type OnboardingStore } from './store';
import { BirthDraftStore } from './birth-draft';

const StoreContext = createContext<OnboardingStore | null>(null);
type Draft = BirthInput;
const DraftContext = createContext<{ draft: Draft; setDraft: (draft: Draft) => void; updateDraft: (patch: Partial<Draft>) => void;
  saveDraft: (outcome: BirthOutcome) => Promise<void> | undefined } | null>(null);

function DraftProvider({ children }: PropsWithChildren) {
  const { store } = useOnboarding();
  const [drafts] = useState(() => new BirthDraftStore(store));
  const { owner, draft } = useSyncExternalStore(drafts.subscribe, drafts.getSnapshot, drafts.getSnapshot);
  // Only the authority token is captured. Edits and submit read the latest draft
  // synchronously, even when several input events precede the next React render.
  // Keeping this provider mounted preserves recovery forms and navigation history.
  return <DraftContext.Provider value={{ draft, setDraft: next => drafts.replace(next, owner),
    updateDraft: patch => drafts.update(patch, owner), saveDraft: outcome => drafts.save(outcome, owner) }}>{children}</DraftContext.Provider>;
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

export function useMedia() {
  const { store } = useOnboarding();
  const media = store.media;
  const state = useSyncExternalStore(media.subscribe, media.getSnapshot, media.getSnapshot);
  return { media, state };
}
