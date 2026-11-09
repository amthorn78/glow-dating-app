import type { NotificationFailureCode } from './client.ts';

export type NotificationKind = 'match' | 'message';
export const KINDS: readonly NotificationKind[] = Object.freeze(['match', 'message']);

/**
 * Glow's own wording for the notification settings screen (P06.3, Outcome 3; ADR 0003, decision
 * 3). Keyed by Glow's codes, never by a response's text: no name, photo, message text, provider,
 * platform or push service appears here. Nathan may change any of it; a change is an edit here
 * and its copy test.
 */
/** The push wording Glow's server composes (D4; `glow_domain/notifications.py`, `WORDING`). */
export const PUSH_WORDING: Readonly<Record<NotificationKind, string>> = Object.freeze({
  match: 'You have a new match.',
  message: 'You have a new message.',
});
export const KIND_LABEL: Readonly<Record<NotificationKind, string>> = Object.freeze({
  match: 'New matches',
  message: 'New messages',
});
/** Before any request, what each kind sends: one fixed sentence per kind (Outcome 3; DM-44 4.2). */
export const KIND_SENDS: Readonly<Record<NotificationKind, string>> = Object.freeze({
  match: `When you have a new match, Glow sends “${PUSH_WORDING.match}” and nothing else.`,
  message: `When you have a new message, Glow sends “${PUSH_WORDING.message}” and nothing else.`,
});
export const TURN_ON: Readonly<Record<NotificationKind, string>> = Object.freeze({
  match: 'Turn on new match notifications',
  message: 'Turn on new message notifications',
});
export const TURN_OFF: Readonly<Record<NotificationKind, string>> = Object.freeze({
  match: 'Turn off new match notifications',
  message: 'Turn off new message notifications',
});
export const SCREEN_TITLE = 'Notifications, your choice.';
export const INTRO = 'Glow can tell you when something new happens. Both kinds start off, and Glow asks this device for permission only when you turn one on.';
export const STATUS_ON = 'On for this device';
export const STATUS_OFF = 'Off for this device';
export const LOADING = 'Loading your notification settings…';
/** A denied permission: notifications are off in the device's settings, and Glow works without them. */
export const DENIED = 'Notifications are off in this device’s settings. Glow works without them.';
export const FAILURE_COPY: Readonly<Record<NotificationFailureCode, string>> = Object.freeze({
  signed_out: 'Your session has ended. Sign in again to continue.',
  stale: 'Your notification settings changed. Review them and try again.',
  not_active: 'Notifications are not set up on this device yet. Turn a kind on to set them up.',
  conflict: 'This change conflicts with an earlier request. Try again.',
  temporary: 'Your notification settings could not be saved right now. Try again.',
  invalid_request: 'Your notification settings could not be saved. Try again.',
  invalid_response: 'Your notification settings could not be shown. Try again.',
  offline: 'The response was not received. Try again.',
  unavailable: 'Your notification settings are unavailable.',
});

/** Every sentence above, for the copy test. */
export const ALL_COPY: readonly string[] = Object.freeze([
  ...Object.values(PUSH_WORDING), ...Object.values(KIND_LABEL), ...Object.values(KIND_SENDS),
  ...Object.values(TURN_ON), ...Object.values(TURN_OFF), SCREEN_TITLE, INTRO, STATUS_ON, STATUS_OFF, LOADING, DENIED,
  ...Object.values(FAILURE_COPY),
]);
