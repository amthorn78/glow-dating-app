/** P02 logical contracts only; no production URL/client or authorization is activated. */
import { validateAppIntent, validateAppResponse, validateError } from './generated/validators.js';
import type { AppIntent, AppResponse, Error as ApiError } from './generated/gapp-api-v1.ts';
import { assertUniqueKeys } from './validation.ts';

export class ProductionContractError extends Error {
  constructor() {
    super('The response does not match the supported application contract.');
    this.name = 'ProductionContractError';
  }
}

export function parseAppResponse(value: unknown): AppResponse {
  if (!validateAppResponse(value) || !assertUniqueKeys(value)) throw new ProductionContractError();
  return value as AppResponse;
}
export function parseAppIntent(value: unknown): AppIntent {
  if (!validateAppIntent(value) || !assertUniqueKeys(value)) throw new ProductionContractError();
  return value as AppIntent;
}
export function parseApiError(value: unknown): ApiError {
  if (!validateError(value)) throw new ProductionContractError();
  return value as ApiError;
}
