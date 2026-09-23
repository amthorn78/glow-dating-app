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
    const result = spawnSync(process.execPath, ['node_modules/expo/bin/cli', 'config', '--type', 'public'], {
      env: { ...process.env, ...env }, encoding: 'utf8', timeout: 15000,
    });
    assert.notEqual(result.status, 0);
    assert.match(result.stderr + result.stdout, /development-only/);
  }
});

test('Expo public config rejects unreviewed credential variables without echoing values', () => {
  const sentinel = 'synthetic-provider-credential-never-print';
  for (const name of ['EXPO_PUBLIC_HDE_API_TOKEN', 'EXPO_PUBLIC_STREAM_SECRET', 'EXPO_PUBLIC_UNKNOWN']) {
    const result = spawnSync(process.execPath, ['node_modules/expo/bin/cli', 'config', '--type', 'public'], {
      env: { ...process.env, GLOW_APP_ENV: 'development', EXPO_PUBLIC_GLOW_MODE: 'fixture', [name]: sentinel },
      encoding: 'utf8', timeout: 15000,
    });
    assert.notEqual(result.status, 0);
    assert.match(result.stderr + result.stdout, /Unreviewed public environment/);
    assert.ok(!(result.stderr + result.stdout).includes(sentinel));
  }
});
