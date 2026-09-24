import { Button } from '../components/ui';

export type ActionButtonProps = {
  label: string; testID: string; disabled: boolean; onPress: () => void; secondary?: boolean;
};

export function ActionButton(props: ActionButtonProps) {
  return <Button {...props} />;
}
