/** Real loopback HTTP to the spawned Django process, consumed by the mobile client. */
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { setTimeout as delay } from 'node:timers/promises';
import { fetchDevelopmentRecommendations } from '../apps/mobile/src/data/recommendations.ts';
import { getDevelopmentConfig } from '../apps/mobile/src/config/development.ts';

const root = fileURLToPath(new URL('../', import.meta.url));
const python = process.env.GLOW_SMOKE_PYTHON ?? `${root}services/api/.venv/bin/python`;
const child = spawn(python, ['-m', 'glow_api.devserver', '--port', '0', '--ready-json'], {
  cwd: `${root}services/api`,
  env: { ...process.env, GLOW_ENV: 'development' },
  stdio: ['ignore', 'pipe', 'pipe'],
});
let childFailed = false;
child.on('error', () => { childFailed = true; });
// Never forward supplied environment values, response bodies or startup traces.
child.stderr.resume();
const exited = new Promise(resolve => child.once('exit', resolve));
function requireRunningChild() {
  if (childFailed || child.exitCode !== null || child.signalCode !== null) {
    throw new Error('The spawned fixture API is not running.');
  }
}

/** The child reports its own OS-assigned port only after it owns the socket. */
function boundOrigin() {
  return new Promise((resolve, reject) => {
    let buffer = '';
    const timeout = setTimeout(() => fail(), 10000);
    const cleanup = () => {
      clearTimeout(timeout);
      child.stdout.off('data', receive);
      child.off('error', fail);
      child.off('exit', fail);
    };
    const fail = () => {
      cleanup();
      reject(new Error('Fixture API startup did not produce a valid bound-port handshake.'));
    };
    const receive = chunk => {
      buffer += chunk.toString('utf8');
      if (buffer.length > 2048) return fail();
      if (!buffer.includes('\n')) return;
      try {
        const ready = JSON.parse(buffer.slice(0, buffer.indexOf('\n')));
        assert.equal(ready.event, 'glow_fixture_ready');
        assert.equal(ready.pid, child.pid);
        assert.equal(ready.host, '127.0.0.1');
        assert.ok(Number.isInteger(ready.port) && ready.port > 0 && ready.port <= 65535);
        requireRunningChild();
        cleanup();
        resolve(`http://127.0.0.1:${ready.port}`);
      } catch { fail(); }
    };
    child.stdout.on('data', receive);
    child.once('error', fail);
    child.once('exit', fail);
  });
}

try {
  const origin = await boundOrigin();
  const live = await fetch(`${origin}/health/live`, { signal: AbortSignal.timeout(2000) });
  assert.equal(live.status, 200, 'the spawned API must answer on its bound loopback port');
  assert.deepEqual(await live.json(), { status: 'alive' });
  const ready = await fetch(`${origin}/health/ready`, { signal: AbortSignal.timeout(2000) });
  assert.equal(ready.status, 503, 'fixture process must never report production readiness');
  assert.deepEqual(await ready.json(), {
    status: 'not_ready', mode: 'fixture', reason: 'live_integrations_not_configured',
  });
  const config = getDevelopmentConfig({ isDevelopment: true, mode: 'fixture', apiOrigin: origin });
  const first = await fetchDevelopmentRecommendations(config);
  const second = await fetchDevelopmentRecommendations(config);
  assert.deepEqual(first, second, 'fixture output must be deterministic');
  assert.ok(first.items.length > 0);
  for (const item of first.items) {
    assert.deepEqual(item.compatibility, { status: 'pending', source: 'fixture' });
  }
  const write = await fetch(`${origin}/api/v1/development/recommendations`, {
    method: 'POST', signal: AbortSignal.timeout(2000),
  });
  assert.equal(write.status, 405);
  requireRunningChild();
  console.log('PASS: spawned loopback API -> mobile TypeScript client; live 200, ready 503, deterministic pending fixtures, writes 405.');
} finally {
  child.kill('SIGTERM');
  await Promise.race([exited, delay(1000)]);
  if (child.exitCode === null && child.signalCode === null && !childFailed) child.kill('SIGKILL');
}
