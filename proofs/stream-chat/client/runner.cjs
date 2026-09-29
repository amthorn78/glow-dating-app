'use strict';
/*
 * P06.1 client session runner.
 *
 * One process per client session. The Python harness starts it with a minimal
 * environment: PATH, HOME, the proxy and CA variables, PROOF_API_KEY and, for
 * a user session, PROOF_USER_TOKEN. It never receives the API secret and
 * refuses to start if STREAM_API_SECRET is present.
 *
 * Protocol: one JSON command per stdin line, one JSON reply per stdout line.
 * Every HTTP request the Stream client sends is counted and recorded (method,
 * path, query parameters without credentials, body, status, response body),
 * including a request the SDK sends between commands, which the next reply
 * reports (client/request-log.cjs; P06.1-I2a). Headers are never recorded, except
 * a rate limit's own x-ratelimit-* headers on a 429, so the token never leaves
 * this process through the protocol. Nothing is logged to stdout except replies.
 */

const path = require('node:path');
const readline = require('node:readline');
const { errorInfo } = require('./error-info.cjs');
const { RequestLog, rateLimitOf } = require('./request-log.cjs');
const { productRefusal, normalizedPath, isProductPath } = require('./product-op.cjs');

if (process.env.STREAM_API_SECRET !== undefined) {
  process.stderr.write('refused: STREAM_API_SECRET is present in the client environment\n');
  process.exit(3);
}
const API_KEY = process.env.PROOF_API_KEY;
if (!API_KEY) {
  process.stderr.write('refused: PROOF_API_KEY is missing\n');
  process.exit(3);
}
const USER_TOKEN = process.env.PROOF_USER_TOKEN || null;
const PROCESS_MAX_CALLS = Number(process.env.PROOF_MAX_API_CALLS || '200');
const PROXY = process.env.HTTPS_PROXY || process.env.https_proxy || null;

const WS = require('ws');
const HttpsProxyAgent = require('https-proxy-agent');

// Route the SDK's WebSocket through the session proxy. stream-chat constructs
// `new (require('isomorphic-ws'))(url)` without options, so a subclass that
// adds the proxy agent is placed in the module cache before stream-chat loads.
let wsAttempts = 0;
class ProxiedWebSocket extends WS {
  constructor(url, protocols, options) {
    wsAttempts += 1;
    const opts = Object.assign({}, options || {});
    if (PROXY) opts.agent = new HttpsProxyAgent(PROXY);
    super(url, protocols, opts);
  }
}
const isoPath = require.resolve('isomorphic-ws');
require.cache[isoPath] = {
  id: isoPath,
  filename: isoPath,
  loaded: true,
  exports: ProxiedWebSocket,
  children: [],
  paths: [],
};

const { StreamChat } = require('stream-chat');

// The proxy subclass only takes effect if stream-chat resolves the same
// isomorphic-ws module and did not replace the cache entry while loading.
const isoFromStreamChat = require.resolve('isomorphic-ws', {
  paths: [path.dirname(require.resolve('stream-chat'))],
});
const ISO_WS_SHARED = isoFromStreamChat === isoPath;
const ISO_WS_PATCHED = !!require.cache[isoPath] && require.cache[isoPath].exports === ProxiedWebSocket;
if (!ISO_WS_SHARED || !ISO_WS_PATCHED) {
  process.stderr.write('refused: stream-chat does not load the runner\'s isomorphic-ws WebSocket\n');
  process.exit(4);
}

const client = new StreamChat(API_KEY, {
  timeout: 15000,
  allowServerSideConnect: true,
  recoverStateOnReconnect: false,
  proxy: false,
  httpsAgent: PROXY ? new HttpsProxyAgent(PROXY) : undefined,
});

const BASE = client.baseURL;
// The hosts a product request may go to (P06.1-I2b). Stream's server SDK sends every
// product's requests to the chat host; Stream's Video documentation names the video
// host. The op's default is the chat host; a case may name another.
const PRODUCT_HOSTS = {
  chat: BASE,
  video: 'https://video.stream-io-api.com',
  feeds: 'https://feeds.stream-io-api.com',
};
let totalCalls = 0;
let commandCalls = 0;
let commandMax = 10;
const log = new RequestLog();
const events = [];

function stripParams(params) {
  const out = {};
  for (const [k, v] of Object.entries(params || {})) {
    if (k === 'authorization' || k === 'token') continue;
    out[k] = v;
  }
  return out;
}

function relPath(url) {
  if (!url) return url;
  for (const host of Object.values(PRODUCT_HOSTS)) {
    if (url.startsWith(host)) return url.slice(host.length);
  }
  return url;
}

function bodyOf(data) {
  if (data === undefined || data === null) return null;
  if (typeof data === 'string') {
    try {
      return JSON.parse(data);
    } catch (_e) {
      return { unparsed_body_chars: data.length };
    }
  }
  if (typeof data === 'object' && typeof data.getBoundary === 'function') return '[multipart form]';
  return data;
}

// Where a Video or Feeds request can go (P06.1-C4; the I2b review's finding 1): the two
// products' hosts, and the product path prefixes (client/product-op.cjs) on any host. The
// runner sends nothing to any host but these three.
const PRODUCT_HOSTNAMES = [PRODUCT_HOSTS.video, PRODUCT_HOSTS.feeds].map((h) => new URL(h).hostname);
const STREAM_HOSTNAMES = Object.values(PRODUCT_HOSTS).map((h) => new URL(h).hostname);
const UNRESOLVED_HOST = 'unresolved.invalid';
const FORWARDING_HEADERS = ['x-forwarded-host', 'forwarded', 'x-original-host', 'x-host'];
// Headers that ask a server or its edge to take the request as another method or path
// (P06.1-C5; the manager's addition to the C4 review's finding 1). Neither stream-chat
// 9.53.0 nor axios 1.20.0 sends any of them.
const REWRITING_HEADERS = [
  'x-http-method-override',
  'x-http-method',
  'x-method-override',
  'x-original-url',
  'x-rewrite-url',
];

// The URL axios will send: its buildFullPath (the base URL joined to a relative URL, or to
// any URL when allowAbsoluteUrls is false), then its Node adapter's new URL(). A relative
// URL with no base URL cannot be sent; it is resolved against a placeholder host so that
// its path is still checked.
function sentURL(config) {
  const url = typeof config.url === 'string' ? config.url : String(config.url ?? '');
  const base = typeof config.baseURL === 'string' ? config.baseURL : '';
  let full = url;
  if (base && (!/^([a-z][a-z\d+\-.]*:)?\/\//i.test(url) || config.allowAbsoluteUrls === false)) {
    full = url ? base.replace(/\/+$/, '') + '/' + url.replace(/^\/+/, '') : base;
  }
  try {
    return new URL(full);
  } catch (_e) {
    try {
      return new URL(full, `https://${UNRESOLVED_HOST}`);
    } catch (_e2) {
      return null;
    }
  }
}

// Whether the check can read a body's fields: none, a JSON object or array, or a string
// that parses as JSON. A form, a buffer, a stream or any other string (axios would send
// it form-encoded) could carry a denied field the check cannot see.
function readableBody(data) {
  if (data === undefined || data === null) return true;
  if (typeof data === 'string') {
    try {
      JSON.parse(data);
      return true;
    } catch (_e) {
      return false;
    }
  }
  if (typeof data !== 'object') return false;
  if (Buffer.isBuffer(data) || ArrayBuffer.isView(data) || data instanceof ArrayBuffer) return false;
  if (typeof data.getBoundary === 'function' || typeof data.pipe === 'function') return false;
  if (typeof URLSearchParams !== 'undefined' && data instanceof URLSearchParams) return false;
  if (typeof FormData !== 'undefined' && data instanceof FormData) return false;
  return Array.isArray(data) || Object.getPrototypeOf(data) === Object.prototype;
}

// Why a request, whatever op made it, may not be sent, or null (P06.1-C4; the I2b review's
// finding 1, and C4's own review). Only Stream's three hosts, and no Host, forwarding or
// request-rewriting header (P06.1-C5), each name read as it is sent (sentHeaderName). A request
// to either product's host, or to a path under /api/v2/video, /api/v2/feeds, /video or
// /feeds once letter case, percent-encoding and dot segments are normalized
// (normalizedPath), must pass the product op's own check (client/product-op.cjs) on the
// method, the path as sent, the body and the query (JSON inside a query value included). A
// path whose encoding does not settle, a product path whose form as sent is not its
// normalized form, and a product body the check cannot read are refused outright. Letter
// case is folded to find a product path but kept in the comparison: an ID may hold
// capitals, and the allowlist's fixed segments are lower case, so a miscased fixed segment
// is refused by the op's check.
function productRequestRefusal(config) {
  const parsed = sentURL(config);
  if (!parsed) return 'a URL that cannot be read';
  // HTTPS only: a plain http URL would send the user token in clear text (C4's own review).
  if (parsed.protocol !== 'https:') return 'a protocol other than https';
  const host = parsed.hostname.toLowerCase().replace(/\.$/, '');
  // Only Stream's hosts (C4's own review): a request anywhere else is not the proof's.
  if (!STREAM_HOSTNAMES.includes(host) && host !== UNRESOLVED_HOST) {
    return 'a host other than Stream\'s chat, Video or Feeds host';
  }
  // A caller-supplied Host header would send the request to another virtual host than the
  // URL names (C4's own review).
  const names = headerNames(config.headers);
  if (names.includes('host')) return 'a Host header';
  // Nor a forwarding header naming another host (C4's own review).
  if (FORWARDING_HEADERS.some((h) => names.includes(h))) return 'a forwarding header';
  // Nor a header asking for another method or path (P06.1-C5): matrix.validate sees only the
  // matrix's steps, and the harness's own code sends call ops too, so the runner refuses
  // these for every request, whatever op sent it.
  if (REWRITING_HEADERS.some((h) => names.includes(h))) return 'a request-rewriting header';
  const sent = parsed.pathname;
  const normalized = normalizedPath(sent);
  if (normalized === null) return 'a path whose percent-encoding does not settle';
  const onProductHost = PRODUCT_HOSTNAMES.includes(host);
  if (!onProductHost && !isProductPath(normalized)) return null;
  if (sent !== normalized) return 'a Video or Feeds path not in its normalized form';
  if (!readableBody(config.data)) return 'a Video or Feeds body the check cannot read';
  const query = {};
  for (const [k, v] of parsed.searchParams.entries()) query[k] = v;
  const params = config.params || {};
  // A query value that holds JSON (Stream's GET queries carry a JSON payload) is read too.
  const nested = [];
  for (const v of [...Object.values(query), ...Object.values(params)]) {
    if (typeof v !== 'string') continue;
    try {
      nested.push(JSON.parse(v));
    } catch (_e) {
      // not JSON
    }
  }
  return productRefusal(config.method, sent, bodyOf(config.data), [query, params, nested]);
}

// A header name as it is sent, for comparison: axios's http adapter trims every name before
// sending (AxiosHeaders' normalize), and a server reads names in any letter case (P06.1-C5:
// until then " Host" passed the check and was sent as "Host"). Some servers also read an
// underscore in a name as a hyphen, so "X_HTTP_Method_Override" is compared as
// "x-http-method-override" (C5's own review). No name stream-chat or axios sets holds one.
function sentHeaderName(name) {
  const sent = String(name).trim().toLowerCase();
  return sent.replace(/_/g, '-');
}

// The header names a request config carries, as sent (axios's AxiosHeaders or an object,
// with its per-method sections).
function headerNames(headers) {
  if (!headers || typeof headers !== 'object') return [];
  const plain = typeof headers.toJSON === 'function' ? headers.toJSON() : headers;
  const names = [];
  for (const [key, value] of Object.entries(plain)) {
    names.push(sentHeaderName(key));
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      for (const inner of Object.keys(value)) names.push(sentHeaderName(inner));
    }
  }
  return names;
}

client.axiosInstance.interceptors.request.use((config) => {
  // Before the request is counted or sent (P06.1-C4; the I2b review's finding 1). No
  // redirect is followed: a redirected request would pass neither the check nor the budget
  // (C4's own review).
  config.maxRedirects = 0;
  const refused = productRequestRefusal(config);
  if (refused) {
    const err = new Error(`PROOF_REFUSED: ${refused}`);
    err.proofRefused = true;
    throw err;
  }
  // A command's own cap applies only while a command is in flight; the process
  // cap always does (P06.1-I2a).
  if ((log.inCommand && commandCalls >= commandMax) || totalCalls >= PROCESS_MAX_CALLS) {
    const err = new Error('PROOF_BUDGET: request refused before sending (budget reached)');
    err.proofBudget = true;
    throw err;
  }
  if (log.inCommand) commandCalls += 1;
  totalCalls += 1;
  const record = log.start({
    method: String(config.method || 'get').toUpperCase(),
    path: relPath(config.url),
    params: stripParams(config.params),
    body: bodyOf(config.data),
    status: null,
    response: null,
  });
  config.__proofRecord = record;
  return config;
});
client.axiosInstance.interceptors.response.use(
  (response) => {
    const record = response.config && response.config.__proofRecord;
    if (record) {
      log.finish(record, response.status, response.data, rateLimitOf(response.status, response.headers));
    }
    return response;
  },
  (error) => {
    const record = error && error.config && error.config.__proofRecord;
    if (record) {
      const answer = error.response;
      if (answer) {
        log.finish(record, answer.status, answer.data, rateLimitOf(answer.status, answer.headers));
      } else {
        log.finish(record);
      }
    }
    return Promise.reject(error);
  },
);

client.on((event) => {
  if (event.type === 'health.check') return;
  events.push(JSON.parse(JSON.stringify(event)));
});


function meSummary(me) {
  if (!me) return null;
  return {
    id: me.id,
    role: me.role,
    name: me.name ?? null,
    image: me.image ?? null,
    custom_keys: Object.keys(me).filter(
      (k) =>
        ![
          'id', 'role', 'name', 'created_at', 'updated_at', 'last_active', 'online', 'banned',
          'devices', 'mutes', 'channel_mutes', 'unread_count', 'total_unread_count',
          'unread_channels', 'unread_threads', 'invisible', 'teams', 'language',
          'blocked_user_ids', 'shadow_banned', 'privacy_settings', 'push_preferences',
          'channel_unread_count', 'unread_count_by_team', 'teams_role', 'avg_response_time',
          'total_unread_count_by_team', 'image',
        ].includes(k),
    ),
  };
}

function tokenFor(source, userId) {
  if (source === 'dev') return client.devToken(userId);
  if (source === 'env') {
    if (!USER_TOKEN) throw new Error('no PROOF_USER_TOKEN in this session');
    return USER_TOKEN;
  }
  throw new Error(`unknown token source ${source}`);
}

function skipTokenValidation() {
  // A modified app can skip the SDK's local check that the token's user_id
  // matches the user object; Stream must enforce it server-side.
  client.tokenManager.validateToken = () => {};
}

async function setRestUser(userId, source, skipValidation) {
  if (skipValidation) skipTokenValidation();
  const token = tokenFor(source, userId);
  client.userID = userId;
  client.anonymous = false;
  await client.tokenManager.setTokenOrProvider(token, { id: userId });
  client._setUser({ id: userId });
}

function argsFor(list) {
  return (list || []).map((a) => {
    if (a && typeof a === 'object' && a.__buffer_b64 !== undefined) {
      return Buffer.from(a.__buffer_b64, 'base64');
    }
    return a;
  });
}

async function handle(cmd) {
  switch (cmd.op) {
    case 'ping':
      return { pong: true };
    case 'selfcheck':
      return {
        isomorphic_ws_shared: ISO_WS_SHARED,
        proxied_websocket_installed: ISO_WS_PATCHED,
      };
    case 'set_rest_user':
      await setRestUser(cmd.user_id, cmd.token_source || 'env', !!cmd.skip_validation);
      return { user_id: cmd.user_id };
    case 'connect': {
      if (cmd.skip_validation) skipTokenValidation();
      const token = tokenFor(cmd.token_source || 'env', cmd.user.id);
      const res = await client.connectUser(cmd.user, token);
      return {
        me: meSummary(res && res.me),
        connection_id_present: !!(res && res.connection_id),
        ws_connected: !!(client.wsConnection && client.wsConnection.isHealthy),
      };
    }
    case 'guest': {
      const res = await client.setGuestUser(cmd.user);
      return { me: meSummary(res && res.me), connection_id_present: !!(res && res.connection_id) };
    }
    case 'anonymous': {
      const res = await client.connectAnonymousUser();
      return { me: meSummary(res && res.me), connection_id_present: !!(res && res.connection_id) };
    }
    case 'disconnect':
      await client.disconnectUser();
      return { disconnected: true };
    case 'call': {
      let target;
      if (cmd.target === 'client') target = client;
      else if (cmd.target === 'channel') {
        // The channel's ID is channel_id; cmd.id is the command's own ID (P06.1-I2a).
        target = cmd.channel_data
          ? client.channel(cmd.type, cmd.channel_id, cmd.channel_data)
          : client.channel(cmd.type, cmd.channel_id);
      } else throw new Error(`unknown target ${cmd.target}`);
      const fn = target[cmd.method];
      if (typeof fn !== 'function') throw new Error(`no SDK method ${cmd.target}.${cmd.method}`);
      await fn.apply(target, argsFor(cmd.args));
      return {};
    }
    case 'get': {
      // A GET relative to the client's base URL, as a modified client can send one
      // (P06.1-I2a: the existence oracle's Get Channel). GET only.
      await client.get(BASE + cmd.path, cmd.params || {});
      return {};
    }
    case 'product': {
      // A Video or Feeds request as a modified client can send one, with this
      // session's own token (P06.1-I2b): only a method and path on the allowlist, and
      // nothing on the deny-list (client/product-op.cjs); refused before it is sent.
      const why = productRefusal(cmd.method, cmd.path, cmd.body, cmd.params);
      if (why) {
        const err = new Error(`PROOF_REFUSED: ${why}`);
        err.proofRefused = true;
        throw err;
      }
      const host = PRODUCT_HOSTS[cmd.host || 'chat'];
      if (!host) throw new Error(`unknown product host ${cmd.host}`);
      const url = host + cmd.path;
      const method = String(cmd.method).toUpperCase();
      if (method === 'GET') await client.get(url, cmd.params || {});
      else if (method === 'POST') await client.post(url, cmd.body || {});
      else if (method === 'PUT') await client.put(url, cmd.body || {});
      else if (method === 'PATCH') await client.patch(url, cmd.body || {});
      else throw new Error(`unknown product method ${method}`);
      return {};
    }
    case 'events': {
      await new Promise((r) => setTimeout(r, cmd.wait_ms || 0));
      const out = events.splice(0, events.length);
      return { events: out };
    }
    default:
      throw new Error(`unknown op ${cmd.op}`);
  }
}

// The SDK can reject promises it does not await (for example on channels it
// invalidated at disconnect). Record them instead of letting Node exit, with
// Stream's status and code when the error carries them, so that the harness checks
// them for a charge or limit signal like any other answer (P06.1-I2a).
const asyncErrors = [];
function asyncError(origin, reason) {
  const info = errorInfo(reason);
  const text = reason && reason.message ? String(reason.message) : String(reason);
  asyncErrors.push({
    text: `${origin}: ${text}`.slice(0, 300),
    kind: info.kind,
    status: typeof info.status === 'number' ? info.status : null,
    code: typeof info.code === 'number' ? info.code : null,
    message: info.message === null || info.message === undefined ? null : String(info.message).slice(0, 300),
  });
}
process.on('unhandledRejection', (reason) => asyncError('unhandledRejection', reason));
process.on('uncaughtException', (err) => asyncError('uncaughtException', err));

const rl = readline.createInterface({ input: process.stdin });
let chain = Promise.resolve();
rl.on('line', (line) => {
  chain = chain.then(async () => {
    let cmd;
    try {
      cmd = JSON.parse(line);
    } catch (_e) {
      process.stdout.write(JSON.stringify({ id: null, ok: false, error: { kind: 'protocol' } }) + '\n');
      return;
    }
    if (cmd.op === 'exit') {
      try {
        if (client.userID) await client.disconnectUser();
      } catch (_e) {
        // ignore
      }
      // Everything still kept, answered or not, and every asynchronous error, so
      // that closing the session checks them too (P06.1-I2a).
      const exitReply = {
        id: cmd.id,
        ok: true,
        api_calls_total: totalCalls,
        ws_attempts: wsAttempts,
        ...log.takeKept(true),
        async_errors: asyncErrors.splice(0, asyncErrors.length),
      };
      process.stdout.write(JSON.stringify(exitReply) + '\n');
      process.exit(0);
    }
    commandCalls = 0;
    commandMax = Number.isInteger(cmd.max_calls) ? cmd.max_calls : 10;
    log.beginCommand();
    const wsBefore = wsAttempts;
    let reply;
    try {
      const data = await handle(cmd);
      reply = { id: cmd.id, ok: true, data, error: null };
    } catch (err) {
      reply = { id: cmd.id, ok: false, data: null, error: errorInfo(err) };
    }
    reply.requests = log.endCommand();
    reply.api_calls = commandCalls;
    reply.api_calls_total = totalCalls;
    reply.ws_attempts = wsAttempts - wsBefore;
    Object.assign(reply, log.takeKept(false));
    reply.async_errors = asyncErrors.splice(0, asyncErrors.length);
    process.stdout.write(JSON.stringify(reply) + '\n');
  });
});
rl.on('close', () => {
  chain.then(() => process.exit(0));
});
