import { expect, test, type Page } from '@playwright/test';

const password = 'fixture-passphrase';
// Native stacks retain hidden prior screens; interact with the active screen only.
const active = (page: Page, id: string) => page.getByTestId(id).filter({ visible: true });
test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status === testInfo.expectedStatus) return;
  // Only safe screen identities, never URLs, form values or private page snapshots.
  const screens = await page.locator('[data-testid^="screen-"]:visible').evaluateAll(nodes => nodes.map(node => node.getAttribute('data-testid'))).catch(() => []);
  console.info('Visible screen identities after failure:', screens);
});
async function account(page: Page, mode: 'register' | 'sign-in' = 'register') {
  await page.goto('/account');
  await active(page, `mode-${mode}`).click();
  await active(page, 'account-email').fill('alex@example.invalid');
  await active(page, 'account-password').fill(password);
  await active(page, 'account-submit').click();
  await expect(active(page, 'screen-verify')).toBeVisible();
}
async function outcome(page: Page, value: string) {
  if (!await active(page, `outcome-${value}`).isVisible()) await active(page, 'fixture-outcomes').click();
  await active(page, `outcome-${value}`).click();
}
async function backAfterLogout(page: Page, deniedRoute: '/remaining' | '/explore') {
  await expect(active(page, 'screen-account')).toBeVisible();
  await page.goBack();
  // Removing protected history may leave the one-page test's initial blank tab.
  // Returning through a formerly protected URL must still start signed out.
  if (page.url() === 'about:blank') await page.goto(deniedRoute);
  await expect(active(page, 'screen-account')).toBeVisible();
}
async function reachBirth(page: Page) {
  await account(page);
  await active(page, 'verify-submit').click();
  await expect(active(page, 'screen-eligibility')).toBeVisible();
  await active(page, 'adult-date').fill('1990-06-15');
  await active(page, 'consent-checkbox').click();
  await active(page, 'eligibility-submit').click();
  await expect(active(page, 'screen-birth')).toBeVisible();
}

test('register, reject an expired verification, resend, and accept adapter verification', async ({ page }) => {
  await account(page);
  await outcome(page, 'expired');
  await active(page, 'verify-submit').click();
  await expect(page.getByText(/synthetic challenge expired/i).filter({ visible: true })).toBeVisible();
  await expect(page.getByRole('alert')).toBeFocused();
  await expect(active(page, 'screen-verify')).toBeVisible();
  await outcome(page, 'success');
  await active(page, 'verify-resend').click();
  await active(page, 'verify-submit').click();
  await expect(active(page, 'screen-eligibility')).toBeVisible();
});

test('sign in and synthetic recovery remain separate; errors and neutral receipts are rendered', async ({ page }) => {
  await account(page, 'sign-in');
  await active(page, 'logout').click();
  await active(page, 'recover-access').click();
  await active(page, 'recovery-email').fill('unrelated@example.invalid');
  await outcome(page, 'rate_limited');
  await active(page, 'recovery-submit').click();
  await expect(page.getByText(/too many fixture attempts/i).filter({ visible: true })).toBeVisible();
  await outcome(page, 'success');
  await active(page, 'recovery-submit').click();
  await expect(page.getByText(/If this address can receive a recovery message/).filter({ visible: true })).toBeVisible();
  await active(page, 'open-reset').click();
  await outcome(page, 'wrong_context');
  await active(page, 'reset-password').fill(password);
  await active(page, 'reset-submit').click();
  await expect(active(page, 'screen-recovery')).toBeVisible();
  await expect(active(page, 'screen-reset-password')).toHaveCount(0);
  await expect(active(page, 'open-reset')).toHaveCount(0);
  await active(page, 'recovery-email').fill('unrelated@example.invalid');
  await active(page, 'recovery-submit').click();
  await active(page, 'open-reset').click();
  await active(page, 'reset-password').fill(password);
  await active(page, 'reset-submit').click();
  await expect(active(page, 'screen-account')).toBeVisible();
  await expect(active(page, 'account-password')).toHaveValue('');
});

test('direct private routes and malformed query destinations cannot bypass the account gate', async ({ page }) => {
  for (const route of ['/recommended', '/explore', '/birth', '/remaining', '/reset-password', '/verify?email=private-value']) {
    await test.step(`deny ${route}`, async () => {
      await page.goto(route);
      await expect(active(page, 'screen-account')).toBeVisible();
      await expect(page).toHaveURL(/\/account$/);
    });
    await expect(page.getByText('private-value', { exact: true })).toHaveCount(0);
  }
  for (const route of ['/_sitemap', '/unknown-destination?email=private-value#private-value']) {
    await test.step('unsupported link fallback', async () => {
      await page.goto(route);
      await expect(active(page, 'screen-link-unavailable')).toBeVisible();
      await expect(page.getByText('private-value', { exact: true })).toHaveCount(0);
      await active(page, 'return-current-step').click();
      await expect(active(page, 'screen-account')).toBeVisible();
      await expect(page).toHaveURL(/\/account$/);
    });
  }
});

test('private birth journey validates input, preserves uncertainty and stops before profile discovery', async ({ page }) => {
  await reachBirth(page);
  await active(page, 'birth-date').fill('2027-06-15');
  await active(page, 'birth-place').fill('Fictional Harbor');
  await active(page, 'birth-submit').click();
  await expect(page.getByText(/Check the civil birth date/).filter({ visible: true })).toBeVisible();
  await active(page, 'birth-date').fill('1990-06-15');
  await active(page, 'time-known').click();
  await active(page, 'birth-time').fill('09:42:00');
  await active(page, 'birth-submit').click();
  await expect(active(page, 'screen-remaining')).toBeVisible();
  await expect(page.getByText(/profile is still incomplete/).filter({ visible: true })).toBeVisible();
  await active(page, 'edit-birth').click();
  await expect(active(page, 'birth-time')).toHaveValue('09:42:00');
  await active(page, 'time-approximate').click();
  await active(page, 'birth-time').fill('09:30:00');
  await active(page, 'birth-submit').click();
  await expect(active(page, 'screen-remaining')).toBeVisible();
  await active(page, 'edit-birth').click();
  await expect(active(page, 'birth-time')).toHaveValue('09:30:00');
  await active(page, 'time-unknown').click();
  await expect(active(page, 'birth-time')).toHaveCount(0);
  await active(page, 'birth-outcomes').click();
  await active(page, 'resolution-unavailable').click();
  await active(page, 'birth-submit').click();
  await expect(active(page, 'screen-remaining')).toBeVisible();
  await expect(page.getByText('Birth resolution: unavailable. No chart has been calculated.').filter({ visible: true })).toBeVisible();
  await active(page, 'retry-resolution').click();
  await expect(page.getByText('Birth resolution: pending. No chart has been calculated.').filter({ visible: true })).toBeVisible();
  await active(page, 'checkpoint-save').click();
  await active(page, 'development-link').click();
  await active(page, 'checkpoint-restore').click();
  await expect(active(page, 'screen-remaining')).toBeVisible();
  await active(page, 'logout').click();
  await expect(active(page, 'screen-account')).toBeVisible();
  expect(await page.locator('input,textarea').evaluateAll(nodes => nodes.some(node => (node as HTMLInputElement).value === 'Fictional Harbor'))).toBe(false);
  await backAfterLogout(page, '/remaining');
  await expect(page.getByText('Fictional Harbor', { exact: true })).toHaveCount(0);
  expect(await page.locator('input,textarea').evaluateAll(nodes => nodes.some(node => (node as HTMLInputElement).value === 'Fictional Harbor'))).toBe(false);
});

test('programmatic birth form scrolling preserves input focus and subsequent private input', async ({ page }) => {
  await reachBirth(page);
  await active(page, 'birth-place').fill('Fictional Scroll Harbor');
  await active(page, 'time-known').click();
  const time = active(page, 'birth-time');
  await time.scrollIntoViewIfNeeded();
  const keptFocus = await time.evaluate(field => new Promise<boolean>((resolve, reject) => {
    type Responder = { scrollResponderHandleScroll: (event: unknown) => void };
    type ScrollNode = HTMLElement & { getScrollResponder?: () => Responder };
    let scroller = field.parentElement as ScrollNode | null;
    while (scroller && typeof scroller.getScrollResponder !== 'function') scroller = scroller.parentElement as ScrollNode | null;
    if (!(field instanceof HTMLInputElement) || !scroller?.getScrollResponder) {
      reject(new Error('Expected real fixture input and scroll responder.')); return;
    }
    const responder = scroller.getScrollResponder(), original = responder.scrollResponderHandleScroll;
    // Observe completion of the real handler, including its scroll-end debounce.
    // Do not replace _handleScroll, keyboard dismissal, focus handling or any app state.
    responder.scrollResponderHandleScroll = event => {
      responder.scrollResponderHandleScroll = original;
      original(event);
      resolve(document.activeElement === field);
    };
    field.focus({ preventScroll: true });
    scroller.scrollTop = scroller.scrollTop > 0 ? scroller.scrollTop - 1 : 1;
    scroller.dispatchEvent(new Event('scroll'));
  }));
  expect(keptFocus).toBe(true);
  await expect(time).toBeFocused();
  // Keyboard input goes to the retained active element; this does not refocus it.
  await page.keyboard.type('09:30:00');
  await expect(time).toHaveValue('09:30:00');
  await active(page, 'birth-submit').click();
  await expect(active(page, 'screen-remaining')).toBeVisible();
  await active(page, 'edit-birth').click();
  await expect(active(page, 'birth-time')).toHaveValue('09:30:00');
});

test('deferred screen and alert focus leaves a field someone already entered', async ({ page }) => {
  // Focus and select a field in the task that shows it, before the next animation frame,
  // as a fast person or input tool can. Screens, stores and focus handling stay real.
  const focusWhenShown = (shown: string, id: string) => page.evaluate(([selector, testId]) => {
    const visible = (node: Element) => node.getClientRects().length > 0;
    const observer = new MutationObserver(() => {
      const field = Array.from(document.querySelectorAll(`input[data-testid="${testId}"]`)).find(visible);
      if (!Array.from(document.querySelectorAll(selector)).some(visible) || !(field instanceof HTMLInputElement)) return;
      observer.disconnect();
      field.focus();
      field.select();
    });
    observer.observe(document.body, { subtree: true, childList: true, attributes: true });
  }, [shown, id] as const);
  const settleFrames = () => page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  await reachBirth(page);
  await focusWhenShown('input[data-testid="adult-date"]', 'adult-date');
  await active(page, 'birth-back').click();
  await expect(active(page, 'screen-eligibility')).toBeVisible();
  await settleFrames();
  await expect(active(page, 'adult-date')).toBeFocused();
  await page.keyboard.insertText('1992-07-16');
  await expect(active(page, 'adult-date')).toHaveValue('1992-07-16');
  await active(page, 'eligibility-submit').click();
  await expect(active(page, 'screen-birth')).toBeVisible();
  await active(page, 'birth-date').fill('2027-06-15');
  await active(page, 'birth-place').fill('Fictional Harbor');
  await focusWhenShown('[role="alert"]', 'birth-date');
  await active(page, 'birth-submit').click();
  await expect(page.getByText(/Check the civil birth date/).filter({ visible: true })).toBeVisible();
  await settleFrames();
  await expect(active(page, 'birth-date')).toBeFocused();
  await page.keyboard.insertText('1992-07-16');
  await expect(active(page, 'birth-date')).toHaveValue('1992-07-16');
  await active(page, 'birth-submit').click();
  await expect(active(page, 'screen-remaining')).toBeVisible();
});

test('an interrupted private form resumes within its session and clears on account switch', async ({ page }) => {
  await reachBirth(page);
  await active(page, 'birth-place').fill('Private Draft Island');
  await active(page, 'birth-back').click();
  await active(page, 'eligibility-submit').click();
  await expect(active(page, 'birth-place')).toHaveValue('Private Draft Island');
  await active(page, 'logout').click();
  await active(page, 'account-email').fill('sam@example.invalid');
  await active(page, 'account-password').fill(password);
  await active(page, 'account-submit').click();
  await active(page, 'verify-submit').click();
  await active(page, 'adult-date').fill('1991-07-14');
  await active(page, 'consent-checkbox').click();
  await active(page, 'eligibility-submit').click();
  await expect(active(page, 'birth-place')).toHaveValue('');
  expect(await page.locator('input,textarea').evaluateAll(nodes => nodes.some(node => (node as HTMLInputElement).value === 'Private Draft Island'))).toBe(false);
});

test('restricted and policy scenarios deny discovery; explicit eligible preview revokes on logout', async ({ page }) => {
  await page.goto('/development');
  for (const scenario of ['underage', 'unknown_policy', 'stale_consent', 'withdrawn_consent', 'suspended', 'deletion_pending']) {
    await active(page, `scenario-${scenario}`).click();
    const screen = ['suspended', 'deletion_pending'].includes(scenario) ? 'restricted' : 'eligibility';
    await expect(active(page, `screen-${screen}`)).toBeVisible();
    expect(await page.locator('input,textarea').evaluateAll(nodes => nodes.some(node => (node as HTMLInputElement).value === '1988-02-03'))).toBe(false);
    if (screen === 'eligibility') {
      await expect(active(page, 'adult-date')).toHaveValue(scenario === 'underage' ? '2010-09-23' : '1990-06-15');
      await expect(active(page, 'consent-checkbox')).toHaveAttribute('aria-checked', scenario === 'underage' ? 'true' : 'false');
      await active(page, 'adult-date').fill('1988-02-03');
    }
    await expect(page.getByText('Make room for', { exact: false })).toHaveCount(0);
    await active(page, 'development-link').click();
  }
  await active(page, 'scenario-eligible').click();
  await expect(page.getByText(/Make room for/).filter({ visible: true })).toBeVisible();
  await page.getByRole('button', { name: 'Explore more', exact: true }).click();
  await expect(page.getByText('More room to discover.').filter({ visible: true })).toBeVisible();
  await active(page, 'logout').click();
  await expect(active(page, 'screen-account')).toBeVisible();
  await expect(page.getByText('More room to discover.')).toHaveCount(0);
  await backAfterLogout(page, '/explore');
  await expect(page.getByText('More room to discover.')).toHaveCount(0);
});

test('small-screen and enlarged-text account interaction remains labeled and reachable', async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await page.goto('/account');
  await expect(page.getByRole('heading')).toBeFocused();
  await expect(page.getByRole('textbox', { name: 'Fixture email address', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Create fixture account', exact: true })).toBeVisible();
  await page.evaluate(() => {
    const sizes = Array.from(document.querySelectorAll<HTMLElement>('div, input, button')).map(el => [el, parseFloat(getComputedStyle(el).fontSize)] as const);
    for (const [el, size] of sizes) { el.style.fontSize = `${size * 2}px`; el.style.lineHeight = '1.4'; }
  });
  await active(page, 'account-submit').scrollIntoViewIfNeeded();
  await expect(active(page, 'account-submit')).toBeInViewport();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  // Empty form only: evidence contains no birth values, account email or credentials.
  await page.screenshot({ path: testInfo.outputPath('account-320-enlarged.png'), fullPage: true });
});
