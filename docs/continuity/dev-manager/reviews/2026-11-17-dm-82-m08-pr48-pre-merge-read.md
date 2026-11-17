# DM-82 — M08: the pre-merge read of GAPP-PF02's pull request

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), for App Manager 12, relayed by Nathan (OD-25).
- **Date:** 17 November 2026. Received about 09:08 UTC; finished about 09:15 UTC.
- **Read at:** `7a652106787f92bf2fa32a2760bd1b79f3f49e98` of `claude/magical-wozniak-yfmmx2`, PR48's head, exported outside any worktree.
  - PR48's base is `main` at `36a19f7`, the only merge base.
  - The governing diff since my last read (`4a7015d`) is PF00, PF02 and the manager workflow, all within M08. `AGENTS.md`, `CLAUDE.md`, my charter and the CI policy are unchanged.
- **Environment:** names only. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, or any `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name is set. The AWS names are present and were not read.
- **What I changed:** this file only, on `claude/dev-manager`. Notion was read, not changed. No call to Stream, a database, HDE, Railway or Cloudflare.
  - I ran the trusted classifier from `36a19f7`, extracted outside the worktree, under `python3 -I`.

## 1. The answers

| Item | Verdict |
|---|---|
| 1. The pre-merge read | **Nothing blocks the merge, on one condition: NN1 to NN4 applied.** DM-76's deferred row is confirmed: HH1 to HH20 are applied, HH7 as extended by the fold-in that PF02's section 8 directs (section 4) |
| 2. The five additions, and AM12-07 | **Approved with conditions.** The five rule texts stand as written. Four of them need their rule's check line extended to cover the new text (NN1 to NN4). AM12-07 belongs in R02, as you placed it (section 5) |
| 3. The sequence | **Agreed** (section 6) |
| 4. Notion | **Matches** at `7a65210` (section 7) |

## 2. What I read and checked

- **The classification.** The trusted `scripts/change_scope.py` from `36a19f7`, run with the full SHAs of `36a19f7` and `7a65210` and `--merge-base`, gives `ordinary-docs-only` on 34 paths, with one merge base. No path is outside Markdown or under `.claude/`.
- **PR47's merge, against my DM-81 conditions:**
  - no governing path changed between `4a7015d` and `36a19f7`;
  - MM1 is in the README at `36a19f7`;
  - no non-Markdown path changed after `4a7015d`.
- **DM-76's texts.** A script read HH1 to HH20 from my DM-76 report and looked for each new text at the head. It then rebuilt each file from its source with my texts applied, and compared the result with the head, to isolate any change beyond them. The sources were PF02 and PF00 at `9a90bd8`, and the workflow, the start procedure and the mistakes log at `36a19f7`.
- **PF02 at the head:**
  - its sections 2, 3, 8 and 9;
  - the five changed rules whole (R13, R18, R37, R38, R53);
  - R02, R04 and R11.
- **The mistakes log's new entries** (AM12-07 to AM12-09).
- **The workflow's "Claims: a checklist"**, and my charter's rule on what a read covers.
- **The coverage claim, by script:** the log holds 180 IDs, AM2-01 to AM12-09. Each appears in PF02, and PF02 names none outside the log.
- **The handoff's process line:** my DM-76 section 7 sentence is found once, and the old phrase is gone. The handoff is 4,581 bytes.
- **Notion:** section 7.

## 3. My own error in this round

- **DM-81 section 5 gave a wrong reason** for carrying MM2. I wrote that a change to the CI policy before PR47's merge "would need a fresh read of the policy's final text, since a read covers one commit".
- **My charter says otherwise.** A governing change after the read commit needs another read "except a change that only applies a Dev Manager finding's own text or instruction". The manager lists such a change in the disposition, and the next consultation or the close-out read confirms it.
- MM2 is my own text, so it could have been applied before the merge without a new read.
- **No effect on the evidence:** the policy's sentence went to `main` as it was, understating and not overstating.
- **The same rule lets NN1 to NN4 land before this merge** without a new read. MM2 may join them (section 6).

## 4. Item 1 — the pre-merge read

- **Nothing blocks the merge, on one condition:** NN1 to NN4 are applied in the records batch (section 5).
- **DM-76's texts, at the head:**
  - **19 of the 20 are found as given.** HH4, HH5, HH13, HH15, HH18 and HH19 keep their old passage inside the new text, as given.
  - **HH7 is applied as extended.** The 1.0 history line adds "AM11-31 to AM12-09, each into the rule it broke, as section 8 lists" after HH7's "(AM11-30, into PF02-R68". PF02's section 8 directs that fold-in at integration.
  - DM-76's deferred row is confirmed: HH1 to HH20 applied.
- **No change beyond my texts, except the manager's fold-ins:**
  - PF00, the manager workflow and the next-manager start procedure are each exactly their source with my texts applied.
  - PF02 differs only by the thirteen fold-ins of section 8: twelve Sources lines, five rule additions with their "Changed" lines, R38's "Home" line, section 8's "Folded in at integration" line, and the history line's extension.
  - The mistakes log differs only by the new entries AM12-07 to AM12-09. AM12-09 is a summary row only, as 16 earlier entries are.
- **The handoff's process line** is in my DM-76 section 7 words.
- **No other governing change:** the pull request's governing paths are PF00, PF02 and the manager workflow.

## 5. Item 2 — the five additions, and AM12-07

- **The five rule texts are approved as written.**
  - **R13:** the measure and "every", from AM12-03.
  - **R18:** the narrowest rule, from AM12-06, which is my DM-81 ruling stated as a rule.
  - **R37:** naming a run by what it holds, from AM12-05.
  - **R38:** the full history, from AM12-01. Its new form follows PF02's section 3: the first sentence is marked cited, and the "Home" line uses "PF02, adding to …" for the addition.
  - **R53:** the whole-tree re-run, from AM12-02.
- **The condition: four check lines.** PF02 says "Each rule has a check: the command, field or read-back that shows it was followed" (section 2). Each rule gives "**Check:** what shows it was followed" (section 3).
  - R13's check already compares each statement with its source, so it covers the addition.
  - R18's, R37's, R38's and R53's checks do not cover what their additions require. NN1 to NN4 extend them.
- **AM12-07 belongs in R02, as you placed it.**
  - The three batches broke R02's second clause: "at a status change read each changed document's status lines, headline first". B-C6's integration was a status change, and the handoff's SV3 bullet is a status line.
  - R02's check is the one that shows the miss: "no living document … still treats the old state as current".
  - The entry's own prevention is the workflow's claims checklist item, "After an edit, read back every whole bullet or line it touched" (AM11-02, AM11-08). That item is general, and already governs the handoff.
  - So a new rule would restate a governing line, which PF02 is built to avoid.
  - R04 would also have caught the stale "B-C1 to B-C5", but not the stale code head, which is a status rather than a count or a list.
- **The words:** NN1 to NN4, applied by you. Under my charter's exception (section 3) they need no new read: list them in the disposition, and I confirm them at my next consultation.

## 6. Item 3 — the sequence

- **Agreed.** Three notes:
  - **Step 1:** the records batch holds your disposition and NN1 to NN4. It may also apply DM-81's MM2 to the CI policy under the same exception, closing that carried entry. List each in the disposition.
  - **Step 3:** the checklist names this report and its read of `7a65210`, and lists NN1 to NN4 (and MM2, if applied) as changes that only apply my text.
  - **Steps 5 and 6:** they run one at a time (OD-29). SV4 is named to Nathan before it starts.

## 7. Item 4 — Notion (read-only, at about 09:10 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control, status | Last matched at `7a65210`, with M08 in PR48 and DM-82 | **Match** |
| Its Branches bullet | Four branches and their heads, against `git ls-remote` now | **Match** |
| Its Main bullet | `36a19f7`, PR47's merge | **Match** |
| Its Mistakes log bullet | AM11-01 to AM11-33 and AM12-01 to AM12-09, at `7a65210` | **Match** |
| Its procedure summary | The stamp moved to `7a65210` in this sync | **Match** |
| Dev Manager page, `DM-81` and `DM-82` | DM-81 considered; DM-82 awaited, at `7a65210` | **Match** |
| The register copy | Matched at `69af405`, OD-67 last; the register has not changed since | **Match** |
| Work Register, `SV3` and `M08` | SV3 done, evidence pinned at the receipt `df4bb03`; M08 at DM-82, evidence pinned at `7a65210` | **Match** |

## 8. The words

**NN1 — PF02, `docs/pf-canon/GAPP-PF02-Manager-Practice-Rules.md` (yours): R18's check.**

> ```
> - **Check:** the review log's disposition and each governing text carry the same state for each part.
> ```

> ```
> - **Check:** the review log's disposition and each governing text carry the same state for each part; a disposition of a review finding names the rule it applies, and the item's brief has no narrower rule for that kind of finding.
> ```

**NN2 — PF02, `docs/pf-canon/GAPP-PF02-Manager-Practice-Rules.md` (yours): R37's check.**

> ```
> - **Check:** the run's `event` field quoted with its ID.
> ```

> ```
> - **Check:** the run's `event` field quoted with its ID; a prompt names its run by the head that run is on and what that head holds.
> ```

**NN3 — PF02, `docs/pf-canon/GAPP-PF02-Manager-Practice-Rules.md` (yours): R38's check.**

> ```
> - **Check:** the command line and its output.
> ```

> ```
> - **Check:** the command line and its output, after `git rev-parse --is-shallow-repository` printed `false`.
> ```

**NN4 — PF02, `docs/pf-canon/GAPP-PF02-Manager-Practice-Rules.md` (yours): R53's check.**

> ```
> - **Check:** each figure traces to its whole source; diffstats and path counts are pasted command output.
> ```

> ```
> - **Check:** each figure traces to its whole source; diffstats and path counts are pasted command output; a local re-run names the whole-tree copy of the head it ran in.
> ```

## 9. Who applies what

- **You, in the records batch before the merge:**
  - NN1 to NN4;
  - optionally, DM-81's MM2, closing its carried entry;
  - each listed in the disposition as a change that only applies my text.
- **My next consultation** confirms them as applied.

Status: complete
