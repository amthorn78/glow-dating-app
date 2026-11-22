# Dev Manager 6 → Dev Manager 7: handover

- **Direction:** Nathan Amthor, 22 November 2026, in Dev Manager 6's session: *"create a new version of yourself, Glow Dev Manager 7"*. Under OD-35, the outgoing Dev Manager runs its handover and creates its successor with the remote-session tools. The primary manager records the direction in the register.
- **Written by:** Dev Manager 6, `session_01Q789u2AYaBgUF8gPDLeJmV` ("Glow Dev Manager 6"), branch `claude/dev-manager`, environment `Glow App - No Stream`.
- **Basis:**
  - the manager branch `claude/magical-wozniak-yfmmx2` at `4618859` ("Handover to App Manager 13 (OD-83); A1-C1's prompt, revision 1, withdrawn");
  - `main` at `499ccbb` (PR57: SV4 A0, its corrections C1 and C2, and DM-97);
  - this branch at `b505a8e` (DM-97's report), plus this file.
- **What this is:** what the successor needs beyond the charter, the start prompt, the review log and the reports. Dev Manager 6 pushes nothing after this file's commit.

## 1. The role

The charter (`docs/planning/dev-manager.md`) and the start prompt (`docs/planning/start-prompts/dev-manager.md`) hold. So do the earlier handovers' sections 1, 2 and 5: Dev Manager 3's (`2026-11-08-dev-manager-3-handover.md`), Dev Manager 4's (`2026-11-13-dev-manager-4-handover.md`) and Dev Manager 5's (`2026-11-19-dev-manager-5-handover.md`). In short:

- **What it does:** Nathan's second layer of oversight (OD-15). It reviews, challenges and approves consequential decisions, and gives exact words for every text it conditions (AM9-08).
- **D-07 (OD-75):** two Dev Manager reads per code item: the brief, and the pre-merge read. A correction pass happens only for a defect in application behaviour, at a security boundary, or for a false claim. Applying the Dev Manager's own words needs no new read.
- **Where it writes:** only report files under `docs/continuity/dev-manager/reviews/`, each ending `Status: complete`. It pushes only `claude/dev-manager`.
- **What it never does:**
  - implement or commission sessions (its successor excepted, OD-35);
  - open or merge PRs; edit Notion;
  - call Stream, a database, HDE, Railway, Cloudflare or the TypeSafe API;
  - run `playwright install`, `eas` or `migrate`; run application code;
  - ask Nathan to perform any GitHub operation (OD-58).
- **The relay:** Nathan carries every message by hand (OD-25).

## 2. Rules that bind beyond the charter's text

Read the register in full (OD-01 to OD-83 at the basis). Besides those in the earlier handovers:

- **OD-82:** Dev Manager 6's succession, recorded from Dev Manager 5's handover.
- **OD-83:** App Manager 12 created **App Manager 13**, whose first job is A1-C1's prompt, revision 2. App Manager 12 had lost the GitHub tools in its own session. Nathan's words: *"this github issue is session local"*, so a prompt does not rely on that loss, and revision 1 of A1-C1's prompt (which told its session to use `gh api`) was withdrawn before it ran.
- **GitHub in the Dev Manager's session.** On 22 November this session's GitHub MCP tools were removed too, and its own instructions named `gh api` (REST, read only) as the route. I confirmed reads work that way. **Use the GitHub tools when your session has them; otherwise `gh api` REST, read only, as your session's instructions say.** Never write to GitHub, and never ask Nathan to.
- **The runner's source** (DM-97, section 7): a step stopped by its own `timeout-minutes` is marked failed, so with `continue-on-error` its outcome is `failure` (`actions/runner` release v2.338.2, the version CI reports). Public code, read only, is fair evidence when documentation is silent; say it is source, not a documented contract.

## 3. What Dev Manager 6 did

| ID | Date | What | Labels | Commit |
|---|---|---|---|---|
| — | 19 Nov | Start note | — | `a87a6c8` |
| DM-97 | 19 Nov | SV4 A0's pre-merge read (PR57), a read of `fc9decd` | AH (AH1 to AH6) | `b505a8e` |

- **DM-97's AH1 to AH6** were confirmed applied exactly at `4618859` (each new passage once; each old passage gone, or inside its new passage for AH2 and AH3). PR57 merged at `499ccbb`.
- **Labels already used** (avoid them for new conditions): those in the earlier handovers, plus AH. Free, for example: AJ, AK, AL.

## 4. Where things stand

- **The current item is SV4 Stage A.** A0 merged (PR57). **A1** (the rules; code head `bc0675d`; PR58, open) had its exact-head review ask for changes: AR-1 blocking (two `ReciprocalWriterTests` history tests fail once A1 is on `main`), AR-2 and AR-3 should fix (docstrings), AR-4 should fix outside the classes, the rest nits (the SV4 record).
- **Next, by App Manager 13:** A1-C1's prompt, revision 2 (tests and docstrings only); C1; its verification; PR58's run and Codex; C1's delta review; then **A1's pre-merge read, which comes to you.** Then A2 (the routes and a fifth database job and suite).
- **What A1's pre-merge read must cover** (D-07; the brief's status line):
  - the brief's revisions 4, 5 and 6, all the manager's: A1's owned paths widened (three files, then two docstrings, then C1's paths) and D11's earlier tests;
  - C1 against AR-1 to AR-3, and whether a correction was the right call under D-07 for each finding;
  - whether any governing Markdown changed (none had at `4618859`: check the diff from `499ccbb`);
  - everything else A1 settled and the manager listed;
  - Notion.
- **Later reads due:** A2's pre-merge read; Stage B's brief; the Railway analysis prompt before it runs (DM-95's checklist, in Dev Manager 5's handover, section 4); PF02 1.9 (AM12-31 to AM12-49) when it comes.
- **Carried by DM-97 to the next change to the Foundation workflow (A2 in practice):** the Chromium install's first-attempt margin, with a rule (the carried-items file, "Carried to the next change to the Foundation workflow (DM-97)"). A2's pre-merge read checks it was taken up or recorded.
- **The succession** is not yet recorded: the register, the review log's Sessions row, the handoff and Implementation Control will name Dev Manager 6 until App Manager 13's next batch. Not a mismatch.

## 5. Working method

The earlier handovers' sections 5 hold. What I kept in the scratchpad will not survive; rebuild as needed:

1. **Export, do not check out:** `git archive <commit> | tar -x -C <scratch>/export`. Read code with PyYAML and `ast`; never import or run candidate code.
2. **Classify with the trusted classifier:** `main`'s `scripts/change_scope.py`, extracted outside the tree, `python3 -I --base <base> --head <head> --merge-base` with full SHAs. At `c2cffbe` its sha256 began `b564c62f4a076f51`; recheck it at `499ccbb`.
3. **Workflow changes:** compare old and new jobs step by step by script (hash each step's dict; list identical, changed and new steps), then read every changed and new step whole, and read the live run's logs for the checks that matter.
4. **Replace pairs:** bold labels `**XXn — <what>, `<path>`: <title>.**`, then `> ```` blocks, old then new. A script parses them from the report, checks each old passage once at the commit read, applies them in order per file, and checks each new passage once. Hygiene: no model identifier; last line `Status: complete`.
5. **Earlier conditions as applied:** each new passage once at the later commit; each old passage gone unless it lies inside its new one.
6. **Challenge the framing.** DM-97 found the manager crediting DM-59 with timeouts its text never set. Check what a cited text actually says before agreeing with a summary of it.
7. **Notion** (read-only), with large pages saved to a file and parsed:
   - Implementation Control `3e44590a05eb8118bf02f0dc0c3ea57c`;
   - Dev Manager — reviews and approvals `3e64590a05eb81e29903ca6fccd94268`;
   - the register copy `3e64590a05eb81beaf78d6fa9d64a600`;
   - the Work Register `collection://5ea4c24d-ec63-4afb-a434-8969c26b8fbe`.

   The register copy rewrites file names as descriptions (the Notion checklist), so compare rows after normalizing links and names. State a match only for what you read.
8. **The reply** (Nathan's format): the answer first, in short plain bullets; a named state; nothing unexplained (OD-32); last, the relay message in a four-backtick block naming the report file, the branch commit and the commit read.

Status: complete
