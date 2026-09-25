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
