import { useRef, useState } from 'react';
import { Text, View } from 'react-native';
import { Button, styles } from '../components/ui';
import { useInteractions } from '../interactions/context';
import { useChatFixture } from './context';
import { PROVIDER_FIELD_CASES, type ChatScenario, type OwnDelivery } from './fixture-adapter';

const OTHER = 'profile-jules';
const label = (value: string) => value.replaceAll('_', ' ');

/**
 * Labeled synthetic controls for the in-process chat fixture, in the guarded development
 * runtime only. Fictional Jules acts through the same checks as the signed-in member. These
 * are test controls, not product features, and nothing here reaches a provider.
 */
export function ChatFixtureControls({ matchId, compact = false }: { matchId: string | null; compact?: boolean }) {
  const fixture = useChatFixture();
  const { store: interactions } = useInteractions();
  const [shown, setShown] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const sent = useRef(0);
  if (!matchId) return null;
  const done = (ok: boolean, message: string) => setNote(ok ? message : 'This fixture action is unavailable for the current conversation.');
  return <View style={styles.notice} testID="chat-fixture-controls">
    <Text style={styles.eyebrow}>SYNTHETIC CHAT TEST CONTROLS</Text>
    <Button label={shown ? 'Hide chat fixture controls' : 'Show chat fixture controls'} testID="chat-fixture-toggle" secondary onPress={() => setShown(!shown)} />
    {shown && <>
      <Text style={styles.small}>Internal fictional setup. Fictional Jules acts through the same checks as you. Settings: delivery {label(fixture.scenario)}; your next messages {fixture.delivery}; provider field {fixture.providerField ? label(fixture.providerField) : 'none'}; text read {fixture.outage ? 'failing' : 'normal'}.</Text>
      <Button label="Fictional Jules sends a message" testID="chat-other-send" secondary
        onPress={() => done(fixture.developmentOtherSend(OTHER, matchId, `Hello from fictional Jules, message ${++sent.current}.`), 'Fictional Jules sent a message.')} />
      {!compact && <>
        <Button label="Fictional Jules sends a message held in delivery" testID="chat-other-send-held" secondary
          onPress={() => done(fixture.developmentOtherSend(OTHER, matchId, `A held message from fictional Jules, ${++sent.current}.`, 'hold'), 'Fictional Jules sent a message that is held in delivery.')} />
        <Button label="Deliver held fictional messages" testID="chat-deliver-held" secondary
          onPress={() => done(true, `Delivered ${fixture.developmentDeliverHeld()} held messages.`)} />
        <Button label="Seed 25 fictional history messages" testID="chat-seed" secondary
          onPress={() => done(fixture.developmentSeed(OTHER, matchId, 25), 'Seeded fictional history.')} />
        <Button label="Fictional Jules sends a message whose stored text then changes" testID="chat-alter" secondary
          onPress={() => done(fixture.developmentOtherSend(OTHER, matchId, `A message that will change, ${++sent.current}.`) &&
            fixture.developmentAlterLatest(matchId), 'Fictional Jules sent a message, and its stored text changed.')} />
        <Button label="Plant a message Glow never sent" testID="chat-plant" secondary
          onPress={() => { fixture.developmentPlantProviderMessage(`Planted fictional text ${++sent.current}.`); done(true, 'Planted a message Glow never sent.'); }} />
        {(['accept', 'hold', 'fail'] as const satisfies readonly OwnDelivery[]).map(value => <Button key={value} label={`Your next messages: ${value}`}
          testID={`chat-delivery-${value}`} secondary onPress={() => fixture.setDelivery(value)} />)}
        {(['normal', 'offline', 'lost_response', 'delayed'] as const satisfies readonly ChatScenario[]).map(value => <Button key={value}
          label={`Chat ${label(value)} fixture`} testID={`chat-scenario-${value}`} secondary onPress={() => fixture.setScenario(value)} />)}
        <Button label="Complete delayed chat delivery" testID="chat-release" secondary onPress={() => fixture.releaseDelayed()} />
        <Button label={fixture.outage ? 'Restore the text read' : 'Fail the text read'} testID="chat-outage" secondary onPress={() => fixture.setOutage(!fixture.outage)} />
        <Button label="Provider field: none" testID="chat-provider-none" secondary onPress={() => fixture.setProviderField(null)} />
        {PROVIDER_FIELD_CASES.map(value => <Button key={value} label={`Provider field: ${label(value)}`} testID={`chat-provider-${value}`}
          secondary onPress={() => fixture.setProviderField(value)} />)}
        <Button label="Block fictional Jules" testID="chat-block" secondary onPress={() => interactions.developmentBlock(OTHER, true)} />
        <Button label="Fictional Jules blocks you" testID="chat-other-block" secondary
          onPress={() => done(fixture.developmentOtherBlock(OTHER), 'Fictional Jules blocked you.')} />
      </>}
      {note && <Text style={styles.small} testID="chat-fixture-note">{note}</Text>}
    </>}
  </View>;
}
