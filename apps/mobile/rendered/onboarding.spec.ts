import { expect, test, type Page } from '@playwright/test';

const password = 'fixture-passphrase';
async function account(page: Page, mode: 'register' | 'sign-in' = 'register') {
  await page.goto('/account');
  await page.getByTestId(`mode-${mode}`).click();
  await page.getByTestId('account-email').fill('alex@example.invalid');
  await page.getByTestId('account-password').fill(password);
  await page.getByTestId('account-submit').click();
  await expect(page.getByTestId('screen-verify')).toBeVisible();
}
async function outcome(page: Page, value: string) {
  if (!await page.getByTestId(`outcome-${value}`).isVisible()) await page.getByTestId('fixture-outcomes').click();
  await page.getByTestId(`outcome-${value}`).click();
}
async function reachBirth(page: Page) {
  await account(page);
  await page.getByTestId('verify-submit').click();
  await expect(page.getByTestId('screen-eligibility')).toBeVisible();
  await page.getByTestId('adult-date').fill('1990-06-15');
  await page.getByTestId('consent-checkbox').click();
  await page.getByTestId('eligibility-submit').click();
  await expect(page.getByTestId('screen-birth')).toBeVisible();
}

test('register, reject an expired verification, resend, and accept adapter verification', async ({ page }) => {
  await account(page);
  await outcome(page, 'expired');
  await page.getByTestId('verify-submit').click();
  await expect(page.getByText(/synthetic challenge expired/i)).toBeVisible();
  await expect(page.getByTestId('screen-verify')).toBeVisible();
  await outcome(page, 'success');
  await page.getByTestId('verify-resend').click();
  await page.getByTestId('verify-submit').click();
  await expect(page.getByTestId('screen-eligibility')).toBeVisible();
});

test('sign in and synthetic recovery remain separate; errors and neutral receipts are rendered', async ({ page }) => {
  await account(page, 'sign-in');
  await page.getByTestId('logout').click();
  await page.getByTestId('recover-access').click();
  await page.getByTestId('recovery-email').fill('unrelated@example.invalid');
  await outcome(page, 'rate_limited');
  await page.getByTestId('recovery-submit').click();
  await expect(page.getByText(/too many fixture attempts/i)).toBeVisible();
  await outcome(page, 'success');
  await page.getByTestId('recovery-submit').click();
  await expect(page.getByText(/If this address can receive a recovery message/)).toBeVisible();
  await page.getByTestId('open-reset').click();
  await outcome(page, 'wrong_context');
  await page.getByTestId('reset-password').fill(password);
  await page.getByTestId('reset-submit').click();
  await expect(page.getByTestId('screen-account')).toBeVisible();
  await page.getByTestId('recover-access').click();
  await page.getByTestId('recovery-email').fill('unrelated@example.invalid');
  await page.getByTestId('recovery-submit').click();
  await page.getByTestId('open-reset').click();
  await page.getByTestId('reset-password').fill(password);
  await page.getByTestId('reset-submit').click();
  await expect(page.getByTestId('screen-account')).toBeVisible();
  await expect(page.getByTestId('account-password')).toHaveValue('');
});

test('direct private routes and malformed query destinations cannot bypass the account gate', async ({ page }) => {
  for (const route of ['/recommended', '/explore', '/birth', '/remaining', '/reset-password', '/verify?email=private-value', '/unknown-destination']) {
    await page.goto(route);
    await expect(page.getByTestId('screen-account')).toBeVisible();
    await expect(page.getByText('private-value', { exact: true })).toHaveCount(0);
  }
});

test('private birth journey validates input, preserves uncertainty and stops before profile discovery', async ({ page }) => {
  await reachBirth(page);
  await page.getByTestId('birth-date').fill('2027-06-15');
  await page.getByTestId('birth-place').fill('Fictional Harbor');
  await page.getByTestId('birth-submit').click();
  await expect(page.getByText(/Check the civil birth date/)).toBeVisible();
  await page.getByTestId('birth-date').fill('1990-06-15');
  await page.getByTestId('time-known').click();
  await page.getByTestId('birth-time').fill('09:42:00');
  await page.getByTestId('birth-submit').click();
  await expect(page.getByTestId('screen-remaining')).toBeVisible();
  await expect(page.getByText(/profile is still incomplete/)).toBeVisible();
  await page.getByTestId('edit-birth').click();
  await expect(page.getByTestId('birth-time')).toHaveValue('09:42:00');
  await page.getByTestId('time-approximate').click();
  await page.getByTestId('birth-time').fill('09:30:00');
  await page.getByTestId('birth-submit').click();
  await expect(page.getByTestId('screen-remaining')).toBeVisible();
  await page.getByTestId('edit-birth').click();
  await expect(page.getByTestId('birth-time')).toHaveValue('09:30:00');
  await page.getByTestId('time-unknown').click();
  await expect(page.getByTestId('birth-time')).toHaveCount(0);
  await page.getByTestId('birth-outcomes').click();
  await page.getByTestId('resolution-unavailable').click();
  await page.getByTestId('birth-submit').click();
  await expect(page.getByTestId('screen-remaining')).toBeVisible();
  await expect(page.getByText('Birth resolution: unavailable. No chart has been calculated.')).toBeVisible();
  await page.getByTestId('retry-resolution').click();
  await expect(page.getByText('Birth resolution: pending. No chart has been calculated.')).toBeVisible();
  await page.getByTestId('checkpoint-save').click();
  await page.getByTestId('development-link').click();
  await page.getByTestId('checkpoint-restore').click();
  await expect(page.getByTestId('screen-remaining')).toBeVisible();
  await page.getByTestId('logout').click();
  await page.goBack();
  await expect(page.getByTestId('screen-account')).toBeVisible();
  await expect(page.getByText('Fictional Harbor', { exact: true })).toHaveCount(0);
});

test('an interrupted private form resumes within its session and clears on account switch', async ({ page }) => {
  await reachBirth(page);
  await page.getByTestId('birth-place').fill('Private Draft Island');
  await page.getByTestId('birth-back').click();
  await page.getByTestId('eligibility-submit').click();
  await expect(page.getByTestId('birth-place')).toHaveValue('Private Draft Island');
  await page.getByTestId('logout').click();
  await page.getByTestId('account-email').fill('sam@example.invalid');
  await page.getByTestId('account-password').fill(password);
  await page.getByTestId('account-submit').click();
  await page.getByTestId('verify-submit').click();
  await page.getByTestId('adult-date').fill('1991-07-14');
  await page.getByTestId('consent-checkbox').click();
  await page.getByTestId('eligibility-submit').click();
  await expect(page.getByTestId('birth-place')).toHaveValue('');
});

test('restricted and policy scenarios deny discovery; explicit eligible preview revokes on logout', async ({ page }) => {
  await page.goto('/development');
  for (const scenario of ['underage', 'unknown_policy', 'stale_consent', 'withdrawn_consent', 'suspended', 'deletion_pending']) {
    await page.getByTestId(`scenario-${scenario}`).click();
    const screen = ['suspended', 'deletion_pending'].includes(scenario) ? 'restricted' : 'eligibility';
    await expect(page.getByTestId(`screen-${screen}`)).toBeVisible();
    await expect(page.getByText('Make room for', { exact: false })).toHaveCount(0);
    await page.getByTestId('development-link').click();
  }
  await page.getByTestId('scenario-eligible').click();
  await expect(page.getByText(/Make room for/)).toBeVisible();
  await page.getByRole('button', { name: 'Explore more', exact: true }).click();
  await expect(page.getByText('More room to discover.')).toBeVisible();
  await page.getByTestId('logout').click();
  await page.goBack();
  await expect(page.getByTestId('screen-account')).toBeVisible();
  await expect(page.getByText('More room to discover.')).toHaveCount(0);
});

test('small-screen and enlarged-text account interaction remains labeled and reachable', async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await page.goto('/account');
  await expect(page.getByRole('textbox', { name: 'Fixture email address', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Create fixture account', exact: true })).toBeVisible();
  await page.evaluate(() => {
    const sizes = Array.from(document.querySelectorAll<HTMLElement>('div, input, button')).map(el => [el, parseFloat(getComputedStyle(el).fontSize)] as const);
    for (const [el, size] of sizes) { el.style.fontSize = `${size * 2}px`; el.style.lineHeight = '1.4'; }
  });
  await page.getByTestId('account-submit').scrollIntoViewIfNeeded();
  await expect(page.getByTestId('account-submit')).toBeInViewport();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  // Empty form only: evidence contains no birth values, account email or credentials.
  await page.screenshot({ path: testInfo.outputPath('account-320-enlarged.png'), fullPage: true });
});
