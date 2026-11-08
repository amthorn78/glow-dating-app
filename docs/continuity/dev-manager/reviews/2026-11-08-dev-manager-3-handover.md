# Dev Manager 3 → Dev Manager 4: handover

- **Direction:** Nathan Amthor, 8 November 2026, in Dev Manager 3's session: *"create a new DM session (Glow Dev Manager 4) to continue with your role"*. Under OD-35, at Nathan's direction, the outgoing Dev Manager runs its handover and creates its successor with the remote-session tools. The primary manager records the direction.
- **Written by:** Dev Manager 3, `session_01KVuPEpFRh9B22beZKTKb27` ("Glow Dev Manager 3"), branch `claude/dev-manager`, environment `Glow App - No Stream`.
- **Basis:**
  - the manager branch `claude/magical-wozniak-yfmmx2` at `0a63219a5fdd8275afb285dbb85d4b57f809d076` ("P06.2-F: DM-40 applied; brief revision 4 and correction C4's prompt");
  - `main` at `bac3c1983134f4e977f867ac30b3086b5318216f` (PR39);
  - this branch at `497ba97` (DM-40), plus this file.
- **What this is:** what the successor needs beyond the charter, the review log and the reports, with a map of where the rest lives. Dev Manager 3 pushes nothing after this file's commit.

## 1. The role

Read the charter (`docs/planning/dev-manager.md`) and the start prompt (`docs/planning/start-prompts/dev-manager.md`); both hold. In short:
- **What it does:** Nathan's second layer of oversight (OD-15). It reviews, challenges and approves consequential decisions; reads governing Markdown before the PR that carries it merges; and reads every prompt that authorizes credential use or a live provider action before Nathan runs it.
- **Where it writes:** only report files under `docs/continuity/dev-manager/reviews/`, each ending `Status: complete`. It pushes only `claude/dev-manager`.
- **What it never does:**
  - implement or commission sessions, except its successor (OD-35);
  - open or merge PRs, or edit Notion;
  - call Stream, a database, HDE, Railway or the TypeSafe API;
  - run `playwright install`, `eas` or `migrate`.
- **The relay:** Nathan carries every message by hand (OD-25).

## 2. Rules that bind beyond the charter's text

Read the owner-direction register in full (OD-01 to OD-57 at the basis). These shaped Dev Manager 3's work most:
- **OD-29:** one item at a time. A read sits in that line, so answer completely the first time.
- **OD-32:** nothing unexplained reaches Nathan. Most consultations end with no item that is his.
- **OD-47:** Dev Manager 3's creation. **OD-49 and OD-50:** the order and the costed list (M07). **OD-51 and OD-52:** the repository is public for now; no branch controls, procedure only.
- **OD-53:**
  - S2: a correction of 60 or fewer non-test lines that answers a finding gets a delta re-review;
  - S5: Notion holds a summary and a register copy;
  - D1: *Nathan's pick* reads "not recorded".
- **OD-54:** `zod`, `glob` and `minimatch` advisories accepted. **OD-55:** a US legal entity; the US, all states, English, for now; age by self-entered birth date plus store signals. **OD-56:** App Manager 9. **OD-57:** Playwright and similar tools via CLI environments; never `playwright install` in a cloud container.
- **The charter's "A read covers one commit"** (DM-03 G2): a later governing change needs another read, except one that applies a Dev Manager finding's own text, which the next consultation confirms. So write conditions as exact text when wording matters.
- **Fix or carry** (the workflow's step 6; DM-23): a defect in a correction class is fixed before the merge; a nit is a follow-up; a defect only P11 can show goes to the P11 plan. The Dev Manager is consulted when the rule does not decide, or when the fix's design changes.
- **Coverage claims** (DM-38 4.2; DM-39 1.4; AM9-03): never write or accept "any", "every", "all", "follows" or "wherever" over arbitrary code. Ask for named forms and stated limits. Dev Manager 3 made this error itself in DM-38 section 4, and withdrew it in DM-39.

## 3. What Dev Manager 3 did

| ID | Date | What | Verdict, in short | Commit |
|---|---|---|---|---|
| — | 25 Oct | Start note | — | in the review log |
| DM-25 to DM-30 | 25 Oct | P06.2 Stage C2's re-review order, deviations, CX12, the pre-merge read | See each report | in the review log |
| DM-31 | 26 Oct | M05's whole-project review: P-1 to P-19, N1 to N6 | Approved with conditions | `8d51446` |
| DM-32 | 26 Oct | M04's brief | Approved with conditions | `3abbc81` |
| DM-33 | 26 Oct | PR36's pre-merge read; the branch-controls question | Approved with conditions | `8855163` |
| DM-34 | 26 Oct | OD-52's and OD-53's texts | Approved, with D1.1 | `be8f6ae` |
| DM-35 | 1 Nov | M06: path (B), SDK 58 | Approved with conditions | `dfc138e` |
| DM-36 | 1 Nov | `noxcturnal` before PR38's merge | Approved with conditions; a standing rule | `981d3ce` |
| DM-37 | 1 Nov | P09.3a's gaps and the A05 questions | Approved with conditions; PF01's release gate | `0db8c42` |
| DM-38 | 2 Nov | P06.2-F's render-rule check after C1 | Option (b) with conditions | `f019911` |
| DM-39 | 2 Nov | The check after C2's probes | Option (b), no check changes; a positive-list claim | `4450761` |
| DM-40 | 8 Nov | C3's delta re-review; OD-57's texts | Option (a) with syntax-exact words; OD-57 approved | `497ba97` |

## 4. Where things stand

- **The current item: P06.2-F** (PR40, full scope). Corrections C1 to C3 are verified. C4's prompt, at `0a63219`, applies DM-40: comment, record and test-name changes only, with section 4.2's words.
- **What comes to the Dev Manager next:**
  - **DM-40 3.4:** if C4's bounded delta re-review finds a form inside the narrowed words, it comes to the Dev Manager before any C5;
  - **DM-40 section 4.2:** the next consultation confirms that C4 applied the words, as narrow or narrower;
  - after that, PR40's merge, and then P06.3 and the server slices (OD-49). SV1's brief comes to the Dev Manager, with its threat model (DM-31 item 3) and the matrix's pointers (DM-37 2.1).
- **The render-rule saga, in one line:** a source check over arbitrary TypeScript does not converge on a data-flow guarantee.
  - **So the claim is a positive list** (DM-39 4.2; DM-40 4.2), the checks are frozen (DM-39 1.1), and the real fix is option (c), view models by explicit field copy.
  - **When (c) lands:** at the next change to how `screen.tsx` or `rows.ts` hold chat data (DM-38 2.5), and before P11 serves the chat reads at the latest (DM-39 3.1). Its inputs are the forms and fixes in DM-39 1.3 and DM-40 1.3 and 1.4.
  - **Hold the line:** every round has found new forms. Keep the next review bounded, and do not reopen the checks.
- **Open and standing conditions:** the review log's "Deferred conditions" holds them all. The standing ones:
  - DM-36: `noxcturnal` stays unloaded (`apps/mobile/AGENTS.md`, "Dependency changes" 5);
  - DM-30: the standing guard;
  - DM-40 section 7: a prompt that authorizes `--with-deps` says it installs operating-system packages with root.

## 5. Working method

1. **Check the environment by names only.** Fetch the manager branch, and confirm that the consultation's commit is on it. List what changed since your last read, governing paths first (`AGENTS.md` and `CLAUDE.md` at any level, `docs/pf-canon/`, the workflow, the charter, the CI policy, the register and the start prompts).
2. **Read the inputs at the named commit** with `git show <commit>:<path>` into the scratchpad. Never change the working tree except for your report.
3. **Probe claims yourself where you can.**
   - Use a scratch copy outside the checkout: `git archive <commit> apps/mobile packages | tar -x`, then `npm ci --ignore-scripts` in `env -i PATH="$HOME/.local/bin:/usr/bin:/bin" HOME="$HOME" LANG=C.UTF-8`, passing `HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS` by reference.
   - For each probe: edit the file, run `node --test`, `npx tsc --noEmit` and ESLint, then restore and check the SHA-256.
   - Keep probe scripts in a separate scratch folder, and run Python with `-I`.
   - Give your probes IDs and tabulate them in the report. Never hand code to the manager: describe the evidence.
4. **Read Notion, read-only.** The large pages save to a file; parse it with `python3 -I`, and state a match only for the parts you read, by name (AM9-01).
   - *Implementation Control:* `3e44590a05eb8118bf02f0dc0c3ea57c`. Its status section, its standing bullets, "One item at a time" and "Standing directions".
   - *Dev Manager — reviews and approvals:* `3e64590a05eb81e29903ca6fccd94268`.
   - **The register copy:** `3e64590a05eb81beaf78d6fa9d64a600`.
   - **The Work Register:** `collection://5ea4c24d-ec63-4afb-a434-8969c26b8fbe`. Query with SQL on `"Work ID"`.
   - **The TypeSafe uses table:** `collection://e1d83c6d-23b7-447f-8bc6-dcbb4829f24e`. Query with SQL on `"Step"`.
5. **Write the report** under `docs/continuity/dev-manager/reviews/`, dated the day you write it. Its order:
   - a header, with the commit read and "this read covers it";
   - what was read;
   - a verdict table;
   - a section per item, with numbered conditions;
   - Notion;
   - where each item goes;
   - `Status: complete`.

   Keep model identifiers out of the file. Commit only that file, with your session's attribution lines, and push `claude/dev-manager`, retrying on a network error.
6. **Reply in Nathan's format:**
   - the answer first, in short bullets;
   - a named state (IN FLIGHT, NOTHING NEEDED or DECISION NEEDED);
   - plain words;
   - last, the relay message in a four-backtick block, naming the report, your commit and the commit read.

Status: complete
