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
| AM4-01 | 27 Sep 2026 | process | The first report to Nathan listed two standing items as "waiting on you" without saying what they were or what he could do; he would not send the I2b prompt while they stood | Nathan |
| AM4-02 | 27 Sep 2026 | process | Asked Nathan to pick a model and level for I2b when the manager's call and TypeSafe's readings were the same | Nathan |
| AM4-03 | 27 Sep 2026 | process | Scoring requests too thin for an informed reading: one line per level, no facts about cost or capability on either model | Nathan |
| AM4-04 | 27 Sep 2026 | process | Overrode Nathan's six-rung ladder, left max unreachable, and presented the manager's own model judgement as a recommendation | Nathan |
| AM4-05 | 27 Sep 2026 | accuracy | Two slips in the handover records: the start procedure said its placeholders were filled in, and AM4-03 and AM4-04 had no summary rows. Recorded by App Manager 5 | App Manager 5, reading the handover commit |
| AM4-06 | 27 Sep 2026 | accuracy | The verification of I2b repeated I2b's underivable "the plan's eleven" in its own disposition, and did not flag I2b's mypy count of 55 although its own run printed 53. Recorded by App Manager 5 | The exact-head review of I2b (nits 5 and 6) |

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
- **Effect:** none known. The Dev Manager never read, printed or used the values, and its read needed none. The planned rotation of the secret at P06.1's close covers every container started while the variables were set.
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
