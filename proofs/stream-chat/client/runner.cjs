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
 * path, query parameters without credentials, body, status, response body).
 * Headers are never recorded, so the token never leaves this process through
 * the protocol. Nothing is logged to stdout except replies.
 */

const path = require('node:path');
const readline = require('node:readline');
const { errorInfo } = require('./error-info.cjs');

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
let totalCalls = 0;
let commandCalls = 0;
let commandMax = 10;
let records = [];
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
  return url.startsWith(BASE) ? url.slice(BASE.length) : url;
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

client.axiosInstance.interceptors.request.use((config) => {
  if (commandCalls >= commandMax || totalCalls >= PROCESS_MAX_CALLS) {
    const err = new Error('PROOF_BUDGET: request refused before sending (budget reached)');
    err.proofBudget = true;
    throw err;
  }
  commandCalls += 1;
  totalCalls += 1;
  const record = {
    method: String(config.method || 'get').toUpperCase(),
    path: relPath(config.url),
    params: stripParams(config.params),
    body: bodyOf(config.data),
    status: null,
    response: null,
  };
  records.push(record);
  config.__proofRecord = record;
  return config;
});
client.axiosInstance.interceptors.response.use(
  (response) => {
    const record = response.config && response.config.__proofRecord;
    if (record) {
      record.status = response.status;
      record.response = response.data;
    }
    return response;
  },
  (error) => {
    const record = error && error.config && error.config.__proofRecord;
    if (record && error.response) {
      record.status = error.response.status;
      record.response = error.response.data;
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
        target = cmd.channel_data
          ? client.channel(cmd.type, cmd.id, cmd.channel_data)
          : client.channel(cmd.type, cmd.id);
      } else throw new Error(`unknown target ${cmd.target}`);
      const fn = target[cmd.method];
      if (typeof fn !== 'function') throw new Error(`no SDK method ${cmd.target}.${cmd.method}`);
      await fn.apply(target, argsFor(cmd.args));
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
// invalidated at disconnect). Record them instead of letting Node exit.
const asyncErrors = [];
process.on('unhandledRejection', (reason) => {
  const text = reason && reason.message ? String(reason.message) : String(reason);
  asyncErrors.push(`unhandledRejection: ${text}`.slice(0, 300));
});
process.on('uncaughtException', (err) => {
  const text = err && err.message ? String(err.message) : String(err);
  asyncErrors.push(`uncaughtException: ${text}`.slice(0, 300));
});

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
      process.stdout.write(JSON.stringify({ id: cmd.id, ok: true, api_calls_total: totalCalls, ws_attempts: wsAttempts }) + '\n');
      process.exit(0);
    }
    commandCalls = 0;
    commandMax = Number.isInteger(cmd.max_calls) ? cmd.max_calls : 10;
    records = [];
    const wsBefore = wsAttempts;
    let reply;
    try {
      const data = await handle(cmd);
      reply = { id: cmd.id, ok: true, data, error: null };
    } catch (err) {
      reply = { id: cmd.id, ok: false, data: null, error: errorInfo(err) };
    }
    reply.requests = records;
    reply.api_calls = commandCalls;
    reply.api_calls_total = totalCalls;
    reply.ws_attempts = wsAttempts - wsBefore;
    reply.async_errors = asyncErrors.splice(0, asyncErrors.length);
    process.stdout.write(JSON.stringify(reply) + '\n');
  });
});
rl.on('close', () => {
  chain.then(() => process.exit(0));
});
