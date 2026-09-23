import { Redirect } from 'expo-router';
import { useOnboarding } from '../onboarding/context';

export default function EntryScreen() {
  const { state, store } = useOnboarding();
  // Onboarding republishes every profile change after deriving its current stage.
  // A second profile subscription can notify while onboarding is synchronizing,
  // before the matching stage is published, and queue an obsolete redirect.
  const profileState = store.profiles.getSnapshot();
  const routes = { account: '/account', verification: '/verify', eligibility: '/eligibility', birth: '/birth', remaining: '/remaining', restricted: '/restricted', eligible: '/recommended' } as const;
  const destination = (state.stage === 'remaining' || state.stage === 'birth') && profileState.profile ? '/profile' : routes[state.stage];
  return <Redirect href={destination} />;
}
