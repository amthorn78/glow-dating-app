import { parseDevelopmentRecommendations, type DevelopmentRecommendations } from '../contracts/recommendations.ts';
import type { DevelopmentConfig } from '../config/development.ts';

export const DEVELOPMENT_RECOMMENDATIONS_PATH = '/api/v1/development/recommendations';
export type FetchLike = (input: string, init: RequestInit) => Promise<Response>;

/** No credentials, birth inputs, device identifiers or write operations cross this boundary. */
export async function fetchDevelopmentRecommendations(
  config: DevelopmentConfig,
  fetcher: FetchLike = fetch,
  options: { signal?: AbortSignal; timeoutMs?: number } = {},
): Promise<DevelopmentRecommendations> {
  if (config.mode !== 'fixture' || !config.apiOrigin) throw new Error('The development API is not configured.');
  const controller = new AbortController();
  const abort = () => controller.abort();
  if (options.signal?.aborted) controller.abort();
  options.signal?.addEventListener('abort', abort, { once: true });
  const timeout = setTimeout(abort, options.timeoutMs ?? 5000);
  let responseAccepted = false;
  try {
    const response = await fetcher(`${config.apiOrigin}${DEVELOPMENT_RECOMMENDATIONS_PATH}`, {
      method: 'GET', headers: { Accept: 'application/json' }, credentials: 'omit', signal: controller.signal,
    });
    if (!response.ok) throw new Error('The development API is unavailable.');
    responseAccepted = true;
    if (!response.headers.get('content-type')?.toLowerCase().startsWith('application/json')) {
      throw new Error('The development API returned an unsupported response.');
    }
    const result = parseDevelopmentRecommendations(await response.json());
    if (controller.signal.aborted) throw new Error('cancelled');
    return result;
  } catch {
    // JSON parsing and transport errors may contain response text or configured URLs.
    // Return only newly created public errors, without retaining the unsafe cause.
    if (controller.signal.aborted) {
      const error = new Error('The development request was cancelled.');
      error.name = 'AbortError';
      throw error;
    }
    throw new Error(responseAccepted
      ? 'The development API returned an unsupported response.'
      : 'The development API is unavailable.');
  } finally {
    clearTimeout(timeout);
    options.signal?.removeEventListener('abort', abort);
  }
}
