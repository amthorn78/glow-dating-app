import { expect, test, type Page } from '@playwright/test';

// P06.3: the notification settings screen and its route guard, on the actual screens and memory
// fixtures. Full-page navigation starts a fresh fixture instance; the restricted fixtures reach
// `/notifications` by an in-app history navigation, in the same instance.
const active = (page: Page, id: string) => page.getByTestId(id).filter({ visible: true });
const MATCH_SENDS = 'When you have a new match, Glow sends “You have a new match.” and nothing else.';
const MESSAGE_SENDS = 'When you have a new message, Glow sends “You have a new message.” and nothing else.';
const DENIED = 'Notifications are off in this device’s settings. Glow works without them.';

test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status === testInfo.expectedStatus) return;
  const screens = await page.locator('[data-testid^="screen-"]:visible').evaluateAll(nodes => nodes.map(node => node.getAttribute('data-testid'))).catch(() => []);
  console.info('Visible screen identities after failure:', screens);
});

async function eligible(page: Page) {
  await page.goto('/development');
  await active(page, 'scenario-eligible').click();
  await expect(page.getByText(/Make room for/).filter({ visible: true })).toBeVisible();
}
async function openNotifications(page: Page) {
  await active(page, 'open-profile').click();
  await expect(active(page, 'screen-profile')).toBeVisible();
  await active(page, 'profile-notifications').click();
  await expect(active(page, 'screen-notifications')).toBeVisible();
  await expect(active(page, 'notification-toggle-match')).toBeEnabled();
}
async function fixtureControls(page: Page) {
  if (!await active(page, 'notification-fixture-state').isVisible()) await active(page, 'notification-fixture-toggle').click();
  await expect(active(page, 'notification-fixture-state')).toBeVisible();
}
/** An in-app navigation, as a tapped notification's route or a deep link would make: no reload. */
async function navigateInApp(page: Page, path: string) {
  await page.evaluate(target => {
    window.history.pushState(null, '', target);
    window.dispatchEvent(new PopStateEvent('popstate', { state: null }));
  }, path);
}
const settledFrames = (page: Page) => page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));

test('the notification settings route denies signed-out entry and discards private URL data', async ({ page }) => {
  for (const url of ['/notifications', '/notifications?device=private-sentinel#private-sentinel']) {
    await page.goto(url);
    await expect(active(page, 'screen-account')).toBeVisible();
    await expect(page).toHaveURL(/\/account$/);
    await expect(page.getByTestId('screen-notifications')).toHaveCount(0);
    await expect(page.getByText('private-sentinel', { exact: true })).toHaveCount(0);
  }
});

for (const restriction of ['suspended', 'deletion_pending'] as const) {
  test(`a ${restriction} account never reaches the notification settings screen`, async ({ page }) => {
    await eligible(page);
    await openNotifications(page);
    await active(page, 'development-link').click();
    await active(page, `scenario-${restriction}`).click();
    await expect(active(page, 'screen-restricted')).toBeVisible();
    await expect(page.getByTestId('screen-notifications')).toHaveCount(0);
    await navigateInApp(page, '/notifications');
    await settledFrames(page);
    await expect(active(page, 'screen-restricted')).toBeVisible();
    await expect(page.getByTestId('screen-notifications')).toHaveCount(0);
    await expect(page.getByTestId('notification-kinds')).toHaveCount(0);
    await expect(page).not.toHaveURL(/\/notifications/);
  });
}

test('before any request the screen says what each kind sends; both start off and nothing asks at launch', async ({ page }) => {
  await eligible(page);
  await openNotifications(page);
  await expect(active(page, 'notification-sends-match')).toHaveText(MATCH_SENDS);
  await expect(active(page, 'notification-sends-message')).toHaveText(MESSAGE_SENDS);
  await expect(active(page, 'notification-status-match')).toHaveText('Off for this device');
  await expect(active(page, 'notification-status-message')).toHaveText('Off for this device');
  await fixtureControls(page);
  await expect(active(page, 'notification-fixture-state')).toContainText('Times asked: 0.');
  await expect(page.locator('body')).not.toContainText(/SYNTHETIC-FIXTURE-PUSH-TOKEN|Expo|Apple|Google|Firebase/);
});

test('with the permission declined, nothing is saved and every other journey works as before', async ({ page }) => {
  await eligible(page);
  await openNotifications(page);
  await fixtureControls(page);
  await active(page, 'notification-permission-undetermined_deny').click();
  await active(page, 'notification-toggle-match').click();
  await expect(active(page, 'notifications-denied')).toHaveText(DENIED);
  await expect(active(page, 'notification-status-match')).toHaveText('Off for this device');
  await expect(active(page, 'notification-status-message')).toHaveText('Off for this device');
  await expect(active(page, 'notification-fixture-state')).toContainText('Times asked: 1.');
  await active(page, 'notification-toggle-message').click();
  await expect(active(page, 'notifications-denied')).toHaveText(DENIED);
  await expect(active(page, 'notification-fixture-state')).toContainText('Times asked: 1.');
  // Every other route and journey, with the permission declined.
  await active(page, 'notifications-profile').click();
  await expect(active(page, 'screen-profile')).toBeVisible();
  await active(page, 'profile-discovery').click();
  await expect(page.getByText(/Make room for/).filter({ visible: true })).toBeVisible();
  await expect(active(page, 'discovery-card-profile-jules')).toBeVisible();
  await active(page, 'open-matches').click();
  await expect(page.getByTestId('match-list').filter({ visible: true })).toBeVisible();
  await active(page, 'open-profile').click();
  await expect(active(page, 'screen-profile')).toBeVisible();
  await active(page, 'preferences-edit').click();
  await expect(active(page, 'screen-preferences')).toBeVisible();
  await page.goBack();
  await expect(active(page, 'screen-profile')).toBeVisible();
  await active(page, 'profile-notifications').click();
  await expect(active(page, 'screen-notifications')).toBeVisible();
  await expect(active(page, 'notification-status-match')).toHaveText('Off for this device');
  await active(page, 'logout').click();
  await expect(active(page, 'screen-account')).toBeVisible();
});

test('turning kinds on and off saves only that kind, and a logout ends this device\'s notifications', async ({ page }) => {
  await eligible(page);
  await openNotifications(page);
  await active(page, 'notification-toggle-match').click();
  await expect(active(page, 'notification-status-match')).toHaveText('On for this device');
  await expect(active(page, 'notification-status-message')).toHaveText('Off for this device');
  await active(page, 'notification-toggle-message').click();
  await expect(active(page, 'notification-status-message')).toHaveText('On for this device');
  await active(page, 'notification-toggle-match').click();
  await expect(active(page, 'notification-status-match')).toHaveText('Off for this device');
  await expect(active(page, 'notification-status-message')).toHaveText('On for this device');
  await fixtureControls(page);
  await expect(active(page, 'notification-fixture-state')).toContainText('Times asked: 1.');
  await expect(page.locator('body')).not.toContainText('SYNTHETIC-FIXTURE-PUSH-TOKEN');
  await active(page, 'logout').click();
  await expect(active(page, 'screen-account')).toBeVisible();
  await active(page, 'development-link').click();
  await active(page, 'scenario-eligible').click();
  await expect(page.getByText(/Make room for/).filter({ visible: true })).toBeVisible();
  await openNotifications(page);
  await expect(active(page, 'notification-status-match')).toHaveText('Off for this device');
  await expect(active(page, 'notification-status-message')).toHaveText('Off for this device');
});

test('the notification settings screen fits 320px with doubled text', async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await eligible(page);
  await openNotifications(page);
  await page.evaluate(() => {
    const sizes = Array.from(document.querySelectorAll<HTMLElement>('div, button')).map(el => [el, parseFloat(getComputedStyle(el).fontSize)] as const);
    for (const [el, size] of sizes) { el.style.fontSize = `${size * 2}px`; el.style.lineHeight = '1.4'; }
  });
  await expect(active(page, 'notification-sends-message')).toBeVisible();
  await expect(active(page, 'notification-toggle-message')).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});
