import { Redirect } from 'expo-router';
import { useOnboarding } from '../onboarding/context';

export default function EntryScreen() {
  const { state } = useOnboarding();
  const routes = { account: '/account', verification: '/verify', eligibility: '/eligibility', birth: '/birth', remaining: '/remaining', restricted: '/restricted', eligible: '/recommended' } as const;
  return <Redirect href={routes[state.stage]} />;
}
