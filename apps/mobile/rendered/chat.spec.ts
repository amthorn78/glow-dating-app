import { expect, test, type Page } from '@playwright/test';

// P06.2 Stage C2: the chat screens on the in-process fixture (OD-45). Polling is the app's
// own 3-second interval, so assertions wait for the next poll rather than a fixed delay.
const active = (page: Page, id: string) => page.getByTestId(id).filter({ visible: true });
const messageTexts = (page: Page) => active(page, 'message-list').getByTestId('message-text');
const SENTINEL = 'provider-sentinel';

async function conversation(page: Page) {
  await page.goto('/development');
  await active(page, 'scenario-eligible').click();
  await expect(active(page, 'screen-recommended')).toBeVisible();
  await active(page, 'development-link').click();
  await active(page, 'interaction-reciprocal').click();
  await active(page, 'return-current').click();
  await active(page, 'like-profile-jules').click();
  await expect(active(page, 'interaction-feedback')).toContainText(/mutual match/i);
  await active(page, 'open-matches').click();
  await page.getByRole('button', { name: 'View match with Fictional Jules', exact: true }).click();
  await active(page, 'match-conversation').click();
  await expect(active(page, 'screen-conversation')).toBeVisible();
  await expect(active(page, 'conversation-empty')).toBeVisible();
}
async function controls(page: Page) {
  const toggle = active(page, 'chat-fixture-toggle');
  if ((await toggle.textContent())?.includes('Show')) await toggle.click();
  await expect(active(page, 'chat-fixture-toggle')).toContainText('Hide');
}
async function send(page: Page, text: string) {
  await active(page, 'composer-input').fill(text);
  await active(page, 'composer-send').click();
}

test('the list, opening a conversation, unread and the read cursor', async ({ page }) => {
  await conversation(page);
  await expect(active(page, 'screen-conversation')).toContainText('Conversation with Fictional Jules');
  await active(page, 'conversation-back').click();
  await expect(active(page, 'screen-conversations')).toBeVisible();
  const rows = active(page, 'conversation-list').locator('[data-testid^="conversation-row-"]');
  await expect(rows).toHaveCount(1);
  await expect(rows.first()).toContainText('Fictional Jules');
  await expect(rows.first()).toContainText('No unread messages');
  await controls(page);
  await active(page, 'chat-other-send').click();
  await active(page, 'conversations-refresh').click();
  await expect(rows.first()).toContainText('1 unread message');
  await page.getByRole('button', { name: 'Open conversation with Fictional Jules', exact: true }).click();
  await expect(messageTexts(page)).toHaveText(['Hello from fictional Jules, message 1.']);
  await expect(active(page, 'message-list')).toContainText('FICTIONAL JULES');
  await active(page, 'conversation-back').click();
  await expect(rows.first()).toContainText('No unread messages');
});

test('a message from the other member arrives by polling, and a send shows once', async ({ page }) => {
  await conversation(page);
  await controls(page);
  await active(page, 'chat-other-send').click();
  await expect(messageTexts(page)).toHaveText(['Hello from fictional Jules, message 1.']);
  await send(page, 'Hello back from the member.');
  await expect(messageTexts(page)).toHaveText(['Hello from fictional Jules, message 1.', 'Hello back from the member.']);
  await expect(active(page, 'composer-input')).toHaveValue('');
  await expect(active(page, 'message-list')).toContainText('YOU');
});

test('an offline send is not confirmed, and its retry sends the same message once', async ({ page }) => {
  await conversation(page);
  await controls(page);
  await active(page, 'chat-scenario-offline').click();
  await send(page, 'Sent through a bad connection.');
  await expect(active(page, 'send-error')).toContainText('Your message was not confirmed');
  await expect(active(page, 'send-retry')).toBeVisible();
  await active(page, 'chat-scenario-normal').click();
  await active(page, 'send-retry').click();
  await expect(messageTexts(page)).toHaveText(['Sent through a bad connection.']);
  await expect(active(page, 'send-error')).toHaveCount(0);
});

test('a lost response shows the message once, before and after its retry', async ({ page }) => {
  await conversation(page);
  await controls(page);
  await active(page, 'chat-scenario-lost_response').click();
  await send(page, 'Committed, answer lost.');
  await expect(active(page, 'send-retry')).toBeVisible();
  await active(page, 'chat-scenario-normal').click();
  await expect(messageTexts(page)).toHaveText(['Committed, answer lost.']);
  await active(page, 'send-retry').click();
  await expect(active(page, 'send-retry')).toHaveCount(0);
  await expect(messageTexts(page)).toHaveText(['Committed, answer lost.']);
});

test('an older page loads with the page\'s own cursor and keeps the order', async ({ page }) => {
  await conversation(page);
  await controls(page);
  await active(page, 'chat-seed').click();
  await expect(messageTexts(page)).toHaveCount(20);
  await expect(messageTexts(page).first()).toHaveText('Fictional history message 6.');
  await active(page, 'conversation-older').click();
  await expect(messageTexts(page)).toHaveCount(25);
  await expect(messageTexts(page).first()).toHaveText('Fictional history message 1.');
  await expect(messageTexts(page).last()).toHaveText('Fictional history message 25.');
  await expect(active(page, 'conversation-older')).toHaveCount(0);
});

for (const [control, who] of [['chat-block', 'the member blocks'], ['chat-other-block', 'the other member blocks']] as const) {
  test(`the revoked state when ${who}: Glow's wording, no history and no composer`, async ({ page }) => {
    await conversation(page);
    await controls(page);
    await active(page, 'chat-other-send').click();
    await send(page, 'Private words before the block.');
    await expect(messageTexts(page)).toHaveCount(2);
    await active(page, control).click();
    await expect(active(page, 'conversation-revoked')).toContainText('This conversation is unavailable.');
    await expect(page.getByTestId('message-list')).toHaveCount(0);
    await expect(page.getByTestId('composer')).toHaveCount(0);
    await expect(page.locator('body')).not.toContainText('Private words before the block.');
    await expect(page.locator('body')).not.toContainText('Hello from fictional Jules');
    await active(page, 'conversation-back').click();
    await expect(active(page, 'conversations-empty')).toBeVisible();
  });
}

test('a response carrying a provider field shows only Glow\'s error state', async ({ page }) => {
  test.setTimeout(90_000);
  await conversation(page);
  await controls(page);
  await active(page, 'chat-other-send').click();
  await expect(messageTexts(page)).toHaveText(['Hello from fictional Jules, message 1.']);
  let shown = 1;
  for (const field of ['member_object', 'user_object', 'ai_indicator_update', 'channel_name', 'provider_error_text']) {
    await active(page, `chat-provider-${field}`).click();
    await active(page, 'chat-other-send').click();
    await expect(active(page, 'conversation-error')).toContainText('Messages could not be shown. Try again.');
    await expect(page.locator('body')).not.toContainText(SENTINEL);
    // Nothing of the refused page is shown: the new message waits for a valid response.
    await expect(messageTexts(page)).toHaveCount(shown);
    await active(page, 'chat-provider-none').click();
    await expect(active(page, 'conversation-error')).toHaveCount(0);
    await expect(messageTexts(page)).toHaveCount(++shown);
  }
  await active(page, 'chat-provider-channel_image').click();
  await active(page, 'conversation-back').click();
  await expect(active(page, 'conversations-error')).toContainText('Your conversations could not be shown. Try again.');
  await expect(page.locator('body')).not.toContainText(SENTINEL);
});

test('a message whose stored text changed shows Glow\'s "unavailable", with no reason', async ({ page }) => {
  await conversation(page);
  await controls(page);
  await active(page, 'chat-alter').click();
  await expect(active(page, 'message-unavailable')).toHaveText('This message is unavailable.');
  await expect(page.locator('body')).not.toContainText('A message that will change');
  await expect(messageTexts(page)).toHaveCount(0);
});

test('anonymous chat routes show no conversation', async ({ page }) => {
  for (const route of ['/conversations', '/conversation']) {
    await page.goto(route);
    await expect(active(page, 'screen-account')).toBeVisible();
    await expect(page.getByTestId('conversation-list')).toHaveCount(0);
    await expect(page.getByTestId('message-list')).toHaveCount(0);
  }
});
