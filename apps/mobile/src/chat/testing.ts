/** Test composition for the chat fixture: fixture time and app state. Imported by tests only. */
import { createFixtureOnboardingStore } from '../onboarding/store.ts';
import { FixtureDiscoveryAdapter } from '../discovery/fixture-adapter.ts';
import { DiscoveryStore } from '../discovery/store.ts';
import { FixtureInteractionAdapter } from '../interactions/fixture-adapter.ts';
import { InteractionStore } from '../interactions/store.ts';
import { interactionsAuthority } from './authority.ts';
import { ChatClient } from './client.ts';
import { FixtureChatAdapter } from './fixture-adapter.ts';
import { ChatStore, type AppActivity, type ChatTimers } from './store.ts';
import type { ChatTransport } from './transport.ts';

/** Fixture time: intervals run only when a test advances the clock. */
export class FixtureTimers implements ChatTimers {
  now = 0;
  private serial = 0;
  private readonly entries = new Map<number, { at: number; every: number; callback: () => void }>();
  readonly setInterval = (callback: () => void, milliseconds: number) => {
    const id = ++this.serial; this.entries.set(id, { at: this.now + milliseconds, every: milliseconds, callback }); return id;
  };
  readonly clearInterval = (handle: unknown) => { this.entries.delete(handle as number); };
  get active() { return this.entries.size; }
  intervals() { return [...this.entries.values()].map(entry => entry.every).sort((a, b) => a - b); }
  async advance(milliseconds: number) {
    const end = this.now + milliseconds;
    for (;;) {
      const due = [...this.entries.entries()].filter(([, entry]) => entry.at <= end).sort(([, a], [, b]) => a.at - b.at)[0];
      if (!due) break;
      const [, entry] = due;
      this.now = entry.at; entry.at += entry.every;
      entry.callback(); await settle();
    }
    this.now = end; await settle();
  }
}
/** The app's foreground state, set by the test. */
export class FixtureActivity implements AppActivity {
  state = 'active';
  private readonly listeners = new Set<(state: string) => void>();
  readonly current = () => this.state;
  readonly subscribe = (listener: (state: string) => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  set(state: string) { this.state = state; this.listeners.forEach(listener => listener(state)); }
}
/** Lets every pending promise chain of an in-process request finish. */
export const settle = async () => { for (let index = 0; index < 3; index++) await new Promise(resolve => setImmediate(resolve)); };
const options = { isDevelopment: true, mode: 'fixture' };

/** An eligible fictional member with a mutual match with fictional Jules, and a chat store on fixture time. */
export async function chatSetup(wrap: (transport: ChatTransport) => ChatTransport = transport => transport) {
  const owner = createFixtureOnboardingStore(options); owner.scenario('eligible');
  const discovery = new DiscoveryStore(owner.profiles, new FixtureDiscoveryAdapter(owner.profiles, options));
  const adapter = new FixtureInteractionAdapter(owner.profiles, discovery.adapter);
  const interactions = new InteractionStore(owner.profiles, discovery, adapter);
  discovery.enter('recommended'); await settle();
  interactions.developmentReciprocal('profile-jules');
  await interactions.submit('recommended', 'profile-jules', 'like');
  const matchId = adapter.matches().find(match => match.state === 'active')!.match_id;
  const fixture = new FixtureChatAdapter(owner.profiles, adapter);
  const timers = new FixtureTimers(), activity = new FixtureActivity();
  const client = new ChatClient(wrap(fixture));
  const store = new ChatStore({ profiles: owner.profiles, client, activity, timers, authority: interactionsAuthority(adapter) });
  const jules = fixture.developmentMember('profile-jules');
  const viewer = owner.profiles.captureInteractionOwner()!.ownerId;
  return { owner, discovery, adapter, interactions, fixture, timers, activity, client, store, matchId, jules, viewer };
}
/** A second mutual match, with fictional Iris, for tests that need two conversations. */
export async function secondMatch(fixture: Awaited<ReturnType<typeof chatSetup>>) {
  fixture.adapter.reciprocal('profile-iris', 'second:reciprocal');
  const page = await fixture.discovery.adapter.request('recommended', 'second-match', null, true);
  const prepared = fixture.adapter.prepare(page, 'profile-iris', 'like', 'second:like');
  fixture.adapter.execute(prepared.session, prepared.intent);
  return fixture.adapter.matches().find(match => match.state === 'active' && match.match_id !== fixture.matchId)!.match_id;
}
