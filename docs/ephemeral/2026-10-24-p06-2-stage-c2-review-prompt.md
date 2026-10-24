# P06.2 Stage C2 review prompt — the exact-head review of C2

- **Owner:** App Manager 7. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 24 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 15: "Stage C under OD-45", point g with DM-22 7.1 and 7.2, and the points it consumes (c, d, e and f with 6.1 to 6.4).
- **Where the result goes:**
  - The reviewer reports to Nathan.
  - The manager records the review and its disposition in the [P06.2 evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md), "Exact-head review of Stage C2", and in the brief's "Sessions".
  - A correction pass follows if the review asks for one.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Fable 5.1 at max.** Effort score 3.79 (confidence 0.86); rung probabilities low 0.00, medium 0.00, high 0.02, extra high 0.17, max 0.81, ultracode 0.00. Model probabilities Fable 5.1 0.81, Opus 5.5 0.19, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.75). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.016, Fable 5.1 at extra high 0.138, Fable 5.1 at max 0.656, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.004, Opus 5.5 at extra high 0.032, Opus 5.5 at max 0.154, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-24T21:58:24Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none needed. The prompt authorizes no credential use and no live provider action. This session is the only security reading of C2 (OD-41), so section 3 names the security focus.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29).
- **Deletion condition:** prune after Stage C2's PR merges and the evidence record holds the review.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.2 Stage C2**, the mobile half of Stage C of P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. You review C2 at one exact head. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

**What came before.** Stage C1 merged on 24 October (PR32, `a8e9528`).

- **Nathan decided D8 as option (b)** (OD-45):
  - the app holds no Stream credential and no provider package;
  - Glow's API serves history and new messages;
  - Stream stays the provider behind Glow's server.
- **C1** built the server's reads and the contracts: `ConversationList`, `MessagePage`, `MessagePageRequest` and `ReadCursorIntent`, with P02's `MessageIntent` and `MessageSubmission`. Their rules are in the production contracts' "F11 under OD-45".
- **C2** builds the mobile interface on those contracts, offline, on an in-process fixture. Its prompt went to Nathan without a Dev Manager read, on DM-22 9.1's terms.
- **C2 is the draft PR33,** from the manager branch `claude/magical-wozniak-yfmmx2` into `main`.
  - **Code:** `cb3a6a6`.
  - **What it adds,** under `apps/mobile/`:
    - `src/chat/`: a `ChatTransport` interface, its only implementation an in-process fixture adapter (`fixture-adapter.ts`), a validating client boundary (`client.ts`), a polling store (`store.ts`), screens, controls, copy and tests;
    - the routes `/conversations` and `/conversation`, guarded in `_layout.tsx` and `onboarding/routes.ts`;
    - a link from the match screens (`interactions/screen.tsx`);
    - `rendered/chat.spec.ts`, and one changed inherited assertion in `rendered/interactions.spec.ts`;
    - the README's walkthrough.

**The run of record** is the session's push run 40135312825 on `cb3a6a6`. All eight jobs passed. The Mobile job took 6 min 16 s of its 15-minute timeout, and its rendered step printed `94 passed (4.5m)`. The head's code is byte-identical to `cb3a6a6`'s.

- **You review one exact head:** `<RECORDS_COMMIT>`.
- **Your scope is PR33's whole code change:** `git diff origin/main...HEAD` over every non-Markdown path, read against the code at `HEAD`. That is 23 files, about 2,270 lines added. Read the Markdown records too, for their claims, not as code.
- **The review is offline:** the code, the offline tests and the run's logs. You call no provider and need no database.
- **What comes after this review.** Report every finding with its severity. A correction pass takes every blocking finding. It also takes any should-fix finding that could do any of these:
  - let a provider field, provider ID or provider text reach a render, a stored client state or a log;
  - let a revoked member see a conversation's history or send in it;
  - show the other member's pending or failed submissions, or any read state of the other member;
  - let the app poll in the background or after its screen is left;
  - key or order messages by `at`, or let a message accepted late never reach the reader or never count as unread;
  - let a retried send show twice, or change its idempotency key or payload;
  - let the app make a network call, load a provider package, open a socket or event stream, or run outside the development fixture mode;
  - let a test pass where it should fail, including the changed inherited assertion;
  - make a record claim more than the code, the tests or the runs show;
  - leave a DM-22 condition (6.1 to 6.4, 7.1, 7.2) unmet.

  Everything else goes into the records. For each finding, say whether it falls in one of those classes.

**How you work:**
- Nathan started you manually and will relay your report to the manager (App Manager 7). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Reversals and scratch work go in a copy outside the repository, never the checkout** (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Never:**
  - dump the environment, or print a credential, token or password;
  - call Stream or any other provider, or run any harness command that reaches it;
  - connect to any database, HDE, Railway or any other provider;
  - run `playwright install`, `eas` or `migrate`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If one is present, stop and report: this session must start in `Glow App - No Stream`.
3. **The toolchain.** The pinned toolchain is in `$HOME/.local/bin`: Node 24.19.0 and npm 11.9.0 (and Python 3.12.14). Put `$HOME/.local/bin` first on PATH in every process you run.
4. **A clean process environment.** Run each component's commands in one, as `docs/operations/local-development.md` and the READMEs show: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <RECORDS_COMMIT>
git rev-parse HEAD                      # must print <RECORDS_COMMIT>
git merge-base --all origin/main HEAD   # expected: one line, a8e952895ebd3ffc9ef0e4d195c8a7111c69b3ae
git merge-base --is-ancestor <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 -- proofs .github services scripts apps packages && echo "no code after this prompt's commit"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c -E '^#+ Exact-head review of Stage C2'   # must print 0
git diff --quiet cb3a6a6dae0f3ad629a1cbd92ea299fcd5cab03a HEAD -- proofs .github services scripts apps packages && echo "the code of the run of record"
git diff --shortstat origin/main...HEAD -- proofs .github services scripts apps packages   # expected: 24 files changed, 2266 insertions(+), 7 deletions(-) (23 code files and the mobile README)
```

If any check fails, stop and report. The checks on `origin/claude/magical-wozniak-yfmmx2` read the live manager branch. The prompt is stale if:
- this prompt's commit is not on that branch;
- code landed after it;
- or this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree and full SHAs:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
git diff --name-only origin/main...HEAD | grep -v '\.md$' | grep -v -E '^apps/mobile/(src/|rendered/)'
```

- **Expected:** `"full": true`.
- **The last command must print nothing.** Every non-Markdown change must be under `apps/mobile/src/` or `apps/mobile/rendered/`. Anything else is code this review would not cover: stop and report it.

**Then read, completely, at `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md` and `apps/mobile/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`: "What P06.2 delivers" (item 5) and "Stage C under OD-45", whole;
- the DM-22 report, `docs/continuity/dev-manager/reviews/2026-10-24-dm-22-p06-2-stage-c-read.md`;
- C2's prompt, `docs/ephemeral/2026-10-24-p06-2-stage-c2-implementation-prompt.md`, revision 1;
- the evidence record's sections "Stage C2" and "Manager verification of Stage C2";
- ADR 0003, decisions 1 to 3;
- `docs/architecture/production-contracts.md`: the idempotency rule, F11 and "F11 under OD-45";
- **the whole code diff,** read whole at `HEAD`: every file under `apps/mobile/src/chat/`, the two routes, the changes to `_layout.tsx`, `onboarding/routes.ts` and `interactions/screen.tsx`, and both rendered specs;
- for comparison, P05's `src/interactions/fixture-adapter.ts` and `store.ts`, `src/contracts/production.ts` and `validation.ts`, and C1's server reads (`services/api/glow_chat/reads.py`, `glow_domain/chat_reads.py`, `chat_projections.py`), whose semantics the fixture mirrors.

**The run's logs:** run 40135312825 on `cb3a6a6`. Read its Mobile job (the corpus check, `npm run check`'s counts, `check:expo`, the export, the rendered tests with the ten new specs) and its gate. Read enough to confirm the claims below, and say what you read.

## 3. What to review

1. **The display rule and the validation boundary** (point g; ADR 0003; the security focus).
   - Does every response the screens use pass `parseAppResponse`, then its DTO's validator, then the kind and match check, before any state changes?
   - Can any provider field, provider ID or provider error text reach a render, the store or a log, through any path, including an error path?
   - A refused response is refused whole: confirm that nothing of it stays in the store.
   - Judge the client's extra refusal of a duplicate `submission_id` or `match_id`.
   - Do the 15 provider-field cases cover point g's list? The rendered journey covers 5 of them; say whether that is enough.
2. **The no-provider test** (DM-22 7.1, as written):
   - Does it cover the three package-name patterns in `package.json`, `package-lock.json` and every import under `apps/mobile/src`, and every construction of `WebSocket` or `EventSource` in the app's source?
   - Its patterns are built from fragments so that it does not match itself. Does that leave a gap?
   - Is any import or construction form a realistic change could use left unmatched? Weigh the gap against what 7.1 names.
3. **The fixture's semantics against C1** (F11 under OD-45; DM-22 6.1 to 6.4):
   - acceptance order;
   - the member's own pending and failed submissions shown only to that member, and the other member's never;
   - "unavailable" as one state with no reason;
   - the latest-message marker over visible rows only, with no text;
   - unread counting only the other member's accepted messages after the cursor;
   - a page cursor opaque and bound to its match.

   Compare each with C1's server code. A difference is a finding only if the app could rely on behavior the server does not give.
4. **Revocation** (point c). A conversation follows its match in the interactions fixture.
   - Does every read, send and cursor move refuse after each revocation the fixture models?
   - Does the store drop the conversation's history when it is refused?
   - Is the refusal the bare `not_found`, telling no more than the match's projection?
   - **Judge the session's C2-X1:** the fixture closes the conversation for both members when the other member's session is revoked, which C1 does not. Does that show one member another's sign-out in the fixture, and does that matter for a fixture?
5. **Polling** (point d; DM-22 7.2):
   - the constants (3 s and 30 s);
   - no request in the background or iOS `inactive`;
   - polling stops when the screen is left, and resumes with one read on return;
   - no timer left running after unmount, and no overlapping requests;
   - "anything new?" asks with the page's own `newer_cursor`.
6. **Keys, order and retry:**
   - messages keyed on `submission_id`, never `at`, and shown in page order;
   - a message accepted after a later one reaches the next poll and counts as unread;
   - a retried send reuses the same intent object, key and payload, and shows once;
   - a lost response reconciles without a second message.
7. **The read cursor** (point e): forward only, only after the other member's newer messages were shown in the foreground, and no read state of the other member anywhere.
8. **Routes:**
   - `/conversations` and `/conversation` are guarded for an active account only. That is stricter than `/matches`, which also admits suspended and deletion-pending accounts. Judge it against point c.
   - The routes carry no query parameter or private value (the routing rule in `onboarding/routes.ts`).
9. **The changed inherited assertion** (`rendered/interactions.spec.ts`, the session's deviation). The active-match detail no longer asserts `Messaging is unavailable`. Is the new assertion an honest replacement, and is anything the old one guarded left unchecked?
10. **The records:**
    - the evidence record's "Stage C2";
    - the README's walkthrough and limits.

    Does any statement claim more than the code, the tests or the runs show? Judge **C2-X2**: no contract names the projection that carries the version a send's `expected_version` must match, and the fixture uses `MatchProjection.version`. Is that a C2 finding, or a contract question for P11, as the manager proposes?
11. **The offline checks,** run at `HEAD` in a clean environment:
    - **the contracts:** `npm ci --ignore-scripts`, `npm run generate` with no diff, and `npm run check` (586 corpus cases);
    - **the mobile app:** `npm ci --ignore-scripts`, `npm run check` (583 at the run of record), `EXPO_OFFLINE=1 npm run check:expo` and `EXPO_OFFLINE=1 npm run export:development`;
    - `npm run test:rendered` only if it can run without `playwright install`, marked "informational, not the pinned browser".

## 4. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`), and the start gate's and the classification's results;
- the environment check;
- how you split the reading, if you did;
- a verdict: **approve**, or **changes required**, with the findings that require them;
- every finding, numbered, with:
  - its severity (blocking, should fix, nit);
  - its file and line;
  - what is wrong, why it matters, and a suggested fix;
  - whether it falls in one of the correction classes above;
- for each focus area, what you checked and what you found;
- the offline checks you ran, with their exact results;
- limits of the review, and open questions.
