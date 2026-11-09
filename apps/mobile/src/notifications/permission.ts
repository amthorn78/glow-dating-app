/**
 * The platform's notification permission, as the app sees it (P06.3, D5). The seam has three
 * answers: `undetermined` (the platform has not asked), `granted` and `denied`. `request` asks the
 * platform; the app calls it only while the answer is undetermined, and only from the member's own
 * action of turning a kind on. Nothing asks at launch, at sign-in or on any other screen, and there
 * is no provisional authorization.
 *
 * Its only implementation is the fixture below, whose answer a labelled synthetic control sets in
 * the development preview. The native module, the platform's own prompt and mapping its answers
 * (including whether it may ask again) come with P09.2 (D6, D9).
 */
export type PermissionStatus = 'undetermined' | 'granted' | 'denied';
export interface PermissionSeam {
  status(): PermissionStatus;
  request(): Promise<PermissionStatus>;
}

/** What the fixture answers: undetermined (and what it answers when asked), or already decided. */
export type PermissionSetting = 'undetermined_allow' | 'undetermined_deny' | 'granted' | 'denied';
export const PERMISSION_SETTINGS: readonly PermissionSetting[] = Object.freeze(['undetermined_allow', 'undetermined_deny', 'granted', 'denied']);

export class FixturePermissionSeam implements PermissionSeam {
  private value: PermissionStatus = 'undetermined';
  private answer: 'granted' | 'denied' = 'granted';
  private settingValue: PermissionSetting = 'undetermined_allow';
  private asked = 0;
  private readonly listeners = new Set<() => void>();
  readonly subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  private emit() { this.listeners.forEach(listener => listener()); }
  /** How many times the platform was asked. */
  get requests() { return this.asked; }
  get setting() { return this.settingValue; }
  set(setting: PermissionSetting) {
    this.settingValue = setting;
    if (setting === 'granted' || setting === 'denied') this.value = setting;
    else { this.value = 'undetermined'; this.answer = setting === 'undetermined_allow' ? 'granted' : 'denied'; }
    this.emit();
  }
  status(): PermissionStatus { return this.value; }
  async request(): Promise<PermissionStatus> {
    this.asked += 1;
    if (this.value === 'undetermined') { this.value = this.answer; this.settingValue = this.answer; }
    this.emit();
    return this.value;
  }
}
