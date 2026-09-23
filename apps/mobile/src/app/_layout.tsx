import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { Text } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Page, colors, styles } from '../components/ui';

export default function RootLayout() {
  // A JS production bundle cannot display the synthetic profiles, even if exported manually.
  if (!__DEV__ || process.env.EXPO_PUBLIC_GLOW_MODE !== 'fixture') {
    return <SafeAreaProvider><Page><Text style={styles.title}>Development preview unavailable</Text>
      <Text style={styles.body}>This foundation has no production mode.</Text></Page></SafeAreaProvider>;
  }
  return <SafeAreaProvider>
    <StatusBar style="light" />
    <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.background } }}>
      <Stack.Screen name="index" />
      <Stack.Screen name="explore" />
    </Stack>
  </SafeAreaProvider>;
}
