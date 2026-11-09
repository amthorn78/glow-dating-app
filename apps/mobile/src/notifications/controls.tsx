import { useState } from 'react';
import { Text, View } from 'react-native';
import { Button, styles } from '../components/ui';
import { useNotificationFixture } from './context';
import type { NotificationScenario } from './fixture-adapter';
import { PERMISSION_SETTINGS, type PermissionSetting } from './permission';

const PERMISSION_LABELS: Readonly<Record<PermissionSetting, string>> = Object.freeze({
  undetermined_allow: 'not asked yet; allows when asked',
  undetermined_deny: 'not asked yet; declines when asked',
  granted: 'allowed',
  denied: 'declined',
});

/**
 * Labelled synthetic controls for the notification fixture (P06.3, D5), in the guarded development
 * runtime only. They set what the fixture permission seam answers and the fixture's delivery
 * scenario. These are test controls, not product features; nothing here reaches a device's
 * permission, a platform or a push service.
 */
export function NotificationFixtureControls() {
  const { adapter, permission } = useNotificationFixture();
  const [shown, setShown] = useState(false);
  return <View style={styles.notice} testID="notification-fixture-controls">
    <Text style={styles.eyebrow}>SYNTHETIC NOTIFICATION TEST CONTROLS</Text>
    <Button label={shown ? 'Hide notification fixture controls' : 'Show notification fixture controls'} testID="notification-fixture-toggle" secondary
      onPress={() => setShown(!shown)} />
    {shown && <>
      <Text style={styles.small} testID="notification-fixture-state">Fixture permission: {PERMISSION_LABELS[permission.setting]}. Times asked: {permission.requests}. Delivery: {adapter.scenario.replaceAll('_', ' ')}.</Text>
      {PERMISSION_SETTINGS.map(setting => <Button key={setting} label={`Fixture permission: ${PERMISSION_LABELS[setting]}`}
        testID={`notification-permission-${setting}`} secondary onPress={() => permission.set(setting)} />)}
      {(['normal', 'offline', 'lost_response'] as const satisfies readonly NotificationScenario[]).map(value => <Button key={value}
        label={`Notification ${value.replaceAll('_', ' ')} fixture`} testID={`notification-scenario-${value}`} secondary onPress={() => adapter.setScenario(value)} />)}
    </>}
  </View>;
}
