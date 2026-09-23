import { expect, test, type Page } from '@playwright/test';

// These journeys use the actual screens and memory fixture. Full-page navigation
// starts a fresh fixture instance; retained-state assertions use in-app navigation.
const active = (page: Page, id: string) => page.getByTestId(id).filter({ visible: true });

test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status === testInfo.expectedStatus) return;
  const screens = await page.locator('[data-testid^="screen-"]:visible').evaluateAll(nodes => nodes.map(node => node.getAttribute('data-testid'))).catch(() => []);
  console.info('Visible screen identities after failure:', screens);
});

async function completePrivateSteps(page: Page, email = 'alex@example.invalid') {
  await active(page, 'account-email').fill(email);
  await active(page, 'account-password').fill('fixture-passphrase');
  await active(page, 'account-submit').click();
  await active(page, 'verify-submit').click();
  await active(page, 'adult-date').fill('1990-06-15');
  await active(page, 'consent-checkbox').click();
  await active(page, 'eligibility-submit').click();
  await active(page, 'birth-place').fill('Fictional Harbor');
  await active(page, 'birth-submit').click();
  await expect(active(page, 'screen-remaining')).toBeVisible();
}

async function ordinaryProfile(page: Page) {
  await page.goto('/account');
  await completePrivateSteps(page);
  await active(page, 'open-profile').click();
  await expect(active(page, 'screen-profile')).toBeVisible();
}

async function eligibleProfile(page: Page) {
  await page.goto('/development');
  await active(page, 'scenario-eligible').click();
  await expect(page.getByText(/Make room for/).filter({ visible: true })).toBeVisible();
  await active(page, 'open-profile').click();
  await expect(active(page, 'screen-profile')).toBeVisible();
}

async function profileOutcome(page: Page, outcome: string) {
  if (!await active(page, `profile-outcome-${outcome}`).isVisible()) await active(page, 'profile-outcomes').click();
  await active(page, `profile-outcome-${outcome}`).click();
}

async function noInputContains(page: Page, value: string) {
  expect(await page.locator('input,textarea').evaluateAll((nodes, expected) => nodes.some(node => (node as HTMLInputElement).value.includes(expected)), value)).toBe(false);
}

async function savedProfile(page: Page) {
  await expect(page.getByText('Profile saved for this session.', { exact: true }).filter({ visible: true })).toBeVisible();
  await expect(active(page, 'profile-draft-status')).toHaveText('Matches your saved profile');
  await active(page, 'profile-leave').click();
  await expect(active(page, 'screen-profile')).toBeVisible();
}

async function savedPreferences(page: Page) {
  await expect(page.getByText('Preferences saved for this session.', { exact: true }).filter({ visible: true })).toBeVisible();
  await expect(active(page, 'preferences-draft-status')).toHaveText('Matches your saved preferences');
  await active(page, 'preferences-leave').click();
  await expect(active(page, 'screen-profile')).toBeVisible();
}

test('ordinary onboarding saves an incomplete profile, restores a draft, cancels and retries an edit', async ({ page }) => {
  await ordinaryProfile(page);
  await active(page, 'profile-edit').click();
  await active(page, 'profile-name').fill('   ');
  await active(page, 'profile-save').click();
  await expect(page.getByRole('alert').filter({ visible: true })).toBeVisible();
  await expect(page.getByRole('alert').filter({ visible: true })).toBeFocused();
  await active(page, 'profile-name').fill('Fictional Ember');
  await active(page, 'profile-summary').fill('');
  await active(page, 'profile-save').click();
  await savedProfile(page);
  await expect(active(page, 'profile-status')).toContainText('incomplete');
  await expect(page.getByText(/Make room for/)).toHaveCount(0);

  await active(page, 'profile-edit').click();
  await expect(active(page, 'profile-name')).toHaveValue('Fictional Ember');
  await expect(active(page, 'profile-summary')).toHaveValue('');
  await active(page, 'profile-summary').fill('A deliberately unfinished fictional introduction.');
  await active(page, 'profile-leave').click();
  await active(page, 'profile-edit').click();
  await expect(active(page, 'profile-summary')).toHaveValue('A deliberately unfinished fictional introduction.');
  await active(page, 'profile-cancel').click();
  await active(page, 'profile-edit').click();
  await expect(active(page, 'profile-summary')).toHaveValue('');

  await active(page, 'profile-summary').fill('A fictional introduction saved after a temporary error.');
  await profileOutcome(page, 'error');
  await active(page, 'profile-save').click();
  await expect(page.getByRole('alert').filter({ visible: true })).toBeVisible();
  await expect(active(page, 'profile-summary')).toHaveValue('A fictional introduction saved after a temporary error.');
  await profileOutcome(page, 'success');
  await active(page, 'profile-save').click();
  await savedProfile(page);
  await expect(active(page, 'profile-status')).toContainText('incomplete');
  await active(page, 'profile-edit').click();
  await expect(active(page, 'profile-summary')).toHaveValue('A fictional introduction saved after a temporary error.');
});

test('provisional preferences support interruption, cancel and retry without completing ordinary eligibility', async ({ page }) => {
  await ordinaryProfile(page);
  await active(page, 'preferences-edit').click();
  await active(page, 'pref-demo_connection-demo_a').click();
  await active(page, 'preferences-leave').click();
  await active(page, 'preferences-edit').click();
  await expect(active(page, 'pref-demo_connection-demo_a')).toHaveAttribute('aria-checked', 'true');
  await active(page, 'preferences-cancel').click();
  await active(page, 'preferences-edit').click();
  await expect(active(page, 'pref-demo_connection-demo_a')).toHaveAttribute('aria-checked', 'false');
  await active(page, 'pref-demo_connection-demo_b').click();
  await profileOutcome(page, 'error');
  await active(page, 'preferences-save').click();
  await expect(page.getByRole('alert').filter({ visible: true })).toBeVisible();
  await expect(active(page, 'pref-demo_connection-demo_b')).toHaveAttribute('aria-checked', 'true');
  await profileOutcome(page, 'success');
  await active(page, 'preferences-save').click();
  await savedPreferences(page);
  await expect(active(page, 'profile-status')).toContainText('incomplete');
  await expect(page.getByText(/Make room for/)).toHaveCount(0);
  await active(page, 'preferences-edit').click();
  await expect(active(page, 'pref-demo_connection-demo_b')).toHaveAttribute('aria-checked', 'true');
});

test('a retained profile form reconciles a changed source without wiping unrelated deliberate edits', async ({ page }) => {
  await eligibleProfile(page);
  await active(page, 'profile-edit').click();
  await expect(active(page, 'profile-name')).toHaveValue('Alex');
  await active(page, 'profile-name').fill('Deliberately edited fictional name');
  await active(page, 'development-link').click();
  // This count proves an actual retained form exists; a full reload would not
  // test the source-reconciliation behavior or retain the current fixture.
  await expect(page.getByTestId('profile-name')).toHaveCount(1);
  await expect(active(page, 'profile-name')).toHaveCount(0);
  await active(page, 'dev-profile-change').click();
  await page.goBack();
  await expect(active(page, 'screen-profile-edit')).toBeVisible();
  await expect(active(page, 'profile-name')).toHaveValue('Deliberately edited fictional name');
  await expect(active(page, 'profile-summary')).toHaveValue('A newer fictional biography.');
  await active(page, 'profile-save').click();
  await savedProfile(page);
  await active(page, 'profile-edit').click();
  await expect(active(page, 'profile-name')).toHaveValue('Deliberately edited fictional name');
  await expect(active(page, 'profile-summary')).toHaveValue('A newer fictional biography.');
});

test('a retained untouched preference form refreshes when the authoritative selection changes', async ({ page }) => {
  await eligibleProfile(page);
  await active(page, 'preferences-edit').click();
  await expect(active(page, 'pref-demo_connection-demo_a')).toHaveAttribute('aria-checked', 'true');
  await active(page, 'development-link').click();
  await expect(page.getByTestId('pref-demo_connection-demo_a')).toHaveCount(1);
  await expect(active(page, 'pref-demo_connection-demo_a')).toHaveCount(0);
  await active(page, 'dev-preferences-change').click();
  // Revoking discovery prunes its earlier protected history entry. Assert the
  // original hidden form before using an explicit same-session return route.
  await expect(page.getByTestId('pref-demo_connection-demo_a')).toHaveAttribute('aria-checked', 'false');
  await expect(page.getByTestId('pref-demo_connection-demo_b')).toHaveAttribute('aria-checked', 'true');
  await active(page, 'dev-profile-return').click();
  await active(page, 'preferences-edit').click();
  await expect(active(page, 'screen-preferences')).toBeVisible();
  await expect(active(page, 'pref-demo_connection-demo_a')).toHaveAttribute('aria-checked', 'false');
  await expect(active(page, 'pref-demo_connection-demo_b')).toHaveAttribute('aria-checked', 'true');
  await active(page, 'preferences-save').click();
  await savedPreferences(page);
});

test('fictional eligible profile pauses, edits while paused, resumes and rechecks lost media evidence', async ({ page }) => {
  await eligibleProfile(page);
  await expect(active(page, 'profile-status')).toContainText('visible');
  await active(page, 'profile-pause').click();
  await expect(active(page, 'profile-status')).toContainText('paused');
  // Protected discovery screens must be removed, including hidden stack entries.
  await expect(page.getByText(/Make room for/)).toHaveCount(0);
  await active(page, 'profile-edit').click();
  await active(page, 'profile-summary').fill('Edited in the paused fictional profile.');
  await active(page, 'profile-save').click();
  await savedProfile(page);
  await expect(active(page, 'profile-status')).toContainText('paused');
  await active(page, 'profile-resume').click();
  await expect(active(page, 'profile-status')).toContainText('visible');
  await active(page, 'profile-pause').click();
  // Source controls intentionally cancel pending work. Exercise loss of media
  // after the pause has actually committed, rather than cancelling the pause.
  await expect(active(page, 'profile-status')).toContainText('paused');
  await active(page, 'development-link').click();
  await active(page, 'dev-media-change').click();
  await page.goBack();
  await expect(active(page, 'screen-profile')).toBeVisible();
  await active(page, 'profile-resume').click();
  await expect(page.getByRole('alert').filter({ visible: true })).toBeVisible();
  await expect(active(page, 'profile-status')).toContainText('paused');
  await expect(page.getByText(/Make room for/)).toHaveCount(0);
});

for (const evidence of ['policy', 'reciprocal']) {
  test(`changing ${evidence} evidence invalidates retained discovery without a reload`, async ({ page }) => {
    await eligibleProfile(page);
    await expect(page.getByText(/Make room for/)).toHaveCount(1);
    await active(page, 'development-link').click();
    await active(page, `dev-${evidence}-change`).click();
    await expect(page.getByText(/Make room for/)).toHaveCount(0);
    await expect(page.getByTestId('profile-status')).toContainText('Visibility: incomplete');
    await active(page, 'dev-profile-return').click();
    await expect(active(page, 'screen-profile')).toBeVisible();
    await expect(active(page, 'profile-status')).toContainText('Visibility: incomplete');
    // Establish a fresh in-app history entry after protected history pruning;
    // Back must reach the current owner state and cannot revive discovery.
    await active(page, 'profile-preview').click();
    await expect(active(page, 'candidate-unavailable')).toBeVisible();
    await page.goBack();
    await expect(active(page, 'screen-profile')).toBeVisible();
    await expect(active(page, 'profile-status')).toContainText('Visibility: incomplete');
    await expect(page.getByText(/Make room for/)).toHaveCount(0);
  });
}

test('eligible candidate preview contains only public text and retracts from a retained screen', async ({ page }) => {
  await eligibleProfile(page);
  await active(page, 'profile-preview').click();
  const candidate = active(page, 'candidate-preview');
  await expect(candidate).toBeVisible();
  await expect(candidate).toContainText('Alex, 36');
  await expect(candidate).toContainText('A fictional profile for the visibility demonstration.');
  for (const privateText of ['alex@example.invalid', '1990-06-15', 'Fictional Harbor', 'demo_connection', 'demo_a', 'development-preferences-1']) {
    await expect(candidate).not.toContainText(privateText);
  }
  await active(page, 'development-link').click();
  await expect(page.getByTestId('candidate-preview')).toHaveCount(1);
  await expect(candidate).toHaveCount(0);
  await active(page, 'dev-media-change').click();
  await expect(page.getByTestId('candidate-preview')).toHaveCount(0);
  // Check the original retained owner preview before opening another route.
  await expect(page.getByTestId('owner-preview')).toHaveCount(1);
  await expect(page.getByTestId('owner-preview')).toContainText('Visibility: incomplete');
  await expect(page.getByTestId('candidate-unavailable')).toHaveCount(1);
  await active(page, 'dev-profile-return').click();
  await active(page, 'profile-preview').click();
  await expect(active(page, 'screen-profile-preview')).toBeVisible();
  await expect(active(page, 'owner-preview')).toBeVisible();
  await expect(active(page, 'candidate-unavailable')).toBeVisible();
  await page.goBack();
  await expect(active(page, 'screen-profile')).toBeVisible();
  await expect(active(page, 'profile-status')).toContainText('Visibility: incomplete');
  await expect(page.getByTestId('candidate-preview')).toHaveCount(0);
});

test('an invalid profile response cannot reappear as saved data after refresh', async ({ page }) => {
  await ordinaryProfile(page);
  await active(page, 'profile-edit').click();
  await active(page, 'profile-name').fill('Rejected fictional response');
  await active(page, 'profile-summary').fill('This value must never become an accepted profile.');
  await profileOutcome(page, 'malformed');
  await active(page, 'profile-save').click();
  await expect(page.getByRole('alert').filter({ visible: true })).toBeVisible();
  await active(page, 'profile-cancel').click();
  await expect(active(page, 'profile-status')).toContainText('No profile has been saved yet.');
  await active(page, 'profile-reload').click();
  await expect(page.getByText('Current saved values loaded. Review your draft before saving.', { exact: true }).filter({ visible: true })).toBeVisible();
  await expect(active(page, 'profile-status')).toContainText('No profile has been saved yet.');
  await active(page, 'profile-edit').click();
  await expect(active(page, 'profile-name')).toHaveValue('');
  await expect(active(page, 'profile-summary')).toHaveValue('');
  await noInputContains(page, 'Rejected fictional response');
});

test('a version conflict preserves the draft and accepted profile until a reviewed retry', async ({ page }) => {
  await eligibleProfile(page);
  await active(page, 'profile-edit').click();
  await active(page, 'profile-summary').fill('A fictional revision after a version conflict.');
  await profileOutcome(page, 'stale');
  await active(page, 'profile-save').click();
  await expect(page.getByRole('alert').filter({ visible: true })).toBeVisible();
  await active(page, 'profile-leave').click();
  await expect(active(page, 'profile-status')).toContainText('A fictional profile for the visibility demonstration.');
  await expect(active(page, 'profile-status')).not.toContainText('A fictional revision after a version conflict.');
  await active(page, 'profile-edit').click();
  await expect(active(page, 'profile-summary')).toHaveValue('A fictional revision after a version conflict.');
  await profileOutcome(page, 'success');
  await active(page, 'profile-edit-reload').click();
  await expect(page.getByText('Current saved values loaded. Review your draft before saving.', { exact: true }).filter({ visible: true })).toBeVisible();
  await expect(active(page, 'profile-summary')).toHaveValue('A fictional revision after a version conflict.');
  await active(page, 'profile-save').click();
  await savedProfile(page);
  await expect(active(page, 'profile-status')).toContainText('A fictional revision after a version conflict.');
});

test('session expiry removes retained profile fields and discovery before any fresh navigation', async ({ page }) => {
  await eligibleProfile(page);
  await active(page, 'profile-edit').click();
  await active(page, 'profile-summary').fill('Private fictional draft before expiry.');
  await active(page, 'development-link').click();
  await expect(page.getByTestId('profile-summary')).toHaveCount(1);
  await active(page, 'session-expire').click();
  await expect(active(page, 'screen-account')).toBeVisible();
  await noInputContains(page, 'Private fictional draft before expiry.');
  await expect(page.getByTestId('screen-profile-edit')).toHaveCount(0);
  await expect(page.getByText(/Make room for/)).toHaveCount(0);
});

test('new private profile routes deny signed-out entry and discard private URL data', async ({ page }) => {
  for (const route of ['/profile', '/profile-edit', '/preferences', '/profile-preview']) {
    await page.goto(route);
    await expect(active(page, 'screen-account')).toBeVisible();
    await expect(page).toHaveURL(/\/account$/);
    await page.goto(`${route}?summary=private-sentinel#private-sentinel`);
    await expect(active(page, 'screen-account')).toBeVisible();
    await expect(page).toHaveURL(/\/account$/);
    await expect(page.getByText('private-sentinel', { exact: true })).toHaveCount(0);
  }
});

test('logout and account switching remove unsaved profile values from visible and retained screens', async ({ page }) => {
  await ordinaryProfile(page);
  await active(page, 'profile-edit').click();
  await active(page, 'profile-name').fill('Previous owner fictional name');
  await active(page, 'profile-summary').fill('Previous owner fictional private draft.');
  await active(page, 'profile-leave').click();
  await active(page, 'logout').click();
  await expect(active(page, 'screen-account')).toBeVisible();
  await noInputContains(page, 'Previous owner');
  await completePrivateSteps(page, 'sam@example.invalid');
  await active(page, 'open-profile').click();
  await active(page, 'profile-edit').click();
  await expect(active(page, 'profile-name')).toHaveValue('');
  await expect(active(page, 'profile-summary')).toHaveValue('');
  await noInputContains(page, 'Previous owner');
  await active(page, 'logout').click();
  await page.goBack();
  if (page.url() === 'about:blank') await page.goto('/profile-edit');
  await expect(active(page, 'screen-account')).toBeVisible();
  await noInputContains(page, 'Previous owner');
});

test('empty profile form remains labeled and usable at 320px with doubled text', async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await ordinaryProfile(page);
  await active(page, 'profile-edit').click();
  await expect(active(page, 'profile-name')).toHaveValue('');
  await expect(active(page, 'profile-summary')).toHaveValue('');
  await expect(active(page, 'profile-name')).toHaveAccessibleName(/display name/i);
  await expect(active(page, 'profile-summary')).toHaveAccessibleName(/biography/i);
  await page.evaluate(() => {
    const sizes = Array.from(document.querySelectorAll<HTMLElement>('div, input, textarea, button')).map(el => [el, parseFloat(getComputedStyle(el).fontSize)] as const);
    for (const [el, size] of sizes) { el.style.fontSize = `${size * 2}px`; el.style.lineHeight = '1.4'; }
  });
  await active(page, 'profile-save').scrollIntoViewIfNeeded();
  await expect(active(page, 'profile-save')).toBeInViewport();
  await active(page, 'profile-cancel').scrollIntoViewIfNeeded();
  await expect(active(page, 'profile-cancel')).toBeInViewport();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await active(page, 'profile-name').scrollIntoViewIfNeeded();
  // Only the unpopulated active owner form is pictured. No birth/account values,
  // credentials, populated preferences or traces are captured.
  await page.screenshot({ path: testInfo.outputPath('profile-empty-320-enlarged.png'), fullPage: true });
});
