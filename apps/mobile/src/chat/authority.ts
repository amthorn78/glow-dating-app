import type { FixtureInteractionAdapter } from '../interactions/fixture-adapter.ts';
import type { ChatAuthority } from './store.ts';

/** The chat store's view of Glow's match projections in the development composition. */
export function interactionsAuthority(adapter: FixtureInteractionAdapter): ChatAuthority {
  return Object.freeze({
    subscribe: (listener: () => void) => adapter.subscribe(listener),
    // Glow's current match projection: its version is the one a send is authorized at.
    contactVersion: (matchId: string) => adapter.matches().find(match => match.match_id === matchId && match.state === 'active')?.version ?? null,
  });
}
