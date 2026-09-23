import assert from 'node:assert/strict';
import test from 'node:test';
import { getDevelopmentConfig } from './development.ts';

test('fixture runtime rejects release, missing mode and active-provider mode', () => {
  for (const input of [
    { isDevelopment: false, mode: 'fixture', apiOrigin: undefined },
    { isDevelopment: true, mode: undefined, apiOrigin: undefined },
    { isDevelopment: true, mode: 'live', apiOrigin: undefined },
  ]) assert.throws(() => getDevelopmentConfig(input));
});

test('development origin allows secure or private origins only and never credentials', () => {
  const config = (apiOrigin: string | undefined) => getDevelopmentConfig({ isDevelopment: true, mode: 'fixture', apiOrigin });
  assert.deepEqual(config(undefined), { mode: 'fixture' });
  for (const origin of ['http://127.0.0.1:8000', 'http://10.0.2.2:8000', 'http://192.168.1.12:8000', 'https://development.example.test']) {
    assert.equal(config(origin).apiOrigin, origin);
  }
  for (const origin of ['http://public.example.test', 'https://user:secret@example.test', 'https://example.test/path', 'https://example.test?token=secret', 'https://example.test/#part', 'file:///tmp/test', 'bad-url']) {
    assert.throws(() => config(origin));
  }
});
