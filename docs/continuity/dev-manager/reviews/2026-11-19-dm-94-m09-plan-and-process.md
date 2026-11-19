# DM-94 — After M09: PF01 1.19, D-06, D-07 and PF02 1.8

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), for App Manager 12, relayed by Nathan (OD-25).
- **Date:** 19 November 2026. Received at 00:53 UTC; finished about 01:16 UTC.
- **Read at:** `6bee2e9d11152e154759ccf5fdf083e3aefd1403` of `claude/magical-wozniak-yfmmx2`, exported outside any worktree. PF01 there is the text of `b738529`.
  - `main` is at `6edae78` (PR54), the only merge base.
  - The governing diff since my last read (`b721e72`): `AGENTS.md`, `CLAUDE.md`, PF01 1.19, PF02 1.8, the manager workflow, my charter, the CI policy and the start procedure's one line. PF00 is unchanged. PF02 1.7, which PR54 merged, is as DM-91 approved it.
  - Later commits, read for section 12 only: `ebf84e3` (OD-76), and `f1653f1` and `d435f96` (M07's brief and prompt).
- **Environment:** names only. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, or any `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name is set. The three AWS names are present and were not read (OD-76 now records them).
- **What I changed:** this file only, on `claude/dev-manager`. Notion and `amthorn78/glow-docs` were read, not changed. No call to Stream, a database, HDE, Railway, Cloudflare or the TypeSafe API, and no public web page was fetched. No test or application code was run.
  - I ran the trusted classifier from `6edae78`, extracted outside the worktree, under `python3 -I`.

## 1. The answers

| Item | Verdict |
|---|---|
| 1. PF01 1.19 | **Approved with conditions AD1 and AD2.** It changes no owner direction, process rule, D08 authority or HDE boundary, and its three statements about HDE's canon are true to HDE's PF05. Two sentences became false when Nathan answered D-03 after 1.19 was written. Notion's markings are right until the merge, and nothing in it needs his decision first (section 3) |
| 2. OD-73 to OD-75 | **Approved with conditions AD3 and AD4,** which change the records beside the rows, not the rows. The rows say what he said, and mark the manager's readings as readings. But OD-68's row still says "off at launch" with no mark, and no record says who turns the toggle on, or when (section 4) |
| 3. D-06 | **Approved with condition AD5.** Your reading is right: one such item at a time, and a full-scope result stops it. But one line of "The process is linear" still blocks the second item as written (section 5) |
| 4. D-07 | **Approved with conditions AD6, AD7, AD8 and AD11.** Both your choices hold in principle. But SV2-R's correction C1 is not the example you took it for: its first test guards a staff restriction and an owner's removal, which are security boundaries. AD7 says so, and keeps as a correction a missing test that an acceptance check rests on. AD8 and AD11 settle the unclear case between changing and applying a decision (section 6) |
| 5. PF02 1.8 | **Approved with conditions AD10 to AD15** (AD11 is item 4's). R14's new sentence is garbled (AD10), and R46 does not cover AM12-30's handoff errors as a repeat (AD12 to AD15). **The deferred condition closes on this answer** (section 7) |
| 6. `CLAUDE.md` | **Approved** (section 8) |
| 7. The CI policy | **Approved.** One test reads Markdown, and only that one; the gate sentence is DM-34 3.1's wording (section 8) |
| 8. M09's proposals | **(a) Agreed,** with AD9 for the charter now. **(b) Agreed,** with three points on the move (section 9) |
| 9. The sequence | **Agreed** (section 10) |
| 10. Notion | **Five mismatches:** the Branches and Mistakes log bullets, the register copy's header, no DM-94 row on the Dev Manager page, and P07.1's D-03. M09's 32 field changes match its record (section 11) |
| After the read commit | The charter's OD-76 sentence at `ebf84e3`: **approved** (section 12) |

## 2. What I read and checked

- **The classification.** The trusted `scripts/change_scope.py` from `6edae78` (SHA-256 prefix `b564c62f4a076f51`), run with the full SHAs of `6edae78` and `6bee2e9` and `--merge-base`, gives `ordinary-docs-only` on 28 paths, with one merge base.
- **The commits since my last read:** from my DM-93 (`adb769d`) through SV2-R's session, its review, correction C1 and PR54's merge (`6edae78`); M09 (`f086f0d`, `b738529` and `20a0d99`, merged at `c48b950`); its integration (`561dbc3`); and this consultation (`6bee2e9`).
- **Every governing change, whole:** PF01 1.18 to 1.19 (unchanged from `b738529` to `6bee2e9`); PF02 1.7 to 1.8; `AGENTS.md`; `CLAUDE.md`; the manager workflow; my charter; the CI policy; the start procedure's line.
- **The M09 record:** the summary, sections 1.1, 4.5, 4.7, 5 and 8.1, section 10 whole, Appendix B, and "Manager verification of M09".
- **The sources the texts rest on:**
  - HDE's PF05 v2.5.7 in `amthorn78/glow-docs` at `707da56`, read-only: sections 1, 5.1.7 and 5.9, for PF01 1.19's §5 paragraph;
  - `packages/contracts/tests/test_transition_contract.py`, lines 699 to 707, and a search of every test, script and workflow for code that reads a Markdown file, for the CI policy;
  - DM-34 3.1; DM-57's U11; OD-49, OD-51, OD-53, OD-61 and OD-68; AM12-22 to AM12-30 in the log; the review log's deferred conditions;
  - SV2-R's record: the exact-head review's R1 and R2, and correction C1, for D-07's example.
- **Notion:** section 11.

## 3. Item 1 — PF01 1.19

**Approved with conditions AD1 and AD2.**

- **What I checked.**
  - Each change in section 10.1's table is in the text, and nothing else changed.
  - **No owner direction changes:**
    - P06.2-T's place is the Work Register's to set (OD-49), so folding it into SV4 Stage A is a plan change;
    - SV5, SV2-L and AC1 to AC3 add to the server work that OD-49's N1 put before P10, sealed until P11, and reverse nothing;
    - "public for now" is OD-51's.
  - **No process rule, D08 authority or HDE boundary changes.** The glow-docs row and §5 both say that reading HDE's canon authorizes no call to HDE and no change to it, and §5 says the canon is evidence, not the delivered contract.
  - **§5's three statements are true to HDE's canon.** I read PF05 v2.5.7 in glow-docs:
    - the pair read's two versions (the Harmony band; ten categories), with no number (sections 1 and 5.1), and a narrative route beside them (`/aux/narrative`);
    - live database success over live HTTP "deferred to a future epic with the App user model" (section 5.1.7);
    - `POST /_ops/bodygraph/resolve`: inspection "did not find this Required-Now HTTP route" (section 5.9).
- **What became false when Nathan answered D-03 on 19 November (OD-75),** after 1.19 was written:
  - A04's row lists "the photo and CSAM checks if chosen". They are now chosen. **AD1.**
  - The 1.19 entry says §7's Media paragraph "waits for his decision". It no longer does. R-29's disposition is right that the paragraph needs no change, since "moderate before publication" already covers the check. **AD2** says so in the entry.
- **Notion's markings are right until the merge.** PF01 1.19 is not in force before then, and the links are pinned at `b738529`, a commit ID, as PF02-R61 requires. After the merge, the Plan References move to `main` and Notion follows the merged text. AD1 and AD2 change no Notion field that M09 wrote.
- **Nothing in it needs Nathan's decision first.** OD-73 covers it, and the brand's final approval stays his, as the text says (D-14).
  - One thing for the merge message (OD-32): 1.19 changes P09's and P10's acceptance, and puts five items before P10 (SV5, SV2-L and AC1 to AC3). Tell him that in plain words when it merges.

## 4. Item 2 — OD-73 to OD-75

**Approved with conditions AD3 and AD4.** The rows say what he said. Where they go further, they say whose reading it is. The two conditions change the records beside the rows.

- **OD-73** quotes his authorization exactly. Its scope (M09's session, and no later session) is marked as the manager's reading, with section 10 as its basis.
- **OD-74** quotes him exactly.
  - "All HDE docs" is read as `docs/hde/pfcanon/`. I checked: that is the only HDE folder in glow-docs.
  - "Read-only" is not his word. The row gives its sources, D08 and `AGENTS.md`, so it says no more than the rules already did.
- **OD-75** restates option (a) of D-01, D-02, D-03, D-06 and D-07 as M09 wrote them.
  - A01-R comes after M07, as M09's own section 4.7 orders it ("M07, the costed list, and directly after it A01-R").
  - D-04 and D-05 wait for P08.3's brief.
- **The toggle.** OD-75's launch value (on) and the P11 plan's seeded value (off until a real check adapter exists) agree, because the seed is the development value. Two gaps remain:
  - **OD-68's row** still says "off at launch", with no mark. The register's practice is to mark the earlier row, as OD-61's says "partly superseded by OD-68". **AD3.**
  - **No record says who turns the toggle on, or when.** Without that, Nathan's decision has no owner, and a launch could ship with the seeded "off". **AD4** puts it in the P11 plan's line: once the real adapter passes on its target (P11B), staff publish the toggle on before the first real member, and the recheck worker then takes every photo approved while it was off.
- **Unchanged:** DM-52 section 16's open condition still governs the choice of service. It goes to Nathan in OD-32's form after the matrix's recheck. OD-75 sets the launch value, not the service.

## 5. Item 3 — D-06

**Approved with condition AD5.**

- **Your reading is right.**
  - "One such item runs at a time" fits D-06's wording, "a Markdown-only research or policy item", in the singular.
  - It is narrower than his words could bear, not wider, and he can widen it.
  - A full-scope result stops the item until its turn, which keeps OD-29 for code.
- **The bullet is sound:**
  - the trusted classifier's result is the test;
  - the item has its own brief, prompt, branch and message;
  - it shares no owned path;
  - its governing Markdown is still read before its pull request merges.
- **But "The process is linear" still blocks it.** Its third line says "The next one comes only after the current task's report is verified and recorded." With two items open, the Markdown item's prompt could not go out while the code item's task runs. The first line's exception does not reach this line. **AD5:** the order holds within each item.
- `AGENTS.md`'s sentence and the start procedure's line agree with the workflow.

## 6. Item 4 — D-07

**Approved with conditions AD6, AD7, AD8 and AD11.**

- **"Two reads per code item"** matches D-07 (a): the brief and the pre-merge read, plus the charter's triggers.
  - The charter's paragraph says "a case listed here". The workflow's version names cases in brackets, and the brackets leave out two of the charter's cases: new components, services or significant dependencies, and decisions with unclear trade-offs.
  - **AD6** makes the brackets examples, so the charter's list governs.
- **Your first choice: a missing test is a correction only at a security boundary.** Right in principle, but SV2-R's C1 is the wrong example.
  - **C1.1** tested the recheck's state condition. Without it, a photo approved while the toggle was off and then **restricted by staff** or **removed by its owner** would go back to the check, and an approving check would undo the staff decision or the owner's removal.
    - That is revocation and data ownership, both in the workflow's own list of security boundaries.
    - So C1.1 stays a correction, under your line and under D-07 (a) as Nathan accepted it.
    - Your reading shows the line can be read two ways. **AD7** names a staff restriction and an owner's removal in the list.
  - **C1.2** tested `run_check` on an approved photo. That behaviour is not at a boundary, but acceptance check 4 ("run_check behaves as before") rests on it.
    - A missing test that an acceptance check rests on leaves the check unproven. If the record claims the check, the claim is false, which D-07 already sends to correction.
    - **AD7** says so directly, so that an unmet acceptance check is never carried as a "limit".
  - **So C1 would still have run.** That is consistent with D-07. What D-07 carries is the reach of a scan or a guard, a test of behaviour the item does not change, and wording. C1 was none of these.
- **Your second choice: a fix that changes a security-boundary decision comes to me first, and one that applies it goes on the list.** The line is right.
  - Every fix is still read by the exact-head or delta review, and listed for the pre-merge read.
  - The risk is a fix judged "applies" that in fact moves a decision. **AD8** (the workflow) and **AD11** (PF02-R19) settle that case: a fix whose effect on a security-boundary decision is unclear counts as changing it.
- **M09's measure of this role is fair.** Each condition in this report corrects a text that would be false or contradictory, or would leave a decision with no owner. None of them adds a step.

## 7. Item 5 — PF02 1.8

**Approved with conditions AD10 to AD15, with AD11 from item 4. The deferred condition for 1.8 closes on this answer.**

- **Each fold-in, against its entry:**
  - **AM12-22 and AM12-24 into R14:** right in substance, but the sentence is garbled ("the tests that pin their plan or count, by line number or count"). **AD10** gives what DM-93 section 3.1 asked for: the tests that pin a plan, a count or a source line by number, and the records that state a count.
  - **AM12-23 and AM12-28 into R01, as repeats:** right. Both wrote a time before reading the clock.
  - **AM12-25 into R17, as a repeat of its check:** right. A Dev Manager note carried nowhere is what R17's check catches.
  - **AM12-26 into R30:** right. The new sentence is AM12-26's prevention.
  - **AM12-27 into section 7:** right. Git's own error caught it, with no effect.
  - **AM12-29 into R61:** right, and so is its citation: DM-57's U11 put the merge of `main` before the receipt.
  - **AM12-30 into R04 and R46, "as repeats": half right.**
    - R04 covers the wrong range of entries ("AM12-22 to AM12-28").
    - R46 covers plain words in a message to Nathan. The other two errors ("\$100 for life", and the DM-59 citation) were in the handoff, which R46 does not cover, so they are not a repeat of it.
    - **AD12 and AD13** extend R46 to the handoff's summaries. **AD14 and AD15** correct section 8 and the revision entry to match.
  - **R19 for D-07:** matches the workflow's text, with AD11.
- **The deferred condition closes.** My read of 1.8 is the pre-merge read of the pull request that carries it, if PF02's text at that pull request's final head equals `6bee2e9`'s with AD10 to AD15 applied. That is DM-91's form, and the pre-merge checklist confirms it.

## 8. Items 6 and 7 — `CLAUDE.md` and the CI policy

**Both approved.**

- **`CLAUDE.md`:** the sentence agrees with OD-74 and with the paths in glow-docs (`docs/hde/pfcanon/` and `docs/brand/`). Its limits are D08's and `AGENTS.md`'s, not new ones.
- **The CI policy:**
  - I searched every test, script and workflow for code that reads a Markdown file. Only `test_transition_contract.py` reads repository Markdown: lines 699 to 707 read one sentence of `docs/architecture/production-contracts.md`.
    - The Stream proof writes its own Markdown reports.
    - The classifier's tests write Markdown fixtures in a temporary repository.
    - No job lints or formats Markdown.
    - So "No other application check reads Markdown content" holds.
  - The gate sentence is DM-34 3.1's wording exactly.

## 9. Item 8 — M09's two proposals

- **(a) No row for a condition applied in my words: agreed.**
  - The check stays: the next consultation or the pre-merge read confirms the words, and the pre-merge checklist shows how. Only the row goes.
  - A condition that asks for an action, not words, keeps its row.
  - **AD9** words the charter's paragraph now, so it needs no read at my next consultation.
- **(b) The status log in a child page: agreed,** with three points:
  - every entry moves verbatim, checked by script as M09 checked its insertion: the characters removed equal the characters the child page gains;
  - the page keeps the current entry, with a link to the child page, and the Branches, Main and Mistakes log bullets;
  - the superseded full copy of the procedure moves the same way (M09's Appendix B, difference 31: 18,116 characters, due to move since 26 October).
  - No owner direction fixes the log's place. OD-53 S5 governs the guidance summary and the register copy only.

## 10. Item 9 — the sequence

**Agreed.**

- **The records batch:** your disposition, with AD1 to AD15 applied as given. Applied as given, they need no further read.
- **The pull request:** it merges once the review log's disposition covers its final head. Its pre-merge checklist shows that each governing file at that head equals `6bee2e9`'s text with the AD pairs applied, and the charter `ebf84e3`'s, so that this read stands as the pre-merge read.
- **Notion:** your step 4 after the merge, and the five corrections in section 11, none of which waits for the merge.
- **M07:** its prompt went to Nathan at his request (`d435f96`, at `f1653f1`), before this answer.
  - M09's CI and review were clear, so OD-29 allows it.
  - Its prompt authorizes no credential use and no live provider action, so it needs no read of mine.
  - D-06 is not needed for it, since no code item is open.

## 11. Item 10 — Notion (read-only, from about 01:05 UTC)

Notion's SQL query allowance ran out during the read. I read the Work Register's 93 rows through its default view instead, so the comparison is complete.

| Page | What I compared | Result |
|---|---|---|
| Implementation Control, status | Entries at `6bee2e9` ("DM-94 with Nathan") and `ebf84e3` (OD-76), each as the commit has it | **Match** |
| Its procedure summary | Links at `ebf84e3`, moved for the charter's OD-76 sentence, with `6bee2e9` and `561dbc3` before it (PF02-R12) | **Match** |
| Its M09 sentence in "Next items" | Present, as section 10.2 describes it | **Match** |
| Its Branches bullet | Listed at 22:59 UTC on 18 November: three branches, with the manager branch at `964d38a`. At `6bee2e9` the handoff names four, with M09's `claude/nifty-euler-3v8sl7`. `git ls-remote` at 01:12 UTC: `main` `6edae78`, the manager branch `d435f96`, `claude/dev-manager` `adb769d`, `claude/nifty-euler-3v8sl7` `20a0d99` | **Mismatch:** the manager branch has moved six commits since `964d38a` (three of them by `6bee2e9`), and the bullet has not moved (PF02-R05) |
| Its Mistakes log bullet | "AM12-01 to AM12-29, at `4e01cd7`". The log holds AM12-30 at `6bee2e9`, and AM12-31 at `ebf84e3` | **Mismatch** |
| The register copy | Its 76 rows match `ebf84e3`'s register, apart from the same eleven presentation-only differences as at DM-93 (seven in link text, four in Notion's escaped `$`). Its header still says "Matched ... at commit `4e01cd7` ... (OD-72 added)" | **Mismatch:** the header only |
| Dev Manager page | DM-93 considered (merge `d8e76e2`; ZZ1 to ZZ4 as revision 6; the prompt's revision 2). **No DM-94 row.** The page was last edited on 18 November at 17:08 UTC, and the review log has DM-94's row | **Mismatch** |
| Work Register: M09's 32 field changes on 24 rows (section 10.2) | 27 exactly as listed. P07.3, P10.1, A01 and A07 carry the quoted text. SV4's new paragraph is 841 characters without its link's address, as listed, and the earlier 821 characters are unchanged | **Match** |
| The six new rows | A01-R, SV5, SV2-L, AC1, AC2 and AC3: Planned, Task, Cross-cutting, Autonomous, Plan Reference at `b738529`, Depends On as listed | **Match** |
| M09, SV2-R, A01 and M07 | M09 Done, its evidence at `561dbc3`; SV2-R Done; A01 Blocked, with A01-R first; M07 In progress, its plan at `f1653f1`, as `d435f96` has it | **Match** |
| P07.1 (and A05) | P07.1's Depends On still names "Nathan's decisions on what checks a photo and on CSAM detection (... D-03 and D-08)" as open, and A05's says "D-03 and D-08 bear on P07.1". OD-75 decided D-03 (a); what remains at P07.1 is the service and D-08's tool | **Mismatch** |

## 12. After the read commit: `ebf84e3`

- **The charter's sentence for OD-76:** "He confirmed the rule on 19 November 2026, answering DM-01 question 2: *"keep the Dev Manager read"* (OD-76). It applied until then under DM-03 G1." It quotes OD-76's words exactly. **Approved,** read at `ebf84e3`, so it rides in this pull request with no further read.
- **OD-76's row** is faithful to his words. Its finding on the AWS names agrees with every environment check I have run: the names are present and have never been read.
- **AM12-31** names PF02-R68. It folds in at the next revision, for my next read.
- **D-18** is answered (OD-76), so the M09 record's disposition rows at `ebf84e3` are right.

## 13. The words

**AD1 — GAPP-PF01, `docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md` (yours): §10, A04: the photo check is chosen (OD-75).**

> ```
> the photo and CSAM checks if chosen,
> ```

> ```
> the photo check and hash matching for known child sexual abuse material (OD-75, D-03 (a)),
> ```

**AD2 — GAPP-PF01, `docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md` (yours): the 1.19 entry: §7's Media paragraph after D-03.**

> ```
> §7's "Media" paragraph against OD-68, which waits for his decision on what checks a photo before it is shown;
> ```

> ```
> §7's "Media" paragraph, which needs no change, since it already requires moderation before publication and Nathan's answer to D-03 (OD-75, 19 November 2026) puts the automated photo check on at launch, with hash matching for known child sexual abuse material;
> ```

**AD3 — the register, `docs/continuity/owner-directions.md` (yours): OD-68's status: partly superseded by OD-75.**

> ```
> | In force. **For the MVP, no selfie is matched to a government ID**
> ```

> ```
> | In force, **partly superseded by OD-75** (the automated photo check on at launch, D-03 (a)). **For the MVP, no selfie is matched to a government ID**
> ```

**AD4 — the P11 plan, `docs/testing/p11-deferred-acceptance.md` (yours): SV2-R carryforward, the launch default: who turns the toggle on, and when.**

> ```
> The seeded value stays off until a real check adapter exists, since with the toggle on every new photo waits for the check; the service is chosen with D-08 at P07.1 and costed in M07.
> ```

> ```
> The seeded value stays off until a real check adapter exists, since with the toggle on every new photo waits for the check. Once that adapter passes on its target (P11B), staff publish the toggle on before the first real member, and the recheck worker then takes every photo approved while it was off; the service is chosen with D-08 at P07.1 and costed in M07.
> ```

**AD5 — the manager workflow, `docs/planning/manager-workflow.md` (yours): "The process is linear": the order within each item (D-06).**

> ```
>   - That prompt is for the next task not recorded as complete. The next one comes only after the current task's report is verified and recorded.
> ```

> ```
>   - That prompt is for the next task not recorded as complete. The next one comes only after the current task's report is verified and recorded. With a Markdown-only item beside a code item, this order holds within each item.
> ```

**AD6 — the manager workflow, `docs/planning/manager-workflow.md` (yours): "Two reads per code item": the charter's list governs.**

> ```
> goes to it only when its charter names the case (a design decision or a design blocker,
> ```

> ```
> goes to it only when its charter names the case (among them a design decision or a design blocker,
> ```

**AD7 — the manager workflow, `docs/planning/manager-workflow.md` (yours): "What a correction pass is for": the boundary's examples, and a missing test an acceptance check rests on.**

> ```
> a defect at a security boundary (authorization, revocation, privacy, data ownership or the protected HDE boundary), or a false claim that a decision or the merge would rest on. A review prompt's correction classes are drawn from those three. A missing test of the item's own behaviour is a correction only when that behaviour is at a security boundary.
> ```

> ```
> a defect at a security boundary (authorization, revocation, privacy, data ownership or the protected HDE boundary, a staff restriction and an owner's removal included), or a false claim that a decision or the merge would rest on. A review prompt's correction classes are drawn from those three. A missing test of the item's own behaviour is a correction only when that behaviour is at a security boundary or an acceptance check of the item's brief rests on it.
> ```

**AD8 — the manager workflow, `docs/planning/manager-workflow.md` (yours): "Fix or carry, by rule": an unclear case counts as a change.**

> ```
> Any other fix is listed for the pre-merge read (OD-75, D-07).
> ```

> ```
> Any other fix is listed for the pre-merge read (OD-75, D-07). A fix whose effect on a security-boundary decision is unclear counts as changing it.
> ```

**AD9 — the charter, `docs/planning/dev-manager.md` (yours): "A read covers one commit": no row for a condition applied in the Dev Manager's words (M09 8.1, proposal 1).**

> ```
> The primary manager lists those changes in the disposition, and the next consultation or the close-out read confirms them.
> ```

> ```
> The primary manager lists those changes in the disposition and on the pre-merge read's list, and the next consultation or the pre-merge read confirms them. A change that applies the Dev Manager's own words takes no row of its own among the deferred conditions (M09, section 8.1).
> ```

**AD10 — GAPP-PF02, `docs/pf-canon/GAPP-PF02-Manager-Practice-Rules.md` (yours): PF02-R14: the earlier-tests sentence, made plain.**

> ```
> Before a brief says what earlier tests do, read the tests, the proof cases and the tests that pin their plan or count, by line number or count, for every behaviour, setting or case it changes or adds, name those expected to change, and name the records that state a count it changes.
> ```

> ```
> Before a brief says what earlier tests do, read the tests and the proof cases for every behaviour, setting or case it changes or adds, and the tests that pin their plan, their count or a source line by number; name those expected to change, and the records that state a count it changes.
> ```

**AD11 — GAPP-PF02, `docs/pf-canon/GAPP-PF02-Manager-Practice-Rules.md` (yours): PF02-R19: an unclear case counts as a change.**

> ```
> or when a charter trigger applies; any other fix is listed for the pre-merge read.
> ```

> ```
> or when a charter trigger applies; any other fix is listed for the pre-merge read, and a fix whose effect on a security-boundary decision is unclear counts as changing it.
> ```

**AD12 — GAPP-PF02, `docs/pf-canon/GAPP-PF02-Manager-Practice-Rules.md` (yours): PF02-R46, its rule: the handoff's summaries (AM12-30).**

> ```
> and give each option what it is, what it costs, what it closes and what stays open.
> ```

> ```
> and give each option what it is, what it costs, what it closes and what stays open. A summary written into the handoff keeps each definition, citation and range as its record states it.
> ```

**AD13 — GAPP-PF02, `docs/pf-canon/GAPP-PF02-Manager-Practice-Rules.md` (yours): PF02-R46, its check.**

> ```
> - **Check:** each option in the message carries the four lines; each figure traces to a record line.
> ```

> ```
> - **Check:** each option in the message carries the four lines; each figure traces to a record line; each definition, citation and range in the handoff traces to its record.
> ```

**AD14 — GAPP-PF02, `docs/pf-canon/GAPP-PF02-Manager-Practice-Rules.md` (yours): section 8, the 1.8 fold-in: AM12-30.**

> ```
> AM12-30 into R04 and R46 as repeats.
> ```

> ```
> AM12-30 into R04 as a repeat, and into R46, which gains a sentence on the handoff's summaries.
> ```

**AD15 — GAPP-PF02, `docs/pf-canon/GAPP-PF02-Manager-Practice-Rules.md` (yours): section 9, the 1.8 entry.**

> ```
> R14, R30 and R61 gain the additions their entries set, with check lines covering them.
> ```

> ```
> R14, R30, R46 and R61 gain the additions their entries set, with check lines covering them.
> ```

## 14. Who applies what

- **You, in the records batch:** AD1 and AD2 (PF01); AD3 (the register); AD4 (the P11 plan); AD5 to AD8 (the manager workflow); AD9 (the charter); AD10 to AD15 (PF02). Then the five Notion corrections in section 11.
- **The deferred condition for PF02 1.8:** closed by this answer, on the terms in section 7.
- **I read next:** this read stands as the pre-merge read if the final head carries the AD pairs as given. My next read is the next governing change, such as AM12-31's fold-in. Moving the status log needs no read.

Status: complete
