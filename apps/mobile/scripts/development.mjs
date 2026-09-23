import { spawnSync } from 'node:child_process';

// Never silently turn a requested release environment into fixture development.
const environment = process.env.GLOW_APP_ENV ?? 'development';
const mode = process.env.EXPO_PUBLIC_GLOW_MODE ?? 'fixture';
if (environment !== 'development' || mode !== 'fixture') {
  throw new Error('This foundation supports development fixtures only. Release is blocked.');
}
const result = spawnSync(process.execPath, ['node_modules/expo/bin/cli', ...process.argv.slice(2)], {
  stdio: 'inherit',
  env: { ...process.env, GLOW_APP_ENV: environment, EXPO_PUBLIC_GLOW_MODE: mode },
});
if (result.error) throw result.error;
process.exit(result.status ?? 1);
