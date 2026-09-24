import type { OnboardingSnapshot } from './store.ts';
import { FIXTURE_POLICY } from './policy.ts';

export const SAFE_ROUTES = ['/account', '/verify', '/eligibility', '/birth', '/remaining', '/restricted',
  '/recommended', '/explore', '/recovery', '/reset-password', '/development',
  '/profile', '/profile-edit', '/preferences', '/profile-preview', '/media', '/matches', '/match'] as const;
export type SafeRoute = typeof SAFE_ROUTES[number];

/** Only fixed public screen identifiers enter routing. Never propagate query parameters or private values. */
export function sanitizeDestination(value: unknown): SafeRoute | '/' {
  if (typeof value !== 'string' || /[?#%\\\s]/.test(value)) return '/';
  const prefix = 'glow-development://';
  const path = value.startsWith(prefix) ? `/${value.slice(prefix.length).replace(/^\//, '')}` : value;
  return (SAFE_ROUTES as readonly string[]).includes(path) ? path as SafeRoute : '/';
}

export function canAccessRoute(route: SafeRoute, state: OnboardingSnapshot): boolean {
  if (route === '/development') return true; // The enclosing runtime guard is mandatory.
  if (route === '/account' || route === '/recovery') return state.stage === 'account';
  if (route === '/reset-password') return state.stage === 'account' && state.recoveryReady;
  if (route === '/restricted') return state.stage === 'restricted';
  if (route === '/verify') return state.stage === 'verification';
  if (route === '/recommended' || route === '/explore') return state.stage === 'eligible';
  const active = state.account?.state === 'active' && state.account.session_state === 'valid';
  // Revocation remains reachable when discovery eligibility is lost. The
  // interaction service independently authorizes every participant projection.
  if (route === '/matches' || route === '/match') return active;
  if (route === '/eligibility' || ['/profile', '/profile-edit', '/preferences', '/profile-preview', '/media'].includes(route)) return active;
  const eligibleForBirth = active && state.adult === 'pass' && state.consent.state === 'accepted' && state.consent.policy_version === FIXTURE_POLICY.version;
  if (route === '/birth') return eligibleForBirth;
  return route === '/remaining' && eligibleForBirth && state.birth !== null;
}
