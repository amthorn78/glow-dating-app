import type { BirthInput } from '../contracts/generated/gapp-api-v1.ts';
import { validateBirthInput } from '../contracts/generated/validators.js';

export type PredicateOutcome = 'pass' | 'fail' | 'unknown';
export type FixtureClock = () => Date;
export type AdultPolicy = Readonly<{ version: string; minimumAge: number; leapBirthday: 'march_1' }>;

/** Synthetic demonstration policy, not approved terms or a launch-jurisdiction decision. */
export const FIXTURE_POLICY: AdultPolicy = Object.freeze({
  version: 'development-consent-1', minimumAge: 18, leapBirthday: 'march_1',
});
export const FIXTURE_CLOCK: FixtureClock = () => new Date('2026-09-23T12:00:00Z');

export function validCivilDate(value: string): boolean {
  if (value.length !== 10 || !/^(?!0000)\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const [year, month, day] = value.split('-').map(Number);
  if (!year || !month || !day || month > 12) return false;
  const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  return day <= [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]!;
}

/** UTC is the explicit fixture evaluation clock, never a historical birth timezone. */
export function adultOutcome(date: string | null, policy: AdultPolicy | null, clock: FixtureClock): PredicateOutcome {
  if (!date || !validCivilDate(date) || !policy || !Number.isInteger(policy.minimumAge) || policy.minimumAge < 1 ||
      policy.leapBirthday !== 'march_1') return 'unknown';
  const now = clock();
  if (!Number.isFinite(now.getTime())) return 'unknown';
  const today = now.toISOString().slice(0, 10);
  if (date > today) return 'unknown';
  const yearDifference = Number(today.slice(0, 4)) - Number(date.slice(0, 4));
  const birthdayPassed = today.slice(5) >= date.slice(5);
  return yearDifference - (birthdayPassed ? 0 : 1) >= policy.minimumAge ? 'pass' : 'fail';
}

export function birthInputValid(value: unknown, clock: FixtureClock): value is BirthInput {
  if (!validateBirthInput(value)) return false;
  const now = clock();
  if (!Number.isFinite(now.getTime())) return false;
  const input = value as BirthInput;
  return validCivilDate(input.birth_date) && input.birth_date <= now.toISOString().slice(0, 10);
}
