import { sanitizeDestination } from '../onboarding/routes';

/** Native ingress accepts fixed screen destinations only. Account state is checked by the layout. */
export function redirectSystemPath({ path }: { path: string; initial: boolean }): string {
  return sanitizeDestination(path);
}
