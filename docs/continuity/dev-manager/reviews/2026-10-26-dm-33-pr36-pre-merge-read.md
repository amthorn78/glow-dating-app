# DM-33 — the pre-merge read of PR36 (M04), and the branch-controls question

- **Consultation:** DM-33, revision 1, from App Manager 8, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 3, `session_01KVuPEpFRh9B22beZKTKb27`, branch `claude/dev-manager`.
- **Date:** 26 October 2026.
- **Commit read:** `f4d7df563f3adf05078dda7cd6c843b0b29fbeda`, the head of `claude/magical-wozniak-yfmmx2` and of PR36. **This read covers `f4d7df5`** (DM-03 G2).
  - `main` is `85bbd4d` (PR35). PR36 is the only open PR.
  - No `AGENTS.md`, `CLAUDE.md`, canon or charter path changes in PR36.
- **Environment (names only):** none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is set, and no `STREAM_*` name is present.
- **What I did not do:** I called no provider, database, HDE, Railway or the TypeSafe API, and ran no repository code. I only read GitHub and Notion.

## 1. What I read

- **The governing diff:** `git diff 85bbd4d f4d7df5` over the CI policy, the manager workflow and both start prompts.
- **The code those texts describe, at `f4d7df5`:**
  - `branch-cleanup.yml`;
  - `scripts/branch_cleanup.py`, whole, and the names of its 18 tests;
  - the Foundation diff and the classifier diff.
- **The M04 record:** "Exact-head review of M04", "Correction pass M04-C1", "Manager verification of M04-C1" and "Re-review of M04-C1".
- **The rest:**
  - `git diff 515bd72 85bbd4d` over the governing paths and the register (PR35);
  - the review log's "Deferred conditions";
  - the carried-items file and the hardening item.
- **GitHub, read-only:**
  - PR36 and the open PRs, and `git ls-remote`;
  - the jobs of run 40269750327, M04's cancel test;
  - PR run 40350388448 and its artifacts;
  - the runs on `f4d7df5`.
- **Notion, read-only, at about 16:30 UTC:** *Implementation Control*'s status, and the Work Register rows M04 and P06.2-T.

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1 The pre-merge read | **Approved.** The CI policy, the manager workflow and the start prompts may merge as they stand at `f4d7df5`. They meet DM-32 1.2, 1.4, 1.6, 1.12 to 1.14 and OD-51, and they describe the workflows as the code and the runs show them. One optional nit |
| 2 F3 against DM-32 1.5 | **Confirmed:** F3 makes 1.5 exact; it does not depart from it |
| 3 PF01 1.15's entry | **Confirmed** under the charter's exception, with OD-12's cell, which applies my other DM-32 nit |
| 4 The branch controls | **My recommendation for Nathan** (section 6): one ruleset now. It stops anyone deleting or force-pushing the three kept branches, and `main` then accepts changes only through a PR. Requiring the Foundation gate: not yet. Every rule lapses while the repository is private |
| 5 The Deferred conditions | **The manager's states are right, with two more changes** (section 7) |
| Notion | **No mismatch** |

## 3. Item 1 — the pre-merge read

### 3.1 The CI policy

**Each text matches the code and the runs.**

- **The cleanup section matches the code:**
  - the triggers, and the job that runs only on `main`;
  - the mode set by the event, with only an exact `false` deleting on a dispatch (`branch_cleanup.py:62-70`);
  - `permissions: {}` at the top, with the job's own two permissions, and a 10-minute timeout;
  - the token in the one step's environment, with the credential helper reading it from there (`:34-38`);
  - the ancestor test against `main` as `ls-remote` reads it, and the keep-list (`:22`);
  - fork PRs, and the lease (`:191`);
  - the listing, read page by page to the last `next` link (`:102-133`), and the summary (`:206-276`).
- **DM-32 1.2, 1.4 and 1.6** each have a bullet, in DM-32's terms: the trust limit, the fresh branch and the concurrency.
- **DM-32 1.13, the cancel paragraph after D9.** Run 40269750327 bears it out:
  - its API checks, smoke and artifact jobs ran every step and still read `cancelled`;
  - the Stream, Database and Mobile jobs stopped mid-step;
  - the gate ran and failed.
- **The upload-artifact row.** PR run 40350388448 lists both artifacts, `p04-empty-form-layout` and `p06-db-proof-results`, each kept for 14 days (DM-32 1.9).
- **OD-51** is met in four places:
  - the opening line;
  - the push filter: `'ccr-**'` only while the repository is public, and out when it goes private;
  - "Branch enforcement limitation";
  - the Dependabot line.

### 3.2 The manager workflow and the start prompts

- **Step 3's push rule (1.14) and step 5's push-run sentence (1.12)** both cite the CI policy's section. Step 5 states the rule; its one-clause summary of the reason agrees with the CI policy.
- **Step 5's push-filter line** matches OD-51.
- **Step 7's branch report** now reads the cleanup's summary and checks the remote. It falls back to a list by hand until the first run is recorded, and whenever a cleanup run fails.
- **The handover checklist's keep-list line** is right.
- **The TypeSafe sentence** drops the unsourced date, as DM-31 P-11's condition asked.
- **The start prompts** are right:
  - "public for now" (OD-51) in both;
  - the next-manager prompt's keep-list line: a branch a manager started by hand is safe while its PR is open, and deleted once merged.

### 3.3 Notes

- **Optional nit.** The CI policy's "Until Nathan decides which branch controls to use, App Builder 1 uses scoped branches/PRs…" names a role that is now historical (PF01 D08). "The managers use" fits. The words are old, but M04 edited that sentence.
- **The carried follow-ups are proportionate:** F4, F6, and the re-review's nit 1.
  - F4's carry holds because git reaches only checkout's `origin`. The token is the job's own, scoped to this repository, and it expires with the job.
- **The checklist's run** is the PR run on the final head (DM-30 4.3). PR run 40355293798 passed on `f4d7df5`. The head that integrates this report needs its own run.

## 4. Item 2 — F3 against DM-32 1.5

**Confirmed: F3 makes 1.5 exact.**
- **1.5 is met.** It asked for a restore record that survives a failure. The code writes each row as soon as its push returns (`:269-276`), and it appends to and closes the summary file each time (`:206-218`). `test_failure_midway_has_written_each_deletion` holds it.
- **The gap F3 names cannot be closed by writing the row earlier.** A row written before the push would claim a deletion that might not happen.
- **What the gap risks:** a run killed during one push may leave that one deletion unrecorded. The branch was fully merged, so its commits are in `main`, and only its name is lost.
- **Optional, for the carried list:** print `deleting <name> at <head>` to the log just before each push. Even a killed run's log would then name that branch.

## 5. Item 3 — PF01 1.15's entry

**Confirmed.**
- PR35 changed one line of PF01: 1.15's entry now reads "no account is created and nothing is spent before then". That is my DM-32 nit, word for word, so the charter's exception covers it.
- **OD-12's State cell**, "OD-38 resumed P06.2; other feature work stayed paused until OD-49…", applies my other DM-32 nit. It is confirmed too.
- PR35's other register changes, OD-24's cell and OD-51's row, are not charter-governing paths. I read them for item 4.

## 6. Item 4 — the branch controls

### 6.1 Recommended now: one ruleset, created by Nathan

Nathan creates it in the repository's settings. Sessions do not change settings: M04's exclusions stand, and the CI policy records that API access to the branch-protection settings returned 403.

| Rule | Applies to | How it meets the cleanup | Why |
|---|---|---|---|
| **No deletion, no force-push** | Exactly three names: `main`, `claude/magical-wozniak-yfmmx2`, `claude/dev-manager` | Normally they never meet, because the cleanup never deletes or force-pushes these. If the keep-list ever failed, GitHub would refuse the push, the script would record "deletion failed", and the run would fail: the backstop working | Today only the keep-list in code protects these branches, and the cleanup's token can delete branches |
| **Changes only through a pull request**, with no required approvals | `main` | None: the cleanup never pushes to `main`, and merges are PR merges | Today only the procedure stops a direct push to `main`, for example by a GitHub file tool. No approvals: the PRs are opened under Nathan's own account (`amthorn78`, PR34 to PR36), and GitHub does not let an author approve his own PR, so a required approval would block every merge |

- **The trap the consultation names:** a deletion rule must name exactly the three branches. Any rule that blocks deleting all branches, or a pattern such as `claude/**`, would refuse every cleanup deletion and turn every run red.
- **Bypass list:** none. To delete or rename a kept branch on purpose, Nathan edits the ruleset first.
- **Before the manager branch changes:** the keep-list (a full-scope change) and the ruleset (Nathan) must change together.

### 6.2 Not now: requiring the Foundation gate

- **The problem:** on the manager branch, each push starts a push run and a PR run. Both report a check named `Foundation gate` on the same head; on `f4d7df5` they are runs 40355286953 and 40355293798.
- **Why that matters:** the push run's gate passes on the documentation exemption whenever the last push was Markdown only, even when the PR's full run fails. Which of the two gates a rule would count is not established here.
- **The two ways it can go wrong:**
  - a passing push-run gate satisfies the rule while the PR run fails, so the rule gives false assurance;
  - a failed or cancelled push-run gate blocks a merge whose PR run passed.
- **Until that is settled:** the pre-merge checklist's PR-run item (DM-30 4.3) stays the control.
- **If Nathan wants the gate required later:** one small full-scope change first gives the PR run's gate its own check name. A test then shows which run the rule reads, and the rule requires that name. It is its own item.

### 6.3 When the repository goes private

- **The rules lapse.** By GitHub's message of 23 September, rules on a private repository under this account are not enforced. I expect them to stay configured but inactive; the manager confirms that in GitHub's documentation before relying on it.
- **What then protects the branches:** the keep-list protects the kept branches, and the procedural substitutes (never force-push, the checklist) do the rest. They never stop in the meantime.
- **The cleanup works the same while private.** Its token authenticates the remote read, the PR listing and the deletions. Its runs then count against the 2,000 included minutes. That is an estimated minute each: the job has not run yet, and billing rounds each job up to a whole minute.
- **The records:** the CI policy calls the rules "configured, not enforced", because no ineffective rule may be represented as protection. That joins OD-51's list for going private.
- **Enforcing them while private** would take a paid plan, a line of M07's costed list for Nathan to approve. Its name and price are rechecked then.

### 6.4 For the message to Nathan, in OD-32's form

- **What it is:** one ruleset in GitHub's settings, free while the repository is public. The three kept branches cannot be deleted or force-pushed, and `main` changes only through a pull request.
- **What breaks without it:** nothing today. But the project's history and its three working branches are then protected only by procedure and by one list in the cleanup's code, while a workflow with delete permission runs at every merge.
- **Options:**
  - (a) that ruleset;
  - (b) (a), plus requiring the Foundation gate after the small change in 6.2;
  - (c) no ruleset, procedure only, as today.
- **Recommendation:** (a) now. (b)'s gate only later, and only if he wants it. Every rule lapses while the repository is private.
- **Related, optional:** while the repository is public, GitHub offers secret scanning and push protection for free, by its documentation; I did not recheck that today. Nathan can check that both are on in the repository's security settings.

## 7. Item 5 — the Deferred conditions

- **The manager's three states are right:**
  - **DM-32 1.1 to 1.9 and 1.12 to 1.16:** met. I checked them at this head, against the code, the texts and the runs; 1.9 is met by PR run 40350388448's artifacts. They are done when PR36 merges with these texts.
  - **DM-32 1.10:** open until the merge receipt. The expected deletions are `claude/zen-thompson-5fdqqz`, `claude/laughing-meitner-ywjnk1` and `claude/blissful-volta-coypr6`, and `git ls-remote` shows all three today.
  - **DM-32 1.11:** open, with P06.2-T. Its three homes are in place: the carried-items file, P06.2-T's row, and the hardening item's pointer.
- **Two more rows change:**
  - **DM-31 3.7** is met at this head: P-7's step-5 sentence, and P-9's cancel paragraph and upload-artifact row.
  - **The "DM-32: the pre-merge read" row** closes with this report.
- **If Nathan chooses 6.1's ruleset, three rows follow:**
  - the CI policy and step 7 record it as configured, with its date;
  - the handover checklist's keep-list line names it;
  - OD-51's row for going private adds "the ruleset recorded as not enforced".

## 8. Notion

**No mismatch.**
- *Implementation Control*'s status matches `f4d7df5` (DM-33 sent). Its branch list, six branches, matches `git ls-remote`.
- The Work Register's M04 row matches the repository: "In progress"; next DM-33, Codex on the final head, and the receipt with the three expected deletions.
- P06.2-T's row carries finding 13 (DM-32 1.11).

## 9. Where each item goes

- **PR36:** it may merge with these texts once three things hold (step 7; the charter):
  - the review log records DM-33's disposition;
  - the PR run on the final head passes;
  - Codex's review of that head completes.
- **The carried-items file:** the optional log line before each push (section 4).
- **The CI policy:** the optional "managers" nit, at its next change.
- **The message to Nathan:** 6.4, in OD-32's form. It does not gate PR36.
- **The review log:** DM-33's disposition and section 7's changes to the Deferred conditions.

Status: complete
