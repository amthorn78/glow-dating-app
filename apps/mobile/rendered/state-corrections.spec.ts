import { expect, test, type Page } from '@playwright/test';

const active = (page: Page, id: string) => page.getByTestId(id).filter({ visible: true });
test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status === testInfo.expectedStatus) return;
  const screens = await page.locator('[data-testid^="screen-"]:visible').evaluateAll(nodes => nodes.map(node => node.getAttribute('data-testid'))).catch(() => []);
  console.info('Visible screen identities after failure:', screens);
  // Diagnose a failed retained-form transition without logging any entered data.
  // Counts/booleans distinguish missing controls, disabled submission and blank
  // drafts; alert presence does not expose provider text or private values.
  const birthDiagnostics = await page.evaluate(() => {
    const visible = (node: Element) => {
      const rect = node.getBoundingClientRect();
      const style = getComputedStyle(node);
      return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
    };
    const controls = (testId: string) => Array.from(document.querySelectorAll(`[data-testid="${testId}"]`)).filter(visible);
    const submissions = controls('birth-submit');
    const fieldState = (testId: string) => controls(testId).map(node => ({
      empty: node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement ? node.value.length === 0 : null,
    }));
    return {
      submitCount: submissions.length,
      submitDisabled: submissions.map(node => node.getAttribute('aria-disabled') === 'true' || node.hasAttribute('disabled')),
      dateFields: fieldState('birth-date'),
      placeFields: fieldState('birth-place'),
      visibleAlertPresent: Array.from(document.querySelectorAll('[role="alert"]')).some(visible),
    };
  }).catch(() => null);
  console.info('Private birth control diagnostics after failure:', birthDiagnostics);
});
async function reachBirth(page: Page) {
  await page.goto('/account');
  await active(page, 'account-email').fill('alex@example.invalid');
  await active(page, 'account-password').fill('fixture-passphrase');
  await active(page, 'account-submit').click();
  await active(page, 'verify-submit').click();
  await active(page, 'adult-date').fill('1990-06-15');
  await active(page, 'consent-checkbox').click();
  await active(page, 'eligibility-submit').click();
  await expect(active(page, 'screen-birth')).toBeVisible();
}

for (const saved of [true, false]) {
  test(`eligibility correction replaces an obsolete ${saved ? 'accepted' : 'unsaved'} birth draft`, async ({ page }) => {
    await reachBirth(page);
    await active(page, 'birth-date').fill('1990-06-15');
    await active(page, 'birth-place').fill('Discarded Fictional Harbor');
    if (saved) {
      await active(page, 'birth-submit').click();
      await active(page, 'review-eligibility').click();
    } else {
      await active(page, 'birth-back').click();
    }
    await active(page, 'adult-date').fill('1992-07-16');
    await active(page, 'eligibility-submit').click();
    await expect(active(page, 'screen-birth')).toBeVisible();
    await expect(active(page, 'birth-date')).not.toHaveValue('1990-06-15');
    await expect(active(page, 'birth-place')).not.toHaveValue('Discarded Fictional Harbor');
    // A no-edit submission cannot undo the correction, even if the empty form rejects it.
    await active(page, 'birth-submit').click();
    await active(page, 'birth-back').click();
    await expect(active(page, 'adult-date')).toHaveValue('1992-07-16');
    await active(page, 'eligibility-submit').click();
    await active(page, 'birth-date').fill('1992-07-16');
    await active(page, 'birth-place').fill('Current Fictional Harbor');
    await active(page, 'birth-submit').click();
    await expect(active(page, 'screen-remaining')).toBeVisible();
    await active(page, 'review-eligibility').click();
    await expect(active(page, 'adult-date')).toHaveValue('1992-07-16');
  });
}

for (const retained of [false, true]) {
  test(`underage birth correction reconciles eligibility (${retained ? 'retained history' : 'ordinary return'})`, async ({ page }) => {
    await reachBirth(page);
    if (retained) {
      await active(page, 'birth-back').click();
      await active(page, 'development-link').click();
      await active(page, 'return-current').click();
      await expect(active(page, 'screen-birth')).toBeVisible();
      // Establish the suspected route lifetime, not just a fresh eligibility mount.
      await expect(page.getByTestId('adult-date')).toHaveCount(1);
      await expect(active(page, 'adult-date')).toHaveCount(0);
    }
    await active(page, 'birth-date').fill('2010-09-23');
    await active(page, 'birth-place').fill('Underage Fictional Harbor');
    await active(page, 'birth-submit').click();
    await expect(active(page, 'screen-eligibility')).toBeVisible();
    await expect(active(page, 'adult-date')).toHaveValue('2010-09-23');
    await active(page, 'eligibility-submit').click();
    await expect(active(page, 'screen-eligibility')).toBeVisible();
    await expect(active(page, 'adult-date')).toHaveValue('2010-09-23');
    await expect(page.getByText(/Current age check: fail/).filter({ visible: true })).toBeVisible();
    if (retained) {
      await page.goBack();
      if (page.url() === 'about:blank') {
        // Protected history removal may exhaust this test's app entries, as in
        // the original logout test. Re-entry must still deny the private route.
        await page.goto('/birth');
        await expect(active(page, 'screen-account')).toBeVisible();
        console.info('Retained eligibility Back exhausted app history; fresh private entry denied.');
      } else {
        if (await active(page, 'screen-development').isVisible()) await active(page, 'return-current').click();
        await expect(active(page, 'screen-eligibility')).toBeVisible();
        await expect(active(page, 'adult-date')).toHaveValue('2010-09-23');
        console.info('Retained eligibility Back preserved the corrected authoritative date.');
      }
    }
  });
}

test('same-task birth input events preserve both fields in a retained correction', async ({ page }) => {
  await reachBirth(page);
  await active(page, 'birth-back').click();
  await active(page, 'development-link').click();
  await active(page, 'return-current').click();
  await expect(active(page, 'screen-birth')).toBeVisible();
  await expect(page.getByTestId('adult-date')).toHaveCount(1);
  await expect(active(page, 'adult-date')).toHaveCount(0);
  // Exercise the real controlled inputs in one browser task. The native setter
  // bypasses React's DOM value tracker so both bubbling input events reach the
  // normal onChangeText callbacks; no fixture store or component state is edited.
  await active(page, 'screen-birth').evaluate(screen => {
    const setValue = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
    if (!setValue) throw new Error('Native input setter unavailable.');
    for (const [id, value] of [
      ['birth-date', '2010-09-23'],
      ['birth-place', 'Same-task Fictional Harbor'],
    ]) {
      const field = screen.querySelector(`[data-testid="${id}"]`);
      if (!(field instanceof HTMLInputElement)) throw new Error('Expected birth input missing.');
      setValue.call(field, value);
      field.dispatchEvent(new InputEvent('input', { bubbles: true, composed: true, inputType: 'insertReplacementText', data: value }));
    }
  });
  await expect(active(page, 'birth-date')).toHaveValue('2010-09-23');
  await expect(active(page, 'birth-place')).toHaveValue('Same-task Fictional Harbor');
  await active(page, 'birth-submit').click();
  await expect(active(page, 'screen-eligibility')).toBeVisible();
  await expect(active(page, 'adult-date')).toHaveValue('2010-09-23');
  await active(page, 'eligibility-submit').click();
  await expect(active(page, 'screen-eligibility')).toBeVisible();
  await expect(active(page, 'adult-date')).toHaveValue('2010-09-23');
  await expect(page.getByText(/Current age check: fail/).filter({ visible: true })).toBeVisible();
});

test('retained eligibility consent cannot silently restore withdrawn consent', async ({ page }) => {
  await reachBirth(page);
  await active(page, 'birth-back').click();
  await active(page, 'development-link').click();
  await active(page, 'return-current').click();
  await active(page, 'birth-back').click();
  await active(page, 'consent-withdraw').click();
  await expect(active(page, 'consent-checkbox')).toHaveAttribute('aria-checked', 'false');
  for (const checkbox of await page.getByTestId('consent-checkbox').all()) {
    await expect(checkbox).toHaveAttribute('aria-checked', 'false');
  }
  await active(page, 'development-link').click();
  await active(page, 'return-current').click();
  await expect(active(page, 'screen-eligibility')).toBeVisible();
  await expect(active(page, 'consent-checkbox')).toHaveAttribute('aria-checked', 'false');
  await active(page, 'eligibility-submit').click();
  await expect(active(page, 'screen-eligibility')).toBeVisible();
  await expect(page.getByText(/Consent: withdrawn/).filter({ visible: true })).toBeVisible();
});

test('eligibility preserves deliberate edits when only another authoritative field changes', async ({ page }) => {
  await reachBirth(page);
  await active(page, 'birth-back').click();
  await active(page, 'adult-date').fill('1993-08-17');
  await active(page, 'checkpoint-save').click();
  await expect(active(page, 'adult-date')).toHaveValue('1993-08-17');
  await active(page, 'consent-withdraw').click();
  await expect(active(page, 'consent-checkbox')).toHaveAttribute('aria-checked', 'false');
  await expect(active(page, 'adult-date')).toHaveValue('1993-08-17');
  await active(page, 'consent-checkbox').click();
  await active(page, 'eligibility-submit').click();
  await expect(active(page, 'screen-birth')).toBeVisible();
  await active(page, 'birth-back').click();
  await expect(active(page, 'adult-date')).toHaveValue('1993-08-17');
});

for (const scenario of ['suspended', 'deletion_pending']) {
  test(`expired ${scenario} session reaches sign-in and preserves the account restriction`, async ({ page }) => {
    await page.goto('/development');
    await active(page, `scenario-${scenario}`).click();
    await expect(active(page, 'screen-restricted')).toBeVisible();
    await active(page, 'development-link').click();
    await active(page, 'session-expire').click();
    await expect(active(page, 'screen-account')).toBeVisible();
    // Authenticate before any possible full page reload, preserving this fixture instance.
    await active(page, 'mode-sign-in').click();
    await active(page, 'account-email').fill('alex@example.invalid');
    await active(page, 'account-password').fill('fixture-passphrase');
    await active(page, 'account-submit').click();
    await expect(active(page, 'screen-restricted')).toBeVisible();
    await expect(page.getByText(/Make room for/)).toHaveCount(0);
    await active(page, 'development-link').click();
    await expect(active(page, 'checkpoint-restore')).toBeDisabled();
    await active(page, 'session-expire').click();
    await expect(active(page, 'screen-account')).toBeVisible();
    await page.goBack();
    if (page.url() === 'about:blank') await page.goto('/restricted');
    if (await active(page, 'screen-development').isVisible()) await active(page, 'return-current').click();
    await expect(active(page, 'screen-account')).toBeVisible();
    // These full-page URLs separately prove fresh signed-out entry. Store tests
    // also deny every protected route against the still-expired snapshot.
    for (const path of ['/restricted', '/birth', '/remaining', '/recommended', '/explore']) {
      await page.goto(path);
      await expect(active(page, 'screen-account')).toBeVisible();
      await expect(page).toHaveURL(/\/account$/);
    }
  });
}

test('expired verification remains expired after selecting success until resend', async ({ page }) => {
  await page.goto('/account');
  await active(page, 'account-email').fill('alex@example.invalid');
  await active(page, 'account-password').fill('fixture-passphrase');
  await active(page, 'account-submit').click();
  await expect(active(page, 'screen-verify')).toBeVisible();
  await active(page, 'fixture-outcomes').click();
  await active(page, 'outcome-expired').click();
  await active(page, 'verify-submit').click();
  await expect(page.getByText(/synthetic challenge expired/i).filter({ visible: true })).toBeVisible();
  await active(page, 'outcome-success').click();
  await active(page, 'verify-submit').click();
  await expect(page.getByText(/synthetic challenge expired/i).filter({ visible: true })).toBeVisible();
  await expect(active(page, 'screen-verify')).toBeVisible();
  await active(page, 'verify-resend').click();
  await active(page, 'verify-submit').click();
  await expect(active(page, 'screen-eligibility')).toBeVisible();
});
