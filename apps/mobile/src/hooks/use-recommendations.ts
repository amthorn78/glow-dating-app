import { useEffect, useState } from 'react';
import { getDevelopmentConfig } from '../config/development';
import { parseDevelopmentRecommendations, type DevelopmentProfile } from '../contracts/recommendations';
import { developmentRecommendations } from '../data/fixtures';
import { fetchDevelopmentRecommendations } from '../data/recommendations';

type State =
  | { status: 'loading' }
  | { status: 'error' }
  | { status: 'ready'; items: readonly DevelopmentProfile[]; source: 'bundled' | 'api' };

export function useRecommendations() {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<State>({ status: 'loading' });
  useEffect(() => {
    const controller = new AbortController();
    let mounted = true;
    setState({ status: 'loading' });
    async function load() {
      try {
        const config = getDevelopmentConfig({
          isDevelopment: __DEV__, mode: process.env.EXPO_PUBLIC_GLOW_MODE,
          apiOrigin: process.env.EXPO_PUBLIC_GLOW_API_BASE_URL,
        });
        const response = config.apiOrigin
          ? await fetchDevelopmentRecommendations(config, fetch, { signal: controller.signal })
          : parseDevelopmentRecommendations(developmentRecommendations);
        if (mounted) setState({ status: 'ready', items: response.items, source: config.apiOrigin ? 'api' : 'bundled' });
      } catch {
        // Never leak response bodies, configured URLs or personal information into UI/logs.
        if (mounted) setState({ status: 'error' });
      }
    }
    void load();
    return () => { mounted = false; controller.abort(); };
  }, [attempt]);
  return { state, reload: () => setAttempt((value) => value + 1) };
}
