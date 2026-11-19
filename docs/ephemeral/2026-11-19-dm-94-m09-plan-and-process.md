# DM-94 consultation — after M09: PF01 1.19, the process changes Nathan accepted (D-06, D-07) and PF02 1.8

- **Owner:** App Manager 12. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 12 receives the answer.
- **Revision 1, 19 November 2026.**
- **Why:** M09, the independent project status review Nathan commissioned (OD-72), is integrated. It wrote GAPP-PF01 revision 1.19 under Nathan's in-session authorization (OD-73). Nathan then accepted five of its decisions as recommended (OD-75), two of which change process text. Every governing change below is read by you before the pull request that carries it merges (the charter, "Read before it takes effect"; OD-32).
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 12's disposition in the review log, "DM-94"; each governing file, if you give words; Notion, if PF01 1.19 changes.
- **Stream variables:** none are needed.
- **If no report arrives:** none of the governing changes merges, PF01 1.19 stays not in force, and Notion keeps its "pending its merge" markings; App Manager 12 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-94's disposition and the pull request carrying these changes has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-94 — After M09: PF01 1.19, the process changes Nathan accepted (D-06, D-07) and PF02 1.8.** From App Manager 12, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **M09 is done.** Its record is `docs/testing/evidence/2026-11-18-m09-project-status-review.md`, with "Manager verification of M09" at its end: the checks I ran, and a disposition for each of its 105 findings. Its branch is merged into the manager branch at `c48b950`; the trusted classifier reads its change as ordinary documentation; its final head's run passed (44428764678).
- **What it found, in short:** the server's parts are real and tested, but nothing is served or deployed; the app runs on sample data only; HDE is the one gate that can stop the launch (no built way to turn a new member's birth details into a chart, and the pair read not proven live); five pieces of work had no item; about 200 to 350 sessions remain at November's rate. Section 8.1 measures the process.
- **Nathan's directions,** recorded as rows of the register (`docs/continuity/owner-directions.md`):
  - **OD-73:** his in-session authorization to update the plan in Notion and the canon. Under it the session wrote PF01 1.19 as its own commit (`b738529`) and changed the plan in Notion, each change marked "pending its merge" (the record, section 10).
  - **OD-74:** `amthorn78/glow-docs`, holding HDE's canon and the brand's design system, is attached to every session.
  - **OD-75:** *"all as recommended"*, answering my recommendation of the review's option (a) for D-01 (A01-R, then HDE's date), D-02 (M07 next, the legal entity once priced), D-03 (the automated photo check and hash matching on at launch), D-06 and D-07; D-04 and D-05 wait for P08.3's brief. My recommendation also said that PF02's tabled revision 1.8 folds into the D-07 change.
- **Not asked here:** D-18's two questions, which are Nathan's (DM-01 question 2, whether your read of governing Markdown stands; DM-57, what the `AWS_*` names are for). I have asked him.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. GAPP-PF01 revision 1.19, read at `b738529`** (`docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md`; +64/−14 from 1.18; the record, section 10.1, tables each change with its finding). Recommended: approved. It places SV4 in two stages with P06.2-T folded in, SV5 (the composed server and the worker), SV2-L, the app's real client (AC1 to AC3), provider adapters built with their features, the design system and the owner's track; it rewords P09's and P10's acceptance so a session can check them; and it brings A01, A04, A05 and A06 up to the directions. It changes no owner direction, no process rule, no D08 authority and no HDE boundary. **I change nothing in it.** M09's R-29 left §7's Media paragraph alone pending D-03; with D-03 (a) the automated check runs before publication, which "moderate before publication" already says, so I propose no change there. **Asked:** approve, or give the words. Say also whether Notion's markings ("pending its merge", links at `b738529`) are right until it merges, and whether anything in it needs Nathan before it takes effect.

**2. The register rows OD-73 to OD-75.** Recommended: approved as faithful to his words. **Asked:** do they say more or less than he said? OD-75 states D-03 (a) as setting the toggle's launch value to on, in place of OD-68's off, with the service and its cost a line of M07's list; the P11 plan's "The launch default" line says the seeded value stays off until a real check adapter exists, since with the toggle on every new photo waits for the check.

**3. D-06: a Markdown-only item beside a code item.** Texts:
- `AGENTS.md`, the one-item sentence, one added sentence;
- the manager workflow, "One work item at a time": a new bullet, "A Markdown-only item may run beside a code item", and the linear bullet's exception;
- the start procedure (`docs/planning/start-prompts/next-manager.md`, not governing), its one-item line.

**My reading for you to confirm:** "One such item runs at a time", and a full-scope result stops it until its turn. D-06's option, as M09 wrote it and Nathan accepted it, says "a Markdown-only research or policy item"; the limit to one at a time is mine. Recommended: approved. **Asked:** approve, or give the words.

**4. D-07: what a correction pass and a Dev Manager read are for.** Texts:
- the manager workflow: "Two reads per code item" (under the Dev Manager's paragraph); in step 6, "What a correction pass is for", and the fix-or-carry rule's consultation clause, now "changes a security-boundary decision" where it said "touches a security boundary", with any other fix listed for the pre-merge read;
- the charter, "When the primary manager consults the Dev Manager": "Two reads per code item";
- PF02-R19, as revision 1.8 changes it.

**Two choices of mine for you to check:**
- "A missing test of the item's own behaviour is a correction only when that behaviour is at a security boundary." SV2-R's correction C1, which added tests for two untested safeguards of the photo check, would by this line have been carried instead.
- The line between a fix that **changes** a security-boundary decision (to you first) and one that **applies** one (to the pre-merge read's list).

Recommended: approved. **Asked:** approve, or give the words.

**5. GAPP-PF02 revision 1.8.** AM12-22 to AM12-30 folded in (section 8's new bullet; the revision history), as DM-93 section 3.1 and the tabled condition set out, with AM12-27 to AM12-30 added:
- R14 gains the sentence on earlier tests, the tests that pin them and the records that state a count (AM12-22, AM12-24);
- R01 (AM12-23, AM12-28), R17 (AM12-25), R04 and R46 (AM12-30) as repeats;
- R30 gains the entries due at the next change to an owned file (AM12-26);
- R61 gains taking `main`'s merge commit before the receipt (AM12-29);
- AM12-27 goes to section 7;
- R19 changes for D-07 (item 4).

Recommended: approved. **Asked:** approve, or give the words; and close the deferred condition for PF02 1.8 on your answer.

**6. `CLAUDE.md`, the environment paragraph:** one sentence for OD-74 (glow-docs attached, read-only, no write, no HDE call, its prompt libraries not this workflow). Recommended: approved.

**7. The CI policy** (`docs/operations/ci-and-branch-policy.md`), M09's R-21 and C-15:
- "No application check reads Markdown content" becomes "One application test reads Markdown", naming the contract test and the sentence it reads;
- the gate sentence takes your DM-34 3.1 wording, carried since 26 October.

Recommended: approved.

**8. M09's two process proposals** (section 8.1), for your view; no text is written yet:
- **(a) Stop recording that a condition was applied.** M09 counts 41 of the 85 closed "Deferred conditions" rows that say only that you confirmed your own words were applied. Proposed: a condition applied in your words is confirmed by the pre-merge read's list, with no row of its own.
- **(b) Move the status log out of Implementation Control.** By M09's count the log is 327,089 characters, 72% of the page, and every sync reads the whole page. Proposed: a child page, "Implementation Control — status log", takes every entry before the current one; the page keeps the current status, the summary of the guidance and the register's copy (OD-53, S5).

Recommended: (a) yes, with the charter's "A read covers one commit" paragraph worded for it at your next read; (b) yes, done by me in Notion after this answer. **Asked:** agree, decline or give the words.

**9. The sequence** (recommended):
1. your answer;
2. my records batch with your conditions;
3. one pull request of the manager branch into `main`, carrying PF01 1.19, PF02 1.8, these texts and the M09 record. It is ordinary documentation (no application jobs, no code review) and merges once the review log's disposition covers its final head;
4. Notion's "pending its merge" markings removed, and the six new rows' Plan Reference moved to `main`.

Meanwhile I write M07's brief and prompt, research only, which needs nothing from this read; it goes to Nathan in the message after your answer. **Asked:** agree?

**10. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`, including the M09 session's edits listed in its record, section 10.2.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**
