import { expect, test, type Page } from '@playwright/test';

const password = 'fixture-passphrase';
// Native stacks retain hidden prior screens; interact with the active screen only.
const active = (page: Page, id: string) => page.getByTestId(id).filter({ visible: true });
test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status === testInfo.expectedStatus) return;
  // Only safe screen identities, never URLs, form values or private page snapshots.
  const screens = await page.locator('[data-testid^="screen-"]:visible').evaluateAll(nodes => nodes.map(node => node.getAttribute('data-testid'))).catch(() => []);
  console.info('Visible screen identities after failure:', screens);
  const birth = await page.evaluate(() => (window as typeof window & {
    __glowBirthDiagnostics?: { read: () => unknown };
  }).__glowBirthDiagnostics?.read() ?? null).catch(() => null);
  if (birth) console.info('Private birth interaction diagnostics after failure:', JSON.stringify(birth));
});

/** Observe only this fixture journey; never record field values, URLs, page text or private snapshots. */
async function observePrivateBirthJourney(page: Page) {
  await page.addInitScript(() => {
    const allowed = new Set(['screen-account', 'screen-verify', 'screen-eligibility', 'screen-birth', 'screen-remaining',
      'birth-date', 'birth-place', 'birth-time', 'birth-submit', 'time-known', 'time-approximate', 'time-unknown', 'edit-birth']);
    const events: Record<string, unknown>[] = [];
    const started = performance.now();
    const visible = (node: Element) => {
      const bounds = node.getBoundingClientRect(), style = getComputedStyle(node);
      return bounds.width > 0 && bounds.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
    };
    const controls = (id: string) => Array.from(document.querySelectorAll(`[data-testid="${id}"]`)).filter(visible);
    const identity = (node: EventTarget | null) => {
      if (!(node instanceof Element)) return 'other';
      const id = node.closest('[data-testid]')?.getAttribute('data-testid') ?? 'other';
      return allowed.has(id) ? id : 'other';
    };
    const field = (id: string, pattern?: RegExp) => controls(id).map(node => ({
      empty: node instanceof HTMLInputElement ? node.value.length === 0 : null,
      shapeValid: node instanceof HTMLInputElement && pattern ? pattern.test(node.value) : null,
    }));
    const state = () => {
      const alerts = Array.from(document.querySelectorAll('[role="alert"]')).filter(visible);
      const feedback = controls('feedback').map(node => node.textContent ?? '').join('\n');
      const messages: [string, string][] = [
        ['input_invalid', 'Check the civil birth date, time precision and place. Future dates are unavailable.'],
        ['eligibility_required', 'Complete current adult eligibility and consent first.'],
        ['source_stale', 'The fixture changed. Reload its current state and try again.'],
        ['adapter_unavailable', 'The fixture adapter is unavailable. You can retry.'],
        ['request_invalid', 'The synthetic request could not be completed. Check the fixture and try again.'],
        ['response_invalid', 'The adapter could not complete this request. Retry when available.'],
        ['birth_saved', 'Private synthetic birth input saved. Chart resolution and profile completion remain separate.'],
      ];
      return {
        screens: Array.from(document.querySelectorAll('[data-testid^="screen-"]')).filter(visible)
          .map(node => node.getAttribute('data-testid')).filter(id => id !== null && allowed.has(id)),
        focused: identity(document.activeElement),
        focusedHeading: document.activeElement?.getAttribute('role') === 'heading',
        date: field('birth-date', /^\d{4}-\d{2}-\d{2}$/), place: field('birth-place'),
        time: field('birth-time', /^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$/),
        precision: ['known', 'approximate', 'unknown'].filter(value => controls(`time-${value}`).some(node => node.getAttribute('aria-checked') === 'true')),
        submitDisabled: controls('birth-submit').map(node => node.getAttribute('aria-disabled') === 'true' || node.hasAttribute('disabled')),
        busy: Array.from(document.querySelectorAll('[role="progressbar"]')).some(visible), alert: alerts.length > 0,
        feedback: messages.filter(([, message]) => feedback.includes(message)).map(([code]) => code),
      };
    };
    const record = (entry: Record<string, unknown>) => {
      events.push({ atMs: Math.round(performance.now() - started), ...entry });
      if (events.length > 160) events.shift();
    };
    let lastState = '';
    const captureState = () => {
      const current = state(), signature = JSON.stringify(current);
      if (signature !== lastState) { lastState = signature; record({ event: 'state', ...current }); }
    };
    for (const kind of ['focusin', 'focusout', 'input', 'change', 'pointerdown', 'pointerup', 'pointercancel', 'click']) {
      document.addEventListener(kind, event => {
        const target = identity(event.target);
        if (target === 'other') return;
        record({ event: kind, target, trusted: event.isTrusted,
          ...(event instanceof MouseEvent ? { x: Math.round(event.clientX), y: Math.round(event.clientY) } : {}) });
        captureState();
      }, true);
    }
    let lastScroll = -Infinity;
    document.addEventListener('scroll', event => {
      if (controls('screen-birth').length === 0 || performance.now() - lastScroll < 50) return;
      lastScroll = performance.now();
      record({ event: 'scroll', target: identity(event.target), focused: identity(document.activeElement),
        top: event.target instanceof Element ? Math.round(event.target.scrollTop) : Math.round(window.scrollY) });
    }, { capture: true, passive: true });
    new MutationObserver(captureState).observe(document, { subtree: true, childList: true, characterData: true,
      attributes: true, attributeFilter: ['aria-disabled', 'aria-checked', 'style'] });
    (window as typeof window & { __glowBirthDiagnostics?: { read: () => unknown } }).__glowBirthDiagnostics = {
      read: () => ({ current: state(), events }),
    };
  });
}
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
  await observePrivateBirthJourney(page);
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
