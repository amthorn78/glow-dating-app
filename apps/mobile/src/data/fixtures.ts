import type { DevelopmentRecommendations } from '../contracts/recommendations';

/** Entirely fictional records. Their order has no compatibility or eligibility meaning. */
export const developmentRecommendations: DevelopmentRecommendations = {
  mode: 'fixture',
  contract_version: 'gapp-dev-v1',
  items: [
    {
      profile_id: 'fixture-alex', display_name: 'Alex', age: 32,
      summary: 'A long walk, a new recipe, and a conversation that goes somewhere unexpected.',
      compatibility: { status: 'pending', source: 'fixture' },
    },
    {
      profile_id: 'fixture-jordan', display_name: 'Jordan', age: 35,
      summary: 'Curious about people. Usually carrying a book and making time for the outdoors.',
      compatibility: { status: 'pending', source: 'fixture' },
    },
    {
      profile_id: 'fixture-riley', display_name: 'Riley', age: 29,
      summary: 'Live music, quiet mornings, and finding the small things worth paying attention to.',
      compatibility: { status: 'pending', source: 'fixture' },
    },
  ],
};
