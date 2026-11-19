# Dev Manager 5 → Dev Manager 6: handover

- **Direction:** Nathan Amthor, 19 November 2026, in Dev Manager 5's session: *"Create a new version of this session, Glow Dev Manager 6"*. Under OD-35, the outgoing Dev Manager runs its handover and creates its successor with the remote-session tools. The primary manager records the direction in the register.
- **Written by:** Dev Manager 5, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5"), branch `claude/dev-manager`, environment `Glow App - No Stream`.
- **Basis:**
  - the manager branch `claude/magical-wozniak-yfmmx2` at `55ab2a4` ("Handoff: the branch list after DM-96's merge"); DM-96 was read at `ccc05eca4592a36c9df59459ed4eb2c8f1e0a1a5`;
  - `main` at `c2cffbe` (PR56: PF01 1.20, OD-77 to OD-81);
  - this branch at `15aa78d` (DM-96's report), plus this file.
- **What this is:** what the successor needs beyond the charter, the start prompt, the review log and the reports. Dev Manager 5 pushes nothing after this file's commit.

## 1. The role

The charter (`docs/planning/dev-manager.md`) and the start prompt (`docs/planning/start-prompts/dev-manager.md`) hold. So do Dev Manager 3's handover (`2026-11-08-dev-manager-3-handover.md`), sections 1, 2 and 5, and Dev Manager 4's (`2026-11-13-dev-manager-4-handover.md`), sections 1, 2 and 5. In short:

- **What it does:** Nathan's second layer of oversight (OD-15). It reviews, challenges and approves consequential decisions; it gives exact words for every text it conditions (AM9-08).
- **D-07 (OD-75):** two Dev Manager reads per code item, the brief and the pre-merge read. A correction pass happens only for a defect in application behaviour, at a security boundary, or for a false claim. Applying the Dev Manager's own words needs no new read, and takes no deferred-condition row (AD9).
- **Where it writes:** only report files under `docs/continuity/dev-manager/reviews/`, each ending `Status: complete`. It pushes only `claude/dev-manager`.
- **What it never does:**
  - implement or commission sessions (its successor excepted, OD-35);
  - open or merge PRs; edit Notion;
  - call Stream, a database, HDE, Railway, Cloudflare or the TypeSafe API;
  - run `playwright install`, `eas` or `migrate`; run application code;
  - ask Nathan to perform any GitHub operation (OD-58).
- **The relay:** Nathan carries every message by hand (OD-25).

## 2. Rules that bind beyond the charter's text

Read the register in full (OD-01 to OD-81 at the basis). Besides those in the earlier handovers:

- **OD-76:** the Dev Manager's read of governing Markdown stays; there is no AWS use.
- **OD-77 to OD-80** (PF01 1.20, the prototype first):
  - no new cost now;
  - the prototype is the whole system working together;
  - the app uses the existing database;
  - the existing Railway components are to be analyzed and retired;
  - **no design decision about HDE is made now** (OD-80), by any session.
- **OD-81:** `glow-frontend-v2` is deprecated. Dev Manager 5 recorded the words (`2026-11-19-owner-direction-glow-frontend-v2-deprecated.md`).
- **OD-51:** the repository is public for now, so CI minutes cost nothing; it will become private later.
- **Direct owner input:** when Nathan gives a direction in this session, record it word for word in a reports-folder file, with exact words for the register row. `2026-11-19-owner-direction-glow-frontend-v2-deprecated.md` is the latest model.

## 3. What Dev Manager 5 did

| ID | Date | What | Labels | Commit |
|---|---|---|---|---|
| — | 13 Nov | Start note | — | `7fc47e6` |
| DM-68 to DM-81 | 13–17 Nov | SV3 Stages A and B: corrections, scans, the harness locks, Codex's finding, pre-merge reads | SC, BB, DD, EE, FF, MM and others | `9105d11` to `0da7617` |
| DM-76 | 16 Nov | PF02 as canon | — | `ccf1e5a` |
| DM-82 | 17 Nov | PR48's pre-merge read | NN | `10710b2` |
| DM-83 to DM-90 | 17–18 Nov | A05-V to A05-V3, OD-68 to OD-71, the card check and the founding offer | PP, QQ, RR, SS, TT, UU, VV, WW | `3c0a5fe` to `1ce329d` |
| DM-91 to DM-93 | 18 Nov | PF02 1.7; SV2-R's brief, revisions 1, 3 and 5 | XX, YY, ZZ | `b376756`, `37691b5`, `adb769d` |
| DM-94 | 19 Nov | M09, PF01 1.19, D-06, D-07, PF02 1.8 | AD | `221da6d` |
| DM-95 | 19 Nov | PF01 1.20, OD-77 to OD-80 | AE | `04a738c` |
| — | 19 Nov | Owner direction: `glow-frontend-v2` deprecated (OD-81) | AF | `6a3811b` |
| DM-96 | 19 Nov | SV4's brief, revision 1, Stage A (D-07's first read) | AG | `15aa78d` |

**Labels already used** (avoid them for new conditions): those in the earlier handovers, plus SC, AA, BB, DD, EE, FF, MM, NN, PP, QQ, RR, SS, TT, UU, VV, WW, XX, YY, ZZ, AD, AE, AF and AG. Free, for example: AH, AJ, AK.

**DM-95's AE1 to AE9 and the note's AF1 to AF4** were confirmed applied exactly at `c2cffbe` (DM-96, section 2).

## 4. Where things stand

- **The current item is SV4 Stage A** (the brief, `docs/planning/sv4-chat-notifications.md`, revision 1). DM-96 is answered; App Manager 12's disposition and the brief's revision 2 come next. Then come A0's prompt (the CI tooling), A1 (the rules) and A2 (the routes and a fifth suite).
- **DM-96's verdicts, in short:**
  - **C-02 (changes requested):** take revision 1's alternative (b), a block stores `unmatched`. The reason: F10's row change would break the mobile fixture adapter, which reads F10 while it runs (`apps/mobile/src/interactions/fixture-adapter.ts`, line 204; the cleanup cases from line 414), and Stage A changes no mobile file.
  - **C-01:** both reciprocity checks need `retired_at` null, `interact`'s included.
  - **C-08:**
    - a `removed` profile is a deletion, so it is hidden;
    - `chat.history`'s `consent_policy_version` applies fail-closed, and the per-member rule goes to P08.
  - **D8:** the send route answers one code for every cause.
  - **D7:** the token code's users list was completed. `ReciprocalWriterTests` in `test_interactions_offline.py` pins all of `contact.py` as SV3 left it.
- **What comes to you next:**
  - **Confirm AG1 to AG21 as applied** in the brief's revision 2, by script against DM-96's pairs. If the manager departs from them, that revision needs a read.
  - **Before A0 merges:** the CI policy's change (governing Markdown), the complete workflow diff, and each job keeping every check, the decoy-marker refusal included (AG1).
  - **Each stage's pre-merge read** (A0, A1, A2), under D-07.
  - **The Railway analysis prompt** comes to you before it runs (DM-95). Check for:
    - Nathan's authorization of the read, with the token's scope named;
    - variable names only;
    - no deploy, restart, delete or setting change, and no database connection;
    - one component at a time;
    - HDE's components left to HDE's process. `glow-frontend-v2` is on Vercel and outside it, but its source sends `/api/` calls to `glow-backend-v4`.
  - **PF02 1.9** (AM12-31 to AM12-36 folded in) is due for a read.
- **Notion at DM-96:** SV4's Work Register row cites PF01 1.19 and App Manager 8. Check that it has been corrected.

## 5. Working method

The earlier handovers' sections 5 hold. Tools Dev Manager 5 kept in its scratchpad will not survive the session; rebuild them as needed:

1. **Export, do not check out:** `git archive <commit> | tar -x -C <scratch>/export`. Read the export only with `python3 -I`.
2. **Classify with the trusted classifier:** `main`'s `scripts/change_scope.py`, extracted outside the tree (sha256 prefix `b564c62f4a076f51` at the basis). Run it with `python3 -I --base <base> --head <head> --merge-base`.
3. **Verify replace pairs before pushing.** Use bold labels `**XXn — <what>, `<path>`: <title>.**`, followed by `> ```` blocks, old then new. A script applies them in order to copies, and checks each old passage once and each new passage once. It also checks hygiene: no model identifier, last line `Status: complete`.
4. **Check earlier conditions as applied:** each pair's new text occurs once at the later commit, and its old text is gone unless it lies inside the new.
5. **For every brief, search the whole repository:** every name it removes or renames, every line-number, digest or AST pin of a module it changes, and every runtime reader of a contract file it changes. Each brief's earlier-tests list (PF02-R14) is where sessions stop when one is missed.
6. **Notion** (read-only):
   - Implementation Control `3e44590a05eb8118bf02f0dc0c3ea57c`;
   - Dev Manager — reviews and approvals `3e64590a05eb81e29903ca6fccd94268`;
   - the register copy `3e64590a05eb81beaf78d6fa9d64a600`;
   - the Work Register `collection://5ea4c24d-ec63-4afb-a434-8969c26b8fbe`.

   Searching within a page (`page_url`) is cheap; fetch a row by its page ID. State a match only for what you read.
7. **The reply** (Nathan's format): the answer first, in short plain bullets; a named state; nothing unexplained (OD-32); last, the relay message in a four-backtick block naming the report file, the branch commit and the commit read.

Status: complete
