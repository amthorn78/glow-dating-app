import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import test from 'node:test';

test('Expo config rejects production and release preview', () => {
  for (const env of [
    { GLOW_APP_ENV: 'production', EXPO_PUBLIC_GLOW_MODE: 'fixture' },
    { GLOW_APP_ENV: 'development', EXPO_PUBLIC_GLOW_MODE: 'live' },
    { GLOW_APP_ENV: 'development', EXPO_PUBLIC_GLOW_MODE: 'fixture', EAS_BUILD_PROFILE: 'preview' },
    { GLOW_APP_ENV: 'development', EXPO_PUBLIC_GLOW_MODE: 'fixture', EAS_BUILD_PROFILE: 'production' },
  ]) {
    for (const rendered of ['0', '1']) {
      const result = spawnSync(process.execPath, ['node_modules/expo/bin/cli', 'config', '--type', 'public'], {
        env: { ...process.env, ...env, GLOW_RENDERED_TESTS: rendered }, encoding: 'utf8', timeout: 15000,
      });
      assert.notEqual(result.status, 0);
      assert.match(result.stderr + result.stdout, /development-only/);
    }
  }
});

const configEnvironment = (overrides, unset = []) => {
  const env = { ...process.env, GLOW_APP_ENV: 'development', EXPO_PUBLIC_GLOW_MODE: 'fixture', ...overrides };
  for (const name of unset) delete env[name];
  return env;
};
const publicConfig = (env) => spawnSync(process.execPath, ['node_modules/expo/bin/cli', 'config', '--type', 'public'], { env, encoding: 'utf8', timeout: 15000 });

test('Expo config allows only GLOW_APP_ENV=development: staging, preview and unset are refused, not only production (M05 finding 17)', () => {
  for (const [label, env] of [
    ['staging', configEnvironment({ GLOW_APP_ENV: 'staging' })],
    ['preview', configEnvironment({ GLOW_APP_ENV: 'preview' })],
    ['unset', configEnvironment({}, ['GLOW_APP_ENV'])],
  ]) {
    for (const rendered of ['0', '1']) {
      const result = publicConfig({ ...env, GLOW_RENDERED_TESTS: rendered });
      assert.notEqual(result.status, 0, `GLOW_APP_ENV ${label}`);
      assert.match(result.stderr + result.stdout, /development-only/, `GLOW_APP_ENV ${label}`);
    }
  }
  // The allowed environment still passes, so the refusals above are the allow-list's.
  const allowed = publicConfig({ ...configEnvironment({}), GLOW_RENDERED_TESTS: '0' });
  assert.equal(allowed.status, 0, 'GLOW_APP_ENV development with fixture mode is accepted');
});

test('Expo public config refuses an unreviewed name that shares a reviewed prefix: the allow-list is exact (M05 finding 17)', () => {
  const sentinel = 'synthetic-prefix-credential-never-print';
  for (const name of ['EXPO_PUBLIC_GLOW_STREAM_TOKEN', 'EXPO_PUBLIC_GLOW_MODE_OVERRIDE', 'EXPO_PUBLIC_GLOW_API_BASE_URL_SECRET']) {
    for (const rendered of ['0', '1']) {
      const result = publicConfig({ ...configEnvironment({ [name]: sentinel }), GLOW_RENDERED_TESTS: rendered });
      assert.notEqual(result.status, 0, name);
      assert.match(result.stderr + result.stdout, /Unreviewed public environment/, name);
      assert.ok(!(result.stderr + result.stdout).includes(sentinel));
    }
  }
});

test('Expo public config rejects unreviewed credential variables without echoing values', () => {
  const sentinel = 'synthetic-provider-credential-never-print';
  for (const name of ['EXPO_PUBLIC_HDE_API_TOKEN', 'EXPO_PUBLIC_STREAM_SECRET', 'EXPO_PUBLIC_UNKNOWN', 'EXPO_PUBLIC_PROJECT_ROOT']) {
    for (const rendered of ['0', '1']) {
      const result = spawnSync(process.execPath, ['node_modules/expo/bin/cli', 'config', '--type', 'public'], {
        env: { ...process.env, GLOW_APP_ENV: 'development', EXPO_PUBLIC_GLOW_MODE: 'fixture', GLOW_RENDERED_TESTS: rendered, [name]: sentinel },
        encoding: 'utf8', timeout: 15000,
      });
      assert.notEqual(result.status, 0);
      assert.match(result.stderr + result.stdout, /Unreviewed public environment/);
      assert.ok(!(result.stderr + result.stdout).includes(sentinel));
    }
  }
});
