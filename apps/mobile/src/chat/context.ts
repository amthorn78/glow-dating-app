import { useSyncExternalStore } from 'react';
import { AppState } from 'react-native';
import { useOnboarding } from '../onboarding/context';
import type { OnboardingStore } from '../onboarding/store';
import { interactionsFor } from '../interactions/context';
import { interactionsAuthority } from './authority';
import { ChatClient } from './client';
import { FixtureChatAdapter } from './fixture-adapter';
import { ChatStore, type AppActivity } from './store';

type Chat = Readonly<{ store: ChatStore; fixture: FixtureChatAdapter }>;
const chats = new WeakMap<OnboardingStore, Chat>();

/** React Native's own foreground state; on the rendered web harness, the page's visibility. */
const appActivity: AppActivity = Object.freeze({
  current: () => AppState.currentState ?? null,
  subscribe: (listener: (state: string) => void) => {
    const subscription = AppState.addEventListener('change', listener);
    return () => subscription?.remove();
  },
});

/** The guarded development composition: C2's chat transport is the in-process fixture, as P05's is. */
export function chatFor(owner: OnboardingStore): Chat {
  let chat = chats.get(owner);
  if (!chat) {
    const interactions = interactionsFor(owner);
    const fixture = new FixtureChatAdapter(owner.profiles, interactions.adapter);
    const store = new ChatStore({ profiles: owner.profiles, client: new ChatClient(fixture), activity: appActivity,
      authority: interactionsAuthority(interactions.adapter) });
    chat = Object.freeze({ store, fixture });
    chats.set(owner, chat);
  }
  return chat;
}
export function useChat() {
  const { store: owner } = useOnboarding();
  const { store, fixture } = chatFor(owner);
  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
  return { store, fixture, state };
}
export function useChatFixture() {
  const { store: owner } = useOnboarding();
  const { fixture } = chatFor(owner);
  // The fixture's labeled controls show its current settings.
  useSyncExternalStore(fixture.subscribe, () => `${fixture.scenario}:${fixture.delivery}:${fixture.providerField}:${fixture.outage}:${fixture.delayedCount}`);
  return fixture;
}
