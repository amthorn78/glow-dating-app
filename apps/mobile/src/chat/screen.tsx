import { useCallback, useLayoutEffect, useRef, type PropsWithChildren } from 'react';
import { router, useFocusEffect } from 'expo-router';
import { KeyboardAvoidingView, Platform, ScrollView, StyleSheet, Text, View,
  type LayoutChangeEvent, type NativeScrollEvent, type NativeSyntheticEvent } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import type { ConversationMessage } from '../contracts/generated/gapp-api-v1';
import { Button, Field, Page, PreviewNotice, ScreenTitle, colors, styles } from '../components/ui';
import { ActionButton } from '../interactions/action-button';
import { useInteractions } from '../interactions/context';
import { useChat } from './context';
import { ChatFixtureControls } from './controls';
import { DELIVERY_COPY, LIST_COPY, READ_COPY, REVOKED_DETAIL, SEND_COPY, UNAVAILABLE_MESSAGE, timeLabel, unreadLabel } from './copy';
import type { ChatStore } from './store';
import { visibleMessages, type Box, type VisibleArea } from './visibility';

/** Names come from Glow's own match projections, never from a chat response (ADR 0003, decision 1). */
function useMatchNames() {
  const { state } = useInteractions();
  return new Map(state.matches.filter(match => match.state === 'active' && match.profile)
    .map(match => [match.match_id, match.profile!.display_name] as const));
}

function ChatNavigation() {
  return <View style={styles.group}>
    <Button label="Your matches" testID="open-matches" secondary onPress={() => router.push('/matches')} />
    <Button label="Development scenarios" testID="development-link" secondary onPress={() => router.push('/development')} />
  </View>;
}

export function ConversationsScreen() {
  const { store, state } = useChat();
  const names = useMatchNames();
  useFocusEffect(useCallback(() => { store.showList(); return () => store.hideList(); }, [store]));
  const { list } = state;
  return <Page testID="screen-conversations">
    <PreviewNotice />
    <ScreenTitle>Your conversations</ScreenTitle>
    <Text style={styles.body}>A conversation opens with a mutual match. Messages in this preview are fictional and last only for this session.</Text>
    {list.error && <Text style={styles.error} accessibilityRole="alert" testID="conversations-error">{LIST_COPY[list.error]}</Text>}
    <View style={styles.group} testID="conversation-list">
      {list.status === 'loading' && <Text style={styles.body}>Loading your conversations…</Text>}
      {list.status === 'ready' && list.conversations.length === 0 && <Text style={styles.body} testID="conversations-empty">No conversations yet. A conversation opens with a mutual match.</Text>}
      {list.conversations.map(conversation => {
        const name = names.get(conversation.match_id) ?? 'Your match';
        return <View key={conversation.match_id} style={styles.notice} testID={`conversation-row-${conversation.match_id}`}>
          <Text style={styles.subtitle} accessibilityRole="header">{name}</Text>
          <Text style={styles.body} testID={`conversation-unread-${conversation.match_id}`}>{unreadLabel(conversation.unread_count)}</Text>
          <Text style={styles.small}>{conversation.latest ? `Latest message ${timeLabel(conversation.latest.at)}` : 'No messages yet'}</Text>
          <Button label={`Open conversation with ${name}`} testID={`conversation-open-${conversation.match_id}`} secondary
            onPress={() => { store.select(conversation.match_id); router.push('/conversation'); }} />
        </View>;
      })}
    </View>
    <Button label="Refresh conversations" testID="conversations-refresh" secondary onPress={() => store.refreshList()} />
    <ChatFixtureControls matchId={list.conversations[0]?.match_id ?? null} compact />
    <ChatNavigation />
  </Page>;
}

function MessageRow({ message, name, rowRef }: { message: ConversationMessage; name: string; rowRef: (node: View | null) => void }) {
  const own = message.author === 'own';
  const delivery = own && message.delivery ? ` · ${DELIVERY_COPY[message.delivery]}` : '';
  return <View ref={rowRef} style={[styles.notice, own ? chat.own : chat.other]} testID={`message-${message.submission_id}`}>
    <Text style={styles.eyebrow}>{own ? 'YOU' : name.toUpperCase()}</Text>
    {message.content === 'text' && message.text !== null
      ? <Text style={styles.body} testID="message-text">{message.text}</Text>
      : <Text style={styles.body} testID="message-unavailable">{UNAVAILABLE_MESSAGE}</Text>}
    <Text style={styles.small}>{timeLabel(message.at)}{delivery}</Text>
  </View>;
}

function Composer() {
  const { store, state } = useChat();
  const pending = state.send.status === 'pending';
  return <View style={styles.group} testID="composer" accessibilityLiveRegion="polite">
    <Field label="Message" value={state.draft} onChangeText={text => store.setDraft(text)} multiline editable={!pending}
      autoCapitalize="sentences" testID="composer-input" />
    <ActionButton label="Send message" testID="composer-send" disabled={pending} onPress={() => void store.send()} />
    {pending && <Text style={styles.body} accessibilityRole="progressbar" testID="send-pending">Sending your message…</Text>}
    {state.send.status === 'error' && state.send.error && <Text style={styles.error} accessibilityRole="alert" testID="send-error">{SEND_COPY[state.send.error]}</Text>}
    {state.send.canRetry && <ActionButton label="Retry the same message" testID="send-retry" secondary disabled={pending} onPress={() => void store.retrySend()} />}
  </View>;
}

type Viewing = ReturnType<typeof useViewedMessages>;

/**
 * Which messages are inside the conversation's visible area (CX8; DM-23 2.1 and 2.2), from
 * the rendered layout: each row measured against the scroll content's origin with React
 * Native's `measureLayout`, and the scroll view's `onLayout` height and `onScroll` offset.
 * Rows are measured again after every render and size change, since a row can move without
 * resizing (a page of earlier messages above it, a notice), and React Native Web's `onLayout`
 * reports size changes only. A row not yet measured in the current pass is never in view.
 * The store decides what the report moves (`ChatStore.viewed`); nothing here sends anything.
 */
function useViewedMessages(store: ChatStore, messages: readonly ConversationMessage[]) {
  const content = useRef<View>(null);
  const rows = useRef(new Map<string, View>());
  const boxes = useRef(new Map<string, Box>());
  const area = useRef<VisibleArea>({ offset: 0, height: 0 });
  const order = useRef<readonly string[]>([]);
  const report = useCallback(() => { store.viewed(visibleMessages(order.current, boxes.current, area.current)); }, [store]);
  const measure = useCallback(() => {
    const origin = content.current;
    const pass = new Map<string, Box>();
    boxes.current = pass;
    report();
    if (!origin) return;
    rows.current.forEach((node, id) => node.measureLayout(origin, (_left, top, _width, height) => {
      if (boxes.current !== pass) return;
      pass.set(id, { top, height }); report();
    }, () => undefined));
  }, [report]);
  useLayoutEffect(() => { order.current = messages.map(message => message.submission_id); measure(); });
  const rowRef = useCallback((id: string) => (node: View | null) => {
    if (node) rows.current.set(id, node); else rows.current.delete(id);
  }, []);
  const onLayout = useCallback((event: LayoutChangeEvent) => {
    area.current = { ...area.current, height: event.nativeEvent.layout.height }; report();
  }, [report]);
  const onScroll = useCallback((event: NativeSyntheticEvent<NativeScrollEvent>) => {
    const { contentOffset, layoutMeasurement } = event.nativeEvent;
    area.current = { offset: contentOffset.y, height: layoutMeasurement.height || area.current.height }; report();
  }, [report]);
  return { content, rowRef, measure, report, onLayout, onScroll };
}

/**
 * The conversation's own scroll container: `Page`'s structure, unchanged for every other
 * screen, with the content in one view whose origin is the scroll content's origin.
 */
function ConversationPage({ viewing, children }: PropsWithChildren<{ viewing: Viewing }>) {
  return <SafeAreaView style={styles.safe} testID="screen-conversation"><KeyboardAvoidingView style={styles.flex}
    behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
    {/* RNWeb dismisses on programmatic scroll too; preserve browser input focus. */}
    <ScrollView testID="conversation-scroll" keyboardShouldPersistTaps="handled" keyboardDismissMode={Platform.OS === 'web' ? 'none' : 'on-drag'}
      scrollEventThrottle={16} onLayout={viewing.onLayout} onScroll={viewing.onScroll}>
      <View ref={viewing.content} style={styles.page} onLayout={viewing.measure}>{children}</View>
    </ScrollView>
  </KeyboardAvoidingView></SafeAreaView>;
}

export function ConversationScreen() {
  const { store, state } = useChat();
  const names = useMatchNames();
  const { conversation, selectedMatchId } = state;
  const viewing = useViewedMessages(store, conversation.messages);
  const { report } = viewing;
  useFocusEffect(useCallback(() => { store.openConversation(); report(); return () => store.closeConversation(); }, [store, report]));
  const revoked = selectedMatchId === null || conversation.status === 'revoked';
  const name = selectedMatchId ? names.get(selectedMatchId) ?? null : null;
  return <ConversationPage viewing={viewing}>
    <PreviewNotice />
    <ScreenTitle>{!revoked && name ? `Conversation with ${name}` : 'Conversation'}</ScreenTitle>
    {revoked ? <View style={styles.notice} testID="conversation-revoked">
      <Text style={styles.subtitle} accessibilityRole="alert">{READ_COPY[conversation.error ?? 'unavailable']}</Text>
      <Text style={styles.body}>{REVOKED_DETAIL}</Text>
    </View> : <>
      {conversation.status === 'loading' && <Text style={styles.body} accessibilityRole="progressbar">Loading messages…</Text>}
      {conversation.status === 'error' && conversation.error && <View style={styles.notice} testID="conversation-error">
        <Text style={styles.error} accessibilityRole="alert">{READ_COPY[conversation.error]}</Text>
        <Button label="Try again" testID="conversation-retry" secondary onPress={() => store.retryRead()} />
      </View>}
      {conversation.hasOlder && <Button label="Show earlier messages" testID="conversation-older" secondary
        disabled={conversation.older === 'loading'} onPress={() => void store.loadOlder()} />}
      {conversation.older === 'error' && <Text style={styles.error} accessibilityRole="alert">Earlier messages could not be loaded. Try again.</Text>}
      <View style={styles.group} testID="message-list">
        {conversation.status === 'ready' && conversation.messages.length === 0 && <Text style={styles.body} testID="conversation-empty">No messages yet.</Text>}
        {conversation.messages.map(message => <MessageRow key={message.submission_id} message={message} name={name ?? 'Your match'}
          rowRef={viewing.rowRef(message.submission_id)} />)}
      </View>
      <Composer />
    </>}
    <ChatFixtureControls matchId={revoked ? null : selectedMatchId} />
    <Button label="Back to your conversations" testID="conversation-back" secondary onPress={() => router.replace('/conversations')} />
    <ChatNavigation />
  </ConversationPage>;
}

const chat = StyleSheet.create({
  own: { borderColor: colors.accent, marginLeft: 32 },
  other: { marginRight: 32 },
});
