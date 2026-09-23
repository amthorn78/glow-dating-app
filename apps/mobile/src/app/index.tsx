import { useState } from 'react';
import { router } from 'expo-router';
import { ActivityIndicator, Text, View } from 'react-native';
import { Button, Page, PreviewNotice, ProfileCard, colors, styles } from '../components/ui';
import { useRecommendations } from '../hooks/use-recommendations';

export default function RecommendedScreen() {
  const { state, reload } = useRecommendations();
  const [index, setIndex] = useState(0);
  const profile = state.status === 'ready' ? state.items[index % Math.max(state.items.length, 1)] : undefined;
  return <Page>
    <View style={styles.headerRow}><Text style={styles.brand}>glow</Text><Text style={styles.tag}>A LITTLE MORE CONNECTION</Text></View>
    <PreviewNotice />
    <View style={styles.group}>
      <Text style={styles.eyebrow}>RECOMMENDED FIRST</Text>
      <Text style={styles.title} accessibilityRole="header">Make room for{ '\n' }something real.</Text>
      <Text style={styles.body}>A preview of how people will appear. This order is synthetic and has no compatibility meaning.</Text>
    </View>
    {state.status === 'loading' && <View style={styles.status} accessibilityRole="progressbar" accessibilityLabel="Loading fictional profiles"><ActivityIndicator color={colors.accent} /><Text style={styles.body}>Loading preview…</Text></View>}
    {state.status === 'error' && <View style={styles.status} accessibilityLiveRegion="polite">
      <Text style={styles.subtitle}>The preview could not load.</Text>
      <Text style={styles.body}>Check the development API and configuration, then try again. We have not substituted another data source.</Text>
      <Button label="Try again" onPress={reload} />
    </View>}
    {state.status === 'ready' && state.items.length === 0 && <View style={styles.status} accessibilityLiveRegion="polite">
      <Text style={styles.subtitle}>No profiles in this preview.</Text><Text style={styles.body}>The development response is empty.</Text><Button label="Refresh preview" onPress={reload} />
    </View>}
    {profile && <>
      <ProfileCard profile={profile} />
      <View style={styles.group}>
        <Button label="Next fictional profile" hint="Changes only this preview. Does not send a pass or a like." onPress={() => setIndex((value) => value + 1)} />
        <Text style={styles.small}>Preview navigation only. Likes and passes are not connected.</Text>
      </View>
    </>}
    {state.status === 'ready' && <Text style={styles.small}>Source: {state.source === 'api' ? 'development API fixtures' : 'bundled fixtures'}. Nothing here is a mutual match.</Text>}
    <View style={styles.group}><Button label="Explore more" secondary onPress={() => router.push('/explore')} hint="Open the broader discovery layout preview." />
      <Text style={styles.small}>Messaging becomes available only after a mutual match in the future implemented flow.</Text></View>
  </Page>;
}
