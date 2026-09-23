import { useEffect } from 'react';
import { Stack, router, useGlobalSearchParams, usePathname, useRootNavigationState } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { Platform, Text } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Page, colors, styles } from '../components/ui';
import { OnboardingProvider, useOnboarding } from '../onboarding/context';
import { canAccessRoute, sanitizeDestination } from '../onboarding/routes';

function Navigation() {
  const { state } = useOnboarding();
  const path = usePathname();
  const params = useGlobalSearchParams();
  const navigation = useRootNavigationState();
  const hasParams = Object.keys(params).length > 0;
  const invalidWebLocation = Platform.OS === 'web' && typeof window !== 'undefined' &&
    (window.location.search !== '' || window.location.hash !== '');
  useEffect(() => {
    if (navigation?.key && (hasParams || invalidWebLocation || (path !== '/' && sanitizeDestination(path) === '/'))) router.replace('/');
  }, [hasParams, invalidWebLocation, navigation?.key, path]);
  return <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.background } }}>
    <Stack.Screen name="index" />
    <Stack.Protected guard={canAccessRoute('/account', state)}><Stack.Screen name="account" /></Stack.Protected>
    <Stack.Protected guard={canAccessRoute('/verify', state)}><Stack.Screen name="verify" /></Stack.Protected>
    <Stack.Protected guard={canAccessRoute('/recovery', state)}><Stack.Screen name="recovery" /></Stack.Protected>
    <Stack.Protected guard={canAccessRoute('/reset-password', state)}><Stack.Screen name="reset-password" /></Stack.Protected>
    <Stack.Protected guard={canAccessRoute('/eligibility', state)}><Stack.Screen name="eligibility" /></Stack.Protected>
    <Stack.Protected guard={canAccessRoute('/birth', state)}><Stack.Screen name="birth" /></Stack.Protected>
    <Stack.Protected guard={canAccessRoute('/remaining', state)}><Stack.Screen name="remaining" /></Stack.Protected>
    <Stack.Protected guard={canAccessRoute('/restricted', state)}><Stack.Screen name="restricted" /></Stack.Protected>
    <Stack.Protected guard={canAccessRoute('/recommended', state)}><Stack.Screen name="recommended" /><Stack.Screen name="explore" /></Stack.Protected>
    <Stack.Screen name="development" />
    <Stack.Screen name="+not-found" />
  </Stack>;
}

export default function RootLayout() {
  // Synthetic routes and controls never render in a production bundle.
  if (!__DEV__ || process.env.EXPO_PUBLIC_GLOW_MODE !== 'fixture') {
    return <SafeAreaProvider><Page><Text style={styles.title}>Development preview unavailable</Text>
      <Text style={styles.body}>This foundation has no production mode.</Text></Page></SafeAreaProvider>;
  }
  return <SafeAreaProvider><StatusBar style="light" /><OnboardingProvider><Navigation /></OnboardingProvider></SafeAreaProvider>;
}
