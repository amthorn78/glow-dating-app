# DM-34 — the pre-merge read of OD-52's and OD-53's texts

- **Consultation:** DM-34, revision 1, from App Manager 8, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 3, `session_01KVuPEpFRh9B22beZKTKb27`, branch `claude/dev-manager`.
- **Date:** 26 October 2026.
- **Commit read:** `79713c51a49f8cb97e285d57e3aa5869b31b5b5a` of `claude/magical-wozniak-yfmmx2`. **This read covers `79713c5`** (DM-03 G2).
  - `main` is `4794d3e` (PR36), whose tree equals `9d1570e`'s.
  - PR37 is open from the manager branch, at `2681783`. That commit, after `79713c5`, changes only the handoff.
  - Every path changed since `4794d3e` is a regular Markdown file.
- **Environment (names only):** none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is set, and no `STREAM_*` name is present.
- **What I did not do:** I called no provider, database, HDE, Railway or the TypeSafe API, and ran no repository code. I only read GitHub and Notion, and the installed scoring skill's text (section 3.3).

## 1. What I read

- **The governing diff,** `git diff 4794d3e 79713c5`, over:
  - `AGENTS.md`;
  - PF00 and PF01;
  - the manager workflow;
  - the charter;
  - the CI policy.
- **The same diff over the other paths named:** the register, `docs/README.md`, the next-manager start prompt and the reasoning-strength matrix; and over the carried-items file.
- **The terms the texts apply:**
  - DM-31 item 2 (S2, S5, D1) and DM-29 2.3 (the `@codex review` direction);
  - M05's S2, S5 and D1;
  - DM-33 section 6.4.
- **The records:**
  - the review log's "DM-33" and "Deferred conditions";
  - M04's merge receipt;
  - `git ls-remote`, and PR37.
- **The scoring skill's own text,** read only, for D1: `typesafe-scoring`'s `SKILL.md` and the field defaults in `scripts/score_v8.py`.
- **Notion, read-only, at about 18:20 UTC:**
  - *Implementation Control*'s status and its new operating-procedure summary;
  - the register copy, compared row by row with the repository.

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1 OD-52's texts | **Approved.** One optional nit (3.1) |
| 2 OD-53's texts | **Approved, with one condition, D1.1.** S2 is on DM-31's terms. S5 is right in all six places and the start prompt. The `@codex review` permission is DM-29 2.3's, with Nathan's 60 minutes. D1 keeps the column rightly, but the texts must say the manager overrides the skill's "pending" |
| 3 The register rows | **Approved.** OD-52 and OD-53 read Nathan's answers rightly, and the four cells are right |
| 4 The Notion summary | **Approved, with conditions N1 to N3**, which are Notion fixes and do not gate PR37. The stamp and the links are right. Two lines drop a qualifier or a rule, and the status lead is stale |
| 5 The Deferred conditions | **Right, with three state updates** (section 6) |

## 3. Items 1 and 2 — the texts

### 3.1 OD-52

- **Approved.** "Branch enforcement limitation" says Nathan chose none (OD-52), and the procedural substitutes stay, now and once the repository is private. Its own sentence now reads "the managers use", which applies DM-33's nit. Step 7 cites OD-52.
- **Optional nit, at the CI policy's next change:** "require the gate as well when enforceable repository controls become available" (line 91) reads as if no control were available. Under OD-52 they are available, and Nathan chose none. A fit wording: "require the gate as well only if Nathan chooses enforced controls (OD-52 chose none), after the change DM-33 6.2 names".

### 3.2 S2, S5 and the `@codex review` permission

- **S2: these are DM-31's terms.** The step-6 bullet holds each one:
  - the delta review reads every path the correction touches as it stands at the head, not the diff alone;
  - it keeps the security focus;
  - the 60 lines are non-test lines;
  - Codex still reads the final head.

  Its two other qualifiers only narrow it: "that answers a review finding" (M05's own S2), and "a larger correction, or one that changes a design, still gets a full exact-head review".
- **S5: approved** in all six places and the next-manager prompt.
  - Each says the same thing: a summary with links at a named commit, a full copy of the register, and the repository wins.
  - PF00 1.11's and PF01 1.16's entries give the reason, the affected tasks, the impact and the authority.
  - The workflow's match check fits a summary: the register copy must match, the summary must stay true, and its stamp moves when a governing text changes.
- **The `@codex review` permission: approved.** It is the standing direction DM-29 2.3 described, with the wait Nathan accepted (60 minutes): one post when a pass stalls, and Nathan told if the new pass stalls too.
  - **Its scope:** a pass shown running with no result. Codex's answer on PR37, "To use Codex here, create an environment for this repo", was not a stall but a refusal, so taking it to Nathan was right.

### 3.3 D1: keeping the column is right; the texts need one sentence

- **Keeping the column is right.** The skill writes its "Notion row" verbatim, and that row includes *Nathan's pick*: "Do not add columns or rename these; the script's field names are the contract" (`SKILL.md`). The skill is Nathan's, outside the repository. Dropping the Notion property would break the skill's write.
- **The gap:** the skill prints *Nathan's pick* as "pending" (`notion_properties(…, pick="pending")`). So two texts are not exact:
  - step 3's "with *Nathan's pick* left at 'not recorded'": nothing leaves it at "not recorded";
  - the matrix's "the fields are never composed by hand".

  A manager who follows the skill writes "pending", the word DM-31 ruled out.
- **D1.1 (condition, before PR37 merges):** step 3 and the matrix's "Recording" paragraph say that the manager sets *Nathan's pick* to "not recorded", in place of the "pending" the skill prints. That one field is the only one the manager writes by hand. OD-53's D1 sentence may say the same.
- **For Nathan, as information:**
  - He chose (a), "drop it", for the pick column.
  - It stays only because his scoring skill writes it, and every new row reads "not recorded".
  - Removing it means changing the skill, which is his to do if he wants it.

## 4. Item 3 — the register rows

- **OD-52 reads "c" rightly.** Its options are DM-33 6.4's as written, with my recommendation (a) shown. Its State lists the CI policy's substitutes and the keep-list. "Revisit with OD-24's paid-plan review, at P09 at the latest, or when Nathan asks" is the manager's timing, and it fits OD-24.
- **OD-53 reads "I accept your recommendations" rightly** as S2 (a), S5 (a), D1 (a), and the permission with 60 minutes. Its options match M05's 6.3 and DM-31's terms. It states D1's departure from "drop it" openly, with its reason.
- **The four cells are right:**
  - OD-24: "went to Nathan … he chose none";
  - OD-26: "amended by OD-53 (S5)";
  - OD-34: "Nathan's pick is retired by OD-53 (D1)";
  - OD-51: "he chose none, procedure only".

## 5. Item 4 — Notion

**What is right:**
- **The stamp:** `8cffa1e`. No governing text changes between `8cffa1e` and `79713c5`; only the handoff does. Every link is pinned at `8cffa1e`.
- **Most of the summary:** apart from N1, each rule bullet says what the repository says: the relay, one item at a time, decisions, classification, Codex, merges, security, TypeSafe and records.
- **The register copy** matches `8cffa1e`, and the register is unchanged at `79713c5`. Row by row, OD-01 to OD-53 are identical apart from link labels: for example "AGENTS file" for `AGENTS.md`, and "documentation map" for `docs/README.md`.

**Conditions** (the manager's, fixed at once under the match check):

| # | Mismatch | Fix |
|---|---|---|
| N1 | "A correction of 60 or fewer non-test lines gets a delta re-review" drops S2's qualifiers | "…that answers a review finding and changes no design, on step 6's terms" |
| N2 | The Security bullet leaves out the HDE-shared environment rule (`CLAUDE.md`; `AGENTS.md`) | Add: if `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is present, tell Nathan, never use the values, and run app commands only in a clean environment |
| N3 | The status lead still says "this page is its matching copy (OD-26, OD-27)" | Under OD-53 the page summarizes the guidance, copies the register, and carries the status as matched at its commit |

- **Optional:**
  - Move the superseded full copy to a child page. It is marked "do not work from it", but it is most of the page, and it was the copy that drifted (M05 finding 30).
  - The Codex bullet could keep "handle each finding first" and "tell Nathan if the pass stalls too".

## 6. Item 5 — the Deferred conditions

**Right at this head, with three state updates:**
- **DM-31 3.7:** "Met at `f4d7df5`" becomes "Done: PR36 merged with these texts (`4794d3e`)", as the DM-32 rows already say.
- **The OD-52 and OD-53 rows:**
  - OD-52's texts are approved by this read.
  - OD-53's are approved with D1.1. Applying D1.1 needs no further read (the charter's exception).
- **"DM-31 item 2: … D1's 'not given', never 'pending'"** is done only once D1.1 is applied. Until then, a row written from the skill reads "pending".

**Also, in the review log:** DM-33's summary row has six cells under a seven-column header, so its Disposition cell is missing. It reads: "Considered by App Manager 8 (merge `28b37c3`); see 'DM-33' below".

The other rows are right. M04's receipt (run 40366011457) and `git ls-remote` agree that the three expected branches are gone and the three on the keep-list remain.

## 7. Where each item goes

- **Before PR37 merges:**
  - D1.1, in step 3 and the matrix;
  - DM-34's disposition, recorded in the review log;
  - Codex's review of the final head (step 7).
- **Notion, at once:** N1 to N3.
- **The carried list or the next change:** 3.1's optional nit, and 5's optional items.
- **To Nathan, as information:** 3.3's line on the pick column.
- **The review log:** DM-33's missing Disposition cell, and section 6's updates.

Status: complete
