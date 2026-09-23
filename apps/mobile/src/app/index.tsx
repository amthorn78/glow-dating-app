import { Redirect } from 'expo-router';
import { useOnboarding, useProfiles } from '../onboarding/context';

export default function EntryScreen() {
  const { state } = useOnboarding();
  const { state: profileState } = useProfiles();
  const routes = { account: '/account', verification: '/verify', eligibility: '/eligibility', birth: '/birth', remaining: '/remaining', restricted: '/restricted', eligible: '/recommended' } as const;
  const destination = (state.stage === 'remaining' || state.stage === 'birth') && profileState.profile ? '/profile' : routes[state.stage];
  return <Redirect href={destination} />;
}
