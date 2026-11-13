# Manager mistakes log

Nathan's direction, 25 September 2026: *"I also want you to track your mistakes."*

Each Claude manager records its own mistakes here when they are found. A mistake can be found by Nathan, a reviewer, a check, a tool's guard or the manager itself. Each entry says what happened, what caught it, its effect, the correction and what prevents a repeat. The log is part of the record of this high-trust experiment. It does not replace the evidence records.

**Adding an entry**

- Add the entry when the mistake is found, in the same change as its correction where possible, and add a row to the summary.
- Number entries per manager: `AM2-01`, `AM3-01`, and so on.
- Choose one kind:
  - **process:** departed from the plan or the manual-relay process;
  - **accuracy:** a wrong statement in a prompt, record or report;
  - **follow-through:** a commitment not kept;
  - **execution:** a wrong command or tool use.
- Record what actually happened, including who caught it. Never soften an entry or leave one out.
- **Every mistake gets a summary row. A full section is needed only when the mistake reached a record, a prompt, Nathan or `main`** (DM-01 P8, 25 September 2026). A slip that its own tool caught, with no effect, needs only its summary row.
- **A repeated prevention becomes a checklist item.** When a mistake repeats one already logged, move its prevention into a checklist the manager actually runs, such as the manager workflow or a start prompt, and say where in the entry.

## Summary

| ID | Date | Kind | Mistake | Caught by |
|---|---|---|---|---|
| AM2-01 | 24 Sep 2026 | accuracy | M02-I1 prompt said downloads work in a clean `env -i` process; true for curl, not npm | M02-I1 implementer |
| AM2-02 | 24 Sep 2026 | accuracy | M02-I1 prompt prescribed a bare `npx expo install`, which the config guard rejects | M02-I1 implementer |
| AM2-03 | 24 Sep 2026 | execution | Ran the pin test with `python3.12 -I`, which cannot import it | App Manager 2 |
| AM2-04 | 24 Sep 2026 | accuracy | M02-C1 prompt body pointed to sections named only in its unpasted header | App Manager 2, before giving the prompt to Nathan |
| AM2-05 | 24 Sep 2026 | execution | Did not capture the send time of the delta review's TypeSafe request | App Manager 2 |
| AM2-06 | 24 Sep 2026 | process | Merged PR18 three seconds after marking it ready; Codex's automatic review found a P2 after the merge | App Manager 2, reading PR18 during the close-out |
| AM2-07 | 25 Sep 2026 | follow-through | Promised to deal with the old session branches after M02 merged, then did not | App Manager 2, while compiling this log |
| AM2-08 | 25 Sep 2026 | process | Handed over a work queue of its own instead of the plan's next step, the P06.1 proposal | Nathan |
| AM2-09 | 25 Sep 2026 | process | The next-manager start prompt left PF00, PF01 and the Claude handoff out of the required reading | App Manager 2, while fixing AM2-08 |
| AM2-10 | 25 Sep 2026 | process | Tried to run the Setup script by hand in the manager session instead of handing over to a new session | Tool permission guard, then Nathan |
| AM2-11 | 25 Sep 2026 | execution | Three Notion slips: a bare `.md` filename became a broken link, an update's match text omitted link markup, and a status block called current policy "history" | App Manager 2's readbacks |
| AM3-01 | 25 Sep 2026 | execution | A Notion readback query passed a bare property filter where the tool requires a group, and failed validation | The Notion tool's input validation |
| AM3-02 | 25 Sep 2026 | follow-through | Pushed records that did not recommend ultracode for the I1 review, although the manager had committed to recommend it if the scorer flagged it, and the scorer did | App Manager 3, while syncing Notion |
| AM3-03 | 25 Sep 2026 | execution | Ran the trusted classifier with `--head HEAD` instead of a SHA; it failed closed | The classifier's fail-closed output |
| AM3-04 | 25 Sep 2026 | execution | Bare Python module filenames in a Notion row became broken web links, the AM2-11 slip with `.py` | App Manager 3's readback |
| AM3-05 | 25 Sep 2026 | process | Named the I1 review head, then changed the review prompt in a later commit, so the text Nathan received was not the prompt at the named head | The Dev Manager (DM-01 P2) |
| AM3-06 | 25 Sep 2026 | accuracy | Wrote the Dev Manager read into the governing documents as in force, while its disposition said it awaited Nathan | The Dev Manager (DM-03 G1) |
| AM3-07 | 25 Sep 2026 | accuracy | Recorded Nathan's principle as conditional on the I1 review along with the display rule, and left ADR 0003's interim safeguard out of PF01 | The Dev Manager (DM-03 G3, G4) |
| AM3-08 | 25 Sep 2026 | accuracy | Two consistency slips in one batch: the brief both granted and excluded `.github/`, and freezing the Claude handoff left two operations pages citing its inventory as current | The Dev Manager (DM-03 E1, E2) |
| AM3-09 | 25 Sep 2026 | follow-through | Revised PF00 and PF01 several times without updating Notion's operating procedure, which still cited PF00 1.4 and PF01 1.5 | The Dev Manager (Notion operational-guidance note) |
| AM3-10 | 25 Sep 2026 | accuracy | Applied ADR 0004 in some documents and missed six others that still stated the superseded same-logical-database preference as current | App Manager 3, while writing the HDE contract request |
| AM3-11 | 25 Sep 2026 | process | Planned the I1 review and the flake diagnosis to run side by side, and in chat offered Nathan a second prompt while he was starting the first, pointing him to an earlier message for it | Nathan |
| AM3-12 | 25 Sep 2026 | accuracy | Told Nathan the I1 review was running, and later the only task running, when he had not started it | Nathan |
| AM3-13 | 26 Sep 2026 | accuracy | Recorded in ADR 0003's Context and the brief, as established, that the other member receives S15's text in `member.updated` events; I1's harness could not show which event carried it | The exact-head review of I1 (finding 4) |
| AM3-14 | 26 Sep 2026 | execution | Ran the trusted classifier with a short base SHA; it answered `missing-or-invalid-comparison`, and the re-run with full SHAs gave `ordinary-docs-only` | The classifier itself |
| AM3-15 | 26 Sep 2026 | accuracy | The handoff's "Branches" section kept saying that every other remote branch was merged into `main` after the I1 and flake session branches were integrated only into PR26 | App Manager 3, checking branches for C1's integration |
| AM3-16 | 26 Sep 2026 | accuracy | The C2 prompt told the session that RT2 and RT3 HOLD on a `feature` refusal, copying the C1 review's suggested fix without checking it against the brief's matrix quality rule and the harness's own verdict for a feature refusal | C2's own review sub-agent, reported by the C2 session |
| AM3-17 | 26 Sep 2026 | process | Did not tell Nathan that the manager's own container still held the three `STREAM_*` variables after OD-28 limited them to sessions that call Stream. The manager never read or used them | App Manager 3, checking variable names while verifying C2 |
| AM3-18 | 26 Sep 2026 | accuracy | Told Nathan, and wrote in Notion, that all 99 of C2's fix reversals were demonstrated, from the script's summary alone; one reversal failed only because its edit broke the file's syntax | The exact-head review of C2, finding 3 |
| AM3-19 | 26 Sep 2026 | accuracy | The DM-04 consultation told the Dev Manager that the Stream variables were not set for its read, and the records said "No Stream variables"; its container, started before OD-28, holds them, as AM3-17 had found for the manager's own | The Dev Manager, DM-04 finding 10 |
| AM3-20 | 26 Sep 2026 | accuracy | Told Nathan that TypeSafe "only scores the level and can't pick a model". Its Choice questions can pick one, and the v4 request already asks one | Nathan |
| AM3-21 | 27 Sep 2026 | accuracy | A Notion usage-log row said the manager had corrected nit 6's line reference in the I2a review; the evidence record keeps that reference | App Manager 3, re-reading the row |
| AM3-22 | 26 Sep 2026 | accuracy | Recording the I1 review's confirmation of S15, updated OD-14's row and ADR 0003 but left PF01 §7 calling the display rule "conditional on the exact-head review confirming S15". Recorded by App Manager 5 | Dev Manager 2, DM-07 finding 1.2 |
| AM3-23 | 25 Sep 2026 | accuracy | The Work Register row M03 kept "The Dev Manager's ten questions are with Nathan." after Nathan answered them. Recorded by App Manager 5, which had corrected M03's links on 28 September without reading that text | Dev Manager 2, DM-07 finding 8 |
| AM4-01 | 27 Sep 2026 | process | The first report to Nathan listed two standing items as "waiting on you" without saying what they were or what he could do; he would not send the I2b prompt while they stood | Nathan |
| AM4-02 | 27 Sep 2026 | process | Asked Nathan to pick a model and level for I2b when the manager's call and TypeSafe's readings were the same | Nathan |
| AM4-03 | 27 Sep 2026 | process | Scoring requests too thin for an informed reading: one line per level, no facts about cost or capability on either model | Nathan |
| AM4-04 | 27 Sep 2026 | process | Overrode Nathan's six-rung ladder, left max unreachable, and presented the manager's own model judgement as a recommendation | Nathan |
| AM4-05 | 27 Sep 2026 | accuracy | Two slips in the handover records: the start procedure said its placeholders were filled in, and AM4-03 and AM4-04 had no summary rows. Recorded by App Manager 5 | App Manager 5, reading the handover commit |
| AM4-06 | 27 Sep 2026 | accuracy | The verification of I2b repeated I2b's underivable "the plan's eleven" in its own disposition, and did not flag I2b's mypy count of 55 although its own run printed 53. Recorded by App Manager 5 | The exact-head review of I2b (nits 5 and 6) |
| AM4-07 | 27 Sep 2026 | accuracy | Integrating I2b, which added the fifth application job, updated the CI policy's counts but left the build-and-deploy runbook's "All four must pass". Recorded by App Manager 5 | App Manager 5, in its supersession sweep for P06.DB's sixth job |
| AM5-01 | 27 Sep 2026 | execution | Ran the trusted classifier with a short base SHA while checking its own records batch; it answered `missing-or-invalid-comparison`, and the re-run with full SHAs gave `ordinary-docs-only`. A repeat of AM3-14 | The classifier itself |
| AM5-02 | 27 Sep 2026 | accuracy | Recording Nathan's pick for C4 in the TypeSafe uses table, set the *Nathan's pick* column but left the row's *PR* text saying "Nathan's pick pending" | App Manager 5, while writing the C4 review's row |
| AM5-03 | 27 Sep 2026 | accuracy | Two Work Register texts left stale in Notion: the P06.1 row's body still said I2b's review was in flight after the review was recorded, and the D10 row still said "until PR26 merges" after PR27 replaced PR26. A repeat of AM5-02 | App Manager 5, querying the Work Register for old wording after AM5-02 |
| AM5-04 | 27 Sep 2026 | process | Pushed one records batch as three pushes within five minutes (`c7fd0a9`, `a5a113b`, `93cb9a0`): the entries AM5-02 and AM5-03, found during the Notion sync, were each pushed at once instead of with the next batch, and the later pushes cancelled four full runs (359 to 362). DM-01 P2 asks for pushes only when a session needs them. This entry was pushed after PR run 364 finished, so it cancelled no run, though it started one more | App Manager 5, reading the runs |
| AM5-05 | 27 Sep 2026 | accuracy | The brief's entry for the C4 review listed the classes that get another correction pass without "or DOES NOT MEET", so its "only" excluded a class the prompt includes | App Manager 5, comparing the brief with the prompt |
| AM5-06 | 28 Sep 2026 | accuracy | The verification of C5 found "no slip" in C5's section, which, like `README.md:398`, said JSON nested two levels deep in a query value is reachable only through a request-options argument; a `product` step's `params` can carry it too. The verification of C4 had passed the same list to the review untested | The exact-head review of C5 (nit 1) |
| AM5-07 | 28 Sep 2026 | accuracy | Four link properties of two Work Register rows left stale in Notion: D10's *Plan Reference* pointed at the Dev Manager charter on `claude/stoic-carson-66gdig` and its *Evidence* at PR26; M03's *Plan Reference* and *Evidence* pointed at the charter and the review log on the same old branch. The takeover batch replaced the old branch's links in page bodies, and AM5-03's old-wording query read only the rows' *Next Action* text. A repeat of AM5-03 | Dev Manager 2, its start note and DM-06 (finding 6), for D10; App Manager 5's new link query, for M03 |
| AM5-08 | 28 Sep 2026 | accuracy | Wrote that the dashboard's Chat count was "within 7%" of the sessions' ledgers; the bound it had computed, 162 calls, is 7.2% of the ledgers | Dev Manager 2, DM-07 item 5 |
| AM5-09 | 29 Sep 2026 | accuracy | Syncing the batch that recorded DM-07 (`c775f39`), updated the P06.1 row's *Next Action* but left its page body saying "The Dev Manager's close-out read (DM-07) is next." A repeat of AM5-03 | App Manager 5, fetching the whole row while syncing the next batch |
| AM5-10 | 29 Sep 2026 | accuracy | The post-merge batch (`041a081`) marked P06.1 done in the brief's Work ID line and status paragraph but left its headline "Status: in progress." The supersession sweep ran after the commit, not before | App Manager 5, in its supersession sweep before that batch's Notion sync |
| AM5-11 | 29 Sep 2026 | accuracy | Created a Work Register row for P06.DB without searching for an existing one; the register already held P06.DB's planned-stage row, "Planned", so it had two | Dev Manager 2, DM-08 section 8 |
| AM5-12 | 29 Sep 2026 | accuracy | The P06.DB verification named API artifact checks as the job already using the upload pin (it is Mobile checks), and repeated the session's "all three `***` are checkout's" without deriving it (line 152 is setup-python's) | The P06.DB exact-head review (F6 and its log confirmation) |
| AM5-13 | 29 Sep 2026 | accuracy | Two pick-recording batches, the review's (`49525a6`) and C1's, marked the session in flight in the P06.DB brief's Sessions but left its headline saying the session was next. It repeats AM5-10 | App Manager 5, in its supersession sweep before pushing the C1 pick |
| AM5-14 | 29 Sep 2026 | accuracy | The P06.DB-C1 prompt had the session push its records after its code, with the push run of its code commit as the evidence, but did not tell it to wait for that run to finish. The records push started a second run on the branch, and the code run, whose eight jobs all passed, was marked `cancelled` | The P06.DB-C1 session, which reported the label and its cause; Nathan then asked why |
| AM5-15 | 4 Oct 2026 | accuracy | The P06.DB-C1 prompt's start gate checked only its own start commit, so it could not tell that its work was already done and integrated. A session started from it on 4 October, in place of C1's review, passed the gate and made the whole correction pass again; reading Nathan's "ran in opus 5.5 extra high" as the review's start, the manager recorded the review as in flight (`d27519b`) | App Manager 5, verifying the second session's report |
| AM5-16 | 4 Oct 2026 | accuracy | The verification of P06.DB-C1 passed over its local run 2 ("same database, rows accumulating"), whose overlap counts include run 1's rows because the stress run's run tag is fixed, and so did not raise the one-run-per-database limit for C1's review | App Manager 5, checking the second session's "one run per database" limit against C1's code |
| AM5-17 | 5 Oct 2026 | accuracy | The correction for AM5-16 (`cbb3ff7`) named only C1's local run 2's overlap counts, not its controls, and left the implementation's local run 2, which had also reused its database, saying its first race's 200 was established. It repeats AM5-16 | C1's exact-head review (R5) |
| AM5-18 | 5 Oct 2026 | accuracy | The P06.DB brief took loopback as the proof's database boundary: D1 gives the settings a loopback host as their guard, and D4 says a local run "connects to no other database". A loopback host names a route, not a disposable database, so a misdirected local `migrate` could change a database that is not the proof's | Codex's second code review of PR28 (CX3) |
| AM5-19 | 5 Oct 2026 | accuracy | The C2 prompt's revision 1 replaced DM-10's 2.3 query with one that named no database to run in. `pg_class` holds one database's relations, so a step that ran the query from another database would pass whatever the wrong-marker `migrate` did to the proof's database. It also gave the prefix test in words only, which did not exclude `LIKE 'pg_%'`, where `_` is a wildcard | Dev Manager 2, DM-11 item 1, before the prompt ran |
| AM5-20 | 5 Oct 2026 | execution | Verifying C2, restored the scratch worktree after the first fix reversal with `git checkout -- .`, which kept the reverted files that `git checkout <sha> -- <files>` had also staged; the next five reversals and the control ran on a reverted tree. The results were discarded and the reversals redone after a hard reset; no record carried them | App Manager 5, when the unchanged control failed |
| AM5-21 | 5 Oct 2026 | accuracy | Recording C2's run of record at its integration (`dd67696`), the P11 plan said run 37262466651 "reran the whole plan with the same results". Its outcome was the same; its numbers were not (526 submissions against 617, and 197 to 200 overlaps per race against 174 to 200) | C2's exact-head review (F3) |
| AM5-22 | 5 Oct 2026 | accuracy | The handoff's current-item line kept calling the P06.DB brief "revision 2" through revisions 3 to 5, although three records batches changed the handoff and the brief. It repeats the mechanism of AM5-10 and AM5-13 | App Manager 5, in the supersession sweep for revision 6 |
| AM5-23 | 5 Oct 2026 | process | The report of PR28's merge put P06.2's start to Nathan as a choice, with "Hold" as the other option, though nothing in the record argues for holding; only his direction was needed (OD-12). It repeats the mechanism of AM4-02, a choice with nothing to choose | Nathan: *"why would I want to hold?"* |
| AM5-24 | 5 Oct 2026 | follow-through | The retirement of `app-builder-1/p05-1-birth-diagnostics` fell due when the flake fix merged (29 September); the handoff carried it without asking Nathan, the only person who can delete a branch, and no manager set up a cleanup of merged branches. Recorded by App Manager 6 | Nathan ("bad branching hygiene"), with 38 branches |
| AM6-01 | 5 Oct 2026 | process | Took on Stage A's run of record itself: subscribed to PR29's CI events and scheduled a check-in to watch the run, work that belongs to the worker session | Nathan |
| AM6-02 | 22 Oct 2026 | accuracy | Recorded B1-C1's race times as "7 to 23 s" from a listing cut off at 20 lines; the adapter's slowest race took 29.7 s against its 30-second cap | B1-C1's exact-head review (finding 1) |
| AM6-03 | 23 Oct 2026 | scope | Stage B2's prompt added a pinned, untyped SDK to `services/api` but its owned paths named neither `pyproject.toml`, where the type check's override for it lives, nor the API README; the session changed both, reporting one | App Manager 6, verifying Stage B2 |
| AM7-01 | 23 Oct 2026 | accuracy | B2-C1's prompt (revision 2) said `tzdata` stays as resolved and nothing else moves in the lock alignment, copied from DM-17 5.1 without reading the lock, which lists `tzdata` `# via python-dateutil`; aligning `python-dateutil` to 2.9.0.post0 removed it | The B2-C1 session |
| AM7-02 | 23 Oct 2026 | accuracy | B2-C1's prompt said "Each push runs the Foundation workflow on your branch"; the session's harness named its branch `ccr-…`, outside the workflow's push filter, so no run started and the session had no run of record | The B2-C1 session |
| AM7-03 | 23 Oct 2026 | accuracy | B2-C2's prompt, revisions 1 and 2, let the session send "the Video and Feeds `PUT`s that section 4 item 5.1 plans"; item 5.1 is the chat dry run, and the products dry run is item 6.1 | App Manager 7, reading revision 2 before giving it to Nathan |
| AM7-04 | 23 Oct 2026 | accuracy | B2-C2's prompt allowed only "D1 and the class-2 types' grants" in the comparison after the chat apply; emptying those grants necessarily removes `agent` from nine roles' `scopes` in the roles read, which the rule did not allow | The B2-C2 session |
| AM7-05 | 23 Oct 2026 | accuracy | The D8 message for Nathan, revision 1, said "four things" and listed three, called the chat type `agent` "a second kind of chat room" when six others existed, said the removals "held" when they held for one evening's run, and said (b) closes "every way" a Stream change could reach a member "permanently"; it gave (a) no cost line and (b) no "what stays open" line | The Dev Manager (DM-20 item 5), before it reached Nathan |
| AM7-06 | 24 Oct 2026 | accuracy | The brief's revision 8, point ii, said Stream's server-side send "creates that user (M5)" as fact; the evidence record marks it an inference (C4's read found the user absent before M5, D10's read found it after) | Stage B2's exact-head review |
| AM7-07 | 24 Oct 2026 | follow-through | The handoff's branch list kept `claude/dev-manager` at `821efc7` (DM-19, merge `5480b99`) through DM-20's integration, when its head became `ca806e3` (merge `855a92b`) | App Manager 7, checking the remote branches at B2-C4's integration |
| AM7-08 | 24 Oct 2026 | accuracy | PR31's body and Implementation Control said B2-C4 generalized "every run identifier" in the conformance results, repeating the session's claim; strings already passed through `_generic` keep their random part | B2-C4's exact-head re-review (C4R1) |
| AM7-09 | 24 Oct 2026 | follow-through | After DM-21, the manager told Nathan "NOTHING NEEDED" and left its own next steps (Codex's review, the final run, PR31's merge) waiting on his next message | Nathan: *"You don't have a planned next step?"* |
| AM7-10 | 24 Oct 2026 | accuracy | The P11 plan said the reads' guards meant "no enclosing Django transaction can hold their locks", and carried a session's raw-`BEGIN` limit unchecked; `set_autocommit(False)` passed both guards | C1-C1's exact-head re-review (R1) |
| AM7-11 | 24 Oct 2026 | follow-through | DM-17's follow-up on the harness client's `npm ci` advisory was due "before Stage C", and was not decided before C1 ran and merged | App Manager 7, updating the handoff after PR32 merged |
| AM7-12 | 24 Oct 2026 | follow-through | After verifying Codex's CX8 on PR33, the manager carried it to P11 and put the alternative (a correction pass before the merge) to Nathan as a question, instead of consulting the Dev Manager first (OD-32) | Nathan: *"I don't feel comfortable answering that question. It should be an escalationf for the dev manager"* |
| AM7-13 | 25 Oct 2026 | process | The manager gave Nathan C2-C1's exact-head re-review prompt while Codex's review of C2-C1's head was still running; Codex then found CX9, and the manager sent DM-24, which can change the code under review, while telling Nathan the re-review should continue | Nathan: *"You requested a premature review, and now you are looking for a dev manager consultation"* |
| AM7-14 | 25 Oct 2026 | accuracy | Nathan directed the manager to create App Manager 8; the manager read his words as his own hand start, recorded OD-46, the handoff and Notion that way, and told him to start it | Nathan: *"i told you to create the Glow App Manager 8 session"* |
| AM8-01 | 25 Oct 2026 | follow-through | The first report and DM-25 revision 1 went to Nathan without checking PR33's open review threads; Codex's CX10 (00:42 UTC), unrecorded since App Manager 7's handover, was missed | App Manager 8, reading PR33's threads after Codex's next summary reported unresolved findings |
| AM8-02 | 25 Oct 2026 | accuracy | Notion's DM-24 row named the records commit `1ec5186` as the merge of DM-24's report; the merge is `f87f3b5` | Dev Manager 3, start note section 5 |
| AM8-03 | 25 Oct 2026 | accuracy | CX10's records and DM-25 said the unread count "never clears" and that any member sending 20 messages in a row would reach it; both overstated the code | Dev Manager 3, DM-25 section 5 |
| AM8-04 | 25 Oct 2026 | accuracy | Notion paraphrased the re-review's F3 as a revocation dropping "a list read begun after it started", which reads as the reverse of the finding | Dev Manager 3, DM-27 4.1 |
| AM8-05 | 25 Oct 2026 | accuracy | DM-27's proposed d.2 asked for tests of two `cursorKnown` clears that, under d.1, could never fail | Dev Manager 3, DM-27 section 3 |
| AM8-06 | 25 Oct 2026 | accuracy | CX12's records said "history out of order … until it is reopened"; the messages stay in order with a gap, and reopening the same conversation does not clear it; and `:248` for `:244` | Dev Manager 3, DM-28 section 3 and 4.3 |
| AM8-07 | 25 Oct 2026 | follow-through | The Work Register row's Next Action property was left at `9776c6f` when its page body was updated for CX12 and DM-28 | Dev Manager 3, DM-28 4.1 |
| AM8-08 | 25 Oct 2026 | accuracy | *Implementation Control* said "Show earlier messages" is idle once the reload merges; the code turns only `loading` into `idle` | Dev Manager 3, DM-29 1.3 |
| AM8-09 | 25 Oct 2026 | accuracy | "Manager verification of Stage C2-C3" gave `store.ts` as +16 −14; the numstat is +14 −16 | The combined re-review, finding 13 |
| AM8-10 | 25 Oct 2026 | accuracy | Chat reports labelled the push and PR runs of three Markdown-only commits the wrong way round | Dev Manager 3, DM-30 4.3 |
| AM8-11 | 26 Oct 2026 | follow-through | Notion's standing status bullets on Implementation Control left at App Manager 7's state; read-backs checked only the edited strings | M05 review, finding 30 |
| AM8-12 | 26 Oct 2026 | process | The current handoff kept over its 5 KB limit, with follow-ups whose only home it was | M05 review, finding 38 |
| AM8-13 | 26 Oct 2026 | follow-through | The `89f2601` Notion sync left two Implementation Control bullets stale ("No PR is open" with PR34 open; DM-31 "goes to it next" after its answer), repeating AM8-11 | App Manager 8, at the `72c60dd` sync |
| AM8-14 | 26 Oct 2026 | records | M04's brief recorded its implementation prompt's TypeSafe reading in its Sessions line, which step 3 keeps to the prompt's header and the uses table (DM-01 P8) | App Manager 8, at M04's integration |
| AM8-15 | 26 Oct 2026 | accuracy | PR37's description named a PR run ID, 40367951219, that the manager had not read; the run did not exist yet | App Manager 8, on rereading the description it had just posted |
| AM8-16 | 26 Oct 2026 | follow-through | After PR37 merged, the manager named M06 as the next item and ended its turn "NOTHING NEEDED", with no brief and no handoff for Nathan | Nathan: *"ok, why did you not give me a handoff for the next task?"* |
| AM8-17 | 1 Nov 2026 | accuracy | M06 stage two's prompt required `npm audit signatures` and limited the network to the npm registry and `docs.expo.dev`; the command needs Sigstore's TUF host, so the session had to deviate | The stage-two session, which logged the deviation |
| AM8-18 | 1 Nov 2026 | follow-through | M06 stage two's record raised "one precision for the Dev Manager" (`noxcturnal` published by GitHub Actions without provenance), and the manager's verification did not route it | The exact-head review, finding 2 |
| AM8-19 | 1 Nov 2026 | records | Nine prompts and consultations pruned on 26 October and 1 November (M05's, DM-31 to DM-33, M04's four, M06's assessment) left their Notion links on the manager branch, where the files no longer exist | The manager, while pinning M06's links in Notion |
| AM8-20 | 1 Nov 2026 | prompt | P06.2-F's prompt told the session to push its code and read the run of record, but not to hold a records push while that run was in progress, though a newer push on the branch cancels the older run; the session's records push cancelled the run on its code head | The session itself |
| AM8-21 | 1 Nov 2026 | accuracy | P06.2-F's Manager verification counted the diff as "18 changed, 5 added, 2 removed" (it is 17, 6 and 2) and repeated the session's "Expo still inlines it there" without reading a bundle | The exact-head review, findings 7 and 10 |
| AM8-22 | 26 Oct to 2 Nov 2026 | follow-through | Implementation Control's standing status bullets (Phase, Next items, Manager, Main, Branches, Mistakes log) left at 26 October through M06, P09.3a, P06.2-F and the handover; the batches updated only the opening paragraph. The Dev Manager page's consultations stopped at DM-32 likewise. A repeat of AM8-11 and AM8-13. Recorded by App Manager 9 | App Manager 9, reading the whole status section before its first sync |
| AM9-01 | 2 Nov 2026 | accuracy | The first report told Nathan that Implementation Control's status section matched `76dbe4a`, after reading only its opening paragraph; its standing bullets did not (AM8-22) | App Manager 9, reading the whole section before its first sync |
| AM9-02 | 2 Nov 2026 | process | One records batch pushed as two pushes five minutes apart (`c6108e4`, then `06ec8b6` for AM8-22 and AM9-01, at the stop hook's request); the second cancelled the push and PR runs on `c6108e4` (41445575445, 41445585520), whose gates then failed. A repeat of AM5-04's mechanism. It recurred the same day: `903c41f`, then `3cf2ee1` for a wrong checkpoint time and AM8-22's addition, cancelled PR run 41482411075 | App Manager 9, reading the cancelled runs |
| AM9-03 | 2 Nov 2026 | accuracy | The verification of C1 repeated the session's "finds Glow's data by type through any binding" in the delta prompt, Notion and the reply on Codex's thread, after re-running only the session's planted forms and its one named evasion; the delta re-review found more than 20 edits in the two files that pass | C1's delta re-review (findings 1 to 5) |
| AM9-04 | 2 Nov 2026 | accuracy | Wrote the handoff's checkpoint and branch-list times from memory three times: 13:20 UTC for 16:32 (pushed at `903c41f`), 18:30 for 18:24 (pushed at `007377e`), and 20:30 for 21:51 (caught before its push) | App Manager 9, reading `date -u` after each |
| AM9-05 | 2 Nov 2026 | accuracy | Notion's status lead and P06.2-F's Work Register row said the manager recommended "view models as their own item"; DM-39's consultation and the review log asked (c)'s timing without recommending one. The commit message of `6a9a6b5` said the same | Dev Manager 3, DM-39 section 9 |
| AM9-06 | 3 Nov 2026 | accuracy | C3's prompt and the brief's Outcome 1 asked each item of the check's refusal list to name, by ID, the planted forms that pin it, without the manager first checking that each item had one; several had none | Correction C3, its point 1 |
| AM9-07 | 3 Nov 2026 | accuracy | Implementation Control's "Standing directions" line said the Notion register copy holds OD-01 to OD-54 after OD-55 and OD-56 were added to it; App Manager 9's readbacks covered the status section and missed it | App Manager 9, recording OD-57 |
| AM9-08 | 8 Nov 2026 | accuracy | DM-40's option (a) proposed narrowed words for finding 1 ("an object property holding a function, given by reference") without trying forms just inside them; an accessor, a class field and an untyped literal given later pass inside those words | Dev Manager 3, DM-40 section 3 |
| AM9-09 | 8 Nov 2026 | accuracy | The two uses-table rows for C3's delta re-review were created without the PR field, which App Manager 9's earlier rows carry; the skill's printed row has no PR key | Dev Manager 3, DM-40 section 8 |
| AM9-10 | 8 Nov 2026 | process | After C4's run of record failed, asked Nathan to use "Re-run failed jobs" on the run page, posted the same request on PR40, and bundled a relay that depended on it; the CI question should have gone to the Dev Manager first (OD-32), and Nathan does not perform GitHub operations | Nathan (OD-58) |
| AM9-11 | 8 Nov 2026 | accuracy | The review log's DM-40 row (`7983b31`) and DM-41 row (`9e0334a`) linked their consultations as `../ephemeral/`, which resolves under `docs/continuity/`; the log's other rows use `../../ephemeral/` | App Manager 9, syncing Notion |
| AM9-12 | 8 Nov 2026 | follow-through | The OD-58 batch's supersession sweep (step 5) missed two governing texts that still put a GitHub operation on Nathan or kept CI re-runs from the Dev Manager: the charter's "Not for" ("CI reruns") and step 7's branch-cleanup sentence ("the names to delete go to Nathan"). Recorded by App Manager 10 (OD-11; DM-41 7.2) | Dev Manager 4 (DM-41 6.3, 6.4) |
| AM10-01 | 8 Nov 2026 | prompt | C6's prompt, pushed at `678dabd`, quoted DM-42's conditions by line range, and the ranges cut 2.1's opening and carried the report's own section heading into the prompt; found on re-reading the filled text before giving it, and corrected in the same revision before it was given; the correcting push cancelled PR run 42490599464 on the superseded `678dabd` | App Manager 10 |
| AM10-02 | 8 Nov 2026 | accuracy | P06.3's brief, revision 1 (`8bf9d8d`), named the route guard's predicate (`SAFE_ROUTES`, `canAccessRoute`) as the screen's guard and excluded `src/app/_layout.tsx`, whose `Stack.Protected` line is what guards a screen; as written, the new screen would open signed out or the session would stop | Dev Manager 4, DM-44 item 6 |
| AM10-03 | 9 Nov 2026 | accuracy | The verification of correction C1 (the P06.3 record, pushed at `1a2a2c7`) said the adapter's change was the moved `capture` "plus two comment lines"; there are three | C1's delta review, N-3 |
| AM10-04 | 9 Nov 2026 | process | Correction C1's prompt (`3a2b930`) went to Nathan without a Dev Manager consultation, though step 6 consults the Dev Manager when a fix touches a security boundary, revocation included; C1 changed when an ended session's command is refused | Dev Manager 4, DM-45 section 16 |
| AM10-05 | 9 Nov 2026 | follow-through | Notion's operating-procedure summary kept its stamp at `1ce2fcb` (26 October) through App Manager 10's governing-text changes of 8 November (`33c4cc2`, `0a49e62`, `678dabd`, `86e65dc`); the match check moves the stamp when a governing text changes | App Manager 10, checking the summary after adding step 6's sentence |
| AM10-06 | 9 Nov 2026 | follow-through | DM-45 section 9 approved SV1's email change as needing "`ACCOUNT_CHANGE_EMAIL = True` … and reauthentication"; the brief's D3 (revisions 2 and 3) named neither setting, and the prompt left the settings to the session, which kept allauth's default, reauthentication off | the SV1 implementation session's findings, read in the manager's verification |
| AM10-07 | 9 Nov 2026 | accuracy | DM-48 (`38142b3`) proposed words for acceptance check 11 ("the sixth request at `account/password/change` within 300 seconds … is refused") that describe a case allauth's default `5/m/user` also passes, since a sixth request sent at once is refused at 5 a minute too; and its D3 replacement left "They use Django's cache" pointing at the threat model | Dev Manager 4, DM-48 section 3 |
| AM10-08 | 9 Nov 2026 | follow-through | Implementation Control's Branches bullet kept the manager branch's "at this sync" hash one commit behind the status line at two syncs in a row (`30fdf1a` against `38142b3`; `38d48e2` against `cae9cea`); the status edit did not move the bullet | Dev Manager 4, DM-48 section 9 and DM-49 section 5 |
| AM10-09 | 9 Nov 2026 | follow-through | Integrating correction C1, App Manager 10 added C1.5 to P11's plan but left, in the same SV1 entry, "No reauthentication: an email change needs none", which C1 made false; the supersession sweep did not search for the replaced setting's state | Dev Manager 4, DM-50 section 4 |
| AM10-10 | 9 Nov 2026 | accuracy | The second A05 message, revision 1, took its facts from the matrix's section 9 summary and the manager's reading of the design, not from each cited row and text: Apple's row has no derived-data rule (AP-23), California's is a right to limit, not consent (UST-42), New York's fraud-ban notice binds only a paid service (UST-08), "a city or ZIP code" widened the research's "city/region", and rematch was said to change the data model, which says the opposite (`Match`) | Dev Manager 4, DM-51 section 5 |
| AM10-11 | 10 Nov 2026 | accuracy | SV2's brief, revision 1, proposed mechanisms without reading the code and contract they rely on: D7 had SV1's age port update an existing row (`record` refuses one, and `glow_identity` was excluded) and the birth input hold the date before the member gives a place; D11 gave the sensitive consent as `ConsentIntent` with a new purpose (it has no purpose field); D6 assumed `accept_consent` checks the version; D9 left out P04.2's chart and "looking for" requirements | Dev Manager 4, DM-52 sections 8, 9 and 11 |
| AM10-12 | 10 Nov 2026 | accuracy | SV2's brief, revisions 1 and 2, gave D11's additive DTOs owned paths without reading what a DTO addition writes: `generate.mjs` rewrites `apps/mobile/src/contracts/generated/`, which CI compares byte for byte and the corpus test imports, and P04.3 and C1 also registered their DTOs in `flows-v1.json`. The brief excluded `apps/**`, left out the registry, and said the mobile app's generated validators stay untouched | App Manager 10, writing Stage A's prompt |
| AM10-13 | 10 Nov 2026 | prompt | SV2 Stage A's prompt, at `481e2f3`, had its start gate check `main`'s merge commit `c864edd` as an ancestor of the session's branch. That commit is not on the manager branch, so every session would have stopped at the gate | App Manager 10, dry-running the gate before giving Nathan the prompt |
| AM10-14 | 10 Nov 2026 | accuracy | Verifying SV2 Stage A's correction C1 (`40db2c2`), App Manager 10 accepted C1-3 (a future birth date refused with no rerun) as a reading of DM-54's words and put only its supporting argument in the review prompt's revision 1. It did not set it against the brief's acceptance item 7, which counts "a future date" among the dates that fail, or `adult_outcome`, which fails one | Codex, its P2 finding on `40db2c2` |
| AM10-19 | 11 Nov 2026 | accuracy | The brief's "Stage B, correction C1" and C1's prompt placed the state-write guard's allowlist in `tests/test_profiles_offline.py`, from memory; it is `NOT_A_PROFILES_STATE` in `tests/test_profile_recompute.py`, outside C1's owned paths, so the brief's rule to update it could not apply | C1's session, its deviation 1 |
| AM10-18 | 11 Nov 2026 | follow-through | Routing Stage B's prompt, the handoff's checkpoint and branch list were written as 01:24 UTC in the same command whose clock read 01:19: AM10-17's prevention was written but not followed | App Manager 10, reading the command's clock line |
| AM10-17 | 10 Nov 2026 | follow-through | The handoff's waiting checkpoint after PR43's receipt gave 23:57 UTC, written before the clock was read; the clock read 23:55 (AM9-04 repeated) | App Manager 10, when the commit's own clock line printed |
| AM10-16 | 10 Nov 2026 | accuracy | Pruning SV2 Stage A's prompts, App Manager 10's link-pinning script matched link targets by file name. The Dev Manager's reports in `reviews/` share their names with the consultations, so it also pointed 16 links to the reports at the pruned consultations | App Manager 10, reading the script's word diff before the commit |
| AM10-15 | 10 Nov 2026 | accuracy | DM-55's consultation (`496c39e`), item 1.4, proposed erasing the date, time, place and time zone of every birth input revision after a date under 18. It did not read what that breaks: `OwnBirthInput` requires a full `BirthInput`, so the owner's reads would fail on an erased revision; the next save compares its expected version with the erased row's; and `birth_time_uncertainty` ties the time to its precision | Dev Manager 4, DM-55 section 3 |
| AM10-20 | 11 Nov 2026 | follow-through | Implementation Control's "Mistakes log" bullet left listing AM10-01 as the last entry, at `0e890dc`, through AM10-02 to AM10-19 and App Manager 10's last sync at `8130439`. A repeat of AM8-22's mechanism. Recorded by App Manager 11 | App Manager 11, reading the whole page at its start |
| AM10-21 | 11 Nov 2026 | follow-through | Implementation Control's "Standing directions" line left saying the register copy holds OD-01 to OD-62 after OD-63 was added to the copy at `8130439`. A repeat of AM9-07. Recorded by App Manager 11 | App Manager 11, reading the whole page at its start |
| AM10-22 | 11 Nov 2026 | follow-through | Implementation Control's "Phase" bullet left ending "Now: P06.2-F, the mobile hardening, in PR40" after PR40 to PR44 merged, and its "Next items" bullet left saying "now SV2 … Stage B next" after PR44 merged. A repeat of AM8-22's mechanism, as AM10-20 is. Recorded by App Manager 11 | App Manager 11, reading the status section's standing bullets in its first sync |
| AM11-01 | 11 Nov 2026 | accuracy | The first report told Nathan that the next message would carry a prompt for the matrix recheck; the recheck is the manager's own records reading (the OD-60 and P06.3 recheck records), not a session | App Manager 11, reading the earlier recheck records before writing the prompt |
| AM11-02 | 11 Nov 2026 | follow-through | Correcting Implementation Control's "Next items" bullet, replaced only its opening and left "P06.2-F (now, PR40)" further on in the same bullet; the readback searched for the edited strings only. A repeat of AM8-11's mechanism | Dev Manager 4, DM-60 section 18 |
| AM11-03 | 11 Nov 2026 | follow-through | The handoff's checkpoint at `fe1b6ba` gave 19:14 UTC, written before the clock was read; the clock read 19:12 (AM10-17's mechanism) | App Manager 11, when the commit's own clock line printed |
| AM11-04 | 11 Nov 2026 | follow-through | The batch at `d35b0ba` pushed the handoff at 5,198 bytes, over its 5 KB limit, with its "Branches and PRs" section still at App Manager 10's handover (17:09 UTC); both corrected in the next commit, before Stage A's PR was opened, which cancelled the push run on `d35b0ba` (not a run of record) | App Manager 11, reading the commit's byte count |
| AM11-05 | 11 Nov 2026 | follow-through | After opening PR45 at 22:39 UTC, told Nathan "NOTHING NEEDED" and set nothing to wake the manager when the run and Codex finished (22:47 and 22:42); the review prompt waited until Nathan asked at 23:37. A repeat of AM7-09 | Nathan: "still waiting?" |
| AM11-06 | 11 Nov 2026 | accuracy | The review prompt's first TypeSafe action text counted its numbered items as sixteen; there are twenty. Caught before the reading was used; re-sent with the true count, the same cell, both readings recorded | App Manager 11, comparing the text with the prompt |
| AM11-07 | 11 Nov 2026 | follow-through | The handoff's checkpoint at `b09cbf3` gave 23:41 UTC, written before the clock was read (it read 23:40): AM11-03 repeated within the hour. The time now comes from the clock inside the same command that writes it | App Manager 11, reading the commit's clock line |
| AM11-08 | 12 Nov 2026 | follow-through | The Notion sync for `1ffff7d` changed Implementation Control's "Branches" bullet from three branches to four and left its next sentence, "All three are kept by the cleanup's keep-list"; the edit replaced the list, not the bullet. AM11-02's mechanism, repeated | App Manager 11, reading the bullet back |
| AM11-09 | 12 Nov 2026 | accuracy | C1's prompt, revision 1, named the tie-break's files as `predicates.py`, `pages.py` and `keys.py` "and what they need", without `eligibility.py`, whose `parameters` passes the pads it told the session to remove. Corrected in revision 2 before it was given | App Manager 11, checking Codex's CX2 against the prompt |
| AM11-10 | 12 Nov 2026 | process | Held DM-62's relay message for a Codex pass on its own commit, a wait the workflow sets only for review and correction prompts; Codex had already passed the same code at `c3fb5bb` with nothing new. Nathan had nothing to run until he asked what the manager was doing | Nathan: "what are you even doing?" |
| AM11-11 | 12 Nov 2026 | follow-through | Brief revision 3's sync left Implementation Control's "Next items" saying "its brief, revision 2"; the sweep searched the repository, not Notion's standing lines, for the previous revision number. AM5-22's mechanism, repeated | Dev Manager 4, DM-62 section 7 |
| AM11-12 | 12 Nov 2026 | follow-through | The batch at `b67bae2`, which merged DM-62's report, left the handoff's branch list giving `claude/dev-manager` at DM-61's head (`133a715`); AM11-11's new sweep was run for the brief's revision number only. Corrected in the next commit, before any session read it | App Manager 11, listing the branches for Notion's "Branches" bullet |
| AM11-13 | 12 Nov 2026 | accuracy | The exact-head review prompt's revision 2 said "Four offline reversals, at least" over a list of five; seen before it was given, and given as written rather than revised and re-reviewed by Codex | App Manager 11, reading the filled prompt |
| AM11-14 | 12 Nov 2026 | follow-through | The CI policy's discovery sentence, written by the manager at `d35b0ba`, still said the suite's key keys "its keyed tie-break" after DM-61's K2 removed the key; the sweep for K2 did not search for "keyed" outside the brief, and C1's prompt did not list the CI policy or the fixtures note among its records | The exact-head review, F5 |
| AM11-15 | 12 Nov 2026 | follow-through | Recording PR45's run of record for Stage A (`b09cbf3`), and later C1's, the manager left the P11 plan's SV3 entry saying "Run of record: none yet" and concurrency "not claimed" | The exact-head review, F6 |
| AM11-16 | 12 Nov 2026 | accuracy | The evidence record's "PR45's run on `4b771e0`" said "Every other job passed"; the gate job also failed, as designed | The exact-head review, N6; corrected at the next batch |
| AM11-17 | 12 Nov 2026 | follow-through | Gave DM-65 at `c661dce` without a watch on Codex's pass, then wrote C2's prompt at `2475d7b` without reading PR45's comments; Codex's P2 on `c661dce` (17:39 UTC) was found only at 18:47, after the pass on the prompt's commit. Both of its findings were already C2's items, so the prompt stood | App Manager 11, reading PR45's comments before giving C2's prompt |
| AM11-18 | 13 Nov 2026 | communication | After giving F7's decision message on 12 November, named it to Nathan in later status lines only as "your F7 decision", a review label he had no reason to keep in mind, without saying what it was; he asked "what 'F7' decision?" | Nathan |
| AM11-19 | 13 Nov 2026 | records | Two standing lines left stale after their facts changed: the handoff's title ("C2 continues after DM-66") through two later commits (`6b376cf`, `3000014`), and the brief's D8 ("Whether to bound the probing is put to Nathan … it is decided before then") after OD-64 was recorded beneath it (`058829c`) | Dev Manager 4 (DM-67 section 7; GD13, GD14) |
| AM11-20 | 13 Nov 2026 | records | Two standing lines left stale again: `claude/dev-manager`'s head (`a53bdb0`) in the handoff's branch list and Notion's Branches bullet after DM-67's report (`e7786bb`) was merged at `2d04951` (AM11-12's pattern); Notion's "Next items" kept the brief's revision 8 after revision 9 (AM11-11's pattern) | Dev Manager 5 (start note, section 4) |

## App Manager 2

### AM2-01 — A network claim based on curl only (accuracy)

- **What happened:** the M02-I1 prompt said direct HTTPS works in a clean process (`env -i`). App Manager 2 had tested only curl. In this environment npm also needs the proxy variable and `NODE_EXTRA_CA_CERTS`; without them `npm ci` failed with `SELF_SIGNED_CERT_IN_CHAIN`.
- **Caught by:** the M02-I1 implementer.
- **Effect:** two failed installs of about 70 s each in the implementation session. No wrong change landed.
- **Correction:** accepted and recorded in the evidence record. `docs/operations/local-development.md` documents the pass-through.
- **Prevention:** test every environment claim in a prompt with the tool the session will actually use.

### AM2-02 — A command that fails as written (accuracy)

- **What happened:** the M02-I1 prompt prescribed `npx expo install`. `app.config.ts` rejects a bare Expo CLI run; the repository's wrapper `node scripts/development.mjs install` is required.
- **Caught by:** the M02-I1 implementer.
- **Effect:** one failed command. The implementer used the wrapper.
- **Correction:** accepted and recorded. `apps/mobile/AGENTS.md` now gives the wrapper form.
- **Prevention:** take prescribed commands from the repository's documented commands, or run them before putting them in a prompt.

### AM2-03 — Wrong invocation of the pin test (execution)

- **What happened:** App Manager 2 ran `python3.12 -I -m unittest tests.test_toolchain_pins`. Isolated mode drops the working directory from `sys.path`, so the import failed with `ModuleNotFoundError`.
- **Caught by:** App Manager 2.
- **Effect:** none. The re-run without `-I` passed, and the evidence records the invocation error.
- **Prevention:** use the documented command.

### AM2-04 — A prompt body that referred to its header (accuracy)

- **What happened:** the committed M02-C1 prompt body said "the two sections named above". Those names appeared only in the file header, which Nathan does not paste.
- **Caught by:** App Manager 2, before giving the prompt to Nathan.
- **Effect:** none. Commit `4857561` named the sections in the body two minutes later, which changed the start SHA from `38ccbf1`.
- **Prevention:** before committing a prompt, read the paste-ready body on its own.

### AM2-05 — An approximate time in the usage log (execution)

- **What happened:** the send time of the delta review's TypeSafe request was not captured, so its row records "about 23:05 UTC".
- **Caught by:** App Manager 2, when logging the row.
- **Effect:** one approximate timestamp.
- **Prevention:** print the UTC time with every scorer request.

### AM2-06 — Merged before Codex's automatic review finished (process)

- **What happened:** App Manager 2 marked PR18 ready and merged it three seconds later. Marking it ready had started Codex's code and security review. That review finished five minutes after the merge, with a P2: `ln -sfn` into a directory-shaped link destination succeeds silently.
- **Caught by:** App Manager 2, reading PR18's comments during the close-out.
- **Effect:** the P2 is on `main` unfixed. It has no effect in the `Glow app` environment, where the link paths are symlinks.
- **Correction:** App Manager 2 reproduced the finding and replied on PR18. [PR20](https://github.com/amthorn78/glow-dating-app/pull/20) records it, and the fix is a recorded follow-up.
- **Prevention:** step 7 of the [manager workflow](../planning/manager-workflow.md), "Wait for Codex": mark a full-scope PR ready once its final head is pushed, and merge only after Codex's summary shows both reviews completed.

### AM2-07 — The session-branch clean-up was forgotten (follow-through)

- **What happened:** on 24 September App Manager 2 told Nathan: "I'll deal with old session branches after M02 merges. I may not be able to delete them from this session … if so, I'll list them for you." The M02 close-out did neither.
- **Caught by:** App Manager 2, while searching its transcript for this log.
- **Effect:** none yet. The branches were left as they were.
- **Correction:** the current handoff now lists them. (That list is archived in the [earlier handoff](history/m02-p06-1-handoff.md) since the handoff was slimmed on 25 September 2026.)
  - The M02 session branches are fully merged into `main`: `claude/ecstatic-goodall-qajdh4`, `claude/eager-goodall-1zjgey` and `claude/vigilant-einstein-i95w78`.
  - A cloud session cannot delete another session's branch. Nathan may delete merged branches on GitHub.
  - `app-builder-1/p05-1-birth-diagnostics` is deliberately unmerged and stays.
- **Prevention:** record a promised later action in the handoff's next actions when it is made.

### AM2-08 — A work queue of its own instead of the plan (process)

- **What happened:** after M02, App Manager 2 wrote a queue into the handoff, the brief, the next-manager start prompt and Notion: the rendered-test diagnosis first and a P06.1 proposal last. That conflicted with PF01's phase sequence and with the initiation assignment, which ends *"Complete the optimization before proposing whether to resume P06.1."* It also conflicted with App Manager 1's handoff: "Propose, don't dispatch."
- **Caught by:** Nathan: *"there is a specific plan and process that you should be adhering to."*
- **Effect:** the handoff merged in PR19 would have routed App Manager 3 away from the plan. No work item started.
- **Correction:** [PR21](https://github.com/amthorn78/glow-dating-app/pull/21) routes the next manager to the P06.1 proposal. The other items are recorded follow-ups for Nathan to schedule, and Notion matches.
- **Prevention:** before writing next actions, re-read PF01's sequence, the initiation assignment and the previous handoff's next actions, and quote the governing line in the handoff.

### AM2-09 — The start prompt omitted the plan (process)

- **What happened:** the next-manager start prompt merged in PR19 left PF00, PF01, the documentation guide and the full Claude handoff out of its required reading. Root `AGENTS.md` requires them.
- **Caught by:** App Manager 2, while correcting AM2-08.
- **Effect:** none. PR21 corrected it before any manager used the prompt.
- **Prevention:** build a start prompt's reading list from the first paragraph of `AGENTS.md` and PF00's "Start here".

### AM2-10 — Tried to run the Setup script inside the manager session (process)

- **What happened:** after Nathan pasted the new Setup script, App Manager 2 tried to run it by hand in its own session to preview the result. That would have replaced its own toolchain. The right step was to hand over to a new manager session, where the Setup script runs.
- **Caught by:** the tool permission guard, which blocked the command as destructive. Then Nathan: *"you will need to initialize a new session of yourself to use the new script."*
- **Effect:** none; the command did not run.
- **Correction:** App Manager 2 prepared the App Manager 3 handoff and start prompt.
- **Prevention:** environment changes take effect through new sessions. The manager neither changes its own environment nor runs setup tooling.

### AM2-11 — Notion slips (execution)

- **What happened:**
  - A Work Register "Next Action" contained a bare `.md` filename, which Notion turned into a broken link.
  - An Implementation Control update failed, because its match text omitted a link's markup.
  - The new current-status block at the top of Implementation Control ended "The sections below are history", but the operating procedure right below it is current policy.
- **Caught by:** App Manager 2's readbacks.
- **Effect:** none lasting. All three were fixed within the hour.
- **Prevention:**
  - Avoid bare `name.md` in Notion text.
  - Match link markup exactly as fetched.
  - Read the surrounding sections before writing a statement about them.

## App Manager 3

### AM3-01 — A Notion query with an unwrapped filter (execution)

- **What happened:** after correcting the Work Register's P05.3 row, App Manager 3 read it back with a rows-mode query whose filter was a single property condition. The tool requires the filter to be a group, so the call failed input validation.
- **Caught by:** the Notion tool's input validation.
- **Effect:** none. The query was re-sent with the condition inside a group and confirmed the update.
- **Prevention:** in rows-mode Notion queries, always wrap conditions in a group, as the reconciliation's first query did.

### AM3-02 — A level commitment not carried into the review prompt (follow-through)

- **What happened:** after P06.1-I1 started, App Manager 3 told Nathan twice that it expected to recommend "max, or ultracode if the scorer flags it" for the I1 review. It also wrote that into the Work Register's P06.1 row. The scorer then flagged ultracode: P(`single_session`) was 0.37. But the review prompt, the brief and the handoff said that the manager did not recommend ultracode. Commit `200437d` pushed them.
- **Caught by:** App Manager 3, which read the P06.1 row while syncing Notion, before the prompt reached Nathan.
- **Effect:** none on the review. One extra documentation commit, which also became the review head.
- **Correction:** the prompt, the brief and the handoff now recommend max with ultracode, as committed. Nathan picks the level.
- **Prevention:** before recording a level, re-read what the manager has already promised: the handoff, the brief, the Notion rows and its messages to Nathan. Record a conditional level commitment in the brief's "Reasoning levels" when it is made.

### AM3-03 — The classifier given a symbolic head (execution)

- **What happened:** to classify its own documentation delta, App Manager 3 passed `--head HEAD` to the trusted classifier. The documented command resolves `head=$(git rev-parse HEAD)` first. The classifier printed `{"full": true, "reason": "missing-or-invalid-comparison", …}`.
- **Caught by:** the classifier's fail-closed output.
- **Effect:** none. The re-run with the full SHA printed `ordinary-docs-only` for `9ff600f..cd72000`.
- **Prevention:** use the manager workflow's classification command as written.

### AM3-04 — Bare module filenames in Notion (execution)

- **What happened:** the usage-log row for the I1 review named `proof_run.py` and `matrix.py` in plain text. Notion turned `run.py` and `matrix.py` into links to `http://run.py` and `http://matrix.py`.
- **Caught by:** App Manager 3's readback of the row.
- **Effect:** none lasting. The row was rewritten minutes later without filenames.
- **Prevention:** AM2-11's rule covers every filename with an extension, not only `name.md`. In Notion text, describe files without bare filenames.
- **Checklist:** because this repeated AM2-11, the prevention moved into the manager workflow's "Writing to Notion" checklist on 25 September 2026.

### AM3-05 — The review prompt changed after its review head was named (process)

- **What happened:**
  - At 08:03 UTC App Manager 3 committed `c0a34f8` and named it as the head for the exact-head review of P06.1-I1.
  - At 08:08 it added a rule to the review prompt in `9819939`: run every live command from one checkout, one at a time.
  - At 08:09 it gave Nathan the prompt text with that rule, and the text still named `c0a34f8`. The prompt stored at the named head was therefore an earlier text than the one Nathan received.
- **Caught by:** the Dev Manager, in DM-01 finding P2.
- **Effect:** none on any result, because the review had not run. Revision 2's header withdraws the earlier text, and App Manager 3's report on DM-01 and DM-02 tells Nathan not to use it.
- **Correction:** revision 2 of the review prompt names I1's code head, `9ff600f`, and reads the later Markdown records at a named records commit. The review report states the prompt commit it received.
- **Prevention:** workflow step 6, "Name the code head", and step 5, "Batching records".

### AM3-06 — A rule written as in force while its disposition said "pending" (accuracy)

- **What happened:** in the batch at `fa4dc5f`, App Manager 3 wrote the Dev Manager's read of governing Markdown and live prompts into `AGENTS.md`, the charter, the CI policy and the manager workflow without qualification. The same batch's review log disposed of DM-01 P1 as "Accepted, pending Nathan's answer to DM-01 question 2".
- **Caught by:** the Dev Manager, in DM-03 finding G1.
- **Effect:** none. The texts were on the manager branch only, and the rule has a basis in Nathan's direction OD-15.
- **Correction:** the charter cites OD-15 as the authority, and P1's disposition reads "accepted under OD-15", with DM-01 question 2 asking Nathan to confirm or withdraw the rule.
- **Prevention:** a disposition and the governing text that applies it say the same thing. The Dev Manager's read of governing Markdown (charter, "Read before it takes effect") checks this.

### AM3-07 — The principle recorded as conditional, and an interim safeguard left out (accuracy)

- **What happened:** ADR 0003's status and register row OD-14 made the whole S15 decision conditional on the I1 review, including Nathan's principle, which does not depend on it. PF01 section 7 listed the proposed carve-outs but left out the ADR's interim sentence, that no session hides a legally required disclosure or treats a mandated system screen as a defect.
- **Caught by:** the Dev Manager, in DM-03 findings G3 and G4.
- **Effect:** none; the records were on the manager branch only.
- **Correction:** the ADR's status, OD-14 and the brief separate the conditional display rule from the principle, and PF01 section 7 carries the interim sentence.
- **Prevention:** when a decision has parts with different conditions, record each part's condition separately, in every home.

### AM3-08 — Two consistency slips in one batch (accuracy)

- **What happened:**
  - The P06.1 brief gained an owned path for I2b in `.github/workflows/foundation.yml`, while its exclusions still listed `.github/`.
  - Freezing the Claude handoff left `docs/operations/local-development.md` and `docs/operations/environment-inventory.md` pointing to its variable inventory as the current one.
- **Caught by:** the Dev Manager, in DM-03 findings E1 and E2.
- **Effect:** none. No I2b prompt had been written, and no session had relied on the inventory since the freeze.
- **Correction:** the exclusions carve out I2b's one job. The inventory moved verbatim to `docs/operations/environment-inventory.md`, and the frozen handoff keeps a pointer.
- **Prevention:** when a change freezes or moves a document, search for every link to it (`grep -rn '<file name>' docs`) and repoint the ones that treat it as current. When adding an owned path, reread the exclusions.

### AM3-09 — Notion's operating procedure left citing old canon revisions (follow-through)

- **What happened:** App Manager 3 revised PF00 (1.6 to 1.8) and PF01 (1.7 to 1.9) on 25 September and synced Implementation Control's status block each time. It did not update the operating procedure on the same page, whose authority line still cited "PF00 1.4 and PF01 1.5". The procedure also lacked the Dev Manager's relay rules.
- **Caught by:** the Dev Manager, reading Notion after Nathan's direction that operational guidance lives there too (its Notion operational-guidance note).
- **Effect:** Notion named outdated canon revisions as the procedure's authority. No decision is known to have relied on it.
- **Correction:** the operating procedure is rewritten to match the repository and names the commit it was last matched to. The history moved to a sub-page.
- **Prevention:** the repository–Notion match check that ends every records batch (manager workflow, "Notion and the repository").

### AM3-10 — ADR 0004 applied in some documents and missed in others (accuracy)

- **What happened:** the `9b548de` batch applied ADR 0004 (the app's own logical database, OD-18) to PF01, the migration plan, the P11 cases, the domain boundaries, two fixture notes, provider conformance and one row of the resource-ownership record. Six living documents still stated the superseded same-logical-database preference as current:
  - `docs/operations/environments.md`, in five places;
  - `docs/operations/resource-ownership.md`, in its opening paragraph and its persistence section;
  - `docs/operations/configuration.md`;
  - `docs/operations/operational-runbooks.md`, under backup and restore;
  - `docs/architecture/data-model.md`;
  - `docs/architecture/reciprocal-eligibility-fixtures.md`.

  One paragraph of `docs/operations/migration-plan.md` also sat outside its supersession note. PR26's description called the architecture notes aligned.
- **Caught by:** App Manager 3, while collecting the app's HDE requirements for the HDE contract request.
- **Effect:** none known. No session or decision relied on those passages, and P11 has not started.
- **Correction:** each passage now carries a supersession note or a corrected sentence citing ADR 0004. The State of the App snapshot, dated records and source snapshots keep their history.
- **Prevention:** this repeats AM3-08's kind of slip: a change made in one home and missed in others. Its prevention is now a checklist item, "Supersession sweep", in step 5 of the manager workflow.

### AM3-11 — Two sessions offered at once (process)

- **What happened:** App Manager 3 planned the I1 review and the flake diagnosis to run side by side, in the handoff, the brief, the flake prompt's header, PR26 and Notion. In chat, after giving Nathan the review prompt, it told him he could also start the flake diagnosis, whose prompt was in an earlier message.
- **Caught by:** Nathan: *"you MAY NOT give me more than one prompt at a time. Your last message is wholly rejected."* and *"This process needs to be LINEAR."*
- **Effect:** Nathan rejected the messages. By his account he started no review, so no two sessions ran at once.
- **Correction:** Nathan's direction is recorded as OD-29. The handoff, the brief, the flake prompt's header, PR26 and Notion now give a linear order: the flake diagnosis first, then the I1 review.
- **Prevention:** the manager workflow's rule "The process is linear" (OD-29): one prompt per message, pasted in full, for the next task not recorded as complete.

### AM3-12 — A session reported as running when it had not started (accuracy)

- **What happened:** after Nathan wrote *"running it on max"*, App Manager 3 told him the I1 review was running, and later that it was the only task running. Nathan had not started it.
- **Caught by:** Nathan: *"I have not started any review"*.
- **Effect:** the claim was in chat only. No record, prompt or Notion page said the review had started.
- **Correction:** the records give the review as queued after the flake diagnosis.
- **Prevention:** the same rule, which says a session's status comes only from Nathan's own words or its pushed branch.

### AM3-13 — An implementer's claim recorded as established (accuracy)

- **What happened:** App Manager 3 copied I1's statement that the other member receives S15's text *"in realtime `member.updated` events"* into ADR 0003's Context and the brief's "S15: decided", as an established result. The harness could not establish it. B's own channel query raised a local `channels.queried` event carrying the queried state, and the harness searched every recorded event, so its events view found the marker whenever the query did. The manager's verification of I1 read the S15 procedure and did not catch this.
- **Caught by:** the exact-head review of I1, finding 4.
- **Effect:** none on the decision. S15 stands on the channel-query path alone, which the review confirmed live. The display rule already ignores `member.updated` events.
- **Correction:** ADR 0003's Context and the brief now give the event path as unproven and point to I2a, which maps the event types. The evidence record's own lines are corrected in the correction pass, P06.1-C1, with the harness fix.
- **Prevention:** when a record cites a live result as the basis of a decision, name the view or check that produced it, and give an implementer's claim as the implementer's until a review confirms it.

### AM3-15 — A stale branch statement in the handoff (accuracy)

- **What happened:** the handoff's "Branches" section said that every remote branch other than those it named was fully merged into `main`. After App Manager 3 integrated the I1 session branch (`claude/compassionate-lamport-531vtk`) and the flake diagnosis branch (`claude/trusting-mayer-bw6p40`) into PR26, both were merged only into PR26, and the line was not updated.
- **Caught by:** App Manager 3, checking where each remote branch is merged before recording C1's integration.
- **Effect:** none known. No branch was deleted or retired on the strength of it.
- **Correction:** the section now names the session branches merged into PR26, C1's included.
- **Prevention:** an integration batch updates the handoff's "Branches" section in the same commit as the merge's records.

### AM3-16 — A reviewer's suggested rule copied into a prompt unchecked (accuracy)

- **What happened:** C1's exact-head review suggested that RT2 and RT3 give HOLDS only for an `auth`, `permission` or `feature` refusal. App Manager 3 wrote that rule into the C2 prompt, finding 3, as given. It conflicts with the brief's matrix quality rule, under which a refusal counts only when it is an authentication or permission error, and with the harness's own verdict for every other feature refusal, "REFUSED (feature off; not a permission error)". For RT2 it also hides that only the configuration protects B: with typing on, typing events carry any custom field the client adds.
- **Caught by:** C2's own review sub-agent. The C2 session built the rule as directed and reported the conflict as a decision for the manager.
- **Effect:** none on any result. No live run has used the rule, and I1's recorded RT2 result stays as recorded.
- **Correction:** the manager decided that a `feature` refusal in RT2 and RT3 gets "REFUSED (feature off; not a permission error)". The next session that changes the harness makes the change, before any live run, with a test. The C2 review prompt tells the reviewer so.
- **Prevention:** before writing a reviewer's suggested fix into a prompt, check it against the brief's matrix quality rule and the harness's existing verdicts, and say in the prompt where it departs from either.

### AM3-18 — A fix-reversal summary taken at its word (accuracy)

- **What happened:** verifying C2, App Manager 3 ran `checks/fix_reversals.py` and recorded its summary, "reversals: 99, not demonstrated: 0". It told Nathan that all 99 reversals fail without their fix and pass with it, and wrote "99 of 99 fix reversals" in the Work Register. One reversal, C1's "F2 end of run", no longer reverted its fix at C2's head: its pattern matched inside a line C2 had indented further, the edited file did not compile, and the script counted the `SyntaxError` as a failing test. The C1 review had checked each reversal's failure reason; the manager's verification of C2 did not.
- **Caught by:** the exact-head review of C2, finding 3.
- **Effect:** none on the harness. The fix that reversal covers is still tested: with a correct reversal its three tests fail. The real count is 98 of 99 demonstrated.
- **Correction:** the evidence record and the Work Register now give 98 of 99. P06.1-C3 repairs the reversal and makes the script count an edit that does not compile as "not demonstrated".
- **Prevention:** when verifying a fix-reversal run, check each reversal's failure reason, not only the summary, until the script itself rejects an edit that does not compile.

### AM3-19 — "No Stream variables" for a session started before OD-28 (accuracy)

- **What happened:** the DM-04 consultation told the Dev Manager "The Stream variables are not set for this read", and its header, the handoff and Notion said "No Stream variables" for the read. The Dev Manager's session started on 25 September at 09:00 UTC, while the variables were set in the `Glow app` environment, and a session's environment is fixed when it starts. AM3-17 had found the same for App Manager 3's own container, and the manager did not apply it to the Dev Manager's.
- **Caught by:** the Dev Manager's names-only check, DM-04 finding 10. The consultation also told it to report any `STREAM_*` name it found and never read or use the value, and it did so.
- **Effect:** none known. The Dev Manager never read, printed or used the values, and its read needed none. The planned rotation of the secret at P06.1's close covers every container started while the variables were set. (OD-37, 29 September, later dropped that rotation as a close-out item.)
- **Correction:** the consultation's header, the brief, the handoff and Notion now say that none were added for the read, and that the Dev Manager's container holds them.
- **Prevention:** this repeats AM3-17's lesson, so it is now a checklist item in the manager workflow, step 3 ("Prompt"): a prompt or consultation says which credentials a session holds, not only which it needs, and for a session started while the variables were set it says "none added", never "none present".

### AM3-20 — "TypeSafe can't pick a model" (accuracy)

- **What happened:** reporting OD-30 to Nathan on 26 September, the manager wrote: *"TypeSafe is unchanged: it only scores the level and can't pick a model, so its readings stay comparable with earlier ones."* The first half was a choice: the v4 request stays unchanged. The second half was false. A TypeSafe Choice question picks one of a set of options, and the v4 request already asks one, `shape`. The records made only the narrower statement, that v4's reading names no model.
- **Caught by:** Nathan: *"typesafe should be able to pick a model. there must be some semantic rules that can help this"*.
- **Effect:** none on any session. I2a's prompt was given before OD-30, so no prompt lacked a model reading it should have had.
- **Correction:** the model question m1, a separate TypeSafe request, so v4 stays comparable. Its option criteria are the semantic rules for each model. Its decision rule and the manager's labels for 11 past sessions were saved in the Notion usage log before the first run, and the calibration agreed on all 11. The manager workflow, OD-30 and the usage log now describe both readings.
- **Prevention:** before telling Nathan that a tool cannot do something, check the tool's documentation. Say what the current setup does, not what the tool cannot do.

### AM3-21 — A Notion note contradicted the record (accuracy)

- **What happened:** on 27 September, at about 01:21 UTC, the manager wrote the I2a review's outcome into its row of the Notion usage log. The note said that the manager had "corrected … one line reference in nit 6". Its verification in the evidence record, written minutes earlier, keeps that reference: the line names the run as the guard's scope, which is what the record says.
- **Caught by:** App Manager 3, re-reading the row.
- **Effect:** the row misstated the record for about a minute.
- **Correction:** the note was rewritten from the evidence record at about 01:22 UTC and read back.
- **Prevention:** write a Notion note from the committed record, not from memory of the work. The Notion checklist's readback step ("compare it with what was intended") compares with that record.

### AM3-22 — PF01 §7 left calling the display rule conditional (accuracy)

- **What happened:** PF01 §7, written at `fa4dc5f` on 25 September, said Nathan accepted the display rule for S15 *"conditional on the exact-head review confirming S15"*. The I1 review confirmed S15 the same day. App Manager 3's batch that recorded the review (`b9df3a2`, 26 September) updated OD-14's row and ADR 0003, but its supersession sweep missed PF01 §7. App Manager 4 and App Manager 5 did not catch it either, and App Manager 5's DM-07 consultation named PF01 among the files to read without finding it.
- **Caught by:** Dev Manager 2, DM-07 finding 1.2, as a condition before PR27 merges.
- **Effect:** the manager branch's PF01 stated a condition already met, from 26 to 29 September. It never reached `main`, and no decision rested on it: OD-14's row and ADR 0003 said the rule stands.
- **Correction:** PF01 1.11 replaces the clause with the Dev Manager's text, "confirmed live by the I1 review on 25 September 2026".
- **Prevention:** it repeats AM3-08 and AM3-10, supersession sweeps that missed a document, and the manager workflow's step 5 already carries the sweep: search the repository for the old wording. When the decision is that a condition is met, the old wording includes the condition's own words, here "conditional on", not only the rule's name.

### AM3-23 — M03 kept "the ten questions are with Nathan" (accuracy)

- **What happened:** the Work Register row M03's *Next Action*, written after App Manager 3 applied DM-03 on 25 September, ends: *"The Dev Manager's ten questions are with Nathan."* Nathan answered that day; DM-01's questions 2 and 3 were not among his answers (DM-04 finding 12), which the Dev Manager page records. The row was not updated. On 28 September App Manager 5 corrected M03's two links (AM5-07) without reading its *Next Action*.
- **Caught by:** Dev Manager 2, DM-07 finding 8.
- **Effect:** none on any decision: the Dev Manager page, the register and the repository gave the answers.
- **Correction:** M03's *Next Action* now says what Nathan answered, what stays open and that DM-07 made the close-out read; read back.
- **Prevention:** the Notion checklist's old-wording query already reads every property. A manager that edits a row reads every text property of that row too, not only the one it came to fix.

## App Manager 4

### AM4-01 — Two unexplained items put to Nathan (process)

- **What happened:** App Manager 4's first report, which gave Nathan revision 2 of the I2b prompt, carried a line "Waiting on you, standing: confirmation of the shared-restore risk ADR 0004 records as accepted; the HDE contract date (OD-23). Neither blocks I2b." It copied the handoff's waiting checkpoint without saying what either item was, what would break without it, or what Nathan could do. The reporting guidance the start prompt names says a request is never phrased as an observation, and that an item is put to Nathan only with what it does, its impact, the options and a recommendation.
- **Caught by:** Nathan: *"I don't know enough about what this means. If you have questions, they need to go to dev manager. I am not sending any implementation prompts with mysterious outstanding items"*.
- **Effect:** Nathan did not start I2b from that message. No record or prompt was wrong.
- **Correction:** his direction is OD-32. Both items leave the waiting checkpoint: ADR 0004's accepted restore risk is a question for the Dev Manager's close-out read, and the HDE contract date stays in Nathan's own process, where OD-23 put it. The prompt was given again, alone.
- **Prevention:** OD-32's rule in the manager workflow and the start prompt: every item put to Nathan is explained or not put; questions go to the Dev Manager first.

### AM4-02 — A choice offered between identical options (process)

- **What happened:** the message that gave Nathan I2b's prompt said "my call is Fable 5.1, extra high; TypeSafe agrees. You pick." There was nothing to pick.
- **Caught by:** Nathan: *"For the record, you asked me to pick between 2 identical options."*
- **Effect:** none on the session; he ran it on Fable 5.1 at extra high.
- **Correction:** none needed in the records.
- **Prevention:** when the manager's call and TypeSafe's readings agree, the message states the model and level as the recommendation and asks nothing. Only a disagreement is put to Nathan, with both readings.

### AM4-03 — Scoring requests too thin for an informed reading (process)

- **What happened:** the TypeSafe requests inherited and written by earlier managers (v4, m1) described each level in one line, said nothing about what a level costs or does on either model, and v4's second question was written for another project; m1's model criteria were the manager's own rules with no vendor facts. The readings looked precise but rested on almost no information, and the manager's call carried an unmeasured claim ("a lower level on Fable often matches a higher one on Opus") as if it were known.
- **Caught by:** Nathan: *"I am feeling less trust about the scoring. There is a huge gap between fable extra high and opus extra high. ... It's important that your semantic query contains enough information for actual informed decisions."*
- **Effect:** the I2b review prompt was re-scored before it started; no session ran on a wrong reading.
- **Correction:** OD-33; the [reasoning-strength matrix](../planning/reasoning-level-matrix.md) researched from Anthropic's documentation, and the request v5 that carries it, pre-registered and calibrated before use; the manager workflow's step 3 no longer states the unmeasured claim.
- **Prevention:** a scoring request carries the researched facts a reader would need to decide; any change to it is a new version with a rule saved before its first run; a claim about the models is written as judgement unless a source is cited.

### AM4-04 — Overrode the owner's ladder and presented unreachable readings as informed (process)

- **What happened:** Nathan directed a six-rung ladder with ultracode at the top. The manager built v5 around Anthropic's definition instead, told him ultracode "is not a sixth level", worded the max rung so that no review or implementation in this project could reach it, and then presented v5's reading (Opus 5.5 at extra high for the first review of an 11,700-line new system) as a defensible, informed reading. The manager also put its own model judgement to Nathan as a recommendation when no evidence supports an agent's judgement of model strength.
- **Caught by:** Nathan: *"that is stupid. Ultracode needs to be in there, and max needs to be reachable"*; *"extra high is NOT the most capable model in any sense"*; *"I don't really care about your judgment I am only interested in the typesafe score"*.
- **Effect:** the I2b review had not started; no session ran on the v5 reading. A day of scoring revisions.
- **Correction:** OD-34; request v6 with six rungs, built from third-party benchmarks and tested live for reachability before adoption; every recorded prompt re-read with it; the outcome column dropped; the reading produced by the Claude skill `typesafe-scoring`.
- **Prevention:** an owner direction about the shape of a record or a scale is applied as given; a fact from documentation that seems to contradict it is stated once, in one sentence, and does not change the design. A scorer's request is accepted only after a live reachability test on archetype texts, never on the manager's reading of its wording. The manager's own strength judgement is recorded for comparison and never put to Nathan.

### AM4-05 — Two slips in the handover records (accuracy)

Recorded by App Manager 5, after App Manager 4's handover.

- **What happened:**
  - App Manager 4's handover commit `4bc1cd2` added to the next-manager start procedure: "For App Manager 5 the outgoing manager has filled both in below the line, so Nathan pastes the text as it is." The text below the line still carried `<N>` and `<BRANCH>`.
  - AM4-03 and AM4-04 had full sections but no summary rows, against this log's rule that every mistake gets one.
- **Caught by:** App Manager 5, reading the handover commit `2a86c8e` at its start.
- **Effect:** none known. The start text Nathan pasted into App Manager 5's session had both filled in (App Manager 5, `claude/stoic-carson-66gdig`), so no session received the placeholders.
- **Correction:** the start procedure's note now says the text keeps both placeholders and that the current handoff names the branch; the three summary rows are added.
- **Prevention:** before a handover commit, read the start procedure below the line as the successor will receive it, and check that every section of this log has its summary row.

### AM4-06 — The I2b verification repeated an underivable count and missed a wrong one (accuracy)

Recorded by App Manager 5, after I2b's exact-head review.

- **What happened:** App Manager 4's verification of I2b, in the evidence record, accepted "fifteen live commands against the plan's eleven" in its dispositions. It copied I2b's "the plan's eleven", which no count of the I2b prompt's section 5 gives: that section names thirteen commands, the reserve rerun included. The same verification ran mypy and printed "53 source files", but did not flag I2b's "Checks" item 4, which says 55.
- **Caught by:** the exact-head review of I2b, nits 5 and 6.
- **Effect:** two wrong numbers in the record. No verdict or decision rests on either.
- **Correction:** the disposition bullet is corrected in place and marked. P06.1-C4 corrects I2b's own two sentences, marked.
- **Prevention:** a verification derives every count it repeats from its source, and compares each of its own check outputs with the figure the report under verification gives for the same check.

### AM4-07 — A job count left at four when I2b added the fifth (accuracy)

Recorded by App Manager 5, at P06.DB's integration.

- **What happened:** I2b added the Foundation job "Stream proof checks", integrated at `55b2238`. App Manager 4's integration updated the CI policy's job list and counts, but `docs/operations/build-and-deploy.md` kept "All four must pass on the actual proposed candidate before merge", naming P03's four jobs.
- **Caught by:** App Manager 5's supersession sweep when P06.DB added the sixth job.
- **Effect:** one runbook sentence understated the jobs a merge needs. The CI policy, which governs, was right, and the gate required every job.
- **Correction:** the sentence now defers to the CI policy's list (`541ec99`).
- **Prevention:** when a job is added, the sweep searches every document that names a job or counts them (for example "API artifact checks", "Stream proof checks", "four", "five"), not only the CI policy.

## App Manager 5

### AM5-01 — The classifier given a short SHA again (execution)

- **What happened:** checking its own records batch `47fe797`, App Manager 5 ran the trusted classifier with `--base 70a55c9`, a short SHA. The policy answered `missing-or-invalid-comparison`, full scope, as it does for any comparison it cannot read. The re-run with full SHAs gave `ordinary-docs-only`, 8 paths. It repeats AM3-14.
- **Caught by:** the classifier itself.
- **Effect:** none; the batch was already committed, and the full-SHA result is the one recorded.
- **Correction:** none needed.
- **Prevention:** because it repeats AM3-14, whose prevention was never written down, the rule is now a checklist item in the manager workflow's "Classification (trusted base policy)": pass full 40-character SHAs from `git rev-parse`.

### AM5-02 — A uses-table row kept "Nathan's pick pending" after his pick (accuracy)

- **What happened:** when Nathan picked Opus 5.5 at high for C4, App Manager 5 set the *Nathan's pick* column of C4's row in the TypeSafe uses table (Notion), but left the row's *PR* text ending "Nathan's pick pending", written when it scored the prompt. The row contradicted itself until the records batch that integrated C4.
- **Caught by:** App Manager 5, reading C4's row while writing the C4 review's row.
- **Effect:** none on any decision: the *Nathan's pick* column, which the table's default view shows, was right. No other row carries a pick status in its *PR* text.
- **Correction:** the row's *PR* text now says that Nathan picked Opus 5.5 at high and where C4's result is recorded; read back.
- **Prevention:** a row's *PR* text carries no pick status; only the *Nathan's pick* column does. The C4 review's row follows that.

### AM5-03 — Two Work Register texts left stale (accuracy)

- **What happened:** two Notion texts kept a state that App Manager 5's own batches had changed:
  - the P06.1 row's body said "I2b (its review in flight)". The takeover batch wrote it while the review ran; the batch that recorded the review (`47fe797`, `2c2d450`) updated the row's *Next Action* but not its body;
  - the D10 row's *Next Action* said D10 is "on the manager branch until PR26 merges". The takeover batch replaced PR26's branch links across Notion, but not this text, and PR26 is closed.
- **Caught by:** App Manager 5, querying the Work Register for old wording after finding AM5-02, while syncing the batch that integrated C4.
- **Effect:** none on any decision: the rows' other fields, Implementation Control and the repository were right.
- **Correction:** both texts corrected and read back.
- **Prevention:** it repeats AM5-02, a status left stale in a field the update did not touch, so the prevention is now an item of the manager workflow's checklist "Writing to Notion": when a status changes, update every property and page body that states it, then query the touched databases for the old wording before the batch ends.

### AM5-05 — The brief's bound for the C4 review left out a class (accuracy)

- **What happened:** the brief's entry for the C4 review, written with its prompt at `c7fd0a9`, summarised the classes that get another correction pass. Where the prompt says "lose an observed FAIL or DOES NOT MEET", the entry said "lose an observed FAIL", so its "only" excluded a class the prompt includes.
- **Caught by:** App Manager 5, comparing the entry with the prompt before giving the prompt to Nathan.
- **Effect:** none: the review follows its prompt, and no report has yet been dispositioned against the brief.
- **Correction:** the entry now uses the prompt's wording.
- **Prevention:** a brief entry that restates a prompt's bound uses the prompt's words, not a summary.

### AM5-06 — The C5 verification missed a wrong reachability claim (accuracy)

- **What happened:** App Manager 5's verification of C5 said "no slip found" in C5's own section. That section's "Deviations and limits", like `README.md:398`, said the non-header residuals, JSON nested two levels deep in a query value among them, are reachable only through a request-options argument. A `product` step's `params` can carry the nested JSON too, past `validate` and the runner's check. The wording dates from C4's README, and the manager's verification of C4 had passed that list to the review without testing it.
- **Caught by:** the exact-head review of C5, its nit 1.
- **Effect:** none on any result or decision. The residual is C4's, and the C4 review assessed it. No case or harness op carries nested JSON, and whether Stream decodes JSON nested inside a JSON query value is not known.
- **Correction:** `README.md:398` and the evidence record at lines 3600, 4107 and 4191 are corrected in place and marked. The manager confirmed the claim offline with the real `productRefusal`: one level of nested JSON is refused, two levels pass.
- **Prevention:** when a record says a residual is reachable "only through" one route, the verification tests the claim against every input that reaches the checked requests (for the runner's product check, the `product` op's own `params` and body first), not only against the named route.

### AM5-07 — Four Work Register links left on the old branch and PR26 (accuracy)

- **What happened:** two Work Register rows kept link properties from before App Manager 5's takeover. D10's *Plan Reference* pointed at the Dev Manager charter on `claude/stoic-carson-66gdig`, App Manager 4's branch, and its *Evidence* at PR26, closed on 27 September. M03's *Plan Reference* and *Evidence* pointed at the charter and the review log on the same branch. The takeover batch replaced the old branch's links in page bodies, not in properties. When AM5-03 corrected D10's *Next Action*, its old-wording query read only the rows' *Next Action* text.
- **Caught by:** Dev Manager 2, in its start note and in DM-06 (finding 6), for D10. App Manager 5 found M03's two while running the prevention below over every link property of the Work Register.
- **Effect:** none on any decision. The old branch still exists, so every link resolved, to the superseded head; Implementation Control, the rows' other fields and the repository named the manager branch and PR27.
- **Correction:** D10's *Plan Reference* now points at the charter on `claude/magical-wozniak-yfmmx2`, and its *Evidence* at PR27; M03's two links point at the charter and the review log on the same branch; all read back.
- **Prevention:** it repeats AM5-03, so the manager workflow's checklist item for "Writing to Notion" now says that the old-wording query reads every property, links and URLs included, not only text: when a branch or PR is replaced, it looks for the old branch name and PR number in each.

### AM5-08 — "Within 7%" for a bound of 7.2% (accuracy)

- **What happened:** the economics discovery's verification computed that, if the dashboard's Chat count excludes I2b's Video and Feeds requests, Stream counted up to 162 more calls than the sessions' ledgers, "about 7%". The disposition, the brief, the review log's DM-06 section, the DM-07 consultation, Notion's P06.1 row and App Manager 5's report to Nathan then said "within 7%". 162 is 7.2% of the ledgers' 2,261 calls.
- **Caught by:** Dev Manager 2, DM-07 item 5, as a wording nit.
- **Effect:** none on any decision: either way the difference is about 0.1% of the plan, and the verification itself said "about".
- **Correction:** "within about 7%", with "at most 162 calls", in the brief, the evidence record, the review log and Notion; each corrected line says so.
- **Prevention:** a figure carried from a verification into a summary keeps its hedge ("about", "up to") or its exact value; a bound is never rounded down into "within".

### AM5-09 — The P06.1 row's page body left saying DM-07 was next (accuracy)

- **What happened:** the batch that recorded DM-07 (`c775f39`) rewrote the P06.1 row's *Next Action* and read it back with a database query, which returns properties only. The row's page body, which also states the item's status, kept *"The Dev Manager's close-out read (DM-07) is next."*
- **Caught by:** App Manager 5, fetching the whole row page while syncing the next batch (`7fac723`).
- **Effect:** none on any decision. The row's properties, Implementation Control and the repository were right; the body was stale for about 17 minutes.
- **Correction:** the body now says that DM-07 is done and that Nathan answered the close-out; read back.
- **Prevention:** it repeats AM5-03, whose item in the Notion checklist already names page bodies; the readback that missed it used a query. A row whose status changes is read back by fetching its whole page, body included.

### AM5-10 — The P06.1 brief's headline left "in progress" after the merge (accuracy)

- **What happened:** the post-merge batch (`041a081`) marked P06.1 done in the brief's Work ID line and at the end of its status paragraph, but left the brief's first line, "**Status: in progress.**", unchanged.
- **Caught by:** App Manager 5, in its supersession sweep before the Notion sync of that batch.
- **Effect:** none on any decision. The brief contradicted itself for about ten minutes; the evidence record, the handoff and the register were right, and nothing had yet been sent that reads the brief.
- **Correction:** the headline now says done, with the merge commit and the receipt.
- **Prevention:** the supersession sweep already covers it, since the headline treated the old state as current; the sweep ran after the commit instead of before it. It now runs before each records commit, and for a status change it searches each changed document's status lines as well as the old wording.

### AM5-11 — A second Work Register row for P06.DB (accuracy)

- **What happened:** syncing the post-merge batch (`041a081`), App Manager 5 created a row for P06.DB in the Work Register without searching it first. An earlier manager had already added P06.DB's planned-stage row, "Planned", when Nathan approved the item (OD-17), so a query by Work ID returned two rows.
- **Caught by:** Dev Manager 2, DM-08 section 8.
- **Effect:** none on any decision. The new row was the one kept current; the older row stayed "Planned" for under an hour after the item started.
- **Correction:** the older row now sits under the current row as a page, its text kept in its body, so the Work Register holds one P06.DB row.
- **Prevention:** the manager workflow's Notion checklist now asks for a search of the database by Work ID before a row is created, and the old-wording query also looks for duplicate Work IDs (DM-08 section 8).

### AM5-12 — Two unchecked attributions in the P06.DB verification (accuracy)

- **What happened:** App Manager 5's verification of P06.DB, in its evidence record, made two attributions without checking them:
  - it said the results upload used the `actions/upload-artifact` commit that API artifact checks already used. The job that already used it is Mobile checks, in its step "Save empty-form layout evidence";
  - it repeated the session's statement that the log's three `***` were all `actions/checkout`'s token masking. Line 152 is `actions/setup-python`'s `token` input.
- **Caught by:** the P06.DB exact-head review: F6 names Mobile checks, and its log confirmation names setup-python. The manager then found both slips when checking the review's statements.
- **Effect:** two wrong attributions in the record. No verdict rests on either: the pin is the same commit, and no mask stands for a password. The review prompt, given as written, repeats the second one.
- **Correction:** both verification bullets are corrected in place and marked; the session's statement is added to the verification's "Corrections to this record".
- **Prevention:** a verification states which job or step a line belongs to only after reading it there. It is the same rule as AM4-06's, which asks for every count to be derived from its source.

### AM5-13 — The P06.DB brief's headline left at "next" after two picks (accuracy)

- **What happened:** recording Nathan's pick for the P06.DB exact-head review (`49525a6`), App Manager 5 marked the review in flight in the brief's Sessions and in the handoff. The brief's headline status still said "its exact-head review is next". Recording his pick for P06.DB-C1 repeated it before the push: the headline said C1 "is next".
- **Caught by:** App Manager 5, in its supersession sweep before pushing the C1 pick.
- **Effect:** none on any decision. The first slip stood on the pushed branch until `4511bbc` rewrote the headline the same morning. The second was never pushed. In both batches the brief's own Sessions and the handoff said in flight.
- **Correction:** the headline now says C1 is in flight. The first slip needed none, since `4511bbc` had replaced the line.
- **Prevention:** it repeats AM5-10, whose prevention (at a status change, read each changed document's status lines) was written only in this log. It is now part of the supersession-sweep item in the manager workflow's step 5, "Verify and integrate", which also says to run the sweep before each records commit.

### AM5-14 — The C1 prompt did not say to wait for the code run before pushing again (accuracy)

- **What happened:** the P06.DB-C1 prompt (section 4, item 6) made the push run of the session's last code commit its evidence and expected records commits after it. It did not tell the session to wait for that run to finish before pushing again, although the CI policy records that runs of the same branch cancel each other. The session pushed its records 50 seconds after its code. The second run waited until the code run's gate had finished, then started, and the code run, whose eight jobs had all passed, was marked `cancelled`. No earlier session prompt carried the rule either.
- **Caught by:** the P06.DB-C1 session, which reported the label and its cause and asked for a decision; Nathan then asked whether the cloud environment was the cause.
- **Effect:** the run of record's run-level status reads `cancelled`, although every job passed. It needed a decision and an explanation, and it raised the question of whether the proof needs another environment; it does not. No result changes.
- **Correction:** the manager accepted the run's job results as C1's run of record and recorded the label as a limit (the evidence record, "Manager verification of P06.DB-C1"). PR28's pull-request run on the integrated head runs every job again.
- **Prevention:** it repeats the mechanism of AM5-04, a later push cancelling a code run, this time through a session's pushes. The rule is now a checklist item in the manager workflow's step 3, "Say when a session may push again": a prompt whose session pushes code and then records tells it to push nothing more until the code run has finished.

### AM5-15 — The C1 prompt's start gate could not tell that its work was done (accuracy)

- **What happened:** the P06.DB-C1 prompt's start gate fast-forwarded to its start commit, `4511bbc`, and checked that the proof package had not changed between the reviewed head and that commit. Both stay true of that commit, so the gate passes however late the prompt is run. On 4 October Nathan started a session from it, on Opus 5.5 at extra high, in place of C1's review. It passed the gate and made the whole correction pass again on its own branch, `claude/magical-goldberg-ie0j16`, five days after C1 had been verified and integrated at `ea21ac8`. Every earlier prompt used the same gate, the one the manager workflow's prompt template gives ("fetch, fast-forward to the named SHA, verify"). Reading Nathan's message "ran in opus 5.5 extra high" as the start of C1's review, the manager recorded the review as in flight (`d27519b`).
- **Caught by:** App Manager 5, verifying the second session's report, whose first line named the correction prompt's revision and start commit.
- **Effect:** a full correction session, a Foundation run and a branch that PR28 does not use. C1's review has not run yet. `d27519b`'s records and the uses table named the wrong session the same day. No code or evidence on PR28 changed. The second session's report also raised two points that hold for PR28's code; they are now in C1's review.
- **Correction:** the second run is recorded and not integrated (the evidence record, "A second run of the C1 correction prompt"). The review's records are corrected, and revision 2 of C1's review prompt has a start gate that checks the live branch.
- **Prevention:** the manager workflow's step 3 has a new item, "Make a stale prompt stop at its start gate", and the prompt template's start-gate line points to it. The gate also checks the live manager branch and stops if the work the prompt asks for has already landed there.

### AM5-16 — The C1 verification missed the accumulated rows in local run 2 (accuracy)

- **What happened:** C1's section of the evidence record gives its local run 2, in the same database as run 1 with "rows accumulating", every race at 200 of 200 overlaps. The stress run's run tag is fixed (`design:stress`), so each of run 2's per-iteration reads also returned run 1's rows, and an iteration counted as an overlap when either run's writers overlapped. F1 was a read that took in rows from outside the measured race; this is the same kind of read across runs. The manager's verification read the section and the diff and did not raise it.
- **Caught by:** App Manager 5, checking the second session's "one run per database" limit against C1's code.
- **Effect:** none on evidence. Local runs are iteration, not evidence, and the job's database is new in each run. C1's section carried counts that are not run 2's own, and revision 1 of C1's review prompt did not ask about the limit.
- **Correction:** the evidence record's section "A second run of the C1 correction prompt" corrects the statement and records the limit, and revision 2 of C1's review prompt asks about it (focus area 10).
- **Prevention:** when a fix narrows a read to its own rows, the verification checks every way other rows can still reach it: other races, other iterations, and other runs in the same database.

### AM5-17 — The correction for AM5-16 stopped at the overlap counts (accuracy)

- **What happened:** correcting C1's local run 2 (`cbb3ff7`), the manager said that its overlap counts took in run 1's rows. The same rows reach that run's stress controls and the oracle parts of its forced controls, which the correction did not name. The implementation's local run 2 had also reused its database, and the in-place correction in its row still said its first race's 200 was established; neither the verification of C1 nor the correction noticed.
- **Caught by:** C1's exact-head review, R5.
- **Effect:** none on evidence, since local runs are iteration, not evidence. Two record statements were incomplete or wrong for a day.
- **Correction:** the evidence record's "Exact-head review of P06.DB-C1", under "Corrections to this record".
- **Prevention:** it repeats AM5-16, so the prevention is now a checklist item in the manager workflow's step 5, "Follow a stray read to every result": a verification or correction that finds such a read lists every result computed from those rows and every record that reports one, and checks each.

### AM5-18 — The P06.DB brief took loopback as the database boundary (accuracy)

- **What happened:** the brief the manager wrote for P06.DB (revisions 1 and 2) gave the proof's settings an explicit loopback host as their guard against any other database (D1). For local runs it said the recipe "connects to no other database" (D4, condition 2). A loopback host or a Unix socket names a route, not a database. An SSH-forwarded or other local server passes the check, and the documented first command, `migrate`, changes it before `run`'s server checks. The code was built to the brief, and the manager's verification, DM-08 and both exact-head reviews accepted the guard as written.
- **Caught by:** Codex's second code review of PR28, of `9bcec21` (CX3, P1).
- **Effect:** no evidence changes: every run of record used the CI job's own container, which is safe by construction. PR28 did not merge. It needs a correction pass, P06.DB-C2, its exact-head review and the Dev Manager's read of the design first (DM-10).
- **Correction:** brief revision 3 adds the run's marker to D1, D3 and D4. The disposable database's creator sets a marker generated for the run as the database's comment, and the proof refuses any database without it. See the evidence record, "Codex's second code review, of `9bcec21`".
- **Prevention:** when a brief draws a protected boundary, it says how the code proves the boundary holds, by checking the protected thing itself (here, which database it is) rather than a stand-in for it (the route to it), and the review prompt's classes test that proof.

### AM5-19 — The C2 prompt's departure named no database for its query (accuracy)

- **What happened:** writing the C2 prompt (revision 1, `d50f334`), the manager found that DM-10's 2.3 query counts PostgreSQL's own `pg_toast` relations even in a new database, and replaced it with a query that also excludes the `pg_` schemas. The replacement said what to count, but not where. `pg_class` holds one database's relations, and the prompt did not say that the step runs the query in the proof's database. A step that ran it from another database, such as `postgres`, would pass whatever the wrong-marker `migrate` did to the proof's database. The prompt also gave the prefix test in words, "starts with `pg_`", without the SQL; written as `LIKE 'pg_%'`, the test treats `_` as a wildcard and also excludes a schema such as `pgx`, which a role can create.
- **Caught by:** Dev Manager 2, DM-11 item 1, before the prompt ran: "Its query could be satisfied from the wrong database, and its prefix test is a wildcard."
- **Effect:** none on evidence or code: revision 1 never ran.
- **Correction:** revision 2 of the C2 prompt replaces the departure with DM-11's words: the query runs with `psql -d` naming the proof's database, the prefix test is `starts_with(nspname, 'pg_')`, and every schema's count must be the same before and after the wrong-marker `migrate`.
- **Prevention:** when a prompt specifies a database check, it names the database the check runs in and gives the exact SQL test, and asks of the check what 2.3 asks of the exit code: whether it could pass for the wrong reason.

### AM5-21 — The P11 plan said C2's run had "the same results" (accuracy)

- **What happened:** recording C2's run of record at its integration (`dd67696`), the manager wrote in the P11 plan's "Early partial evidence" that Foundation run 37262466651 "reran the whole plan with the same results". Its outcome was the same: 55 of 55 cases, every control failing by its declared signal, and zero violations in the design's rows. Its numbers were not: 526 submissions against C1's 617, and 197 to 200 overlaps per race against 174 to 200.
- **Caught by:** C2's exact-head review (F3).
- **Effect:** none on a mark: DB06's entry gives each run's own overlap counts, and the marks stand as worded. A reader could have taken the counts to repeat.
- **Correction:** the sentence now says "the same outcome" and names it, in the review's words.
- **Prevention:** a record that compares two runs of a timing-dependent suite says what is the same (the plan, the outcome) and gives each run's own counts; "the same results" is not used for them.

### AM5-22 — The handoff kept naming the brief's revision 2 (accuracy)

- **What happened:** the handoff's current-item line, written on 29 September, says the P06.DB brief is "revision 2, which applies the Dev Manager's read (DM-08) as written". Revisions 3 (CX3's marker), 4 (DM-10's conditions) and 5 (DM-11's words) followed on 5 October, each in a records batch that also changed the handoff, and the line stayed.
- **Caught by:** App Manager 5, in the supersession sweep for revision 6, which looked for the brief's revision numbers in living documents.
- **Effect:** none on a decision or a prompt: the line links the brief, whose status line names its current revision, and every prompt names the revision it read. A successor reading only the handoff would have taken revision 2 as current.
- **Correction:** the line named revision 6, the current one at the correction, and points to the brief's status line for the others.
- **Prevention:** it repeats the mechanism of AM5-10 and AM5-13, a status fact left behind in another document. The supersession sweep in the manager workflow's step 5 already requires a search for the old wording; when a brief's revision changes, the old wording includes its previous revision number, so the sweep searches the living documents for it.

### AM5-23 — A "hold" option with nothing for it (process)

- **What happened:** the report of PR28's merge put P06.2's start to Nathan as two options, "Start P06.2 now" and "Hold. No new work starts", and recommended starting. Nothing in the record argues for holding: P06.DB's CI and reviews are clear (OD-08), both proofs P06.2 depends on are done, P06.1's evidence record says P06.2 needs no approvals, and nothing else waits on him. The message needed only his direction, which OD-12 requires before other feature work starts.
- **Caught by:** Nathan: *"why would I want to hold?"*
- **Effect:** none on the work: nothing had started, and P06.2 still needs his direction. It cost him a message.
- **Correction:** the answer says that nothing argues for holding and asks for his direction alone.
- **Prevention:** it repeats AM4-02's mechanism, a choice with nothing to choose, whose prevention covered only the model and level. The manager workflow's rule "Nothing unexplained goes to Nathan" now says that an option goes to him only with what it gains, and that when the record gives no reason for the alternative, the item asks for his direction alone.

### AM5-24 — Merged branches left for Nathan to find (follow-through)

Recorded by App Manager 6 on App Manager 5's behalf, from App Manager 5's relayed message: App Manager 5 writes nothing after its handover commit `a1eb9dc`.

- **What happened:** the retirement of `app-builder-1/p05-1-birth-diagnostics` fell due when the flake fix merged, with PR27 at `47db18d` on 29 September (the flake-diagnosis evidence record retired it "after PR26 merges", and PR27 replaced PR26). The handoff carried the retirement without asking Nathan, the only person who can delete a branch. No manager set up a cleanup of merged branches, though OD-09 gives the managers branch management. By 5 October the repository had 38 branches, 33 of them fully merged into `main`.
- **Caught by:** Nathan on 5 October: *"I am a little concerned about this bad branching hygiene"*.
- **Effect:** none on code or evidence: no repository link named any of the old branches. Some old Notion pages linked to files through a branch name and needed repointing before the deletion. It cost Nathan the cleanup by hand.
- **Correction:** App Manager 5 gave Nathan the list of 34 deletable branches and a delete command; he deleted them on GitHub on 5 October, with `claude/magical-goldberg-ie0j16`, the second run of C1's prompt, never integrated (the handoff of 5 October recorded the result; the current handoff now lists only live branches). Notion links through deleted branches were repointed to `main` or commit-pinned URLs.
- **Prevention:** the manager workflow's step 7 now reports the branch state at each merge, and links Notion only to `main`, a commit ID or the manager branch (OD-39). The work item M04 automates the deletion of merged branches.

## App Manager 6

### AM6-01 — Watching CI that belongs to the worker (process)

- **What happened:** Stage A's push run 37372546600 had no run of record (three jobs got no runner). Integrating the branch, App Manager 6 named PR29's run on the integrated head as the run of record, subscribed the manager session to PR29's CI events and scheduled a check-in to watch it, rather than giving Nathan a relay message for the worker session, whose prompt (section 4, item 6) owns the run of record.
- **Caught by:** Nathan: *"you should not be watching CI, that work belongs to the worker session, so give me a response to pass on"*.
- **Effect:** none on the work: the runs had not finished, and the manager recorded no result from them. It cost Nathan a message, and it put the manager into the implementation work it never does.
- **Correction:** the subscription is removed and the check-in deleted. The relay message gives the run of record back to the Stage A session.
- **Prevention:** when a session's report leaves its run of record open, the manager answers with a relay message to that session; it never watches or chases the session's CI itself. The manager workflow's step 5 reads the CI of the manager branch's own pushes only.

### AM6-02 — A figure read from a cut-off listing (accuracy)

- **What happened:** verifying B1-C1's run of record, App Manager 6 listed the race lines of the database job's log through `head -20` and wrote "Its races ran 7 to 23 s each" in the evidence record. The listing held all 12 of the reference design's races and 8 of the adapter's 15; the 7 it cut off included the slowest, `race.withdraw_high` at 29.7 s, 0.3 s under the per-race cap.
- **Caught by:** B1-C1's exact-head review, finding 1.
- **Effect:** the record understated the job's time margin, which is the basis for deciding when the job's budget goes to the Dev Manager. No result changed, and nothing was decided on it before the correction.
- **Correction:** the bullet is corrected in place and marked; the margin goes to the Dev Manager with Stage B2's prompt (DM-16).
- **Prevention:** a range, a count or a maximum written into a record comes from the whole source, never from a truncated listing; when output is truncated, the figure is computed over the full file (for example `grep … | sort`) and the line count is checked against the expected total.

### AM6-03 — Owned paths that missed what a new dependency needs (scope)

- **What happened:** Stage B2's prompt let the session pin `getstream` and `pyjwt` in `services/api`'s development scope and named the files the pin touches: `requirements-dev.in`, `requirements-dev.lock` and `dependency-inventory.json`. It did not name `services/api/pyproject.toml`, where mypy needs an override for an SDK that ships no type information, or the API README, which describes the component's dependencies. The session changed both without stopping (section 5 said "Nothing else. Report any other change you think is needed"), and reported the first.
- **Caught by:** App Manager 6, verifying Stage B2's paths against section 5.
- **Effect:** two small, reasonable changes outside the prompt's words, which now need the Dev Manager's disposition (DM-17 item 4). No check was weakened: the override applies to `getstream` alone.
- **Correction:** both go to the Dev Manager in DM-17, with the recommendation to accept them.
- **Prevention:** when a prompt adds a dependency to a component, its owned paths name the component's type-check and lint configuration and its README as well as the dependency files, or say that they stay unchanged and why.

## App Manager 7

### AM7-01 — A lock expectation copied without reading the lock (accuracy)

- **What happened:** B2-C1's prompt, revision 2, applied DM-17 5.1 as written: regenerate the API's development lock with the harness's lock as a constraint, and leave `tzdata`, "which only the API holds", as resolved; the prompt added "nothing else moves". The lock before the alignment lists `tzdata` `# via python-dateutil`: only `python-dateutil` 3.0.0 required it, so aligning `python-dateutil` to the harness's 2.9.0.post0 left it an orphan, and uv dropped it.
- **Caught by:** the B2-C1 session, which recorded the deviation and did not edit the lock by hand.
- **Effect:** none on the work: the session handled it correctly, `pip check` and every API check pass without `tzdata`, and nothing was decided on the wrong sentence. The pin test's docstring repeats the sentence, and B2-C2 corrects it. The Dev Manager reads the deviation in DM-18.
- **Correction:** the evidence record, "Manager verification of Stage B2-C1", and the brief's B2-C2 point v record it; B2-C2's prompt corrects the docstring.
- **Prevention:** when a prompt predicts how a lock will change, the manager derives the prediction from the lock's own `# via` lines first, and quotes a condition's expectation only after checking it against them.

### AM7-02 — "Each push runs the workflow" for a branch outside its filter (accuracy)

- **What happened:** B2-C1's prompt, revision 2, said "Each push runs the Foundation workflow on your branch", inherited from B2's prompt. The workflow's `push` trigger names `main`, `app-builder-1/**`, `app-planner-1/**` and `claude/**`; the session's harness named its branch `ccr-a4379c5f-jeokfe`, so none of its pushes started a run, and its check 6 (the run of record) could not be met.
- **Caught by:** the B2-C1 session, which ran the workflow's checks locally and reported that no run existed.
- **Effect:** B2-C1's offline code had no CI run until the manager integrated it; the run of record is PR31's run on the integrating head. No result was wrong.
- **Correction:** B2-C2's prompt names the filter and tells the session to say when its branch is outside it; the brief's B2-C2 point vi and a new step-5 bullet in the manager workflow say the integrating head's PR run is then the run of record, for the Dev Manager to read in DM-18; whether the filter should name such branches goes to M04's brief.
- **Prevention:** the manager workflow's step 5 bullet "A session branch outside the push filter"; prompts state the filter rather than promise a run.

### AM7-03 — A cross-reference to the wrong item (accuracy)

- **What happened:** B2-C2's prompt, revision 1, moved the Video and Feeds lockdown from B2-C1's item 4.4 to item 6 and its dry run to item 6.1, but its "Never" line still said the session may send "the Video and Feeds `PUT`s that section 4 item 5.1 plans"; item 5.1 is the chat target's dry run. Revision 2 carried it, and the Dev Manager's read (DM-18) did not mention it.
- **Caught by:** App Manager 7, reading revision 2 in full before giving it to Nathan.
- **Effect:** none: no session ran either revision. Read literally, the line would have allowed no Video or Feeds `PUT` at all, since item 5.1 plans none, and the session would have stopped at item 6 as a departure.
- **Correction:** revision 2 reads "section 4 item 6.1" before it goes to Nathan. The fix changes a reference, not what the prompt allows; the review log's DM-18 entry lists it for the next consultation to confirm. DM-19 item 6 confirmed it, and the Dev Manager recorded its own share (DM-18 read revision 1 without catching the reference) and now checks every cross-reference in a prompt it reads.
- **Prevention:** when a revision renumbers or moves an item, the manager searches the prompt for every "item N" reference and checks each against the new numbering before the revision is committed.

### AM7-04 — An allowed-change set that left out the plan's own effects (accuracy)

- **What happened:** B2-C2's prompt, revisions 1 and 2, said of the comparison after the chat apply: "The only changes allowed are D1 and the class-2 types' grants", carrying DM-17 2.3's allowed set ("D1 and D4"), which named the application, the chat types and the call types and visibilities. B2-C1's full view, which runs that comparison, also reads the roles, and a role's `scopes` lists the scopes in which it holds grants, so emptying the chat type `agent`'s grants necessarily removes `agent` from the `scopes` of the nine roles that held them. App Manager 7 wrote the allowed set without deriving what the planned change does to the roles read, so the rule did not allow those nine fields.
- **Caught by:** the B2-C2 session, which reported them as fields outside the planned grants, beside the unplanned `blocklist_behavior` field (D6).
- **Effect:** none on the application or the result: the session also stopped on D6, which the rule rightly did not allow, so the stop happened either way. Read as written, the rule would have stopped the session on the roles' `scopes` alone, and the products apply's rule would have done the same for `user` and `guest`.
- **Correction:** the brief's B2-C3 point i states the derived changes before the apply: a role's `scopes` losing exactly the scopes in which the apply emptied all of its grants. DM-19 approved the rule with conditions 2.1 to 2.4 and confirmed this entry; the Dev Manager recorded its own share (the allowed set began in its DM-17 2.3, and DM-18 3.1 re-read it).
- **Prevention:** when a prompt states what a comparison may show after a change, the manager derives every field the planned change alters in every read the comparison covers (here the roles read as well as the types), and lists them, before the prompt is committed.

### AM7-05 — Plain words that outran the record (accuracy)

- **What happened:** writing the D8 message for Nathan, revision 1, App Manager 7 simplified the record and lost accuracy: "four things" with three listed (the two call types counted as one item); "a second kind of chat room" for the chat type `agent`, when six other kinds already existed; "the removals held", when the record shows them held from 21:14 and 22:29 to 22:31 UTC on one evening; and (b) closing "every way a Stream change could reach a member, permanently", when it closes the app's way in and Stream's server side still needs the settings check. It also left out two of OD-32's lines: what (a) costs, and what (b) leaves open.
- **Caught by:** the Dev Manager, reading the message in DM-20 before it went to Nathan (OD-32).
- **Effect:** none on Nathan: revision 1 did not go to him. Revision 2 uses DM-20's words as written.
- **Correction:** the message's revision 2, in DM-20 section 7's words.
- **Prevention:** before a plain-language message goes to Nathan, the manager checks every count, comparison and duration in it against the record line by line, avoids absolutes ("every", "permanently") unless the record shows them, and gives each option all of OD-32's lines: what it is, what it costs, what it closes and what stays open.

### AM7-06 — An inference recorded as fact (accuracy)

- **What happened:** writing the brief's revision 8, point ii, App Manager 7 wrote that a send naming a sender Stream does not hold "is accepted and creates that user (M5)". The run shows M5 accepted, and that the user existed afterwards. Its creation by the send is an inference: C4's read found the user absent before M5, and D10's read found it after. The evidence record says so; the brief did not.
- **Caught by:** Stage B2's exact-head review (focus area 9), as a precision, not a finding.
- **Effect:** none on a decision. DM-20 item 2 approved no adapter change on the same evidence, and the inference is well supported.
- **Correction:** the brief's revision 10 and the P11 plan mark it an inference, in the evidence record's terms.
- **Prevention:** when a record summarizes another record, keep its qualifiers ("by inference", "not shown live") with the claim.

### AM7-07 — A branch head left stale in the handoff (follow-through)

- **What happened:** integrating DM-20's report (`ca806e3`, merge `855a92b`), App Manager 7 updated the review log and the Dev Manager's state, but not the handoff's branch list, which kept `claude/dev-manager` at DM-19's `821efc7`.
- **Caught by:** App Manager 7, listing the remote branches when it added B2-C4's session branch.
- **Effect:** none; no session read that line in between. PR31's body named `ca806e3`.
- **Correction:** the handoff's branch list, checked against `git ls-remote` on 24 October.
- **Prevention:** at each integration, the manager lists the remote branches and updates every line of the handoff's branch list, not only the new branch's.

### AM7-08 — A session's completeness claim repeated unchecked (accuracy)

- **What happened:** recording B2-C4, App Manager 7 read `_without_ids` and described it accurately in the evidence record ("replaces every value of `self.ids`"). But PR31's body and Implementation Control repeated the session's wider claim, "every run identifier generalized". The manager had not checked the strings that reach the results after `_generic` has already rewritten the prefix.
- **Caught by:** B2-C4's exact-head re-review (C4R1).
- **Effect:** none on a decision. The re-review caught it before the merge, and B2-C5 makes the claim true.
- **Correction:** PR31's body and Implementation Control are corrected with the re-review's record.
- **Prevention:** a summary for PR31 or Notion repeats a completeness claim ("every", "all") only after the manager has checked it against the code paths that feed the result; otherwise it describes the mechanism.

### AM7-09 — The manager's own next step left waiting on Nathan (follow-through)

- **What happened:** after integrating DM-21's report, App Manager 7 told Nathan "NOTHING NEEDED" and said it would read Codex's review and the final run when his next message arrived. Reading Codex's review, verifying the run and merging PR31 were the manager's own steps, with nothing of Nathan's needed. So was writing Stage C's design afterwards.
- **Caught by:** Nathan: *"You don't have a planned next step?"*
- **Effect:** PR31's merge and Stage C's design waited one relay turn. No record was wrong.
- **Correction:** the manager read Codex's review and verified the final run, merged PR31 and recorded the receipt (`d0439fc`). It then wrote Stage C's design and DM-22 in the same turn.
- **Prevention:** before ending a turn, the manager checks the handoff's next actions. Any step that needs nothing from Nathan or another session, it takes now. A message that ends a turn is "NOTHING NEEDED" only when the next step is someone else's.

### AM7-10 — A session's limit turned into an absolute in the P11 plan (accuracy)

- **What happened:** recording C1-C1, App Manager 7 wrote in the P11 plan that the reads' guards meant "no enclosing Django transaction can hold their locks across it". It also carried the session's C1C1-X1 (raw `BEGIN`) as the remaining limit. The manager had checked neither claim. Django's own `transaction.set_autocommit(False)` passes both guards, and the pinned psycopg already refuses a raw `BEGIN`.
- **Caught by:** C1-C1's exact-head re-review (R1).
- **Effect:** none on a decision or a member. The re-review caught it before PR32 merges, and nothing is served.
- **Correction:** the P11 plan's line and the manager's verification note are corrected in place, marked as corrections. C1-C2 closes the path in code.
- **Prevention:** AM7-08's rule applies to the manager's own summaries as well as to a session's claims. A record says "no", "never" or "every" only when the manager has checked the paths it covers. Otherwise it states what the mechanism does.

### AM7-11 — A follow-up due "before Stage C" not decided when Stage C started (follow-through)

- **What happened:** DM-17 (item 5) approved B2-C1's handling of the harness client's `npm ci` advisory, and set its follow-up to be decided before Stage C, "whose mobile app has its own lock". App Manager 7 kept it among the handoff's recorded follow-ups. It then wrote Stage C's design and C1's prompt without deciding it, and C1 ran and merged first.
- **Caught by:** App Manager 7, updating the handoff after PR32 merged.
- **Effect:** none. C1 changed no dependency. The advisory's package, `follow-redirects` 1.16.0, is only in the harness's client lock: the mobile app's and the contracts' locks hold none. No live harness run has occurred since.
- **Correction:** decided before C2. The P11 plan carries the lock's update as a fix required before the harness's next live run.
- **Prevention:** before writing a stage's first prompt, the manager reads the handoff's recorded follow-ups for any due "before" that stage, and decides or schedules each one first.

### AM7-12 — A review question put to Nathan instead of the Dev Manager (follow-through)

- **What happened:** after verifying Codex's CX8 on PR33 (the read cursor advances past messages not yet scrolled into view), App Manager 7 carried it to the P11 plan, following CX4 to CX7, and replied on Codex's thread. In the same message it asked Nathan whether to fix it before the merge instead. That choice is a review question that no correction class decides. OD-32 sends such questions to the Dev Manager first, and Nathan receives only what the Dev Manager refers to him. The manager's carry disposition had also not weighed that CX8 misses item 8 of C2's own prompt ("when the member has seen newer messages").
- **Caught by:** Nathan: *"I don't feel comfortable answering that question. It should be an escalationf for the dev manager"*.
- **Effect:** none on the code or a member. PR33's merge is held for the Dev Manager's read, and the reply on Codex's thread ("not fixed in this PR") may need correcting.
- **Correction:** DM-23 to the Dev Manager, with a recommendation of a correction pass, C2-C1. The merge is held.
- **Prevention:** when a verified finding leaves a choice between fixing it before a merge and carrying it, and no correction class decides it, the manager consults the Dev Manager before saying anything to Nathan. A finding that misses an item of the stage's own prompt is weighed as such, not only by the precedent of earlier carried findings.

### AM7-13 — An exact-head review requested before Codex had reported on that head (process)

- **What happened:**
  - App Manager 7 integrated C2-C1 and gave Nathan its exact-head re-review prompt from `83ce64d` on 25 October. Codex's automatic review of C2-C1's head `73ef97e` had started at 00:22:36 UTC and was still running.
  - Codex posted CX9 at 00:25 UTC, a verified defect in the code under review. The manager sent DM-24, whose recommended outcome, a correction pass, changes that code.
  - In the same message, it told Nathan that the re-review should continue because "its report covers C2-C1's own diff". A review of a head that is about to change certifies nothing for the merge, and the work goes to waste.
- **Caught by:** Nathan: *"You requested a premature review, and now you are looking for a dev manager consultation. ... I have not submitted "review session for P06.2 Stage C2-C1" and will not due to your confused context. Your subsequent dev manager escalation invalidates that."*
- **Effect:** none on the code or a member. C2-C1's re-review never ran; its prompt is withdrawn. DM-24 revision 1 assumed the re-review was in flight, so revision 2 corrects that. App Manager 8 receives DM-24's answer (OD-46).
- **Correction:**
  - the re-review prompt is marked withdrawn;
  - DM-24 revision 2 states that the re-review did not run, and proposes one exact-head re-review after any correction pass, given only after Codex has reported on that head;
  - the evidence record, the brief's Sessions, the handoff and Notion are corrected.
- **Prevention:**
  - Codex reviews each new head within minutes. Before giving Nathan an exact-head review prompt, the manager waits for Codex's review of the head's code commit to report, and handles any finding first.
  - When a new finding may change the code under a review that is already with Nathan, the manager tells Nathan to hold that review. It never tells him to continue it.

### AM7-14 — A direction to create the successor read as Nathan's own hand start (accuracy)

- **What happened:** Nathan wrote: *"It's time to create a new Glow App Manager Session. ... I will submit the DM-24 request, create a new session to receive it. It will be Glow App Manager 8."* App Manager 7 read "create a new session" as Nathan's own act. It recorded OD-46, the handoff, the start procedure and Notion as a hand start, with a replacement PR for PR33. It then told Nathan to start App Manager 8 himself.
- **Caught by:** Nathan: *"i told you to create the Glow App Manager 8 session"*.
- **Effect:** a delay, and records that briefly named the wrong path (a replacement PR instead of the manager branch as the successor's outcome branch). No PR was closed and no branch was created.
- **Correction:**
  - OD-46, the handoff, the start procedure, DM-24's header and Notion are corrected;
  - App Manager 7 creates App Manager 8 with the remote-session tools, in `Glow App - No Stream`, with the manager branch as its outcome branch (OD-31).
- **Prevention:** a direction to the outgoing manager that says it is time to create a new manager session is OD-31's case: the outgoing manager creates the successor. When the words leave unclear who creates it, the manager asks in one line before recording either path.

## App Manager 8

### AM8-01 — A start report and a consultation sent without reading the PR's open threads (follow-through)

- **What happened:** App Manager 8 started, read the handoff, found DM-24's report and sent Nathan its first report with DM-25 revision 1, saying nothing else was open. It read PR33's check runs and body, but not its review threads. Codex had posted CX10 at 00:42 UTC (on C2-C1's cursor code), before App Manager 7's handover commit; the handover did not record it, and App Manager 8 did not find it.
- **Caught by:** App Manager 8, reading PR33's review threads when Codex's next summary reported unresolved findings.
- **Effect:** DM-25 revision 1 went to Nathan without CX10, which needs the same Dev Manager read (its fix changes DM-23 2.3's rule). If carried, the Dev Manager would have answered without it. No code, prompt or merge was affected.
- **Correction:** CX10 verified and recorded in the evidence record; DM-25 revision 2 adds it as item 3 and replaces revision 1; Nathan is told to carry revision 2 only.
- **Prevention:** at start, and before any message that says nothing else is open on a PR, the manager lists the PR's review threads and Codex's latest summary, and checks each unresolved thread against the records.

### AM8-02 — A records commit named as a merge commit (accuracy)

- **What happened:** App Manager 8 wrote on Notion's *Dev Manager — reviews and approvals* that DM-24 was "merged at `1ec5186`". `1ec5186` is the records commit after the merge; the merge is `f87f3b5`, as earlier rows name the merge itself. The review log named no SHA.
- **Caught by:** Dev Manager 3, comparing Notion with the repository in its start note.
- **Effect:** none on a decision; a reader following the SHA finds the records, not the merge.
- **Correction:** the review log and Notion name `f87f3b5`.
- **Prevention:** when a record names a merge, the manager takes the SHA from `git log --merges -1` after the merge, not from the batch's last commit.

### AM8-03 — A defect's effect and reach overstated (accuracy)

- **What happened:** recording CX10, App Manager 8 wrote that the unread count "never clears" and that the defect reaches "any member who sends 20 messages in a row after an unread one", in the evidence record, DM-25, the review log and Notion. The count clears once the member views a later incoming message, and through this app the defect takes a missed view, since sending usually brings the incoming message into view.
- **Caught by:** Dev Manager 3, DM-25 section 5.
- **Effect:** none on the verdict, which DM-25 reached on C2's item 8; the records overstated the defect.
- **Correction:** the evidence record's CX10 section, the review log's DM-25 row and the Work Register row state the outcome and reach in DM-25 3.7's terms, marked as corrections.
- **Prevention:** AM7-05's and AM7-10's rule applies to a defect's effect as well as to a fix: "never", "any" and "every" only when the manager has traced the paths that end it. For a stuck state, the manager names what clears it.

### AM8-04 — A finding paraphrased into its reverse (accuracy)

- **What happened:** writing *Implementation Control*'s status after the re-review, App Manager 8 summarized F3 as "a revocation drops a list read begun after it started". Read with "it" as the revocation, that says the opposite of the finding: a list read made after a revocation is kept (DM-24 1.3). The review's words are "begun after the authority change that led to it".
- **Caught by:** Dev Manager 3, DM-27 4.1.
- **Effect:** none on a decision; the repository's records used the review's words.
- **Correction:** Notion's line now uses the review's words; the P11 plan's F3 limit quotes them.
- **Prevention:** a finding's timing or causal clause is copied in the source's words, not shortened, in every summary.

### AM8-05 — Proposed tests that could never fail (accuracy)

- **What happened:** DM-27's proposed d.2 asked C2-C3 for one test per clear of `cursorKnown` (F2), beside d.1's `cursorKnown && from >= 0`. `lastRead` and `cursorKnown` are set and cleared together, so under d.1 neither clear can change a result, and no such test can fail under its reversal: the same kind of error as DM-24 1.4's impossible pairings (DM-26 item 1).
- **Caught by:** Dev Manager 3, DM-27 section 3, before any session met it.
- **Effect:** none; DM-27 1.1 removes the flag and drops the tests.
- **Correction:** C2-C3's prompt quotes DM-27 1.1 to 1.4, not d.1 to d.4.
- **Prevention:** before proposing a test condition, the manager checks that a reversal of the code it covers can make it fail, given every other condition proposed with it.

### AM8-06 — A stuck state's effect and end stated without tracing them (accuracy)

- **What happened:** recording CX12, App Manager 8 wrote that the history is "out of order and partly unreachable in the open conversation until it is reopened", and cited `:248` for the `stale` branch. The messages stay in order with a silent gap; leaving and reopening the same conversation keeps the window (`select()` returns at once, `:124`), so the state lasts until another conversation or account is selected, a revocation, another `stale` reload or a restart. The branch is at `:244`.
- **Caught by:** Dev Manager 3, DM-28 section 3 and 4.3.
- **Effect:** none on the verdict; the records overstated one part and misstated the end.
- **Correction:** the evidence record's CX12 lines, marked as corrections.
- **Prevention:** AM8-03's prevention ("for a stuck state, the manager names what clears it") repeated here. So before writing a stuck state's end, the manager now traces every call that could reset it (here `select`, `closeConversation`, `resetConversation`, `revoke`), and cites a line only after reading it at the commit named.

### AM8-07 — A Notion property left behind its page body (follow-through)

- **What happened:** writing CX12 and DM-28 to the Work Register row, App Manager 8 updated the page body but not the Next Action property, which stayed at `9776c6f`.
- **Caught by:** Dev Manager 3, DM-28 4.1.
- **Effect:** a reader of the property saw a step already past; no decision used it.
- **Correction:** the property is updated in this batch.
- **Prevention:** this repeats AM5-02 and AM5-03, whose prevention is already the manager workflow's checklist item ("update every property and page body that states it"). The manager now writes the Work Register's property and body together on every update, and reads both back.

### AM8-08 — A state change stated without its scope (accuracy)

- **What happened:** writing C2-C4 to *Implementation Control*, App Manager 8 wrote that "Show earlier messages" is idle once the reload merges. The code turns only a `loading` state into `idle` at the replacement; an earlier `error` is kept (`store.ts:245`). The manager's own verification in the evidence record stated it correctly; the Notion summary dropped the qualifier, as DM-28 1.2's words and the session's record had.
- **Caught by:** Dev Manager 3, DM-29 1.3.
- **Effect:** a reader of Notion could take the observation DM-29 decided as already fixed; no decision used it.
- **Correction:** the phrase is corrected in this batch, and the evidence record's two unscoped lines are annotated (DM-29 1.3).
- **Prevention:** a summary of a state change names which state changes, in the code's terms, and is checked against the verification it summarizes before it is written (AM8-03 and AM8-04's kind: a summary that says more than its source).

### AM8-09 — A diffstat written in the wrong order (accuracy)

- **What happened:** "Manager verification of Stage C2-C3" gave `store.ts` as +16 −14 for `1506986..ccf8392`; `git diff --numstat` gives 14 added and 16 removed.
- **Caught by:** the combined exact-head re-review of C2-C3 and C2-C4, finding 13.
- **Effect:** none on a decision; a record figure was reversed.
- **Correction:** corrected in place, with an annotation.
- **Prevention:** a diffstat in a record is pasted from `git diff --numstat` or `--shortstat` output, not retyped.

### AM8-10 — Push and PR runs swapped (accuracy)

- **What happened:** reporting CI on `ab05992`, `c3cce7a` and `c2b7929` to Nathan, App Manager 8 called the run whose application jobs all ran the push run, and the run that skipped them the PR run. It is the other way round: on a Markdown-only commit, the push run compares with the branch's previous head and skips the application jobs; the PR run compares from the merge base with `main` and runs them all.
- **Caught by:** Dev Manager 3, DM-30 4.3 (for `c2b7929`); the manager then checked the others with `get_workflow_run`.
- **Effect:** none on a decision; no repository record carried the swap (the evidence record's labels for `33bae36` are right).
- **Correction:** recorded in the evidence record (DM-30's lines).
- **Prevention:** a run is named by the `event` field of `get_workflow_run`, never by which jobs it skipped; the pre-merge checklist names the PR run on the final head (DM-30 4.3).

### AM8-11 — Notion's standing status bullets left stale (follow-through)

- **What happened:** each records batch updated the lead paragraph of Notion's *Implementation Control* and read back the strings it had edited. The page's standing bullets (Manager, Dev Manager, `main`, branches, mistakes, phase, next items) stayed at App Manager 7's state of 24 October, and its procedure copy stayed stamped `51844a5`. The match check compared only what each batch changed. App Manager 7's batches had done the same.
- **Caught by:** the M05 review, finding 30.
- **Effect:** for about two days Notion misstated the manager, the Dev Manager, `main` and the branches. No decision rested on it.
- **Correction:** the bullets corrected and read back on 26 October. The procedure copy goes with M05's proposal S5 to DM-31.
- **Prevention:** the match check reads the whole status section, not only the edited strings. M05's claims checklist (P-7, for DM-31) carries it.

### AM8-12 — The handoff over its 5 KB limit (process)

- **What happened:** the documentation map keeps the current handoff under 5 KB (DM-01 P3). It was last under at `2542a06` on 23 October and reached 20.9 KB by PR33's merge. App Manager 8's archive at `f669f37` halved it to 10.9 KB but left it over, with follow-ups whose only home was the handoff.
- **Caught by:** the M05 review, finding 38.
- **Effect:** the handoff changed in most records batches, and gated follow-ups lived only in a routing file.
- **Correction:** on 26 October the follow-ups moved to their owning homes (the P06.2 brief's "Carried to later changes", the M02 brief and the P11 plan), and the handoff went under 5 KB.
- **Prevention:** each records batch checks the handoff's size with `wc -c` before its commit. M05's P-7 proposes the standing rule (DM-31).

### AM8-13 — Two status bullets left stale again (follow-through)

- **What happened:** the sync that stamped Implementation Control at `89f2601` updated the lead paragraph but not the `main` bullet, which said "No PR is open" while PR34 was open, nor the Dev Manager bullet, which said DM-31 "goes to it next" after Dev Manager 3 had answered it (`8d51446`). AM8-11's prevention, reading the whole status section back, was not applied to that sync.
- **Caught by:** App Manager 8, reading the whole status section at the `72c60dd` sync.
- **Effect:** for about an hour Notion misstated the open PR and DM-31's state. No decision rested on it.
- **Correction:** both bullets, the phase and next-items bullets and the branch heads corrected and read back at the `72c60dd` sync.
- **Prevention:** AM8-11's, applied to every sync: after the edits, fetch the page and check every status bullet against the handoff, not only the edited strings. The claims checklist's last line already says so.

### AM8-14 — A TypeSafe reading in a brief (records)

- **What happened:** the commit that gave M04's prompt to Nathan wrote the prompt's reading ("Opus 5.5 at extra high, flagged at the boundary with max") into the brief's Sessions line. Step 3 says the readings live in the prompt's header and the Notion uses table only, not in briefs, handoffs or reports (DM-01 P8). PR35 merged it.
- **Caught by:** App Manager 8, rereading the Sessions line to add the integration.
- **Effect:** none on a decision. The brief repeated, correctly, what the header holds; a reader could take it for a recommendation that outlives the prompt.
- **Correction:** the line now points to the prompt's header and the uses table, in M04's PR.
- **Prevention:** before a records commit that names a prompt, search the changed briefs, handoffs and reports for a model name with a rung (`grep -nE '(Fable|Opus|Sonnet|Haiku) [0-9.]+ at'`); only Nathan's pick, the cell he ran, may stand there.

### AM8-15 — A run ID written before it was read (accuracy)

- **What happened:** opening the docs-only PR37, the manager wrote its pre-merge checklist with a PR run ID, 40367951219, and ticked the item. No run had been read: the PR had just been opened, and its run did not exist yet. The ID was a placeholder that looked like evidence.
- **Caught by:** App Manager 8, minutes later, when it checked the runs on the head to fill in that item.
- **Effect:** for a few minutes PR37's description claimed a run of record that no one had read. Nothing was merged on it.
- **Correction:** the description now names the real PR run, 40375587337 on `7bc15c0`, read with its jobs and the gate's line (`Ordinary documentation: application jobs intentionally skipped`).
- **Prevention:** the claims checklist's rule applies to PR descriptions too: an ID, a count or a result goes into any record only after it is read, and an item not yet checked stays unticked and says "pending".

### AM8-16 — The next item named, but no handoff given (follow-through)

- **What happened:** after PR37 merged, the manager reported the merge, named M06 as the next item (OD-49) and said "I write its brief next", then ended its turn with "NOTHING NEEDED". It had written no brief and no prompt, so Nathan had nothing to run, and the relay stopped on the manager.
- **Caught by:** Nathan: *"ok, why did you not give me a handoff for the next task?"*
- **Effect:** one relay round lost. No work was wrong.
- **Correction:** the same turn wrote M06's brief and its assessment prompt, with the prompt's TypeSafe reading, and gave Nathan the prompt.
- **Prevention:** a report that closes an item carries the next item's handoff in the same message: the prompt or the consultation, ready to run. "NOTHING NEEDED" is used only when nothing waits on the manager; when the next step is the manager's own work, the manager does it before reporting.

### AM8-17 — A required command needed a host the prompt excluded (accuracy)

- **What happened:** M06 stage two's prompt required `npm audit signatures` (the new-package review, DM-35 section 8) and limited the network to the npm registry and `docs.expo.dev`. The command refreshes Sigstore's public TUF metadata from `tuf-repo-cdn.sigstore.dev` when its cache is older than npm's seed, so the prompt contradicted itself.
- **Caught by:** the stage-two session, which recorded the contact as a deviation and did not run the command again.
- **Effect:** one contact with a host outside the prompt, fetching public signed key data with no credential. The command then failed on another package's attestation, and the session checked the registry signatures locally instead.
- **Correction:** recorded in the stage-two record's "Manager verification".
- **Prevention:** before a prompt requires a command, the manager checks which hosts it contacts and names them in the prompt's network line, or drops the command.

### AM8-18 — A session's note for the Dev Manager not routed (follow-through)

- **What happened:** M06 stage two's record said "one precision for the Dev Manager": the brief names `noxcturnal`'s maintainer, not its publishing identity, and the version was published by GitHub Actions through npm's trusted publishing without a provenance attestation. The manager's verification checked the package's facts but did not route the note to the Dev Manager.
- **Caught by:** the exact-head review, finding 2.
- **Effect:** none yet; PR38 had not merged. The note would have reached the merge unread by the Dev Manager.
- **Correction:** DM-36 carries it with the review's finding 1, before the merge.
- **Prevention:** the manager's verification lists every item a session addresses to the Dev Manager or to Nathan, and routes each in the same batch.

### AM8-19 — Pruned prompts left with unpinned Notion links (records)

- **What happened:** when the manager pruned M05's prompt and DM-31's consultation (`7bc15c0`), M04's four prompts with DM-32's and DM-33's consultations (`1bf067b`), and M06's assessment prompt (`0139b10`), it pinned the repository's links but left Implementation Control's links to those files on the manager branch. Nine links there pointed at files that no longer exist.
- **Caught by:** the manager, listing Implementation Control's ephemeral links while pinning M06's after PR38 merged.
- **Effect:** a reader following those links in Notion got GitHub's "not found" from 26 October or 1 November until this fix. No decision rested on them; the repository's links were pinned.
- **Correction:** the nine links, and M06's three, now point at the commit before each prune. Every remaining manager-branch ephemeral link in the page names a file that exists.
- **Prevention:** a prune batch lists every link to the pruned files in the repository and in Notion (Implementation Control and the Work Register rows), pins each to a commit that holds the file, and reads Notion back before it reports the prune.

### AM8-20 — A prompt that let a records push cancel the code head's run (prompt)

- **What happened:** P06.2-F's prompt said "Commit and push… The run of record is the one on your last code commit." The Foundation workflow cancels a branch's in-progress run when a newer push lands, and a Markdown-only push's run skips the application jobs. The session pushed its draft record while the run on its code head `3db50d8` was in progress, so that run was cancelled, and the records head's run covered no code.
- **Caught by:** the session, which stopped and asked Nathan.
- **Effect:** about 40 minutes and one extra cycle. Nathan approved a `--force-with-lease` reset of the session's own branch to `67b0201` and the fast-forward push of `3db50d8`; run 41359462167 is the run of record. No commit was rewritten.
- **Correction:** none needed in the code; the record and the brief's "Sessions" say what happened.
- **Prevention:** every implementation prompt that names a run of record says: push the code, wait for its run to complete, and push records only after it, or push code and records together in one push.

### AM8-21 — A miscount and an unchecked claim in a verification (accuracy)

- **What happened:** P06.2-F's Manager verification said the 25 paths were "18 changed, 5 added, 2 removed"; `git diff --name-status 67b0201 3db50d8` gives 17 modified, 6 added and 2 deleted. It also said "Expo still inlines it there" of the layout's mode, repeating the session's sentence. The manager had read the diff, not a bundle; a development bundle reads the mode through Expo's env module, `_expoVirtualEnv.env.EXPO_PUBLIC_GLOW_MODE`, as it reads the two unchanged reads.
- **Caught by:** the exact-head review, findings 7 and 10.
- **Effect:** records only. The total of 25 was right, and the guard's behavior is unchanged.
- **Correction:** both sentences corrected in place in the record, marked.
- **Prevention:** a verification's counts come from a command's output (`git diff --name-status … | cut -c1 | sort | uniq -c`), quoted as counted; a claim about build output either comes from reading that output or is attributed to the session that made it.

### AM8-22 — Implementation Control's standing bullets left at 26 October (follow-through)

- **What happened:** from 26 October to the handover on 2 November, each Notion sync prepended a new entry to the opening paragraph of Implementation Control's "Current status" and left the section's standing bullets as they were. At `76dbe4a` they still said that App Manager 8 was the manager with PR37 open, that `main` was `35a5827` with PR38 open, the branch list of 26 October 18:50 UTC, M06 as the next item, a Phase line ending at M04, and a mistakes list ending at AM8-18. Recorded by App Manager 9.
- **Caught by:** App Manager 9, reading the whole section before its first sync.
- **Effect:** a reader of the bullets alone got a state a week old. The opening paragraph, the handoff and the Work Register row were current, and no decision rested on the bullets.
- **Correction:** the six bullets are brought up to date in App Manager 9's first sync (at `c6108e4`'s records), and read back. The same gap was on *Dev Manager — reviews and approvals*, whose consultations stopped at DM-32 (last edited 26 October); DM-33 to DM-37, with DM-38, were added at `903c41f`'s sync and read back.
- **Prevention:** it repeats AM8-11 and AM8-13, whose prevention is already in the manager workflow's claims checklist ("read back the whole status section, not only what changed"). The checklist item is unchanged; what was missing was running it: each sync's readback now lists the section's standing bullets by name with the state each states, against the handoff.

## App Manager 9

### AM9-01 — A Notion match claimed from its first paragraph (accuracy)

- **What happened:** App Manager 9's first report told Nathan that "Implementation Control's status section and the P06.2-F Work Register row both match `76dbe4a`". The page is over 180,000 characters, and the manager had read only the status section's opening paragraph; the section's standing bullets did not match (AM8-22). The report said it had read only the status section, which was itself more than it had read.
- **Caught by:** App Manager 9, reading the whole section before its first sync.
- **Effect:** one line of one report to Nathan; nothing was decided on it.
- **Correction:** this entry, the bullets' correction (AM8-22), and the next report to Nathan, which says so.
- **Prevention:** the claims checklist's "say *every*, *no* or *never* only after tracing each path" covers a match claim: a match is stated only for the parts read, by name, or after reading the whole section.

### AM9-03 — A session's completeness claim repeated after testing only its own forms (accuracy)

- **What happened:** C1's record said its type check "finds Glow's data by type … through any binding" and that "every way that type can be dropped or widened in the file is either a refusal above or a type error". App Manager 9's verification re-ran PA, PB, PC and finding 2's reversal and confirmed the one evasion the record named, then wrote "through any binding" in its own words in the delta re-review prompt, the Work Register row, Implementation Control and its reply on Codex's thread (`display-rule.test.ts:133`). It tried no form of its own.
- **Caught by:** C1's delta re-review, findings 1 to 5: more than 20 edits confined to `screen.tsx` or `rows.ts` pass the test, `tsc` and ESLint. The manager re-ran three; each passed.
- **Effect:** the claim reached the prompt (which asked the reviewer to test it, so the review was not misled), Notion and a PR comment. No merge rested on it.
- **Correction:** the record's "Delta re-review of correction C1" states the finding; Notion's texts are corrected at this batch's sync; the PR thread gets a reply when C2's fix is on the PR.
- **Prevention** (as DM-38 4.1 and 4.2 strengthen it): it repeats the mechanism of AM7-08 and AM8-21's second half, a session's claim repeated unchecked.
  - A verification that meets a completeness claim ("any", "every", "all") tries forms the session did not list, at least two, recording each with its result, **and** still attributes the claim to the session, with its own forms and their results beside it. No test over source proves "through any binding", so the manager never makes such a claim in its own words (DM-38 4.1).
  - Part of the cause was the brief: C1's Outcome 1 asked for a check that "fails … through any binding", which no source check can show, and the session then claimed exactly that. A brief asks for named forms and a stated guarantee with its limits, never "any" or "every" over arbitrary code (DM-38 4.2). Brief revision 2 applies it to C1's Outcome 1 and to C2.
  - This applies the claims checklist's first item (say *every*, *no* or *never* only after tracing each path) to a session's words as well as the manager's own.

### AM9-04 — Times written from memory (accuracy)

- **What happened:** the current handoff's waiting checkpoint and branch-list headings carry a time. App Manager 9 wrote them without reading the clock: "13:20 UTC" at 16:32 (`903c41f`, corrected at `3cf2ee1`), "18:30" at 18:24 (`007377e`, corrected in the batch after it), and "20:30" at 21:51, caught before its push.
- **Caught by:** App Manager 9, reading `date -u` after writing each.
- **Effect:** two pushed records said a wait or a listing began at a time it did not; no decision rested on either, and the waits' causes were right.
- **Correction:** each time corrected from `date -u`.
- **Prevention:** a time that goes into a record comes from a command run in the same step (`date -u +%H:%M`, or a tool result's timestamp), never from memory; the records script takes it as an argument.

### AM9-05 — A recommendation in Notion that the consultation did not make (accuracy)

- **What happened:** syncing `6a9a6b5`, the manager wrote in Implementation Control's status lead and P06.2-F's Work Register row that DM-39 recommended restating the guarantee "and view models as their own item". The consultation's item 3 asked whether (c) should become its own item, and made no recommendation; the review log's row says the same. The commit message of `6a9a6b5` carries the same phrase.
- **Caught by:** Dev Manager 3, DM-39 section 9.
- **Effect:** Notion overstated the manager's position on one question for the time between the sync and this batch; the Dev Manager answered the question as asked, and nothing was decided on the Notion text.
- **Correction:** both Notion texts corrected at this batch's sync to say the timing was asked, with DM-39's answer; the commit message stays as history.
- **Prevention:** a Notion summary of a consultation is written from the consultation's own text, item by item ("recommended" only where it says so), and the readback compares each "recommended" in the summary with the consultation.

### AM9-06 — A prompt asked for evidence the manager had not checked exists (accuracy)

- **What happened:** C3's prompt and the brief's "Correction C3" Outcome 1 asked each item of "What it refuses, in its own terms" to name, by ID, the planted forms that pin it. The text came from DM-39 section 4.2's terms. The manager did not first check that each item had a planted form. Several did not: a rest read; an `in` check, a `for…in` or a destructuring assignment; some widenings; an inferred predicate; a type error; and two source-check items.
- **Caught by:** correction C3, its point 1. The session marked each such item "no planted form", confirmed each refusal by a probe and added none, as DM-39 1.1 requires.
- **Effect:** none on the code. The prompt asked for something that could not be met as written; the session reported it, and the open question went to the delta re-review (its focus 9).
- **Correction:** recorded in "Manager verification of correction C3"; the delta re-review's prompt states the gap and asks for a view on it.
- **Prevention:** when a prompt asks a session to cite evidence for each item of a list (an ID, a test, a run), the manager checks first that the evidence exists for each item, or the prompt says what to do where it does not.

### AM9-07 — A range on Implementation Control left behind the register (accuracy)

- **What happened:** Implementation Control's "Standing directions" section says which directions Notion's copy of the register holds. It still said OD-01 to OD-54 after OD-55 (1 November) and OD-56 (2 November) were added to the copy. App Manager 9's readbacks of the page covered the status section and its standing bullets, not the sections after the operating procedure.
- **Caught by:** App Manager 9, recording OD-57.
- **Effect:** a reader of Implementation Control alone would have missed two directions; the copy itself was current.
- **Correction:** the line now names OD-01 to OD-57, at this batch's sync.
- **Prevention:** a page's readback covers every section that names a range, a count or a commit, not only the section the batch wrote; adding a direction updates the register copy and that line together.

### AM9-08 — Narrowed words proposed without forms just inside them (accuracy)

- **What happened:** DM-40's option (a) proposed the words for finding 1's narrowed callback item: "a declared function, a `useCallback` result or an object property holding a function, given by reference". The manager had re-run the review's forms, but did not try forms just inside its own proposed words.
- **Caught by:** Dev Manager 3, DM-40 section 3. An accessor (F1c), a class field (G3) and an untyped literal given later (G2) pass the check and sit inside those words.
- **Effect:** none on the code; the Dev Manager gave section 4.2's syntax-exact words instead, and C4 uses them.
- **Correction:** recorded in the review log's "DM-40" and the record's dispositions.
- **Prevention:** AM9-03's prevention extends to proposals. Wording the manager proposes for what a check refuses is tried with forms just inside its words before it is proposed, or the proposal says it is untried. Words name syntax, not categories.

### AM9-09 — Uses rows without the PR field (accuracy)

- **What happened:** the uses-table rows "P06.2-F C3 delta re-review" and its revision 2 were created from the skill's printed row, which has no PR key, without adding the PR field that the manager's earlier rows carry.
- **Caught by:** Dev Manager 3, DM-40 section 8.
- **Effect:** the two rows did not name their PR for five days.
- **Correction:** both rows name PR40, at this batch's sync.
- **Prevention:** before creating a uses row, add the PR field (the PR, its scope and the code head) to the skill's printed properties.

### AM9-10 — Asked Nathan to perform a GitHub Actions re-run (process)

- **What happened:** C4 stopped because its push run, 42464917902, failed in two jobs that C4 does not touch: a 504 while `setup-python` downloaded Python, and a rendered test that calls `page.goBack()` straight after a logout click. The manager verified C4's code, diagnosed both failures, and then asked Nathan to use "Re-run failed jobs" on the run page. It posted the same request on PR40, and gave him a relay for C4's session that depended on that re-run. It followed the manager workflow's "Actions re-runs" line, which says to do exactly that.
- **Caught by:** Nathan, the same day: *"no, rejected, asking me to do github actions is incorrect. You are failing at process."* (OD-58).
- **Effect:** none on the code or the runs; nothing was re-run. The PR comment carried the request until it was marked withdrawn.
- **Correction:** the PR comment is marked withdrawn; how to handle the failure goes to the Dev Manager as DM-41; the workflow line is replaced (OD-58), for the Dev Manager's read before PR40 merges; App Manager 10 receives DM-41's report. DM-41 found two more texts that put the old rule in force, missed by the sweep (AM9-12): the charter's "Not for" ("CI reruns") and step 7's branch-cleanup sentence ("the names to delete go to Nathan"); App Manager 10 replaced both in DM-41's words (6.3, 6.4).
- **Prevention:** the manager never asks Nathan to perform a GitHub operation (a re-run, a comment, a merge, a setting). A CI failure that seems to call for a re-run, or any question about how to verify a head, goes to the Dev Manager first (OD-32), with options that need no action from Nathan (DM-41 6.2, 7.1). A written procedure that puts a GitHub operation on Nathan is reported to the Dev Manager as a conflict, not followed.

### AM9-11 — Two review-log links resolved to a missing folder (accuracy)

- **What happened:** the review log's DM-40 row, written at `7983b31`, and DM-41 row, written at `9e0334a`, linked their consultations as `../ephemeral/…`. From `docs/continuity/dev-manager/` that resolves to `docs/continuity/ephemeral/`, which does not exist. The log's other 30 consultation links use `../../ephemeral/`.
- **Caught by:** App Manager 9, checking every relative link in its handover batch before creating its successor.
- **Effect:** two broken links in the log, from 3 to 8 November; nothing else.
- **Correction:** both links corrected in the handover batch.
- **Prevention:** before each records commit, resolve every relative link added in it and confirm that the target exists.

### AM9-12 — The OD-58 sweep missed two governing texts (follow-through)

- **What happened:** App Manager 9's OD-58 batch replaced the manager workflow's "Actions re-runs" line and the start prompt's rule, but its supersession sweep did not find two other governing texts that conflicted with OD-58: the charter's "Not for", which excluded "CI reruns" from the Dev Manager, and step 7's branch-cleanup sentence, which said that when a cleanup run fails "the names to delete go to Nathan".
- **Caught by:** Dev Manager 4, in DM-41 (6.3, 6.4, 7.2). Recorded by App Manager 10 (OD-11).
- **Effect:** none acted on; both texts stood from 8 November, 09:37 UTC, until App Manager 10 replaced them.
- **Correction:** both replaced in DM-41's words; AM9-10's correction lists them.
- **Prevention:** a sweep for a new rule searches for the action it forbids, by every name (here: re-run, rerun, delete, "goes to Nathan"), in every governing text, not only for the line it replaces.

## App Manager 11

### AM11-20 — AM11-11's and AM11-12's patterns again (records)

- **What happened:** the batch at `2e3ef0f` merged DM-67's report and moved the brief to revision 9. It did not update `claude/dev-manager`'s head where the handoff's branch list and Notion's Branches bullet name it (still `a53bdb0`), and it left Notion's "Next items" at "its brief, revision 8".
- **Caught by:** Dev Manager 5, in its start note (section 4).
- **Effect:** none on the work; neither misled the next step.
- **Correction:** both fixed at the records commit after `6cf247c`, with the succession.
- **Prevention:** the manager workflow's supersession sweep already names both (a brief's previous revision number; every record that names a branch's head). Before each records batch is pushed, the manager now greps the handoff and Notion's standing lines for the previous revision number and for every branch head the batch moved.

### AM11-19 — A title and a sentence left behind by their own updates (records)

- **What happened:** the handoff's body moved on at `6b376cf` and `3000014`, but its title still said "C2 continues after DM-66". In D8, OD-64's answer went in as a sub-bullet beneath "Whether to bound the probing is put to Nathan … it is decided before then", and that sentence was left as it was.
- **Caught by:** Dev Manager 4, reading Notion and the repository for DM-67 (section 7), which gave the words (GD13, GD14).
- **Effect:** none on the work; neither misled a reader of the current state, as the Dev Manager notes.
- **Correction:** both applied in DM-67's words, at its merge's records commit.
- **Prevention:** the supersession sweep also reads the file's title when a handoff's state changes, and the sentence a new sub-bullet answers when an answer is recorded under it.

### AM11-18 — A pending decision named only by its review label (communication)

- **What happened:** F7's decision message (`docs/ephemeral/2026-11-12-f7-two-way-disclosure-decision.md`) went to Nathan on 12 November. In the messages after it, the manager reminded him of it only as "your F7 decision", a finding label from the exact-head review, never with what it was about.
- **Caught by:** Nathan, asking "what 'F7' decision?"
- **Effect:** the decision stayed unanswered longer than it needed to; it holds no merge.
- **Correction:** the manager restated the decision in plain words, with its options, in the reply.
- **Prevention:** a reminder to Nathan of a pending decision says in plain words what the decision is about, every time, not only its label (OD-32).

### AM11-17 — A Codex pass on a consultation's commit left unread (follow-through)

- **What happened:** after AM11-10, consultations go to Nathan without waiting for Codex. The manager gave DM-65 at `c661dce` and set no watch for that pass, so its P2 (17:39 UTC, `pointers.name_order`'s `id(tx)`) went unread. C2's prompt was then written at `2475d7b` without reading PR45's comments; the finding surfaced only when the watch on the prompt's commit ended at 18:47.
- **Caught by:** App Manager 11, listing PR45's review comments before giving the prompt.
- **Effect:** none on the work: both new findings were the review's F4 and DM-64's item, already C2's items 4 and 10. The prompt went as written.
- **Correction:** both recorded (the brief's "Sessions"; the evidence record with C2's verification).
- **Prevention:** not waiting for Codex before a consultation still means reading its result: before writing any prompt, list PR45's review comments since the last one read, and set a watch on every pass whose result is not yet read.

### AM11-13 to AM11-16 — Four slips the exact-head review and the manager found

- **What happened:**
  - **AM11-13:** the review prompt's revision 2 (`3b36969`) headed its reversal list "Four offline reversals, at least" over five items. The manager saw it before giving the prompt and gave it as written, to avoid another commit and Codex pass, saying so to Nathan.
  - **AM11-14:** the CI policy's discovery sentence, the manager's own (`d35b0ba`), kept "its keyed tie-break" after DM-61's K2. The sweep at `1ffff7d` searched the brief, not every text, for "keyed", and C1's prompt listed neither the CI policy nor `discovery-fixtures.md`.
  - **AM11-15:** the P11 plan's SV3 entry kept "Run of record: none yet" after the manager recorded PR45's run of record (`b09cbf3`), and "concurrency … not claimed" after C1's.
  - **AM11-16:** the evidence record said "Every other job passed" of a run whose gate job also failed.
- **Caught by:** the manager (AM11-13); the exact-head review, F5, F6 and N6 (AM11-14 to AM11-16).
- **Effect:** none on code. Three records claimed more than the runs and code show, until C2; AM11-16's line is corrected at this batch.
- **Correction:** AM11-16 now; AM11-14 and AM11-15 in C2, as the review's F5 and F6 (DM-65).
- **Prevention:** AM11-11's sweep, applied to a replaced design as well as a revision number: when a decision replaces a design, search every text (`docs`, `.github`, code comments) for the old design's own words (here "keyed"), and when a run of record lands, search for "none yet" and "not claimed" in each record that names the item.

### AM11-12 — The branch list left at the Dev Manager's previous head (follow-through)

- **What happened:** the batch at `b67bae2` merged DM-62's report (`f5c69fa`) and left the handoff's "Branches and PRs" giving `claude/dev-manager` at `133a715`, DM-61's head. The sweep the same batch added (AM11-11) was run for the brief's revision number only.
- **Caught by:** App Manager 11, listing the branches for Notion's "Branches" bullet.
- **Effect:** the handoff was wrong at `b67bae2` for a few minutes; no session read it. Corrected at `823be0b`, with the summary row; this section follows at the next batch.
- **Correction:** the branch list gives `880635d`, merged at `f5c69fa`.
- **Prevention:** the supersession sweep for a batch that merges a branch includes that branch's head wherever a record names it (the handoff's "Branches and PRs", Notion's "Branches").

### AM11-11 — The brief's old revision number left in Notion (follow-through)

- **What happened:** the sync for the brief's revision 3 (`1ffff7d`) updated Implementation Control's status, "Branches" and "Mistakes log" lines, and left "Next items" saying "its brief, revision 2, approved by the Dev Manager in DM-60". The supersession sweep searched the repository only.
- **Caught by:** Dev Manager 4, DM-62 section 7.
- **Effect:** Notion named the wrong revision for about 90 minutes; no session read it.
- **Correction:** the bullet names revision 4 at this batch, read back.
- **Prevention:** AM5-22's, repeated, so now in the checklist: the manager workflow's supersession sweep also searches Notion's standing lines, and searches for a brief's previous revision number.

### AM11-10 — A consultation held for a wait the workflow does not set (process)

- **What happened:** DM-62 was committed at `c3fb5bb` (00:49 UTC), and the manager chose to wait for Codex's pass on that commit before giving its relay message. Codex finished at 00:52 with nothing new, but the stop hook's push of a one-line handoff change (`3cdddd3`) restarted the wait, and the manager told Nathan "NOTHING NEEDED" twice. The workflow's wait for Codex (step 6) covers review and correction prompts, not consultations.
- **Caught by:** Nathan: "what are you even doing? I feel like you have not been very task oriented".
- **Effect:** DM-62 reached Nathan only when he asked; Codex never started on `3cdddd3`, so the wait would not have ended on its own.
- **Correction:** the message was given at once, and the watch kept running alongside it.
- **Prevention:** a consultation goes to Nathan as soon as its commit is pushed. A later Codex finding on the same code goes to the Dev Manager as an addition, without holding the message.

### AM11-09 — The prompt named the tie-break's files without the one that passes the key (accuracy)

- **What happened:** C1's prompt, revision 1 (`1ffff7d`), gave the tie-break's owned files as `predicates.py`, `pages.py` and `keys.py` "and what they need", and listed the same three to read whole. It told the session to remove `keys.sql_pads` "and their parameters", which are set in `eligibility.parameters`, a file it never named. The brief's own path, `services/api/glow_discovery/**`, does include it.
- **Caught by:** App Manager 11, checking Codex's CX2 (`eligibility.py:67`) against the prompt.
- **Effect:** the prompt had not been given. A session reading the parenthesis as a limit could have stopped, or left the pads' parameters behind. One more revision, TypeSafe reading and Codex pass.
- **Correction:** revision 2 names `eligibility.py` in the owned paths, the reading list and item 2.
- **Prevention:** when a prompt removes a function or a value, find every caller and every place that sets it with a scan, and name each file in the owned paths and the reading list.

### AM11-08 — The branch count changed and the sentence after it did not (follow-through)

- **What happened:** the sync for `1ffff7d` replaced the list in Implementation Control's "Branches" bullet, from three branches to four, and left the bullet's next sentence, "All three are kept by the cleanup's keep-list", unchanged. Stage A's session branch is the fourth, and it is not on the keep-list.
- **Caught by:** App Manager 11, reading the bullet back.
- **Effect:** Notion's bullet read wrongly for about ten minutes; no decision rested on it.
- **Correction:** the sentence now says the first three are on the keep-list, read back in the next sync.
- **Prevention:** AM11-02's, repeated, so now a checklist item: the manager workflow's claims checklist reads back every whole bullet an edit touches, and checks each count and status word in it against the edit.

### AM11-05 — A wait with nothing set to end it (follow-through)

- **What happened:** after opening PR45 at 22:39 UTC, the manager told Nathan "NOTHING NEEDED" and that it was waiting for the run and Codex. It set no wake-up, background watch or check-in. The run passed at 22:47 and Codex finished at 22:42, but nothing happened until Nathan asked "still waiting?" at 23:37.
- **Caught by:** Nathan.
- **Effect:** the exact-head review prompt reached Nathan about 50 minutes later than it could have.
- **Correction:** the run and Codex were read at once, and the prompt written.
- **Prevention:** AM7-09's, now a checklist step: a wait on CI or Codex ends the turn only after a background watch or a scheduled wake-up is set for it. The message to Nathan names that watch and the time it fires.

### AM11-02 — A stale phrase left in the bullet being corrected (follow-through)

- **What happened:** App Manager 11's first sync corrected the opening of Implementation Control's "Next items" bullet ("now SV2 …") and left, in the same bullet, "P06.2-F (now, PR40)". Its readback counted the new strings and the old opening only.
- **Caught by:** Dev Manager 4, DM-60 section 18.
- **Effect:** Notion called a merged item current for about an hour; no decision rested on it.
- **Correction:** "P06.2-F (**done**, PR40)" at the next sync, read back.
- **Prevention:** AM8-11's, which this repeats: when a sync corrects a standing line, read the whole line after the edit and search it for every status word ("now", "next", "in flight", "pending"), not only for the edited strings.

### AM11-01 — A session promised for the manager's own work (accuracy)

- **What happened:** the first report to Nathan said that the next message would carry one prompt, for the matrix recheck for SV3. The two earlier rechecks (8 and 10 November) were App Manager 10's own records readings of public pages, each recorded as "not an implementation or review session", and DM-37 5.1 has the brief recheck its rows on the day it is written.
- **Caught by:** App Manager 11, reading the OD-60 recheck record to write that prompt, before any prompt was given.
- **Effect:** Nathan was told to expect a session that was not needed. No prompt was written or given. The next message corrected it.
- **Correction:** the recheck was done by the manager and recorded (`docs/testing/evidence/2026-11-11-sv3-matrix-recheck.md`), and the next message to Nathan said the earlier statement was wrong.
- **Prevention:** before naming a session's prompt for a step, read how the step was done last time, in its evidence record.

### AM10-22, AM10-21 and AM10-20 (recorded by App Manager 11)

- **What happened:** App Manager 10's last Notion sync, at `8130439`, moved Implementation Control's status section, but two standing lines stayed old. The "Mistakes log" bullet still listed AM10-01 as the last entry, at `0e890dc`, although the log held AM10-02 to AM10-19. The "Standing directions" line still said the register copy held OD-01 to OD-62, although OD-63 had been added to the copy.
- **Caught by:** App Manager 11, reading the whole page at its start.
- **Also (AM10-22):** the "Phase" bullet still ended "Now: P06.2-F, the mobile hardening, in PR40", stale since PR40 merged, and the "Next items" bullet still said "now SV2 … Stage B next", stale since PR44 merged.
- **Effect:** Notion understated the mistakes log by 18 entries and the register by one row, and named items already merged as current; no decision rested on any of them.
- **Correction:** all four lines corrected in App Manager 11's first sync, with readbacks.
- **Prevention:** AM8-22's and AM9-07's: the readback of a sync covers every standing line of the page, not only the status paragraph.

## App Manager 10

### AM10-19 — A test's location named from memory (accuracy)

- **What happened:** the brief's "Stage B, correction C1 (DM-58 item 9)" and C1's prompt, revision 1, told the session that the state-write guard's allowlist was in `tests/test_profiles_offline.py`, beside `LockOrderTests`, and that a line C1 moved would update it. The allowlist is `NOT_A_PROFILES_STATE` in `tests/test_profile_recompute.py`, which pins `media.py:128` and is not one of C1's owned paths. No one checked the location against the code.
- **Caught by:** C1's session (its deviation 1).
- **Effect:** none in the code. The session kept the pinned line at 128 by shortening `media.py`'s module docstring, wrote nothing outside its owned paths, and the guard passes unchanged.
- **Correction:** the manager's verification of C1 records the location; the brief's C1 section stands as history.
- **Prevention:** a brief or prompt that names a file, a test class or a line for a session finds it in the code (`git grep`) before it is written, as a start gate's commands are dry-run.

### AM10-18 — AM10-17 repeated the next day (follow-through)

- **What happened:** the script that routed Stage B's prompt in the handoff wrote its waiting checkpoint and its branch list as 01:24 UTC. The same command's clock printed 01:19. AM10-17's prevention, taking the time from the clock's output, had been logged but was not followed: the time was typed into the script.
- **Caught by:** App Manager 10, reading the command's clock line.
- **Effect:** none: both were corrected to 01:19 before any commit.
- **Correction:** the handoff reads 01:19 UTC.
- **Prevention:** a script that writes a time takes it from `date -u` through a shell variable in the same command, and no time is typed by hand.

### AM10-17 — A time written before the clock was read (follow-through)

- **What happened:** completing PR43's merge receipt, the script that updated the handoff wrote the waiting checkpoint as 23:57 UTC. The clock, read in the same command, printed 23:55. AM9-04's rule is to read the clock before writing a time.
- **Caught by:** App Manager 10, when the command's clock line printed.
- **Effect:** none: the unpushed commit was amended to 23:55 before the push.
- **Correction:** the checkpoint reads 23:55 UTC.
- **Prevention:** the clock command runs before the script that writes a time, and the script takes the time from its output, not from the manager.

### AM10-16 — Links rewritten by file name, not by path (accuracy)

- **What happened:** to pin the links to SV2 Stage A's eleven pruned prompts and consultations at `4dc2061`, a script matched each link target's file name against the prune list. The Dev Manager's reports in `docs/continuity/dev-manager/reviews/` have the same file names as the consultations, so the script also pointed 16 links to DM-53 to DM-56's reports at the pruned consultations, in the brief, the review log and the evidence record.
- **Caught by:** App Manager 10, reading the word diff's removed targets before the commit.
- **Effect:** none: the changes were reverted, and the script was rerun matching each target's resolved path; it pinned 19 links, none to a report.
- **Correction:** the pinned links point only to `docs/ephemeral/` files.
- **Prevention:** a script that rewrites links resolves each target against its file's directory and matches the full path, and the manager reads the removed targets in the word diff before committing.

### AM10-15 — A data erasure proposed without reading what it breaks (accuracy)

- **What happened:** DM-55 item 1.4 proposed that a reset erase every birth input revision's private fields, keeping the rows as `missing`, and named the migration it needed. It did not read the read path, the save path or the model checks that erasure touches:
  - `OwnBirthInput` requires a full `BirthInput`, and `contract.own_birth_input` calls `birth_date.isoformat()`, so both owner reads would fail on an erased revision;
  - the next save compares its expected version with the erased row's;
  - `birth_time_uncertainty` ties `local_time` to `time_precision`;
  - G-05's hold may need to stop an erasure.
- **Caught by:** Dev Manager 4, in DM-55 section 3.
- **Effect:** none: 1.4 was declined as worded and carried to P07 for G-01 (Z18), before any prompt.
- **Correction:** Z2 and Z18 in DM-55's words.
- **Prevention:** AM10-11's rule covers a consultation's proposals too. Before proposing a change to stored data, the manager reads every DTO and read that returns it, the writers that compare its version, and the model's checks on it.

### AM10-14 — A reading accepted with one side of the words (accuracy)

- **What happened:** C1's session left C1-3 to the manager: a future birth date keeps its 400 refusal, and only a date under 18 takes DM-54's refused-and-rerun path. The manager accepted it as a reading for the review and the Dev Manager, citing D7's validity clause ("valid, not in the future"). The review prompt's revision 1 gave that side only. The brief's acceptance item 7 counts "a future date" among the dates that fail, and `adult_outcome` fails one; Y6 and Y7 speak of a date that fails "the rule" and "the adult rule".
- **Caught by:** Codex, its P2 finding on `40db2c2` (`operations.py:1019`).
- **Effect:** none: revision 1 was held before Nathan ran it.
- **Correction:** the review prompt's revision 2 puts both readings in focus item 3, and the records say the reading is contested.
- **Prevention:** before accepting a session's reading of a Dev Manager's words, the manager reads every place the brief and the code use the term at issue, and puts the counter-reading beside it.

### AM10-13 — A start gate checked a commit its branch does not hold (prompt)

- **What happened:** SV2 Stage A's prompt, at `481e2f3`, checked `git merge-base --is-ancestor c864edd… HEAD`. `c864edd` is PR42's merge commit on `main`, and the manager branch does not contain it. SV1's prompt had checked the PR's head and said that `main`'s merge has the same tree.
- **Caught by:** App Manager 10, running the gate's commands against the prompt's commit before giving it to Nathan.
- **Effect:** none: the prompt had not gone out. Every session would have stopped at the gate and reported.
- **Correction:** the gate checks PR42's head, `df8a04c`, whose tree equals `c864edd`'s (`a6624de`).
- **Prevention:** before giving Nathan a prompt, the manager runs its start gate's commands against the commit the prompt names, and an ancestry check names a commit on the branch the session starts from.

### AM10-12 — Owned paths given without reading what the change writes (accuracy)

- **What happened:** SV2's brief, revisions 1 and 2, made D11's contract additions additive DTOs and gave them owned paths without reading what adding a DTO writes.
  - `packages/contracts/scripts/generate.mjs` writes `apps/mobile/src/contracts/generated/` from every schema definition. CI's Mobile checks job runs its `--check`, which fails on any byte difference, and `corpus.test.mjs` imports the generated validators. The brief excluded `apps/**`, and D11 said the mobile app's generated validators stay untouched until P10.
  - P04.3 registered `MediaCollection` in F05 of `flows-v1.json`, and P06.2 C1 its DTOs in F11, with a README section. The brief's owned paths left out the registry and the README.
  - P06.2 C1's prompt had owned both, so the precedent D11 names was not read.
- **Caught by:** App Manager 10, reading the generator, the corpus test and the registry while writing Stage A's prompt.
- **Effect:** none on code: the prompt was held, and the paths went to the Dev Manager as DM-53, since DM-52's report repeats the untouched claim.
- **Correction:** DM-53's answer, applied in revision 3.
- **Prevention:** before a brief lists owned paths for a change to a generated or registered artifact, the manager reads the generator's output paths, the checks that compare them, and the owned paths of the precedent the brief names.

### AM10-11 — Mechanisms proposed without reading their code (accuracy)

- **What happened:** SV2's brief, revision 1, named existing functions, DTOs and rules as the mechanisms for its design without reading them.
  - D7 had the adult check update SV1's `unknown` age row through `AgeAssurancePort`, whose `record` refuses an existing row by design, while the brief excluded `glow_identity`. It also kept the date in the birth input, which at that step cannot exist, since its shape needs a place the member has not given yet.
  - D11 gave the sensitive-fields consent as `ConsentIntent` with a new purpose; `ConsentIntent` has no purpose field.
  - D6 relied on `accept_consent` for F02's "old consent version rejected", which it does not check.
  - D9's completion list left out P04.2's reviewed requirements, the resolved chart and a "looking for" value.
- **Caught by:** Dev Manager 4, DM-52 sections 8, 9 and 11, which read each function, schema and fixture rule.
- **Effect:** none on code: no prompt had gone out. Revision 2 applies B17 to B28 and B34 to B37.
- **Correction:** DM-52's words, applied as written.
- **Prevention:** before a brief names an existing function, DTO or reviewed rule as a mechanism, the manager reads its signature and docstring, the DTO's properties, or the fixture rule's text, and cites the line; a design that changes a reviewed rule says so.

### AM10-10 — Facts written from a summary, not from the rows (accuracy)

- **What happened:** the second A05 message, revision 1, cited matrix rows and design texts but took their content from the matrix's section 9 summary and from the manager's own reading. Five statements were wrong against their sources: both stores ask for derived data (only Google's row says so, GP-25); California requires consent at its threshold (its row is a right to limit, UST-42); New York's fraud-ban notice binds now (only for a paid service, UST-08); the research's "city/region" became "a city or ZIP code", without its privacy testing; and rematch added later "changes the data model's one-pair rule" (the `Match` row says rematch is policy on one pair record). The matrix's own section 9 line carried the California error.
- **Caught by:** Dev Manager 4, DM-51 section 5, which read every cited row.
- **Effect:** none on Nathan: the message had not gone to him. Revision 2 applies M1 to M17, and X1 corrects the matrix.
- **Correction:** DM-51's M1 to M17 and X1, applied as written.
- **Prevention:** before a decision message goes to the Dev Manager, each statement that cites a row or a design text is checked against that row's own cells or that text's own words, not a summary of them; a paraphrase of a source is quoted or marked as a paraphrase.

### AM10-09 — A replaced state left in P11's plan (follow-through)

- **What happened:** C1 turned `ACCOUNT_REAUTHENTICATION_REQUIRED` on. Integrating C1, App Manager 10 added C1.5's session-list bullet to the P11 plan's SV1 entry. The same entry kept, under "Limits", "No reauthentication: an email change needs none (`ACCOUNT_REAUTHENTICATION_REQUIRED` keeps its default, off)". Its list of what SV1 proves also named neither C1's reauthentication case nor C2's password-change limit.
- **Caught by:** Dev Manager 4, DM-50 section 4, in a sweep of the living documents for the states C1 and C2 replaced.
- **Effect:** none on the code. P11 could have wired the app without allauth's `reauthenticate` flow; the server would still refuse the change, so the cost would have been a broken screen, not a weaker boundary.
- **Correction:** DM-50 2.1's words, applied as written.
- **Prevention:** a correction that changes a setting or a behavior gets a supersession sweep that `git grep`s the living documents (the P11 plan, the carried-items file, the architecture texts, the CI policy) for the replaced state, by the setting's name and by its plain words, before its integration's records commit.

### AM10-08 — The Branches bullet one commit behind the status (follow-through)

- **What happened:** at the syncs for `38142b3` and `cae9cea`, App Manager 10 moved Implementation Control's status line to the new commit. Each time, it left the Branches bullet's "at this sync" hash at the commit before (`30fdf1a` and `38d48e2`).
- **Caught by:** Dev Manager 4, DM-48 section 9 and DM-49 section 5, each as a nit.
- **Effect:** none on the work. The page read one commit behind in one place until the next sync. The repository wins (OD-27).
- **Correction:** the bullet was fixed at the `2f577f8` sync and again at DM-49's disposition sync.
- **Prevention:** every Implementation Control status edit carries the Branches bullet's edit in the same call. The bullet's "at this sync" hash and its listing time are checked against the status line's commit when the page is read back.

### AM10-07 — A proposed check that the old setting also passes (accuracy)

- **What happened:** DM-48 proposed `change_password` at `5/300s/user`, with words for acceptance check 11: "the sixth request at `account/password/change` within 300 seconds, a wrong current password among them", is refused. A sixth request sent at once is refused under allauth's default, `5/m/user`, too, so a case written to those words passes whether or not the setting is in place. The proposed D3 replacement also changed only the bullet's first sentence, so its next sentence, "They use Django's cache", would have pointed at the threat model.
- **Caught by:** Dev Manager 4, DM-48 section 3 (C2.1, C2.3).
- **Effect:** none: no prompt had been written. As proposed, the case and its reversal could not have shown the new limit.
- **Correction:** C2.3's words: a sixth request with the right password, sent more than 60 and less than 300 seconds after the first of five, is refused and the password unchanged, with a reversal that restores the default. C2.1 replaces the whole bullet.
- **Prevention:** a check for a changed value names the observation only the new value produces, and says what the old value would do there. A replacement of one sentence is read with the sentences after it.

### AM10-06 — An approval's named setting was not carried into the brief (follow-through)

- **What happened:** DM-45 section 9 approved "email change verified by code. That needs `ACCOUNT_CHANGE_EMAIL = True`, which defaults to `False`, and reauthentication, which does not cycle the key." It was approval text, not a blockquoted condition, so App Manager 10's revision 2 did not carry it. D3 kept "The evidence names the installed release's settings for this", and the prompt left the settings to the session. The session turned on `ACCOUNT_CHANGE_EMAIL` and kept `ACCOUNT_REAUTHENTICATION_REQUIRED` at its default, off.
- **Caught by:** the SV1 implementation session, which reported that an email change needs no reauthentication; App Manager 10 matched it to DM-45's words in the verification.
- **Effect:** at code head `269ac3b`, a holder of a live access token, refresh token or session key can move the account's address and then reset the password from it. Nothing is served: the runtime is sealed and the proof uses synthetic accounts.
- **Correction:** DM-47 puts the gap and a proposed correction (`ACCOUNT_REAUTHENTICATION_REQUIRED = True`, with its cases and a reversal) to the Dev Manager before the exact-head review.
- **Prevention:** when disposing of a Dev Manager report, read its approval text as well as its conditions, and carry into the brief every setting, rule or requirement the approval names; one the manager does not carry is put back to the Dev Manager in the disposition.

### AM10-05 — The procedure summary's stamp was not moved (follow-through)

- **What happened:** the manager workflow's match check says that when a governing text changes, Notion's procedure summary "is checked and its stamp moved". App Manager 10 changed governing texts four times on 8 November (OD-58's texts and the CI policy's paragraphs, at `33c4cc2`, `0a49e62`, `678dabd` and `86e65dc`) and did not move the stamp, which still named `1ce2fcb` (26 October). Earlier managers' governing changes after 26 October had left it there too.
- **Caught by:** App Manager 10, reading the summary after adding step 6's sentence on 9 November.
- **Effect:** the summary's links pointed at an older commit. Its statements were still true at the new commit; it did not mention OD-58's rule that Nathan is never asked to perform a GitHub operation.
- **Correction:** the stamp and every link moved to this batch's commit, with OD-58's rule added, and read back.
- **Prevention:** a records batch whose diff touches a governing path (`AGENTS.md`, `CLAUDE.md`, `docs/pf-canon/`, the manager workflow, the Dev Manager charter, the CI policy, the owner-direction register) moves the summary's stamp in the same Notion sync; the batch's `git diff --name-only` is checked against that list before the sync.

### AM10-04 — A correction on a revocation path went without a consultation (process)

- **What happened:** step 6 says the Dev Manager is consulted when a fix "touches a security boundary (authorization, revocation, privacy or data ownership)". Correction C1 changed when the mobile fixture adapter refuses an ended session's command, a revocation path. App Manager 10 judged that the fix only applied DM-44 1.2's words, recorded that reading, and wrote C1's prompt without a consultation.
- **Caught by:** Dev Manager 4, DM-45 section 16.
- **Effect:** none in substance. The Dev Manager read `85ae241` and confirmed C1 against DM-44 1.2.
- **Correction:** step 6 gains the Dev Manager's sentence: a fix that only makes code do what a Dev Manager condition already says, in that condition's words, and changes no design, interface, contract or dependency, needs no consultation first, even on a security boundary; the correction's brief names the condition, and the next consultation confirms the fix.
- **Prevention:** before a correction prompt, read step 6's consultation triggers against the fix one by one, and name in the brief the condition whose words the fix applies, if any; a trigger that applies with no such condition means a consultation first.

### AM10-03 — A line count from memory in the verification of C1 (accuracy)

- **What happened:** the manager's "Manager verification of correction C1" said the one non-test change was the moved `capture(session)` "plus two comment lines". The diff adds three: two `//` lines at `fixture-adapter.ts:100-101` and a `/** … */` line at `:120`. The `+6 −5` count beside it was right. The manager counted the comment lines from its reading of the file, not from the diff's added lines.
- **Caught by:** C1's delta review, N-3.
- **Effect:** the record understated the change by one comment line, from `1a2a2c7` until the correction; no disposition rested on it.
- **Correction:** the line corrected in that section, with a note, and the delta review's section records it.
- **Prevention:** the claims checklist's "check every count against its source" applies to the manager's own counts too: count added and removed lines from `git diff`'s `+` and `-` lines, not from a read of the file.

### AM10-02 — The brief named the guard's predicate, not its enforcement (accuracy)

- **What happened:** P06.3's brief, revision 1, said `/notifications` would be guarded by one new entry in `SAFE_ROUTES` and `canAccessRoute`, and excluded `src/app/_layout.tsx`. In Expo Router 58 a screen is guarded by its own `Stack.Protected` line in the layout, and a route file the layout does not declare is added unguarded. The manager read `routes.ts` and the layout's imports, but not the layout's `Stack.Protected` lines.
- **Caught by:** Dev Manager 4, DM-44 item 6, from Expo Router 58.0.29's source.
- **Effect:** none in code: no prompt had been written. As written, the session would either have shipped a screen that opens signed out while every `canAccessRoute` unit test passed, or stopped on the exclusion.
- **Correction:** the brief's revision 2 applies DM-44 6.1 to 6.3: one owned `Stack.Protected` line, and a rendered test whose reversal removes it.
- **Prevention:** when a brief adds a screen or changes access, read how access is enforced at render (the layout's `Stack.Protected` lines), not only the predicate, and name the enforcing line in the owned paths with a rendered test of it.

### AM10-01 — Conditions quoted by line range lost a sentence (prompt)

- **What happened:** C6's prompt quoted DM-42's conditions by extracting line ranges of the report. One range began two lines late, so item 2's condition lost its opening ("2.1 Finding 3 is valid" and its locations), and another carried the report's heading "## 5. Item 5" into the prompt, beside the prompt's own numbered sections.
- **Caught by:** App Manager 10, reading the filled prompt whole before giving it to Nathan.
- **Effect:** the prompt had not been given. The correcting push (`0e890dc`), three minutes after `678dabd`, cancelled PR run 42490599464 on `678dabd` (Database proof checks and Mobile checks cancelled, the gate failed), AM9-02's mechanism; that head was records only and superseded. One more Codex pass.
- **Correction:** items 2 and 3 and the review's conditions re-extracted whole, without the heading, in the same revision.
- **Prevention:** after quoting conditions into a prompt, check each quoted block's first and last lines against the source's condition numbers, and read the filled prompt whole before pushing it.
