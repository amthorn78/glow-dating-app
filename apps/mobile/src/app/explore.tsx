import { router } from 'expo-router';
import { ActivityIndicator, Text, View } from 'react-native';
import { Button, Page, PreviewNotice, ProfileCard, colors, styles } from '../components/ui';
import { useRecommendations } from '../hooks/use-recommendations';

export default function ExploreScreen() {
  const { state, reload } = useRecommendations();
  return <Page>
    <Button label="Back to recommended" secondary onPress={() => router.replace('/')} />
    <PreviewNotice />
    <View style={styles.group}><Text style={styles.eyebrow}>EXPLORE MORE</Text>
      <Text style={styles.title} accessibilityRole="header">More room to discover.</Text>
      <Text style={styles.body}>The broader discovery layout, using the same fictional people. Filters, eligibility, and real discovery are not connected.</Text></View>
    {state.status === 'loading' && <ActivityIndicator color={colors.accent} accessibilityLabel="Loading fictional profiles" />}
    {state.status === 'error' && <View style={styles.group}><Text style={styles.body}>The development preview could not load.</Text><Button label="Try again" onPress={reload} /></View>}
    {state.status === 'ready' && state.items.length === 0 && <Text style={styles.body}>No profiles in this preview.</Text>}
    {state.status === 'ready' && state.items.map((profile) => <ProfileCard key={profile.profile_id} profile={profile} />)}
  </Page>;
}
