import assert from 'node:assert/strict';
import test from 'node:test';
import { fetchDevelopmentRecommendations, DEVELOPMENT_RECOMMENDATIONS_PATH } from './recommendations.ts';

const config = { mode: 'fixture' as const, apiOrigin: 'http://127.0.0.1:8000' };
const body = { mode: 'fixture', contract_version: 'gapp-dev-v1', items: [] };

test('reads exact smoke endpoint without credentials or a request body', async () => {
  const result = await fetchDevelopmentRecommendations(config, async (url, init) => {
    assert.equal(url, config.apiOrigin + DEVELOPMENT_RECOMMENDATIONS_PATH);
    assert.equal(init.method, 'GET'); assert.equal(init.credentials, 'omit'); assert.equal(init.body, undefined);
    assert.deepEqual(init.headers, { Accept: 'application/json' });
    return Response.json(body);
  });
  assert.deepEqual(result, body);
});

test('network and invalid responses do not silently fall back to bundled fixtures', async () => {
  for (const response of [new Response('private error body', { status: 503 }), new Response('<html>Login</html>'), Response.json({ ...body, secret: 'private' }), new Response('broken', { headers: { 'content-type': 'application/json' } })]) {
    await assert.rejects(fetchDevelopmentRecommendations(config, async () => response));
  }
  await assert.rejects(fetchDevelopmentRecommendations(config, async () => { throw new Error('offline'); }));
});

test('in-flight request is aborted after a bounded timeout', async () => {
  let aborted = false;
  await assert.rejects(fetchDevelopmentRecommendations(config, async (_url, init) => await new Promise<Response>((_resolve, reject) => {
    init.signal?.addEventListener('abort', () => { aborted = true; reject(new Error('aborted')); }, { once: true });
  }), { timeoutMs: 10 }), { name: 'AbortError', message: 'The development request was cancelled.' });
  assert.equal(aborted, true);
});

test('caller cancellation reaches the request without persisting a result', async () => {
  const controller = new AbortController();
  controller.abort();
  await assert.rejects(fetchDevelopmentRecommendations(config, async (_url, init) => {
    assert.equal(init.signal?.aborted, true);
    throw new Error('aborted');
  }, { signal: controller.signal }), { name: 'AbortError', message: 'The development request was cancelled.' });
});


test('exported client errors never retain response body or transport details', async () => {
  const marker = 'PRIVATE-BODY-MARKER-DO-NOT-EXPOSE';
  const fetchers = [
    async () => new Response(marker, { headers: { 'content-type': 'application/json' } }),
    async () => { throw new Error(`Failed to fetch https://private.example.test/${marker}`); },
    async () => new Response(marker, { status: 503 }),
  ];
  for (const fetcher of fetchers) {
    await assert.rejects(fetchDevelopmentRecommendations(config, fetcher), (error: unknown) => {
      assert.ok(error instanceof Error);
      assert.equal(error.cause, undefined);
      assert.doesNotMatch(`${String(error)} ${error.stack}`, new RegExp(marker));
      assert.doesNotMatch(`${String(error)} ${error.stack}`, /private\.example\.test/);
      assert.match(error.message, /^The development API (returned an unsupported response|is unavailable)\.$/);
      return true;
    });
  }
});
