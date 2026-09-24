import { useCallback } from 'react';
import { router, useFocusEffect } from 'expo-router';
import { ActivityIndicator, Text, View } from 'react-native';
import { Button, Page, PreviewNotice, ProfileCard, ScreenTitle, colors, styles } from '../components/ui';
import { useOnboarding } from '../onboarding/context';
import { NextPageButton } from './next-page-button';
import { useDiscovery } from './context';
import type { DiscoveryMode } from './fixture-adapter';
import { useInteractions } from '../interactions/context';
import { CandidateActions, InteractionFeedback } from '../interactions/controls';

export function DiscoveryScreen({ mode }: { mode: DiscoveryMode }) {
  const { store } = useOnboarding();
  const { state, discovery } = useDiscovery(mode);
  const { store: interactions, state: interactionState } = useInteractions();
  useFocusEffect(useCallback(() => () => interactions.cancelPending(), [interactions]));
  const recommended = mode === 'recommended';
  const loading = state.status === 'loading' || state.status === 'idle';
  const submitting = interactionState.status === 'pending';
  const hasPage = state.status === 'ready' || state.status === 'partial';
  return <Page testID={recommended ? 'screen-recommended' : 'screen-explore'}>
    {recommended ? <View style={styles.headerRow}><Text style={styles.brand}>glow</Text><Text style={styles.tag}>A LITTLE MORE CONNECTION</Text></View>
      : <Button label="Back to recommended" secondary onPress={() => router.replace('/recommended')} />}
    <PreviewNotice />
    <View style={styles.group}><Text style={styles.eyebrow}>{recommended ? 'RECOMMENDED FIRST' : 'EXPLORE MORE'}</Text>
      <ScreenTitle>{recommended ? 'Make room for something real.' : 'More room to discover.'}</ScreenTitle>
      <Text style={styles.body}>{recommended ? 'A finite selection of fictional people. This order is synthetic and has no compatibility meaning.'
        : 'The same eligible fictional people, in a different order. Each view keeps its place when you switch.'}</Text>
    </View>
    <View testID="discovery-status" accessibilityLiveRegion="polite" style={styles.group}>
      {loading && <><ActivityIndicator color={colors.accent} accessibilityLabel="Loading fictional profiles" /><Text style={styles.body}>Loading preview…</Text></>}
      {state.status === 'reload_required' && <><Text style={styles.subtitle}>This preview has changed.</Text><Text style={styles.body}>Refresh to see the current selection.</Text></>}
      {state.status === 'error' && <><Text style={styles.subtitle}>The preview could not load.</Text><Text style={styles.body}>The preview is offline or unavailable. Try refreshing when you are ready.</Text></>}
      {state.status === 'empty' && <><Text style={styles.subtitle}>No people in this preview.</Text><Text style={styles.body}>You can refresh to check the selection again.</Text></>}
      {state.status === 'partial' && <Text style={styles.body}>Some compatibility results are pending or unavailable. You can still browse these eligible fictional profiles.</Text>}
      {hasPage && <Text style={styles.small}>Page {state.pageNumber}. {state.complete ? 'You have reached the end of this preview.' : 'More fictional people follow.'}</Text>}
      {state.status === 'exhausted' && <Text style={styles.body}>You have reached the end of this preview.</Text>}
    </View>
    <InteractionFeedback />
    <View testID="discovery-cards" style={styles.group}>
      {hasPage && state.page?.items.map(profile => <View key={profile.profile_id} testID={`discovery-card-${profile.profile_id}`}>
        <ProfileCard profile={profile} />
        <CandidateActions mode={mode} profileId={profile.profile_id} name={profile.display_name} />
      </View>)}
    </View>
    <View style={styles.group}>
      <NextPageButton disabled={loading || submitting || !state.page?.next_cursor} onPress={() => void discovery.next()} />
      <Button label="Refresh preview" testID="discovery-refresh" secondary disabled={loading || submitting} onPress={() => void discovery.refresh()}
        hint="Start a new selection in this view." />
      <Text style={styles.small}>Browsing does not record likes or passes. Use the labeled actions to commit your choice. Saved choices stay consumed in both views, including after refresh.</Text>
      <Text style={styles.small}>Source: in-memory fixtures. No live Human Design result or messaging.</Text>
    </View>
    {recommended && <Button label="Explore more" secondary onPress={() => router.push('/explore')} hint="Browse the same eligible fictional people in a different order." />}
    <Button label="Your matches" testID="open-matches" secondary onPress={() => router.push('/matches')} />
    <Button label="Your profile and preferences" testID="open-profile" secondary onPress={() => router.push('/profile')} />
    <Button label="Log out" testID="logout" secondary onPress={() => { store.logout(); router.replace('/'); }} />
    <Button label="Development scenarios" testID="development-link" secondary onPress={() => router.push('/development')} />
  </Page>;
}
