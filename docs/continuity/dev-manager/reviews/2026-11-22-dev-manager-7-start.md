# Dev Manager 7: start note

- **Session:** `session_01Q789u3mBCcA1Fu21CMJKbS`, titled "Glow Dev Manager 7", created on 22 November 2026 at 07:50:00 UTC in environment `env_01GAnJ5Rdi5k1wGvGUxJuDbe` (`Glow App - No Stream`, OD-36), permission mode auto, tag `glow-dev-manager`, source and outcome branch `claude/dev-manager`. Parent session `session_01Q789u2AYaBgUF8gPDLeJmV` (Dev Manager 6). All of this is as `get_session` reports.
  - **The model:** `get_session` reports the configured model. This file carries no model identifier; the relay reply may.
- **Direction:** Nathan Amthor, 22 November 2026, in Dev Manager 6's session: *"create a new version of yourself, Glow Dev Manager 7"* (Dev Manager 6's handover). The OD-35 pattern applies. The primary manager records it in the register; at `4618859` no row does (section 4).
- **Started from:**
  - this branch, `claude/dev-manager`, at `7b2c92810cac8fe9a1ec349c80b386d5a7efc09c`, Dev Manager 6's handover commit;
  - the manager branch `claude/magical-wozniak-yfmmx2` at `461885966d7de15fe513db428467305f4037ffc7`, the handover's basis and still the live head (PR58's head);
  - `main` at `499ccbbec758ed4ef34a93ad19fa8df454fb095c` (PR57), the handover's basis.
- **Written:** 22 November 2026, between about 07:50 and 08:10 UTC.
- **What this is:** the first deliverable of the start prompt. It answers no consultation. The next (DM-98, if the numbering continues) is expected to be SV4 A1's pre-merge read, from App Manager 13 through Nathan.

## 1. Environment check (names only)

| Command | Result |
|---|---|
| `for n in DATABASE_URL HD_API_KEY GEO_API_KEY STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n+x}" ] && echo "$n present"; done` | Nothing printed for these six, as expected for `Glow App - No Stream` (OD-36) |
| The same loop over `AWS_ACCESS_KEY_ID AWS_CA_BUNDLE AWS_SECRET_ACCESS_KEY` | All three present, as Dev Managers 4 to 6 recorded and OD-76 explains (set by the cloud container) |

- Names only. I did not read, print or use any value, and nothing I do needs them. Any command against the repository's code runs under `env -i` without them.
- I did not dump the environment, and checked no other name.

## 2. Start gate

| Command | Result |
|---|---|
| `git fetch origin claude/dev-manager claude/magical-wozniak-yfmmx2 main` | Fetched; `claude/dev-manager` moved `7383e22..7b2c928` in the local clone |
| `git switch claude/dev-manager` | Already on it, but **3 commits behind** `origin/claude/dev-manager` (the clone was made at `7383e22`); `git merge --ff-only origin/claude/dev-manager` brought it to the remote head. No local change was lost: the worktree was clean |
| `git rev-parse HEAD` | `7b2c92810cac8fe9a1ec349c80b386d5a7efc09c`, the handover commit, as the start prompt expects |
| `git merge-base --is-ancestor 7b2c928… HEAD && echo "handover present"` | `handover present` |
| `git rev-parse origin/claude/magical-wozniak-yfmmx2 origin/main` | `4618859…` / `499ccbb…`, both equal to the handover's basis |
| `git ls-remote origin` (07:51 UTC) | Four branches: `main` `499ccbb`; `claude/dev-manager` `7b2c928`; the manager branch `4618859`; A1's `claude/sleepy-mendel-0kqgw9` `a1651fb`. Dev Manager 6 pushed nothing after its handover commit |
| `gh api repos/amthorn78/glow-dating-app/pulls/58` and the open-PR list (07:53 UTC, REST, read only) | One open PR: PR58, open, not a draft, head `4618859`, base `main` |

**Since my predecessor's last read** (DM-97 read `fc9decd`; the handover's basis `4618859`), the manager branch moved from `499ccbb` through ten commits (`1fd59a2` to `4618859`): PR57's receipt, A1's prompts (revisions 1 and 2), A1's code `bc0675d` and record `a1651fb`, the manager's verification, PR58, the exact-head review and its disposition, A1-C1's prompt (revision 1) and the handover to App Manager 13.

**Governing Markdown since `main`:** none. `git diff --name-only 499ccbb 4618859` names no `AGENTS.md` or `CLAUDE.md`, nothing under `docs/pf-canon/`, and not the manager workflow, the charter or the CI policy. One start prompt changed, `docs/planning/start-prompts/next-manager.md`, by one history line (App Manager 13's creation); it is not in the charter's governing list. The trusted classifier (`main`'s `scripts/change_scope.py`, sha256 beginning `b564c62f4a076f51`, unchanged from Dev Manager 6's reading, extracted outside the tree and run with `python3 -I --merge-base` and full SHAs from `499ccbb` to `4618859`) prints `"full": true`, reason `behavior-or-empty`, as PR58 should; `git merge-base --all` gives one base, `499ccbb`. No non-Markdown path changed after the code head `bc0675d`.

## 3. What I read

The manager's records at `4618859`, exported with `git archive` into the scratchpad.

1. **The handover** (`2026-11-22-dev-manager-6-handover.md`), whole; Dev Manager 6's start note, whole, as this note's model. **Not** re-read: Dev Manager 3's, 4's and 5's handovers, whose sections 1, 2 and 5 the handover cites; I rely on its summary.
2. **Root `AGENTS.md` and `CLAUDE.md`** at `4618859`, whole. This branch's copies are older; the manager branch's govern. **The charter**, whole.
3. **The review log** at `4618859`: the Sessions table; the Consultations rows DM-95 to DM-97; the "Deferred conditions" rows marked Open and those naming SV4 or DM-94 to DM-97; the DM-96 and DM-97 dispositions. **Not** every earlier row or disposition body.
4. **The manager's records:**
   - the register, OD-01 to OD-83, every row;
   - the current handoff, whole;
   - the manager workflow, whole;
   - the CI policy, whole;
   - the mistakes log: its headings and the summary rows AM12-40 to AM12-49. **Not** every earlier section's body.
5. **The current item:**
   - SV4's brief, revision 6, whole;
   - its evidence record: section A1 whole (the session's report, the manager's verification, the exact-head review with its findings AR-1 to AR-16 and the disposition); A0's sections by heading only;
   - DM-96's and DM-97's verdicts, as the review log and the handover give them, **not** the reports' bodies.
6. **The P11 plan:** its SV4 lines (the block's direction; the history policy; the epoch revocation's revisit). The carried-items file's "Carried to SV4". **Not** either file whole.
7. **Notion, read-only, 07:50 to 08:00 UTC** (section 4).

**Not read or done:** application code; CI logs; A1-C1's withdrawn prompt; PF00, PF01, PF02. Nothing ran against the application; no provider, database, HDE, Railway, Cloudflare or TypeSafe service was called. GitHub was read only, with `gh api` REST.

## 4. The state as I found it

- **The current item is SV4 Stage A, at A1** (the rules; code head `bc0675d`; PR58 open, head `4618859`). Its exact-head review asked for changes: AR-1 blocking, AR-2 and AR-3 should fix, all three taken by correction A1-C1 (tests and docstrings); AR-4 and the nits carried or recorded. The waiting checkpoint: App Manager 13 regenerates A1-C1's prompt as revision 2, then C1, its verification, PR58's run and Codex, C1's delta review, then **A1's pre-merge read, which comes to me.**
- **What that read must cover** (the brief's status line; the handover, section 4): the brief's revisions 4, 5 and 6 (the manager's: A1's owned paths widened and D11's earlier tests); C1 against AR-1 to AR-3, and whether a correction was right under D-07 for each; any governing Markdown changed after `499ccbb` (none at `4618859`); A1's deviation (two README bullets beside the owned line, accepted by the manager); the lines outside A1's paths carried; the review's deviation (`gh api` reads, accepted); Notion.
- **A first view, before the read, not a verdict.** AR-1 meets D-07 as the manager says: a test that fails on `main`'s first push run after the merge turns CI red, which OD-21 makes part of the current item, and the record's limit claimed less than the test does. AR-3 is the stronger of the two docstring findings: it is a false claim at the who-may-read boundary that A2 and P11 wire against. AR-2 rests on D6's acceptance check being read through the detector; I will check that reading at the read.
- **One point for App Manager 13, from evidence, on the GitHub tools.** OD-83 and AM12-49 record the GitHub MCP tools' retirement as local to App Manager 12's session (Nathan: *"this github issue is session local"*). It was not only there: Dev Manager 6's session lost them on 22 November (its handover, section 2), A1's exact-head review session lost them during its run (the SV4 record, "Its deviation"), and this session has none, its system instruction saying the built-in GitHub server *"has been retired for this organization"* and naming `gh api` REST as the route. So a prompt that relies on the GitHub tools being present may meet a session without them. The wording that holds either way is the one my own start prompt uses: *the GitHub tools if your session has them; otherwise `gh api` (REST, read only)*. Nathan's words stand as his; this is a point of prompt wording for the manager, not a decision for him, and I raise it now because A1-C1's revision 2 is being written now. If App Manager 13 wants a ruling, it is a consultation.
- **The succession is not yet recorded:** the register (OD-83 is the last row), the review log's Sessions table, the handoff and Implementation Control name Dev Manager 6. Expected until App Manager 13's next batch; not a mismatch.

### Notion

Each large page saved to a file and parsed with `python3 -I`; a match is stated only for the parts named. The repository wins on any difference (OD-27).

| Page | What I compared | Result |
|---|---|---|
| Implementation Control (`3e44590a05eb8118bf02f0dc0c3ea57c`, last edited 07:49:19 UTC) | The status heading and its stamp | "Last matched to … `4618859`: Handover to App Manager 13 (OD-83); A1-C1's prompt, revision 1, withdrawn", with the A1 review summary as the record has it. **Match** |
| Implementation Control | "Dev Manager" | Names Dev Manager 6, DM-97 answered. True until the succession is recorded; **not a mismatch** |
| Implementation Control | "Branches" | Four branches at 07:49 UTC, the manager branch at `4618859`. **Match** with `git ls-remote` |
| Implementation Control | "Mistakes log" | AM12-01 to AM12-49 at `4618859`. **Match** |
| Implementation Control | **"Main"** | **Mismatch.** It reads "`Main` is `c2cffbe` (PR56 …)" and ends "Open pull requests: none." At `4618859`, `main` is `499ccbb` (PR57, merged 20 November) and PR58 is open; `499ccbb` does not occur in that bullet. The status log above it records PR57's merge, so only this standing bullet was not moved, through every batch since PR57's receipt. For App Manager 13's next batch: `main` at `499ccbb` (PR57: SV4 A0 with C1, C2 and DM-97), and PR58 open |
| Dev Manager — reviews and approvals (`3e64590a05eb81e29903ca6fccd94268`, last edited 20 November 01:41 UTC) | The Sessions rows; the DM-97 row | Dev Manager 6's row and DM-97's (answered at `b505a8e`, a read of `fc9decd`) as the review log has them; no DM-98 row. **Match** |
| Register copy (`3e64590a05eb81beaf78d6fa9d64a600`, last edited 07:50:15 UTC) | Its stamp; its rows against `owner-directions.md` at `4618859` | Stamped "Matched … at `4618859` … (OD-83 added)". 83 rows each, OD-01 to OD-83; after normalizing links, markup and code spans, every row's quoted words are equal. **Match** for the quotes; I did not compare every row's whole text |
| Work Register `SV4` (SQL on `"Work ID"`) | Next Action, Owner Role, Evidence, State | State "In progress"; Owner Role names App Manager 13; Next Action matches the handoff's next actions and the record (A1-C1 revision 1 withdrawn, AM12-49). **Match.** One nit, not a mismatch: Evidence links A1-C1's prompt at `998116b` without saying it is withdrawn; Next Action says so |

## 5. What I will do

Wait. The next consultation comes through Nathan. I answer each as the start prompt and the handover's section 5 say: a names-only check; a read at the exact commit named, and the governing diff since `4618859`, the last commit I listed; the code each claim rests on, read without importing it; every cross-reference checked against the current numbering; Notion; one report file, ending `Status: complete`, committed alone and pushed. Labels used so far run through AH; new conditions start at AJ.

Status: complete
