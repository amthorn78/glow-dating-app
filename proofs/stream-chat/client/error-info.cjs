'use strict';
/*
 * How the runner reports a failed command. Kept separate so that it can be
 * tested offline (tests/test_runner.py).
 *
 * kind 'api': the SDK's error carries Stream's HTTP response.
 * kind 'ws-api': the SDK built the error from Stream's own error frame on the
 *   WebSocket (the SDK's JSON message has isWSFailure === false).
 * kind 'ws-failure': any other WebSocket failure; it carries no answer from Stream.
 * kind 'budget': the runner refused the request before sending it.
 * kind 'error': anything else, local to the SDK or the runner.
 */

function errorInfo(err) {
  const info = { status: null, code: null, message: null, kind: 'error' };
  if (err && err.proofBudget) {
    info.kind = 'budget';
    info.message = err.message;
    return info;
  }
  if (err && err.name === 'ErrorFromResponse') {
    info.kind = 'api';
    info.status = err.status ?? null;
    info.code = err.code ?? null;
    const data = err.response && err.response.data;
    info.message = data && typeof data.message === 'string' ? data.message : err.message;
    return info;
  }
  if (err && err.response && err.response.data) {
    info.kind = 'api';
    info.status = err.response.status ?? null;
    info.code = err.response.data.code ?? null;
    info.message = err.response.data.message ?? null;
    return info;
  }
  const text = err && err.message ? String(err.message) : String(err);
  try {
    const parsed = JSON.parse(text);
    if (parsed && typeof parsed === 'object') {
      // isWSFailure is false only when the SDK built the error from Stream's
      // own error frame on the WebSocket; anything else is local to the SDK.
      info.kind = parsed.isWSFailure === false ? 'ws-api' : 'ws-failure';
      info.status = parsed.StatusCode ?? null;
      info.code = parsed.code ?? null;
      info.message = parsed.message ?? text;
      return info;
    }
  } catch (_e) {
    // not JSON
  }
  info.message = text;
  return info;
}

module.exports = { errorInfo };
