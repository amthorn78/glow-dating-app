# P06.2-F — Mobile hardening: evidence record

- **Work:** P06.2-F, the mobile hardening ([brief](../../planning/p06-2-f-mobile-hardening.md), revision 1; Outcome items 1 to 7, D1 to D6).
- **Prompt:** [`docs/ephemeral/2026-11-01-p06-2-f-implementation-prompt.md`](../../ephemeral/2026-11-01-p06-2-f-implementation-prompt.md), revision 1, from `67b02013a954c441f1d84d6a82da43a6afcf4009` of the manager branch `claude/magical-wozniak-yfmmx2`.
- **Session:** one implementation session, started by Nathan, 1 November 2026. Branch `claude/practical-wozniak-fg1e2i`, started at `67b0201`.
- **Code head:** `3db50d876e2c9423d25ee197735855a77228f93c`. **Records head:** the last commit on the branch, Markdown only (this record); no code after the code head.
- **Run of record:** push run **41359462167** on `3db50d8`: all eight jobs `success`, `Application checks passed`, rendered `97 passed (4.3m)`, Mobile 5 min 58 s of 25. [Corrected in C1: this said "5 min 56 s"; the job ran 22:54:52 to 23:00:50 UTC (the exact-head review, finding 6).]
- **Correction C1:** branch `claude/trusting-cori-gxlila`, code head `0881db514b96dd6b35ae54f8759af68dee20e3d7`; run of record push run 41383619096, all eight jobs `success`, `Application checks passed`, rendered `97 passed (5.0m)`, Mobile 7 min 27 s of 25; the section "Correction C1" below.

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
| The layout's predicate moved to an importable module; the layout passes `__DEV__` and `process.env.EXPO_PUBLIC_GLOW_MODE` itself, so the read gets the same rewrite as the two unchanged reads (`onboarding/context.tsx`, `discovery/context.ts`): a development bundle reads the mode through Expo's env module, `_expoVirtualEnv.env.EXPO_PUBLIC_GLOW_MODE`. [Corrected in C1: this said "so Expo still inlines the mode there" (the exact-head review, finding 10).] `!(a && b)` equals the old `!a \|\| b !== 'fixture'`: **the guard allows exactly what it allowed** (D2) | `src/config/release-guard.ts` (new), `src/app/_layout.tsx` | `src/config/release-guard.test.ts`: the predicate (true only for `(true, 'fixture')`; false for `__DEV__` false, mode unset, `live`, `Fixture`, empty); a source test that `RootLayout` first returns the unavailable screen unless `developmentPreviewAvailable(__DEV__, process.env.EXPO_PUBLIC_GLOW_MODE)` passes, and renders `<Navigation />` in one place only | 1a: `isDevelopment && mode === 'fixture'` → `mode === 'fixture'` | `✖ the layout's guard renders routes only in a development bundle in fixture mode`; `AssertionError: __DEV__ false, mode fixture` |
| | | | 1b: the layout passes `true` for `__DEV__` | `✖ the root layout gates every route on that guard, with __DEV__ and the inlined public mode`; `Expected values to be strictly equal` |
| The environment allow-list is probed beyond `production` | `scripts/build-guard.test.mjs` | `GLOW_APP_ENV` `staging`, `preview` and unset are refused (rendered harness off and on); `development` with `fixture` is accepted, so the refusals are the allow-list's | 1c: `app.config.ts:15` `!== 'development'` → `=== 'production'` | `✖ Expo config allows only GLOW_APP_ENV=development: …`; `AssertionError: GLOW_APP_ENV staging` |
| The public-name allow-list is exact | `scripts/build-guard.test.mjs` | `EXPO_PUBLIC_GLOW_STREAM_TOKEN`, `EXPO_PUBLIC_GLOW_MODE_OVERRIDE`, `EXPO_PUBLIC_GLOW_API_BASE_URL_SECRET` are refused, without echoing the value | 1d: `!publicNames.has(name)` → `!name.startsWith('EXPO_PUBLIC_GLOW_')` | `✖ Expo public config refuses an unreviewed name that shares a reviewed prefix …`; `AssertionError: EXPO_PUBLIC_GLOW_STREAM_TOKEN` |
| | | | 1e: a prefix rule over the reviewed names (`![...publicNames].some(r => name.startsWith(r))`) | the same test; `AssertionError: EXPO_PUBLIC_GLOW_MODE_OVERRIDE` |
| The comment names SDK 58. **Checked in the installed source:** `node_modules/expo/node_modules/@expo/cli` 58.1.18, `build/src/start/server/metro/withMetroMultiPlatform.js:739`: `process.env.EXPO_PUBLIC_PROJECT_ROOT = process.env.EXPO_PUBLIC_PROJECT_ROOT ?? projectRoot;` ("Required for @expo/metro-runtime to format paths in the web LogBox"). The guard's code is unchanged | `app.config.ts` (comment only) | by text; the rendered harness's run of record exercises it | none (a comment) | — |

### Item 2 — the display rule's client-side gaps (M05 finding 18)

| Change | Files | Test | Reversal | Failing output |
|---|---|---|---|---|
| `no-console` (ESLint core; no dependency change) for `src/**/*.{ts,tsx}`. The rendered specs keep their diagnostic `console.info` lines; they are outside `src/` | `eslint.config.mjs` | `npm run lint` | 2a: `console.info('chat page', page.messages.map(message => message.text));` after `mergeHead` in `store.ts` | `244:7  error  Unexpected console statement  no-console`; `✖ 1 problem (1 error, 0 warnings)` |
| The render rule no longer rests on the validator alone. `screen.tsx` (and, after item 4, `rows.ts`) is read from source: every path it reads from `message`, `conversation`, `list`, `state`, `match` or `row` must be one of a named list of contract and store fields, and no type cast (other than `as const`), `any`, spread, computed read or reflective read (`Object.values`, `Reflect`, `JSON`) may appear. The checker is itself tested against nine planted forms. [Corrected in C1: this said "seven planted forms" (the exact-head review, finding 8). That check read only paths reached through those six names, so a renamed binding or a loosely typed helper prop passed it (finding 1). **Since C1** it is the source check, with an `in` check on a string added, beside a type check built on the installed TypeScript compiler that finds Glow's data by type through any binding; both are tested against 22 planted edits of `screen.tsx`. What it covers and what still evades it: the section "Correction C1".] | `src/chat/display-rule.test.ts` | `the chat screens render only the contract's fields: …` | 2b: the eyebrow renders `String((message as { name?: string }).name ?? name)` | `✖ the chat screens render only the contract's fields …`; `Expected values to be strictly deep-equal` |
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
| **Finding 4:** a final send refusal that leaves the conversation open restores the draft, unless the composer already holds a new draft. That arises through Retry, not while a send is pending (the composer cannot be edited then: `screen.tsx`, `editable={!pending}`): a draft typed after a retryable failure, then a final refusal on the retry. [Corrected in C1: this said "unless the member started a new one while it was pending" (the exact-head review, finding 5). The test's title, `… keeps a draft started while the message was pending`, is unchanged; C1 changes no other test.] A refusal that ends access still revokes and drops the draft (DM-24 1.2), and a retryable failure still keeps the draft empty and offers the same intent | `src/chat/store.ts` (`run`'s catch; class comment) | `store.test.ts`: `a final send refusal (stale_version / idempotency_conflict / state_conflict) restores the draft; the conversation stays open` (nothing sent; sending again succeeds); `… keeps a draft started while the message was pending`; `a retryable failure keeps the draft empty …; a refusal that ends access drops it` | 5a: `const restore = false;` | the three refusal tests `✖`; `AssertionError: the refused message is back in the composer` |
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
| `npx playwright test -c .work/local-rendered.config.ts …` (scratch config, preinstalled Chromium 1243) | **informational only:** the item 5 and 7 baselines and reversals above; the whole suite at the code head, `97 passed (6.1m)` |

## The run of record

**Push run 41359462167** ([run](https://github.com/amthorn78/glow-dating-app/actions/runs/41359462167)), on the code head `3db50d876e2c9423d25ee197735855a77228f93c`, read through the GitHub tools after it completed:

| Job | Conclusion | Duration (job start to completion) |
|---|---|---|
| Change scope | success: `COMPARE_BASE` `67b0201…`, `COMPARE_HEAD` `3db50d8…`; the trusted policy (from `origin/main`) printed `{"full": true, "reason": "behavior-or-empty", "paths": [...]}`, listing the 25 changed paths | 6 s |
| API checks | success | 48 s |
| Mobile checks | success: `npm run check && npm run check:expo`, `export:development`, the pinned Chromium installed by the workflow, and the rendered suite **`97 passed (4.3m)`**; the empty-form layout artifact uploaded (2 files) | **5 min 58 s of the 25-minute timeout** (22:54:52 to 23:00:50 UTC). [Corrected in C1: this said "5 min 56 s" and "23:00:48" (the exact-head review, finding 6).] |
| API mobile smoke | success (`node scripts/smoke.mjs && node --test scripts/smoke.test.mjs`) | 1 min 24 s |
| API artifact checks | success | 19 s |
| Stream proof checks | success (offline checks; no provider call) | 1 min 39 s |
| Database proof checks | success | 7 min 12 s of 30 |
| Foundation gate | success; its line: **`Application checks passed`** | 3 s |

The rendered suite's 97 includes the three restricted-match tests with finding 5's assertions and the reset test with item 7's two, each passing on the pinned browser.

**How this run came about (a session error, recorded).** The first push run on the code head, **41355778256**, was **cancelled**: the session pushed the draft of this record (`51c98e7`, Markdown only) while it was running, and the workflow's `concurrency` (`cancel-in-progress: true`) cancelled it at 22:14:40 UTC, mid-way through the rendered suite (12 chat cases had passed) and the database suite; its gate then failed. The draft's own run, **41356042982**, compared `3db50d8..51c98e7` (Markdown only) and skipped the application jobs, so it is not a run of the code. The prompt forbids the session a re-run, so the session asked Nathan, who directed it to push to trigger a run. The session then moved the remote branch back to the start commit `67b0201` (`git push --force-with-lease=…:51c98e7`; its run, **41359453519**, was cancelled by the next push) and pushed `3db50d8` as a fast-forward from it, so the workflow compared `67b0201..3db50d8`: the complete change. The records commits were pushed only after 41359462167 completed. No commit was rewritten; the branch's history is unchanged from the session's local history.

## What could not run, and limits

- **The rendered suite on the pinned browser** runs only in CI (`playwright install` is forbidden here). Local rendered results used Chromium 1243 through an uncommitted config under the ignored `.work/` and are informational (the whole suite at the code head: `97 passed (6.1m)`); the pinned-browser result is the run of record's `97 passed (4.3m)`.
- **Expo's documentation** was not read (no network beyond the npm registry). Item 1's comment rests on the installed `@expo/cli` 58.1.18 source.
- **Source-reading tests.** The layout's gate (item 1), the render rule (item 2), the provider wording (item 3) and the list's open control (item 4) are checked from source, because those modules import Expo Router or React Native and cannot load in Node. A determined edit can evade any such check (a name built from fragments, for example); they catch the forms the findings name and the planted forms each test lists. [Corrected in C1: the sentence above claimed more than the render rule's check showed. A plain rename of `MessageRow`'s binding, or a loosely typed helper prop, passed it (the exact-head review, finding 1). **Since C1** the render rule is also checked by type, through any binding, inside `screen.tsx` and `rows.ts`; it still does not read any module those two import, so a helper elsewhere that takes the contract's exact type and casts inside evades it, and a template literal's string coercion of a message is not refused. The section "Correction C1" lists the 22 planted forms and the known evasions.] The provider-wording check reads the whole screen file, so a future identifier named `provider` in one of those four screens would also fail it.
- **Finding 9** (optional) is not done; the reason is in item 6.
- **Records outside the owned paths** still name the removed hook: `docs/continuity/claude-code-handoff.md:41` and `docs/architecture/profiles-preferences-fixtures.md:213`. They are the manager's to update.
- No guard's allowance changed (D2), no dependency or lock changed (D3), and no path outside the brief's owned paths changed. Nothing met the stop rule.

## Correction C1 (2 November 2026)

- **Work:** the brief's "Correction C1", Outcome 1 to 3: the exact-head review's finding 1 (should fix), finding 2 (nit, same file) and the record's findings 5, 6, 8 and 10.
- **Prompt:** [`docs/ephemeral/2026-11-02-p06-2-f-c1-correction-prompt.md`](../../ephemeral/2026-11-02-p06-2-f-c1-correction-prompt.md), revision 1, from `cdc7c487d26fe31c19878b6079750f9c5a42d59c` of the manager branch `claude/magical-wozniak-yfmmx2`. Started by Nathan.
- **Branch:** `claude/trusting-cori-gxlila`, started at `cdc7c48`. **Code head:** `0881db514b96dd6b35ae54f8759af68dee20e3d7`, one commit, `apps/mobile/src/chat/display-rule.test.ts` only. **Records head:** the last commit on the branch, Markdown only (this record); no code after the code head.

### Environment check (names only)

- `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`: none present.
- `STREAM_*`: no name present. The session ran in `Glow App - No Stream`.
- `GH_TOKEN` and `GITHUB_TOKEN` are present; never read. Every app command ran without them.
- **Toolchain:** `node --version` → `v24.19.0`; `npm --version` → `11.9.0`, both from `$HOME/.local/bin`. Every npm, Node and Expo command ran in `env -i PATH="$HOME/.local/bin:$PATH" HOME="$HOME" LANG=C.UTF-8`; `npm ci` also passed `HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS` by reference, never printed.

### Start gate

| Check | Result |
|---|---|
| `git fetch origin claude/magical-wozniak-yfmmx2 main` | fetched; `origin/claude/magical-wozniak-yfmmx2` = `cdc7c487d26fe31c19878b6079750f9c5a42d59c`, `origin/main` = `bac3c1983134f4e977f867ac30b3086b5318216f` |
| `git switch -C claude/trusting-cori-gxlila cdc7c48…`; `git rev-parse HEAD` | `cdc7c487d26fe31c19878b6079750f9c5a42d59c` |
| `git merge-base --is-ancestor cdc7c48… origin/claude/magical-wozniak-yfmmx2` | `this prompt's commit is on the live branch` |
| `git diff --quiet 3db50d8… HEAD -- .github scripts services apps packages proofs` | `the code head under correction` |
| `git diff --quiet 3db50d8… origin/claude/magical-wozniak-yfmmx2 -- …` (the same paths) | `no code on the live branch after 3db50d8` |
| `git show origin/claude/magical-wozniak-yfmmx2:<this record> \| grep -c -E '^#+ Correction C1'` | `0` |
| `git ls-remote origin refs/heads/claude/trusting-cori-gxlila` | nothing (a new branch) |

**Read before the work:** root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md` and `CLAUDE.md`; the brief, whole; this record, whole, with "Exact-head review of P06.2-F"; ADR 0003; `src/chat/display-rule.test.ts`, `src/chat/screen.tsx`, `src/chat/rows.ts` and `src/components/provider-wording.test.ts`, whole. Expo's documentation was not needed: C1 touches no Expo API.

### Finding 1: the mechanism and why

**Both checks, in `display-rule.test.ts`.** The render-rule test now has two checks over `screen.tsx` and `rows.ts`:

- **The source check** is the old one, kept whole: the six-name path list, and the refusals of a cast, `any`, a reflective read, a spread and a computed read. It gains one refusal: **an `in` check on a string literal** (`'name' in …`). It is kept because it is cheap, and the nine planted forms it was tested against must still fail it.
- **The type check** is new. It builds the two files with the TypeScript compiler the app already declares (`typescript` 6.0.3, a devDependency; no dependency or lock change, D3), under the app's own `tsconfig.json`. It finds **Glow's data by type, not by name:** a value is Glow's data when its type declares a property in one of the files where Glow's data types live (`GLOW_DATA`): the two generated contracts (`gapp-api-v1.ts`, `gapp-dev-v1.ts`), the chat store (`chat/store.ts`), the row model (`chat/rows.ts`), and the interactions' state and match view (`interactions/store.ts`, `interactions/fixture-adapter.ts`). Through any binding, it refuses:
  - **a field outside Glow's types:** a property read, or a destructured one, from Glow's data whose symbol is not declared in a Glow data file. This covers a field the compiler allows only after an `in` check (it comes from `Record<"name", unknown>`), a field read through `any`, and one the compiler refuses;
  - **a computed or rest read** of Glow's data (or of `any`, `unknown` or a type parameter);
  - **an `in` check** (any), **a `for…in` enumeration**, **a destructuring assignment** or **a spread** of Glow's data;
  - **a widening:** Glow's data where the expected type declares a property the data's type does not, or is `any`, `unknown`, `object`, `{}`, or has an index signature, checked recursively through arrays, tuples and property types. The expected type is the contextual type (a prop, an annotation, a return, an assignment, an array element), or, for a call's argument, the resolved signature's instantiated parameter. Through `call`, `apply` or `bind`, it is the called function's own `this` or parameter. A loosely typed callback parameter is refused against what the caller passes. So `String(message)`, `JSON.stringify(message)` and `Object.values(message)` are refused as widenings too;
  - **a local generic or a local overload,** whose types the check does not follow;
  - **any type error** in the two files.
- **Its named exceptions,** each needed by today's screen:
  - the value an Array predicate (`filter`, `some`, `every`, `find`…, from the default library) returns, which it reads for truthiness alone. This is `useMatchNames`'s `match.state === 'active' && match.profile`;
  - an element of a React hook's dependency list (`@types/react`'s `DependencyList`), which React compares by identity: `[store]` and `[store, report]`;
  - the initializer of an unannotated object destructuring (`const { list } = state`), whose reads the pattern's own check covers. An annotated one is checked as a widening;
  - a type parameter of a function outside the two files, which is inferred from the value.
- **Why a type check, not a wider name list:** a name list is a deny list, and any name it lacks (a new binding, a helper's prop) is a way around it. The type check follows the value: whatever the binding is called, its type is still `ConversationMessage`, and every way that type can be dropped or widened in the file is either a refusal above or a type error. It needed no runtime change: today's `screen.tsx` and `rows.ts` pass it unchanged, so nothing met the stop rule.
- **Cost:** one TypeScript program per test, about 2 to 2.5 s each locally; the file's 21 tests take about 5 s.

**The planted forms.** The checker is now tested by a second test, `the render rule's checks refuse each planted form of a provider-shaped field (M05 finding 18; correction C1)`. It applies 22 planted edits to `screen.tsx`'s text in memory, each beside `screen.tsx` so its imports resolve, and builds them in one program. The nine old forms were text appended to the source; they are now placed in the screen (after `MessageRow`'s time line, the list row's status line, or the revoked notice) and must still fail the source check. Every form must fail the type check with the violation the test names, not only with a type error. The first test keeps its name and asserts that today's two files have no violation in either check.

### Each planted form as a reversal

Each form was also run as an **edit to `screen.tsx` in a scratch copy of `apps/mobile`** outside the checkout (`git archive HEAD apps/mobile packages` of the code head into the session's scratch directory, with the checkout's `node_modules` linked). The edits were generated from the test's own `PLANTED` list, so each is exactly the edit the test plants. For each: the edit written, `node --test src/chat/display-rule.test.ts`, `npx tsc --noEmit` and `npx eslint src/chat/screen.tsx` run, the file restored with `git checkout` and its SHA-256 checked against the original (`3aef02c3…`), and the test run again. **All 22 failed with the edit in place and passed once it was undone** (`ℹ pass 21`, `ℹ fail 0` each time). The failing output is the first test's violation list, from the first check that fails. The type check runs only when the source check passes, so a form the source check catches shows the source check's violation; the planted test shows the type check's verdict on every form.

| # | Planted edit | `tsc` / ESLint with the edit | Test with the edit | Failing output (first test) |
|---|---|---|---|---|
| 1 | `{message.name}` | TS2339 / pass | 1 fail | `'message.name'` |
| 2 | `{(message as { name?: string }).name}` | pass / pass | 1 fail | `'a type cast'` |
| 3 | `{String(message['name'])}` | TS7053 / pass | 1 fail | `'a computed read'` |
| 4 | `<Text {...message} />` | TS2559 / pass | 1 fail | `'a spread'` |
| 5 | `{Object.values(message).join()}` | pass / pass | 1 fail | `'a reflective read'` |
| 6 | `{conversation.member?.name}` | TS2339 / pass | 1 fail | `'conversation.member', 'conversation.member.name'` |
| 7 | `{(message as any).user}` | pass / `no-explicit-any` | 1 fail | `'a type cast', 'an any type'` |
| 8 | `{row.custom}` | TS2339 / pass | 1 fail | `'row.custom'` |
| 9 | `{Object.entries(conversation)}` | pass / pass | 1 fail | `'a reflective read'` |
| PA | `MessageRow`'s binding renamed (`{ message: item, name, rowRef }`, `item.` for `message.`), rendering `{'name' in item ? String(item.name) : null}` | **pass / pass** | 2 fail | `'an in check'` (the source check's new refusal); the planted test also fails, since the edit removed its anchors. In memory, the type check reports `an in check: 'name' in item` and `a field outside Glow's types: item.name` |
| PB | `function Eyebrow({ entry }: { entry: { name?: string; text: string \| null } })` rendering `entry.name`, used as `<Eyebrow entry={message} />` | **pass / pass** | 1 fail | `'a widening to { name?: string \| undefined; text: string \| null; }: message'` (the source check passes it; the type check alone closes it) |
| PC | the rename, then `const { name: label } = item;`, rendering `{label}` | TS2339 / pass | 2 fail | `"a type error: Property 'name' does not exist on type 'ConversationMessage'.", "a field outside Glow's types: name: label"` |
| 13 | the rename, then `const loose: { name?: string; text: string \| null } = item;`, rendering `{loose.name}` | **pass / pass** | 2 fail | `'a widening to { name?: string \| undefined; text: string \| null; }: item'` |
| 14 | `function Label<T extends { name?: string; text: string \| null }>({ entry }: { entry: T })` rendering `entry.name`, used as `<Label entry={item} />` | **pass / pass** | 2 fail | `'a local generic: function Label<T extends { name?: string; text: string \| null }>({ entry }: { en'` |
| 15 | `{conversation.messages.map((entry: { name?: string; text: string \| null }) => entry.name).join()}` | **pass / pass** | 1 fail | `'a widening callback parameter: entry: { name?: string; text: string \| null }'` |
| 16 | `{((entry: { name?: string; text: string \| null }) => entry.name).call(null, message)}` | **pass / pass** | 1 fail | `'a widening to { name?: string \| undefined; text: string \| null; }: message'` |
| 17 | `{(function (this: { name?: string; text: string \| null }) { return this.name; }).call(message)}` | **pass / pass** | 1 fail | the same |
| 18 | `{((entry: { name?: string; text: string \| null }) => entry.name).apply(null, [message])}` | **pass / pass** | 1 fail | `'a widening to [entry: { name?: string \| undefined; text: string \| null; }]: [message]', 'a widening to { name?: …; text: …; }: message'` |
| 19 | the rename, then `const { name: label }: { name?: string; text: string \| null } = item;`, rendering `{label}` | **pass / pass** | 2 fail | `'a widening to { name?: string \| undefined; text: string \| null; }: item'` |
| 20 | `function loud(entry: ConversationMessage): string;` with the implementation `function loud(entry: { name?: string; text: string \| null }) { return entry.name ?? ''; }`, rendered as `<Text>{loud(message)}</Text>` | **pass / pass** | 1 fail | `'a local overload: function loud(entry: ConversationMessage): string;'` |
| 21 | `const loose: readonly { name?: string; text: string \| null }[] = conversation.messages;`, rendering `{loose[0]?.name}` | **pass / pass** | 1 fail | `'a widening to readonly { name?: string \| undefined; text: string \| null; }[]: conversation.messages'` |
| 22 | `for (const { name: label } of conversation.messages) void label;` | TS2339 / pass | 1 fail | `"a type error: Property 'name' does not exist …", "a field outside Glow's types: name: label"` |

"**pass / pass**" marks the forms that pass both `tsc` and ESLint, so only this test stands between them and the screen. **The test as it stood at `cdc7c48` passed all thirteen new forms** (PA, PB, PC and 13 to 22), each run as the same edit in the scratch copy (`exit 0` each), since none reads a field through the six names. **Forms of the session's own** are 13 to 22, beyond the brief's PA, PB and PC. Three of them came from probes the first version of the type check missed, and the check was extended for each before the code commit:
- the `call` and `apply` forms (16 to 18), first missed because the method's type parameters are inferred from the argument itself. The check now compares against the called function's own `this` and parameters;
- the annotated destructuring (19), first exempted as a destructuring;
- the local overload (20).

A probe with `// @ts-expect-error` above `message.name` also failed the test, at the source check (`'message.name'`).

### Forms known to evade the check

- **Anything in a module outside `screen.tsx` and `rows.ts`.** The check reads those two files only. A probe confirmed it: a new `src/chat/eyebrow.tsx` with `Eyebrow({ entry }: { entry: ConversationMessage })` rendering `(entry as { name?: string }).name`, used in `screen.tsx` as `<Eyebrow entry={message} />`. It passed the test (`ℹ pass 21`), `tsc` and ESLint, since the flow keeps the contract's exact type and the cast is in the other file. The same holds for the modules the screens import today (`controls.tsx`, `components/ui.tsx` and others), and for a module that hands the screen Glow's data under a wider or untyped type.
- **A template literal's coercion of a message** (`` {`${message}`} ``) passed the test in a probe. It renders `[object Object]`, not a field, but it is not refused.
- **A name built from fragments,** read without an element access (none known), and any form the probes above did not try. The check refuses the forms it names; it is not a proof over all programs.

### Finding 2: the copy test's word list

`PROVIDER_TERMS` in `display-rule.test.ts` (line 20 now) was `/\b(provider|stream|getstream|channel|member|custom|ai)\b/i`. It is now `/\b(providers?|stream|getstream|cloudflare|allauth|channels?|members?|custom|ai)\b/i`: item 3's terms, with its own and the plurals. It serves the copy-table test and the `invalid_response` assertions; both pass on today's `copy.ts`.

**Reversal** (in the scratch copy): `READ_COPY.unavailable` (`copy.ts:21`) changed to `'Our providers cannot show this conversation.'`:
- with the new test: `✖ every copy table and label in copy.ts names no provider (M05 finding 18; ADR 0003, decision 3)`, `AssertionError [ERR_ASSERTION]: Our providers cannot show this conversation.` (`ℹ pass 20`, `ℹ fail 1`);
- with the test as it stood at `cdc7c48`: the same edit **passed** (`ℹ pass 1`, `ℹ fail 0` for that test), which is the gap finding 2 names.
Then restored: `copy.ts`'s SHA-256 matches the checkout's (`cfa33b17…`), and the file's 21 tests pass.

### Commands and results

All in `apps/mobile`, in the clean environment.

| Command | Result |
|---|---|
| `npm ci --ignore-scripts` (with the proxy and CA variables by reference) | `added 651 packages, and audited 652 packages in 22s`; `22 moderate severity vulnerabilities` (npm audit's line; no lock change) |
| `node --test src/chat/display-rule.test.ts` | `ℹ tests 21`, `ℹ pass 21`, `ℹ fail 0` (20 at `cdc7c48`; the planted-forms test is new) |
| `npx tsc --noEmit`; `npx eslint .` | no output (pass) |
| `git diff --check` | no output |
| **`npm run check`** at the code head | exit 0; `ℹ tests 650`, `ℹ pass 650`, `ℹ fail 0` (649 at `3db50d8`) |
| The 22 reversals and finding 2's reversal above | each test run `exit 1` with the edit, `exit 0` restored; each file's hash checked |

`check:expo` and `export:development` were not run: C1 changes one test file, which neither reads (the brief's D5 names them for the item; the prompt asks for `npm run check`). The run of record runs both.

### The run of record

**Push run 41383619096** ([run](https://github.com/amthorn78/glow-dating-app/actions/runs/41383619096)), on the code head `0881db514b96dd6b35ae54f8759af68dee20e3d7`, read through the GitHub tools after it completed (`status: completed`, `conclusion: success`). Nothing was pushed while it ran: the records commits were held locally until it completed (AM8-20).

| Job | Conclusion | Duration (job start to completion) |
|---|---|---|
| Change scope | success: `COMPARE_BASE` `0000000…` (the branch's first push), `COMPARE_HEAD` `0881db5…`; the trusted policy printed `{"full": true, "reason": "missing-or-invalid-comparison", "paths": []}`, so every check ran | 5 s |
| API checks | success | 54 s |
| API artifact checks | success | 17 s |
| API mobile smoke | success | 1 min 24 s |
| Mobile checks | success: `npm run check` in `packages/contracts` (`@glow/contracts`), then in `apps/mobile` `npm run check && npm run check:expo`, `export:development`, the pinned Chromium installed by the workflow, and the rendered suite **`97 passed (5.0m)`**; the empty-form layout artifact uploaded (2 files). [Corrected in C2: this said "`npm run check`, `npm run check && npm run check:expo`", which reads as two steps of the mobile app. The first runs in `packages/contracts`, as the workflow's `working-directory` shows (`.github/workflows/foundation.yml`, the Mobile job); the delta re-review counted its 586 tests (nit 8).] | **7 min 27 s of the 25-minute timeout** (03:32:14 to 03:39:41 UTC) |
| Stream proof checks | success (offline checks; no provider call) | 1 min 29 s |
| Database proof checks | success | 7 min 20 s of 30 |
| Foundation gate | success; its line: **`Application checks passed`** | 3 s |

The session read the gate's and the Mobile job's log tails; it did not read the unit-test count from the Mobile job's log. The local `npm run check` count is 650.

### What could not run, and limits

- **The rendered suite on the pinned browser** runs only in CI (`playwright install` is forbidden here); it was not run locally. C1 changes no rendered path; the run of record runs the suite.
- **The checks are tests over source.** The type check follows types inside two files; the forms it does not reach are listed above.
- **No change outside the owned paths:** `git diff --name-only cdc7c48 HEAD` lists `apps/mobile/src/chat/display-rule.test.ts` and this record. No runtime file, guard, dependency or lock changed. Nothing met the stop rule.

## Manager verification (1 November 2026, App Manager 8)

- **The branch:** `claude/practical-wozniak-fg1e2i`, code head `3db50d8`, records head `02f1972`: nine commits on `67b0201`, one per item, then the draft record and its completion. Integrated into the manager branch by fast-forward.
  - The 25 paths of `67b0201..3db50d8` are all inside the brief's owned paths: 17 modified, 6 added, 2 deleted (`src/hooks/use-recommendations.ts` and `src/data/fixtures.ts`, which only that hook imported). [Corrected by App Manager 8 after the exact-head review, finding 7: this said "18 changed, 5 added, 2 removed"; `git diff --name-status` gives 17, 6 and 2 (AM8-21).] No `package.json`, lock or inventory changed. `02f1972` adds this record only.
  - The trusted policy from `main` classified `bac3c19..02f1972` as full scope (`behavior-or-empty`), and `git diff --check` printed nothing.
- **The guards, read in the diff:**
  - `src/app/_layout.tsx` now calls `developmentPreviewAvailable(__DEV__, process.env.EXPO_PUBLIC_GLOW_MODE)`, which returns `isDevelopment && mode === 'fixture'`: the negation of the old `!__DEV__ || mode !== 'fixture'`, so the guard allows exactly what it did. The layout still passes the mode itself, so Expo rewrites that read as it rewrites the two unchanged reads (`onboarding/context.tsx`, `discovery/context.ts`): a development bundle reads it through Expo's env module, `_expoVirtualEnv.env.EXPO_PUBLIC_GLOW_MODE`. [Corrected by App Manager 8 after the exact-head review, finding 10: this said "so Expo still inlines it there", which the manager had not checked in a bundle (AM8-21).]
  - `app.config.ts` changes in its comment only.
- **The behavior changes the brief asked for,** read in `src/chat/store.ts`: a newest-page reload sets the older-page state to `idle` whatever it was (the P06.2 brief's carried entry); a final refusal that does not end access restores the draft when none has been started (finding 4). `src/chat/rows.ts` makes a `closed` conversation show the unavailable wording with no open control.
- **The run of record,** read by the manager: push run 41359462167 on `3db50d8`: all eight jobs succeeded; the gate printed `Application checks passed`; the rendered suite printed `97 passed (4.3m)`; Mobile 5 min 58 s of its 25 minutes, Database proof 7 min 12 s of 30. Runs 41355778256 (on `3db50d8`) and 41359453519 (on `67b0201`) are cancelled, and 41356042982 (on the draft record) ran change scope and the gate only, as the session's record says.
- **Re-run by the manager,** in a scratch copy of `3db50d8` outside the checkout, in a clean environment: `npm ci --ignore-scripts` (651 packages); `npm test`, 649 of 649 passed. Six reversals, each restored afterwards (the copy's `git status` clean), each failing as the record says:
  - `app.config.ts`'s allow-list turned into a deny-list of `production`: `build-guard.test.mjs`, 1 failure;
  - the public-name allow-list turned into an `EXPO_PUBLIC_GLOW_` prefix rule: `build-guard.test.mjs`, 1 failure;
  - `developmentPreviewAvailable` without `isDevelopment`: `release-guard.test.ts`, 1 failure;
  - the older-page line restored to its `'loading'`-only form: `store.test.ts`, 2 failures;
  - the draft restore disabled: `store.test.ts`, 3 failures;
  - a `console.info` added to `src/chat/store.ts`: ESLint's `no-console`, 1 error.
- **The push that cancelled the first run** was the prompt's gap: it did not tell the session to hold a records push while the code head's run was in progress (AM8-20). Nathan approved the session's `--force-with-lease` reset of its own branch to `67b0201` and the fast-forward push of `3db50d8`, which rewrote no commit.
- **Not re-checked by the manager:** the rendered reversals (the session ran them against the preinstalled Chromium, informational), the remaining unit reversals, and item 3's added strings beyond the four the brief named, which the session's provider-wording test covers.
- **Records outside the session's paths:** `docs/architecture/profiles-preferences-fixtures.md` describes the removed hook historically; a note now says it was removed in P06.2-F. `docs/continuity/claude-code-handoff.md:41` is the frozen handoff of 25 September and is left as it was.
- **Next:** the PR, Codex's review of its head, and the exact-head code review of `3db50d8`.

## Exact-head review of P06.2-F (2 November 2026)

- **The review:** an exact-head code review that Nathan ran from the review prompt, revision 1 at `a007328`, of code head `3db50d8`. The start gate passed (one merge base, `05f4c3a`; no non-Markdown path changed after `3db50d8`), and the trusted classifier read full scope (`behavior-or-empty`). It changed nothing; Nathan relayed its report.
- **Verdict: changes required,** in one test and the records. The runtime code needs no change:
  - no guard allows anything new: `isDevelopment && mode === 'fixture'` is the exact negation of the old condition; the layout's read gets the same Expo rewrite as the two unchanged reads; `app.config.ts` changes in comments only; the route guards are unchanged; and no path opens a `closed` conversation (each other way in ends in a fresh read, which Glow refuses);
  - no test is weakened: the 621 unit tests at `67b0201` are all present among the head's 649, the one renamed test aside, and 19 named reversals fail as recorded;
  - the older-page state and the draft restore are correct, with DM-29 1.1 and DM-30 2.1 and 2.2 tested; optional finding 9's reason holds (that line also sends the `readHead(true)` an unmatch, block or pause queues for a hidden conversation);
  - the removed modules have no importer; item 7's two assertions pin the landing; the README matches the code.
- **Both runs passed:** push run 41359462167 on `3db50d8` (eight of eight jobs, `Application checks passed`, rendered `97 passed (4.3m)`, Mobile 5 min 58 s of 25), and PR run 41362003818 on `a007328` (eight of eight, `Application checks passed`).
- **The manager confirmed finding 1** in a scratch copy of `3db50d8`, outside the checkout: with `MessageRow`'s binding renamed to `item` and `{'name' in item ? <Text …>{String(item.name)}</Text> : null}` added, `tsc` passed and so did the render-rule test. The file was restored and its hash checked.

**The findings and their dispositions** (the manager, by step 6's rule):

| # | Finding | Severity; class | Disposition |
|---|---|---|---|
| 1 | The render-rule check reads only paths reached through six variable names (`message`, `conversation`, `list`, `state`, `match`, `row`). A provider-shaped field rendered through a renamed binding, or through a loosely typed helper prop, passes `tsc` and the test (the helper form passes ESLint too). The record's limit said only "a determined edit" evades it | Should fix; in two classes (a test passes where it should fail; a record claims more than the tests show) | **Fixed before the merge,** by correction C1 (the brief, "Correction C1") |
| 2 | The copy test's word list (`display-rule.test.ts:18`) has no plurals and lacks `cloudflare` and `allauth`, which item 3's list has | Nit | **In C1,** which changes the same file and the same family of tests |
| 3 | No test fails when the restore's `!ends(failure.code)` is removed: `revoke()` clears the draft afterwards, but one snapshot in between holds the refused text | Nit | **A recorded follow-up,** in the P06.2 brief's "Carried to later changes", at the next change to `store.ts` |
| 4 | The server and the fixture check the contact version before replaying an idempotent send, so a retry whose first attempt committed could be refused `stale_version`, and the restored draft would invite a duplicate under a new key. Not reachable at this head: the contact version rises only when contact ends, and the match-state check runs first | Nit; P11's | **To the P11 plan,** beside C2-X2 (rule (c)) |
| 5 | Item 5's "unless the member started a new one while it was pending": the composer cannot be edited while a send is pending (`screen.tsx:75`); the case arises through Retry | Nit (records) | **Corrected in C1,** in the record |
| 6 | The record gives Mobile 5 min 56 s; the job ran 22:54:52 to 23:00:50 UTC, 5 min 58 s | Nit (records) | **Corrected in C1** |
| 7 | The Manager verification's "18 changed, 5 added, 2 removed"; `git diff --name-status` gives 17, 6 and 2 | Nit (records) | **Corrected above,** marked (AM8-21) |
| 8 | The record says the checker is tested against "seven planted forms"; the test lists nine | Nit (records) | **Corrected in C1** |
| 9 | `no-dead-modules.test.ts` counts a test as an importer, and does not resolve imports through the `@/` alias | Nit (a limit) | **Recorded here as a limit.** It fails loudly, not silently, and no file uses the alias today |
| 10 | "Expo still inlines the mode there": a development bundle reads it through Expo's env module | Nit (records) | **Corrected** in the Manager verification above, marked (AM8-21), and in the record's item 1 by C1 |

- **Outside this item:** the chat fixture controls label their synthetic test fields "Provider field: …" on development-preview screens (`chat/controls.tsx`); no finding.
- **Codex** found nothing on `b924afa`, PR40's first head. It did not start on `a007328`; at Nathan's direction the manager posted `@codex review` once on PR40, and Codex's review of `a007328` completed with no finding (2 November, 00:28 UTC).
- **Next:** correction C1, its run of record, Codex on its head, and a delta re-review (step 6: C1 changes no non-test line).

## Manager verification of correction C1 (2 November 2026, App Manager 9)

- **The branch:** `claude/trusting-cori-gxlila`, started at `cdc7c48`: code head `0881db5` (one commit, `apps/mobile/src/chat/display-rule.test.ts` only, +310 −12), then records `f4022b7` and `0e98f25` (this record only, +145 −6). `git diff --name-only cdc7c48 0e98f25` lists the two owned paths. "Manager verification" and "Exact-head review of P06.2-F" are byte-identical to `cdc7c48`.
- **The diff, read whole:** the source check is kept (its six-name path list and its refusals), with an `in` check on a string literal added; the type check and the 22 planted forms are as "Correction C1" describes; each planted form asserts the violation it must produce, so a checker that loads nothing fails the planted test. No runtime file, guard, dependency or lock changed.
- **Local checks,** in a scratch worktree of `0881db5` outside the checkout, in the clean environment: `npm ci --ignore-scripts`; `npm run check`, exit 0, `ℹ tests 650`, `ℹ pass 650`, `ℹ fail 0` (27.8 s); `node --test src/chat/display-rule.test.ts`, 21 of 21 (5.0 s).
- **Reversals re-run** as real edits to `screen.tsx` (and `copy.ts`) by a scratch script, each file's SHA-256 checked after its restore:
  - **PA** (the binding renamed to `item`, rendering `{'name' in item ? String(item.name) : null}`): the render test fails; restored, 21 of 21;
  - **PB** (`<Eyebrow entry={message} />` with the loose prop): fails with `a widening to { name?: string | undefined; text: string | null; }: message`; restored, 21 of 21;
  - **PC** (`const { name: label } = item`): fails with `a field outside Glow's types: name: label`; restored, 21 of 21;
  - **finding 2** (`READ_COPY.unavailable` → "Our providers cannot show this conversation."): fails with `AssertionError [ERR_ASSERTION]: Our providers cannot show this conversation.`; restored;
  - **the named evasion:** a new `src/chat/probe-eyebrow.tsx` taking the exact `ConversationMessage` and casting inside, rendered from `screen.tsx`, passes the test (21 of 21) and `tsc` (exit 0), as "Forms known to evade the check" says. Removed afterwards.
  - **A coupling, which fails closed:** an edit to `screen.tsx` also fails the planted-forms test when it moves one of its anchors ("the anchor occurs once"), as the record's PA row says. A later change to those lines moves the anchors with it.
- **The run of record, read from its logs:** push run 41383619096 on `0881db5`, eight of eight jobs `success`; the gate printed `Application checks passed`; the Mobile job's unit tests `ℹ tests 650`, `ℹ pass 650`, `ℹ fail 0` (the line the session did not read); rendered `97 passed (5.0m)`; Mobile 03:32:14 to 03:39:41 UTC, 7 min 27 s of 25. Its `npm run check && npm run check:expo` step took 24 s; the time added since `3db50d8`'s run is in `npm ci` and the rendered step, not the new check.
- **Integrated** into the manager branch by a merge commit, `8b0b72a` (the branch had moved past `cdc7c48` with Markdown only); every non-Markdown path at it is byte-identical to `0881db5`. The trusted classifier (from `origin/main`, full SHAs) reads the PR full scope (`behavior-or-empty`), with one merge base, `05f4c3a`.
- **Next:** the PR run and Codex on PR40's head, then the delta re-review of `0881db5` ([prompt](../../ephemeral/2026-11-02-p06-2-f-c1-delta-review-prompt.md), revision 1).

## Delta re-review of correction C1 (2 November 2026)

- **The review:** a delta re-review on M05 S2's terms that Nathan ran from the prompt, revision 1 at `c6108e4`, of code head `0881db5`. The start gate passed (one merge base, `05f4c3a`; no non-Markdown path changed after `0881db5`; the live head `06ec8b6`, Markdown only), and the trusted classifier read full scope (`behavior-or-empty`). It changed nothing; Nathan relayed its report.
- **Verdict: changes required.** C1 closes PA, PB, PC and all 22 planted forms, each for its named reason; no earlier check is weakened (`sourceViolations` is the old check plus the `in` line; the nine old forms keep their assertion; the copy tests are unchanged apart from the wider word list); finding 2 is closed; no dependency, lock, runtime or bundle change. But the type check does not hold its claim "through any binding": more than 20 edits confined to `screen.tsx` or `rows.ts` render a provider-shaped field and pass the test, `tsc` and ESLint, none through another module or a template literal.
- **Both runs passed:** push run 41383619096 on `0881db5` (eight of eight, `Application checks passed`, 650 unit tests, `97 passed (5.0m)`), and PR run 41446234782 on `06ec8b6` (eight of eight, `Application checks passed`, 650, `97 passed (5.0m)`). Codex found nothing on `c6108e4` or `06ec8b6`.
- **The manager confirmed findings 1 to 3** in a scratch worktree of `0881db5`, each a real edit to `screen.tsx`, the file's SHA-256 checked after each restore: a wrapper held in a variable (`const wrap = { m: message }`, given to a helper whose loose prop renders `entry.m.name`), a declared function passed by reference (`[message].map(shout)`), and an aliased `Object.assign` (`const { assign: merge } = Object`, its result given to a loose prop) each passed the test (21 of 21) and `tsc`. Two of its first variants, an inline wrapper literal and a direct `.name` read of the merged value, were caught: the gaps are where the data is held or passed, not every form near them.

**The findings** (dispositions wait on DM-38, below):

| # | Finding | Severity; class |
|---|---|---|
| 1 | `carries` (`display-rule.test.ts:215`) recognises Glow's data only as the value itself or an array or tuple of it, at most four levels deep. Data held in an object wrapper, a closure, a Map, Set or WeakMap, a Promise, a generator, a class field, a JSX spread of a wrapper, or arrays nested five deep can be re-typed loosely with no refusal (the review's W1, W1b, W2, W4, W5; the probe's a01 to a24, a15b in `rows.ts`) | Should fix; in two classes (the test passes where it should fail; a field reaches output outside the named evasions) |
| 2 | The widening-callback-parameter check (`:335-345`) covers only inline, annotated arrow or function expressions; a declared function passed by reference is never compared (a03, a13b) | Should fix; the same two classes |
| 3 | (a) A local type guard or assertion function narrowing to `ConversationMessage & { name: string }` passes, since `keeps` finds `name` on the intersection; (b) `Reflect.get(message, 'name')` is caught only by the source check's literal `Reflect.`, and `const { get: pick } = Reflect` evades both; (c) `const { assign: merge } = Object` evades the source check's `Object\s*\.`, and `merge({ name: '' }, message)` passes the type check (a04, a19b, R1, R3, a05, a22) | Should fix; the same two classes |
| 4 | Two exceptions are wider than described: (a) the dependency-list exception applies to any call whose array argument is `@types/react`'s `DependencyList`, not only hooks (D1; its `readonly unknown[]` control is refused); (b) the destructuring exception exempts a nested binding element's default even under an annotated outer pattern (a18) | Should fix; the same two classes |
| 5 | The record's "finds Glow's data by type … through any binding", "every way that type can be dropped or widened in the file is either a refusal above or a type error" and "a name built from fragments, read without an element access (none known)", and the test comment's matching lines, claim more than findings 1 to 4 allow; "Forms known to evade the check" lists two | Should fix; a record claims more than the code and tests show |
| 6 | Nothing checks that each `GLOW_DATA` path exists or is exercised: misspelling `gapp-dev-v1` or `interactions/store.ts` still passes (21 of 21); `fixture-adapter` fails closed | Nit |
| 7 | The planted forms are coupled to `screen.tsx` (single-occurrence anchors, fixed helper names); a harmless edit can fail the planted test until the list is updated. It fails closed | Nit; the review judges it acceptable |
| 8 | The record's Mobile row lists "`npm run check`, `npm run check && npm run check:expo`"; the first step runs `@glow/contracts` (586 tests), not the mobile app | Nit (records) |

- **The manager's share:** its verification of C1 confirmed the planted forms and the one named evasion, and then repeated the session's "through any binding" in the review prompt, Notion and its reply on Codex's thread without trying forms of its own (AM9-03).
- **Next:** the disposition. Step 6's rule (a) puts findings 1 to 5 before the merge, since each falls in a correction class the review prompt names; the fix's design (extend the check, narrow its claim with cheap hardening, or change how the screens hold data) and the display-rule boundary it guards go to the Dev Manager first (DM-38; the charter; step 6).
- **Codex on `903c41f`** (2 November, 16:34 UTC) raised two P2 threads, both this review's findings: data held in an object wrapper (`display-rule.test.ts:215`, finding 1) and a callback passed by reference (`:339`, finding 2). The manager answered both; they stay open until C2 is on PR40.

**The dispositions** (DM-38, [report](../../continuity/dev-manager/reviews/2026-11-02-dm-38-p06-2-f-render-rule-check.md), answered at `f019911`, accepted as written):

| # | Disposition |
|---|---|
| 1 | **Not fixed; settled by the narrowed claim.** Data held inside another value (a group or section, a list's render-item wrapper, a view-model object, a closure or a container) becomes a named limit that an ordinary refactor reaches (DM-38 2.3), and option (c), view models by explicit field copy, is carried to the next change to how the chat screens hold their data (2.5; the carried-items file). Codex's thread at `:215` is answered on that basis when C2 is on PR40 |
| 2 | **Fixed in C2** (2.1): a function passed by reference is compared against what the caller passes, as an inline callback is; planted forms for the review's `shout`, a render function, a `useCallback` function and a method. Codex's thread at `:339` closes with it |
| 3 | **Fixed in C2** (2.2, 2.6): type predicates and assertion signatures refused by resolved signature, except the default library's, and when declared in the two files; `Reflect`, and `Object` members other than `freeze`, refused by identifier however aliased |
| 4 | **Fixed in C2** (2.6): the dependency-list exception only as an argument of a React hook call; the destructuring exception only when no enclosing pattern is annotated |
| 5 | **Fixed in C2:** the test comment, this record and the brief state DM-38 section 4's guarantee and limits, with the `FlatList` false positive recorded (2.4) |
| 6 | **In C2** (nit): a missing or unexercised `GLOW_DATA` path fails the test |
| 7 | **A recorded limit** (nit): the planted forms' anchors fail closed |
| 8 | **In C2** (nit): the Mobile row of "Correction C1"'s run of record names the `@glow/contracts` step as such |

- **Next:** correction C2 (the brief, "Correction C2").

## Correction C2 (2 November 2026)

- **Work:** the brief's "Correction C2" (revision 2), Outcome 1 to 7: C1's delta re-review, findings 2 to 5 with nits 6 and 8, under DM-38's conditions 2.1 to 2.6. Finding 1 is not fixed; it is the named limit below (DM-38 2.3).
- **Prompt:** [`docs/ephemeral/2026-11-02-p06-2-f-c2-correction-prompt.md`](../../ephemeral/2026-11-02-p06-2-f-c2-correction-prompt.md), revision 1, from `007377e81cdead1fbf0b67c23f99dcfad20e5c56` of the manager branch `claude/magical-wozniak-yfmmx2`. Started by Nathan.
- **Branch:** `claude/inspiring-ramanujan-tjpril`, started at `007377e`.
- **Code head:** `816cd607019e69442f99007ef6324c9aa00dd83c`. Three code commits, each to `apps/mobile/src/chat/display-rule.test.ts` only:
  - `345e311`, the change;
  - `082506f` and `816cd60`, two gaps in C2's own refusals that the session's probes found after the first push (below).
- **Records head:** the last commit on the branch, Markdown only (this record); no code after the code head.
- **Run of record:** push run **41513359474** on `816cd60`: all eight jobs `success`, `Application checks passed`, 650 unit tests, rendered `97 passed (4.9m)`, Mobile 7 min 31 s of 25.

### Environment check (names only)

- `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`: none present.
- `STREAM_*`: no name present. The session ran in `Glow App - No Stream`.
- `GH_TOKEN` and `GITHUB_TOKEN` are present; never read. Every app command ran without them.
- **Toolchain:** `node --version` → `v24.19.0`; `npm --version` → `11.9.0`, both from `$HOME/.local/bin`. Every npm and Node command ran in `env -i PATH="$HOME/.local/bin:$PATH" HOME="$HOME" LANG=C.UTF-8`; `npm ci` also passed `HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS` by reference, never printed.

### Start gate

| Check | Result |
|---|---|
| `git fetch origin claude/magical-wozniak-yfmmx2 main` | fetched; `origin/claude/magical-wozniak-yfmmx2` = `007377e81cdead1fbf0b67c23f99dcfad20e5c56`, `origin/main` = `bac3c1983134f4e977f867ac30b3086b5318216f` |
| `git switch -C claude/inspiring-ramanujan-tjpril 007377e…`; `git rev-parse HEAD` | `007377e81cdead1fbf0b67c23f99dcfad20e5c56` |
| `git merge-base --is-ancestor 007377e… origin/claude/magical-wozniak-yfmmx2` | `this prompt's commit is on the live branch` |
| `git diff --quiet 0881db5… HEAD -- .github scripts services apps packages proofs` | `the code head under correction` |
| `git diff --quiet 0881db5… origin/claude/magical-wozniak-yfmmx2 -- …` (the same paths) | `no code on the live branch after 0881db5` |
| `git show origin/claude/magical-wozniak-yfmmx2:<this record> \| grep -c -E '^#+ Correction C2'` | `0` |
| `git ls-remote origin claude/inspiring-ramanujan-tjpril` | nothing (a new branch) |

**Read before the work:** root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md` and `CLAUDE.md`; the brief, whole; this record's "Correction C1", "Manager verification of correction C1" and "Delta re-review of correction C1"; DM-38's report, whole; ADR 0003; `src/chat/display-rule.test.ts`, `src/chat/screen.tsx` and `src/chat/rows.ts`, whole. Expo's documentation was not needed: C2 touches no Expo API.

### The change

One file, `apps/mobile/src/chat/display-rule.test.ts`, +222 −39 from `007377e` to `816cd60`. `screen.tsx` and `rows.ts` are unchanged (SHA-256 `3aef02c3…` and `bdce90ca…`), and both pass both checks: no exception was added and nothing met the stop rule. The source check is unchanged. Every earlier refusal of the type check, and every earlier planted form with its assertion, is kept. What C2 adds to the type check:

1. **A function given by reference** (finding 2; DM-38 2.1). Any expression with a call signature, other than an inline arrow or function expression, is compared against the expected signature. That signature is the call's resolved parameter, or the contextual type of an annotation, a return, an assignment or a prop.
   - **Each parameter, `this` included:** a parameter that widens what the expected signature gives it is refused as `a widening by reference to <type>`.
   - **The return** (`082506f`): a return of Glow's data that the expected signature's return widens is refused as `a widening by reference of its return to <type>`.

   Inline callbacks keep C1's check.
2. **Type predicates and assertion signatures** (finding 3a; 2.2). Each is refused unless its signature is the default library's:
   - declared in the two files, by syntax (`x is T`, `asserts x`) and by the declaration's signature, which also catches an inferred predicate;
   - at a call whose resolved signature has one, so a guard imported from another module is refused where it is called;
   - given by reference rather than called (`816cd60`), so an imported guard given to the default library's `filter`, `find` or `every` is refused too.
3. **`Reflect`, and `Object` other than as `Object.freeze`'s receiver** (findings 3b, 3c; 2.6). Each is refused three ways:
   - by identifier, when it resolves to the default library's global;
   - by an expression's type, when that type is the default library's `Reflect` or `ObjectConstructor`;
   - by a destructuring's type, whatever its key (`816cd60`).

   So these are all refused: `const { get: pick } = Reflect`, `const { assign: merge } = Object`, `globalThis.Object`, `const { 'Reflect': { get: pick } } = globalThis` and `const { ['Object']: { assign: merge } } = globalThis`.
4. **The two exceptions narrowed to their words** (finding 4; 2.6):
   - the dependency-list exception applies only to an array literal given as an argument of a call whose resolved signature is a function named `use…` declared in `@types/react`;
   - the destructuring exception applies only when no enclosing pattern, up to the variable or parameter, is annotated.
5. **`GLOW_DATA` is checked** (nit 6): the first test asserts that each listed path exists, and that the type check matched a declaration in each while checking today's two files. All six paths are matched today. `interactions/fixture-adapter.ts` is matched at `match.profile`, a field read.
6. **The guarantee** (finding 5; 2.3, 2.4): the render-rule comment states DM-38 section 4's guarantee word for word (checked by a script against the report's text), then the refusals and exceptions in the check's own terms. It names finding 1's class as the limit an ordinary refactor reaches, with option (c) for the next change to how the screens hold or render chat data (2.5), and records the `FlatList` false positive with its failing output.
7. **The false positive is pinned:** F0 is run by the planted test, which asserts that it fails closed, and for that one reason alone (`FALSE_POSITIVE`).

The planted test now has 38 forms (C1's 22 and C2's 16) and the false positive. `typedViolations` takes an optional map of served modules, which the checked files may import but which are not checked themselves, for the imported-guard forms. It returns its violations together with the `GLOW_DATA` files it matched. "Through any binding" is gone from the test. In this record, "Correction C1"'s wording ("through any binding", in its "Finding 1" and its limit) is superseded by the guarantee below; this section does not edit it, since C2 changes only that section's Mobile row.

**The guarantee, as the test states it:**

> The check follows Glow's data by its own type: at a property read, a destructuring, a spread, an enumeration and an `in` check, and wherever the data is passed, returned, assigned, annotated, given as a prop, or given to a callback, inline or by reference. It refuses type predicates and assertion signatures, references to `Reflect` and to `Object` members other than `freeze` however aliased, and any type error. It does not follow data held inside another value (a group or section, a list's render-item wrapper, a view-model object, a closure or a container), another module, or a template literal's coercion. It refuses some harmless code, such as a list component over Glow's data. It is a test over two files' source, not a proof over all programs.

**Its limits, as the test states them:**
- **Finding 1's class.** Data held inside another value is the limit an ordinary refactor reaches, not only a deliberate evasion. Grouped sections, a render-item wrapper or a view model can carry a message to a loosely typed helper, which then renders a provider-shaped field, and the check passes it. The next change to how `screen.tsx` or `rows.ts` hold or render chat data moves them to view models built by explicit field copy, with its own check (DM-38 2.5).
- **The false positive (DM-38 F0).** A harmless `<FlatList data={conversation.messages} keyExtractor={entry => entry.submission_id} renderItem={({ item }) => <Text>{item.text ?? ''}</Text>} />` fails with `a widening to Readonly<ArrayLike<ConversationMessage>> | undefined: conversation.messages`, since `ArrayLike` has an index signature. It fails closed, and that change changes the design rather than loosening the check.

**What this record claims.** Only the forms tested are claimed: the 38 planted forms, the reversals, and the session's own forms below. The probes found forms outside every limit (the session's findings, below). For those forms, the guarantee's words claim more than the check shows.

### Each new planted form as a reversal

Each form was also run as an **edit to `screen.tsx` in a scratch copy** of `apps/mobile` and `packages` outside the checkout, with the checkout's `node_modules` linked. The edits were generated from the test's own `PLANTED` list at `816cd60` (the test module loaded with `test` replaced by a no-op), so each is exactly the edit the test plants. For the imported-guard forms, the guard module was also written as a real `src/chat/planted-guard.ts` in the copy.

For each edit, these ran:
- the new test, `node --test src/chat/display-rule.test.ts`;
- the test as it stood at `0881db5`, which is `007377e`'s;
- `npx tsc --noEmit` and `npx eslint src/chat/screen.tsx`.

Then `screen.tsx` was restored from the snapshot and its SHA-256 checked against the original (`3aef02c3…`, each time), the guard removed, and the new test run again.

**All 17 failed the new test with the edit in place, and passed once undone** (`ℹ pass 21`, `ℹ fail 0` each time). Each with the edit gives `ℹ pass 19`, `ℹ fail 2`. The first test fails with the edit's violation (below). The planted test fails at F0's exact assertion, because F0's text carries the edit's violation as well; it fails closed. For C2-4a and F0 it fails earlier: their edits change an import line that a planted form anchors on (the review's nit 7).

The column "at `0881db5`" gives that version's two checks run alone on the edit, by its own `sourceViolations` and `typedViolations`. Every edit passes `tsc` and ESLint.

| # | Planted form | First test's failing output (new test) | At `0881db5`: source / type check |
|---|---|---|---|
| C2-1a | the review's `shout`: `[message].map(shout)`, with `shout(entry: { name?: string; text: string \| null })` returning `entry.name` | `a widening by reference to { name?: string \| undefined; text: string \| null; }: shout` | `[]` / `[]` |
| C2-1b | a render function: `{conversation.messages.map(renderEntry)}`, with `renderEntry(entry: …)` rendering `entry.name` | the same kind, `…: renderEntry` | `[]` / `[]` |
| C2-1c | a `useCallback` function: `const renderRow = useCallback((entry: …) => entry.name ?? '', [])`, used as `.map(renderRow)` | `…: renderRow` | `[]` / `[]` |
| C2-1d | an object's method: `const view = { line(entry: …) { return entry.name ?? ''; } }`, used as `.map(view.line)` | `…: view.line` | `[]` / `[]` |
| C2-1e | a function returning Glow's data by reference into a wider type: `function identity(entry: ConversationMessage) { return entry; }`, then `conversation.messages.map<…>(identity).map(entry => entry.name)` | `a widening by reference of its return to { name?: string \| undefined; text: string \| null; }: identity` | `[]` / `[]` |
| C2-2a | a local type guard `named(entry: ConversationMessage): entry is ConversationMessage & { name: string }`, then `{named(message) && <Eyebrow entry={message} />}` (PB's loose helper) | `a call to a type predicate or assertion: named(message)`, `a type predicate or assertion by reference: named` and twice `a type predicate or assertion signature: …` | `[]` / `[]` |
| C2-2b | a local assertion function `assertNamed(entry): asserts entry is ConversationMessage & { name: string }`, called in `MessageRow`, then `<Eyebrow entry={message} />` | `a call to a type predicate or assertion: assertNamed(message)`, with the by-reference and signature refusals | `[]` / `[]` (the old planted test failed, since the assertion also narrows `message` for old form 2) |
| C2-2c | the same guard **imported** from another module (`./planted-guard`), then `{named(message) && <Eyebrow entry={message} />}` | `a type predicate or assertion by reference: named` (at the import), `a call to a type predicate or assertion: named(message)` | `[]` / `[]` |
| C2-2d | a local guard given to the **default library's `filter`**: `conversation.messages.filter(named).map(entry => <Eyebrow key={entry.submission_id} entry={entry} />)` | `'conversation.messages.filter'` (the source check, which runs first); in memory the type check reports `a type predicate or assertion signature: entry is ConversationMessage & { name: string }` | `['conversation.messages.filter']` / `[]` |
| C2-2e | an **imported** guard given by reference to the default library's `filter`: `const all = conversation.messages;`, then `all.filter(named).map(entry => <Eyebrow … entry={entry} />)` | `a type predicate or assertion by reference: named` (at the import and at the use) | `[]` / `[]` |
| C2-3a | an aliased `Reflect`: `const { get: pick } = Reflect;`, rendering `{String(pick(message, 'name'))}` | `a reference to Reflect or an Object member: { get: pick }`, and twice `…: Reflect` (by identifier and by type) | `[]` / `[]` |
| C2-3b | an aliased `Object.assign`: `const { assign: merge } = Object;`, then `<Eyebrow entry={merge({ name: '' }, message)} />` | `a reference to Reflect or an Object member: { assign: merge }`, and twice `…: Object` | `[]` / `[]` |
| C2-3c | `Reflect` by a string key: `const { 'Reflect': { get: pick } } = globalThis;`, rendering `{String(pick(message, 'name'))}` | `a reference to Reflect or an Object member: 'Reflect': { get: pick }` and `…: { get: pick }` | `[]` / `[]` |
| C2-3d | `Object` by a computed key: `const { ['Object']: { assign: merge } } = globalThis;`, then `<Eyebrow entry={merge({ name: '' }, message)} />` | `a reference to Reflect or an Object member: ['Object']: { assign: merge }` and `…: { assign: merge }` | `[]` / `[]` |
| C2-4a | a dependency list outside a hook: `function keep(list: DependencyList) { return JSON.stringify(list[0]); }`, rendering `{keep([message])}` | `'a reflective read'` (the source check, at `JSON.`); in memory the type check reports `a widening to DependencyList: [message]` and `a widening to unknown: message` | `['a reflective read']` / `[]` |
| C2-4b | a default under an annotated outer pattern: `const { inner: { name: label } = message }: { inner?: { name?: string; text: string \| null } } = {};`, rendering `{label}` | `a widening to { name?: string \| undefined; text: string \| null; } \| undefined: message` | `[]` / `[]` |
| F0 | the harmless `FlatList` (the false positive, not a planted form) | `a widening to Readonly<ArrayLike<ConversationMessage>> \| undefined: conversation.messages` | `[]` / the same widening |

**At `0881db5`, the type check alone passed all 16 new forms.** The source check refused two of them: C2-2d by its path list, and C2-4a at `JSON.`. For every new form, this test is the only check standing between it and the screen.

**Each mechanism as a reversal.** Each new piece of the check was undone in a scratch copy of the test at `816cd60`. For each, the test was run, and the file restored and its hash checked (`262e20e3…`):

| Reversal in the test | Result |
|---|---|
| R1: the by-reference comparison off | `ℹ fail 1`: `the type check: C2-1a, the review's shout … : []` |
| R1b: the return comparison off | `ℹ fail 1`: `the type check: C2-1e …` |
| R2: every predicate refusal off | `ℹ fail 1`: `the type check: C2-2a …` |
| R2b: the declared-in-file refusals off | `ℹ fail 1`: `the type check: C2-2d …`. Before C2-2d was added, this reversal **passed**: the call refusal alone caught every predicate form then planted. So C2-2d was added before the first code commit, to pin 2.2's second half |
| R2c: the call refusal off | `ℹ fail 1`: `the type check: C2-2a …` |
| R2d: the by-reference predicate refusal off | `ℹ fail 1`: `the type check: C2-2e …` |
| R3: every `Reflect` and `Object` refusal off | `ℹ fail 1`: `the type check: C2-3a …` |
| R3b: the destructuring-type refusal off | `ℹ fail 1`: `the type check: C2-3c …` |
| R4: the dependency-list exception as at C1 (any call) | `ℹ fail 1`: `the type check: C2-4a …` |
| R5: the destructuring exception as at C1 (any binding element) | `ℹ fail 1`: `the type check: C2-4b …` |
| R6: a `GLOW_DATA` path misspelled (`gapp-dev-v1` → `gapp-dev-v2`) | `ℹ fail 1`: `a GLOW_DATA path exists: …/gapp-dev-v2.ts` |
| R7: an existing path no checked type comes from, added to `GLOW_DATA` (`./copy.ts`) | `ℹ fail 1`: `each GLOW_DATA path is one the type check found Glow's data in` |

### Forms of the session's own

**How they were tried.** Seven probe agents worked in parallel, each in its own scratch copy, each assigned the guarantee's mechanisms. Between them they tried **256 forms**, each as a real edit to `screen.tsx` or `rows.ts` (or a new module, for the "another module" limit). For every form they ran:
- the render test, `tsc --noEmit` and ESLint;
- then a restore of the file, with its hash checked.

**The judging.** Each form was judged against the guarantee's words: caught, inside a named limit (which one), outside every limit, or a false positive. A second, adversarial agent per group then re-ran every form that passed and tried to refute its classification. The probes and verifiers ran against `345e311`'s test.

**The consolidated re-run.** All 70 forms first judged outside every limit were then re-run against the code head `816cd60` (and against a scratch candidate, below), each time with `tsc` and the hashes checked.

| Mechanism the guarantee names | Tried | Caught | Inside a limit | False positive | Outside every limit at `345e311` → still at `816cd60` |
|---|---|---|---|---|---|
| a property read | 9 | 4 | 0 | 1 | 4 → 4 (all **N1**) |
| a destructuring | 7 | 2 | 0 | 1 | 4 → 4 (**N1**) |
| a spread | 10 | 3 | 3 (a wrapper; arrays four deep) | 1 | 3 → 3 (**N1**) |
| an enumeration | 9 | 6 | 1 (the context object) | 0 | 2 → 2 (**N3**, **N2**) |
| an `in` check | 8 | 5 | 0 | 1 | 2 → 2 (**N3**) |
| any type error | 12 | 5 | 0 | 0 | 7 → 7 (**N2**; T8 is **N3**) |
| passed | 14 | 6 | 0 | 2 | 6 → 4 (**N4**, **N5**; P4 and P4b now caught) |
| returned | 8 | 5 | 0 | 0 | 3 → 1 (**N4**; R3 and R8 now caught) |
| assigned | 12 | 5 | 1 | 0 | 6 → 4 (**N4**, **N6**; A4 and A10 now caught) |
| annotated | 16 | 13 | 1 (a view model) | 0 | 2 → 2 (**N1**) |
| given as a prop | 14 | 11 | 0 | 0 | 3 → 3 (**N1**) |
| given to a callback inline | 18 | 12 | 0 | 4 | 2 → 2 (**N1**) |
| given to a callback by reference | 19 | 11 | 0 | 0 | 8 → 8 (**N3**, **N7**, **N8**) |
| type predicates | 13 | 3 | 0 | 2 | 8 → 2 (**N9**; the imported-guard forms now caught) |
| assertion signatures | 8 | 7 | 0 | 1 | 0 |
| `Reflect`, however aliased | 13 | 7 | 1 (another module) | 0 | 5 → 0 (now caught) |
| `Object` members other than `freeze` | 14 | 6 | 1 (another module) | 3 | 4 → 0 (now caught) |
| data held inside another value | 27 | 14 | 12 (groups, wrappers, view models, closures, a ref) | 0 | 1 → 1 (**N4**) |
| another module | 7 | 2 | 5 | 0 | 0 |
| a template literal's coercion, and kin (`+`, `join`, a tagged template) | 9 | 1 | 8 | 0 | 0 |
| harmless list components and array use | 9 | 0 | 0 | 9 | 0 |
| **All** | **256** | **128** | **33** | **25** | **70 → 49** |

**Two classes of the 70 fell inside C2's own items.** Each was fixed before the run of record, with planted forms, and each fix passes today's two files with no exception:
- **a function returned by reference** (`082506f`; Outcome 1): `conversation.messages.map<Loose>(identity)` passed while the inline form was caught. Six forms. Now caught, and planted as C2-1e;
- **`Reflect` or `Object` by a string or computed key, and an imported guard by reference** (`816cd60`; Outcomes 3 and 2):
  - the destructuring forms: nine of them, such as `const { 'Reflect': { get: pick } } = globalThis`;
  - the imported guards given to the default library's `filter`, `find`, `findLast` or `every`: six forms.

  All are now caught, and planted as C2-3c, C2-3d and C2-2e.

**The session's findings: forms outside every limit at the code head.** These classes are not among Outcome 1 to 5. Each passes the test, `tsc` and ESLint, except where noted. No guarantee wording was widened to cover them. Every one rests on the guarantee's words "by its own type" and the mechanisms it names, which these forms show the check does not follow:

| # | Class | Forms (examples) | Why the check passes it |
|---|---|---|---|
| N1 | **Narrow first, then widen.** Glow's data is first given a type of its own declaring only some of its fields, then widened | `const plain: { text: string \| null } = message;` then `const loose: { text: string \| null; name?: string } = plain;` rendering `{loose.name}`. An intermediate component whose prop is `{ entry: { text: string \| null } }` hands it to PB's loose helper (X2, an ordinary refactor). `Object.freeze<{ text … }>(message)`, `useState<{ text … }>(message)`, two chained inline `map` callbacks (X3) | `keeps` accepts a narrowing, since every target field exists on the data. The narrowed type declares no field in a `GLOW_DATA` file, so the value is no longer Glow's data and nothing after it is checked. `Pick<>` and `Omit<>` keep the contract's declarations and are caught. Twenty forms (r1, r3, r4, r7, d1, d5, d6, d8, s1, s3, s7, X1, X2, X3, X5, X6, X7, X8b, P10, P10b). P10 alone renders nothing at runtime (its branch is dead); P10b, with `Symbol.hasInstance`, does |
| N2 | **A suppressed type error** | `// @ts-expect-error` (or `@ts-ignore`, or `// @ts-nocheck` at the top) above `<Caption entry={message} />`, where `Caption`'s prop is `() => void` and renders `entry.name` (`Function.name`'s slot). A function-typed, `never` or primitive target, given Glow's data under a suppression | The suppressed diagnostic never reaches `getSemanticDiagnostics`, and a function, `never` or primitive target "keeps". Seven forms (E6, T2, T3, T4, T5, T10, T11, one in `rows.ts`). T5 fails ESLint (`ban-ts-comment`); the others pass it |
| N3 | **Glow's data as `this` through `.call`** to a function that declares no `this` | `({}).hasOwnProperty.call(message, 'name')`; `const raw = ({}).valueOf.call(message)`, then a `for…in` over `raw` or a loose prop; `Array.prototype.map.call(conversation.messages, shout)`, `[].map.call(…)`, `Array.prototype.filter.call(…)` | With no declared `this`, the argument has no expected type to compare, and `Array.prototype.map`'s own `this` makes the callback's value `any`. Eight forms (E5, I4, I6, T8, R3, R14, R11, R20) |
| N4 | **A container the check does not follow:** a tuple's later elements, and arrays nested four deep | `const pair = ['label', message] as const` given to `readonly (string \| Loose)[]` (P3, R6, A8); `[[[[message]]]]` given to `readonly Loose[][][][]` (P9, K6r) | `keeps` compares only a tuple's first element against an array target, and `carries` stops at depth 4 (three deep is caught). Five forms. Its verifier reads arrays four deep (P9, K6r) as the "container" limit, with the depth cap as the defect; the tuple forms are outside every limit, and a tuple whose message is at index 0 is caught |
| N5 | **A thrown value** | `async function fail(entry: ConversationMessage) { throw entry; }`, then `fail(message).catch((entry: Loose) => …entry.name…)` (P5b) | A `throw` operand is never compared, and a rejection reason is `any`. One form. P5, the same through a `.then` arrow that captures `message`, its verifier places in the closure limit |
| N6 | **A `for…of` into an existing target** | `let loose: Loose \| undefined; for (loose of conversation.messages) break;`, and `for (box.entry of conversation.messages)` | The loop's existing target gets no contextual check. Three forms (A2, A2b, A5) |
| N7 | **`arguments`** | `function shout() { return String(arguments[0]?.name ?? ''); }` used as `[message].map(shout)`; the inline form; a render function the same way (R1, R2, R21) | `arguments` is `any`, and the by-reference comparison is per declared parameter. ESLint's `prefer-rest-params` refuses all three, so `npm run check` fails on them, but this test does not |
| N8 | **An inline parameter typed only by its default** | `[message].map((entry = BLANK) => entry.name ?? '')`, with `BLANK: Loose` (R7) | C1's inline check skips a parameter without an annotation. The by-reference forms are caught (R6, R15). One form |
| N9 | **`instanceof` narrowing** | `message instanceof NamedEntry && <Eyebrow entry={message} />`, with a local class `NamedEntry { name = '' }` and `static [Symbol.hasInstance]` returning true (P10b) | `instanceof` narrows the data to `ConversationMessage & NamedEntry`, which keeps its type at the loose prop. It is counted under N1 above, and listed here as its own mechanism |

These are findings for the manager and, where a fix would change the design, for the Dev Manager. None was fixed in C2, since each lies outside Outcome 1 to 5 and DM-38 sends a change of design to the Dev Manager first.

**A candidate, measured and not committed.** For that decision, the session tried a candidate in a scratch copy of the test at `816cd60`. It has three changes, ten lines of diff:
- **a narrowing refused:** an object target that declares no field in a `GLOW_DATA` file, given Glow's data itself, does not keep;
- **any `@ts-` directive refused;**
- **`this` without a declared parameter treated as `unknown`:** Glow's data given as `this` through `.call` or `.apply` to a function that declares no `this`.

Its results:
- **today's code:** both files pass it, as does every planted form (`ℹ pass 21`);
- **N1, N2 and N3:** it catches 36 of the 49 forms (N9's P10 and P10b with them);
- **N4 to N8:** it catches none of the other 13 forms;
- **harmless code:** it newly refuses five harmless controls:
  - `const plain: { text: string | null } = message` reading only `.text`;
  - a component prop typed `{ text: string | null }` rendering only `.text`;
  - `stamp.call(message)` with `this` unused;
  - `Array.prototype.map.call(conversation.messages, (entry: ConversationMessage) => entry.text ?? '')`;
  - a comment that merely contains "@ts-expect-error".

So N1's fix fails closed, but it refuses ordinary narrow helpers: a trade the Dev Manager would weigh against option (c), view models by explicit field copy (DM-38 2.5), which N1 also points to.

**False positives found** (harmless code the check refuses; it fails closed). These are inside the guarantee's "it refuses some harmless code":
- a `FlatList` (F0), a `VirtualizedList`, `Array.from` and `new Set` over the messages, since an `Iterable` or `ArrayLike` parameter has an index signature;
- a spread of the messages, and a computed read with a constant key;
- an `in` check on the screen's own `StyleSheet`;
- `Object.is`, `Object.groupBy`, and `globalThis.Object.freeze` or `(Object).freeze` in `rows.ts`;
- `conversation.messages.at(-1)`, `.toReversed()` and `.filter(…)`, refused by the source check's path list alone.

**Two are new with C2:**
- an inferred type predicate in harmless code, such as `.filter(text => text !== null)` over strings, since TypeScript infers `text is string`;
- Node's `assert`, whose `asserts value` is not the default library's.

**The adversarial verifiers** re-ran every form that passed, each in its own copy, and reproduced every result. They refuted two classifications: P5 (inside the closure limit, as written) and P10 (no runtime reach, as above). They disputed a third, K6r: arrays nested four deep read as the "container" limit, and the real defect is `carries`' silent depth cap. They upheld the rest, and added forms of their own in the same classes: P5d (N5, with no closure), and X5r and X6b (N1, X6b with no array).

### Commands and results

All in `apps/mobile`, in the clean environment, unless the row says otherwise.

| Command | Result |
|---|---|
| `npm ci --ignore-scripts` (with the proxy and CA variables by reference) | `added 651 packages, and audited 652 packages in 18s`; `22 moderate severity vulnerabilities` (npm audit's line; no lock change) |
| `node --test src/chat/display-rule.test.ts` at `007377e` | `ℹ tests 21`, `ℹ pass 21`, `ℹ fail 0` |
| the same at `345e311`, `082506f` and `816cd60` | `ℹ tests 21`, `ℹ pass 21`, `ℹ fail 0` each time (the file's test count is unchanged; the planted test holds 38 forms and F0) |
| `npx tsc --noEmit`; `npx eslint src/chat/display-rule.test.ts` | no output (pass), before each code commit |
| `git diff --check` | no output |
| **`npm run check`** before each code commit (`345e311`, `082506f`, `816cd60`) | exit 0; `ℹ tests 650`, `ℹ pass 650`, `ℹ fail 0` each time (650 at `0881db5`) |
| The guarantee in the comment against DM-38's text (a script, comment markers removed) | `word for word: True` |
| The 17 planted-form reversals and the 12 mechanism reversals above | each with the edit `exit 1`, restored `exit 0`; each file's hash checked |
| The own forms: 256 by the probes, and the 70 gap forms re-run at `816cd60` | as above; every restore's hash matched |
| `git diff --name-only 007377e HEAD` | `apps/mobile/src/chat/display-rule.test.ts` and this record |

`check:expo` and `export:development` were not run locally: C2 changes one test file, which neither reads. The run of record runs both.

### The run of record

**Push run 41513359474** ([run](https://github.com/amthorn78/glow-dating-app/actions/runs/41513359474)), on the code head `816cd607019e69442f99007ef6324c9aa00dd83c`, read through the GitHub tools after it completed (`status: completed`, `conclusion: success`):

| Job | Conclusion | Duration (job start to completion) |
|---|---|---|
| Change scope | success: `COMPARE_BASE` `082506f…`, `COMPARE_HEAD` `816cd60…`; the trusted policy printed `{"full": true, "reason": "behavior-or-empty", "paths": ["apps/mobile/src/chat/display-rule.test.ts"]}` | 6 s |
| API checks | success | 45 s |
| API artifact checks | success | 18 s |
| API mobile smoke | success | 1 min 28 s |
| Mobile checks | success. Its steps, in order:<br>- `npm run check` in `packages/contracts`: `@glow/contracts`, `ℹ tests 586`, `ℹ pass 586`, `ℹ fail 0`;<br>- in `apps/mobile`, `npm run check && npm run check:expo`: `@glow/mobile`, **`ℹ tests 650`, `ℹ pass 650`, `ℹ fail 0`**, then `Dependencies are up to date`;<br>- `export:development`: `iOS Bundled … (1361 modules)`, `Android Bundled … (1330 modules)`, `Exported: .work/native-export`;<br>- the pinned Chromium installed by the workflow;<br>- the rendered suite, **`97 passed (4.9m)`**, with no failed, flaky or skipped line;<br>- the empty-form layout artifact uploaded (2 files) | **7 min 31 s of the 25-minute timeout** (19:49:02 to 19:56:33 UTC) |
| Stream proof checks | success (offline checks; no provider call) | 1 min 39 s |
| Database proof checks | success | 7 min 34 s of 30 |
| Foundation gate | success; its line: **`Application checks passed`** | 4 s |

**The earlier code heads' runs**, each complete before the next push, so no push cancelled a run (AM8-20):
- **push run 41509123092** on `345e311`: eight of eight jobs `success`, with Mobile 19:21:17 to 19:28:36 UTC (7 min 19 s);
- **push run 41510786950** on `082506f`: `conclusion: success`. Its jobs were not read one by one.

The records commit was pushed only after 41513359474 completed.

### What could not run, and limits

- **The rendered suite on the pinned browser** runs only in CI (`playwright install` is forbidden here). It was not run locally; C2 changes no rendered path, and the run of record runs it.
- **Expo's documentation** was not read; C2 touches no Expo API.
- **The check is a test over two files' source.** The forms it does not reach are the guarantee's named limits and the findings N1 to N9 above. The candidate is a measurement for the decision, not a change.
- **The probes and their verifiers ran against `345e311`'s test.** Only the 70 gap forms were re-run against `816cd60`. A form caught at `345e311` was not re-run at `816cd60`, which adds refusals and narrows nothing.
- **No change outside the owned paths:** `git diff --name-only 007377e HEAD` lists `apps/mobile/src/chat/display-rule.test.ts` and this record. No runtime file, guard, dependency or lock changed. No exception was added. Nothing met the stop rule.

## Manager verification of correction C2 (2 November 2026, App Manager 9)

- **The branch:** `claude/inspiring-ramanujan-tjpril`, started at `007377e`: code commits `345e311`, `082506f` and `816cd60` (the code head; `apps/mobile/src/chat/display-rule.test.ts` only, +222 −39 against `0881db5`), then the record `3c0acfe`. `git diff --name-only 007377e 3c0acfe` lists the two owned paths. "Manager verification", "Exact-head review of P06.2-F", "Manager verification of correction C1" and "Delta re-review of correction C1" are byte-identical to `007377e` apart from the blank line before the new heading.
- **The diff, read whole:** Outcomes 1 to 5 as the session reports them, each with its planted forms, which name the violation they must produce; the test comment states DM-38 section 4's guarantee and finding 1's class as a limit an ordinary refactor reaches; the `FlatList` false positive is planted to fail closed for its one reason; the `GLOW_DATA` paths must exist and be matched. The two later code commits close gaps the session's own probes found in C2's refusals (a by-reference function's return; `Reflect` and `Object` by any key, predicates by reference), inside Outcomes 1 to 3. No exception was added, and no runtime file, dependency or lock changed.
- **Local checks,** in a scratch worktree of `816cd60` outside the checkout, in the clean environment: `npm ci --ignore-scripts`; `npm run check`, exit 0, `ℹ tests 650`, `ℹ pass 650`, `ℹ fail 0`.
- **The session's outside-limit classes, re-run by the manager** as real edits to `screen.tsx`, each file's SHA-256 checked after its restore (the session's claims are its own, AM9-03):
  - **N1** (narrow, then widen): `<Narrow entry={message} />`, where `Narrow`'s prop is `{ text: string | null }` and it passes `entry` to `Wide`, whose prop `{ name?: string; text: string | null }` renders `entry.name`: the test passed (21 of 21), `tsc` and ESLint passed;
  - **N3** (`this` through `.call`): `{String(({}).hasOwnProperty.call(message, 'name'))}`: the test, `tsc` and ESLint passed;
  - **N2** (a suppressed type error): the manager's variant, `@ts-expect-error` above `{message.name}`, was caught (the source check's path list, and ESLint); the session's seven N2 forms were not re-run, so N2 stands as the session reports it.
- **The run of record, read from its jobs and the gate's log:** push run 41513359474 on `816cd60`, eight of eight jobs `success`, the gate printed `Application checks passed`; Mobile 19:49:02 to 19:56:33 UTC, 7 min 31 s of 25. The unit and rendered counts (650; `97 passed (4.9m)`) are the session's reading; the manager did not re-read the Mobile log.
- **Integrated** into the manager branch by a merge commit, `880a42f`; every non-Markdown path at it is byte-identical to `816cd60`. The trusted classifier reads the PR full scope (`behavior-or-empty`), one merge base, `05f4c3a`.
- **What this means:** C2 meets its Outcomes, but DM-38 section 4's guarantee, as the test now states it, still claims more than the check does: the session's 49 passing forms in nine classes (N1 to N9; the record, "Correction C2") fall outside every limit it names, N1 through an ordinary refactor (an intermediate component with a narrower prop). Three rounds (C1's exact-head review, its delta re-review, C2's own probes) have each found forms outside the stated claim. The next step is a design decision, not a review: **DM-38's "a change of design goes to the Dev Manager first" applies, as DM-39.** No delta re-review prompt is written until it is answered.
- **Codex on `6a9a6b5`** (2 November, 21:53 UTC) raised two P2 threads, both C2's classes: narrow then widen (`display-rule.test.ts:280`, N1) and an inline parameter typed only by its default (`:415`, N8). The manager answered both.
- **DM-39** ([report](../../continuity/dev-manager/reviews/2026-11-02-dm-39-p06-2-f-render-rule-after-c2.md), answered at `4450761`, accepted as written): option (b). N1 to N9 become known passing classes in a positive list of what the check refuses; no check changes; DM-38 section 4's wording is withdrawn (DM-39 1.4) and DM-39 section 4.2's replaces it, in correction C3 (the brief, "Correction C3"). Its probes show that a narrower type built from the contract's own (`Pick<ConversationMessage, 'text'>`) keeps Glow's identity: N1's X2 so written is caught, and its harmless use passes (DM-39 section 3). C2's 49 forms, the candidate's rules and that result go to option (c)'s brief (1.3), and (c) lands before P11 serves the chat reads at the latest (3.1).

## Correction C3 (3 November 2026)

- **Work:** the brief's "Correction C3" (revision 3), Outcome 1 to 3, on DM-39's terms ([report](../../continuity/dev-manager/reviews/2026-11-02-dm-39-p06-2-f-render-rule-after-c2.md), sections 4 and 6; conditions 1.1 to 1.4).
- **Prompt:** [`docs/ephemeral/2026-11-02-p06-2-f-c3-correction-prompt.md`](../../ephemeral/2026-11-02-p06-2-f-c3-correction-prompt.md), revision 1, from `ca5a27e6a2d6f6896cb57ce03227d71a29de3167` of the manager branch `claude/magical-wozniak-yfmmx2`. Started by Nathan, in `Glow App - No Stream`.
- **Branch:** `ccr-7506019b-5rfdfn` (the session branch the environment named), started at `ca5a27e`.
- **Code head:** `f87e8b19110544b1ceddfc1afd44a8492350fb81`, one commit, to the comments of `apps/mobile/src/chat/display-rule.test.ts` only.
- **Records head:** the next commit on the branch, Markdown only (this section); no code after the code head.
- **Run of record:** push run **41553218994** on `f87e8b1`: eight of eight jobs `success`, `Application checks passed`, 650 unit tests, rendered `97 passed (5.0m)`, Mobile 7 min 42 s of 25.
- **What this section supersedes.** The guarantee wording of "Correction C1" ("through any binding", in its "Finding 1" and its limit) and of "Correction C2" (DM-38 section 4's paragraph, under "The guarantee, as the test states it", and "Its limits, as the test states them") is superseded by the wording below (DM-39 1.4). This section does not edit them.

### Environment check (names only)

- `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`: none present.
- `STREAM_*`: no name present.
- `GH_TOKEN` and `GITHUB_TOKEN` are present; never read. App commands ran without them.
- **Toolchain:** `node --version` → `v24.19.0`; `npm --version` → `11.9.0`, both resolved from `$HOME/.local/bin` (`/root/.local/bin`). On the session's own PATH, `/nix/var/nix/profiles/default/bin` comes before it, though `node` and `npm` resolve to `$HOME/.local/bin`; each npm and Node command ran in `env -i PATH="$HOME/.local/bin:$PATH" HOME="$HOME" LANG=C.UTF-8`, which puts it first. `npm ci` also passed `HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS` by reference, never printed.

### Start gate

| Check | Result |
|---|---|
| `git fetch origin claude/magical-wozniak-yfmmx2 main` | fetched; `origin/claude/magical-wozniak-yfmmx2` = `ca5a27e6a2d6f6896cb57ce03227d71a29de3167`; `origin/main` moved `35a5827..bac3c19` |
| `git switch -C ccr-7506019b-5rfdfn ca5a27e…`; `git rev-parse HEAD` | `ca5a27e6a2d6f6896cb57ce03227d71a29de3167` |
| `git merge-base --is-ancestor ca5a27e… origin/claude/magical-wozniak-yfmmx2` | `this prompt's commit is on the live branch` |
| `git diff --quiet 816cd60… HEAD -- .github scripts services apps packages proofs` | `the code head under correction` |
| `git diff --quiet 816cd60… origin/claude/magical-wozniak-yfmmx2 -- …` (the same paths) | `no code on the live branch after 816cd60` |
| `git show origin/claude/magical-wozniak-yfmmx2:<this record> \| grep -c -E '^#+ Correction C3'` | `0` |

**Read before the work:** root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md` and `CLAUDE.md`; the brief's "Correction C2" and "Correction C3"; this record's "Correction C1", "Exact-head review of P06.2-F", "Delta re-review of correction C1", "Correction C2" and "Manager verification of correction C2"; DM-39's report, whole; `src/chat/display-rule.test.ts`, whole.

### What the check does

The test comment now states this paragraph word for word (DM-39 section 4.2), in place of DM-38 section 4's:

> **What the check does (DM-39).** It refuses the forms listed below, and its planted forms are that list's specification: a form that evades a listed refusal is a defect, and any other form that passes is a limit, recorded when found. It treats a value as Glow's data while the value's type declares a field in a `GLOW_DATA` file, and it does not check the value once its type declares none, for example after a narrower type declared outside those files; a narrower type built from the contract's own, such as `Pick<>` or `Omit<>`, keeps it Glow's data. The forms it is known to pass are named below; probes found them, and more may exist. It refuses some harmless code, which fails closed. It is a test over two files' source, not a proof. The client validator is the first guard, and view models built by explicit field copy (DM-38 2.5) are the structural fix.

A script compared the comment's paragraph, with comment markers removed and whitespace collapsed, against the brief's text with its bold markers removed: `word for word: True`.

**The source check, as the comment now describes it.** It is a text match over the two files with comments removed: it reads the property paths its pattern matches after the six names, against a named list, and refuses a cast, `any`, a spread, a computed read written as one of those names then `[`, a reflective read, and an `in` check after a quoted string. C3's verifiers found that, as a text match, it passes `message?.['name']`, `message ?.name`, a path split across lines and `('name') in message`. The type check refuses each of the four (C3's probes, below), so none is a passing form of the check as a whole.

### What it refuses

The comment's "What it refuses, in its own terms" list stays, with the planted forms that pin each item in brackets. IDs are this record's: 1 to 9, PA, PB, PC and 13 to 22 (C1's table), C2-1a to C2-4b (C2's table). The test asserts only that forms 1 to 9 fail the source check, so a form pins a source-check item when that item is its only source-check violation.

| Item | Pinned by | Without a planted form (C3's probe: the violation reported) |
|---|---|---|
| **The source check:** a path outside its list; a cast; `any`; a spread; a computed read; a reflective read; an `in` check on a string | 1, 6, 8 (path); 2 (cast); 4 (spread); 3 (computed); 5, 9 (reflective) | `any`: 7 reports it beside a cast, so it pins nothing alone. `in` on a string: `const x = 'name' in item;` → `an in check` |
| a read from Glow's data of a property its type does not declare, and a computed or rest read | 1, 6, 8, PA, PC, 22; 3 (computed) | rest read: `const { ...rest } = message` → `a rest read: ...rest` |
| an `in` check, a `for…in` enumeration, a destructuring assignment or a spread of Glow's data | 4 (spread) | `'text' in message` → `an in check`; `for (const key in message)` → `an enumeration`; `({ text: held } = message)` → `a destructuring assignment`. PA reports its `in` check beside its named field read |
| a widening, at a parameter (through `call`, `apply` or `bind` too), a prop, an annotation, a return or an assignment, to a type declaring a property the data's does not, or to `any`, `unknown`, `object`, `{}` or an index signature | 2, 5, 7, 9, PB, 13, 16 to 19, 21, C2-4a, C2-4b | `bind`, a return (`lift(entry): Loose { return entry; }`), an assignment (`loose = message`), `object` and `{}`: each → `a widening to …` |
| a callback, inline or by reference, whose parameter widens what it is given, or whose return of Glow's data is widened | 15 (inline); C2-1a to C2-1d (by reference); C2-1e (return) | — |
| a type predicate or assertion signature: declared in the two files, written or inferred; called; given by reference; each unless the default library's | C2-2d (declared, written); C2-2a, C2-2b, C2-2c (called); C2-2e (by reference) | inferred: `const present = (text: string \| null) => text !== null` → `a type predicate or assertion signature: …` |
| `Reflect`, and `Object` other than as `Object.freeze`'s receiver: by identifier, by an expression's type, by a destructuring's type whatever its key | C2-3a, C2-3b (identifier; each also reports the expression's type); C2-3c, C2-3d (destructuring) | by type alone, `globalThis.Reflect` → `…: globalThis.Reflect`, and a verifier's `g['Reflect']`, `g['Object']` → refused |
| a local generic or overload; a type error the compiler reports in the two files | 14 (generic); 20 (overload) | type error: `const wrong: number = 'x'` → `a type error: …`. PC and 22 report one beside their named reads |

The named exceptions are unchanged; C2-4a pins the dependency-list exception's narrowing, and C2-4b the destructuring exception's. C3 added no planted form (DM-39 1.1): the items without one are recorded here, for the delta re-review (DM-39 1.2) and option (c)'s brief.

### What it is known to pass

Where they came from: the exact-head review of P06.2-F (its finding 1 began C1) and C1's own probes ("Correction C1", "Forms known to evade the check"); C1's delta re-review (its finding 1); and C2's 256 probe forms ("Correction C2", N1 to N9). Codex found N1 and N8 again (`display-rule.test.ts:280`, `:415` at `6a9a6b5`). `Loose` is `{ name?: string; text: string | null }`.

| Class | One example, as the comment gives it |
|---|---|
| **Finding 1's class** (C1's delta re-review): data held inside another value | a group or section, a list's render-item wrapper, a view-model object, a closure or a container, given to a loosely typed helper that renders a provider-shaped field |
| **N1**, narrow then widen | **X2, an ordinary refactor:** `<Narrow entry={message} />`, where `Narrow`'s prop is `{ text: string \| null }` and it hands `entry` to `Wide`, whose `Loose` prop renders `entry.name` |
| **N2**, a suppressed type error | `// @ts-expect-error` above `<Caption entry={message} />`, where `Caption`'s prop is `() => void` and it renders `entry.name` |
| **N3**, `this` through `.call` to a function declaring no `this` | `({}).hasOwnProperty.call(message, 'name')` |
| **N4**, a container the check does not follow | `const pair = ['label', message] as const`, given to `readonly (string \| Loose)[]`; arrays nested four deep |
| **N5**, a thrown value | `async function fail(entry: ConversationMessage) { throw entry; }`, then `fail(message).catch((entry: Loose) => entry.name)` |
| **N6**, a `for…of` into an existing target | `let loose: Loose \| undefined;` then `for (loose of conversation.messages) break;` |
| **N7**, `arguments` | `function shout() { return String(arguments[0]?.name ?? ''); }`, used as `[message].map(shout)`; ESLint's `prefer-rest-params` refuses it, this test does not |
| **N8**, an inline parameter typed only by its default | `[message].map((entry = BLANK) => entry.name ?? '')`, with `BLANK: Loose` |
| **N9**, `instanceof` narrowing | `message instanceof NamedEntry && <Eyebrow entry={message} />`, with a local `NamedEntry { name = '' }` whose `Symbol.hasInstance` returns true |
| **Another module** | `<Eyebrow entry={message} />`, where `Eyebrow`, in a module other than the two files, takes the exact `ConversationMessage` and casts it to render `name` |
| **A template literal's coercion** | `` {`${message}`} `` (it renders `[object Object]`) |

### What harmless code it refuses

Each fails closed. The next author who meets one changes the design (view models by explicit field copy, DM-38 2.5), not the check.
- **F0's family:** a harmless `FlatList` over the messages fails with `a widening to Readonly<ArrayLike<ConversationMessage>> | undefined: conversation.messages` (`FALSE_POSITIVE`), and so do a `VirtualizedList`, `Array.from` and `new Set` over them. An `ArrayLike` parameter's index signature is a widening. An `Iterable` parameter has no index signature: its one property is the symbol-keyed iterator, which `keeps` does not find by name on the array, so it reads as a widening (a C3 verifier's finding; `new Set(conversation.messages)` → `a widening to Iterable<ConversationMessage> | null | undefined`). The comment states both reasons.
- **Inferred predicates,** such as `.filter(text => text !== null)` over strings, since TypeScript infers `text is string`.
- **Node's `assert`,** whose `asserts value` is not the default library's.
- **The source check's path list,** which refuses `conversation.messages.at(-1)`, `.toReversed()` and `.filter(…)`.

"Correction C2" names more (a spread of the messages, a computed read with a constant key, an `in` check on the screen's `StyleSheet`, `Object.is`, `Object.groupBy`, `globalThis.Object.freeze` and `(Object).freeze` in `rows.ts`).

### Kept for option (c)'s brief (DM-39 1.3)

- **C2's 49 forms,** in nine classes, as "Correction C2"'s table gives them, with their IDs:
  - **N1** (20): r1, r3, r4, r7, d1, d5, d6, d8, s1, s3, s7, X1, X2, X3, X5, X6, X7, X8b, P10, P10b;
  - **N2** (7): E6, T2, T3, T4, T5, T10, T11;
  - **N3** (8): E5, I4, I6, T8, R3, R14, R11, R20;
  - **N4** (5): P3, R6, A8 (tuples), P9, K6r (arrays four deep);
  - **N5** (1): P5b;
  - **N6** (3): A2, A2b, A5;
  - **N7** (3): R1, R2, R21;
  - **N8** (1): R7;
  - **N9:** P10b, counted under N1.

  These per-class counts sum to 48; the table gives the total as 49 (70 → 49) and does not say where the 49th falls. The verifiers' added forms (P5d in N5; X5r and X6b in N1) are listed beside them. C3 did not re-run these forms; it changes no check, so their results at `816cd60` stand. Option (c)'s check must refuse them (DM-39 1.3).
- **The candidate's three rules and their measured results** ("Correction C2", measured at `816cd60`, not committed):
  1. a narrowing refused: an object target that declares no field in a `GLOW_DATA` file, given Glow's data itself, does not keep;
  2. `@ts-` directives refused;
  3. `this` without a declared parameter treated as `unknown`, for Glow's data given as `this` through `.call` or `.apply`.

  Today's two files and the planted forms pass it (`ℹ pass 21`). It catches 36 of the 49 forms (N1, N2 and N3, with N9's P10 and P10b), and none of the other 13 (N4 to N8). It newly refuses five harmless controls: a narrow variable `{ text: string | null }` reading only `.text`; a narrow prop the same; `stamp.call(message)` with `this` unused; `Array.prototype.map.call(conversation.messages, (entry: ConversationMessage) => entry.text ?? '')`; a comment that contains "@ts-expect-error". DM-39 4.1 found two of the five have a spelling that passes and keeps the protection, and one is a comment-matching flaw.
- **DM-39 section 3's `Pick<>` result:** a narrower type built from the contract's own keeps Glow's identity. X2 with `Narrow`'s prop written as `Pick<ConversationMessage, 'text'>` fails (`a widening to { name?: string | undefined; text: string | null; }: entry`), and the variable form the same (HVW). The harmless uses, as a prop (HP) and a variable (HV), pass. N1 needs a narrow type declared outside `GLOW_DATA`. Option (c)'s check must pass today's harmless controls (the candidate's five, and F0's family; DM-39 1.3).

### Only the comment changed

- `git diff 816cd60 f87e8b1 -- apps` touches `apps/mobile/src/chat/display-rule.test.ts` alone. No line outside a comment was added or removed: a filter of the diff's `+` and `-` lines for those that do not begin, after whitespace, with `*`, `/**` or `//` prints nothing.
- **Both versions compiled with comments stripped:** the TypeScript printer over each file's parse tree, with `removeComments` (types kept), gives identical text (SHA-256 prefix `af0654d8edd45489` for each); `ts.transpileModule` with `removeComments` gives identical JavaScript (`47c23e92fd998178` for each). A raw token scan differed, since a standalone scanner misreads regular expressions and template literals and runs into comment text; the parse-tree comparison is the one recorded.
- **Two comments changed:** the render-rule block, and the one-line comment before the type check's assertion in the first render-rule test, which said "within the guarantee above" and now says "as the comment above states it (DM-39)", since that guarantee is withdrawn. No refusal, exception or planted form changed (DM-39 1.1).
- **Words that claim coverage** (DM-38 4.2; DM-39 4.2): in the diff's added lines, "any" occurs four times, three as the type `any` and one in the core paragraph's mandated "any other form"; "follows", "every", "all" and "wherever" do not occur. The comment's earlier "reads every property path" and "not a proof over all programs" are gone.

### How the wording was checked

- **C3's probes** (in a scratch copy of `apps/mobile` and `packages` from `git archive` of `ca5a27e`, outside the checkout, with the checkout's `node_modules` linked; the test copied with `test` stubbed, and edits planted beside `screen.tsx` in memory through the test's own `typedViolations` and `sourceViolations`). Each item the comment marks as having no planted form was planted once and refused, with the violations in the table above. The four source-check misses were each refused by the type check: `message?.['name']` → `a computed read`; `message ?.name` and the split path → `a field outside Glow's types`; `('name') in message` → `an in check`.
- **Three adversarial verifiers** (read-only subagents, in the scratch copy) checked the comment before the code commit: the planted-form IDs against the test's `PLANTED` list and C1's table; the two lists against this record and DM-39; coverage wording and behaviour claims against the code. They found three false statements, each corrected before the commit: the source check's description overstated what its text match reads; form 7 was listed as pinning `any` though it also trips the cast refusal; and the `Iterable` reason (above). They found no wrong ID and no unfaithful example.

### Commands and results

In `apps/mobile`, in the clean environment, unless the row says otherwise.

| Command | Result |
|---|---|
| `npm ci --ignore-scripts` (with the proxy and CA variables by reference) | completed with npm audit's summary as its last lines (the exit status was not captured separately); the installed tree ran the checks below; no lock change |
| `node --test src/chat/display-rule.test.ts` at `ca5a27e`, before the change | `ℹ tests 21`, `ℹ pass 21`, `ℹ fail 0` |
| the same at `f87e8b1` | `ℹ tests 21`, `ℹ pass 21`, `ℹ fail 0` |
| **`npm run check`** at `f87e8b1` (twice: before and after the verifiers' corrections) | exit 0; `ℹ tests 650`, `ℹ pass 650`, `ℹ fail 0` each time |
| the core paragraph against the brief (a script) | `word for word: True` |
| the parse-tree and emitted-JavaScript comparisons with `816cd60` | `true` / `true` |
| `git diff --check` | no output |
| `git diff --name-only ca5a27e HEAD` | `apps/mobile/src/chat/display-rule.test.ts` and this record |

### The run of record

**Push run 41553218994** ([run](https://github.com/amthorn78/glow-dating-app/actions/runs/41553218994)), on the code head `f87e8b19110544b1ceddfc1afd44a8492350fb81`, read through the GitHub tools after it completed (`status: completed`, `conclusion: success`). The records commit was pushed only after it completed (AM8-20).

| Job | Conclusion | Duration (job start to completion) |
|---|---|---|
| Change scope | success. The trusted policy printed `{"full": true, "reason": "missing-or-invalid-comparison", "paths": []}`: the branch's first push has no earlier head to compare, so it classified full scope, failing safe | 5 s |
| API checks | success | 38 s |
| API artifact checks | success | 19 s |
| API mobile smoke | success | 1 min 12 s |
| Mobile checks | success. Its steps, in order:<br>- `npm run check` in `packages/contracts`: `@glow/contracts`, `ℹ tests 586`, `ℹ pass 586`, `ℹ fail 0`;<br>- in `apps/mobile`, `npm run check && npm run check:expo`: `@glow/mobile`, **`ℹ tests 650`, `ℹ pass 650`, `ℹ fail 0`**, then `Dependencies are up to date`;<br>- `export:development`: `iOS Bundled … (1359 modules)`, `Android Bundled … (1358 modules)`, `Exported: .work/native-export`;<br>- the pinned Chromium installed by the workflow;<br>- the rendered suite, **`97 passed (5.0m)`**, with no failed, flaky or skipped line;<br>- the empty-form layout artifact uploaded (2 files) | **7 min 42 s of the 25-minute timeout** (00:29:42 to 00:37:24 UTC) |
| Stream proof checks | success (offline checks; no provider call) | 1 min 32 s |
| Database proof checks | success | 7 min 26 s of 30 |
| Foundation gate | success; its line: **`Application checks passed`** | 13 s |

The Mobile job's log was read in full from the job's log download; the counts above are its lines.

### What could not run, and limits

- **`check:expo`, `export:development` and the rendered suite** were not run locally: C3 changes a comment, which none of them reads, and `playwright install` is forbidden here. The run of record runs them.
- **C2's 49 forms and the candidate** were not re-run; C3 changes no check, so their results at `816cd60` stand as "Correction C2" records them.
- **Planted forms are missing for some refusals** (the table above). C3 confirmed each by a probe and added none (DM-39 1.1). Whether to plant them is for the delta re-review or option (c)'s brief.
- **No change outside the owned paths:** the comment of `display-rule.test.ts` and this section. No runtime file, refusal, exception, planted form, dependency or lock changed. Nothing met the stop rule.

## Manager verification of correction C3 (3 November 2026, App Manager 9)

- **The branch:** `ccr-7506019b-5rfdfn` (the name its environment gave it), started at `ca5a27e`. It has one code commit, `f87e8b1`, which changes comments in `apps/mobile/src/chat/display-rule.test.ts` only (+94 −40), then the record commit `14e37a6`. `git diff --name-only ca5a27e 14e37a6` lists the two owned paths. The record's change is a pure insertion of 159 lines at its end, after "Manager verification of correction C2", so no earlier section changed. The branch cleanup has no name rule (`scripts/branch_cleanup.py` keeps only its keep-list, open PR heads and unmerged branches), so this branch is deleted once PR40 merges, like the others.
- **Only comments changed,** checked the manager's own way. Both versions of the test (`816cd60` and `f87e8b1`) were printed from their parse trees with comments removed, with the TypeScript compiler installed on the machine (6.0.2, `/opt/node-tools`, not the app's pinned copy). The two outputs are identical, with SHA-256 prefix `af0654d8edd45489` for each, the prefix the session recorded. The diff, read whole, changes the render-rule comment block and one line comment before the type check's assertion ("within the guarantee above" became "as the comment above states it (DM-39)"). Both are comments, and the second points at the withdrawn guarantee, so its change is inside the owned scope. The records head keeps the code head's test file byte for byte.
- **The wording:**
  - **The core paragraph:** a script compared it, with comment markers, bold markers and whitespace normalized, against the brief's "Correction C3". It is word for word in the comment (`True`) and in the record's new section (`True`).
  - **Coverage words** (DM-38 4.2; DM-39 4.2): in the comment block, "follows", "all" and "wherever" do not occur. "any" occurs four times: three as the type `any` and once as the core paragraph's "any other form". "every" occurs once, as the method name `every` in the exceptions, a line unchanged since C2. "follow" occurs twice, each in a limit ("does not follow").
  - **The three lists:** they meet DM-39 section 4.2's terms. Two of the old list's phrases were reworded to drop coverage claims ("reads every property path"; "any type error"); the meaning is unchanged.
- **Not re-run by the manager:** `npm run check`, the planted forms and C3's probes of the refusals that no planted form pins. The test's code is unchanged, so its results at `816cd60` stand. The probes are the session's own claims (AM9-03), and the delta re-review tries its own forms against each listed refusal (DM-39 1.2; its focus 3).
- **The run of record, read from its jobs and logs:** push run 41553218994 on `f87e8b1`. All eight jobs concluded `success`, and the gate's log prints `Application checks passed`. The manager downloaded the Mobile job's full log (2,329 lines). It shows `@glow/contracts` at `ℹ tests 586`, `ℹ pass 586`, `ℹ fail 0`; `@glow/mobile` at `ℹ tests 650`, `ℹ pass 650`, `ℹ fail 0`; and the rendered suite at `97 passed (5.0m)`. Mobile ran from 00:29:42 to 00:37:24 UTC, 7 min 42 s of its 25.
- **The 48-or-49 count** (the session's point 3). The 49 comes from C2's mechanism table, whose last column sums to 49. The class lists in "Correction C2" name 48 IDs, with N5 as one form (P5b). C2's report, as relayed, counted N5 as two. The verifiers added P5d to N5, so P5d is the likely 49th form, but C2's record does not settle it. The candidate's "36 of the 49" (N1 to N3) is also one more than the 35 IDs those lists name. The count is recorded, not reconciled. Option (c)'s brief takes the forms by ID, with the verifiers' additions (P5d, X5r, X6b; DM-39 1.3).
- **The refusals with no planted form** (the session's point 1). The comment marks them, and C3 added none, as DM-39 1.1 requires. Whether they need planted forms before the merge is the delta re-review's focus 9. The manager disposes of it after that review, and takes it to the Dev Manager if planting them would depart from DM-39 1.1.
- **The prompt's share** (AM9-06). The C3 prompt asked each refusal item to name its planted forms without the manager first checking that each item had one; several had none. The session reported it rather than inventing IDs.
- **Integrated** into the manager branch by a merge commit, `cfab39b`; every non-Markdown path at it is byte-identical to `f87e8b1`. The trusted classifier reads the PR full scope (`behavior-or-empty`), with one merge base, `05f4c3a`.
- **Codex's threads at `:280` (N1) and `:415` (N8):** C3's list now names both classes as known passing forms, so the manager answers and resolves them once this batch is on PR40.
- **Next:** the delta re-review ([prompt](../../ephemeral/2026-11-03-p06-2-f-c3-delta-review-prompt.md), revision 1, then revision 2 for its start gate after OD-57; TypeSafe v8.2: Opus 5.5 at high), after Codex on PR40's head, which holds it and C3's code. It is held to DM-39 1.2.

## Delta re-review of correction C3 (3 November 2026)

- **The review:** a delta re-review held to DM-39 1.2, which Nathan ran from the prompt, revision 2 at `b2904a4`, of code head `f87e8b1`. The start gate passed: one merge base, `05f4c3a`, and no non-Markdown path changed after `f87e8b1`. The trusted classifier read full scope (`behavior-or-empty`). The review changed nothing, and Nathan relayed its report.
- **Verdict: changes required.**
  - **What holds:** C3 changes only comments. The parse trees match without comments, as do the printed source (`af0654d8…`) and the emitted JavaScript (`47c23e92…`). The core paragraph is word for word. Every planted-form bracket and every "no planted form" bracket is true. Each known-passing example passes as written.
  - **What does not:** three of the review's own forms evade refusals the comment lists, and render a provider-shaped field with the test, `tsc` and ESLint passing. Under DM-39 1.2, each is a finding.
  - **How it tested:** about 90 forms, 45 of them as real edits, each file's SHA-256 checked after its restore.
- **Both runs passed:**
  - push run 41553218994 on `f87e8b1`;
  - PR run 41556434433 on `b2904a4`: eight of eight jobs, `Application checks passed`, 650 unit tests, `97 passed (5.0m)`.
  - Codex found nothing on `4d576d3` or `b2904a4`.
- **The manager confirmed findings 1 to 3 and 5** in a scratch copy of `f87e8b1` outside the checkout. Findings 1 to 3 were real edits to `MessageRow` in `screen.tsx`, with `screen.tsx`'s SHA-256 (`3aef02c392c5`) checked after each restore:
  - **Finding 1:** `const view: { line(entry: ConversationMessage): string } = { line(entry: Loose) { return entry.name ?? ''; } }` rendering `view.line(message)`. The test passed 21 of 21, and `tsc` passed.
  - **Finding 2:** `const caption: (entry?: Loose) => string = ({ name } = message) => name ?? ''` rendering `caption()`. The test passed 21 of 21, and `tsc` passed.
  - **Finding 3:** `let rest: Loose = { text: null }; for ({ ...rest } of [message]) break;` rendering `rest.name`. The test passed 21 of 21, and `tsc` passed.
  - **A control:** the arrow-property form `{ line: (entry: Loose) => entry.name ?? '' }` was refused, with 19 passed and 2 failed.
  - **Finding 5:** `@react-native/virtualized-lists`'s `VirtualizedList.d.ts:203` types `data` as `any`.

  The review reported 20 of 21 for its edits, because its placement moved a planted form's anchor; the manager's placement did not. ESLint was not re-run by the manager.

**The findings** (dispositions wait on DM-40, below). Line numbers are in `apps/mobile/src/chat/display-rule.test.ts` at `f87e8b1`.

| # | Finding | Severity; class |
|---|---|---|
| 1 | **The listed refusal of a callback "passed by reference (… an object's method)" whose parameter widens:** an object literal's method shorthand (`{ line(entry: Loose) { … } }`) gets neither the inline check nor the by-reference check. It also passes as a JSX prop (C4), through an interface with overloads (C5), as a class instance under that interface type (C3), and in `rows.ts` (C15). The arrow property (C2), `{ line: shout }` (C13) and `{ line }` (C14) are refused. The comment is at `:162-165`; the code at `:418`, `:451-461` and `:469` | Should fix; in a correction class (a form evades a listed refusal) |
| 2 | **The destructuring exception's "whose reads the pattern's own check covers"** (`:178-179`; code `:406-412`) is false when the parameter's type comes from context, not an annotation. The pattern is then typed `Loose`, not as Glow's data, and the Glow-data default is exempt. X1 is `const caption: (entry?: Loose) => string = ({ name } = message) => name ?? ''`; X2 is the same as a JSX prop. The annotated form X3 is refused. This is the same shape as C1's delta re-review finding 4 | Should fix; in a correction class (the exception claims more than the code; a widening passes through it) |
| 3 | **The listed "destructuring assignment"** is refused only as an `=` expression (`:447-448`). A destructuring assignment in a `for…of` head passes (D5, `for ({ ...rest } of conversation.messages) break;`). It overlaps N6 | Should fix; in a correction class (a form evades a listed refusal) |
| 4 | **The source check's text match misses more forms than the four the comment names** (`:120-126`): `(message)as{…}`, `message as/* */{…}`, `<{…}>conversation` in `rows.ts`, `'/*'` and `'*/'` in strings (which hide a read from the comment stripper), `any` between two apostrophes, `'name'in message`, `...(message)`, `Reflect['get']`, `Object['values']` and `const { stringify } = JSON`. The type check refused each one tried | Should fix (low); in a correction class (it evades the source check's listed refusals; the check as a whole refuses each) |
| 5 | **`VirtualizedList` is grouped under F0's `ArrayLike` and `Iterable` reasons** (`:212-217`, and this record's "What harmless code it refuses"). Its `data` prop is `any`, so it fails as `a widening to unknown` and `a widening to any`. The corrected `Iterable` reason is true | Should fix (low); in a correction class (a false reason) |
| 6 | **Probe IDs in "Correction C2" are not unique** (`R3` is "now caught" in one row and listed under N3; `R6` is in N4 and among the caught by-reference forms), so "(c)'s brief takes the forms by ID" is ambiguous | Nit (records) |
| 7 | **The 49th form:** C2's mechanism table places it in the "passed" row (four forms, N4 and N5), whose class lists name only P3, P9 and P5b. So it is N4 or N5; P5, which the verifiers moved into the closure limit, is a candidate beside P5d | Nit (records) |
| 8 | **The comment says "C3's probes found these"** of the four source-check misses (`:126`); the record says C3's verifiers found them | Nit |
| 9 | **"whatever its key"** (`:171`) is a coverage phrase. A union-typed key gives a union type, which is not refused (O5, `globalThis[key]` with `key: 'Reflect' \| 'JSON'`, passes; no read through it was found) | Nit |

- **Passing forms outside the list,** as records lines:
  - finding 1's mechanism as a class, if it is disposed of as one: "a method whose parameter widens, given inside an object or instance" (C1, C3, C4, C5, C15);
  - O5, a reflective global reached through a union-typed key (harmless as tried);
  - the test name at `:670` ("whatever the validators let through"), a coverage phrase in a non-comment line, outside C3's scope.
- **Focus 9, the planted-form specification:** the core paragraph's "planted forms are that list's specification" holds for the items that have planted forms, and the brackets state the gaps, so it is not an overclaim. The review's view is to keep them as marked, plant nothing before the merge (that would depart from DM-39 1.1 for a check that option (c) replaces), and carry the unpinned items, with its forms, to (c)'s brief. It is not a correction class.
- **Codex on `7983b31`** (3 November, 01:56 UTC) raised three P2 threads. They are this review's findings 1 to 3, with the same forms: method shorthand (`display-rule.test.ts:452`), the contextually typed destructuring default (`:411`) and the `for…of` destructuring head (`:448`). The manager answered each; they stay open until DM-40's disposition is applied.
- **Next:** the disposition. Step 6's rule (a) puts findings 1 to 5 before the merge. Each can be closed in the comment and the records, by narrowing the listed items to what the check refuses and naming the forms, which is inside DM-39 1.1; or in the check, which departs from it. Either is a design choice for a member-privacy boundary, so it goes to the Dev Manager first, as DM-40, with OD-57's governing texts for its pre-merge read.

**The dispositions** (DM-40, [report](../../continuity/dev-manager/reviews/2026-11-08-dm-40-p06-2-f-c3-review-and-od-57.md), answered at `497ba97`, a read of `6e9149e`, accepted as written):

| # | Disposition |
|---|---|
| 1 | **Closed in C4 by narrowing, not by a code change** (DM-40 1.1, 1.2). The callback item names the syntax the check compares: an inline arrow or function expression at its annotated parameters, and an expression whose type has a call signature at each parameter and its return; an object literal property written `key: value` or `{ key }` in a literal with a contextual type. A function reached only through an object or a class instance becomes a known passing class, with this form as its example. DM-40's probes found three more forms inside the manager's proposed wording (an accessor, a class field, an untyped literal given later), so the words name syntax, not categories (AM9-08) |
| 2 | **Closed in C4 by narrowing:** the destructuring exception says that the pattern's own check reads the initializer's fields only when the pattern is typed as Glow's data; a contextually typed parameter's default becomes a known passing class |
| 3 | **Closed in C4 by narrowing:** "a destructuring assignment written with `=`"; a destructuring target in a `for…of` head becomes a known passing class |
| 4 | **Closed in C4:** the source check's sentence names spacing, line breaks, parentheses, comments, string contents and bracket forms, with examples, and the type check refusing each one tried |
| 5 | **Closed in C4:** `VirtualizedList` fails as a widening to `unknown` and to `any`, since its `data` prop is `any`; F0's reasons stay for `Array.from` and `new Set` |
| 6, 7 | **In C4's record section** (nits): C2's forms listed by class and ID, the duplicates named, and the 49th placed in N4 or N5; the same go to option (c)'s inputs |
| 8, 9 | **In C4,** through DM-40 section 4.2's words |
| Records lines | O5 becomes a known passing class; the test name at `:670` is corrected in C4 to "today's chat screens and list rows pass both render-rule checks (M05 finding 18)" (DM-40 section 6) |
| Focus 9 | **Agreed:** the refusals no planted form pins stay marked, and go with the review's forms and DM-40 section 3's to option (c)'s inputs (the carried-items file) |
| The three code fixes | **Noted for (c), not made** (DM-40 1.4): exempt only a Glow-typed pattern; refuse a `for…of` head with a literal target; compare an object literal's method against its contextual property type |

- **Next:** correction C4 (the brief, "Correction C4"), then its delta re-review, bounded to the changed items (DM-40 3.1 to 3.4).

## Correction C4: the stop, and the manager's verification (8 November 2026, App Manager 9)

- **The session** stopped under its stop rule. It ran from prompt revision 1 at `0a63219`, on branch `claude/upbeat-mccarthy-499h9k`. Its code head is `691dfba` (one commit, `apps/mobile/src/chat/display-rule.test.ts` only, +42 −17). Its push run's gate did not print `Application checks passed`. So it did not push its "Correction C4" section, which was drafted only in its own session files. Nathan has since archived that session (by 09:07 UTC, by the session list), so the draft may not be recoverable; DM-41 item 4 asks how C4's record is finished.
- **The code head, verified by the manager:**
  - **Only one non-comment line changed.** Both versions (`f87e8b1`, `691dfba`) were printed from their parse trees without comments, with the TypeScript compiler on the machine (6.0.2). Of 559 lines, one differs: the first render test's name, now `today's chat screens and list rows pass both render-rule checks (M05 finding 18)`, as DM-40 section 6 gives it.
  - **The comment carries DM-40 section 4.2's words,** checked by script. Two items match exactly: the source check's sentence and the `Reflect` and `Object` item. Three match with the differences the session reported: "Another expression" for "Any other expression", a narrowing that drops a coverage word; the destructuring exception ending in ";" to continue its sentence; and F0's family keeping its sentence's start. The four known-passing entries and "written with `=`" are present.
  - **Coverage words:** "follows", "all" and "wherever" do not occur. "any" occurs only as the type `any` and in the core paragraph's "any other form".
- **The run, push run 42464917902 on `691dfba`, read by the manager from its jobs and logs:**
  - **Passed:** Change scope, API checks, API artifact checks, API mobile smoke and Stream proof checks.
  - **Failed:** Database proof checks, Mobile checks and the Foundation gate.
  - **Database proof checks:** `actions/setup-python` failed after about a minute. The session reported three `504` responses from github.com while it downloaded Python 3.12.14. None of the job's own steps ran.
  - **Mobile checks:** `@glow/contracts` 586 of 586 and `@glow/mobile` 650 of 650 passed, as did `check:expo` and `export:development`. The rendered suite gave `1 failed`, `96 passed (5.2m)`. The failing test was `profile-preferences.spec.ts:321` ("logout and account switching remove unsaved profile values …"). `getByTestId('screen-account').filter({ visible: true })` was not found within 10 s at line 342, and the harness printed `Visible screen identities after failure: []`. The rendered config has no retries.
- **The manager's reading of the rendered failure:**
  - **The sequence:** at lines 339 to 342 the test clicks `logout`, then calls `page.goBack()` at once, without waiting for the logout to land.
  - **Router 58's hazard:** M06 found that Router 58 applies a navigation after the click's task, and fixed this same test's first `logout` by waiting for the destination first (`:329`; the M06 record, "The test changes", change 2). The second `logout` has no such wait.
  - **Not P06.2-F's code:** P06.2-F does not touch this spec, the onboarding routes or logout. Its one routing edit, in `_layout.tsx`, moves the release guard's predicate into a function without changing what it allows.
  - **Open:** the reading is unproven. Whether an empty screen after back-navigation could also reach a member is not established.
  - **History:** each earlier PR40 run on a code head passed the rendered suite (97 of 97), so the failure is intermittent.
- **The PR runs after the stop, read by the manager from their jobs and logs.** These heads carry records only; each has the same non-Markdown files as `0a63219` (`git diff 0a63219 <head>` excluding `*.md` is empty), so they test C3's code, not C4's:
  - **PR run 42467985101 on `9e0334a`:** Mobile checks passed, the rendered suite included (97 passed). The manager's next push cancelled the run at Database proof checks, so its gate failed.
  - **PR run 42468434772 on `27b90b0`:** the same test failed at the same line: `profile-preferences.spec.ts:321`, `screen-account` not visible at `:342`, `Visible screen identities after failure: []`, `1 failed`, `96 passed (5.3m)`. Database proof checks passed; the `504` did not recur.
  - **The environment:** these two runs, C4's run and PR run 42460584909 on `0a63219` (passed, 97 of 97) all used runner image `ubuntu24/20261101.360` and Chrome for Testing 151.0.7922.34 (Playwright's chromium v1234).
  - **The rate:** since M06's fix (`524d42f`, 1 November), 30 Foundation runs executed the rendered suite. Two failed, both this test and both on 8 November: C4's run and PR run 42468434772.
  - **So:** the failure is not tied to C4's change. The same code passed and failed with the same image and browser, so it is intermittent. The reading that it is a race after the second `logout` is still unproven, and so is whether a member could reach an empty screen.
- **What the manager did wrong next (AM9-10):** it asked Nathan to re-run the failed jobs, posted that request on PR40, and drafted a relay for C4's session that depended on it. Nathan rejected it: the manager never asks him to perform a GitHub operation (OD-58). The PR comment is marked withdrawn, and how to handle the failure goes to the Dev Manager as DM-41.
- **The `504` recurs (App Manager 10, 8 November 2026).** PR run 42469365545 on the handover commit `106f849` (records only; C3's code): Stream proof checks failed at `actions/setup-python`, with three `504` responses while it downloaded Python 3.12.14 (09:58:09 to 09:59:01 UTC); no job step ran. API checks, API mobile smoke and Database proof checks downloaded the same version in the same run. Mobile checks: passed, the rendered suite included: `97 passed (4.6m)`, so `profile-preferences.spec.ts:321` passed on this run; 2 of 31 rendered runs since M06's fix have now failed it. The other five application jobs passed; the gate failed on Stream proof checks alone. So the `504` failed a job in two of the last three completed runs that executed PR40's code (C4's run and this one; not PR run 42468434772). DM-41 item 2's premise, that it did not recur, no longer holds; the [addendum](../../ephemeral/2026-11-08-dm-41-addendum-504-recurs.md) takes it to Dev Manager 4.
- **DM-41's answer** (Dev Manager 4, [report](../../continuity/dev-manager/reviews/2026-11-08-dm-41-p06-2-f-c4-run-failure.md), `49ef4a4`): a repair pass, C5, in `Glow App - No Stream`, fixes the rendered race in the spec (its probes: the test's immediate back races the app's post-logout `replaceState('/')` and `history.go(-2)`, and `main` fails the same way), retries the toolchain install once, verifies C4's code by its own run and appends "Correction C4" in Outcome 5's form; the manager's reading above is refined, not confirmed. Dispositions: the review log, "DM-41".
- **A third `504`** (App Manager 10, read after C5's prompt was given): PR run 42470101373 on `10cb35f` (records only; C3's code) failed Stream proof checks at `actions/setup-python`, with three `504` responses (10:08:21 to 10:09:08 UTC) before any step; the other five application jobs passed, the rendered suite included, so 2 of 32 rendered runs since M06's fix have failed `profile-preferences.spec.ts:321`. It supports DM-41 item 2 and changes nothing in C5's prompt; the manager read this run late, after writing "2 of 31" into C5's prompt; that figure is the count to `106f849`, and the rate is 2 of 32 with this run. PR run 42473262141 on `33c4cc2` (C3's code) then passed every job, the gate included, with the rendered suite passing: 2 of 33. A green run on the old code settles nothing (OD-21); C5's run is the run of record.
- **Next:** repair pass C5 (the brief, "Repair pass C5").

## Correction C4 (written by repair pass C5)

- **Provenance** (DM-41 4.2). Repair pass C5 wrote this section, not C4's session. C4's own draft was kept only in that session's files, and was not recovered after Nathan archived the session. The section is written from C4's code head `691dfbad0ab38d60ba2eb0d9715512c85b5aaccf` (read by C5 with `git diff f87e8b1 691dfba`) and from the manager's section above, "Correction C4: the stop, and the manager's verification".
  - **What it cannot supply:** C4's own start gate, its environment check, and its command results (the script check of each quoted item, its parse-tree comparison, its scratch-copy runs of the four new examples, and its `npm run check`). Their outcomes are known only as the manager's verification above states them.
  - **What was verified, and by whom:** the manager verified, from the parse trees without comments, that only the first render test's name changed outside comments, and by script that the comment carries DM-40 section 4.2's words with the differences named below. DM-41 section 9 confirmed the same for the code. C5's own run of record on a head that holds `691dfba`'s code is in "Repair pass C5", below.
  - **C5's own check of the words** (informational, for this section): a script joined `691dfba`'s comment blocks, normalized whitespace and searched for each DM-40 4.2 quotation. The source check's sentence, the `Reflect` and `Object` item and F0's family are exact; the callback item matches with "Another expression" for "Any other expression"; the destructuring exception matches with "(below);" for "(below)."; the four known-passing entries and "written with `=`" are present. "follows", "wherever" and "every" do not occur in the comments; "all" occurs once, in an unchanged comment outside the render-rule list ("which is all the screens render").
- **Work:** the brief's "Correction C4" (revision 4), Outcome 1 to 5, on DM-40's terms ([report](../../continuity/dev-manager/reviews/2026-11-08-dm-40-p06-2-f-c3-review-and-od-57.md), sections 4.2 and 6; conditions 1.1 to 1.4).
- **Prompt:** [`docs/ephemeral/2026-11-08-p06-2-f-c4-correction-prompt.md`](../../ephemeral/2026-11-08-p06-2-f-c4-correction-prompt.md), revision 1, from `0a63219` of the manager branch. Branch `claude/upbeat-mccarthy-499h9k`.
- **Code head:** `691dfbad0ab38d60ba2eb0d9715512c85b5aaccf`, one commit, `apps/mobile/src/chat/display-rule.test.ts` only (+42 −17).
- **C4's own run:** push run 42464917902 on `691dfba` failed in Database proof checks (the `504`) and Mobile checks (`profile-preferences.spec.ts:321`), neither touching C4's change (the manager's section above). C4's code is verified by repair pass C5's run of record instead (DM-41 item 3).
- **What this section supersedes** (DM-40 4.2). C3's three items that its delta re-review's findings 1 to 3 concern (the callback item, the destructuring assignment and the destructuring exception, as "Correction C3" states them), with the other wording the items below replace (the source check's last sentence, the `Reflect` and `Object` item's "whatever its key", and F0's family's `VirtualizedList` reason), are superseded by the words below. This section does not edit them.

### The comment's words, as `691dfba` carries them

Line numbers are in `apps/mobile/src/chat/display-rule.test.ts` at `691dfba`. Each item replaces the text the brief names (at `f87e8b1`).

- **The source check's last sentence** (`:124-128`), exactly as DM-40 4.2 gives it:

  > As a text match, spacing, line breaks, parentheses, comments, string contents and bracket forms evade it, for example `message ?.name`, `(message)as{…}`, `'name'in message`, `'/*'` in a string and `Reflect['get']`; C3's verifiers and its delta re-review found these, and the type check refuses each one tried.

- **The destructuring assignment** (`:157-159`): "a destructuring assignment written with `=`".
- **The callback item** (`:165-173`), with **one narrowing**: "Another expression" where DM-40 4.2 reads "Any other expression". It drops a coverage word that DM-38 4.2 bars; the manager and DM-41 section 9 read it as narrower.

  > a callback whose parameter widens what it is given, or whose return of Glow's data is widened. An inline arrow function or function expression is compared at each parameter that has a type annotation, against its contextual signature [15]; what it returns is checked as a widening (above). Another expression whose type has a call signature (a function's name, a `useCallback` result, a property read such as `view.line`) is compared at each parameter and at its return, against the call's resolved parameter or its contextual type [C2-1a to C2-1e]. An object literal property written `key: value` or `{ key }`, in a literal that has a contextual type, is compared by these two rules [no planted form]. A function reached only through an object or a class instance is not compared (below).

- **`Reflect` and `Object` by a destructuring** (`:179-182`), exactly as DM-40 4.2 gives it:

  > by a destructuring whose type is `Reflect` or `ObjectConstructor`, as a string or computed key that names one gives [C2-3c, C2-3d]; a key of a union type gives a union, which is not refused (O5)

  The item keeps its earlier bracket, so it cites C2-3c and C2-3d twice (DM-41 section 9, a nit, not wrong).
- **The destructuring exception** (`:188-192`), with **one punctuation change**: its last sentence ends in ";" where DM-40 4.2 ends it with ".", because the item continues into the list's next exception ("(below); and a type parameter of a function outside the two files, …"):

  > the initializer of an object destructuring when no enclosing pattern is annotated (C2: only then; C2-4b pins it). The pattern's own check reads the initializer's fields only when the pattern is typed as Glow's data, as when the initializer types it. When the pattern's type comes from context, as for an unannotated parameter of a contextually typed function, the initializer is exempt and not checked (below);

- **F0's family** (`:238-242`), exactly as DM-40 4.2 gives it, keeping the sentence's start ("…") as it was:

  > …and so do `Array.from` and `new Set` over the messages, since the check reads an `ArrayLike` parameter's index signature, and an `Iterable` parameter's symbol-keyed iterator, which it does not find by name on the array, as widenings. A `VirtualizedList`, whose `data` prop is typed `any`, fails as a widening to `unknown` and to `any`.

- **"What it is known to pass" gains four entries** (`:223-233`), as DM-40 4.2 gives them:
  - **A function reached only through an object or class instance** (C3's delta re-review, finding 1): `const view: { line(entry: ConversationMessage): string } = { line(entry: Loose) { return entry.name ?? ''; } }`, then `view.line(message)`. The same holds for an accessor, for a class's method or field under an interface type, and for an object literal with no contextual type that is given later.
  - **A contextually typed parameter's destructuring default** (finding 2): `const caption: (entry?: Loose) => string = ({ name } = message) => name ?? ''`.
  - **A destructuring target in a `for…of` head** (finding 3): `for ({ ...rest } of conversation.messages) break;`.
  - **A reflective global reached through a key of a union type** (O5): `globalThis[key]`, with `key: 'Reflect' | 'JSON'`. No read through it was found.

### The new test name

`:695`: `today's chat screens and list rows pass both render-rule checks (M05 finding 18)`, as DM-40 section 6 gives it, in place of `the chat screens render only the contract's fields: no provider-shaped field is read, whatever the validators let through (M05 finding 18)`. Outside comments, it is the only change (the manager's verification above: one of 559 lines differs).

### Nits 6 and 7: C2's forms by class and ID

From "Correction C2" (its N1 to N9 table, its mechanism table and its verifiers' paragraph), as C3's "Kept for option (c)'s brief" lists them:

- **N1** (20): r1, r3, r4, r7, d1, d5, d6, d8, s1, s3, s7, X1, X2, X3, X5, X6, X7, X8b, P10, P10b; the verifiers added X5r and X6b.
- **N2** (7): E6, T2, T3, T4, T5, T10, T11. Its table cell also says "one in `rows.ts`" without an ID.
- **N3** (8): E5, I4, I6, T8, R3, R14, R11, R20.
- **N4** (5): P3, R6, A8 (tuples); P9, K6r (arrays four deep).
- **N5** (1): P5b; the verifiers added P5d.
- **N6** (3): A2, A2b, A5.
- **N7** (3): R1, R2, R21.
- **N8** (1): R7.
- **N9:** P10b, counted under N1.

**Nit 6, the duplicate IDs.** C2's probe IDs are not unique:
- **`R3`** is "now caught" in the mechanism table's "returned" row ("R3 and R8 now caught"), and is listed under N3, which passes.
- **`R6`** is listed under N4, which passes, and is among the caught by-reference forms in N8's row ("The by-reference forms are caught (R6, R15)").
- C2's mechanism-reversal table also uses `R2b`, `R3` and `R6` as names of its reversals, a third use of the same letters.

So a form named only `R3` or `R6` is ambiguous. Option (c)'s brief takes each by its class and its written form, not its ID alone.

**Nit 7, the 49th form.** The class lists name 48 forms; the mechanism table's last column sums to 49. The mechanism table's "passed" row reads "6 → 4 (**N4**, **N5**; P4 and P4b now caught)", so four forms of that row pass, in N4 and N5. The lists name three of them: P3 and P9 (N4) and P5b (N5). **So the 49th is the "passed" row's fourth form, in N4 or N5.** Its ID is not settled by C2's record. The two candidates the records name are both N5's mechanism (a rejection reason that is `any`): P5, which its verifier placed in the closure limit, and P5d, which the verifiers added "with no closure". On that evidence it is placed in **N5**, with its ID unsettled between P5 and P5d. This is a reading of the records, not a re-run.

### DM-40 1.3's forms, for option (c)'s inputs

Each passes the render test, `tsc` and ESLint at `f87e8b1` (C3's delta re-review; DM-40 section 3). `T` is `{ line(entry: ConversationMessage): string }`; `Loose` is `{ name?: string; text: string | null }`; each is an edit to `MessageRow` in `screen.tsx` unless named.

| From | Form |
|---|---|
| Finding 1 (C3's delta re-review) | An object literal's method shorthand: `const view: T = { line(entry: Loose) { return entry.name ?? ''; } }`, rendering `view.line(message)`. Also as a JSX prop (C4), through an interface with overloads (C5), as a class instance under that interface type (C3), and in `rows.ts` (C15) |
| Finding 2 | A contextually typed destructuring default: `const caption: (entry?: Loose) => string = ({ name } = message) => name ?? ''` (X1), and the same as a JSX prop (X2) |
| Finding 3 | A destructuring target in a `for…of` head: `for ({ ...rest } of conversation.messages) break;` (D5); the manager's form `let rest: Loose = { text: null }; for ({ ...rest } of [message]) break;` |
| Finding 4 | Source-check text-match misses, each refused by the type check: `(message)as{…}`, `message as/* */{…}`, `<{…}>conversation` in `rows.ts`, `'/*'` and `'*/'` in strings, `any` between two apostrophes, `'name'in message`, `...(message)`, `Reflect['get']`, `Object['values']`, `const { stringify } = JSON` |
| O5 | `globalThis[key]`, with `key: 'Reflect' \| 'JSON'` |
| DM-40 F1c | An accessor: `const view: T = { get line() { return shout; } }` |
| DM-40 F1d | A class instance: `const view: T = new Liner()`, whose method is `line(entry: Loose)` |
| DM-40 G2 | An untyped literal given later: `const plain = { line: (entry: Loose) => … }`, then `const view: T = plain` |
| DM-40 G3 | A class field: `line = (entry: Loose) => …` in `Liner` |

DM-40 1.4's three code fixes are noted for (c), not made: exempt only a pattern typed as Glow's data; refuse a `for…of` head whose target is a literal; compare an object literal's method against its contextual property type.

### What C4 did not record, and limits

- C4's start gate, environment check and command results are not recovered (provenance, above).
- C4's code is verified by repair pass C5's run of record, not by C4's own run.
- DM-40 4.2's record part ("the record says the same") is met by this section; the Dev Manager's next consultation confirms it (DM-41 section 9).

## Repair pass C5 (8 November 2026)

- **Work:** the brief's "Repair pass C5" (revision 5), on DM-41's terms ([report](../../continuity/dev-manager/reviews/2026-11-08-dm-41-p06-2-f-c4-run-failure.md); conditions 1.1 to 1.6, 2.1 to 2.3, 2.5, 2.6, 3.1 to 3.3 and 4.1 to 4.3). 1.7 was already in the P11 plan's N01 row; 2.4's CI policy paragraph is the manager's.
- **Prompt:** [`docs/ephemeral/2026-11-08-p06-2-f-c5-repair-prompt.md`](../../ephemeral/2026-11-08-p06-2-f-c5-repair-prompt.md), revision 1, from `33c4cc2a0dfa7e702c306984676788756c3f0a24` of the manager branch `claude/magical-wozniak-yfmmx2`. Started by Nathan, in `Glow App - No Stream`.
- **Branch:** `claude/inspiring-ride-chqpjx` (the push filter's `claude/**`), started at C4's code head `691dfba` with the prompt's commit merged in (`fba7489`).
- **Code head:** `7f1df9615b10e844dc252b9111b3c4c5b67b0b37`: two commits on `fba7489`, `bb80f05` (the spec) and `7f1df96` (the workflow). `git diff --name-only 691dfba HEAD -- . ':(exclude)*.md'` lists only `.github/workflows/foundation.yml` and `apps/mobile/rendered/profile-preferences.spec.ts`.
- **Records head:** the next commit on the branch, Markdown only (the two sections at this file's end); no code after the code head.
- **Run of record:** push run **42481684565** on `7f1df96`: eight of eight jobs `success`, `Application checks passed`, `@glow/mobile` 650 unit tests, rendered `97 passed (5.0m)` with `profile-preferences.spec.ts:321` passing, Mobile 7 min 22 s of 25. **No toolchain retry fired:** each first `actions/setup-python` attempt succeeded, and the two added steps were skipped in all four jobs.
- **Nothing met a stop rule** (1.1, 1.6, 2.6, 3.3). No runtime change was found or made (DM-41 5.3).

### Environment check (names only)

- `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`: none present.
- `STREAM_*`: no name present.
- `GH_TOKEN` and `GITHUB_TOKEN` are present; never read. App commands ran without them.
- **Toolchain:** `node --version` → `v24.19.0`; `npm --version` → `11.9.0`, from `$HOME/.local/bin`, put first on PATH. Every npm, Node and Playwright command ran in `env -i PATH="$HOME/.local/bin:…" HOME="$HOME" LANG=C.UTF-8`. Under `env -i` alone, `npm ci` could not reach the registry (`npm error Exit handler never called!`), so `npm ci` also passed `HTTPS_PROXY`, `NO_PROXY`, `NODE_EXTRA_CA_CERTS` and `NPM_CONFIG_USERCONFIG` by reference, never printed (as C2's record did for two of them). No other command was given them.

### Start gate

| Check | Result |
|---|---|
| `git fetch origin claude/magical-wozniak-yfmmx2 claude/upbeat-mccarthy-499h9k main` | fetched; the manager branch at `1cd515e`, C4's branch at `691dfba`, `main` moved `35a5827..bac3c19` |
| `git switch -C claude/inspiring-ride-chqpjx 691dfba…` | switched; the remote branch did not exist (`git ls-remote` empty) |
| `git merge --no-edit 33c4cc2…` | `Merge made by the 'ort' strategy`, 16 Markdown files, no conflict (`fba7489`) |
| `git merge-base --is-ancestor 691dfba… HEAD` | `C4's code head is in the branch` |
| `git merge-base --is-ancestor 33c4cc2… origin/claude/magical-wozniak-yfmmx2` | `this prompt's commit is on the live branch` |
| `git diff --quiet 691dfba… HEAD -- . ':(exclude)*.md'` | `the code is C4's` |
| `git diff --quiet 33c4cc2… origin/claude/magical-wozniak-yfmmx2 -- . ':(exclude)*.md'` | `no code on the live branch after this prompt` |
| `git show origin/claude/magical-wozniak-yfmmx2:<this record> \| grep -c -E '^## (Correction C4 \(written by repair pass C5\)\|Repair pass C5)$'` | `0` |

**Read before the work:** root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md` and `CLAUDE.md`; the CI policy; the brief's "Correction C4" and "Repair pass C5"; this record's "Correction C4: the stop, and the manager's verification", "Correction C2" (its class and mechanism tables) and "Delta re-review of correction C3"; the M06 record's "The test changes"; DM-40's report, sections 3 to 6; DM-41's report, whole; C4's prompt; `apps/mobile/rendered/profile-preferences.spec.ts`, whole; `.github/workflows/foundation.yml`, whole.

### The browser and the configuration (informational; DM-41 1.1)

- **Browser:** this container's Chromium 1243 headless shell, `/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`, `Google Chrome for Testing 153.0.8010.12`. Playwright 1.62.1 pins chromium 1234 (Chrome for Testing 151.0.7922.34, CI's browser), so every rendered result below is **informational only** (`apps/mobile/AGENTS.md`). No `playwright install` was run.
- **Configuration:** an uncommitted copy of `apps/mobile/playwright.config.ts` in the session's scratch directory, outside the checkout, identical except for `launchOptions.executablePath` (the browser above), the web server's `cwd` (`apps/mobile`), its output directory, and a `testDir` that probe specs could override. Workers 1, retries 0, expect timeout 10 s, as the repository's.
- **Probe specs** (uncommitted, in the scratch directory): the test's own steps to `:340`, then a recorded back. Two traces: a navigation-only trace from the Chrome DevTools Protocol (`Page.navigatedWithinDocument` with its navigation type, top-frame `Page.frameNavigated`, and `Page.getNavigationHistory` at the end), and, in one run, in-page hooks on `history.pushState`, `replaceState`, `go` and `back` and on `popstate`, each logging through `console.debug`.

### The diagnosis (DM-41 1.2)

**The failure reproduces at the test's own sequence** (the repository's spec at `691dfba`, unchanged, `--grep "logout and account switching" --repeat-each 30`): **5 of 30 failed**, each at `:342` (`getByTestId('screen-account').filter({ visible: true })`, element not found in 10 s) with `Visible screen identities after failure: []`, CI's signature.

**The probes, unfixed:**

| Run | Trace | Repeats | Failed | Notes |
|---|---|---|---|---|
| B | navigation only | 20 | 8 | every failure: `goBack()` resolved at `/`, then `about:blank` |
| C | navigation and in-page hooks | 30 | 8 | the hooks did not stop the failure here (DM-41's P4 saw none in 8) |
| E | navigation only, with `Page.getNavigationHistory` | 20 | 4 | every failure: history `[about:blank, /remaining, /account, /]`, current index 0 |

With run A, **25 of 100** unfixed repeats failed in this container. `main` is cited from DM-41's P8 (4 of 12), not repeated.

**One failing repeat's order of history operations** (run C, repeat 0; milliseconds from the test's start):

| ms | Event |
|---|---|
| 4251 | the test sends the second `logout` click, at `/profile-edit`, history length 4 |
| 4284 | the click resolves; the test sends `page.goBack()` at once |
| 4301 | **the app: `history.replaceState(…, '/')`**, from `/profile-edit` |
| 4302 | **`goBack()` resolves; `page.url()` is `http://localhost:8081/`**, the `replaceState`'s URL, so the guard at `:341` (`page.url() === 'about:blank'`) does nothing |
| 4304 | the same-document navigation to `/` (`historyApi`) |
| 4306 | **the app: `history.go(-2)`**, from `/`, length 4 |
| 4321 | **the top frame navigates to `about:blank`**: the test's back and the app's `go(-2)` together go back three entries from index 3, to index 0 |

After the 10 s expectation the page was still `about:blank`: body empty, no input, no visible screen, history length 4. The run-E failures show it is **the tab's initial entry**: `Page.getNavigationHistory` reads `[about:blank, /remaining, /account, /]` with the current index 0. So 1.6's second condition does not hold: the page left is not an app route showing no screen.

**In the passing repeats** the clean-up landed before `goBack()` was sent: `replaceState('/')`, `go(-2)`, a `popstate` at `/remaining`, then `replaceState('/')` and `replaceState('/account')`, all before the click resolved. Back from index 1 then reached `about:blank`, `goBack()` resolved there, and the guard reloaded `/profile-edit`, which showed account entry. In 4 of run C's 22 passes, back landed first, on `/profile`, before the app's clean-up (DM-41's order (i)).

**Where the calls come from.** A run with a stack captured in each hook shows `replaceState` called from a function `replace` and `go` from a function `go` returning a `Promise`, both in Expo Router's web bundle. In `node_modules/expo-router` 58.0.29, `build/global-state/browserHistoryAdapter.js` is the module that calls `window.history.replaceState` and `window.history.go(n)` (lines 29 to 76). So the clean-up is Router's.

**The mechanism, as these repeats show it** (DM-41 3.1, confirmed): logout calls `store.logout(); router.replace('/')`. After the click's task, Router's post-logout history clean-up runs: `replaceState('/')`, then `history.go(-2)`, then the redirect to account entry. A back sent at once can land between the `replaceState` and the `go(-2)`. `goBack()` then resolves on the `replaceState`, a same-document navigation, the guard reads `/`, and the two traversals carry the tab to its initial `about:blank`, outside the app.

### The fix (DM-41 1.3)

`apps/mobile/rendered/profile-preferences.spec.ts`, commit `bb80f05`, +4 lines, nothing removed, loosened or moved:

```ts
  await active(page, 'logout').click();
  // Router's post-logout history clean-up (replaceState('/'), then history.go(-2), then the
  // redirect to account entry) runs after the click's task. A back sent before it lands can
  // resolve on that replaceState and then leave the app (DM-41). Wait for account entry first.
  await expect(active(page, 'screen-account')).toBeVisible();
  await page.goBack();
```

The wait is the one 1.3 names, after the second `logout` click and before `page.goBack()`; the comment states 1.2's mechanism, not M06's shared-control reason. M06's comment at `:327-328` is unchanged.

### The measurement (DM-41 1.4)

| Sequence | Where | Repeats | Failed |
|---|---|---|---|
| Unfixed, the repository's spec (run A) | `691dfba`'s spec | 30 | 5 |
| Unfixed, the probes (runs B, C, E) | the probe spec | 70 | 20 |
| **Fixed, the probe** (run D) | the probe spec, with the wait | **40** | **0** |
| **Fixed, the repository's spec** (run F) | `bb80f05`'s spec, `--grep "logout and account switching" --repeat-each 40` | **40** | **0** (`40 passed (3.1m)`) |
| The whole rendered suite, once, with the fix | `bb80f05`'s spec | 97 tests | 0 (`97 passed (5.0m)`) |

**Where back lands with the fix** (run D, 40 of 40, the same in every repeat): the clean-up completes before the wait passes (`replaceState('/')`, the traversal to `/remaining`, `replaceState('/')`, `replaceState('/account')`); `goBack()` then **leaves the app**, resolving at `about:blank`; the guard at `:341` loads `/profile-edit`, which shows account entry at `/account`, with history `[about:blank, /account]`. So the test's last two assertions (`:346-347` after the fix) run after a fresh load, as in its siblings, and its in-app retained-state checks are the ones at `:331-332` and `:336-338`, as DM-41 1.4 says.

**The optional assertion that back leaves the app was not added.** Every fixed repeat here left the app, but on Chromium 1243, not CI's pinned 1234; an assertion that held here and failed there would turn the run of record red on a browser difference. The guard's fresh-load path covers both outcomes, and the wait already removes the race.

### The scan (DM-41 1.5)

The 13 `page.goBack()` calls in `apps/mobile/rendered/` at `691dfba`, with what precedes each (line numbers at `691dfba`; after the fix, `profile-preferences.spec.ts`'s calls from `:340` on are four lines later):

| # | Call | What precedes it | Changed? |
|---|---|---|---|
| 1 | `discovery.spec.ts:86` | `discovery-next` click, then `expect.poll(() => identities(page)).toEqual(…)` | No: a wait |
| 2 | `discovery.spec.ts:219` | `logout` click, then `screen-account` visible and two count checks | No: a wait |
| 3 | `onboarding.spec.ts:26` | in `backAfterLogout`, `screen-account` visible (its callers at `:152` and `:272` click `logout` first) | No: a wait |
| 4 | `profile-preferences.spec.ts:139` | `dev-profile-change` click, with no wait | No: see below |
| 5 | `profile-preferences.spec.ts:191` | `dev-media-change` click, with no wait (after `development-link`) | No: see below |
| 6 | `profile-preferences.spec.ts:217` | `profile-preview` click, then `candidate-unavailable` visible | No: a wait |
| 7 | `profile-preferences.spec.ts:250` | `profile-preview` click, then three visibility checks | No: a wait |
| 8 | `profile-preferences.spec.ts:340` | the second `logout` click, with no wait | **Yes: the fix** (now `:344`) |
| 9 | `profile-preferences.spec.ts:387` | `dev-pair-${direction}` click, then `candidate-preview` count 0 | No: a wait |
| 10 | `profile-preferences.spec.ts:409` | `dev-pair-restore_viewer_preferences` click, then `candidate-preview` count 1 | No: a wait |
| 11 | `profile-preferences.spec.ts:425` | `dev-pair-viewer_pause` click, then `candidate-preview` count 0 | No: a wait |
| 12 | `state-corrections.spec.ts:99` | `eligibility-submit` click, then `screen-eligibility` visible, the date's value and the age-check text | No: a wait |
| 13 | `state-corrections.spec.ts:210` | `session-expire` click, then `screen-account` visible | No: a wait |

**`:139` and `:191`, the two that follow a click with no wait.** Their handlers (`development.tsx:26`) call `profiles.developmentChange(change)` and no `router` method. A `Stack.Protected` guard could still flip through the stage: `/recommended`'s guard is `state.stage === 'eligible'` (`routes.ts:24`), and the stage reads `profiles.getSnapshot().canDiscover` (`onboarding/store.ts:109`). So each was checked:
- **`:139`, `dev-profile-change`:** the profile change bumps the name and summary and calls `retract()`, which demotes only a profile that is no longer eligible; this one stays eligible. A probe of the test's steps to the click, with the history hooks, then 1.5 s without a back: **no history operation in 10 of 10**, and discovery stays (`Make room for` 1 → 1).
- **`:191`, `dev-media-change`:** the profile is paused at that point, so `canDiscover` is already false; the media change cannot flip the guard. The same probe: **no history operation from the click in 10 of 10**, discovery 0 → 0. In 9 of 10 the hooks recorded one `pushState('/development')` 21 to 31 ms in: the preceding `development-link` click's own navigation, which must land before `dev-media-change` can be clicked, since that button is only on the development screen.

So neither meets 1.5's rule, and no call other than `:340` was changed.

### The toolchain retry (DM-41 2.1 to 2.3)

`.github/workflows/foundation.yml`, commit `7f1df96`. In each of the four jobs that install Python (API checks, API mobile smoke, Stream proof checks, Database proof checks), the one `actions/setup-python` step became three:

```yaml
      - id: python
        uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        continue-on-error: true
        with:
          python-version: '3.12.14'
      - name: Wait 60 s before the one retry of the Python install (DM-41)
        if: steps.python.outcome == 'failure'
        run: echo "::warning::actions/setup-python failed on its first attempt; retrying once after 60 s" && sleep 60
      - name: Retry the Python install once (DM-41)
        if: steps.python.outcome == 'failure'
        uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: '3.12.14'
```

- **What is retried:** only the Python install, at its existing pin and version. `actions/setup-node` is **not** wrapped (2.1 makes it optional): the `504` was seen only in the Python download, and the change stays smallest. So 2.4's paragraph takes the form without the parenthesis. No checkout, dependency install, check, test or proof step is retried or made `continue-on-error`.
- **The pause:** a fixed **60 s**, then one retry.
- **How it reads in the log** (GitHub's documented semantics): with `continue-on-error: true`, a failed first attempt has `steps.python.outcome` `failure` and `conclusion` `success`, so the job goes on. Its step shows its own error lines, the wait step prints the `::warning::` annotation, and the step named "Retry the Python install once (DM-41)" runs. When the first attempt succeeds, both added steps show as skipped. A step `if:` without a status function is `success() && …`, which holds after a `continue-on-error` failure.
- **A failed retry fails the job:** the retry step has no `continue-on-error`, so its failure fails the job, and the steps after it are skipped; the gate then fails on that job's result.
- **Nothing new** (checked by parsing both versions): the same four action pins; triggers, `permissions`, `concurrency`, each job's `timeout-minutes`, `needs`, `if`, `defaults` and `name` unchanged; the eight job names unchanged; the gate's step unchanged. Only the four `api`, `smoke`, `proof` and `database` jobs gained two steps each, and their other steps are as before. No cache, no new source: the install is setup-python's own, as before.
- **The size** (DM-41 5.1): `git diff --numstat 691dfba 7f1df96 -- .github/workflows/foundation.yml` → `44 4`: **48 changed non-test lines**, all in the workflow. The spec's 4 added lines are test lines.

### Commands and results

All in `apps/mobile` unless named, in the clean process environment above.

| Command | Result |
|---|---|
| `npm ci --ignore-scripts` (with the proxy names) | succeeded; then `npm audit`: `17 moderate severity vulnerabilities` |
| `./node_modules/.bin/playwright --version` | `Version 1.62.1` |
| run A: `playwright test -c <scratch config> profile-preferences.spec.ts --grep "logout and account switching" --repeat-each 30` at `691dfba` | `5 failed`, `25 passed (3.3m)`, each failure at `:342` |
| runs B, C, E (probe, unfixed): `--repeat-each 20`, `30`, `20` | `8 failed, 12 passed (2.8m)`; `8 failed, 22 passed (3.6m)`; `4 failed, 16 passed (2.2m)` |
| run D (probe, fixed): `--repeat-each 40` | `40 passed (3.1m)` |
| run F: the repository's spec with the fix, as run A with `--repeat-each 40` | `40 passed (3.1m)` |
| the whole rendered suite with the fix: `playwright test -c <scratch config>` | `97 passed (5.0m)` |
| the stack probe (fixed, hooks with stacks): `--repeat-each 1` | `1 passed`; `replace` and `go` in `expo-router/entry.bundle` |
| the scan probe (`:139` and `:191`): `--repeat-each 10` | `20 passed (1.2m)`; results above |
| `npm run check` | `tsc --noEmit` and `eslint .` clean; `ℹ tests 650`, `ℹ pass 650`; exit 0 |
| `node --test src/chat/display-rule.test.ts` | `ℹ tests 21`, `ℹ pass 21`, `ℹ fail 0` |
| the workflow parsed before and after with PyYAML | the structure checks above all true; `pins same: True` |
| `git push -u origin claude/inspiring-ride-chqpjx` (code commits only) | `* [new branch]`, at `7f1df96` |

### The run of record (DM-41 3.2)

Foundation push run **42481684565** (run 846, attempt 1), on `7f1df9615b10e844dc252b9111b3c4c5b67b0b37`, the branch's first push (12:44:57 UTC). Read with the GitHub tools (the run, its jobs and steps, and each job's log). Runner image `ubuntu-24.04` version `20261101.360.1` in every job. **Conclusion: success.**

| Job | Conclusion | What its steps and log show | Duration |
|---|---|---|---|
| Change scope | success | `COMPARE_BASE` `0000…`, a new branch: `{"full": true, "reason": "missing-or-invalid-comparison", "paths": []}`, so full checks ("New-branch zero-base pushes conservatively run full checks") | 9 s |
| API checks | success | setup-python: `Version 3.12.14 was not found in the local cache`, then `Successfully set up CPython (3.12.14)` on the first attempt; **the wait and retry steps skipped**; the candidate policy tests (`Ran 14 tests … OK`, `Ran 18 tests … OK`), `manage.py test` (`Ran 366 tests … OK`), Ruff and mypy, and the contracts' tests (`Ran 39 tests … OK`) | 48 s |
| Mobile checks | success | `@glow/contracts` `ℹ tests 586`, `ℹ pass 586`, `ℹ fail 0`; `@glow/mobile` **`ℹ tests 650`, `ℹ pass 650`, `ℹ fail 0`**; `Dependencies are up to date`; `export:development` (`Android Bundled … (1344 modules)`, `iOS Bundled … (1361 modules)`, `Exported: .work/native-export`); Chrome for Testing 151.0.7922.34 (`playwright chromium v1234`) installed; the rendered suite **`97 passed (5.0m)`**, with no failed, flaky or skipped line, and `✓ 82 rendered/profile-preferences.spec.ts:321:5 › logout and account switching … (3.8s)`; the layout artifact uploaded (2 files, `p04-empty-form-layout`, artifact 13617778533) | **7 min 22 s of 25** (12:45:11 to 12:52:33) |
| API mobile smoke | success | setup-python as above, first attempt (`Successfully set up CPython (3.12.14)`); **the wait and retry steps skipped**; setup-node, the hash-locked install, `npm ci`, and the smoke script and its tests | 1 min 24 s |
| API artifact checks | success | the pinned image built; the inspection, refusals, loopback smoke and termination | 19 s |
| Stream proof checks | success | setup-python as above, first attempt; **the wait and retry steps skipped**; the hash-locked installs, the offline tests, Ruff and mypy (`Success: no issues found in 57 source files`), `node --check` and the run plan | 1 min 31 s |
| Database proof checks | success | setup-python as above, first attempt; **the wait and retry steps skipped**; the offline tests (`Ran 160 tests`), the disposable PostgreSQL 17.11, the wrong marker's and `dbshell`'s refusals, the migrations, the suite on both subjects, the second run's refusal, the results artifact and the clean-up | 5 min 7 s |
| Foundation gate | success; its line: **`Application checks passed`** | | 4 s |

- **The rendered count:** 97 of 97, the test this pass fixed included. It is one pinned-browser run; it shows the fix on CI's browser once, not a rate.
- **Whether a toolchain retry fired: no.** In API checks, API mobile smoke, Stream proof checks and Database proof checks, step 3 (`Run actions/setup-python@5fda3b9…`) is `success`, and steps 4 ("Wait 60 s before the one retry of the Python install (DM-41)") and 5 ("Retry the Python install once (DM-41)") are `skipped`. Each job downloaded Python 3.12.14 (it was not in the runner's cache) and set it up in 6 to 7 s; no `504` and no warning annotation appear in the four logs.
- **C4's code is verified** by this run (DM-41 item 3): `7f1df96`'s tree holds `691dfba`'s code, with only the spec's wait and the workflow's retry added (`git diff --name-only 691dfba 7f1df96 -- . ':(exclude)*.md'`).
- Nothing else was pushed until this run had completed (AM8-20).

### Limits, and what could not run (DM-41 2.5)

- **The retry path is not exercised by the run of record** unless a download failed during it (above, it did not: no download failed, and both added steps were skipped in all four jobs). No deliberately failing run was pushed to test it (2.5). The review reads the YAML against GitHub's documented semantics of `continue-on-error` and `steps.<id>.outcome`.
- **Every local rendered result is informational:** Chromium 1243 headless shell (Chrome for Testing 153.0.8010.12), not the pinned 1234. CI's run is the pinned-browser run of record.
- **The in-page hooks shift timing**, as DM-41's P4 found; here they did not stop the failure (8 of 30). The navigation-only runs (B, E) show the same order without them.
- **The native analogue** (Android hardware back, an iOS back gesture during the clean-up) is beyond the web harness; it is the P11 plan's N01 row (1.7).
- `main` was not re-run; DM-41's P8 is cited.
- Not run: `check:expo`, `export:development` (CI runs both), and any command in `proofs/`. No GitHub write other than the push of this branch; nothing in Notion.

## Review of C4 and repair pass C5 (8 November 2026)

- **The review:** prompt revision 1 at `0a49e62` ([prompt](../../ephemeral/2026-11-08-p06-2-f-c5-review-prompt.md)), of code head `7f1df96`, on S2's terms (DM-41 5.1 to 5.3; DM-40 3.1 to 3.4), in `Glow App - No Stream`. Start gate passed; classification `"full": true`; environment check clean (names only).
- **Verdict: changes required.** Two forms inside C4's narrowed inline-callback words pass the render test, `tsc` and ESLint (findings 1 and 2); everything else in scope holds.
- **Findings:**

| # | Severity | Finding | Class |
|---|---|---|---|
| 1 | Blocking (DM-39 1.2) | A function expression with a `this` parameter evades the inline-callback comparison: the check pairs `node.parameters[index]` with `signature.parameters[index]` (`display-rule.test.ts:479-480`), and a declared `this` parameter is in the first list and not the second, so the annotated parameter is never compared. Form: `<Text>{[message].map(function (this: ConversationMessage, entry: Loose) { return entry.name ?? ''; }).join()}</Text>` | A form evades a listed refusal; to the Dev Manager first (DM-40 3.4) |
| 2 | Blocking (DM-39 1.2) | A contextual signature with a rest parameter leaves `signature.parameters[1]` undefined, so the second parameter is skipped (the check's own `parameterAt` handles rest; this rule does not use it). Form: `const join: (...entries: ConversationMessage[]) => string = (first, second: Loose) => second.name ?? String(first.text);`, rendering `{join(message, message)}` | The same |
| 3 | Low | "Correction C4 (written by repair pass C5)" says "'follows', 'wherever' and 'every' do not occur in the comments"; `every` occurs at `:185` (the Array method), "wherever" at `:511` (a code comment) and "Every" at `:105` and `:721`. None claims coverage, so DM-38 4.2 is met | A record claims more than the file shows; a records fix |
| 4 | Nit | The `VirtualizedList` reason: `data` is declared `any`, but the check reports a widening to `unknown` in every form tried, and to `any` only when `getItem` returns Glow's data; the comment says it fails as both | A comment line, by a strict reading of the last class |

- **What holds:** about 30 of the review's literal-property forms and 17 destructuring forms are refused; the four new known-passing examples pass; `f87e8b1` and `691dfba` differ outside comments only in the test name's string (6,501 nodes each); the diagnosis reproduces (unfixed 7 of 15, fixed 15 of 15, Chromium 1243, informational); the spec adds one wait and nothing else; the scan is complete; the workflow retries only `setup-python`, at the same pin, with `continue-on-error` on the four first attempts only, and the gate is unchanged. An informational note: when a first attempt fails and the retry passes, the job reads `success`, so the gate cannot tell it from a clean pass; the first failure shows in the job's log and its warning annotation, which meets DM-41 2.2.
- **Runs read:** run of record 42481684565 on `7f1df96` and PR run 42483045373 on `0a49e62`: eight of eight jobs passed, retry steps skipped, `Application checks passed`, rendered 97 passed.
- **The manager's verification** (App Manager 10): findings 1 and 2 re-run as real edits to `MessageRow` in a scratch copy of `7f1df96`, with `type Loose = { name?: string; text: string | null }`: each passed `display-rule.test.ts` 21 of 21 and `tsc --noEmit`; the control, the same widening as an annotated arrow, failed 2 of 21, as it should; `screen.tsx`'s SHA-256 prefix `3aef02c392c546db` was restored after each.
- **Dispositions:** findings 1 and 2 fall in the correction classes, and under DM-40 3.4 they go to the Dev Manager before any further correction: DM-42 ([consultation](../../ephemeral/2026-11-08-dm-42-p06-2-f-c5-review-findings.md)). Findings 3 and 4 and the gate note go with it.
- **Codex** found findings 1 and 2 again on `a436211` (P2, `display-rule.test.ts:480` and `:482`); the manager answered both threads, which stay open until C6 is on PR40. Codex had found nothing on `0a49e62`; PR run 42483045373 on `0a49e62` passed every job.
- **DM-42's dispositions** ([report](../../continuity/dev-manager/reviews/2026-11-08-dm-42-p06-2-f-c5-review-findings.md), `b338ea2`): findings 1 and 2, option (a), comment-only words that state the inline rule's pairing as written, with F3 (a declared `this` against a signature with no first parameter) named beside them (correction C6); finding 3, C6's record section carries DM-42 2.1's correction line; finding 4, one comment line in DM-42 3.1's words (C6); the gate note, DM-42 4.1's line in the CI policy (applied by the manager).
