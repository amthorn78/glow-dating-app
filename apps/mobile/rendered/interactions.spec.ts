import { expect, test, type Page } from '@playwright/test';

const active = (page: Page, id: string) => page.getByTestId(id).filter({ visible: true });
const matchRows = (page: Page) => active(page, 'match-list').locator('[data-testid^="match-row-"]');

async function eligible(page: Page) {
  await page.goto('/development');
  await active(page, 'scenario-eligible').click();
  await expect(active(page, 'screen-recommended')).toBeVisible();
  await expect(active(page, 'like-profile-jules')).toBeEnabled();
}

async function development(page: Page) {
  await active(page, 'development-link').click();
  await expect(active(page, 'screen-development')).toBeVisible();
}

async function setDelivery(page: Page, value: 'normal' | 'offline' | 'lost_response' | 'delayed') {
  await development(page);
  await active(page, `interaction-scenario-${value}`).click();
  await active(page, 'return-current').click();
  await expect(active(page, 'screen-recommended')).toBeVisible();
}

async function reciprocal(page: Page) {
  await development(page);
  await active(page, 'interaction-reciprocal').click();
  await active(page, 'return-current').click();
  await expect(active(page, 'screen-recommended')).toBeVisible();
}

async function mutual(page: Page) {
  await eligible(page);
  await reciprocal(page);
  // A command by the other participant cannot advertise a unilateral like.
  await expect(active(page, 'discovery-card-profile-jules')).toBeVisible();
  await expect(active(page, 'discovery-card-profile-jules')).not.toContainText(/liked you|reciprocal|mutual match/i);
  await active(page, 'like-profile-jules').click();
  await expect(active(page, 'interaction-feedback')).toContainText(/mutual match/i);
  await active(page, 'open-matches').click();
  await expect(matchRows(page)).toHaveCount(1);
  await expect(matchRows(page).first()).toContainText('Mutual match');
}

test('a committed own like stays consumed across modes and refresh without creating a unilateral match', async ({ page }) => {
  await eligible(page);
  await active(page, 'like-profile-jules').click();
  await expect(active(page, 'interaction-feedback')).toContainText(/like saved|liked|like committed/i);
  await expect(active(page, 'like-profile-jules')).toHaveCount(0);
  await page.getByRole('button', { name: 'Explore more', exact: true }).click();
  await expect(active(page, 'like-profile-iris')).toBeEnabled();
  await expect(active(page, 'like-profile-jules')).toHaveCount(0);
  await active(page, 'discovery-refresh').click();
  await expect(active(page, 'like-profile-iris')).toBeEnabled();
  await expect(active(page, 'like-profile-jules')).toHaveCount(0);
  await active(page, 'open-matches').click();
  await expect(matchRows(page)).toHaveCount(0);
  await expect(active(page, 'matches-empty')).toContainText('No mutual matches yet');
});

test('a committed pass is not undone by refresh or the other discovery mode', async ({ page }) => {
  await eligible(page);
  await active(page, 'pass-profile-jules').click();
  await expect(active(page, 'interaction-feedback')).toContainText(/pass saved|passed|pass committed/i);
  await active(page, 'discovery-refresh').click();
  await expect(active(page, 'like-profile-morgan')).toBeEnabled();
  await expect(active(page, 'discovery-card-profile-jules')).toHaveCount(0);
  await page.getByRole('button', { name: 'Explore more', exact: true }).click();
  await expect(active(page, 'like-profile-iris')).toBeEnabled();
  await expect(active(page, 'discovery-card-profile-jules')).toHaveCount(0);
});

test('two committed fictional likes produce one participant match and a safe detail with no messaging grant', async ({ page }) => {
  await mutual(page);
  await page.getByRole('button', { name: 'View match with Fictional Jules', exact: true }).click();
  await expect(active(page, 'screen-match')).toBeVisible();
  await expect(active(page, 'match-detail')).toContainText('You both liked each other');
  await expect(active(page, 'match-detail')).toContainText('Messaging is unavailable');
  await expect(active(page, 'match-unmatch')).toBeEnabled();
  await expect(active(page, 'match-detail')).not.toContainText(/birth_date|birth_time|chart_id|demo_connection|engine_reference|fixture-passphrase/);
  await expect(page.getByRole('button', { name: /send message|start chat/i })).toHaveCount(0);
});

test('the opposite arrival order forms the same single match through the command setup', async ({ page }) => {
  await eligible(page);
  await active(page, 'like-profile-jules').click();
  await expect(active(page, 'interaction-feedback')).toContainText(/like saved|liked|like committed/i);
  await reciprocal(page);
  await active(page, 'open-matches').click();
  await expect(matchRows(page)).toHaveCount(1);
  await expect(matchRows(page).first()).toContainText('Mutual match');
  await active(page, 'matches-refresh').click();
  await expect(matchRows(page)).toHaveCount(1);
});

test('unmatch retracts the retained profile and never restores contact after refresh or unblock', async ({ page }) => {
  await mutual(page);
  await page.getByRole('button', { name: 'View match with Fictional Jules', exact: true }).click();
  await active(page, 'match-unmatch').click();
  await expect(active(page, 'match-detail')).toContainText('You are unmatched');
  await expect(active(page, 'match-detail')).not.toContainText('Jules');
  await expect(active(page, 'match-unmatch')).toHaveCount(0);
  await development(page);
  await active(page, 'interaction-block').click();
  await active(page, 'interaction-unblock').click();
  await active(page, 'open-matches').click();
  await expect(matchRows(page)).toHaveCount(1);
  await expect(matchRows(page).first()).toContainText('Unmatched');
  await expect(matchRows(page).first()).not.toContainText('Mutual match');
});

test('an active participant can unmatch while paused and the restricted detail exposes no former profile', async ({ page }) => {
  await mutual(page);
  await active(page, 'open-profile').click();
  await active(page, 'profile-pause').click();
  await expect(active(page, 'profile-resume')).toBeVisible();
  await active(page, 'open-matches').click();
  await expect(matchRows(page)).toHaveCount(1);
  await expect(matchRows(page).first()).toContainText('Connection unavailable');
  await page.getByRole('button', { name: 'View connection status', exact: true }).click();
  await expect(active(page, 'match-detail')).not.toContainText('Jules');
  await expect(active(page, 'match-unmatch')).toBeEnabled();
  await active(page, 'match-unmatch').click();
  await expect(active(page, 'match-detail')).toContainText('You are unmatched');
});

test('blocking purges retained match details and unblocking does not restore a mutual match', async ({ page }) => {
  await mutual(page);
  await page.getByRole('button', { name: 'View match with Fictional Jules', exact: true }).click();
  await expect(active(page, 'match-detail')).toContainText('Jules');
  await development(page);
  await active(page, 'interaction-block').click();
  // Hidden retained projections must retract, not merely disappear on navigation.
  await expect(page.getByTestId('match-detail')).not.toContainText('Jules');
  await active(page, 'interaction-unblock').click();
  await active(page, 'open-matches').click();
  await expect(matchRows(page)).toHaveCount(1);
  await expect(matchRows(page).first()).toContainText('Connection unavailable');
  await expect(matchRows(page).first()).not.toContainText('Mutual match');
});

test('offline error remains an error, focuses feedback, and retries the same current intent', async ({ page }) => {
  await eligible(page);
  await setDelivery(page, 'offline');
  await active(page, 'like-profile-jules').click();
  await expect(active(page, 'interaction-result')).toHaveAttribute('role', 'alert');
  await expect(active(page, 'interaction-result')).toBeFocused();
  await expect(active(page, 'interaction-retry')).toBeEnabled();
  await setDelivery(page, 'normal');
  await active(page, 'interaction-retry').click();
  await expect(active(page, 'interaction-feedback')).toContainText(/like saved|liked|like committed/i);
  await expect(active(page, 'like-profile-jules')).toHaveCount(0);
  await active(page, 'open-matches').click();
  await expect(matchRows(page)).toHaveCount(0);
});

test('lost response reconciles consumption and recovers the original result without a second actionable card', async ({ page }) => {
  await eligible(page);
  await setDelivery(page, 'lost_response');
  await active(page, 'like-profile-jules').click();
  await expect(active(page, 'interaction-retry')).toBeEnabled();
  await expect(active(page, 'like-profile-jules')).toHaveCount(0);
  await setDelivery(page, 'normal');
  await active(page, 'interaction-retry').click();
  await expect(active(page, 'interaction-feedback')).toContainText(/like saved|liked|like committed/i);
  await expect(active(page, 'like-profile-jules')).toHaveCount(0);
  await active(page, 'open-matches').click();
  await expect(matchRows(page)).toHaveCount(0);
});

test('delayed double activation keeps pending focus and announces committed status only after completion at 320px', async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await eligible(page);
  await setDelivery(page, 'delayed');
  await page.evaluate(() => {
    const sizes = Array.from(document.querySelectorAll<HTMLElement>('div, button')).map(node => [node, parseFloat(getComputedStyle(node).fontSize)] as const);
    for (const [node, size] of sizes) { node.style.fontSize = `${size * 2}px`; node.style.lineHeight = '1.4'; }
  });
  const like = active(page, 'like-profile-jules');
  await like.scrollIntoViewIfNeeded();
  await expect(like).toHaveAccessibleName('Like Fictional Jules');
  const box = await like.boundingBox();
  expect(box!.height).toBeGreaterThanOrEqual(44);
  expect(box!.x).toBeGreaterThanOrEqual(0);
  expect(box!.x + box!.width).toBeLessThanOrEqual(320);
  await like.focus();
  await page.keyboard.press('Enter');
  await expect(active(page, 'interaction-feedback')).toContainText('Saving your action');
  await expect(like).toBeDisabled();
  await expect(like).toBeFocused();
  await like.dispatchEvent('click');
  await expect(active(page, 'interaction-feedback')).not.toContainText(/like saved|mutual match/i);
  await active(page, 'interaction-release').click();
  await expect(active(page, 'interaction-result')).toContainText(/like saved|liked|like committed/i);
  await expect(active(page, 'interaction-result')).toBeFocused();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await active(page, 'open-matches').click();
  await expect(matchRows(page)).toHaveCount(0);
});

test('leaving a delayed action then switching accounts cannot adopt a late result or match', async ({ page }) => {
  await eligible(page);
  await setDelivery(page, 'delayed');
  await active(page, 'like-profile-jules').click();
  await expect(active(page, 'interaction-feedback')).toContainText('Saving your action');
  await development(page);
  await active(page, 'scenario-new').click();
  await expect(active(page, 'screen-account')).toBeVisible();
  await active(page, 'development-link').click();
  await active(page, 'scenario-eligible').click();
  await expect(active(page, 'like-profile-jules')).toBeEnabled();
  await development(page);
  await active(page, 'interaction-release').click();
  await active(page, 'return-current').click();
  await expect(active(page, 'like-profile-jules')).toBeEnabled();
  await active(page, 'open-matches').click();
  await expect(matchRows(page)).toHaveCount(0);
});

test('anonymous match routes cannot disclose participant details', async ({ page }) => {
  for (const route of ['/matches', '/match']) {
    await page.goto(route);
    await expect(active(page, 'screen-account')).toBeVisible();
    await expect(page.getByTestId('match-list')).toHaveCount(0);
    await expect(page.getByTestId('match-detail')).toHaveCount(0);
  }
});
