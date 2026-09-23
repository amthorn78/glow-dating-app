import { router } from 'expo-router';
import { ActivityIndicator, Text, View } from 'react-native';
import { Button, Page, PreviewNotice, ProfileCard, ScreenTitle, colors, styles } from '../components/ui';
import { useRecommendations } from '../hooks/use-recommendations';
import { useOnboarding } from '../onboarding/context';

export default function ExploreScreen() {
  const { store } = useOnboarding();
  const { state, reload } = useRecommendations();
  return <Page testID="screen-explore">
    <Button label="Back to recommended" secondary onPress={() => router.replace('/recommended')} />
    <PreviewNotice />
    <View style={styles.group}><Text style={styles.eyebrow}>EXPLORE MORE</Text>
      <ScreenTitle>More room to discover.</ScreenTitle>
      <Text style={styles.body}>The broader discovery layout, using the same fictional people. Real discovery and filters are not connected. Access here uses a separate eligible development scenario.</Text></View>
    {state.status === 'loading' && <ActivityIndicator color={colors.accent} accessibilityLabel="Loading fictional profiles" />}
    {state.status === 'error' && <View style={styles.group}><Text style={styles.body}>The development preview could not load.</Text><Button label="Try again" onPress={reload} /></View>}
    {state.status === 'ready' && state.items.length === 0 && <Text style={styles.body}>No profiles in this preview.</Text>}
    {state.status === 'ready' && state.items.map((profile) => <ProfileCard key={profile.profile_id} profile={profile} />)}
    <Button label="Log out" testID="logout" secondary onPress={() => { store.logout(); router.replace('/'); }} />
    <Button label="Development scenarios" testID="development-link" secondary onPress={() => router.push('/development')} />
  </Page>;
}
