import { useEffect, useState } from 'react';
import { getDevelopmentConfig } from '../config/development';
import { parseDevelopmentRecommendations, type DevelopmentProfile } from '../contracts/recommendations';
import { developmentRecommendations } from '../data/fixtures';
import { fetchDevelopmentRecommendations } from '../data/recommendations';
import { useOnboarding, useProfiles } from '../onboarding/context';

type State =
  | { status: 'blocked' }
  | { status: 'loading' }
  | { status: 'error' }
  | { status: 'ready'; items: readonly DevelopmentProfile[]; source: 'bundled' | 'api' };

export function useRecommendations() {
  const { store, state: onboarding } = useOnboarding();
  const { profiles, state: profileState } = useProfiles();
  const [attempt, setAttempt] = useState(0);
  const pairContext = profiles.candidateContext();
  const pairAllowed = profiles.candidatePreview(pairContext) !== null;
  const allowed = onboarding.stage === 'eligible' && profileState.canDiscover && pairAllowed;
  const accessKey = `${onboarding.generation}:${onboarding.account?.account_id ?? ''}:${profileState.discoveryRevision}:${JSON.stringify(pairContext?.version ?? null)}`;
  const [loaded, setLoaded] = useState<{ key: string; state: State }>({ key: '', state: { status: 'loading' } });
  useEffect(() => {
    if (!allowed) return;
    const capturedPair = profiles.candidateContext();
    const controller = new AbortController();
    let mounted = true;
    setLoaded({ key: accessKey, state: { status: 'loading' } });
    function current() {
      const owner = store.getSnapshot();
      const profile = profiles.getSnapshot();
      const currentPair = profiles.candidateContext();
      return mounted && owner.stage === 'eligible' && profile.canDiscover && profiles.candidatePreview(capturedPair) !== null &&
        `${owner.generation}:${owner.account?.account_id ?? ''}:${profile.discoveryRevision}:${JSON.stringify(currentPair?.version ?? null)}` === accessKey;
    }
    async function load() {
      try {
        const config = getDevelopmentConfig({
          isDevelopment: __DEV__, mode: process.env.EXPO_PUBLIC_GLOW_MODE,
          apiOrigin: process.env.EXPO_PUBLIC_GLOW_API_BASE_URL,
        });
        const response = config.apiOrigin
          ? await fetchDevelopmentRecommendations(config, fetch, { signal: controller.signal })
          : parseDevelopmentRecommendations(developmentRecommendations);
        if (current()) setLoaded({ key: accessKey, state: { status: 'ready', items: response.items, source: config.apiOrigin ? 'api' : 'bundled' } });
      } catch {
        // Never leak response bodies, configured URLs or personal information into UI/logs.
        if (current()) setLoaded({ key: accessKey, state: { status: 'error' } });
      }
    }
    void load();
    return () => { mounted = false; controller.abort(); };
  }, [attempt, allowed, accessKey, profiles, store]);
  // Mask retained results synchronously. Waiting for effect cleanup leaves one
  // render where the old owner or revoked permission could disclose a card.
  const state: State = !allowed ? { status: 'blocked' } : loaded.key === accessKey ? loaded.state : { status: 'loading' };
  return { state, reload: () => setAttempt((value) => value + 1) };
}
