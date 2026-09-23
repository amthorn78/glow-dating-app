import { defineConfig } from '@playwright/test';

// Development rendering of the native screens on React Native Web. This is not
// a consumer web target, signed native build, or device accessibility proof.
export default defineConfig({
  testDir: './rendered',
  outputDir: './.work/rendered-results',
  timeout: 45_000,
  expect: { timeout: 10_000 },
  workers: 1,
  retries: 0,
  reporter: 'list',
  use: {
    browserName: 'chromium',
    baseURL: 'http://127.0.0.1:8081',
    viewport: { width: 390, height: 844 },
    trace: 'off',
    screenshot: 'off',
  },
  webServer: {
    command: 'node scripts/development.mjs start --web --host localhost --port 8081',
    url: 'http://127.0.0.1:8081',
    timeout: 180_000,
    reuseExistingServer: false,
    env: { CI: '1', EXPO_OFFLINE: '1', BROWSER: 'none' },
    gracefulShutdown: { signal: 'SIGTERM', timeout: 5_000 },
  },
});
