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
    baseURL: 'http://localhost:8081',
    viewport: { width: 390, height: 844 },
    trace: 'off',
    screenshot: 'off',
  },
  webServer: {
    command: 'node scripts/development.mjs start --web --host localhost --port 8081',
    // Match Expo's localhost binding (which may resolve to IPv6).
    url: 'http://localhost:8081/status',
    timeout: 180_000,
    reuseExistingServer: false,
    env: { CI: '1', EXPO_OFFLINE: '1', BROWSER: 'none', GLOW_RENDERED_TESTS: '1' },
    stdout: 'pipe',
    stderr: 'pipe',
    gracefulShutdown: { signal: 'SIGTERM', timeout: 5_000 },
  },
});
