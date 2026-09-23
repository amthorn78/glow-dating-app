import type { ExpoConfig } from 'expo/config';

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
  platforms: ['ios', 'android'],
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
