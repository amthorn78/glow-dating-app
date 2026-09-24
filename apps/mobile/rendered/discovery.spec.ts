import { expect, test, type Page } from '@playwright/test';

// These are real routed screens using the guarded in-memory fixture. A full
// document load creates a new session; progress assertions use in-app routes.
const active = (page: Page, id: string) => page.getByTestId(id).filter({ visible: true });
const cards = (page: Page) => active(page, 'discovery-cards').locator('[data-testid^="discovery-card-"]');
const identities = async (page: Page) => cards(page).evaluateAll(nodes => nodes.map(node => node.getAttribute('data-testid')!.slice('discovery-card-'.length)));

const expectedPages = {
  recommended: [['profile-jules', 'profile-morgan'], ['profile-iris', 'profile-kai'], ['profile-lena', 'profile-noor']],
  broader: [['profile-iris', 'profile-jules'], ['profile-kai', 'profile-lena'], ['profile-morgan', 'profile-noor']],
} as const;

test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status === testInfo.expectedStatus) return;
  // Safe route identities only; do not capture private forms, state or traces.
  const screens = await page.locator('[data-testid^="screen-"]:visible').evaluateAll(nodes => nodes.map(node => node.getAttribute('data-testid'))).catch(() => []);
  console.info('Visible screen identities after failure:', screens);
});

async function eligibleDiscovery(page: Page) {
  await page.goto('/development');
  await active(page, 'scenario-eligible').click();
  await expect(active(page, 'screen-recommended')).toBeVisible();
  await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[0]);
}

async function setDiscoveryScenario(page: Page, scenario: 'normal' | 'empty' | 'pending' | 'unavailable' | 'error' | 'offline') {
  await active(page, 'development-link').click();
  await active(page, `discovery-scenario-${scenario}`).click();
  await active(page, 'return-current').click();
  await expect(active(page, 'screen-recommended')).toBeVisible();
  await active(page, 'discovery-refresh').click();
}

for (const mode of ['recommended', 'broader'] as const) {
  test(`${mode} has three ordered pages without duplicates and stops at exhaustion`, async ({ page }) => {
    await eligibleDiscovery(page);
    if (mode === 'broader') await page.getByRole('button', { name: 'Explore more', exact: true }).click();
    const seen: string[] = [];
    for (const [index, expected] of expectedPages[mode].entries()) {
      await expect.poll(() => identities(page)).toEqual(expected);
      seen.push(...await identities(page));
      if (index < expectedPages[mode].length - 1) {
        await expect(active(page, 'discovery-next')).toBeEnabled();
        await active(page, 'discovery-next').click();
      }
    }
    expect(seen).toHaveLength(6);
    expect(new Set(seen).size).toBe(6);
    await expect(active(page, 'discovery-next')).toBeDisabled();
    await expect(active(page, 'discovery-status')).toContainText(/end of|exhausted|all profiles/i);
    // Returning to a mode is not a refresh and cannot wrap its finite queue.
    const leave = mode === 'recommended' ? 'Explore more' : 'Back to recommended';
    const back = mode === 'recommended' ? 'Back to recommended' : 'Explore more';
    await page.getByRole('button', { name: leave, exact: true }).click();
    await page.getByRole('button', { name: back, exact: true }).click();
    await expect.poll(() => identities(page)).toEqual(expectedPages[mode][2]);
    await expect(active(page, 'discovery-next')).toBeDisabled();
  });
}

test('recommended and broader discovery preserve their independent current page', async ({ page }) => {
  await eligibleDiscovery(page);
  await active(page, 'discovery-next').click();
  await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[1]);
  await page.getByRole('button', { name: 'Explore more', exact: true }).click();
  await expect(active(page, 'screen-explore')).toBeVisible();
  await expect.poll(() => identities(page)).toEqual(expectedPages.broader[0]);
  await active(page, 'discovery-next').click();
  await expect.poll(() => identities(page)).toEqual(expectedPages.broader[1]);
  await page.getByRole('button', { name: 'Back to recommended', exact: true }).click();
  await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[1]);
  await page.getByRole('button', { name: 'Explore more', exact: true }).click();
  await expect.poll(() => identities(page)).toEqual(expectedPages.broader[1]);
});

test('browser Back reactivates the retained recommended queue before the next browse action', async ({ page }) => {
  await eligibleDiscovery(page);
  await active(page, 'discovery-next').click();
  await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[1]);
  await page.getByRole('button', { name: 'Explore more', exact: true }).click();
  await expect.poll(() => identities(page)).toEqual(expectedPages.broader[0]);
  await active(page, 'discovery-next').click();
  await expect.poll(() => identities(page)).toEqual(expectedPages.broader[1]);
  await page.goBack();
  await expect(active(page, 'screen-recommended')).toBeVisible();
  await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[1]);
  await active(page, 'discovery-next').click();
  await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[2]);
  await page.getByRole('button', { name: 'Explore more', exact: true }).click();
  await expect.poll(() => identities(page)).toEqual(expectedPages.broader[1]);
});

test('explicit refresh starts a new finite queue without recording a like or pass', async ({ page }) => {
  await eligibleDiscovery(page);
  await active(page, 'discovery-next').click();
  await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[1]);
  await active(page, 'discovery-next').click();
  await expect(active(page, 'discovery-next')).toBeDisabled();
  await active(page, 'discovery-refresh').click();
  await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[0]);
  await expect(active(page, 'discovery-next')).toBeEnabled();
  await expect(active(page, 'screen-recommended')).toContainText(/browsing|navigation/i);
  await expect(page.getByRole('button', { name: /^(like|pass|send message)$/i })).toHaveCount(0);
});

test('loading announces progress, hides the previous page and prevents a double advance', async ({ page }) => {
  await page.clock.install({ time: new Date('2026-09-23T12:00:00Z') });
  await eligibleDiscovery(page);
  const currentTime = await page.evaluate(() => Date.now());
  await page.clock.pauseAt(currentTime + 10_000);
  // Freeze the real fixture delay instead of racing a 250ms loading state.
  // Dispatch the button event through React; do not change app/store state.
  await active(page, 'discovery-next').dispatchEvent('click');
  await expect(active(page, 'discovery-status')).toHaveText('Loading preview…');
  await expect(active(page, 'discovery-status')).toHaveAttribute('aria-live', 'polite');
  await expect(cards(page)).toHaveCount(0);
  await expect(active(page, 'discovery-next')).toBeDisabled();
  await expect(active(page, 'discovery-refresh')).toBeDisabled();
  await active(page, 'discovery-next').dispatchEvent('click');
  await page.clock.runFor(300);
  await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[1]);
  await expect(active(page, 'discovery-next')).toBeEnabled();
  await page.clock.resume();
});

test('mixed provider outcomes keep eligible people visible with pending compatibility', async ({ page }) => {
  await eligibleDiscovery(page);
  await expect(active(page, 'discovery-status')).toContainText(/pending|unavailable/i);
  await expect(active(page, 'discovery-card-profile-jules')).toContainText('Compatibility pending');
  await expect(active(page, 'discovery-card-profile-morgan')).toContainText('Compatibility pending');
  await expect(active(page, 'screen-recommended')).not.toContainText(/no (people|profiles)/i);
  await active(page, 'discovery-next').click();
  await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[1]);
  await expect(active(page, 'discovery-card-profile-iris')).toContainText('Compatibility pending');
  await expect(active(page, 'discovery-card-profile-kai')).toContainText('Compatibility pending');
});

test('empty discovery has an honest empty state and an explicit refresh', async ({ page }) => {
  await eligibleDiscovery(page);
  await setDiscoveryScenario(page, 'empty');
  await expect(cards(page)).toHaveCount(0);
  await expect(active(page, 'discovery-status')).toContainText(/no (people|profiles)/i);
  await expect(active(page, 'discovery-next')).toBeDisabled();
  await expect(active(page, 'discovery-refresh')).toBeEnabled();
  await setDiscoveryScenario(page, 'normal');
  await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[0]);
});

for (const scenario of ['pending', 'unavailable'] as const) {
  test(`all provider outcomes ${scenario} retain authorized cards without claiming no people`, async ({ page }) => {
    await eligibleDiscovery(page);
    await setDiscoveryScenario(page, scenario);
    await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[0]);
    if (scenario === 'pending') {
      // A supported pending result is a successful page, not a provider failure.
      await expect(active(page, 'discovery-status')).toHaveText('Page 1. More fictional people follow.');
    } else {
      await expect(active(page, 'discovery-status')).toContainText('Some compatibility results are pending or unavailable.');
    }
    await expect(active(page, 'discovery-card-profile-jules')).toContainText('Compatibility pending');
    await expect(active(page, 'discovery-card-profile-morgan')).toContainText('Compatibility pending');
    await expect(active(page, 'screen-recommended')).not.toContainText(/no (people|profiles)/i);
    await expect(active(page, 'discovery-next')).toBeEnabled();
  });
}

for (const scenario of ['error', 'offline'] as const) {
  test(`${scenario} hides retained cards and recovers only through a current successful refresh`, async ({ page }) => {
    await eligibleDiscovery(page);
    await setDiscoveryScenario(page, scenario);
    await expect(cards(page)).toHaveCount(0);
    await expect(active(page, 'discovery-status')).toContainText(/could not load|unavailable|offline/i);
    await expect(active(page, 'screen-recommended')).not.toContainText(/no (people|profiles)/i);
    await expect(active(page, 'discovery-next')).toBeDisabled();
    await expect(active(page, 'discovery-refresh')).toBeEnabled();
    await page.getByRole('button', { name: 'Explore more', exact: true }).click();
    await expect(active(page, 'screen-explore')).toBeVisible();
    await expect(active(page, 'discovery-status')).toContainText(/could not load|unavailable|offline/i);
    await expect(cards(page)).toHaveCount(0);
    await setDiscoveryScenario(page, 'normal');
    await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[0]);
  });
}

test('source invalidation retracts hidden cards and requires explicit reload before displaying current data', async ({ page }) => {
  await eligibleDiscovery(page);
  await active(page, 'discovery-next').click();
  await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[1]);
  await active(page, 'development-link').click();
  // Prove the route is retained before changing authority; no reload/reset is
  // allowed to substitute for revocation of the original hidden projection.
  await expect(page.getByTestId('discovery-card-profile-iris')).toHaveCount(1);
  await expect(active(page, 'discovery-card-profile-iris')).toHaveCount(0);
  await active(page, 'discovery-invalidate').click();
  await expect(page.locator('[data-testid^="discovery-card-"]')).toHaveCount(0);
  await active(page, 'return-current').click();
  await expect(active(page, 'discovery-status')).toContainText(/refresh|reload/i);
  await expect(cards(page)).toHaveCount(0);
  await expect(active(page, 'discovery-next')).toBeDisabled();
  await active(page, 'discovery-refresh').click();
  await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[0]);
});

test('logout removes both modes including their retained public projections', async ({ page }) => {
  await eligibleDiscovery(page);
  await page.getByRole('button', { name: 'Explore more', exact: true }).click();
  await expect.poll(() => identities(page)).toEqual(expectedPages.broader[0]);
  await active(page, 'logout').click();
  await expect(active(page, 'screen-account')).toBeVisible();
  await expect(page.locator('[data-testid^="discovery-card-"]')).toHaveCount(0);
  await expect(page.getByText(/Fictional (Iris|Jules|Kai|Lena|Morgan|Noor)/)).toHaveCount(0);
  await page.goBack();
  if (page.url() === 'about:blank') await page.goto('/explore');
  await expect(active(page, 'screen-account')).toBeVisible();
  await expect(page.locator('[data-testid^="discovery-card-"]')).toHaveCount(0);
});

test('both modes disclose public candidate text without private eligibility or provider data', async ({ page }) => {
  const consoleText: string[] = [];
  page.on('console', message => consoleText.push(message.text()));
  await eligibleDiscovery(page);
  for (const mode of ['recommended', 'broader'] as const) {
    if (mode === 'broader') await page.getByRole('button', { name: 'Explore more', exact: true }).click();
    for (const [index, expected] of expectedPages[mode].entries()) {
      await expect.poll(() => identities(page)).toEqual(expected);
      const screen = active(page, mode === 'recommended' ? 'screen-recommended' : 'screen-explore');
      const rendered = `${await screen.innerText()}\n${await screen.ariaSnapshot()}`;
      for (const privateValue of [
        'alex@example.invalid', '1990-06-15', 'Fictional Harbor', 'demo_connection', 'demo_a',
        'demo_b', 'development-eligibility-1', 'development-preferences-1', 'source-discovery-',
        'fixture-chart-', 'mapping-1', 'birth-1', 'Fictional Paused', 'Fictional Deleted',
        'Fictional Restricted', 'Fictional BlockedOut', 'Fictional BlockedIn',
        'Fictional Nonreciprocal', 'Fictional UnknownMedia',
      ]) expect(rendered).not.toContain(privateValue);
      expect(rendered).not.toMatch(/\d+\s*%|compatibility score/i);
      await expect(screen).toContainText(/fictional/i);
      if (index < expectedPages[mode].length - 1) await active(page, 'discovery-next').click();
    }
  }
  expect(consoleText.join('\n')).not.toMatch(/alex@example\.invalid|1990-06-15|fixture-chart-|source-discovery-/);
});

test('ordinary completed private steps still cannot enter discovery with unresolved requirements', async ({ page }) => {
  await page.goto('/account');
  await active(page, 'account-email').fill('alex@example.invalid');
  await active(page, 'account-password').fill('fixture-passphrase');
  await active(page, 'account-submit').click();
  await active(page, 'verify-submit').click();
  await active(page, 'adult-date').fill('1990-06-15');
  await active(page, 'consent-checkbox').click();
  await active(page, 'eligibility-submit').click();
  await active(page, 'birth-place').fill('Fictional Harbor');
  await active(page, 'birth-submit').click();
  await expect(active(page, 'screen-remaining')).toBeVisible();
  await active(page, 'development-link').click();
  await active(page, 'return-current').click();
  await expect(active(page, 'screen-remaining')).toBeVisible();
  await expect(page.getByTestId('discovery-cards')).toHaveCount(0);
  await expect(page.getByText(/Make room for|More room to discover/)).toHaveCount(0);
});

test('320px enlarged discovery keeps labeled controls reachable and keyboard page focus stable', async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await eligibleDiscovery(page);
  await expect(page.getByRole('heading', { name: 'Make room for something real.', exact: true })).toBeFocused();
  await page.evaluate(() => {
    const sizes = Array.from(document.querySelectorAll<HTMLElement>('div, button')).map(node => [node, parseFloat(getComputedStyle(node).fontSize)] as const);
    for (const [node, size] of sizes) { node.style.fontSize = `${size * 2}px`; node.style.lineHeight = '1.4'; }
  });
  const next = active(page, 'discovery-next');
  await expect(next).toHaveAccessibleName('Next page');
  await expect(active(page, 'discovery-refresh')).toHaveAccessibleName('Refresh preview');
  for (const control of [next, active(page, 'discovery-refresh'), page.getByRole('button', { name: 'Explore more', exact: true })]) {
    await control.scrollIntoViewIfNeeded();
    await expect(control).toBeInViewport();
    const box = await control.boundingBox();
    expect(box).not.toBeNull();
    expect(box!.height).toBeGreaterThanOrEqual(44);
    expect(box!.x).toBeGreaterThanOrEqual(0);
    expect(box!.x + box!.width).toBeLessThanOrEqual(320);
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await next.scrollIntoViewIfNeeded();
  await next.focus();
  await page.keyboard.press('Enter');
  await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[1]);
  await expect(next).toBeFocused();
  await page.keyboard.press('Enter');
  await expect.poll(() => identities(page)).toEqual(expectedPages.recommended[2]);
  await expect(next).toBeDisabled();
  await expect(next).toBeFocused();
});
