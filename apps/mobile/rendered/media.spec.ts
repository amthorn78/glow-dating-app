import { expect, test, type Page } from '@playwright/test';
import { syntheticSelection } from '../src/media/policy';

// Actual screen journeys. Actor/permission controls are explicitly synthetic.
// In-app navigation preserves this process; no full reload proves restoration.
const active = (page: Page, id: string) => page.getByTestId(id).filter({ visible: true });
const status = (page: Page, asset: string) => active(page, `media-status-${asset}`);
async function ordinaryMedia(page: Page) {
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
  await active(page, 'open-profile').click();
  await active(page, 'profile-media').click();
  await expect(active(page, 'screen-media')).toBeVisible();
}
async function eligibleMedia(page: Page) {
  await page.goto('/development');
  await active(page, 'scenario-eligible').click();
  await active(page, 'open-profile').click();
  await active(page, 'profile-media').click();
  await expect(active(page, 'screen-media')).toBeVisible();
}
async function fixtures(page: Page) {
  if (!await active(page, 'media-select-valid').isVisible()) await active(page, 'media-fixtures').click();
}
async function outcome(page: Page, value: string) {
  await fixtures(page);
  await active(page, `media-outcome-${value}`).click();
}
async function assets(page: Page): Promise<string[]> {
  return active(page, 'media-collection').locator('[data-testid^="media-item-"]').evaluateAll(nodes => nodes.map(node => node.getAttribute('data-testid')!.slice('media-item-'.length)));
}
async function prepare(page: Page) {
  const before = await assets(page);
  await fixtures(page);
  await active(page, 'media-select-valid').click();
  await active(page, 'media-prepare').click();
  await expect.poll(async () => (await assets(page)).length).toBe(before.length + 1);
  const id = (await assets(page)).find(item => !before.includes(item))!;
  await expect(status(page, id)).toHaveText('Upload pending');
  return id;
}
async function approve(page: Page, id: string) {
  await active(page, `media-upload-${id}`).click();
  await expect(status(page, id)).toHaveText('Quarantined');
  await fixtures(page);
  await active(page, `media-review-${id}`).click();
  await expect(status(page, id)).toHaveText('Review pending');
  await active(page, `media-approve-${id}`).click();
  await expect(status(page, id)).toHaveText('Approved');
}

test('empty media, synthetic permission choices, invalid content and bounded real PNG selection', async ({ page }) => {
  await ordinaryMedia(page);
  await expect(active(page, 'media-empty')).toBeVisible();
  await fixtures(page);
  for (const permission of ['denied', 'limited', 'cancelled']) {
    await active(page, `media-picker-${permission}`).click();
    await expect(active(page, 'media-selection')).toHaveCount(0);
    await expect(active(page, 'media-empty')).toBeVisible();
  }
  for (const kind of ['invalid', 'unsupported', 'truncated', 'oversize', 'pixels']) {
    await active(page, `media-select-${kind}`).click();
    await expect(page.getByRole('alert').filter({ visible: true })).toHaveText('This image is unsupported, invalid or exceeds the development limits.');
    await expect(active(page, 'media-selection')).toHaveCount(0);
  }
  // System web picker delivers an actual synthetic PNG File, not a permission simulation.
  const chooserPromise = page.waitForEvent('filechooser');
  await active(page, 'media-picker').click();
  const chooser = await chooserPromise;
  await chooser.setFiles({ name: 'private-source-location.png', mimeType: 'image/png', buffer: Buffer.from(syntheticSelection().bytes) });
  await expect(active(page, 'media-selection')).toContainText('Selected photo');
  await expect(active(page, 'screen-media')).not.toContainText('private-source-location');
  await active(page, 'media-prepare').click();
  await expect.poll(async () => (await assets(page)).length).toBe(1);
  const id = (await assets(page))[0]!;
  await approve(page, id);
  await expect(active(page, 'media-owner-controls').getByRole('button', { name: /approve|purge/i })).toHaveCount(0);
  await active(page, 'media-profile').click();
  await expect(active(page, 'profile-requirements')).toContainText('Resolved Human Design inputs');
  await expect(active(page, 'profile-effective-visibility')).toContainText('Visibility: incomplete');
});

for (const uploadOutcome of ['error', 'interrupted', 'wrong_object']) test(`upload ${uploadOutcome} retries the same asset without skipping quarantine and review`, async ({ page }) => {
  await ordinaryMedia(page);
  const id = await prepare(page);
  await outcome(page, uploadOutcome);
  await active(page, `media-upload-${id}`).click();
  await expect(page.getByRole('alert').filter({ visible: true })).toBeVisible();
  await expect(status(page, id)).toHaveText('Upload pending');
  await outcome(page, 'success');
  await approve(page, id);
  expect(await assets(page)).toEqual([id]);
});

test('review rejection, removal, failed purge and provider retry retain exact lifecycle feedback', async ({ page }) => {
  await ordinaryMedia(page);
  const id = await prepare(page);
  await active(page, `media-upload-${id}`).click();
  await expect(status(page, id)).toHaveText('Quarantined');
  await active(page, `media-review-${id}`).click();
  await expect(status(page, id)).toHaveText('Review pending');
  await active(page, `media-reject-${id}`).click();
  await expect(status(page, id)).toHaveText('Rejected');
  await active(page, `media-remove-${id}`).click();
  await expect(status(page, id)).toHaveText('Removal pending');
  await outcome(page, 'error');
  await active(page, `media-purge-${id}`).click();
  await expect(page.getByRole('alert').filter({ visible: true })).toBeVisible();
  await expect(status(page, id)).toHaveText('Removal pending');
  await outcome(page, 'success');
  await active(page, `media-purge-${id}`).click();
  await expect(status(page, id)).toHaveText('Removed');
  const replacement = await prepare(page);
  expect(replacement).not.toBe(id);
  await approve(page, replacement);
});

test('accessible earlier and later controls reorder the complete approved collection', async ({ page }) => {
  await ordinaryMedia(page);
  const first = await prepare(page); await approve(page, first);
  const second = await prepare(page); await approve(page, second);
  await expect(active(page, `media-position-${first}`)).toHaveText('Approved position 1');
  await expect(active(page, `media-earlier-${first}`)).toBeDisabled();
  await active(page, `media-earlier-${second}`).click();
  await expect(active(page, `media-position-${second}`)).toHaveText('Approved position 1');
  await expect(active(page, `media-position-${first}`)).toHaveText('Approved position 2');
  await active(page, `media-later-${second}`).click();
  await expect(active(page, `media-position-${first}`)).toHaveText('Approved position 1');
});

test('same-session interruption keeps pending work and cancellation prevents late completion', async ({ page }) => {
  await ordinaryMedia(page);
  const id = await prepare(page);
  await active(page, 'media-profile').click();
  await expect(page.getByTestId(`media-status-${id}`)).toHaveCount(1);
  await active(page, 'profile-media').click();
  await expect(status(page, id)).toHaveText('Upload pending');
  await active(page, `media-upload-${id}`).click();
  await active(page, `media-cancel-${id}`).click();
  await expect(status(page, id)).toHaveText('Removal pending');
  await active(page, 'media-reload').click();
  await expect(status(page, id)).toHaveText('Removal pending');
});

test('cancelling a selection while its grant is preparing leaves no hidden asset', async ({ page }) => {
  await ordinaryMedia(page);
  await fixtures(page);
  await active(page, 'media-select-valid').click();
  await active(page, 'media-prepare').click();
  await active(page, 'media-selection-cancel').click();
  await expect(active(page, 'media-selection')).toHaveCount(0);
  await active(page, 'media-reload').click();
  await expect(active(page, 'media-empty')).toBeVisible();
});

test('malformed prepare with no assets is rejected and reload cannot revive hidden state', async ({ page }) => {
  await ordinaryMedia(page);
  await fixtures(page);
  await active(page, 'media-select-valid').click();
  await outcome(page, 'malformed');
  await active(page, 'media-prepare').click();
  await expect(page.getByRole('alert').filter({ visible: true })).toBeVisible();
  await expect(active(page, 'media-empty')).toBeVisible();
  await outcome(page, 'success');
  await active(page, 'media-reload').click();
  await expect(active(page, 'media-empty')).toBeVisible();
  await active(page, 'media-prepare').click();
  await expect.poll(async () => (await assets(page)).length).toBe(1);
});

test('last approved photo removal immediately revokes retained candidate preview', async ({ page }) => {
  await eligibleMedia(page);
  const id = (await assets(page))[0]!;
  await active(page, 'media-profile').click();
  await active(page, 'profile-preview').click();
  await expect(active(page, 'candidate-preview')).toBeVisible();
  await active(page, 'development-link').click();
  await active(page, 'dev-profile-return').click();
  await active(page, 'profile-media').click();
  await expect(page.getByTestId('candidate-preview')).toHaveCount(1);
  await active(page, `media-remove-${id}`).click();
  await expect(status(page, id)).toHaveText('Removal pending');
  await expect(page.getByTestId('candidate-preview')).toHaveCount(0);
  await active(page, 'media-profile').click();
  await expect(active(page, 'profile-effective-visibility')).toContainText('Visibility: blocked');
  await expect(active(page, 'profile-discovery')).toHaveCount(0);
});

for (const removeOutcome of ['error', 'malformed']) test(`owner removal ${removeOutcome} stays private through moderator reapproval and purge retry`, async ({ page }) => {
  await eligibleMedia(page);
  const id = (await assets(page))[0]!;
  await active(page, 'media-profile').click();
  await active(page, 'profile-preview').click();
  await expect(active(page, 'candidate-preview')).toBeVisible();
  await expect(active(page, 'candidate-photo-0')).toBeVisible();
  await active(page, 'development-link').click();
  await active(page, 'dev-profile-return').click();
  await active(page, 'profile-media').click();
  // The original candidate stays mounted; a fresh page would erase this regression.
  await expect(page.getByTestId('candidate-preview')).toHaveCount(1);
  await outcome(page, removeOutcome);
  await active(page, `media-remove-${id}`).click();
  await expect(page.getByRole('alert').filter({ visible: true })).toBeVisible();
  await expect(status(page, id)).toHaveText('Approved');
  await expect(page.getByTestId('candidate-preview')).toHaveCount(0);
  await expect(page.getByTestId('candidate-photo-0')).toHaveCount(0);
  await expect(page.getByTestId('candidate-unavailable')).toHaveCount(1);

  await outcome(page, 'success');
  await active(page, `media-restrict-${id}`).click();
  await expect(status(page, id)).toHaveText('Review pending');
  await active(page, `media-approve-${id}`).click();
  await expect(status(page, id)).toHaveText('Approved');
  // Moderator approval cannot undo the owner's still-pending removal intent.
  await expect(page.getByTestId('candidate-preview')).toHaveCount(0);
  await expect(page.getByTestId('candidate-photo-0')).toHaveCount(0);
  await expect(page.getByTestId('owner-preview').getByTestId('profile-effective-visibility')
    .getByText('Visibility: blocked', { exact: true })).toHaveCount(1);
  await active(page, 'media-reload').click();
  await expect(page.getByText('Current photo status loaded.', { exact: true }).filter({ visible: true })).toBeVisible();
  await expect(status(page, id)).toHaveText('Approved');
  await expect(page.getByTestId('candidate-unavailable')).toHaveCount(1);

  await active(page, `media-remove-${id}`).click();
  await expect(status(page, id)).toHaveText('Removal pending');
  await active(page, `media-purge-${id}`).click();
  await expect(status(page, id)).toHaveText('Removed');
  await expect(page.getByTestId('candidate-preview')).toHaveCount(0);
  await expect(page.getByTestId('candidate-photo-0')).toHaveCount(0);
});

test('pause survives media changes and fresh resume denies missing approved photos', async ({ page }) => {
  await eligibleMedia(page);
  const id = (await assets(page))[0]!;
  await active(page, 'media-profile').click();
  await active(page, 'profile-pause').click();
  await expect(active(page, 'profile-effective-visibility')).toContainText('Visibility: paused');
  await active(page, 'profile-media').click();
  await active(page, `media-remove-${id}`).click();
  await expect(status(page, id)).toHaveText('Removal pending');
  await active(page, 'media-profile').click();
  await expect(active(page, 'profile-effective-visibility')).toContainText('Visibility: paused');
  await active(page, 'profile-resume').click();
  await expect(page.getByRole('alert').filter({ visible: true })).toBeVisible();
  await expect(active(page, 'profile-effective-visibility')).toContainText('Visibility: paused');
});

test('advancing the actual fixture clock expires a grant and success cannot revive it', async ({ page }) => {
  await ordinaryMedia(page);
  const id = await prepare(page);
  await active(page, 'media-clock-expire').click();
  await active(page, `media-upload-${id}`).click();
  await expect(page.getByRole('alert').filter({ visible: true })).toBeVisible();
  await expect(status(page, id)).toHaveText('Upload pending');
  await active(page, `media-upload-${id}`).click();
  await expect(page.getByRole('alert').filter({ visible: true })).toBeVisible();
  await expect(status(page, id)).toHaveText('Upload pending');
});

test('logout clears selection and retained media; a new session has an empty collection', async ({ page }) => {
  await ordinaryMedia(page);
  const id = await prepare(page);
  await active(page, 'logout').click();
  await expect(active(page, 'screen-account')).toBeVisible();
  await expect(page.getByTestId(`media-status-${id}`)).toHaveCount(0);
  await expect(page.getByTestId('media-selection')).toHaveCount(0);
  await active(page, 'account-email').fill('sam@example.invalid');
  await active(page, 'account-password').fill('fixture-passphrase');
  await active(page, 'account-submit').click();
  await active(page, 'verify-submit').click();
  await active(page, 'adult-date').fill('1990-06-15');
  await active(page, 'consent-checkbox').click();
  await active(page, 'eligibility-submit').click();
  await active(page, 'birth-place').fill('Another fictional place');
  await active(page, 'birth-submit').click();
  await active(page, 'open-profile').click();
  await active(page, 'profile-media').click();
  await expect(active(page, 'media-empty')).toBeVisible();
});

test('320px doubled text keeps media actions reachable without horizontal clipping', async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 700 });
  await ordinaryMedia(page);
  const id = await prepare(page); await approve(page, id);
  await page.evaluate(() => {
    document.querySelectorAll<HTMLElement>('[data-testid="screen-media"] div').forEach(node => {
      if (node.childElementCount === 0 && node.textContent?.trim()) {
        const style = getComputedStyle(node);
        node.style.fontSize = `${parseFloat(style.fontSize) * 2}px`;
        node.style.lineHeight = '1.45';
      }
    });
  });
  const buttons = active(page, 'screen-media').getByRole('button');
  const bounds = await buttons.evaluateAll(nodes => nodes.map(node => { const b = node.getBoundingClientRect(); return { x: b.x, right: b.right, width: b.width, height: b.height }; }));
  for (const bound of bounds) { expect(bound.x).toBeGreaterThanOrEqual(0); expect(bound.right).toBeLessThanOrEqual(320); expect(bound.height).toBeGreaterThanOrEqual(48); }
  await active(page, `media-remove-${id}`).click();
  await expect(status(page, id)).toHaveText('Removal pending');
});
