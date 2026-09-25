# P06.1 Stream dashboard discovery (Claude in Chrome)

- **Owner:** Nathan Amthor. Written by App Manager 3 on 25 September 2026.
- **Purpose:** confirm owner inputs 1 and 2 of the [P06.1 proposal](../planning/p06-1-chat-provider-proof.md) from the Stream dashboard: the plan and its limits, and the test application and its region.
- **Runs in:** Claude in Chrome, in Nathan's own signed-in browser. It is a read-only lookup, not an implementation, review or correction session, so it gets no reasoning-level recommendation.
- **Deletion condition:** prune once its results are recorded in the P06.1 proposal.

---

You're helping Nathan confirm facts about his Stream account (getstream.io) for a sandbox test of chat permissions in his Glow dating app. He is signed in to the Stream dashboard in this browser; start at dashboard.getstream.io. **This is a read-only lookup.**

**Rules**

- Only look. Don't change any setting, and don't create, edit or delete anything: apps, users, channels, channel types, roles, permissions, webhooks, API keys or team members.
- Don't click anything that upgrades or downgrades a plan, starts a trial, opens a checkout, applies to a program (including Maker) or accepts terms. If a page pushes you toward one of those, stop and tell Nathan.
- Never reveal, copy, type or record the API secret. If you see a secret unmasked, don't record it, and tell Nathan it was visible.
- Don't record email addresses, payment details, or any user's or message's content. Counts and setting names are enough.
- If you need to sign in, pass a security check or choose between accounts, stop and ask Nathan.

**Find these for Stream Chat**

1. **The app.** Find the app with App ID `1729640`. Record its name and its region exactly as shown, and whether its API key is `qdstwyevnyea` (the key is not secret). If the dashboard shows an environment or mode for the app, such as development or production, record it.
2. **Other apps.** List every other app in the organization with its name, App ID and region. Say whether any looks like a production app.
3. **The plan.** Record the organization's current Chat plan name. If it is a trial, record the end date. Record any Maker program status the account shows: applied, approved, or not shown.
4. **Limits and usage.** Record the plan's limits as shown: monthly active users, concurrent connections, and any other limit listed. Record this billing period's usage, if shown.
5. **Past a limit.** Record what the dashboard says happens when a limit is exceeded: a hard stop, automatic overage charges, or a prompt to upgrade. Record whether a payment method is on file: yes or no only.
6. **Data in app 1729640.** Record how many users and channels it has, and whether they look like test data or real people. Don't open any conversation.
7. **Safety settings in app 1729640.** Record whether settings named like "Disable Auth Checks" or "Disable Permission Checks" exist, and whether each is on or off.
8. **Configuration in app 1729640.** Record the names of its channel types and roles, marking any that are custom rather than Stream's defaults. Record whether any webhook, event or before-message-send hook URL is set: yes or no, with the hostname only.

**Report back in this format**

- Checked at: date and time (UTC).
- One line per item: *item: value (dashboard page) — confirmed, not shown, or unclear*.
- Risks noticed: for example real-looking user data, automatic billing or a configured webhook.
- Actions taken: "navigation and reading only", or exactly what else happened.
