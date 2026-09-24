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
    <Button label="Your profile and preferences" testID="open-profile" secondary onPress={() => router.push('/profile')} />
    <Button label="Development scenarios" testID="development-link" secondary onPress={() => router.push('/development')} />
    <Button label="Log out" testID="logout" secondary onPress={() => { store.logout(); router.replace('/'); }} />
  </View>;
}

export function MatchesScreen() {
  const { store, state } = useInteractions();
  useFocusEffect(useCallback(() => { store.refresh(); }, [store]));
  return <Page testID="screen-matches">
    <PreviewNotice />
    <ScreenTitle>Your matches</ScreenTitle>
    <Text style={styles.body}>A mutual match appears only after both fictional people have committed a like. A match does not enable messaging in this preview.</Text>
    <InteractionFeedback />
    <View style={styles.group} testID="match-list">
      {state.matches.length === 0 && <Text style={styles.body} testID="matches-empty">No mutual matches yet. A like on its own is private and is not a match.</Text>}
      {state.matches.map(match => <View key={match.match_id} style={styles.notice} testID={`match-row-${match.match_id}`}>
        <Text style={styles.subtitle} accessibilityRole="header">{match.state === 'active' && match.profile ? match.profile.display_name : 'Connection unavailable'}</Text>
        <Text style={styles.body}>{match.state === 'active' ? 'Mutual match' : match.state === 'unmatched' ? 'Unmatched. New contact is unavailable.' : 'New contact is unavailable.'}</Text>
        <Button label={match.state === 'active' && match.profile ? `View match with ${match.profile.display_name}` : 'View connection status'}
          testID={`match-open-${match.match_id}`} secondary onPress={() => { store.selectMatch(match.match_id); router.push('/match'); }} />
      </View>)}
    </View>
    <Button label="Refresh matches" testID="matches-refresh" secondary disabled={state.status === 'pending'} onPress={() => store.refresh()} />
    <MatchNavigation />
  </Page>;
}

export function MatchScreen() {
  const { store, state } = useInteractions();
  useFocusEffect(useCallback(() => { store.refresh(); return () => store.cancelPending(); }, [store]));
  const match = state.matches.find(item => item.match_id === state.selectedMatchId);
  return <Page testID="screen-match">
    <PreviewNotice />
    <ScreenTitle>{match?.state === 'active' ? 'A mutual connection.' : 'Connection status'}</ScreenTitle>
    <InteractionFeedback />
    <View style={styles.group} testID="match-detail">
      {!match && <Text style={styles.body}>This connection is unavailable. Return to your matches to check current access.</Text>}
      {match?.state === 'active' && match.profile && <ProfileCard profile={match.profile} />}
      {match && <>
        <Text style={styles.body}>{match.state === 'active' ? 'You both liked each other in this fictional preview.'
          : match.state === 'unmatched' ? 'You are unmatched. New contact is unavailable.' : 'This connection is unavailable for new contact.'}</Text>
        <Text style={styles.small}>Messaging is unavailable. This preview has no provider channel, messages or history access.</Text>
        {match.state !== 'unmatched' && <>
          <Text style={styles.body}>Unmatching ends this connection. It remains available while your profile is paused. This preview does not offer undo or rematching.</Text>
          <ActionButton label="Unmatch" testID="match-unmatch" disabled={state.status === 'pending'}
            onPress={() => void store.unmatch(match.match_id)} />
        </>}
      </>}
    </View>
    <Button label="Back to your matches" testID="match-back" secondary onPress={() => router.replace('/matches')} />
    <MatchNavigation />
  </Page>;
}
