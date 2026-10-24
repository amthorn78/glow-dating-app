import corpus from '../../../../packages/contracts/fixtures/interactions-v1.json' with { type: 'json' };
import type { BlockIntent, ConversationMessage, ConversationSummary, Error as ApiError, LatestMessageMarker, MessageIntent,
  MessagePageRequest, ReadCursorIntent } from '../contracts/generated/gapp-api-v1.ts';
import { validateMessagePageRequest } from '../contracts/generated/validators.js';
import { parseAppIntent } from '../contracts/production.ts';
import type { FixtureInteractionAdapter } from '../interactions/fixture-adapter.ts';
import type { ProfileStore } from '../profiles/store.ts';
import { ChatTransportError, type ChatTransport } from './transport.ts';

/** P05's delivery scenarios, applied to chat requests: offline and a lost response to every request, a delay to sends. */
export type ChatScenario = 'normal' | 'offline' | 'lost_response' | 'delayed';
/** What the fixture's provider does with the member's next sends: accept, hold pending, or fail. */
export type OwnDelivery = 'accept' | 'hold' | 'fail';
/**
 * Provider fields the display-rule test plants in a response (ADR 0003; the brief's point g).
 * Glow's contracts carry none of them, so the client's generated validators refuse each one.
 */
export const PROVIDER_FIELD_CASES = ['member_object', 'user_object', 'custom_data', 'member_updated', 'ai_indicator_update',
  'ai_indicator_clear', 'ai_indicator_stop', 'channel_name', 'channel_image', 'channel_object', 'provider_message_id',
  'provider_channel_id', 'provider_user_id', 'provider_timestamp', 'provider_error_text'] as const;
export type ProviderFieldCase = typeof PROVIDER_FIELD_CASES[number];
/** Every planted provider value carries this marker, so a test can show that none reaches a state or a render. */
export const PROVIDER_SENTINEL = 'provider-sentinel';
/** Bounds for one in-memory fixture session; not product limits. */
export const CHAT_FIXTURE_LIMITS = Object.freeze({ submissions: 1_000, requestLog: 200, unsentPerPage: 50 });

type Code = ApiError['code'];
type Refusal = Readonly<{ refused: Code; retryable?: boolean }>;
type Grant = Readonly<{ actor: string; matchId: string; contactVersion: number }>;
/** The member a request acts for: the signed-in viewer, or a fictional participant the fixture composes. */
type Member = Readonly<{ kind: 'viewer' }> | Readonly<{ kind: 'fixture'; profile: string }>;
type Submission = {
  readonly id: string; readonly matchId: string; readonly author: string; readonly text: string;
  readonly contactVersion: number; readonly canonical: string; readonly submitted: number;
  state: 'pending' | 'accepted' | 'failed'; version: number; accepted: number | null; held: boolean;
  /** The text the fixture's provider would return for this message; null when it holds none. */
  providerText: string | null;
};
export type ChatRequestRecord = Readonly<{ operation: 'conversations' | 'messages' | 'send' | 'read_cursor'; matchId: string | null; cursor: string | null }>;

const CONTRACT_VERSION = 'gapp-api-v1';
// Glow's fixture time: one second per recorded event from the onboarding fixture's clock.
const BASE_TIME = Date.parse('2026-09-23T12:00:00Z');
const instant = (tick: number) => new Date(BASE_TIME + tick * 1000).toISOString().slice(0, 19) + 'Z';
const uuid = (kind: number, value: number) => `${kind.toString(16).padStart(8, '0')}-0000-4000-8000-${value.toString(16).padStart(12, '0')}`;
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
/** The send's canonical request, as `request_digest` hashes it: the match, the contact version and the text. */
const canonical = (matchId: string, contactVersion: number, text: string) => `${matchId}\n${contactVersion}\n${text}`;
// An opaque page cursor carrying Glow's identifiers only (the match and one accepted message), as C1's does.
const CURSOR_FORM = /^c1\.([on])\.([0-9a-f]{32})\.([0-9a-f]{32})$/;
const compact = (id: string) => id.replaceAll('-', '');
const expand = (hex: string) => `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
const encodeCursor = (direction: 'older' | 'newer', matchId: string, boundary: string) => `c1.${direction === 'older' ? 'o' : 'n'}.${compact(matchId)}.${compact(boundary)}`;
function decodeCursor(text: string): { direction: 'older' | 'newer'; matchId: string; boundary: string } | null {
  const parts = CURSOR_FORM.exec(text);
  return parts ? { direction: parts[1] === 'o' ? 'older' : 'newer', matchId: expand(parts[2]!), boundary: expand(parts[3]!) } : null;
}

/**
 * In-process substitute for Glow's conversation API (P06.2 Stage C2; C1's semantics, F11
 * under OD-45). It answers the conversation list, a page of messages, a send and the
 * read-cursor command with the JSON bodies Glow's API will return, and nothing else.
 *
 * - **A conversation follows its match.** It exists only for a match the interactions
 *   fixture holds, and every request makes that fixture's contact check: the match active
 *   with its pair current. An unmatch, a block either way, a pause, a consent or eligibility
 *   change and a suspension or deletion the fixture models all refuse a read as they refuse
 *   a send (point c; DM-22 3.1). The refusal is Glow's generic `not_found`, or
 *   `unauthenticated` for the member's own session, and says no more than the match does.
 * - **Glow's rows define the conversation.** Accepted messages come in acceptance order
 *   (DM-22 2.2); the member's own pending and failed submissions follow on the newest page,
 *   to that member only; the other member's never appear (F11). A text is shown only when
 *   the fixture's provider holds exactly the text Glow sent (DM-22 2.1); otherwise the
 *   message is "unavailable", one state with no reason (6.2). A provider-only message never
 *   reaches a page.
 * - **The unread count** counts the other member's accepted messages after the member's read
 *   cursor (6.3); the latest-message marker is computed over the rows the member may see and
 *   carries no text (6.1); the cursor moves only forward, to an accepted message of that
 *   match (point e); a page cursor is opaque and bound to its match (6.4).
 *
 * No network, route, provider, storage or log is involved.
 */
export class FixtureChatAdapter implements ChatTransport {
  private readonly submissions = new Map<string, Submission>();
  private readonly byMatch = new Map<string, Submission[]>();
  private readonly receipts = new Map<string, Readonly<{ canonical: string; submissionId: string }>>();
  private readonly readCursors = new Map<string, number>();
  private readonly providerOnly: string[] = [];
  private readonly listeners = new Set<() => void>();
  private releases: (() => void)[] = [];
  private requestLog: ChatRequestRecord[] = [];
  private clock = 0;
  private serial = 0;
  private fixtureKeys = 0;
  private scenarioValue: ChatScenario = 'normal';
  private deliveryValue: OwnDelivery = 'accept';
  private providerFieldValue: ProviderFieldCase | null = null;
  private outageValue = false;
  readonly profiles: ProfileStore;
  readonly interactions: FixtureInteractionAdapter;
  constructor(profiles: ProfileStore, interactions: FixtureInteractionAdapter) {
    this.profiles = profiles; this.interactions = interactions;
  }
  readonly subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  private emit() { this.listeners.forEach(listener => listener()); }

  // -- the transport: what Glow's API answers the signed-in member ---------------------

  async conversations(): Promise<unknown> {
    this.record({ operation: 'conversations', matchId: null, cursor: null });
    await this.gate(false);
    return this.respond(this.list({ kind: 'viewer' }));
  }
  async messages(request: MessagePageRequest): Promise<unknown> {
    const captured = this.capture(request);
    this.record({ operation: 'messages', matchId: typeof captured?.match_id === 'string' ? captured.match_id : null,
      cursor: typeof captured?.cursor === 'string' ? captured.cursor : null });
    await this.gate(false);
    return this.respond(this.page({ kind: 'viewer' }, captured));
  }
  async send(intent: MessageIntent): Promise<unknown> {
    const captured = this.capture(intent);
    this.record({ operation: 'send', matchId: typeof captured?.match_id === 'string' ? captured.match_id : null, cursor: null });
    await this.gate(true);
    return this.respond(this.submit({ kind: 'viewer' }, captured));
  }
  async readCursor(intent: ReadCursorIntent): Promise<unknown> {
    const captured = this.capture(intent);
    this.record({ operation: 'read_cursor', matchId: typeof captured?.match_id === 'string' ? captured.match_id : null, cursor: null });
    await this.gate(false);
    return this.respond(this.moveCursor({ kind: 'viewer' }, captured));
  }

  /** Own-property data only: a request is read once, as JSON, before any check. */
  private capture(value: unknown): Record<string, unknown> | null {
    try { const copy = clone(value); return copy && typeof copy === 'object' && !Array.isArray(copy) ? copy as Record<string, unknown> : null; } catch { return null; }
  }
  private record(entry: ChatRequestRecord) {
    this.requestLog = [...this.requestLog.slice(1 - CHAT_FIXTURE_LIMITS.requestLog), Object.freeze(entry)];
  }
  private async gate(command: boolean) {
    if (this.scenarioValue === 'offline') throw new ChatTransportError();
    if (command && this.scenarioValue === 'delayed') await new Promise<void>(resolve => { this.releases.push(resolve); });
  }
  /** A lost response commits on the server and then withholds the answer, as P05's scenario does. */
  private respond(body: object): unknown {
    if (this.scenarioValue === 'lost_response') throw new ChatTransportError();
    return this.providerFieldValue ? plantProviderField(body, this.providerFieldValue, this.requestId()) : body;
  }
  private requestId() { return uuid(0x90, ++this.serial); }
  private error(refusal: Refusal): ApiError {
    return { contract_version: CONTRACT_VERSION, request_id: this.requestId(), code: refusal.refused, retryable: refusal.retryable ?? false };
  }
  private success(data: object) { return { contract_version: CONTRACT_VERSION, request_id: this.requestId(), data }; }
  private tick() { return ++this.clock; }

  // -- point c: whatever refuses a send refuses a read ---------------------------------

  private member(member: Member): Readonly<{ actor: string }> | Refusal {
    // The member's own session: unauthenticated. The member's own account no longer active: generic.
    if (!this.profiles.captureInteractionCleanupOwner()) return member.kind === 'viewer' ? { refused: 'unauthenticated' } : { refused: 'not_found' };
    const viewer = this.profiles.captureInteractionOwner();
    if (!viewer) return { refused: 'not_found' };
    if (member.kind === 'viewer') return { actor: viewer.ownerId };
    // A fictional participant of one of the viewer's matches. The grant's membership and contact
    // checks refuse anyone else, and their pause, suspension, deletion or revoked session as the
    // interactions fixture models them.
    const identity = corpus.identities.find(value => value.profile_id === member.profile);
    return identity ? { actor: identity.account_uuid } : { refused: 'not_found' };
  }
  private grant(member: Member, matchId: unknown): Grant | Refusal {
    const found = this.member(member);
    if ('refused' in found) return found;
    if (typeof matchId !== 'string') return { refused: 'invalid_request' };
    const match = this.interactions.inspect().matches.find(value => value.id === matchId);
    if (!match || ![match.first, match.second].includes(found.actor)) return { refused: 'not_found' };
    // The interactions fixture's contact check: the match active, its pair current, both members eligible.
    const contact = this.interactions.contact(matchId);
    if (!contact?.eligible) return { refused: 'not_found' };
    return { actor: found.actor, matchId, contactVersion: contact.contactVersion };
  }
  private memberMatches(member: Member): readonly string[] {
    const found = this.member(member);
    if ('refused' in found) return [];
    return this.interactions.inspect().matches.filter(match => [match.first, match.second].includes(found.actor)).map(match => match.id);
  }

  // -- Glow's rows ---------------------------------------------------------------------

  private rows(matchId: string): readonly Submission[] { return this.byMatch.get(matchId) ?? []; }
  private accepted(matchId: string): Submission[] {
    return this.rows(matchId).filter(row => row.state === 'accepted').sort((a, b) => a.accepted! - b.accepted!);
  }
  private cursorKey(matchId: string, actor: string) { return `${matchId}:${actor}`; }
  private summary(grant: Grant): ConversationSummary {
    const position = this.readCursors.get(this.cursorKey(grant.matchId, grant.actor)) ?? 0;
    const rows = this.rows(grant.matchId);
    // 6.3: the other member's accepted messages after the member's cursor, in acceptance order.
    const unread = rows.filter(row => row.state === 'accepted' && row.author !== grant.actor && row.accepted! > position).length;
    // 6.1: only rows the member may see (accepted, and the member's own pending or failed); no text.
    let latest: Submission | null = null, latestAt = -1;
    for (const row of rows) {
      if (row.state !== 'accepted' && row.author !== grant.actor) continue;
      const at = row.state === 'accepted' ? row.accepted! : row.submitted;
      if (at > latestAt) { latest = row; latestAt = at; }
    }
    const marker: LatestMessageMarker | null = latest ? { submission_id: latest.id, at: instant(latestAt) } : null;
    return { kind: 'conversation', match_id: grant.matchId, state: 'open', unread_count: unread, latest: marker };
  }
  private message(row: Submission, actor: string): ConversationMessage {
    const own = row.author === actor;
    if (row.state !== 'accepted') {
      if (!own) throw new Error('Another member\'s unsent submission never appears.');
      return { submission_id: row.id, author: 'own', at: instant(row.submitted), content: 'text', text: row.text, delivery: row.state };
    }
    // 2.1: the provider's text only when it is exactly the text Glow sent; otherwise one unavailable state (6.2).
    const shown = row.providerText !== null && canonical(row.matchId, row.contactVersion, row.providerText) === row.canonical ? row.providerText : null;
    return { submission_id: row.id, author: own ? 'own' : 'other', at: instant(row.accepted!), content: shown === null ? 'unavailable' : 'text',
      text: shown, delivery: own ? 'accepted' : null };
  }

  // -- the reads and commands, for a member --------------------------------------------

  private list(member: Member): object {
    const found = this.member(member);
    if ('refused' in found) return this.error(found);
    const entries: ConversationSummary[] = [];
    for (const matchId of this.memberMatches(member)) {
      const grant = this.grant(member, matchId);
      if (!('refused' in grant)) entries.push(this.summary(grant));
    }
    entries.sort((a, b) => Number(b.latest !== null) - Number(a.latest !== null) ||
      (b.latest?.at ?? '').localeCompare(a.latest?.at ?? '') || b.match_id.localeCompare(a.match_id));
    return this.success({ kind: 'conversation_list', conversations: entries.slice(0, 200) });
  }
  private page(member: Member, request: Record<string, unknown> | null): object {
    if (!validateMessagePageRequest(request)) return this.error({ refused: 'invalid_request' });
    const { match_id: matchId, cursor, limit } = request as unknown as MessagePageRequest;
    const first = this.grant(member, matchId);
    if ('refused' in first) return this.error(first);
    const accepted = this.accepted(matchId);
    let rows: Submission[], older: boolean, atHead: boolean;
    const decoded = cursor === null ? null : decodeCursor(cursor);
    if (cursor !== null) {
      // 6.4: bound to the match it was issued for, and naming an accepted message of that match.
      const index = decoded && decoded.matchId === matchId ? accepted.findIndex(row => row.id === decoded.boundary) : -1;
      if (!decoded || index < 0) return this.error({ refused: 'stale_version' });
      if (decoded.direction === 'older') {
        const before = accepted.slice(0, index);
        rows = before.slice(-limit); older = before.length > limit; atHead = false;
      } else {
        const after = accepted.slice(index + 1);
        rows = after.slice(0, limit); older = rows.length > 0; atHead = after.length <= limit;
      }
    } else { rows = accepted.slice(-limit); older = accepted.length > limit; atHead = true; }
    const unsent = atHead ? this.rows(matchId).filter(row => row.author === first.actor && row.state !== 'accepted')
      .sort((a, b) => a.submitted - b.submitted).slice(-CHAT_FIXTURE_LIMITS.unsentPerPage) : [];
    // 2.4: the text read failing fails the read; a page with no accepted message reads no text.
    if (rows.length > 0 && this.outageValue) return this.error({ refused: 'provider_unavailable', retryable: true });
    const messages = [...rows.map(row => this.message(row, first.actor)), ...unsent.map(row => this.message(row, first.actor))];
    // The final check, after the text read: a revocation committed meanwhile refuses the page (DM-22 3.2).
    const final = this.grant(member, matchId);
    if ('refused' in final) return this.error(final);
    const last = rows.at(-1);
    const newer = last ? encodeCursor('newer', matchId, last.id) : decoded?.direction === 'newer' ? cursor : null;
    return this.success({ kind: 'message_page', match_id: matchId, messages,
      older_cursor: rows.length > 0 && older ? encodeCursor('older', matchId, rows[0]!.id) : null, newer_cursor: newer });
  }
  private submit(member: Member, intent: Record<string, unknown> | null, delivery: OwnDelivery = this.deliveryValue): object {
    let captured: MessageIntent;
    try { parseAppIntent(intent); if (intent!.operation !== 'message') throw new Error(); captured = intent as unknown as MessageIntent; }
    catch { return this.error({ refused: 'invalid_request' }); }
    // Authorize, then deduplicate: a replay never bypasses a current refusal.
    const grant = this.grant(member, captured.match_id);
    if ('refused' in grant) return this.error(grant);
    if (captured.meta.expected_version !== grant.contactVersion) return this.error({ refused: 'stale_version' });
    const key = `${grant.actor}:message:${captured.meta.idempotency_key}`;
    const request = canonical(grant.matchId, captured.meta.expected_version, captured.text);
    const prior = this.receipts.get(key);
    if (prior) {
      if (prior.canonical !== request) return this.error({ refused: 'idempotency_conflict' });
      return this.success(this.submission(this.submissions.get(prior.submissionId)!));
    }
    if (this.submissions.size >= CHAT_FIXTURE_LIMITS.submissions) return this.error({ refused: 'rate_limited' });
    const row: Submission = { id: uuid(0x91, ++this.serial), matchId: grant.matchId, author: grant.actor, text: captured.text,
      contactVersion: grant.contactVersion, canonical: request, submitted: this.tick(), state: 'pending', version: 1, accepted: null,
      held: delivery === 'hold', providerText: null };
    this.submissions.set(row.id, row); this.byMatch.set(row.matchId, [...this.rows(row.matchId), row]);
    this.receipts.set(key, Object.freeze({ canonical: request, submissionId: row.id }));
    if (delivery === 'accept') this.accept(row);
    if (delivery === 'fail') { row.state = 'failed'; row.version += 1; }
    return this.success(this.submission(row));
  }
  private submission(row: Submission) { return { kind: 'message', submission_id: row.id, version: row.version, state: row.state }; }
  private accept(row: Submission) {
    row.state = 'accepted'; row.version += 1; row.accepted = this.tick(); row.held = false; row.providerText = row.text;
  }
  private moveCursor(member: Member, intent: Record<string, unknown> | null): object {
    let captured: ReadCursorIntent;
    try { parseAppIntent(intent); if (intent!.operation !== 'read_cursor') throw new Error(); captured = intent as unknown as ReadCursorIntent; }
    catch { return this.error({ refused: 'invalid_request' }); }
    const grant = this.grant(member, captured.match_id);
    if ('refused' in grant) return this.error(grant);
    // Point e: only to an accepted message of that match, and only forward.
    const target = this.submissions.get(captured.submission_id);
    if (!target || target.matchId !== grant.matchId || target.state !== 'accepted') return this.error({ refused: 'not_found' });
    const key = this.cursorKey(grant.matchId, grant.actor);
    if (target.accepted! > (this.readCursors.get(key) ?? 0)) this.readCursors.set(key, target.accepted!);
    return this.success(this.summary(grant));
  }

  // -- labeled fixture controls (development composition only) --------------------------

  get scenario() { return this.scenarioValue; }
  get delivery() { return this.deliveryValue; }
  get providerField() { return this.providerFieldValue; }
  get outage() { return this.outageValue; }
  get delayedCount() { return this.releases.length; }
  setScenario(scenario: ChatScenario) { this.scenarioValue = scenario; this.emit(); }
  setDelivery(delivery: OwnDelivery) { this.deliveryValue = delivery; this.emit(); }
  setProviderField(field: ProviderFieldCase | null) { this.providerFieldValue = field; this.emit(); }
  setOutage(outage: boolean) { this.outageValue = outage; this.emit(); }
  releaseDelayed() { const releases = this.releases; this.releases = []; releases.forEach(release => release()); this.emit(); }
  /**
   * A fictional participant's own requests, answered by the same checks as the viewer's,
   * so a test can show each member the fixture composes. Bodies are returned unplanted.
   */
  developmentMember(profile: string) {
    const member: Member = Object.freeze({ kind: 'fixture', profile });
    return Object.freeze({
      conversations: () => this.list(member),
      messages: (request: MessagePageRequest) => this.page(member, this.capture(request)),
      send: (intent: MessageIntent, delivery: OwnDelivery = 'accept') => this.submit(member, this.capture(intent), delivery),
      readCursor: (intent: ReadCursorIntent) => this.moveCursor(member, this.capture(intent)),
    });
  }
  /** The other participant sends through the same checks; `hold` keeps it pending until delivered. */
  developmentOtherSend(profile: string, matchId: string, text: string, delivery: OwnDelivery = 'accept'): boolean {
    const grant = this.grant({ kind: 'fixture', profile }, matchId);
    if ('refused' in grant) return false;
    const body = this.submit({ kind: 'fixture', profile }, { operation: 'message', match_id: matchId, text,
      meta: { expected_version: grant.contactVersion, idempotency_key: `fixture-other:${++this.fixtureKeys}` } }, delivery) as { data?: unknown };
    this.emit(); return 'data' in body;
  }
  /** Delivers every held submission now, so each is accepted after any message accepted meanwhile (DM-22 2.2). */
  developmentDeliverHeld(): number {
    const held = [...this.submissions.values()].filter(row => row.held && row.state === 'pending').sort((a, b) => a.submitted - b.submitted);
    held.forEach(row => this.accept(row)); this.emit(); return held.length;
  }
  /** Seeds alternating fictional history through the same checks. */
  developmentSeed(profile: string, matchId: string, count: number): boolean {
    const viewer = this.grant({ kind: 'viewer' }, matchId);
    if ('refused' in viewer) return false;
    for (let index = 1; index <= count; index++) {
      const member: Member = index % 2 ? { kind: 'fixture', profile } : { kind: 'viewer' };
      this.submit(member, { operation: 'message', match_id: matchId, text: `Fictional history message ${index}.`,
        meta: { expected_version: viewer.contactVersion, idempotency_key: `fixture-seed:${++this.fixtureKeys}` } }, 'accept');
    }
    this.emit(); return true;
  }
  /** The provider's copy of the latest accepted message changes by one character; Glow's digest check refuses it. */
  developmentAlterLatest(matchId: string): boolean {
    const row = this.accepted(matchId).at(-1);
    if (!row?.providerText) return false;
    const last = row.providerText.at(-1);
    row.providerText = row.providerText.slice(0, -1) + (last === 'x' ? 'y' : 'x'); this.emit(); return true;
  }
  /** A message the provider holds that Glow never sent; no page is built from it. */
  developmentPlantProviderMessage(text: string) { this.providerOnly.push(text); this.emit(); }
  /** The other participant blocks the viewer through the interactions fixture's own command service. */
  developmentOtherBlock(profile: string): boolean {
    const target = this.profiles.getSnapshot().profile?.profile_id;
    if (!target) return false;
    try {
      const session = this.interactions.developmentSession(profile);
      const intent: BlockIntent = { operation: 'block', target_profile_id: target, action: 'block',
        meta: { expected_version: 0, idempotency_key: `fixture-other-block:${++this.fixtureKeys}` } };
      this.interactions.execute(session, intent); return true;
    } catch { return false; }
  }
  /** Requests that reached the transport, newest last. */
  requests(): readonly ChatRequestRecord[] { return this.requestLog; }
  inspect() {
    return Object.freeze({
      submissions: [...this.submissions.values()].map(row => Object.freeze({ id: row.id, matchId: row.matchId, author: row.author,
        state: row.state, version: row.version, text: row.text })),
      readCursors: Object.freeze(Object.fromEntries(this.readCursors)),
      providerOnly: this.providerOnly.length,
    });
  }
}

/** Adds one provider field to a response body, as a misbehaving server or provider passthrough would. */
export function plantProviderField(body: object, field: ProviderFieldCase, requestId: string): unknown {
  if (field === 'provider_error_text') {
    return { contract_version: CONTRACT_VERSION, request_id: requestId, code: 'provider_unavailable', retryable: true,
      message: `${PROVIDER_SENTINEL}: the provider's own error text` };
  }
  const copy = clone(body) as Record<string, unknown>;
  const data = (copy.data && typeof copy.data === 'object' ? copy.data : copy) as Record<string, unknown>;
  const nested = [data.messages, data.conversations].find(value => Array.isArray(value) && value.length > 0) as Record<string, unknown>[] | undefined;
  const item = nested?.[0] ?? data;
  switch (field) {
    case 'member_object': data.member = { user_id: `${PROVIDER_SENTINEL}-user`, role: 'channel_member', custom: { note: PROVIDER_SENTINEL } }; break;
    case 'user_object': item.user = { id: `${PROVIDER_SENTINEL}-user`, name: `${PROVIDER_SENTINEL} name`, image: `https://${PROVIDER_SENTINEL}.invalid/user.png` }; break;
    case 'custom_data': item.custom = { note: PROVIDER_SENTINEL }; break;
    case 'member_updated': data.type = 'member.updated'; data.member = { custom: { note: PROVIDER_SENTINEL } }; break;
    case 'ai_indicator_update': data.type = 'ai_indicator.update'; data.ai_state = `${PROVIDER_SENTINEL}_THINKING`; break;
    case 'ai_indicator_clear': data.type = 'ai_indicator.clear'; data.cid = `messaging:${PROVIDER_SENTINEL}`; break;
    case 'ai_indicator_stop': data.type = 'ai_indicator.stop'; data.cid = `messaging:${PROVIDER_SENTINEL}`; break;
    case 'channel_name': data.name = `${PROVIDER_SENTINEL} channel name`; break;
    case 'channel_image': data.image = `https://${PROVIDER_SENTINEL}.invalid/channel.png`; break;
    case 'channel_object': data.channel = { id: `${PROVIDER_SENTINEL}-channel`, name: `${PROVIDER_SENTINEL} channel`, image: `https://${PROVIDER_SENTINEL}.invalid/c.png` }; break;
    case 'provider_message_id': item.id = `${PROVIDER_SENTINEL}-message`; break;
    case 'provider_channel_id': data.cid = `messaging:${PROVIDER_SENTINEL}`; data.channel_ref = `${PROVIDER_SENTINEL}-channel`; break;
    case 'provider_user_id': item.user_id = `${PROVIDER_SENTINEL}-user`; break;
    case 'provider_timestamp': item.created_at = '2026-09-23T12:00:00.000Z'; item.updated_at = `${PROVIDER_SENTINEL}`; break;
  }
  return copy;
}
