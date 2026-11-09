import { useSyncExternalStore } from 'react';
import { useOnboarding } from '../onboarding/context';
import type { OnboardingStore } from '../onboarding/store';
import { NotificationClient } from './client';
import { FixtureNotificationAdapter } from './fixture-adapter';
import { FIXTURE_INSTALLATION_ID, syntheticTokenSource } from './fixture-device';
import { FixturePermissionSeam } from './permission';
import { NotificationStore } from './store';

type Notifications = Readonly<{ store: NotificationStore; adapter: FixtureNotificationAdapter; permission: FixturePermissionSeam }>;
const compositions = new WeakMap<OnboardingStore, Notifications>();

/**
 * The guarded development composition (P06.3, D7): F12's transport is the in-process fixture, the
 * permission seam is the fixture whose answer a labelled control sets, and the token is synthetic.
 * It is made when the notification settings screen is first shown; nothing here asks for a
 * permission or registers anything by itself.
 */
export function notificationsFor(owner: OnboardingStore): Notifications {
  let composition = compositions.get(owner);
  if (!composition) {
    const adapter = new FixtureNotificationAdapter();
    const permission = new FixturePermissionSeam();
    const store = new NotificationStore({ owner, client: new NotificationClient(adapter), permission, tokens: syntheticTokenSource(),
      sessions: adapter, installation: FIXTURE_INSTALLATION_ID });
    composition = Object.freeze({ store, adapter, permission });
    compositions.set(owner, composition);
  }
  return composition;
}
export function useNotifications() {
  const { store: owner } = useOnboarding();
  const { store } = notificationsFor(owner);
  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
  return { store, state };
}
export function useNotificationFixture() {
  const { store: owner } = useOnboarding();
  const { adapter, permission } = notificationsFor(owner);
  // The labelled controls show the fixture's current settings.
  useSyncExternalStore(permission.subscribe, () => `${permission.setting}:${permission.requests}`);
  useSyncExternalStore(adapter.subscribe, () => adapter.scenario);
  return { adapter, permission };
}
