import { useCallback } from 'react';
import { router, useFocusEffect } from 'expo-router';
import { Text, View } from 'react-native';
import { Button, Page, PreviewNotice, ProfileCard, ScreenTitle, styles } from '../components/ui';
import { useOnboarding } from '../onboarding/context';
import { canAccessRoute } from '../onboarding/routes';
import { useInteractions } from './context';
import { ActionButton } from './action-button';
import { InteractionFeedback } from './controls';

function MatchNavigation() {
  const { state, store } = useOnboarding();
  return <View style={styles.group}>
    {canAccessRoute('/recommended', state) && <Button label="Back to recommended" secondary onPress={() => router.replace('/recommended')} />}
    {canAccessRoute('/profile', state) && <Button label="Your profile and preferences" testID="open-profile" secondary onPress={() => router.push('/profile')} />}
    {canAccessRoute('/restricted', state) && <Button label="Back to account status" testID="matches-restricted" secondary onPress={() => router.replace('/restricted')} />}
    <Button label="Development scenarios" testID="development-link" secondary onPress={() => router.push('/development')} />
    <Button label="Log out" testID="logout" secondary onPress={() => { store.logout(); router.replace('/'); }} />
  </View>;
}

export function MatchesScreen() {
  const { store, state } = useInteractions();
  const { state: owner } = useOnboarding();
  const restricted = owner.account?.state !== 'active';
  // Cleanup references survive lost counterpart disclosure. Only a separately
  // authorized current view may add a profile or active-match wording.
  const matches = state.cleanupMatches.map(reference => {
    const view = restricted ? undefined : state.matches.find(item => item.match_id === reference.match_id);
    return { ...reference, profile: view?.profile ?? null, active: view?.state === 'active' && view.profile !== null };
  });
  useFocusEffect(useCallback(() => { store.refresh(); }, [store]));
  return <Page testID="screen-matches">
    <PreviewNotice />
    <ScreenTitle>Your matches</ScreenTitle>
    <Text style={styles.body}>{restricted ? 'Your account is restricted. You can end existing connections. Profile details, discovery and messaging remain unavailable.'
      : 'A mutual match appears only after both fictional people have committed a like. A match does not enable messaging in this preview.'}</Text>
    <InteractionFeedback />
    <View style={styles.group} testID="match-list">
      {matches.length === 0 && <Text style={styles.body} testID="matches-empty">{restricted ? 'No connections are available to end.' : 'No mutual matches yet. A like on its own is private and is not a match.'}</Text>}
      {matches.map(match => <View key={match.match_id} style={styles.notice} testID={`match-row-${match.match_id}`}>
        <Text style={styles.subtitle} accessibilityRole="header">{match.active && match.profile ? match.profile.display_name : 'Connection unavailable'}</Text>
        <Text style={styles.body}>{match.active ? 'Mutual match' : match.state === 'unmatched' ? 'Unmatched. New contact is unavailable.' : 'New contact is unavailable.'}</Text>
        <Button label={match.active && match.profile ? `View match with ${match.profile.display_name}` : 'View connection status'}
          testID={`match-open-${match.match_id}`} secondary onPress={() => { store.selectMatch(match.match_id); router.push('/match'); }} />
      </View>)}
    </View>
    <Button label="Refresh matches" testID="matches-refresh" secondary disabled={state.status === 'pending'} onPress={() => store.refresh()} />
    <MatchNavigation />
  </Page>;
}

export function MatchScreen() {
  const { store, state } = useInteractions();
  const { state: owner } = useOnboarding();
  const restricted = owner.account?.state !== 'active';
  useFocusEffect(useCallback(() => { store.refresh(); return () => store.cancelPending(); }, [store]));
  const match = state.cleanupMatches.find(item => item.match_id === state.selectedMatchId);
  const view = restricted ? undefined : state.matches.find(item => item.match_id === state.selectedMatchId);
  const active = view?.state === 'active' && view.profile !== null;
  return <Page testID="screen-match">
    <PreviewNotice />
    <ScreenTitle>{active ? 'A mutual connection.' : 'Connection status'}</ScreenTitle>
    <InteractionFeedback />
    <View style={styles.group} testID="match-detail">
      {!match && <Text style={styles.body}>This connection is unavailable. Return to your matches to check current access.</Text>}
      {active && view?.profile && <ProfileCard profile={view.profile} />}
      {match && <>
        <Text style={styles.body}>{active ? 'You both liked each other in this fictional preview.'
          : match.state === 'unmatched' ? 'You are unmatched. New contact is unavailable.' : 'This connection is unavailable for new contact.'}</Text>
        <Text style={styles.small}>Messaging is unavailable. This preview has no provider channel, messages or history access.</Text>
        {match.state !== 'unmatched' && <>
          <Text style={styles.body}>Unmatching ends this connection. You can unmatch while your profile is paused or your account is restricted. This preview does not offer undo or rematching.</Text>
          <ActionButton label="Unmatch" testID="match-unmatch" disabled={state.status === 'pending'}
            onPress={() => void store.unmatch(match.match_id)} />
        </>}
      </>}
    </View>
    <Button label="Back to your matches" testID="match-back" secondary onPress={() => router.replace('/matches')} />
    <MatchNavigation />
  </Page>;
}
