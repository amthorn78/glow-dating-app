import { expect, test, type Page } from '@playwright/test';

const active = (page: Page, id: string) => page.getByTestId(id).filter({ visible: true });
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
      await expect(active(page, 'screen-eligibility')).toBeVisible();
      await expect(active(page, 'adult-date')).toHaveValue('2010-09-23');
    }
  });
}

test('retained eligibility consent cannot silently restore withdrawn consent', async ({ page }) => {
  await reachBirth(page);
  await active(page, 'birth-back').click();
  await active(page, 'development-link').click();
  await active(page, 'return-current').click();
  await active(page, 'birth-back').click();
  await active(page, 'consent-withdraw').click();
  await expect(active(page, 'consent-checkbox')).toHaveAttribute('aria-checked', 'false');
  await page.goBack();
  await expect(active(page, 'screen-eligibility')).toBeVisible();
  await expect(active(page, 'consent-checkbox')).toHaveAttribute('aria-checked', 'false');
  await active(page, 'eligibility-submit').click();
  await expect(active(page, 'screen-eligibility')).toBeVisible();
  await expect(page.getByText(/Consent: withdrawn/).filter({ visible: true })).toBeVisible();
});

for (const scenario of ['suspended', 'deletion_pending']) {
  test(`expired ${scenario} session reaches sign-in and preserves the account restriction`, async ({ page }) => {
    await page.goto('/development');
    await active(page, `scenario-${scenario}`).click();
    await expect(active(page, 'screen-restricted')).toBeVisible();
    await active(page, 'development-link').click();
    await active(page, 'session-expire').click();
    await expect(active(page, 'screen-account')).toBeVisible();
    await page.goBack();
    if (page.url() === 'about:blank') await page.goto('/restricted');
    // Development can remain in history; its ordinary return must require sign-in.
    if (await active(page, 'screen-development').isVisible()) await active(page, 'return-current').click();
    await expect(active(page, 'screen-account')).toBeVisible();
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
