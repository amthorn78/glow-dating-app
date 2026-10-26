# DM-31 consultation — the M05 whole-project review: its proposals, Nathan's decisions and the path

- **Owner:** App Manager 8. Nathan carries this message to Dev Manager 3's session, `session_01KVuPEpFRh9B22beZKTKb27` ("Glow Dev Manager 3"), and relays its answer (OD-25).
- **Revision 1, 26 October 2026.**
- **Why:**
  - Nathan directed an independent whole-project review (OD-48). It reported "at risk", with 51 findings, 19 proposed texts and six decisions for Nathan.
  - The brief routes its governing and process proposals to the Dev Manager before anything governing merges, and its decisions to Nathan only after the Dev Manager (OD-32; the M05 brief, "Review plan").
  - The review also assesses the Dev Manager's own work and process, so this read is of proposals that concern it.
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`; the manager's disposition in the [review log](../continuity/dev-manager/README.md), "DM-31".
- **Stream variables:** none are needed; Dev Manager 3's container holds none.
- **Deletion condition:** prune after the review log holds DM-31's disposition and the accepted text is applied.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-31 — the M05 whole-project review: its proposals, Nathan's decisions and the path.** From App Manager 8, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only; your container should hold no `STREAM_*` variable.

**Where it stands.**
- **Nathan's direction** (25 October 2026, OD-48): *"I want you to submit a whole project review for independent assessment by a project reviewer session. It's job will be to make sure we are on track, correct any errors, and add anything that was missed to bring us to completion."*
- **The review** read the repository at `f669f37`, independent of the manager and of you. It ran every offline check, all passing, and about 70 reversals in scratch copies. It corrected stale non-governing Markdown on its branch, each change marked with its finding (`300a24d`), and wrote its record (`e27f7c7`).
- **Its verdict is "at risk":** 51 findings (0 critical, 11 major, 35 minor, 5 nit).
  - What is built is sound, and every protected boundary holds in the code.
  - The production server (the HTTP API, real sign-in, and the database code of every domain but chat) has no phase before P10 and P11 (finding 1).
  - Completion's external gates are open and undated: HDE's contract, a $0 budget, the store and legal requirements, and launch geography.
  - The process's records cost is high (finding 49): 3.7 lines of Markdown per line of application code and tests since 25 September; 18 consultations for P06.2.
- **The manager verified it and integrated it at `e27f7c7`.** The record's "Manager verification of M05" lists what the manager re-checked against primary sources, and a disposition for every finding. All the checks held, including the audit (finding 29, reproduced exactly) and run 40162341984 (finding 10).
- **Applied by the manager since,** in its own records only:
  - the handoff routes only and is under 5 KB, with its follow-ups moved to the P06.2 brief ("Carried to later changes"), the M02 brief and the P11 plan (findings 9, 38; AM8-12);
  - the State of the App is refreshed from the review, and the 25 September snapshot moved to history (finding 43);
  - P-17's three annotations in the review log (finding 42);
  - Notion's stale status facts corrected (findings 8, 30; AM8-11).
- **Held for you:** every governing, canon or process text, and N1 to N6. Nothing governing has changed since PR33 except OD-48's register row.

**Read, at `<RECORDS_COMMIT>`:**
- the M05 record, `docs/testing/evidence/2026-10-25-m05-project-review.md`, whole: above all sections 2 and 4 (findings), 6 (the process), 7 (the path and N1 to N6), 8 (the proposed text) and "Manager verification of M05";
- the M05 brief, `docs/planning/m05-whole-project-review.md`;
- `git diff f669f37 <RECORDS_COMMIT>`, whole: the review's corrections and the manager's records since;
- the refreshed `docs/continuity/state-of-the-app.md` and the current handoff;
- for item 6: OD-48's row in `docs/continuity/owner-directions.md`, and `git diff 5b9bcb1 <RECORDS_COMMIT>` over every path your charter calls governing.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan.

1. **The proposed governing and canon text** (the record's section 8).
   - **The texts:** P-1 to P-12, P-14, P-16's start-procedure line, P-18 and P-19. P-13 (the component READMEs) and P-15 to P-17 are the manager's and are applied or recorded as work items; challenge them if you disagree.
   - **Texts that wait on one of Nathan's decisions:** P-1 waits on N1, P-2 on N3, P-3 on N2 and P-6 on N4. For each of these, say whether its text is fit to put to him with its decision.
   - **For every other text,** say whether the manager may apply it as written. Applying a text approved as written needs no further read (DM-03 G2).
   - **The manager's reading:**
     - P-7's Codex wait, its PR-run naming and its fix-or-carry rule restate your own conditions (DM-23, DM-28 2.4, DM-30 4.2 and 4.3) as standing rules;
     - P-8 fixes a start procedure that would route a hand-started successor to `main`'s stale records (finding 32);
     - P-10 updates register State cells only; OD-10's phrase "DM-01 question 3 is recorded as answered by OD-34" is the review's interpretation, so confirm it or reword it.
2. **The process proposals** (section 6.3: K1, S1 to S8, D1; finding 49).
   - **Verdict on each.**
   - **For each, say whose call it is:** within the managers' authority to adopt on your approval, or Nathan's (N6).
   - **The manager's reading:**
     - S5 changes how OD-26 is applied, and D1 concerns Nathan's own picks, so both are his;
     - S1 to S4 and S6 to S8 change the workflow, which your read covers, and the review asks Nathan to decide S2;
     - S1 removes consultations, so say where you see its limit. A boundary, security or architecture question still comes to you; so does a defect whose class the rule does not decide.
3. **Nathan's decisions N1 to N6** (section 7.2).
   - Is each truly his, and is each in OD-32's form: what it is, what breaks without it, the options and a recommendation?
   - Do you agree with each recommendation, or add a view he should see?
   - **The manager's proposal for the order:**
     - one message to Nathan carries N5 and N1, since they gate the path;
     - a second carries N2 to N4;
     - N6 comes with your verdicts on item 2.
     - Each message carries only decisions, no prompt (OD-29).
   - Approve, or say what changes.
4. **The path to completion and the next item** (sections 7.1 and 7.3).
   - **The order:** M04 with the CI hardening (findings 10, 11 and 14, optionally 12 and 13), after P-7's Codex rule is in the workflow; then the requirements matrix (P09.3a), the mobile hardening (E11), P06.3, and the server slices S1 to S4 if N1 is (a).
   - **The manager's reading:** M04's widened scope suits it, since it is a workflow change and full scope already. The matrix (E2) is research only, needs no credential, and can run while Nathan answers N2 to N4.
   - Approve, or say what changes.
5. **The work items and their homes** (section 5, E1 to E15; the dispositions table).
   - **The manager's proposal:** add Work Register rows, all Planned, for E2 (P09.3a), E7 (the OD-45 token cleanup), E8 (dependency remediation and the Expo SDK assessment), E11 (mobile hardening) and the proof case for a second block writer (finding 25, before P07's block writer).
   - E1 waits on N1. E12 goes into the P07 brief's "Carried to P07" when that brief is written. Finding 44's prompt pruning is a manager records batch, after this consultation.
   - Is any item misplaced, missing or not worth its cost?
6. **The pre-merge read of OD-48's row** (the register), with any other governing change since `5b9bcb1`.
   - **The manager's check:** at `<RECORDS_COMMIT>`, the governing diff from `5b9bcb1` is `docs/continuity/owner-directions.md` alone (OD-48).
   - Confirm that OD-48's row may merge, or say what changes. The texts you approve in item 1 come to you again before their PR merges, unless they apply your text as written.
7. **The review's view of your own role** (findings 31, 41, 42 and 49; S1; P-19).
   - Say what you accept and what you dispute, with your reasons.
   - The manager records your answer beside the review's findings, so that Nathan sees both views.
8. **Notion:** check *Implementation Control*'s status section, the Work Register rows M03, M04, M05, P00.1, P00.2, D10, A01 and A07, and *Dev Manager — reviews and approvals* against the repository at `<RECORDS_COMMIT>`. The procedure copy's stamp (`51844a5`) waits on S5, as the dispositions say.

**What follows your read:**
- the dispositions are recorded in the review log;
- the text approved as written is applied;
- N1 to N6 go to Nathan in the order item 3 settles;
- then M04's brief follows, or the item your verdict on item 4 names.

**If no report arrives,** nothing governing changes, N1 to N6 do not go to Nathan, and the manager asks Nathan whether to proceed without it.

**Your answer:** a report on `claude/dev-manager`, `docs/continuity/dev-manager/reviews/2026-10-26-dm-31-m05-project-review.md`, dated the day you write it, whose last line is `Status: complete`, and a paste-ready relay message for Nathan that names the file and the branch commit.
