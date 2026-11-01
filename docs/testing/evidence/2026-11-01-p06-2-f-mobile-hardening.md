# P06.2-F — Mobile hardening: evidence record

- **Work:** P06.2-F, the mobile hardening ([brief](../../planning/p06-2-f-mobile-hardening.md), revision 1; Outcome items 1 to 7, D1 to D6).
- **Prompt:** [`docs/ephemeral/2026-11-01-p06-2-f-implementation-prompt.md`](../../ephemeral/2026-11-01-p06-2-f-implementation-prompt.md), revision 1, from `67b02013a954c441f1d84d6a82da43a6afcf4009` of the manager branch `claude/magical-wozniak-yfmmx2`.
- **Session:** one implementation session, started by Nathan, 1 November 2026. Branch `claude/practical-wozniak-fg1e2i`, started at `67b0201`.
- **Code head:** `3db50d876e2c9423d25ee197735855a77228f93c`. **Records head:** the commit that adds this file (no code after the code head).
- **Run of record:** see "The run of record" below.

## Environment check (names only)

- `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`: none present.
- `STREAM_*`: no name present. The session ran in `Glow App - No Stream`.
- GitHub token names `GH_TOKEN` and `GITHUB_TOKEN` are present (the environment inventory); never read. Every app command ran without them.
- **Toolchain:** `node --version` → `v24.19.0`; `npm --version` → `11.9.0`, both from `$HOME/.local/bin`. Every npm, Node and Expo command ran in `env -i PATH="$HOME/.local/bin:$PATH" HOME="$HOME" LANG=C.UTF-8`; `npm ci` also passed `HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS` by reference, never printed.

## Start gate

| Check | Result |
|---|---|
| `git fetch origin claude/magical-wozniak-yfmmx2 main` | fetched; `origin/claude/magical-wozniak-yfmmx2` = `67b02013a954c441f1d84d6a82da43a6afcf4009` (the prompt's commit is the live manager head) |
| `git switch -C claude/practical-wozniak-fg1e2i 67b0201…`; `git rev-parse HEAD` | `67b02013a954c441f1d84d6a82da43a6afcf4009` |
| `git merge-base --is-ancestor 05f4c3a… HEAD` | `PR39 present` |
| `git diff --name-only bac3c19… HEAD \| grep -v '\.md$'` | nothing |
| `grep` of `apps/mobile/package.json` | `expo` 58.0.22, `expo-router` 58.0.29, `react-native` 0.88.1 |
| `test -e apps/mobile/src/hooks/use-recommendations.ts` | `dead hook present` |
| The brief's "Sessions" | "None yet": the prompt is not stale |

**Read before the work:** root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`, `CLAUDE.md` and `README.md`; the brief; the P06.2 brief's "Carried to later changes"; M05's findings 17 to 20 and P-13; the carried-items file's "Carried to P06.2-F"; ADR 0003; the Foundation workflow's Mobile job (rendered suite, `timeout-minutes: 25`). For item 6, also DM-29 (1.1 to 1.4), DM-30 (2.1, 2.2) and the combined C2-C3/C2-C4 re-review's findings in the P06.2 evidence record; for item 5, the C2 exact-head review's findings table.

**Expo documentation:** not read. The session's network allowed only the npm registry, so `docs.expo.dev` was not fetched (`apps/mobile/AGENTS.md`, "Expo has changed"). The one SDK claim this change makes (item 1's comment) rests on the installed package's source, named below, not on the documentation or on memory.

## The cited lines, re-located at `67b0201`

Every line the brief and its sources cite is where they say:

| Citation | At `67b0201` |
|---|---|
| `_layout.tsx:58` `!__DEV__` | `:58` |
| `app.config.ts:15` (allow-list), `:7` (SDK 57 comment), the name check | `:15`, `:7`, `:10` |
| `display-rule.test.ts:39` (copy check of `invalid_response` only) | `:39` |
| `store.ts:189` (list clear on an account change) | `:189` |
| `interactions/screen.tsx:76`, `media.tsx:91`, `:100`, `verify.tsx:12` | `:76`, `:91`, `:100`, `:12`; the same screens also carried `media.tsx:49`, `:90`, `:119`, `onboarding/shell.tsx:30` (shown on the verification screen), and the media store's feedback `media/store.ts:173`, `:190` |
| README `:18`, `:24`, `:440`, the last sentence, the cursor sentence (`:405-408` in the re-review) | `:18`, `:24`, `:440`, `:456-457`, `:405-408` |
| `store.ts:65` (class comment), `:245`, `:300`, `:259` | `:65`, `:245`, `:300` (loadOlder's catch), `:259` |
| `store.ts` draft cleared before the send's result (the C2 review's `:282-284`) | `:374` |
| `store.test.ts` `staleOnce` `:619`, `staleReload` `:635`, `staleAnswer` `:723`, F1 (c) `:673`, CX12 (e) `:817` | the same |
| `rendered/interactions.spec.ts:115-128`, `:145-169` | the paused test at `:115`, the restricted tests at `:145`/`:146` |
| `rendered/onboarding.spec.ts:76-77` (at `524d42f`) | `:76-77` |
| `no-provider.test.ts:17-22` | `:17-22` |

## Changes, tests and reversals

Each reversal was a temporary edit made by a scratch helper that replaced one exact string, ran the named command in the clean environment, restored the file and checked its SHA-256 against the original. Every file was restored; `git status` was clean of reversal edits after each. Unit and lint reversals ran locally. **Rendered reversals ran locally against the preinstalled Chromium 1243, not the revision `@playwright/test` 1.62.1 pins**, through an uncommitted config under the ignored `.work/`: they are **informational only**. The pinned-browser evidence for the rendered assertions themselves is the run of record.

### Item 1 — the release guards (M05 finding 17)

| Change | Files | Test | Reversal | Failing output |
|---|---|---|---|---|
| The layout's predicate moved to an importable module; the layout passes `__DEV__` and `process.env.EXPO_PUBLIC_GLOW_MODE` itself, so Expo still inlines the mode there. `!(a && b)` equals the old `!a \|\| b !== 'fixture'`: **the guard allows exactly what it allowed** (D2) | `src/config/release-guard.ts` (new), `src/app/_layout.tsx` | `src/config/release-guard.test.ts`: the predicate (true only for `(true, 'fixture')`; false for `__DEV__` false, mode unset, `live`, `Fixture`, empty); a source test that `RootLayout` first returns the unavailable screen unless `developmentPreviewAvailable(__DEV__, process.env.EXPO_PUBLIC_GLOW_MODE)` passes, and renders `<Navigation />` in one place only | 1a: `isDevelopment && mode === 'fixture'` → `mode === 'fixture'` | `✖ the layout's guard renders routes only in a development bundle in fixture mode`; `AssertionError: __DEV__ false, mode fixture` |
| | | | 1b: the layout passes `true` for `__DEV__` | `✖ the root layout gates every route on that guard, with __DEV__ and the inlined public mode`; `Expected values to be strictly equal` |
| The environment allow-list is probed beyond `production` | `scripts/build-guard.test.mjs` | `GLOW_APP_ENV` `staging`, `preview` and unset are refused (rendered harness off and on); `development` with `fixture` is accepted, so the refusals are the allow-list's | 1c: `app.config.ts:15` `!== 'development'` → `=== 'production'` | `✖ Expo config allows only GLOW_APP_ENV=development: …`; `AssertionError: GLOW_APP_ENV staging` |
| The public-name allow-list is exact | `scripts/build-guard.test.mjs` | `EXPO_PUBLIC_GLOW_STREAM_TOKEN`, `EXPO_PUBLIC_GLOW_MODE_OVERRIDE`, `EXPO_PUBLIC_GLOW_API_BASE_URL_SECRET` are refused, without echoing the value | 1d: `!publicNames.has(name)` → `!name.startsWith('EXPO_PUBLIC_GLOW_')` | `✖ Expo public config refuses an unreviewed name that shares a reviewed prefix …`; `AssertionError: EXPO_PUBLIC_GLOW_STREAM_TOKEN` |
| | | | 1e: a prefix rule over the reviewed names (`![...publicNames].some(r => name.startsWith(r))`) | the same test; `AssertionError: EXPO_PUBLIC_GLOW_MODE_OVERRIDE` |
| The comment names SDK 58. **Checked in the installed source:** `node_modules/expo/node_modules/@expo/cli` 58.1.18, `build/src/start/server/metro/withMetroMultiPlatform.js:739`: `process.env.EXPO_PUBLIC_PROJECT_ROOT = process.env.EXPO_PUBLIC_PROJECT_ROOT ?? projectRoot;` ("Required for @expo/metro-runtime to format paths in the web LogBox"). The guard's code is unchanged | `app.config.ts` (comment only) | by text; the rendered harness's run of record exercises it | none (a comment) | — |

### Item 2 — the display rule's client-side gaps (M05 finding 18)

| Change | Files | Test | Reversal | Failing output |
|---|---|---|---|---|
| `no-console` (ESLint core; no dependency change) for `src/**/*.{ts,tsx}`. The rendered specs keep their diagnostic `console.info` lines; they are outside `src/` | `eslint.config.mjs` | `npm run lint` | 2a: `console.info('chat page', page.messages.map(message => message.text));` after `mergeHead` in `store.ts` | `244:7  error  Unexpected console statement  no-console`; `✖ 1 problem (1 error, 0 warnings)` |
| The render rule no longer rests on the validator alone. `screen.tsx` (and, after item 4, `rows.ts`) is read from source: every path it reads from `message`, `conversation`, `list`, `state`, `match` or `row` must be one of a named list of contract and store fields, and no type cast (other than `as const`), `any`, spread, computed read or reflective read (`Object.values`, `Reflect`, `JSON`) may appear. The checker is itself tested against seven planted forms | `src/chat/display-rule.test.ts` | `the chat screens render only the contract's fields: …` | 2b: the eyebrow renders `String((message as { name?: string }).name ?? name)` | `✖ the chat screens render only the contract's fields …`; `Expected values to be strictly deep-equal` |
| | | | 2b′: `'name' in message ? String(message.name) : …` (no cast) | the same test fails |
| The copy test covers every export of `copy.ts`: the three failure tables, `DELIVERY_COPY`, `UNAVAILABLE_MESSAGE`, `REVOKED_DETAIL` and the outputs of `timeLabel` and `unreadLabel` (33 strings); the export list is pinned so a new table is not missed | `src/chat/display-rule.test.ts` | `every copy table and label in copy.ts names no provider` | 2c: `READ_COPY.unavailable` → `'This Stream conversation is unavailable.'` | `✖ every copy table …`; `AssertionError: This Stream conversation is unavailable.` |
| | | | 2c′: `DELIVERY_COPY.failed` → `'Not delivered by the provider'` | the same; `AssertionError: Not delivered by the provider` |
| The list clear on an account change | `src/chat/store.test.ts` | `signing out` / `another account clears the conversation list at once, before any read`: the list is read and holds the conversation; right after the change, no conversation and no error, and the match ID is nowhere in the snapshot | 2d: `this.publish({ list: emptyList });` removed (`store.ts:189`) | both tests `✖`; `AssertionError: nothing of the earlier account's list is kept` |

### Item 3 — no provider wording outside chat (M05 finding 19; ADR 0003, decision 3)

| Change | Files | Test | Reversal | Failing output |
|---|---|---|---|---|
| `interactions/screen.tsx:76` → "Messaging is unavailable. This connection shows no messages or history in this preview." (the rendered `toContainText('Messaging is unavailable')` still holds) | `src/interactions/screen.tsx` | `src/components/provider-wording.test.ts`: the four screens' source, comments removed, has no line matching `provider(s)`, `stream`, `getstream`, `cloudflare`, `allauth` or `channel(s)` | 3a: the old sentence restored | `✖ interactions/screen.tsx names no provider …` |
| `media.tsx:91` → "Synthetic purge confirmed. …"; `:100` → "… separate storage, system and moderator actors."; also, on the same screen, `:49` → "Real photo processing …", `:90` → "Deletion of the stored photo is still pending.", and the developer button `:119` → "Storage: retry or confirm Photo N purge" (testID `media-purge-*` unchanged; no rendered test reads the label) | `src/app/media.tsx` | the same | 3b: `:91` restored; 3c: `:100` restored | `✖ app/media.tsx names no provider …` (each) |
| `verify.tsx:12` → "In the live flow, you will confirm your email address from a message Glow sends." | `src/app/verify.tsx` | the same | 3d: the old sentence restored | `✖ app/verify.tsx names no provider …` |
| The fixture outcome panel the verification screen shows (`shell.tsx:30`) → "No real service is contacted." | `src/onboarding/shell.tsx` | the same | 3e: restored | `✖ onboarding/shell.tsx names no provider …` |
| The media store's feedback, which the photo screen shows: removal → "Photo removed from delivery. Its purge is pending."; developer events name the actor through `ACTOR_LABELS` (`provider` → `storage`). The adapter's `actor` value `'provider'` is unchanged | `src/media/store.ts` | `the media store's removal and purge feedback names no provider` (review, approve, remove, purge; four messages) | 3f: `` `Synthetic ${actor} event` `` restored | `AssertionError: Synthetic provider event: purged.` |
| | | | 3g: the removal message restored | `AssertionError: Photo removed from delivery. Provider purge is pending.` |

The README's walkthrough label was updated with it (item 4's README commit). The broader README prose and the discovery screens' "provider outcomes" wording were not in the brief and were not changed.

### Item 4 — dead code, a closed conversation and the README (M05 finding 20; P-13; DM-23 3.1; DM-26 item 2)

| Change | Files | Test | Reversal | Failing output |
|---|---|---|---|---|
| `src/hooks/use-recommendations.ts` removed. **Beyond the brief's list:** `src/data/fixtures.ts` was imported only by that hook, so it was removed with it (no other importer in `apps/mobile`, the root scripts or any test; `scripts/smoke.mjs` imports `src/data/recommendations.ts` and `src/config/development.ts`, both kept) | both files deleted | `src/components/no-dead-modules.test.ts`: every `.ts`/`.tsx`/`.js` module under `src/` outside `src/app` (Router's routes) and other than tests and `.d.ts` has a relative importer (platform variants resolved) | 4a: the hook restored from `67b0201` | `✖ every source module outside src/app has an importer`; `actual: [ 'hooks/use-recommendations.ts' ]` |
| | | | 4a′: `src/data/fixtures.ts` restored | `actual: [ 'data/fixtures.ts' ]` |
| A `closed` summary is not an openable row: `rows.ts` builds each list row from Glow's summary and match names; a closed one shows "This conversation is unavailable." (`READ_COPY.unavailable`) with no count, time, reason or open control. The screen renders only from the row, and "Open conversation" only under `row.openable`. An open row renders as before | `src/chat/rows.ts` (new), `src/chat/screen.tsx` | `src/chat/rows.test.ts`: an open and a closed contract summary (each accepted by the generated validator) and their rows; a source test that the list renders through `conversationRow`, has one open control, under `row.openable &&`, and no other `store.select(` | 4b: `rows.ts` returns a closed summary as open (the closed branch disabled) | `✖ a closed conversation is not an openable row …`; `Expected values to be strictly deep-equal` |
| | | | 4c: the screen's `row.openable &&` removed | `✖ the list screen renders its rows from conversationRow …`; the regex did not match |
| | | | 4d: the screen builds rows itself, always openable | the same test; the `conversationRow` regex did not match |
| README: P-13's `:18` and `:440` text; `:24`'s development-origin sentence (no loader or bundled fixtures remain); the last sentence now names "Stage C2" to "Stage C2-C4", with their verifications and reviews, and this record; plus the closed row, item 3's purge label and the release-guard module | `apps/mobile/README.md` | by text | none (documentation) | — |

The render rule's source check (item 2) now also reads `rows.ts`, with `conversation.state` and the row's fields in its list.

### Item 5 — the C2 review's findings 4, 5 and 1

| Change | Files | Test | Reversal | Failing output |
|---|---|---|---|---|
| **Finding 4:** a final send refusal that leaves the conversation open restores the draft, unless the member started a new one while it was pending. A refusal that ends access still revokes and drops the draft (DM-24 1.2), and a retryable failure still keeps the draft empty and offers the same intent | `src/chat/store.ts` (`run`'s catch; class comment) | `store.test.ts`: `a final send refusal (stale_version / idempotency_conflict / state_conflict) restores the draft; the conversation stays open` (nothing sent; sending again succeeds); `… keeps a draft started while the message was pending`; `a retryable failure keeps the draft empty …; a refusal that ends access drops it` | 5a: `const restore = false;` | the three refusal tests `✖`; `AssertionError: the refused message is back in the composer` |
| | | | 5a′: the restore without the `draft === ''` condition | `✖ a final send refusal keeps a draft started while the message was pending` |
| **Finding 5:** the paused and the two restricted tests assert `page.getByTestId('match-conversation')` has a count of 0, without the visible filter, on the connection's detail and after the unmatch | `rendered/interactions.spec.ts` | the three tests | 5b: `interactions/screen.tsx` renders a `match-conversation` button for a connection that is not active. **Local, informational (Chromium 1243)** | baseline: `3 passed (14.2s)`; reversal: `3 failed`, each `expect(locator).toHaveCount(expected) failed … Locator: getByTestId('match-conversation') Expected: 0 Received: 1` at `:126` and `:164` |
| **Finding 1, optional (done):** `no-provider.test.ts` also fails on any bare `WebSocket` or `EventSource` identifier in the app's source, so an aliased constructor fails; its pattern test covers three forms that must match and three that must not. README sentence updated | `src/chat/no-provider.test.ts`, README | `the app's manifest, lock and source name no provider package and construct or name no socket or event stream` | 5c: `const Socket = (globalThis as { WebSocket?: unknown }).WebSocket; void Socket;` in `transport.ts` (no `new`, so the construction patterns alone pass it) | `✖ the app's manifest, lock and source …`; `Expected values to be strictly deep-equal` |

### Item 6 — the window-replacement follow-up (DM-29 1.1; DM-30 2.1, 2.2)

**The change:** `store.ts:245` → `const older = cursor === null ? 'idle' : this.state.conversation.older;`. A read of the newest page alone (a replacement) leaves the older-page state `idle` whatever it was, `error` included; a newer page keeps it. The class comment's sentence at `:65` is now true as written and is unchanged.

| Entry (DM-30 2.1) | Test | Reversal | Failing output |
|---|---|---|---|
| **DM-29 1.1** | `DM-29 1.1: an older-page error from the window a stale reload replaces is not shown, and "Show earlier messages" asks with the reload's cursor`: the older page fails offline while its window is current (`older` is `error`); a head read is answered `stale`; after the reload, `older` is `idle` with no error (`assertReloaded`), and `reachTheGap` asks with the reload's `older_cursor` | 6a: today's `:245` (only `loading` becomes `idle`) | `✖ DM-29 1.1: …`; `actual: [ 'ready', true, 'error', null ]` |
| **Finding 2** (the gap ordering) | `DM-29 1.1 in the gap: …`: the reload is held; an older page asked from the window about to be replaced fails first (`older` is `error`); then the reload is released | 6a (the same reversal) | `✖ DM-29 1.1 in the gap: …` (with 6a's output) |
| **Finding 3** (CX9-style, `loadOlder`'s catch) | `CX9: an older page held across a revocation that is then released to fail / refused publishes nothing and starts nothing`: a held older page, a block that revokes, then the release; the snapshot object is unchanged and no request starts | 6b: `:300`'s `if (epoch !== this.conversationEpoch) return;` removed | both `✖`; `AssertionError: nothing published: no older-page error and no second revocation`, with `older: 'error'` published into the revoked state |
| **Finding 4** (DM-30 2.2: an addition to the existing test (e), by the existing-test rule) | CX12 (e), all three outcomes, gains one poll while the current window's older page is held: one more request, and `older` stays `loading`. Nothing existing in (e) was removed or loosened | 6c: `cursor === null` removed from `:245` (the new line becomes `const older = 'idle';`) | the three (e) tests `✖`; `AssertionError: its page is still held` |
| **Finding 5, optional (done)** | `the older-page slot is the window's: a page held in another conversation does not hold back this one's` and `… a page held from before a revocation does not hold back a window read after it` | 6d: a slot not keyed by the window (`this.olderInFlight === windowId` → `this.olderInFlight !== null`) | both `✖` (`the second conversation's older page is asked`, `the new window's older page is asked`), and the three (e) tests |
| **Finding 6** | `staleReload` and `staleAnswer` count the fixture's `messages` requests after the `stale` answer: exactly one, cursorless (`[null]`), where they read only the last one | 6e: a no-op `stale` branch | **F1 (c) fails, as DM-30 2.1 requires**, with F1 (a), (b), CX12 (a) to (f) and both DM-29 1.1 tests: 13 `✖`; `AssertionError: then the newest page alone, once` |
| **Finding 7** | `staleOnce`'s doc comment: it answers the next `messages` request made with any non-null cursor, without passing it to the fixture | none (a comment) | — |
| **Finding 9, optional: not done** | — | — | — |
| **Finding 11** | README: the known position holds "for that conversation in this session (closing and reopening the same conversation keeps the position; selecting another conversation or account, or a revocation, clears it)" | none (documentation) | — |

**Why finding 9 is not done.** `:259`'s queued read is not only the `stale` reload. `authorityChanged` (an unmatch, a block, a pause) queues `readHead(true)` for a retained, hidden conversation, and when a head read is already in flight it is that queued read which `:259` sends. Gating `:259` on `conversationShown` would drop that revalidation while the screen is hidden, so a revoked conversation's retained history would stay until the screen is shown again. DM-30 judged the gate safe for the `stale` case only. It is optional, and a narrower gate (the `stale` case alone) would add a flag the specification does not name, so the session left it as it is.

### Item 7 — the failed-reset landing (M06's exact-head review, findings 5 and 6; DM-36 section 6)

**The landing: account entry, with the reset's generic error,** as the brief chooses. No navigation, route guard or screen changed.

| Change | Files | Test | Reversal | Failing output |
|---|---|---|---|---|
| Finding 5's two assertions, after the `wrong_context` reset: (1) on account entry, an alert with the reset's generic error, "The synthetic request could not be completed. Check the fixture and try again." (the adapter's `invalid` failure, which `wrong_context` raises); (2) `page.getByTestId('screen-reset-password')` has a count of 0 without the visible filter. The existing visible-filtered assertion stays | `rendered/onboarding.spec.ts` (`:78-82`) | `sign in and synthetic recovery remain separate; …` | 7a: `reset-password.tsx` calls `store.logout()` on a failure, so account entry shows no error. **Local, informational** | `✘ … expect(locator).toBeVisible() failed … getByTestId('screen-account').filter({ visible: true }).getByRole('alert').filter({ hasText: … }) … element(s) not found` at `:81` |
| | | | 7b: the reset screen kept mounted and hidden: its guard set to `true` in `_layout.tsx`, and `router.push('/account')` on a failure. **Local, informational** | `✘ … expect(locator).toHaveCount(expected) failed  Locator: getByTestId('screen-reset-password')  Expected: 0  Received: 1` at `:82` |

Baseline: the test passed locally (informational, `1 passed (21.5s)`). **A probe, not a reversal:** an explicit `router.replace('/recovery')` after a failed reset still passed the test locally (`1 passed (8.4s)`): the landing stayed account entry. Router 58's redirect for the failed guard decides it, which is the race the carried-items entry warns of. Neither 7b's guard edit nor any other was kept (D2).

## Commands and results

All in `apps/mobile`, in the clean environment.

| Command | Result |
|---|---|
| `npm ci --ignore-scripts` (with the proxy and CA variables by reference) | `added 651 packages, and audited 652 packages in 23s`; `22 moderate severity vulnerabilities` (npm audit's line; no lock change) |
| `node --test scripts/build-guard.test.mjs src/config/release-guard.test.ts` (item 1) | `ℹ tests 6`, `ℹ pass 6` |
| `node --test src/chat/display-rule.test.ts` (item 2) | `ℹ pass 20`, `ℹ fail 0` |
| `node --test src/components/provider-wording.test.ts` (item 3) | `ℹ pass 5`, `ℹ fail 0` |
| `node --test src/components/no-dead-modules.test.ts`, `src/chat/display-rule.test.ts src/chat/rows.test.ts` (item 4) | `ℹ pass 1`; `ℹ pass 23`, `ℹ fail 0` |
| `node --test src/chat/no-provider.test.ts` (item 5) | `ℹ pass 2`, `ℹ fail 0` |
| `node --test src/chat/store.test.ts` (items 5 and 6) | `ℹ pass 63`, `ℹ fail 0` |
| `npx tsc --noEmit`, `npx eslint .` after each item | no output (pass) |
| The reversals above | each `exit 1` with the failing output shown; each file restored and its hash checked |
| **`npm run check`** at the code head | exit 0; `ℹ tests 649`, `ℹ pass 649`, `ℹ fail 0` (621 at M05's count; 638 after item 4) |
| **`EXPO_OFFLINE=1 npm run check:expo`** | exit 0; `Dependency validation is unreliable in offline-mode`, `Dependencies are up to date` |
| **`EXPO_OFFLINE=1 npm run export:development`** | exit 0; `iOS Bundled 24288ms … (1361 modules)`, `Android Bundled 24282ms … (1358 modules)`, iOS 8.2 MB, Android 8.1 MB, `Exported: .work/native-export` |
| `npx playwright test -c .work/local-rendered.config.ts …` (scratch config, preinstalled Chromium 1243) | **informational only:** the item 5 and 7 baselines and reversals above; the whole suite: see "What could not run" |

## The run of record

Pending: push run 41355778256 on the code head `3db50d8` was in progress when this draft was committed; its results replace this line.

## What could not run, and limits

- **The rendered suite on the pinned browser** runs only in CI (`playwright install` is forbidden here). Local rendered results used Chromium 1243 through an uncommitted config and are informational; the run of record is CI's.
- **Expo's documentation** was not read (no network beyond the npm registry). Item 1's comment rests on the installed `@expo/cli` 58.1.18 source.
- **Source-reading tests.** The layout's gate (item 1), the render rule (item 2), the provider wording (item 3) and the list's open control (item 4) are checked from source, because those modules import Expo Router or React Native and cannot load in Node. A determined edit can evade any such check (a name built from fragments, for example); they catch the forms the findings name and the planted forms each test lists. The provider-wording check reads the whole screen file, so a future identifier named `provider` in one of those four screens would also fail it.
- **Finding 9** (optional) is not done; the reason is in item 6.
- **Records outside the owned paths** still name the removed hook: `docs/continuity/claude-code-handoff.md:41` and `docs/architecture/profiles-preferences-fixtures.md:213`. They are the manager's to update.
- No guard's allowance changed (D2), no dependency or lock changed (D3), and no path outside the brief's owned paths changed. Nothing met the stop rule.
