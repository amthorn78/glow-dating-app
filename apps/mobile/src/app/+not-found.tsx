import { router } from 'expo-router';
import { Text } from 'react-native';
import { Button, Page, ScreenTitle, styles } from '../components/ui';

export default function UnknownDestination() {
  // Do not reflect untrusted path/query contents or automatically navigate while
  // Router is resolving its unmatched route and dynamic params.
  return <Page testID="screen-link-unavailable">
    <ScreenTitle>This link is unavailable.</ScreenTitle>
    <Text style={styles.body}>Return to your current step to continue safely.</Text>
    <Button label="Return to current step" testID="return-current-step" onPress={() => router.replace('/')} />
  </Page>;
}
