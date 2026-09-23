/** Development-only wire schema; generated validation is not API authorization. */
import { validateDevelopmentRecommendations } from './generated/validators.js';
import { assertUniqueKeys } from './validation.ts';
import type { DevelopmentRecommendations } from './generated/gapp-dev-v1.ts';
export type { DevelopmentProfile, DevelopmentRecommendations } from './generated/gapp-dev-v1.ts';

export class ContractError extends Error {
  constructor() {
    super('The development response does not match the supported public contract.');
    this.name = 'ContractError';
  }
}

export function parseDevelopmentRecommendations(value: unknown): DevelopmentRecommendations {
  if (!validateDevelopmentRecommendations(value) || !assertUniqueKeys(value)) throw new ContractError();
  return value as DevelopmentRecommendations;
}
