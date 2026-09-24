import { useSyncExternalStore } from 'react';
import { useOnboarding } from '../onboarding/context';
import type { OnboardingStore } from '../onboarding/store';
import { discoveryFor } from '../discovery/context';
import { FixtureInteractionAdapter } from './fixture-adapter';
import { InteractionStore } from './store';
const stores = new WeakMap<OnboardingStore, InteractionStore>();
export function interactionsFor(owner: OnboardingStore) {
  let store = stores.get(owner);
  if (!store) {
    const discovery = discoveryFor(owner);
    store = new InteractionStore(owner.profiles, discovery, new FixtureInteractionAdapter(owner.profiles, discovery.adapter),
      () => new Promise(resolve => setTimeout(resolve, 250)));
    stores.set(owner, store);
  }
  return store;
}
export function useInteractions() {
  const { store: owner } = useOnboarding();
  const store = interactionsFor(owner);
  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
  return { store, state };
}
