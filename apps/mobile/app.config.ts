import type { ExpoConfig } from 'expo/config';

// Expo embeds EXPO_PUBLIC_* values into client bundles. Only these reviewed
// public configuration names are permitted; do not echo rejected names/values.
const publicNames = new Set(['EXPO_PUBLIC_GLOW_MODE', 'EXPO_PUBLIC_GLOW_API_BASE_URL']);
const renderedTests = process.env.GLOW_RENDERED_TESTS === '1';
// SDK 57 injects this exact project directory before web manifest evaluation.
// Accept it only for the explicit local test harness, never an arbitrary path.
const isRenderedSdkRoot = (name: string) => renderedTests && name === 'EXPO_PUBLIC_PROJECT_ROOT' && process.env[name] === __dirname;
if (Object.keys(process.env).some((name) => name.startsWith('EXPO_PUBLIC_') && !publicNames.has(name) && !isRenderedSdkRoot(name))) {
  throw new Error('Unreviewed public environment configuration is forbidden.');
}

if (
  process.env.GLOW_APP_ENV !== 'development' ||
  process.env.EXPO_PUBLIC_GLOW_MODE !== 'fixture' ||
  (process.env.EAS_BUILD_PROFILE && process.env.EAS_BUILD_PROFILE !== 'development')
) {
  throw new Error('Glow foundation is development-only. Production and preview release builds are blocked.');
}

const config: ExpoConfig = {
  name: 'Glow Development',
  slug: 'glow-dating-development',
  version: '0.1.0',
  // The explicit test harness renders these native screens with React Native Web.
  // Normal app configuration and native exports remain iOS/Android only.
  platforms: renderedTests ? ['ios', 'android', 'web'] : ['ios', 'android'],
  orientation: 'default',
  scheme: 'glow-development',
  userInterfaceStyle: 'dark',
  backgroundColor: '#17151E',
  plugins: ['expo-router'],
  experiments: { typedRoutes: true },
  ios: { supportsTablet: true },
  android: { blockedPermissions: ['android.permission.RECORD_AUDIO'] },
};
export default config;
