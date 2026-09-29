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
 *     create_notification_activity: true, each key in any letter case and true as a
 *     boolean or as "true" in any letter case (P06.1-C4);
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

// A boolean true, or the string "true" in any letter case.
function isTrue(item) {
  return item === true || (typeof item === 'string' && item.toLowerCase() === 'true');
}

// The key of a denied field found anywhere in a body or query, in lower case, or null.
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
      // In any letter case (P06.1-C4; the I2b review's nit 3): Stream's JSON decoding may
      // match a field name without regard to case.
      const name = String(key).toLowerCase();
      if (DENIED_KEYS.includes(name)) return name;
      if (DENIED_TRUE_KEYS.includes(name) && isTrue(item)) return `${name}: true`;
      const found = deniedField(item);
      if (found) return found;
    }
  }
  return null;
}

// Where a Video or Feeds request can go on any Stream host (P06.1-C4): the REST prefixes
// and the Video and Feeds clients' own bare forms.
const PRODUCT_PREFIXES = ['/api/v2/video', '/api/v2/feeds', '/video', '/feeds'];
const DECODE_ROUNDS = 8;

// One round of percent-decoding, byte by byte (%XX becomes the character with that code), so
// that it never throws: an escape that is not valid UTF-8 (%ff, %c0) is decoded like any
// other, and one that is not hex (%zz) is left as it is (P06.1-C4; C4's own review found
// that decodeURIComponent threw on %ff and so left the whole path undecoded).
function decodeOnce(text) {
  return text.replace(/%([0-9A-Fa-f]{2})/g, (_m, hex) => String.fromCharCode(parseInt(hex, 16)));
}

// A path as a server may read it: percent-encoding decoded until it no longer changes,
// backslashes read as slashes, empty and dot segments resolved; letter case is kept. null
// when it still changes after DECODE_ROUNDS rounds: such a path is refused. The Python
// mirror is glow_stream_proof/products.normalized_path; a test compares the two.
function normalizedPath(pathname) {
  let text = String(pathname).split('?')[0].replace(/\\/g, '/');
  let settled = false;
  for (let i = 0; i < DECODE_ROUNDS; i += 1) {
    const next = decodeOnce(text).replace(/\\/g, '/');
    if (next === text) {
      settled = true;
      break;
    }
    text = next;
  }
  if (!settled) return null;
  const out = [];
  for (const segment of text.split('/')) {
    if (segment === '' || segment === '.') continue;
    if (segment === '..') out.pop();
    else out.push(segment);
  }
  return '/' + out.join('/');
}

// Whether a normalized path reaches Video or Feeds (letter case folded).
function isProductPath(normalized) {
  const folded = String(normalized).toLowerCase();
  return PRODUCT_PREFIXES.some((p) => folded === p || folded.startsWith(p + '/'));
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

module.exports = {
  productRefusal,
  normalizedPath,
  isProductPath,
  ALLOWED,
  DENIED_PATH_WORDS,
  DENIED_KEYS,
  DENIED_TRUE_KEYS,
  PRODUCT_PREFIXES,
};
