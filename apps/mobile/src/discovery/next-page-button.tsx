import { Button } from '../components/ui';
export type NextPageButtonProps = { disabled: boolean; onPress: () => void };
export function NextPageButton({ disabled, onPress }: NextPageButtonProps) {
  return <Button label="Next page" testID="discovery-next" disabled={disabled} onPress={onPress}
    hint="Browse the next fictional profiles. This does not record a like or a pass." />;
}
