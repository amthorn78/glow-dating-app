'use strict';
/*
 * The runner's Video and Feeds op (P06.1-I2b, step 2; DM-05 finding 3): what a modified
 * client can send to the two products with its own user token, and nothing else.
 *
 * The allowlist and the deny-list are in code, here, and the Python guard carries the
 * same tables (glow_stream_proof/products.py); tests/test_products.py drives this file
 * with node and checks that the two agree on every path of a table. The README lists
 * the endpoints; this file enforces them.
 *
 * Refused before anything is sent:
 *   - a path holding join, go_live, start_, stop_, broadcast, recording, transcription,
 *     caption, ring, notify, rtmp, hls or egress (a media session, a push, a recording
 *     or a broadcast: each could reach a device or incur a charge);
 *   - a body or query carrying ring or notify (any value), video: true, or
 *     create_notification_activity: true;
 *   - any method and path outside the allowlist below (no delete, no configuration).
 */

const SEG = '[^/]+';
const ALLOWED = [
  [new RegExp(`^/api/v2/video/call/${SEG}/${SEG}$`), ['GET', 'POST', 'PATCH']],
  [new RegExp(`^/api/v2/video/call/${SEG}/${SEG}/members$`), ['POST']],
  [new RegExp(`^/api/v2/video/call/${SEG}/${SEG}/event$`), ['POST']],
  [/^\/api\/v2\/video\/call\/members$/, ['POST']],
  [/^\/api\/v2\/video\/calls$/, ['POST']],
  [new RegExp(`^/api/v2/feeds/feed_groups/${SEG}/feeds/${SEG}$`), ['POST', 'PUT']],
  [/^\/api\/v2\/feeds\/feeds\/query$/, ['POST']],
  [/^\/api\/v2\/feeds\/activities$/, ['POST']],
  [/^\/api\/v2\/feeds\/activities\/query$/, ['POST']],
  [new RegExp(`^/api/v2/feeds/activities/${SEG}$`), ['GET', 'PUT']],
  [new RegExp(`^/api/v2/feeds/activities/${SEG}/reactions$`), ['POST']],
  [/^\/api\/v2\/feeds\/comments$/, ['POST']],
  [/^\/api\/v2\/feeds\/comments\/query$/, ['POST']],
  [new RegExp(`^/api/v2/feeds/comments/${SEG}$`), ['GET']],
  [/^\/api\/v2\/feeds\/follows$/, ['POST']],
  [/^\/api\/v2\/feeds\/follows\/query$/, ['POST']],
];
const DENIED_PATH_WORDS = [
  'join', 'go_live', 'start_', 'stop_', 'broadcast', 'recording', 'transcription', 'caption',
  'ring', 'notify', 'rtmp', 'hls', 'egress',
];
const DENIED_KEYS = ['ring', 'notify'];
const DENIED_TRUE_KEYS = ['video', 'create_notification_activity'];

// The key of a denied field found anywhere in a body or query, or null.
function deniedField(value) {
  if (Array.isArray(value)) {
    for (const item of value) {
      const found = deniedField(item);
      if (found) return found;
    }
    return null;
  }
  if (value && typeof value === 'object') {
    for (const [key, item] of Object.entries(value)) {
      if (DENIED_KEYS.includes(key)) return key;
      if (DENIED_TRUE_KEYS.includes(key) && (item === true || item === 'true')) return `${key}: true`;
      const found = deniedField(item);
      if (found) return found;
    }
  }
  return null;
}

// Why the request is refused, or null when it may be sent.
function productRefusal(method, path, body, params) {
  const verb = String(method || '').toUpperCase();
  const text = String(path || '');
  const clean = text.split('?')[0];
  for (const segment of clean.toLowerCase().split('/')) {
    for (const word of DENIED_PATH_WORDS) {
      if (segment.includes(word)) return `denied path (${word})`;
    }
  }
  if (text.includes('?')) return 'query parameters belong in params, not in the path';
  const field = deniedField(body) || deniedField(params);
  if (field) return `denied field (${field})`;
  for (const [pattern, methods] of ALLOWED) {
    if (pattern.test(clean)) {
      if (methods.includes(verb)) return null;
      return `method ${verb} is not allowed on this path`;
    }
  }
  return 'path outside the Video and Feeds allowlist';
}

module.exports = { productRefusal, ALLOWED, DENIED_PATH_WORDS, DENIED_KEYS, DENIED_TRUE_KEYS };
