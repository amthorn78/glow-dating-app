import { useCallback, useSyncExternalStore } from 'react';
import { useFocusEffect } from 'expo-router';
import { useOnboarding } from '../onboarding/context';
import type { OnboardingStore } from '../onboarding/store';
import { FixtureDiscoveryAdapter, type DiscoveryMode } from './fixture-adapter';
import { DiscoveryStore } from './store';
const stores = new WeakMap<OnboardingStore, DiscoveryStore>();
export function discoveryFor(owner: OnboardingStore) {
  let store = stores.get(owner);
  if (!store) {
    store = new DiscoveryStore(owner.profiles, new FixtureDiscoveryAdapter(owner.profiles, {
      isDevelopment: __DEV__, mode: process.env.EXPO_PUBLIC_GLOW_MODE, pause: () => new Promise(resolve => setTimeout(resolve, 250)),
    }));
    stores.set(owner, store);
  }
  return store;
}
export function useDiscovery(mode: DiscoveryMode) {
  const { store: owner } = useOnboarding();
  const store = discoveryFor(owner);
  const snapshot = useCallback(() => store.getSnapshot(mode), [store, mode]);
  const state = useSyncExternalStore(store.subscribe, snapshot, snapshot);
  useFocusEffect(useCallback(() => { store.enter(mode); }, [store, mode]));
  return { state, discovery: store };
}
