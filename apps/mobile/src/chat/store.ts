import type { ConversationMessage, ConversationSummary, MessageIntent, MessagePage } from '../contracts/generated/gapp-api-v1.ts';
import type { ProfileStore } from '../profiles/store.ts';
import { ChatFailure, type ChatClient, type ChatFailureCode } from './client.ts';

/** Point d: an open conversation asks for newer messages every 3 seconds while the app is in the foreground. */
export const CONVERSATION_POLL_MS = 3_000;
/** Point d: the conversation list is read when shown, and every 30 seconds while it stays shown. */
export const CONVERSATION_LIST_POLL_MS = 30_000;
/** Messages per page request; the contract allows 1 to 50. */
export const CONVERSATION_PAGE_LIMIT = 20;

export type ChatTimers = Readonly<{ setInterval: (callback: () => void, milliseconds: number) => unknown; clearInterval: (handle: unknown) => void }>;
/** The app's own foreground state (React Native's `AppState`): only `active` is the foreground. */
export type AppActivity = Readonly<{ current: () => string | null; subscribe: (listener: (state: string) => void) => () => void }>;
/** Glow's own match projections: a signal when they may have changed, and the version a send is authorized at. */
export type ChatAuthority = Readonly<{ subscribe: (listener: () => void) => () => void; contactVersion: (matchId: string) => number | null }>;
export const systemTimers: ChatTimers = Object.freeze({
  setInterval: (callback: () => void, milliseconds: number) => setInterval(callback, milliseconds),
  clearInterval: (handle: unknown) => clearInterval(handle as ReturnType<typeof setInterval>),
});

export type ChatState = Readonly<{
  list: Readonly<{ status: 'idle' | 'loading' | 'ready' | 'error'; conversations: readonly ConversationSummary[]; error: ChatFailureCode | null }>;
  selectedMatchId: string | null;
  conversation: Readonly<{ status: 'idle' | 'loading' | 'ready' | 'error' | 'revoked'; messages: readonly ConversationMessage[];
    hasOlder: boolean; older: 'idle' | 'loading' | 'error'; error: ChatFailureCode | null }>;
  draft: string;
  send: Readonly<{ status: 'idle' | 'pending' | 'sent' | 'error'; error: ChatFailureCode | null; canRetry: boolean }>;
}>;
type Submission = Readonly<{ intent: MessageIntent; epoch: number }>;
type Options = Readonly<{ profiles: ProfileStore; authority: ChatAuthority; client: ChatClient; activity: AppActivity; timers?: ChatTimers }>;

const emptyList: ChatState['list'] = Object.freeze({ status: 'idle', conversations: [], error: null });
const emptyConversation: ChatState['conversation'] = Object.freeze({ status: 'idle', messages: [], hasOlder: false, older: 'idle', error: null });
const idleSend: ChatState['send'] = Object.freeze({ status: 'idle', error: null, canRetry: false });
const codeOf = (error: unknown): ChatFailureCode => error instanceof ChatFailure ? error.code : 'invalid_response';
const ends = (code: ChatFailureCode) => code === 'unavailable' || code === 'signed_out';
const isAccepted = (message: ConversationMessage) => message.author === 'other' || message.delivery === 'accepted';
const sameSummary = (a: ConversationSummary | undefined, b: ConversationSummary | undefined) => a === b || (a !== undefined && b !== undefined
  && a.state === b.state && a.unread_count === b.unread_count && a.latest?.submission_id === b.latest?.submission_id && a.latest?.at === b.latest?.at);
let keySerial = 0;

/**
 * The chat screens' presentation state (P06.2 Stage C2). Every result comes through the
 * client boundary; nothing here authorizes anything.
 *
 * - **Keys and order.** Messages are keyed on `submission_id`, never on `at`, and shown in
 *   the order the pages give: accepted messages, then the member's own unsent ones from the
 *   newest page. Newer messages come with the page's opaque `newer_cursor` and older ones
 *   with `older_cursor`; no position is computed from `at` or from a cursor.
 * - **Polling** (point d). Only while a screen is shown and the app is in the foreground:
 *   the open conversation every `CONVERSATION_POLL_MS`, the list when shown and every
 *   `CONVERSATION_LIST_POLL_MS`. Leaving a screen or the foreground stops it; returning
 *   resumes it with one read. Nothing is requested in the background (DM-22 7.2).
 * - **The read cursor** (point e; CX8, DM-23 2.1 to 2.3) moves forward only, to the newest
 *   accepted message the screen has reported inside the conversation's visible area while the
 *   conversation was shown and the app was in the foreground. A page arriving never moves it.
 *   Until a command has succeeded, the store does not know the server's position, so the
 *   loaded window alone cannot hold a move back (CX10, DM-25 3.1 and 3.2).
 * - **Revocation.** A refusal ends the conversation in Glow's revoked state and drops its
 *   history, draft, cursors and any pending send at once. Every request outstanding then is
 *   invalidated: its response, success or failure, changes nothing and starts nothing
 *   (CX9, DM-24 1.1 to 1.3). Requests made afterwards are decided by Glow as before.
 * - **Sends** reuse the same intent, so the same idempotency key and payload, on retry.
 */
export class ChatStore {
  private state: ChatState = Object.freeze({ list: emptyList, selectedMatchId: null, conversation: emptyConversation, draft: '', send: idleSend });
  private readonly listeners = new Set<() => void>();
  private readonly profiles: ProfileStore;
  private readonly authority: ChatAuthority;
  private readonly client: ChatClient;
  private readonly timers: ChatTimers;
  private ownerKey: string;
  /** Advanced by another owner and by each revocation: a list read made before either is never used (DM-24 1.1). */
  private listEpoch = 0;
  /** Advanced by another conversation, another owner and each revocation: a response to an earlier request is never used. */
  private conversationEpoch = 0;
  private accepted: readonly ConversationMessage[] = [];
  private unsent: readonly ConversationMessage[] = [];
  private olderCursor: string | null = null;
  private newerCursor: string | null = null;
  private lastRead: string | null = null;
  /** The messages the shown screen last reported inside its visible area (`viewed`). */
  private visible: readonly string[] = [];
  /** The newest accepted message that has been in view while shown and in the foreground. */
  private seen: string | null = null;
  /** A cursor command failed without ending access: it is tried again after the next read. */
  private cursorRetry = false;
  /**
   * A cursor command has succeeded since `lastRead` was last cleared (this opening). Until then
   * the server's position is unknown (C2C1-X1), and DM-25 3.1's grounds apply.
   */
  private cursorKnown = false;
  private listShown = false;
  private conversationShown = false;
  private foreground: boolean;
  private revalidate = false;
  private listTimer: unknown = null;
  private conversationTimer: unknown = null;
  private listInFlight: number | null = null;
  private headInFlight: number | null = null;
  private headAgain = false;
  private olderInFlight: number | null = null;
  private cursorInFlight: number | null = null;
  private sending: Submission | null = null;
  private retryable: Submission | null = null;
  constructor(options: Options) {
    this.profiles = options.profiles; this.authority = options.authority; this.client = options.client;
    this.timers = options.timers ?? systemTimers;
    this.foreground = options.activity.current() === 'active';
    this.ownerKey = this.profiles.getSnapshot().ownerKey;
    this.profiles.subscribe(() => this.ownerChanged());
    this.authority.subscribe(() => this.authorityChanged());
    options.activity.subscribe(state => this.activityChanged(state));
  }
  readonly subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  readonly getSnapshot = () => this.state;
  private publish(patch: Partial<ChatState>) { this.state = Object.freeze({ ...this.state, ...patch }); this.listeners.forEach(listener => listener()); }
  private publishConversation(patch: Partial<ChatState['conversation']>) {
    this.publish({ conversation: Object.freeze({ ...this.state.conversation, ...patch,
      messages: Object.freeze([...this.accepted, ...this.unsent]), hasOlder: this.olderCursor !== null }) });
  }

  // -- screens and the app's foreground ------------------------------------------------

  /** Selects the conversation the `/conversation` route shows; a different one starts empty. */
  select(matchId: string) {
    if (this.state.selectedMatchId === matchId) return;
    this.resetConversation(matchId);
  }
  showList() { this.listShown = true; if (this.foreground) void this.readList(); this.schedule(); }
  hideList() { this.listShown = false; this.schedule(); }
  openConversation() { this.conversationShown = true; if (this.foreground) void this.readHead(false); this.schedule(); }
  closeConversation() { this.conversationShown = false; this.visible = []; this.schedule(); }
  refreshList() { void this.readList(); }
  retryRead() { void this.readHead(true); }
  /**
   * The shown conversation screen reports the messages now inside its visible area, measured
   * from the rendered layout (DM-23 2.1). Only accepted messages count; a report while the
   * screen is not shown is ignored, and one in the background counts once the app returns.
   */
  viewed(submissionIds: readonly string[]) {
    if (!this.conversationShown) return;
    this.visible = submissionIds;
    this.noteSeen();
  }
  private indexOf(submissionId: string | null) {
    return submissionId === null ? -1 : this.accepted.findIndex(message => message.submission_id === submissionId);
  }
  /** Moves `seen` forward to the newest accepted message in view; never backward. */
  private noteSeen() {
    if (!this.conversationShown || !this.foreground) return;
    const visible = new Set(this.visible);
    const index = this.accepted.findLastIndex(message => visible.has(message.submission_id));
    if (index <= this.indexOf(this.seen)) return;
    this.seen = this.accepted[index]!.submission_id;
    void this.moveReadCursor();
  }
  private activityChanged(state: string) {
    const foreground = state === 'active';
    if (foreground === this.foreground) return;
    this.foreground = foreground;
    if (foreground) {
      if (this.listShown) void this.readList();
      if (this.conversationShown || this.revalidate) void this.readHead(true);
      this.revalidate = false;
      // What stayed in view counts now; a move deferred by the background is sent now.
      this.noteSeen();
      void this.moveReadCursor();
    }
    this.schedule();
  }
  /** A match projection may have changed (an unmatch, a block, a pause): ask Glow again now, in the foreground only. */
  private authorityChanged() {
    if (!this.foreground) { this.revalidate = true; return; }
    if (this.state.selectedMatchId && this.state.conversation.status !== 'idle') void this.readHead(true);
    if (this.listShown) void this.readList();
  }
  private ownerChanged() {
    const key = this.profiles.getSnapshot().ownerKey;
    if (key === this.ownerKey && this.profiles.captureInteractionOwner()) return;
    if (key === this.ownerKey && this.state.selectedMatchId === null && this.state.list === emptyList) return;
    // Another account, a signed-out or restricted one: nothing private is retained.
    this.ownerKey = key; this.listEpoch += 1;
    this.publish({ list: emptyList });
    this.resetConversation(null);
  }
  private resetConversation(matchId: string | null) {
    this.conversationEpoch += 1;
    this.accepted = []; this.unsent = []; this.olderCursor = null; this.newerCursor = null; this.lastRead = null;
    this.visible = []; this.seen = null; this.cursorRetry = false; this.cursorKnown = false;
    this.sending = null; this.retryable = null; this.headAgain = false;
    this.publish({ selectedMatchId: matchId, conversation: emptyConversation, draft: '', send: idleSend });
    this.schedule();
  }
  private schedule() {
    const conversation = this.conversationShown && this.foreground && this.state.selectedMatchId !== null && this.state.conversation.status !== 'revoked';
    if (conversation && this.conversationTimer === null) this.conversationTimer = this.timers.setInterval(() => this.poll(), CONVERSATION_POLL_MS);
    if (!conversation && this.conversationTimer !== null) { this.timers.clearInterval(this.conversationTimer); this.conversationTimer = null; }
    const list = this.listShown && this.foreground;
    if (list && this.listTimer === null) this.listTimer = this.timers.setInterval(() => { if (this.listShown && this.foreground) void this.readList(); }, CONVERSATION_LIST_POLL_MS);
    if (!list && this.listTimer !== null) { this.timers.clearInterval(this.listTimer); this.listTimer = null; }
  }
  private poll() { if (this.conversationShown && this.foreground) void this.readHead(false); }

  // -- reads ---------------------------------------------------------------------------

  private async readList() {
    const epoch = this.listEpoch;
    if (this.listInFlight === epoch) return;
    this.listInFlight = epoch;
    if (this.state.list.status === 'idle') this.publish({ list: Object.freeze({ ...this.state.list, status: 'loading' }) });
    try {
      const list = await this.client.conversations();
      // Made before a revocation: it could put the revoked conversation's row back (DM-24 1.1).
      if (epoch !== this.listEpoch) return;
      const before = this.summary();
      this.publish({ list: Object.freeze({ status: 'ready', conversations: list.conversations, error: null }) });
      // A changed summary is new evidence for a move held back while the position is unknown (DM-25 3.2).
      if (!sameSummary(before, this.summary())) void this.moveReadCursor();
    } catch (error) {
      if (epoch !== this.listEpoch) return;
      const code = codeOf(error);
      // A refused response is never partly used; earlier validated entries stay unless access ended.
      this.publish({ list: Object.freeze({ status: 'error', conversations: ends(code) ? [] : this.state.list.conversations, error: code }) });
    } finally { if (this.listInFlight === epoch) this.listInFlight = null; }
  }
  /** The newest page, or the page after `newer_cursor`. `again` queues one more read behind one in flight. */
  private async readHead(again: boolean) {
    const matchId = this.state.selectedMatchId, epoch = this.conversationEpoch;
    if (!matchId) return;
    if (this.headInFlight === epoch) { this.headAgain ||= again; return; }
    this.headInFlight = epoch;
    const cursor = this.newerCursor;
    if (this.state.conversation.status === 'idle' || this.state.conversation.status === 'revoked') this.publishConversation({ status: 'loading', error: null });
    try {
      const page = await this.client.messages(matchId, cursor, CONVERSATION_PAGE_LIMIT);
      if (epoch !== this.conversationEpoch) return;
      this.mergeHead(page, cursor === null);
      this.publishConversation({ status: 'ready', error: null });
      this.schedule();
      // A page never moves the cursor itself (DM-23 2.1); it only retries a failed move to `seen`.
      if (this.cursorRetry) void this.moveReadCursor();
    } catch (error) {
      if (epoch !== this.conversationEpoch) return;
      const code = codeOf(error);
      if (ends(code)) this.revoke(code);
      else if (code === 'stale') { this.newerCursor = null; this.headAgain = true; }
      else this.publishConversation({ status: 'error', error: code });
    } finally {
      if (this.headInFlight === epoch) {
        this.headInFlight = null;
        if (this.headAgain && epoch === this.conversationEpoch) { this.headAgain = false; if (this.foreground) void this.readHead(false); }
      }
    }
  }
  private mergeHead(page: MessagePage, newest: boolean) {
    const accepted = page.messages.filter(isAccepted), unsent = page.messages.filter(message => !isAccepted(message));
    if (newest) {
      this.accepted = accepted; this.unsent = unsent; this.olderCursor = page.older_cursor; this.newerCursor = page.newer_cursor;
      return;
    }
    const positions = new Map(this.accepted.map((message, index) => [message.submission_id, index] as const));
    const next = [...this.accepted];
    for (const message of accepted) {
      const index = positions.get(message.submission_id);
      if (index === undefined) next.push(message); else next[index] = message;
    }
    this.accepted = next;
    const acceptedIds = new Set(next.map(message => message.submission_id));
    // Own unsent submissions come only on a page at the head; fewer than a full page, or any unsent row, shows it is.
    this.unsent = (unsent.length > 0 || accepted.length < CONVERSATION_PAGE_LIMIT ? unsent : this.unsent).filter(message => !acceptedIds.has(message.submission_id));
    this.newerCursor = page.newer_cursor ?? this.newerCursor;
  }
  async loadOlder() {
    const matchId = this.state.selectedMatchId, epoch = this.conversationEpoch, cursor = this.olderCursor;
    if (!matchId || !cursor || this.olderInFlight === epoch || this.state.conversation.status === 'revoked') return;
    this.olderInFlight = epoch;
    this.publishConversation({ older: 'loading' });
    try {
      const page = await this.client.messages(matchId, cursor, CONVERSATION_PAGE_LIMIT);
      if (epoch !== this.conversationEpoch) return;
      const known = new Set(this.accepted.map(message => message.submission_id));
      const earlier = page.messages.filter(message => isAccepted(message) && !known.has(message.submission_id));
      this.accepted = [...earlier, ...this.accepted];
      this.olderCursor = page.older_cursor;
      this.publishConversation({ older: 'idle' });
      // Messages before `seen` are new evidence for a move held back while the position is unknown (DM-25 3.2).
      if (earlier.length > 0 && this.seen !== null) void this.moveReadCursor();
    } catch (error) {
      if (epoch !== this.conversationEpoch) return;
      const code = codeOf(error);
      if (ends(code)) this.revoke(code); else this.publishConversation({ older: 'error' });
    } finally { if (this.olderInFlight === epoch) this.olderInFlight = null; }
  }
  /** The conversation's entry in the store's list, as the last list read or cursor command returned it. */
  private summary() {
    const matchId = this.state.selectedMatchId;
    return matchId === null ? undefined : this.state.list.conversations.find(entry => entry.match_id === matchId);
  }
  /**
   * Point e (DM-23 2.1 to 2.3, DM-25 3.1): forward only, to `seen`, and only when that passes a
   * message from the other member. Until a command has succeeded, the server's position is
   * unknown, so a move is also sent when the summary held shows an unread count above zero, or
   * when no summary is held; the server moves the cursor forward only. One command at a time;
   * a move made while one is in flight follows it.
   */
  private async moveReadCursor() {
    const matchId = this.state.selectedMatchId, epoch = this.conversationEpoch;
    if (!matchId || !this.foreground || this.cursorInFlight === epoch || this.state.conversation.status === 'revoked') return;
    const from = this.indexOf(this.lastRead), to = this.indexOf(this.seen);
    if (to <= from) return;
    const passesOther = this.accepted.slice(from + 1, to + 1).some(message => message.author === 'other');
    const held = this.summary();
    if (!passesOther && (this.cursorKnown || (held !== undefined && held.unread_count === 0))) return;
    const target = this.accepted[to]!;
    this.cursorInFlight = epoch;
    let moved = false;
    try {
      const summary = await this.client.readCursor(this.client.readCursorIntent(matchId, target.submission_id));
      if (epoch !== this.conversationEpoch) return;
      this.lastRead = target.submission_id; this.cursorRetry = false; this.cursorKnown = true; moved = true;
      this.publish({ list: Object.freeze({ ...this.state.list,
        conversations: this.state.list.conversations.map(entry => entry.match_id === summary.match_id ? summary : entry) }) });
    } catch (error) {
      if (epoch !== this.conversationEpoch) return;
      if (ends(codeOf(error))) this.revoke(codeOf(error)); else this.cursorRetry = true;
    } finally { if (this.cursorInFlight === epoch) this.cursorInFlight = null; }
    if (moved) void this.moveReadCursor();
  }
  /**
   * CX9 (DM-24 1.1 and 1.2): advancing both epochs invalidates every request outstanding now
   * (a head read and one queued behind it, an older page, a cursor command, a send and a list
   * read), so none of their responses can restore the history, the composer or the row. A
   * pending send is dropped with them. Requests made afterwards carry the new epochs (1.3).
   */
  private revoke(code: ChatFailureCode) {
    const matchId = this.state.selectedMatchId;
    this.conversationEpoch += 1; this.listEpoch += 1;
    this.accepted = []; this.unsent = []; this.olderCursor = null; this.newerCursor = null; this.lastRead = null;
    this.visible = []; this.seen = null; this.cursorRetry = false; this.cursorKnown = false;
    this.sending = null; this.retryable = null; this.headAgain = false;
    this.publishConversation({ status: 'revoked', older: 'idle', error: code });
    this.publish({ draft: '', send: idleSend,
      list: Object.freeze({ ...this.state.list, conversations: this.state.list.conversations.filter(entry => entry.match_id !== matchId) }) });
    this.schedule();
  }

  // -- the composer --------------------------------------------------------------------

  setDraft(text: string) { if (this.state.conversation.status !== 'revoked') this.publish({ draft: text }); }
  async send() {
    const matchId = this.state.selectedMatchId;
    if (!matchId || this.sending || this.state.conversation.status === 'revoked') return;
    const version = this.authority.contactVersion(matchId);
    if (version === null) { this.publish({ send: Object.freeze({ status: 'error', error: 'unavailable', canRetry: false }) }); return; }
    let intent: MessageIntent;
    const key = `chat-message:${(++keySerial).toString(36)}-${Math.random().toString(36).slice(2, 12)}`;
    try { intent = this.client.messageIntent(matchId, this.state.draft, version, key); }
    catch (error) { this.publish({ send: Object.freeze({ status: 'error', error: codeOf(error), canRetry: false }) }); return; }
    this.retryable = null;
    this.publish({ draft: '' });
    await this.run(Object.freeze({ intent, epoch: this.conversationEpoch }));
  }
  /** The same intent again: the same idempotency key and payload, so at most one message. */
  async retrySend() {
    if (this.sending || !this.retryable || this.retryable.epoch !== this.conversationEpoch) return;
    await this.run(this.retryable);
  }
  private async run(submission: Submission) {
    this.sending = submission;
    this.publish({ send: Object.freeze({ status: 'pending', error: null, canRetry: false }) });
    try {
      await this.client.send(submission.intent);
      if (this.sending !== submission || submission.epoch !== this.conversationEpoch) return;
      this.retryable = null;
      this.publish({ send: Object.freeze({ status: 'sent', error: null, canRetry: false }) });
      if (this.foreground) void this.readHead(true);
    } catch (error) {
      if (this.sending !== submission || submission.epoch !== this.conversationEpoch) return;
      const failure = error instanceof ChatFailure ? error : new ChatFailure('invalid_response', true);
      // The outcome is unknown or temporary: the same intent may be retried. A refusal is final.
      this.retryable = failure.retryable && !ends(failure.code) ? submission : null;
      this.publish({ send: Object.freeze({ status: 'error', error: failure.code, canRetry: this.retryable !== null }) });
      if (ends(failure.code)) this.revoke(failure.code);
    } finally { if (this.sending === submission) this.sending = null; }
  }
}
