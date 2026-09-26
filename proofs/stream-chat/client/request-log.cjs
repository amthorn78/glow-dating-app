'use strict';
/*
 * The runner's record of every HTTP request the Stream client sends (P06.1-I2a).
 * Kept separate so that it can be tested offline (tests/test_runner.py).
 *
 * A request sent while a command is in flight belongs to that command and is
 * reported in the command's reply ('requests'), as before. Two kinds of request
 * are kept and reported later, in the first reply after Stream answered them
 * ('background_requests'), so that the harness checks every answer for a charge
 * or limit signal:
 *   - a request the SDK sends outside any command, between commands
 *     (marked 'background' and counted apart: 'background_api_calls');
 *   - a command's request still unanswered when the command replied
 *     (marked 'late'; it was already counted with its command).
 * The exit reply reports every kept request, answered or not.
 */

class RequestLog {
  constructor() {
    this.inCommand = false;
    this.commandRecords = [];
    this.kept = [];
    this.backgroundCalls = 0;
  }

  beginCommand() {
    this.inCommand = true;
    this.commandRecords = [];
  }

  // A request is about to be sent; returns its record.
  start(record) {
    record.done = false;
    if (this.inCommand) {
      this.commandRecords.push(record);
    } else {
      record.background = true;
      this.backgroundCalls += 1;
      this.kept.push(record);
    }
    return record;
  }

  // Stream answered the request (status and body), or it failed without an answer.
  finish(record, status, response, rateLimit) {
    if (status !== undefined && status !== null) {
      record.status = status;
      record.response = response === undefined ? null : response;
    }
    if (rateLimit) record.ratelimit = rateLimit;
    record.done = true;
  }

  // The command replied: its requests, and the unanswered ones kept for later.
  endCommand() {
    this.inCommand = false;
    const requests = this.commandRecords;
    for (const record of requests) {
      if (!record.done) {
        record.late = true;
        this.kept.push(record);
      }
    }
    this.commandRecords = [];
    return requests;
  }

  // The kept requests Stream has answered (all of them when 'all'), and the count of
  // requests started outside a command since the last report.
  takeKept(all) {
    const out = this.kept.filter((r) => all || r.done);
    this.kept = this.kept.filter((r) => !(all || r.done));
    const calls = this.backgroundCalls;
    this.backgroundCalls = 0;
    return { background_requests: out, background_api_calls: calls };
  }
}

// Only a rate limit's own headers, never the request's.
function rateLimitOf(status, headers) {
  if (status !== 429 || !headers) return null;
  const read = (name) => (typeof headers.get === 'function' ? headers.get(name) : headers[name]);
  const pick = (name) => {
    const value = read(name);
    return value === undefined || value === null ? null : String(value);
  };
  return {
    limit: pick('x-ratelimit-limit'),
    remaining: pick('x-ratelimit-remaining'),
    reset: pick('x-ratelimit-reset'),
  };
}

module.exports = { RequestLog, rateLimitOf };
