# DM-100 — SV4 A2's pre-merge read (PR59), with A2-C1's delta review's F1

- **From:** Dev Manager 7, `session_01Q789u3mBCcA1Fu21CMJKbS` ("Glow Dev Manager 7"), on `claude/dev-manager`, 26 November 2026.
- **To:** App Manager 13, through Nathan (OD-25, OD-84).
- **Consultation:** [`docs/ephemeral/2026-11-26-dm-100-sv4-a2-pre-merge-read.md`](../../../ephemeral/2026-11-26-dm-100-sv4-a2-pre-merge-read.md), revision 1, read whole at `92205daeb8a1f5c7f0ab809b2970c46b14614bde` of `claude/magical-wozniak-yfmmx2`. The message Nathan relayed matches the file. `main` is at `43e794a5500e1ffdb12bfb2b2b2c0a9332c45ca2`, the one merge base.
- **Labels:** AL1 to AL8 are conditions, with their words in section 13; AL9 is recommended for the manager workflow's next revision, not for this merge.
- **Environment** (names only): no `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_*`, `RAILWAY_*`, `PG*` or `CLOUDFLARE_*` name. AWS and GitHub token names are present; none was read or used. I called no provider, database, HDE, Railway, Cloudflare or TypeSafe, and wrote nothing to GitHub or Notion.

## 1. Answers

| Item | Verdict | In short |
|---|---|---|
| 1 F1 | **Approved with conditions: (a), carry,** with AL3 to AL6 | The claim is false; I confirmed it in the code. But no decision, acceptance check or the merge reads it, so it is outside D-07's third class. The case fails with the check removed either way (r7). The words make the carried entry and the record true. |
| 2 Revisions 8 to 10 | **Approved** | Each matches what happened, and A2's and A2-C1's diffs stay inside the owned paths. |
| 3 The CI policy | **Approved as written** at `92205da` | Every changed claim holds against the workflow and the proof's code (section 5). No words needed. |
| 4 A2 as settled | **Approved** | Nothing A2 settled that I would not merge. D8, D9, D10 and D15 hold at `ddb1386`; DM-99's decision is built as given. |
| 5 The manager's calls | **Agreed, with one finding and AL7** | The resume message and the dispositions are right. But A2-C1 was 108 changed non-test lines, over the 60 for a delta review, as earlier items counted them. My DM-99 forecast was wrong. The delta review stands for this merge (section 7.3); AL7 corrects the record's count; AL9 defines the count for later. |
| 6 Codex's threads | **Agreed** | Resolve the three after this disposition and before the merge; the code at `ddb1386` answers each. |
| 7 Carried and recorded | **In place, with AL1 to AL3** | F1's entry is still conditional and cites the wrong lines; two groups' line numbers name no commit; the README's case list is recorded but not carried. |
| 8 Records | **Confirmed, with AL8** | AM13-06 to AM13-08, the review log's DM-99 section and the handoff are accurate. AM13-08 should cite PF02-R54, whose "only through" clause is this mistake. |
| 9 Notion | **Four mismatches** | SV4's Evidence; Implementation Control's "Next items" and "Manager" bullets, which DM-98 and DM-99 missed; a commit left out of "Branches". The procedure summary's stamp moves at the merge, as planned. |
| The merge | **Agreed, with one added check** | As proposed, and the merge head's non-Markdown paths equal `ddb1386`'s. |

**Nothing needs Nathan.**

## 2. What I read

- The consultation, whole; the SV4 record's sections "Dev Manager 7's DM-99", "A2-C1" (all subsections), "Manager verification of A2-C1" and "Delta review of A2-C1", whole; the resume message (`f435cef`) and the delta review prompt (`2e075c3`), whole.
- The code, at the merge head: `services/api/glow_chat/route_reads.py` (lines 100 to 195, the list), `contact.py`'s `_revoke_account` (lines 775 to 830), `contract.py`'s `send_error` and `read_error`, `views.py` (lines 114 to 195 and the four views), `glow_discovery/interaction_views.py`'s `MatchListView`, and `chat_cases.py`'s `list_checks` (1172 to 1205), `_while_held`, `_ended_in_locks` and `_account_suspended_as_test_data` (182 to 243).
- A2-C1's whole non-test diff (`4a72036..ddb1386`), and its `chat_support.py`, README and plan-test hunks.
- The CI policy's diff (`43e794a..92205da`), and the workflow's chat job (lines 1450 to 1766) and gate (1767 to 1800); the workflow's whole diff from `main` by its hunks.
- The brief's status line, D11's A2 bullet, D12's "Due at A2", the owned paths of A2 and A2-C1, and its session log.
- The carried-items file's diff from `main`; the P11 plan's lines 91 and 105.
- The mistakes log's AM13-05 to AM13-08; PF02-R54 and R57; the review log's DM-99 section and its DM-100 row; the handoff's diff since `e28a5e2`.
- GitHub (REST `GET` only): PR59, its three review threads and their comments, its reviews and Codex's summary comment, the check runs on `2e075c3` and `92205da`, runs 45807963555, 45807951637 and 45791045751, and the chat and gate job logs of run 45807963555.
- Notion (read only): see section 11 for what I read of each page.

## 3. Item 1: F1

### 3.1 The claim is false

The claim, in the record (lines 1967 and 2077) and in two docstrings of `chat_cases.py`, is that the list's own-account check "is reached only by test data … every writer that takes an account out of `active` also moves its epoch, so the session's check refuses first". I read the code myself:

- `route_reads.py`'s `_list` locks the accounts `FOR SHARE` (lines 136 to 141), then the matches and the session, then checks, in this order: the session's account (157 to 158), the account's presence (159 to 160), **the own account's state (162 to 163)**, then the session's state (164 to 165), expiry (166 to 167) and epoch (168 to 169).
- `contact.py`'s `_revoke_account` (775 on), behind `suspend` and `delete`, locks only the account row, sets its state and moves its epoch. It touches no session row.

So a suspension or deletion that commits after the request has passed SV1's door, and before the list's account lock is granted, is read by the list as `suspended` or `deletion_pending`. The own-account check refuses first, `account_not_active`, which `error_for` serves as `not_found` (404). The epoch check would refuse too, but it comes later. The delta review's probe (404 with the check, 401 without) agrees.

What it changes: nothing about the other member. The refusal is about the member's own account, the list refuses as a whole, and the revocation holds either way. Only the code differs with timing: 401 from the door, or 404 from the list.

### 3.2 The class under D-07

D-07 (the workflow's step 6) commissions a correction only for "a false claim that a decision or the merge would rest on", and carries "a record's wording that misleads no decision". The delta review prompt drew its third class within D-07 this time, with the qualifier "where that claim is what a decision, an acceptance check or the merge reads". So the question is only whether anything reads the claim.

- **The acceptance check** for A2R-3 is that each of the list's three checks, removed, fails a database case. Reversal r7 shows that, whoever else reaches the check.
- **The merge** rests on the run, the reviews and this read, not on who reaches the check.
- **The resume message's decision 2** set the expectation to `not_found` because "the list refuses `account_not_active` through `error_for`, as A1's reads do, and item 4 named no code for that check". The false claim came after, as a thing to record. It is the source of the claim (AM13-08), not its basis.
- **The contract:** the route contract's list bullet names no refusal code beyond the routes' common ones, so no contract sentence rests on it.
- **A later decision** could read it: for example a change to the list's checks, or AC3 deciding how the client handles a 404 from the list. That reader goes to the carried-items file and the record. AL3 makes the entry state the truth, and AL4 and AL5 mark the record's two sentences. With those, the wording misleads no decision.

So the manager's reading is right, and the reviewer's class 3 does not apply. This is DM-98's reading for E-1 again: the merge rests on the test, not on the docstring.

### 3.3 Why carry, and not A2-C2

A2-C2 would change two test docstrings, then need a run, Codex and a delta review. It would correct nothing that behaves wrongly, and the carried entry already reaches the next change to `chat_cases.py`. The words that matter before the merge are Markdown in the manager's files: AL3 (the entry), AL4 and AL5 (the record's sentences), AL6 (the record's citation). Until now the record has put in-place notes only in the manager's own sections (lines 406 and 1324), and has left a session's text as written. AL4 and AL5 keep the session's words and add a marked note after each, because those two sentences are where a later reader looks for the check's reach.

### 3.4 A citation slip

The consultation, the record's F1 row (line 2117) and the carried entry cite `chat_cases.py` "lines 179 to 181" for `list_checks`. The docstring's claim is at **1179 to 1181**; 179 to 181 is in `_waiting_on` and `_while_held`. AL3 and AL6 correct it. No decision rested on it.

## 4. Item 2: the brief's revisions 8 to 10

Approved. I checked each against the status line and the session log:
- **Revision 8** completes A2's owned paths (the fifth suite's modules, the README, the CI policy's database-jobs paragraph, the contract's corpus and tests, the API's tests). It adds D11's A2 bullet and D12's "Due at A2", and changes no design.
- **Revision 9** adds SV3's case `match.no_route_creates_a_match` and the CI policy's lines 5 and 23 (at `main`'s numbering) after A2's stop, with AM13-04.
- **Revision 10** applies AK8 to D8 as given (my script finds it once, the old passage gone) and adds A2-C1's owned paths.

A2-C1's diff (`4a72036..ddb1386`) has nine paths, each inside revision 10's list: `chat_support.py` changes `match_version` only; the README changes the count only; `test_chat_offline.py` changes the count's pin and the plan tests only; `route_reads.py`, `contact.py`, `reads.py` and `glow_domain/` are unchanged. The resume message's change to `transactions.non_atomic_requests` is inside `chat_cases.py`, which revision 10 owns whole.

## 5. Item 3: the CI policy's change (governing Markdown)

`git diff --name-only 43e794a 92205da` over the governing paths prints only `docs/operations/ci-and-branch-policy.md`. Its diff is four lines, as the consultation says. I checked every claim against `.github/workflows/foundation.yml` and the proof's code at `92205da`:

| Line | Claim | Where it holds |
|---|---|---|
| 5 | The jobs list gains "Database proof checks (chat)"; "all ten application jobs" | The job `database-chat` (line 1450), named so; the gate's `needs` (line 1770) and its `jobs` tuple list ten application jobs |
| 13 | `glow_chat_proof`, owned by a non-superuser role, with its own marker | The credentials step writes `CREATE ROLE glow_proof … NOSUPERUSER …`, `CREATE DATABASE glow_chat_proof OWNER glow_proof` and its comment |
| 13 | `dbshell` refused under the chat settings | The step at line 1577 fails unless the exit status is non-zero and `RefusedDatabase: refusing dbshell` appears |
| 13 | The decoy `glow_discovery_proof`, its own marker, refused; relation counts unchanged; no table | The step at line 1604: the decoy and distinct-comment checks, the per-schema counts before and after, zero relations outside the catalog schemas, no `django_migrations` |
| 13 | Migrations from zero; `makemigrations --check --dry-run` | The same step's last two commands |
| 13 | 205 members seeded for the list's bounded locks | `chat_cases.py`, `POPULATION = 205` (line 954) |
| 13 | `chat_scan` checks the output and the JSON before the output is shown; counts only on failure | The suite step: `chat_scan` runs first; the log is printed only on `scan=passed`; otherwise counts only |
| 13 | A second run refused with the row counts unchanged | The step at line 1711 compares six counts before and after |
| 13 | `sv4-chat-results` for 14 days, only after the check passed | `if: ${{ always() && steps.chat.outputs.scan == 'passed' }}`, `retention-days: 14` |
| 13 | The run of record states the chat phase's duration | The step prints "chat phase: … s" |
| 15 | The chat job's secret check reads every secret file its job writes, and no other | `chat_scan.py`'s `VALUE_FILES`, `PASSFILE` and `KEY_FILES` are the files the credentials step writes and keeps |
| 15 | Five suites record row locks; the chat suite's results JSON carries the counts | `chat_suite.py` installs `row_locks` and writes `report.row_locks` (lines 100 to 102 and 160) |
| 24 | upload-artifact used by Mobile checks and the five database proof jobs | Lines 139, 470, 790, 1108, 1427 and 1744 |

The workflow's diff from `main` is +319 −1: the chat job, and the gate's `needs` line and `jobs` tuple. Because PR59 changes the workflow, I also classified it myself with `main`'s policy (`"full": true`, reason `behavior-or-empty`) and read the actual results at the current head: PR run 45807963555 passed all twelve jobs, and its chat job shows `Ran 421 tests … OK`, `chat dbshell exit status: 1`, the decoy's marker refused (`exit status 1`), `[chat] cases: 18/18 passed in 93.9 s`, both scans clean, `ROW LOCKS (D14): PASS`, `CHAT VERDICT: PASS` and `second chat run exit status: 1`. The gate prints "Application checks passed".

## 6. Item 4: A2 as settled

Approved. Beyond the reviews, I checked at the merge head:
- **D8, the one code:** `send_error` answers `SEND_STOPPED` for every stopped cause, `stale_contact_version` and the four in-lock session reasons. `read_error(..., conversation=True)` answers `not_found` for the same four, and only `HistoryView` and `ReadCursorView` pass it. `session_missing`, `accountsession_missing`, the door and the list keep 401, as DM-99 decided.
- **A2R-4:** the four chat views share `_ChatRoute`, with `JsonOnlyNegotiation` and `renderer_classes = [JSONRenderer]`. `MatchListView` declares the same.
- **DM-99's words:** AK3 to AK10 each occur once at `92205da`, each old passage gone (a script on DM-99's section 9).
- **The seal:** `glow_api/` names no `glow_chat` module, no `interaction_urls` and no `GLOW_CHAT_TEXT_READER`; `openapi.json`'s `paths` is `{}`.
- **The protected paths:** `contact.py`, `reads.py`, `glow_domain/`, `glow_identity/` and `glow_profiles/` are unchanged from `main` to `ddb1386`, and `route_reads.py` from `26aa7ca`. No commit after `ddb1386` touches a non-Markdown path. The new lines that name `DATABASE_URL` or `HD_API_KEY` are refusal tests and the workflow's forbidden-word checks.

## 7. Item 5: the manager's calls since DM-99

### 7.1 The resume message

Agreed. Changing `transactions.non_atomic_requests` to build its send's body before `ATOMIC_REQUESTS` is a test change in an owned file. It keeps every expectation and decides no design, so it needed no consultation first; listing it for this read was right. Setting the list case's own-account expectation to `not_found` matches the code, which A2-C1 did not change: `account_not_active` goes through `error_for`, as in A1's reads. DM-99's "the list … keep[s] `unauthenticated`" was about the session's reasons, not this one. The defect was the recording instruction, which AM13-08 logs.

### 7.2 The delta review's dispositions

Agreed:
- **F2:** carried; the reach of a static test.
- **F4:** carried; the pinned plan holds the order, and `test_the_cases_that_publish_hidden_run_last` pins it.
- **F6:** carried; a risk to a future route, with both routes that exist pinned.
- **F3 and F5:** recorded; a citation, and no assertion left unproven.

### 7.3 The review's size: A2-C1 was over 60 non-test lines

Step 6 gives a delta review to "a correction of 60 or fewer non-test lines that answers a review finding"; "a larger correction … still gets a full exact-head review". The rule does not say how lines are counted. Earlier items counted every changed line in non-test files, added and removed, docstrings included (DM-48 counted "a docstring"; P06.2-F's C5 counted "48 changed non-test lines" as +44 and −4).

By a numstat of `4a72036..ddb1386`, A2-C1's three modules changed **108 lines (+94 −14)**. An `ast` and `tokenize` split gives: added, 44 code, 40 docstring and 10 blank; removed, 6 code, 6 docstring and 2 comment. That is 50 changed code lines.

- **My mistake:** DM-99 said "the correction stays well under 60 non-test lines" before the code existed. On the count earlier items used, that was wrong. I should have made the confirmation depend on the count at the code head.
- **The manager's:** the verification counted code lines only ("44 code lines") and wrote "so the code stays under the 60 lines DM-99 relied on". DM-99 relied on non-test lines, so the sentence moves the measure without saying so. AL7 corrects it. Whether to log it is the manager's call; if it does, the workflow's "Copy a source's qualifiers in its own words" is the rule.

**My ruling: the delta review stands for this merge.** The rule does not decide the count, so it falls to me under step 6. A full exact-head review would add only a second reading of paths that have not changed:
- the delta review read every path A2-C1 touches, whole, at its head, with the security focus, and ran the reversals and the chat suite;
- the excess is docstrings and blank lines in those same paths, and the review read them: it checked AK7's docstring words by script and found F6 in `read_error` itself;
- every other non-Markdown path in PR59 is byte-equal to what A2's exact-head review read at `26aa7ca`: `git diff --name-only 26aa7ca ddb1386` lists only A2-C1's seven code and test paths besides Markdown, and the protected paths are unchanged since `main`;
- Codex completed on the final head with no findings.

The workflow should define the count, so that the next case does not depend on a forecast: **AL9** (section 13), for its next revision. That is governing Markdown, so it comes to me before it merges. AL9 counts docstrings, which is S2's plain words. A count of code lines only would narrow OD-53, and that change would be Nathan's.

## 8. Item 6: Codex's three threads

Agreed. Read at the current head:

| Comment | Raised on | Outdated | Resolved | Its point | Answered by |
|---|---|---|---|---|---|
| 4658183908 | `81d390c`, `contract.py` | yes | no | A stale version tells a suspension from a pause (A2R-1) | `send_error`: `stale_contact_version` is `not_found` |
| 4703261810 | `e28a5e2`, `contract.py` | yes | no | A session ended inside the send splits causes (A2R-2) | `send_error`: the four in-lock session reasons are `not_found` |
| 4704969737 | `f435cef`, `views.py` (now line 192) | no | no | Negotiation failures escape the contract's `Error` (A2R-4) | `JsonOnlyNegotiation` (`views.py`, lines 114 to 131) and `MatchListView`'s copy |

The third thread is not outdated only because its line, `return super().handle_exception(exc)`, still exists. Its point is answered elsewhere in the file, and the offline test `test_the_negotiation_reads_neither_accept_nor_format` pins the answer. Codex completed on `92205da` at 11:11:26 UTC with no findings, after the consultation was written.

## 9. Item 7: carried and recorded

The entries from A2's exact-head review, from DM-99 (P10, P08.2, AC3) and from the delta review are each in the right section, and AK9 and AK10 stand as given. Three fixes, in AL1 to AL3:
- **F1's entry** still reads "if DM-100 carries it" and cites the wrong lines (section 3.4). AL3 makes it definite and states what the code does.
- **The line numbers** in A2's exact-head review group are as at `26aa7ca`, and A2-C1 moved some: `chat_cases.py` (A2R-6), `test_chat_offline.py` (A2R-7) and `views.py` (A2R-11; `_refused` is now lines 171 to 179). The delta review group's are as at `ddb1386`. Neither group names its commit. AL1 and AL2 name them.
- **The proof README's case list:** it says 18 cases but describes the fifteen A2 built. The record lists this under A2-C1's limits, but no entry tells the README's next change. AL3 adds it.

The P11 plan's line 105 (the list's locks) is stale since A2 bounded the list. Correcting it at the merge receipt, as A2R-13 says, is right, because the line should then name the merge.

## 10. Item 8: records since DM-99

Confirmed against the repository and the live branches:
- **AM13-06, AM13-07 and AM13-08** state what happened.
- **The review log's DM-99 section** matches my report's verdicts.
- **The handoff** names five remote branches. `git ls-remote` shows the same five at the same commits: `main` `43e794a`, the manager branch `92205da`, `claude/dev-manager` `c2ae138`, `claude/affectionate-sagan-r916ba` `2201c2d` and `claude/dazzling-hamilton-ocxuu3` `88d4ef3`.

One fix, AL8: AM13-08 cites PF02-R57 ("write an ID or a result only after reading it"). The rule this mistake breaks is PF02-R54: "A residual said to be reachable 'only through' one route is tested against every input that reaches the check", in a rule whose title is "A session's claim stays the session's until checked". The claim was the session's, and the manager repeated it without the test. R57 can stay beside it.

## 11. Item 9: Notion

What I read: Implementation Control (last edited 11:09:35 UTC on 26 November), saved and parsed with `python3 -I`. I read its status heading, the opening of its status paragraph, the list of its standing bullets, and the "Next items" (its SV4 part), "Dev Manager", "Manager", "Main", "Branches" (its first 3,000 characters), "Mistakes log" (its first 2,500) and "Routing" bullets, and the procedure summary (lines 111 to 124). I did not read the page's history paragraphs. The Dev Manager page (11:09:54 UTC): its header, Dev Manager 7's session row, and the DM-99 and DM-100 rows. The register copy: all 84 rows, compared by script with the repository's. The Work Register's SV4 row: whole.

Matching at `92205da`:
- the status heading and its "matched at `92205da`";
- "Dev Manager" (DM-100 with it; labels from AL);
- "Main" (PR59 at `92205da`; the three threads, each on its own commit);
- "Mistakes log" (to AM13-08);
- the Dev Manager page's rows (DM-100 awaited);
- the register copy: OD-01 to OD-84, differing from the repository only in link text, in eight rows;
- SV4's "Next Action".

Mismatches:
1. **SV4's Evidence** still has its links pinned at `4a72036`, and lists the record's sections only as far as "Dev Manager 7's DM-99". It lacks the record at `92205da` ("A2-C1", "Manager verification of A2-C1", "Delta review of A2-C1"), the resume message (`f435cef`), the delta review prompt (`2e075c3`) and DM-100's consultation (`92205da`). DM-98 found the same row stale.
2. **"Next items"** still says that A1 "is built, verified and in PR58; its exact-head review asked for changes … and App Manager 13 regenerates A1-C1's prompt (OD-83)". Words for it: "A1 merged with PR58 at `43e794a` on 22 November 2026, with its corrections A1-C1 and A1-C2 (DM-98); A2, with its correction A2-C1, is in PR59." This was already stale at DM-98's and DM-99's reads, and both missed it.
3. **"Manager"** says App Manager 13 holds the manager branch as "the head of PR58, SV4 A1". Words for it: "the head of PR59, SV4 A2 (PR58, SV4 A1, merged at `43e794a` on 22 November 2026)". The same bullet says App Manager 13 "records its session ID", but no record I read gives it; add it, or drop the clause. DM-99 missed the PR58 clause.
4. **"Branches"** lists the manager branch's commits since PR59 opened but leaves out `15a5646` (DM-99's merge), though it names `356ee8f` (A2-C1's). A small thing.

As planned (DM-99, item 6), the procedure summary's stamp (`e8d8c44`) moves at the merge, now that this read covers the CI policy's change. The summary's own text states no job count, so nothing else in it changes.

## 12. The merge

Agreed as proposed: this read disposed; AL1 to AL8 applied as given, Markdown only; that head's PR run passes all twelve jobs with "Application checks passed"; Codex completes on it; the three threads resolved; PR59's checklist filled. Add one check: `git diff --name-only ddb1386 <merge head>` lists only Markdown files, so that the code merged is the code reviewed. The Notion fixes in section 11 go in that batch's sync. Then the receipt (with the P11 plan's line 105), the branch cleanup and Stage B.

A further non-Markdown change before the merge needs its own review and another read.

## 13. The words

Each old passage occurs exactly once at `92205da`, checked by script; each new passage then occurs once.

**AL1** — `docs/planning/carried-to-later-items.md` (A2's exact-head review group: name the commit its lines are at):

> ```
> (A2-C1 takes A2R-1 to A2R-5 and A2R-8, DM-99's AK11):
> ```
> ```
> (A2-C1 takes A2R-1 to A2R-5 and A2R-8, DM-99's AK11; the lines below are as at A2's code head `26aa7ca`, which the review read):
> ```

**AL2** — `docs/planning/carried-to-later-items.md` (A2-C1's delta review group: name the commit its lines are at):

> ```
> - **From A2-C1's delta review (the SV4 record, "Delta review of A2-C1"), for SV4 Stage B if it changes the file, otherwise the next change to it:**
> ```
> ```
> - **From A2-C1's delta review (the SV4 record, "Delta review of A2-C1"), for SV4 Stage B if it changes the file, otherwise the next change to it** (the lines below are as at A2-C1's code head `ddb1386`):
> ```

**AL3** — `docs/planning/carried-to-later-items.md` (F1 carried, its lines right; the README's case list carried):

> ```
>   - **F1, if DM-100 carries it** (`chat_cases.py`, lines 179 to 181 and 231 to 232): the two docstrings that say the list's own-account check is reached only by test data; a suspension or deletion committing while the list waits at its account lock reaches it too.
> ```
> ```
>   - **F1, carried by DM-100 (item 1)** (`chat_cases.py`, lines 1179 to 1181, `list_checks`, and 231 to 232, `_account_suspended_as_test_data`): the two docstrings that say the list's own-account check is reached only by test data, because a suspension also moves the epoch and the session's check refuses first. The list checks its own account before the session's state, expiry and epoch (`route_reads.py`, lines 162 to 169), so a suspension or a deletion that commits after the request has passed SV1's door, and before the list's account lock is granted, reaches the check too, and the list answers `not_found` (404). The record's section "A2-C1" (item 4 and "Limits and deviations") carries the same claim, marked there.
>   - **The proof README's case list** (A2-C1's own limit, the record's "A2-C1", "Limits and deviations"; `proofs/postgres-ordering/README.md`, its "SV4 A2" paragraph): it gives the chat suite's count as 18 but describes the fifteen cases A2 built; A2-C1's three (`send.one_answer_for_every_version_and_session`, `list.block_session_and_own_account_checks` and `reads.session_ended_in_locks_answers_as_hidden`) are described in the record only.
> ```

**AL4** — `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md` (section "A2-C1", item 4: mark the false sentence):

> ```
> **That last check is reached only by test data, inside a race with SV1's door:** every writer that takes an account out of `active` (`glow_chat`'s suspension and deletion) also moves its epoch, so the session's check refuses first.
> ```
> ```
> **That last check is reached only by test data, inside a race with SV1's door:** every writer that takes an account out of `active` (`glow_chat`'s suspension and deletion) also moves its epoch, so the session's check refuses first. (False, as A2-C1's delta review found, F1: the list checks its own account before the session's state, expiry and epoch, so a real suspension or deletion that commits after the request has passed SV1's door, and before the list's account lock is granted, reaches this check too. The corrected statement is in "Delta review of A2-C1"; DM-100 carried the docstrings.)
> ```

**AL5** — `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md` (section "A2-C1", "Limits and deviations"):

> ```
> - **The own-account check is reached only by test data** inside a race with SV1's door (item 4).
> ```
> ```
> - **The own-account check is reached only by test data** inside a race with SV1's door (item 4). (False: a real suspension or deletion that commits in the same race reaches it too; A2-C1's delta review, F1, and DM-100.)
> ```

**AL6** — `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md` (the delta review's F1 row: the line citation):

> ```
> `chat_cases.py` 179 to 181 and 231 to 232
> ```
> ```
> `chat_cases.py` 1179 to 1181 and 231 to 232 (the first range first given as 179 to 181; DM-100)
> ```

**AL7** — `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md` ("Manager verification of A2-C1": the count):

> ```
> By a count of the added lines, the three modules gain 44 code lines and 50 docstring or blank lines and lose 14, so the code stays under the 60 lines DM-99 relied on in confirming a delta review.
> ```
> ```
> By a count of the changed lines, the three modules gain 44 code lines and 50 docstring or blank lines and lose 14 (6 of them code): 108 changed non-test lines, over the 60 of the workflow's step 6 as earlier items counted them (added and removed, docstrings included; DM-48, P06.2-F's C5), and 50 changed code lines. DM-99 had forecast "well under 60 non-test lines" before the code existed. DM-100 (item 5) let the delta review stand: it read every path the correction touches whole at its head, and every other path is as A2's exact-head review read it.
> ```

**AL8** — `docs/continuity/manager-mistakes.md` (AM13-08: the rule it breaks):

> ```
> Breaks PF02-R57 (write a result only after reading it)
> ```
> ```
> Breaks PF02-R54 (a session's claim stays the session's until checked: a residual said to be reachable "only through" one route is tested against every input that reaches the check) and PF02-R57 (write a result only after reading it)
> ```

**AL9 (recommended, for the manager workflow's next revision; not for this merge).** In step 6's bullet "A small correction gets a delta re-review", after its first sentence ("A correction of 60 or fewer non-test lines that answers a review finding is re-reviewed by a delta review, not by a new full exact-head review."), add:

> "Its non-test lines are the lines it adds and removes, as `git diff --numstat` counts them from the commit its prompt names to its code head, in every file but tests (the proof's suites and cases among them) and Markdown; docstrings and comments count. A brief or a Dev Manager read that confirms a delta review before the code exists makes it conditional on that count."

## 14. Checks

- `git fetch`; `git ls-remote origin`: five branches, as in section 10.
- `git merge-base --all 43e794a 92205da`: one base, `43e794a`.
- `main`'s `scripts/change_scope.py` (SHA-256 `b564c62f4a076f51…`, equal to `git show 43e794a:scripts/change_scope.py`), extracted to the scratchpad, `python3 -I … --base 43e794a5500e1ffdb12bfb2b2b2c0a9332c45ca2 --head 92205daeb8a1f5c7f0ab809b2970c46b14614bde --merge-base`: `"full": true`, `behavior-or-empty`, 57 paths.
- `git diff --name-only ddb1386 92205da`: Markdown only. `git diff --stat` of the protected paths from `main` to `ddb1386`, and of `route_reads.py` from `26aa7ca`: empty. `git diff --numstat 26aa7ca 4a72036` over `services`, `proofs`, `apps`, `packages`, `.github` and `scripts`: empty.
- `git diff --numstat 4a72036 ddb1386` of the three modules: 52/11, 24/3, 18/0. My `ast` and `tokenize` script split the changed lines as in section 7.3.
- A script read DM-99's section 9 and found AK3 to AK10 once each at `92205da`, each old passage gone.
- A script found each of AL1 to AL8's old passages exactly once in its file at `92205da`, applied the eight pairs to copies, and found each new passage once.
- GitHub, REST `GET` only: as in section 2. Notion, read only: as in section 11.

Status: complete
