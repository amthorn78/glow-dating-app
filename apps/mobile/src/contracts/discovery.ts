/** Closed development-only page shape. Current authorization belongs to the fixture adapter. */
import { validateDevelopmentDiscoveryPage } from './generated/validators.js';
import { ContractError } from './recommendations.ts';
import { assertUniqueKeys } from './validation.ts';
import type { DevelopmentDiscoveryPage } from './generated/gapp-dev-v1.ts';

export type { DevelopmentDiscoveryPage, DevelopmentDiscoveryProfile } from './generated/gapp-dev-v1.ts';

export function parseDevelopmentDiscoveryPage(value: unknown): DevelopmentDiscoveryPage {
  if (!validateDevelopmentDiscoveryPage(value) || !assertUniqueKeys(value)) throw new ContractError();
  return value as DevelopmentDiscoveryPage;
}
