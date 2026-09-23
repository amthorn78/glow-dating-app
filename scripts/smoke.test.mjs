import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const root = fileURLToPath(new URL('../', import.meta.url));

function smoke(environment = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, ['scripts/smoke.mjs'], {
      cwd: root, env: { ...process.env, ...environment }, stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    const timeout = setTimeout(() => {
      child.kill('SIGKILL');
      reject(new Error('Smoke regression timed out.'));
    }, 15000);
    child.stdout.on('data', value => { stdout += value; });
    child.stderr.on('data', value => { stderr += value; });
    child.once('error', error => { clearTimeout(timeout); reject(error); });
    child.once('exit', code => { clearTimeout(timeout); resolve({ code, stdout, stderr }); });
  });
}

test('smoke owns its port and cannot pass using an existing matching server', async () => {
  let requests = 0;
  const fixture = { mode: 'fixture', contract_version: 'gapp-dev-v1', items: [{
    profile_id: 'unrelated-server', display_name: 'Demo', age: 30, summary: 'Synthetic decoy.',
    compatibility: { status: 'pending', source: 'fixture' },
  }] };
  const server = createServer((request, response) => {
    requests++;
    response.setHeader('Content-Type', 'application/json');
    if (request.method === 'POST') { response.statusCode = 405; response.end('{}'); }
    else if (request.url === '/health/live') response.end(JSON.stringify({ status: 'alive' }));
    else if (request.url === '/health/ready') { response.statusCode = 503; response.end('{}'); }
    else response.end(JSON.stringify(fixture));
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(18765, '127.0.0.1', resolve);
  });
  try {
    const success = await smoke();
    assert.equal(success.code, 0, success.stderr);
    assert.match(success.stdout, /PASS: spawned loopback API/);
    assert.equal(requests, 0, 'the unrelated old-port server must receive no smoke traffic');

    const failure = await smoke({ GLOW_COMPATIBILITY_PROVIDER: 'unsupported' });
    assert.notEqual(failure.code, 0);
    assert.doesNotMatch(failure.stdout, /PASS:/);
    assert.match(failure.stderr, /startup did not produce a valid bound-port handshake/);
    assert.equal(requests, 0, 'failed startup must not fall back to an existing server');
  } finally {
    await new Promise(resolve => server.close(resolve));
  }
});
