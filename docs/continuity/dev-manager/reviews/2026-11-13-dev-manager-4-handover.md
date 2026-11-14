# Dev Manager 4 → Dev Manager 5: handover

- **Direction:** Nathan Amthor, 13 November 2026, in Dev Manager 4's session: *"create a new version of this session, Glow Dev Manager 5"*. Under OD-35, at Nathan's direction, the outgoing Dev Manager runs its handover and creates its successor with the remote-session tools. The primary manager records the direction in the register.
- **Written by:** Dev Manager 4, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4"), branch `claude/dev-manager`, environment `Glow App - No Stream` (`env_01GAnJ5Rdi5k1wGvGUxJuDbe`).
- **Basis:**
  - the manager branch `claude/magical-wozniak-yfmmx2` at `30000142eb810050c921ab0d338a939eed67543a`, PR45's head ("SV3 Stage A C2's delta re-review recorded …; DM-67 to the Dev Manager");
  - `main` at `3240ef0acca7983e5b60b9a111be371ed5a16b74` (PR44, SV2 Stage B);
  - this branch at `e7786bb` (DM-67's report), plus this file.
- **What this is:** what the successor needs beyond the charter, the start prompt, the review log and the reports. Dev Manager 4 pushes nothing after this file's commit.

## 1. The role

Read the charter (`docs/planning/dev-manager.md`) and the start prompt (`docs/planning/start-prompts/dev-manager.md`); both hold. Dev Manager 3's handover (`2026-11-08-dev-manager-3-handover.md`), sections 1, 2 and 5, still holds too; this file adds to it. In short:
- **What it does:** Nathan's second layer of oversight (OD-15). It reviews, challenges and approves consequential decisions, gives exact words for every text it conditions (AM9-08), and reads governing Markdown before the PR that carries it merges.
- **Where it writes:** only report files under `docs/continuity/dev-manager/reviews/`, each ending `Status: complete`. It pushes only `claude/dev-manager`.
- **What it never does:** implement or commission sessions (its successor excepted, OD-35); open or merge PRs; edit Notion; call Stream, a database, HDE, Railway, Cloudflare or the TypeSafe API; run `playwright install`, `eas` or `migrate`; run application code; ask Nathan to perform any GitHub operation (OD-58).
- **The relay:** Nathan carries every message by hand (OD-25). Every consultation repeats the charter lines and ends: *"Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`."*

## 2. Rules that bind beyond the charter's text

Read the register in full (OD-01 to OD-64 at the basis). Besides those in Dev Manager 3's handover, section 2:
- **OD-58:** never ask Nathan to run a GitHub operation; a failed run is recorded and read, not re-run by him. **OD-21:** a passing rerun alone does not resolve an intermittent failure.
- **OD-60:** the discovery product rules (two-way "show me" sets, distance by area, no exact coordinates). **OD-61** and **OD-62:** SV2's identity and photo decisions (`2026-11-10-nathan-answers-dm-52.md` holds Nathan's answers to DM-52 word for word).
- **OD-64** (13 November): F7's probing bounded by field (birth date locked once identity-verified; gender, orientation, relationship status at most 2 changes per field per rolling 30 days; looking for unlimited; a plain-words notice; change-and-revert to trust and safety). Carried to before P11 with its own brief, which comes to the Dev Manager before it is built.
- **AM9-08:** where a condition changes text, give the words, as replace pairs (an old passage found exactly once, and its new text) or words to place. The manager applies them by script, so each old passage must be unique at the commit read. Verify that yourself before pushing (section 5).
- **Coverage claims:** never write "any", "every" or "all" over code you have not enumerated. Enumerate by AST, then state named forms and limits. Dev Manager 4's own errors of this kind are recorded in the reports that correct them: DM-61's "completes without waiting" (corrected in DM-63), DM-64 T9's signature (ii) (DM-66 CK5), DM-64 T8's limit words (DM-67 R1) and DM-66's "harmless extra coverage" (DM-67 N1). Acknowledge an error of your own in the report that finds it.
- **The supersession sweep:** dated records keep their history, with a pointer or note where they would otherwise mislead (DM-67 GD9 is an example).

## 3. What Dev Manager 4 did

| ID | Date | What | Verdict, in short | Commit |
|---|---|---|---|---|
| — | 8 Nov | Start note | — | `58bacb8` |
| DM-41 to DM-43 | 8 Nov | P06.2-F: C4's failed run; forms inside C4's and C6's callback words | Repair pass approved; (a) with exact words | `49ef4a4`, `b338ea2`, `3a1c6a0` |
| DM-44 | 8 Nov | P06.3's brief | Approved with conditions | `65618c1` |
| DM-45 to DM-50 | 9 Nov | SV1: brief, revision 2, review findings (F-2), lost runs, C2's delta review and pre-merge read | Approved with conditions throughout | `0dcd122`, `778ee29`, `1516629`, `c6bce37`, `21882dd`, `85df720` |
| DM-51 | 9 Nov | The second A05 message | Approved with M1 to M17 | `0fc2426` |
| DM-52 | 10 Nov | SV2's brief, with Nathan's answers | B1 to B55 (consolidated) | `eefa349`, `e616f33`, `093204a` |
| DM-53 to DM-59 | 10–11 Nov | SV2 Stages A and B: owned paths, decisions, review findings, pre-merge reads | W, Y, Z, V, U, J and L conditions | `f60cfda` to `d2b46ad` |
| DM-60 | 11 Nov | SV3's brief, revision 1 | Q1 to Q20 | `777a6ad` |
| DM-61, DM-62 | 12 Nov | SV3 Stage A: the lock cycle (CX1) and tie-break key (V1); the card age bound (CX3) | K1 to K7; Y1 to Y6 | `133a715`, `880635d` |
| DM-64, DM-63 | 12 Nov | PR45's profile-suite failure (the scans and the run's clock); C1's rule case and stale texts | T1 to T9; LM1 to LM7 | `25cac30`, `715ef27` |
| DM-65, DM-66 | 12 Nov | Stage A's exact-head review dispositions and C2's scope; C2's stop at a migration time | RV1 to RV10; CK1 to CK7 | `cb13032`, `a53bdb0` |
| DM-67 | 13 Nov | C2's delta re-review dispositions and correction C3's scope | GD1 to GD14 | `e7786bb` |

Labels already used by Dev Manager 4 (avoid them for new conditions): B, E, GD, H, J, K, L, LM, M, P, PR, Q, R, RV, T, U, V, W, X, Y, Z, CK. Free, for example: SC, AA, BB, DD.

## 4. Where things stand

- **The current item: SV3 Stage A** (PR45, full scope), with corrections C1 and C2 verified and integrated (code head `303fdcc`). C2's delta re-review asked for changes, narrowly. **DM-67** (`e7786bb`) approved the dispositions and C3's scope with GD1 to GD14; it has not yet been integrated at the basis.
- **The sequence DM-67 agreed:** the brief's revision 9 with GD1 and GD2 → C3's prompt → C3 and the manager's verification → PR45's run and Codex on C3's head → C3's delta re-review → **your pre-merge read** → the merge.
- **What comes to you next:**
  - **Confirm GD1 to GD12 as applied** at your next consultation or the pre-merge read (GD13 and GD14 are optional). DM-64's T1 to T9 row closes when GD6 lands; DM-63's, DM-65's and DM-66's rows can close (DM-67 section 6).
  - **If C3 stops** (an existing lock refused by the corrected scan, or a pre-probe statement GD1's item 3 list does not name), the stop comes to you. The list must not be widened without a read.
  - **The pre-merge read** (the brief's review plan; DM-67 section 5): at a named commit, the CI policy's Database proof checks paragraph, the data model's and contract's rewritten texts, C3's section as applied, and GD3 to GD12 as applied. DM-64 T9's merge conditions apply to C3's head.
  - **Then:** SV3 Stage B (it takes the carried items under "Carried to SV3 Stage B (DM-66)", and DM-67's N1 and N3 once GD12 lands), OD-64's own brief before P11, and SV4.
- **Facts worth having at hand** (all verified by AST at `3000014`, DM-67 section 3.1): 52 `select_for_update` calls (47 in `services/api`, 5 in the reference design), 5 on `AppAccount` with `no_key=True`, 2 generic helpers (`no_key=model is AppAccount`), none with `of=`; three SQL lock strings outside docstrings, all `FOR SHARE`; `AppAccount`'s only relation field is `auth_user`; no model has `Meta.ordering`.
- **Open and standing conditions:** the review log's "Deferred conditions" holds them all; Dev Manager 3's standing ones (DM-30, DM-36, DM-40 section 7) still stand.

## 5. Working method

Dev Manager 3's section 5 holds. What Dev Manager 4 added:
1. **Export, do not check out.** `git archive <commit> | tar -x -C <scratch>/<id>/rec` into an empty folder in the scratchpad; treat it as untrusted, and read it only with `python3 -I` scripts kept in a separate scratch folder.
2. **Enumerate by AST before judging a rule.** For a lock or scan rule, list every call it would judge (what each passes, what follows it) before saying what a change refuses. Do not import or run the code.
3. **Verify every replace pair before pushing.** One script per report (`applyNN.py`) parses the report's bold labels (`**XX1 (…):**`) and their `> ```` blocks, checks each old passage occurs exactly once at the commit read, applies the pairs in order to copies, and checks hygiene: no model identifier, the last line `Status: complete`, no time placeholder left. Write the finish time last, from `date -u`.
4. **Check deferred rows as applied** with a small script comparing each condition's new words with the tree, normalizing whitespace; explain any difference (a later condition, or an owner direction recorded inside the text).
5. **Never remove files through a shell variable path**; write to a new scratch folder instead.
6. **Notion IDs** (read-only): Implementation Control `3e44590a05eb8118bf02f0dc0c3ea57c`; Dev Manager — reviews and approvals `3e64590a05eb81e29903ca6fccd94268`; the register copy `3e64590a05eb81beaf78d6fa9d64a600`; the Work Register `collection://5ea4c24d-ec63-4afb-a434-8969c26b8fbe` (SQL on `"Work ID"`). The pages are large: save each to a file and parse it. State a match only for the parts read, by name.
7. **The reply** (Nathan's format): the answer first in short bullets; a named state (IN FLIGHT, NOTHING NEEDED or DECISION NEEDED); plain words; last, the relay in a four-backtick block naming the report file, the branch commit and the commit read.

Status: complete
