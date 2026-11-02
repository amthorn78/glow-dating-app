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
| Mobile checks | success: `npm run check`, `npm run check && npm run check:expo`, `export:development`, the pinned Chromium installed by the workflow, and the rendered suite **`97 passed (5.0m)`**; the empty-form layout artifact uploaded (2 files) | **7 min 27 s of the 25-minute timeout** (03:32:14 to 03:39:41 UTC) |
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
