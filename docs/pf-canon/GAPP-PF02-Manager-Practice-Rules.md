# Glow Dating App — Manager Practice Rules

**Identity:** GAPP-PF02 · **Revision:** 1.0 · **Recorded:** 16 November 2026
**Scope:** the managers' practice in this application's manual relay. It does not govern the Glow HD engine or its canon.
**Source:** the [managers' mistakes log](../continuity/manager-mistakes.md) at commit `553d9ed96bf3fb32e57e3ecf59d759eb3bcadf53`, from AM2-01 to AM11-29: 167 entries. Entries added after that commit are folded in under "Maintenance" below.

## 1. Purpose and authority

- PF02 is the canonical home of the managers' standing practice rules that the mistakes log's preventions set.
- The log stays the dated record of what happened (OD-11). It is evidence, not authority, and the managers keep writing to it.
- A rule that another governing home already states (root `AGENTS.md` or `CLAUDE.md`, the [manager workflow](../planning/manager-workflow.md), the [Dev Manager charter](../planning/dev-manager.md), the [CI policy](../operations/ci-and-branch-policy.md) or the [owner-direction register](../continuity/owner-directions.md)) is cited there by section, with a one-line gist. PF02 does not restate it (PF00: never create a second editable authority by copying). The [next-manager start procedure](../planning/start-prompts/next-manager.md), which every manager runs at its start, is cited the same way.
- Where PF02 and a governing home differ, the governing home wins until the Dev Manager rules and the difference is corrected.
- PF02 holds a rule only where no governing home states it, or where it adds a check or a case to a rule a home states. Its "Home" line says which.

## 2. How to use it

- A manager reads PF02 at its start, after the current handoff and before the mistakes log. The next-manager start procedure's reading list (step 3), the manager workflow's "Mistakes log" paragraph and the mistakes log's head route a manager here (DM-76).
- A prompt, a consultation, a record or a message may cite a rule by its ID, such as PF02-R01.
- Each rule has a check: the command, field or read-back that shows it was followed.

## 3. Reading a rule

Each rule gives:

- **Rule:** one or two imperative sentences. For a rule a governing home holds, the gist only, marked "cited".
- **Check:** what shows it was followed.
- **Sources:** the log entries that set or tightened it.
- **Changed:** where a later entry tightened or replaced an earlier form, what changed. PF02 states the later form.
- **Home:** "PF02", or the governing section it points to. "PF02, adding to …" means the home states the core and PF02 holds the named addition.

## 4. The rules

### 4.1 Times and clocks

#### PF02-R01 — A time comes from the clock, read before the write

- **Rule:** Every time written into a record, the handoff or a Notion page comes from a clock reading. A scorer request's send time is the one the scoring skill prints in its reading ("Sent …"), never typed. In a shell command, take it from `date -u` through a variable inside the same command that writes it. In a tool call (a Notion or GitHub write), take it from a clock read in an earlier call whose output the write uses. Never type a time, write it from memory, or read the clock in a call sent in parallel with the write.
- **Check:** the clock's printed line comes before the write and equals the time written; the read-back shows the same time.
- **Sources:** AM2-05, AM9-04, AM10-17, AM10-18, AM11-03, AM11-07, AM11-25, AM12-04.
- **Changed:** AM9-04 had the records script take the time as an argument. AM10-17 and AM10-18 moved the clock into the writing command, with no typed time. AM11-25 extended the rule to tool writes and excluded a clock read sent alongside the write. AM2-05's own step, printing the UTC time beside each scorer request, is now done by the scoring skill, which prints the send time in its reading (DM-76).
- **Home:** PF02.

### 4.2 Standing lines, revision numbers and supersession sweeps

#### PF02-R02 — Run the supersession sweep before each records commit

- **Rule (cited):** before each records commit, search the repository and Notion's standing lines for the wording, revision numbers and links a batch replaces, and at a status change read each changed document's status lines, headline first.
- **Check:** the searches run return no living document that still treats the old state as current.
- **Sources:** AM3-08, AM3-10, AM3-22, AM5-10, AM5-13, AM5-22, AM11-11, AM12-07.
- **Home:** the manager workflow, step 5, "Supersession sweep".

#### PF02-R03 — Search for a replaced thing by every name it has

- **Rule:** The sweep's search terms include, besides the old phrase: a met condition's own words ("conditional on", "pending", "until"); a replaced setting's name and its state in plain words; a replaced design's own words (such as "keyed"); and, for a new rule, the action it forbids under every name it goes by (for OD-58: re-run, rerun, delete, "goes to Nathan"). The search covers `docs`, `.github`, code comments and every governing text, not only the brief or the line being replaced.
- **Check:** the batch's record or commit lists each term searched; no living document matches.
- **Sources:** AM3-22, AM9-12, AM10-09, AM11-14.
- **Home:** PF02, adding to the manager workflow, step 5, "Supersession sweep".

#### PF02-R04 — Counts, lists and placeholders follow the change

- **Rule:** When a change alters a count or a list (application jobs, cases, routes), grep every record for the old figure and the list's other names, the manager's own governing sentences included (the CI policy, the P11 plan's entry, the handoff), and correct each before the integration commit. When a run of record or a result lands, search each record that names the item for its placeholder ("none yet", "not claimed", "pending").
- **Check:** a grep for the old figure and for each placeholder returns no living document.
- **Sources:** AM4-07, AM11-15, AM11-26, AM11-33.
- **Home:** PF02.

#### PF02-R05 — Every listed branch head moves with the batch

- **Rule:** A batch that integrates or merges a branch, or moves a branch's head, lists the remote branches (`git ls-remote origin`) and updates every line of the handoff's branch list that names a head in the same commit as the merge's records, and Notion's Branches bullet in that batch's sync, before the batch is pushed. It checks every line of the list, not only the new branch's.
- **Check:** each head the handoff and Notion name equals `git ls-remote`'s output at the batch's commit.
- **Sources:** AM3-15, AM7-07, AM11-12, AM11-20.
- **Home:** PF02.

#### PF02-R06 — A title and the sentence an answer settles are status lines

- **Rule:** When a handoff's state changes, the sweep reads its title. When an answer is recorded beneath a sentence (a question, a "put to Nathan", a "decided before then"), the sentence it answers is revised in the same edit.
- **Check:** the title and the answered sentence agree with the new state.
- **Sources:** AM11-19.
- **Home:** PF02, adding to the manager workflow, step 5, "Supersession sweep".

#### PF02-R07 — The handoff stays under 5 KB, checked at every commit

- **Rule:** Every commit that changes the current handoff prints its byte count (`wc -c docs/continuity/current-handoff.md`) before the commit. At 5,000 bytes or more, that commit cuts it: history goes to the brief or the evidence record, follow-ups to their owning home.
- **Check:** the printed count for each such commit is under 5,000.
- **Sources:** AM8-12, AM11-04, AM11-27.
- **Home:** PF02 for the check. The limit is the documentation map's ([`docs/README.md`](../README.md), "One home per fact") and the manager workflow's, step 5, "Batching records".

### 4.3 Notion syncs and read-backs

#### PF02-R08 — Run the Notion write checklist on every write

- **Rule (cited):** no bare filename with an extension, a literal `$` escaped, rows-mode filters in a group, every write read back, a status change carried to every property and page body with an old-wording query over every property (links included), and a search by Work ID before a row is created.
- **Check:** as the checklist states; the read-back.
- **Sources:** AM2-11, AM3-01, AM3-04, AM5-02, AM5-03, AM5-07, AM5-11.
- **Changed:** AM5-02's own prevention concerned the pick column; Nathan's pick is no longer recorded (OD-53, D1), so only the general rule it fed stands.
- **Home:** the manager workflow, "Writing to Notion: a checklist".

#### PF02-R09 — Edit Notion from what was fetched

- **Rule:** Match an update's text, link markup included, exactly as the fetch returned it. Read the sections around a passage before writing a statement about them. When editing a row, read every text property of that row, not only the one being fixed.
- **Check:** a fetch of the page or row precedes each update; the read-back shows every text property consistent.
- **Sources:** AM2-11, AM3-23.
- **Home:** PF02.

#### PF02-R10 — Write a property and its page body together

- **Rule (cited):** fetch the whole Notion page, write a property and the body together, and read both back.
- **Check:** the read-back shows both.
- **Sources:** AM5-09, AM8-07.
- **Home:** the manager workflow, "Claims: a checklist".

#### PF02-R11 — Read back every standing line of the page

- **Rule:** Each Notion sync ends by fetching the whole Implementation Control page and checking every standing line, by name, against the handoff at the batch's commit: the status lead; each status bullet (Phase, Next items, Manager, Dev Manager, Main, Branches, Mistakes log); and every line elsewhere on the page that names a range, a count or a commit, such as the register copy's range and the procedure summary's stamp. Every edit of the status line carries the Branches bullet's edit in the same call, and its "at this sync" hash and listing time are checked against the status line's commit. Adding a direction updates the register copy and its range line in the same sync. A match is reported only for the parts read, named. The same holds for the Dev Manager page's list of consultations.
- **Check:** the sync's read-back lists each standing line by name with the state it gives.
- **Sources:** AM8-11, AM8-13, AM8-22, AM9-01, AM9-07, AM10-08, AM10-20, AM10-21, AM10-22, AM11-02, AM11-08.
- **Changed:** AM8-11 asked for the whole status section; AM8-22 for each bullet by name; AM9-07 for the lines after the operating procedure; AM10-08 for the Branches bullet in the same call; AM11-02 and AM11-08 for the whole bullet after an edit.
- **Home:** PF02, adding to the manager workflow, "Claims: a checklist" (the whole status section; every whole bullet an edit touches, with its counts and status words).

#### PF02-R12 — Move the procedure summary's stamp with every governing change

- **Rule:** Before the Notion sync, check the batch's `git diff --name-only` against the paths the procedure summary links to: the charter's governing Markdown (`AGENTS.md` and `CLAUDE.md` at any level, `docs/pf-canon/`, the manager workflow, the Dev Manager charter, the CI policy) and the owner-direction register, which the charter does not count as governing Markdown. If any is touched, the same sync checks Implementation Control's procedure summary and moves its stamp and links to the batch's commit.
- **Check:** the summary's stamp names a commit at or after the last governing change.
- **Sources:** AM3-09, AM10-05, AM11-31.
- **Home:** PF02, adding to the manager workflow, "Notion and the repository", the match check (OD-26, OD-27, OD-53).

#### PF02-R13 — Write Notion text from its source

- **Rule:** Write a Notion note from the committed record, not from memory of the work. Summarize a consultation from its own text, item by item, writing "recommended" only where it recommends. A summary names the measure its source compares, in the source's words, and says *every* only where the source does.
- **Check:** the read-back compares each statement, and each "recommended", with the record or the consultation.
- **Sources:** AM3-21, AM9-05, AM12-03.
- **Changed:** AM12-03 added the measure: "every row-lock count" was written for the account-table counts the record compares.
- **Home:** PF02.

### 4.4 Briefs, proposals and the Dev Manager's reports

#### PF02-R14 — Read the code before naming a mechanism

- **Rule:** Before a brief, consultation or proposal names an existing function, DTO, setting or reviewed rule as a mechanism, read its signature and docstring, the DTO's properties or the rule's text, and cite the line. Before proposing a change to stored data, read every DTO and read that returns it, the writers that compare its version and the model's checks on it. When a brief adds a screen or changes access, read how access is enforced at render (the layout's `Stack.Protected` lines), name that line in the owned paths and ask for a rendered test of it. A design that changes a reviewed rule says so.
- **Check:** each named mechanism carries a file and line read at the brief's commit.
- **Sources:** AM10-02, AM10-11, AM10-15.
- **Home:** PF02.

#### PF02-R15 — Prove a protected boundary on the protected thing

- **Rule:** When a brief draws a protected boundary, it says how the code proves the boundary holds by checking the protected thing itself (which database it is, by its marker), not a stand-in for it (the route to it). The review prompt's classes test that proof.
- **Check:** the brief names the check on the protected thing, and the review prompt names a class that tests it.
- **Sources:** AM5-18.
- **Home:** PF02.

#### PF02-R16 — A proposed check must be able to fail

- **Rule:** Before proposing a test, a check or the words for what a check refuses: confirm that a reversal of the code it covers can make it fail, given every other condition proposed with it. For a changed value, name the observation only the new value produces, and say what the old value would do there. Try forms just inside proposed words, or say they are untried; words name syntax, not categories. Read a replacement for one sentence with the sentences after it.
- **Check:** each proposed test names its reversal and the observation that distinguishes it.
- **Sources:** AM8-05, AM9-08, AM10-07.
- **Home:** PF02.

#### PF02-R17 — Read a Dev Manager report whole when disposing of it

- **Rule:** When disposing of a Dev Manager report, read its approval text as well as its conditions, and carry into the brief every setting, rule or requirement either names; one not carried goes back to the Dev Manager in the disposition and, as an item accepted with changes, to Nathan with the Dev Manager's own text. Before accepting a session's reading of a Dev Manager's words, read every place the brief and the code use the term at issue, and put the counter-reading beside it.
- **Check:** the disposition lists each named setting or requirement with where it is carried.
- **Sources:** AM10-06, AM10-14.
- **Home:** PF02, adding to the Dev Manager charter, "The relay", step 4.

#### PF02-R18 — A disposition and its governing text agree, part by part

- **Rule:** A disposition and the governing text that applies it say the same thing: a rule awaiting Nathan is not written as in force. When a decision has parts with different conditions, record each part's condition separately in every home. A disposition applies the narrowest rule that governs it: the item's brief's own correction classes, and its rule for record nits, before the manager workflow's step 6 (b).
- **Check:** the review log's disposition and each governing text carry the same state for each part.
- **Sources:** AM3-06, AM3-07, AM12-06.
- **Changed:** AM12-06 added the narrowest rule: a Markdown record nit in SV3 was carried under step 6 (b), where the brief corrects one before the merge.
- **Home:** PF02. The manager checks it before the records commit. A governing change also goes to the Dev Manager's read (the charter, "Read before it takes effect"), which may catch a mismatch but is not defined as this check.

#### PF02-R19 — Consult the Dev Manager before a fix that meets a step-6 trigger

- **Rule (cited):** a fix goes to the Dev Manager before Nathan hears of it when the fix-or-carry rule does not decide, when the fix's design changes or departs from a Dev Manager condition, when it touches a security boundary, a contract, a dependency or an interface, or when a charter trigger applies. A fix that only makes code do what a condition says, in its words, and changes no design, interface, contract or dependency needs no consultation first, even on a security boundary. A defect in a stage's own code that misses an item of that stage's prompt, or falls in a correction class its review prompt names, is fixed before the merge.
- **Check:** before a correction prompt, read the triggers one by one against the fix, and name in the brief the condition whose words it applies, if any.
- **Sources:** AM7-12, AM10-04.
- **Home:** the manager workflow, step 6, "Fix or carry, by rule" (DM-45, section 16), and "Nothing unexplained goes to Nathan" (OD-32).

### 4.5 Prompts

#### PF02-R20 — Test environment claims and commands with the session's own tool

- **Rule:** Test every environment or network claim in a prompt with the tool the session will use (npm, not only curl). Take prescribed commands from the repository's documented commands, or run them before putting them in a prompt, and use the documented form when running them. Before a prompt requires a command, find which hosts it contacts and name them in the network line, or drop the command.
- **Check:** each command in the prompt is documented or was run, and each host it reaches is named.
- **Sources:** AM2-01, AM2-02, AM2-03, AM8-17, AM11-32.
- **Home:** PF02.

#### PF02-R21 — Read the filled prompt whole, as the session receives it

- **Rule:** Before committing a prompt, read the paste-ready body on its own; it never points to the unpasted header. After quoting conditions into a prompt, check each quoted block's first and last lines against the source's numbering. When a revision renumbers or moves items, check every "item N" reference against the new numbering.
- **Check:** a whole read of the filled body before the push, with each quoted block's boundaries and each cross-reference checked.
- **Sources:** AM2-04, AM7-03, AM10-01.
- **Home:** PF02.

#### PF02-R22 — Dry-run the start gate, and leave a waiting prompt's owned paths alone

- **Rule:** Before giving Nathan any prompt, run its start-gate commands against the commit it names and the live manager branch; an ancestry check names a commit on the branch the session starts from. From a prompt's commit until its session's branch is integrated, write nothing to its owned paths: a fact seen meanwhile goes to the handoff, and into the session's records only at integration.
- **Check:** the gate's output, run by the manager, before the prompt is given.
- **Sources:** AM5-15, AM10-13, AM11-21.
- **Home:** PF02, adding to the manager workflow, step 3, "Make a stale prompt stop at its start gate", and the prompt template's start-gate line.

#### PF02-R23 — Owned paths cover everything the change writes

- **Rule:** When a prompt or brief gives owned paths: for a new dependency, name the component's type-check and lint configuration and its README as well as the dependency files, or say they stay unchanged and why; for a generated or registered artifact, read the generator's output paths, the checks that compare them and the owned paths of the precedent named; for a removed function or value, scan for every caller and every place that sets it and name each file in the owned paths and in the prompt's reading list. On adding an owned path, re-read the exclusions.
- **Check:** the owned paths and the reading list name each file the scan or generator names, and no exclusion overlaps them.
- **Sources:** AM3-08, AM6-03, AM10-12, AM11-09.
- **Home:** PF02.

#### PF02-R24 — Find a named file, test or line in the code first

- **Rule:** A brief or prompt that names a file, a test class, an allowlist or a line finds it in the code (`git grep`) at the commit named before writing it.
- **Check:** the `git grep` output that locates it.
- **Sources:** AM10-19.
- **Home:** PF02.

#### PF02-R25 — Sweep the earlier tests and reconcile the stop clauses before a stage's prompt

- **Rule:** Before a stage's prompt, list every earlier test that pins what the stage extends (routes, a plan's coverage or count, the migration leaf, a parameter set or signature) by reading the earlier stage's tests whole, and grep every suite's source, harnesses included, for statements the stage's new checks refuse. Name each in the prompt as expected to change, with what it becomes, or settle it first. Check each stop clause against each item that changes a rule an earlier test pins, so the clause stops only on unexpected failures.
- **Check:** the prompt lists the expected-to-change tests, and no item triggers its own stop clause.
- **Sources:** AM11-22, AM11-23.
- **Home:** PF02.

#### PF02-R26 — Word each item from its own rule

- **Rule:** A behavior shared by two items, such as a reversal or a bound, is written once per item, from each item's own words. A brief entry that restates a prompt's bound uses the prompt's words.
- **Check:** each item's wording traces to its own rule in the brief.
- **Sources:** AM5-05, AM11-24.
- **Home:** PF02.

#### PF02-R27 — Ask only for evidence that exists

- **Rule:** When a prompt asks a session to cite evidence for each item of a list (an ID, a test, a run), check first that the evidence exists for each item, or say what to do where it does not.
- **Check:** the manager's list of items with their evidence, or the prompt's instruction for a gap.
- **Sources:** AM9-06.
- **Home:** PF02.

#### PF02-R28 — Derive a predicted effect from the artifact

- **Rule:** When a prompt predicts how a lock will change, derive it from the lock's own `# via` lines. When it states what a comparison may show after a change, derive every field the planned change alters in every read the comparison covers. When it specifies a database check, name the database the check runs in and give the exact SQL test, and ask whether the check could pass for the wrong reason.
- **Check:** the prediction cites the lines or fields it was derived from.
- **Sources:** AM5-19, AM7-01, AM7-04.
- **Home:** PF02.

#### PF02-R29 — Check a reviewer's suggested fix before prompting it

- **Rule:** Before writing a reviewer's suggested fix into a prompt, check it against the brief's rules and the harness's existing verdicts, and say in the prompt where it departs from either.
- **Check:** the prompt states the fix's agreement or departure.
- **Sources:** AM3-16.
- **Home:** PF02.

#### PF02-R30 — Settle the follow-ups due before a stage

- **Rule:** Before a stage's first prompt, read the recorded follow-ups for any due "before" that stage (the brief's carried items, the carried-items file, the P11 plan) and decide or schedule each.
- **Check:** each such follow-up has a recorded decision or schedule before the prompt's commit.
- **Sources:** AM7-11.
- **Changed:** AM7-11 read the handoff's follow-ups; follow-ups now live in their owning briefs or the carried-items file (the manager workflow, step 5, "Batching records").
- **Home:** PF02.

#### PF02-R31 — Read how a step was done last time before prompting it

- **Rule:** Before naming a session's prompt for a step, read how the step was done last time, in its evidence record. A step done as the manager's own records reading is not a session.
- **Check:** the earlier evidence record cited in the prompt or message.
- **Sources:** AM11-01.
- **Home:** PF02.

#### PF02-R32 — Say which credentials a session holds

- **Rule (cited):** a prompt or consultation says which credentials a session holds, not only which it needs; for a session started while the Stream variables were set, it says "none added", never "none present".
- **Check:** the prompt's credential line.
- **Sources:** AM3-17, AM3-19.
- **Home:** the manager workflow, step 3, "Say which credentials a session holds, not only which it needs".

#### PF02-R33 — Say when a session may push, and whether its branch starts a run

- **Rule:** A prompt whose session pushes code and then records tells it to push nothing more until the code run has finished (cited). Every implementation prompt that names a run of record says so, or tells the session to push code and records together in one push. A prompt states the push filter rather than promising a run (cited).
- **Check:** the prompt's push line and its run-of-record line.
- **Sources:** AM5-14, AM7-02, AM8-20.
- **Changed:** AM8-20 widened the rule to every implementation prompt that names a run of record and added the alternative of one push for code and records.
- **Home:** PF02, adding to the manager workflow, step 3, "Say when a session may push again", and step 5, "A session branch outside the push filter".

#### PF02-R34 — Name the code head

- **Rule (cited):** a review prompt names the head that carries the code under review, not a later records commit, and the review report states the commit of the prompt text it received.
- **Check:** the prompt's head line and the review report's stated prompt commit.
- **Sources:** AM3-05.
- **Home:** the manager workflow, step 6, "Name the code head" (DM-01 P2).

### 4.6 Runs, pushes and commands

#### PF02-R35 — One records batch, one push

- **Rule:** While a code PR is under review, push the manager's records only when a session needs them and at close-out (cited). A mistake entry found during a sync, or a stop hook's request, then waits for the next batch: a second push before the first push's runs finish cancels them.
- **Check:** one push per batch; no cancelled run on the manager branch's records heads.
- **Sources:** AM5-04, AM9-02.
- **Home:** PF02, adding to the manager workflow, step 5, "Batching records" (DM-01 P2).

#### PF02-R36 — A session's run of record is the session's

- **Rule (cited):** while a session's run of record is open, the manager does not subscribe to, watch or chase it; it gives Nathan a relay message for that session.
- **Check:** no subscription or check-in on a session's run.
- **Sources:** AM6-01.
- **Home:** the manager workflow, step 5, "A session's run of record is the session's".

#### PF02-R37 — Name a run by its event

- **Rule:** In every report and record, a run is named by the `event` field `get_workflow_run` returns, never by which jobs it skipped. A prompt names the run it must read by what that run holds (the PR run on the latest head whose non-Markdown paths equal the code head under review), never by its commit's place ("its commit or its parent").
- **Check:** the run's `event` field quoted with its ID.
- **Sources:** AM8-10, AM12-05.
- **Changed:** AM12-05 added the prompt's naming: a review prompt asked for a run on its commit or its parent, where neither had one that finished.
- **Home:** PF02, adding to the manager workflow, step 7, the pre-merge checklist (DM-30 4.3), which names the PR run by its event on the exact head.

#### PF02-R38 — Run the classifier as written, with full SHAs

- **Rule:** Run the trusted classifier from the manager workflow's command, with full 40-character SHAs from `git rev-parse` (cited). Run it in a clone with full history: when `git rev-parse --is-shallow-repository` prints `true`, run `git fetch --unshallow origin` first, since a shallow history gives a wrong merge base.
- **Check:** the command line and its output.
- **Sources:** AM3-03, AM3-14, AM5-01, AM12-01.
- **Changed:** AM12-01 added the full history: the classifier in a shallow clone gave the merge base `04b89d3` for `947576d`.
- **Home:** PF02, adding to the manager workflow, "Classification (trusted base policy)" (the full history).

### 4.7 Codex and the waits

#### PF02-R39 — Wait for Codex before a review prompt and before a merge

- **Rule (cited):** before an exact-head review prompt, or a correction prompt for code under review, wait for Codex's review on the code head and on the prompt's commit and handle each finding; tell Nathan to hold a review that a new finding may change. Merge only after Codex's summary shows its code review complete on the final head.
- **Check:** Codex's completed summary on each commit, read before the prompt or the merge.
- **Sources:** AM2-06, AM7-13.
- **Changed:** AM2-06 required both of Codex's reviews; its security reviews are no longer available (OD-41).
- **Home:** the manager workflow, step 6, "Wait for Codex before a review prompt", and step 7, "Wait for Codex".

#### PF02-R40 — Read the PR's new comments before every prompt or consultation

- **Rule:** After any push to the PR's head, a records-only push included, wait for Codex's pass on that commit, and list the PR's review comments created since the last read, printing each. Read that list before writing or giving the next prompt or consultation, and set a watch on every pass whose result is not yet read. A wait that reads only Codex's state on the newest commit is not enough. The one exception is the pass on a consultation's own commit (PF02-R41).
- **Check:** the comment listing, with its time, before each prompt or consultation is given.
- **Sources:** AM11-17, AM11-28, AM11-29.
- **Changed:** AM11-17 asked for the comments before any prompt; AM11-28 extended the wait to consultations; AM11-29 made the listing part of the wait and counted a records-only push.
- **Home:** PF02.

#### PF02-R41 — Do not hold a consultation for a Codex pass on its own commit

- **Rule:** A consultation is not held for Codex's pass on its own commit. Before it is written, PF02-R40's wait applies to every earlier push. Once its commit is pushed, the manager lists the PR's review comments again, gives the message, and keeps a watch on the pass over the consultation's commit. A finding from that pass goes to the Dev Manager as an addition, without holding the message, and PF02-R40's wait reads it before the next prompt.
- **Check:** the relay message follows the push and a comment listing made after it; the watch on the consultation's commit is named.
- **Sources:** AM11-10.
- **Changed:** AM11-28 applied the wait to consultations too; AM11-10's exemption stands for the consultation's own commit only, as the Dev Manager confirmed (DM-76; the M08 record, conflict C2).
- **Home:** PF02. The manager workflow's wait for Codex (step 6) covers review and correction prompts only.

#### PF02-R42 — End a wait only with a watch set

- **Rule:** A turn that waits on CI or Codex for the manager's own pushes ends only after a background watch or a scheduled wake-up is set for it, and the message to Nathan names it and when it fires. A session's run of record is not watched (PF02-R36).
- **Check:** the watch's or wake-up's identity and time, named in the message.
- **Sources:** AM11-05.
- **Home:** PF02.

### 4.8 Messages to Nathan and turn endings

#### PF02-R43 — Nothing unexplained, and no option without a gain

- **Rule (cited):** an item goes to Nathan only with what it is, what breaks without it, the options and the recommendation; questions go to the Dev Manager first; an option goes to him only with what it gains, and when the record gives no reason for the alternative, the item asks for his direction alone.
- **Check:** each item in the message carries those parts.
- **Sources:** AM4-01, AM4-02, AM5-23.
- **Changed:** AM4-02's own form, putting a disagreement between the manager's call and TypeSafe to Nathan, is superseded: the manager's call is not put to him (OD-34), and his pick is not asked (OD-53, D1).
- **Home:** the manager workflow, "Nothing unexplained goes to Nathan" (OD-32).

#### PF02-R44 — One prompt per message, and a session's status from his words or its branch

- **Rule (cited):** each message carries at most one prompt or relay message, pasted in full, for the next task not recorded as complete; a session's status comes only from Nathan's own words or its pushed branch.
- **Check:** one prompt block per message; each status claim cites his words or the branch.
- **Sources:** AM3-11, AM3-12.
- **Home:** the manager workflow, "The process is linear" (OD-29).

#### PF02-R45 — Never ask Nathan to perform a GitHub operation

- **Rule (cited):** the manager never asks Nathan to perform a GitHub operation, a re-run included; a CI failure that seems to call for one, or any question about how to verify a head, goes to the Dev Manager first, with options that need no action from him; a written procedure that says otherwise is reported to the Dev Manager as a conflict, not followed.
- **Check:** no message or PR comment asks him for one.
- **Sources:** AM9-10.
- **Home:** the manager workflow, "Branches and pushes", "Actions re-runs"; OD-58; the next-manager start procedure, "Reporting to Nathan".

#### PF02-R46 — Plain words stay true to the record, and each option gets all its lines

- **Rule:** Before a plain-language message goes to Nathan, check every count, comparison and duration in it against the record, line by line, and give each option what it is, what it costs, what it closes and what stays open.
- **Check:** each option in the message carries the four lines; each figure traces to a record line.
- **Sources:** AM7-05.
- **Home:** PF02, adding to the manager workflow, "Claims: a checklist" (counts, and *every*, *no* or *never*), and "Nothing unexplained goes to Nathan" (OD-32).

#### PF02-R47 — Name a pending decision in plain words

- **Rule:** A reminder to Nathan of a pending decision says in plain words what the decision is about, every time, never only its label.
- **Check:** each reminder states the decision's subject.
- **Sources:** AM11-18.
- **Home:** PF02, under OD-32.

#### PF02-R48 — Take the manager's own next step before ending a turn

- **Rule:** Before ending a turn, check the handoff's next actions and take every step that needs nothing from Nathan or another session. A report that closes an item carries the next item's prompt or consultation, ready to run. "NOTHING NEEDED" is used only when the next step is someone else's.
- **Check:** at a turn's end, the next action's owner is named and is not the manager.
- **Sources:** AM7-09, AM8-16.
- **Home:** PF02. The next-manager start procedure names the states ("Reporting to Nathan").

#### PF02-R49 — Check a tool before saying it cannot

- **Rule:** Before telling Nathan that a tool cannot do something, check the tool's documentation. Say what the current setup does.
- **Check:** the documentation read, cited.
- **Sources:** AM3-20.
- **Home:** PF02.

#### PF02-R50 — Apply an owner direction as given, and ask who acts when it is unclear

- **Rule:** An owner direction about the shape of a record or a scale is applied as given; a documentation fact that seems to contradict it is stated once, in one sentence, and does not change the design. A direction that it is time to create a new manager session is OD-31's case: the outgoing manager creates the successor. When the words leave unclear who acts, ask in one line before recording either path.
- **Check:** the record of the direction matches its words; any question asked is one line.
- **Sources:** AM4-04, AM7-14.
- **Changed:** AM4-04's scorer-request prevention (a live reachability test before a request is adopted) is retired: the scoring skill carries the request and its rule (OD-34, OD-42). Its judgement prevention is stated by the manager workflow, step 3: a call the manager records for comparison goes into the uses table before the run and is not put to Nathan (OD-34).
- **Home:** PF02; OD-31 for the successor case; the manager workflow, step 3, for the manager's own judgement (OD-34).

### 4.9 Records, claims and verification

#### PF02-R51 — Run the claims checklist

- **Rule (cited):** *every*, *no* or *never* only after tracing each path; a source's qualifiers in its own words; every count in a message to Nathan checked against its source; what clears a stuck state named.
- **Check:** as the checklist states.
- **Sources:** AM5-08, AM7-06, AM7-08, AM7-10, AM8-03, AM8-04, AM8-06, AM8-08, AM11-16.
- **Home:** the manager workflow, "Claims: a checklist" (DM-01 P8).

#### PF02-R52 — Trace a state's end, cite only lines read, and keep a bound's hedge

- **Rule:** Before writing how a stuck state ends, trace every call that could reset it. Cite a line number only after reading it at the commit named. A figure carried into a summary keeps its hedge ("about", "up to") or its exact value; a bound is never rounded down into "within".
- **Check:** each cited line was read at the named commit; each carried figure matches its source's form.
- **Sources:** AM5-08, AM8-06.
- **Home:** PF02, adding to the manager workflow, "Claims: a checklist".

#### PF02-R53 — Take every figure from command output over the whole source

- **Rule:** Every count, diffstat, range or maximum in a record or in text sent to the scorer is derived from the whole source, never from a truncated listing (check the line count against the expected total). A diffstat or path count is pasted from command output (`git diff --numstat` or `--shortstat`; `git diff --name-status … | cut -c1 | sort | uniq -c`), and added or removed lines are counted from the diff's `+` and `-` lines, not from a reading of the file. A verification compares each of its own outputs with the figure the report gives for the same check, and says which job or step a line belongs to only after reading it there. A local re-run of a suite or a test set runs on a whole-tree copy of the head, since tests read paths outside their own folder.
- **Check:** each figure traces to its whole source; diffstats and path counts are pasted command output.
- **Sources:** AM4-06, AM5-12, AM6-02, AM8-09, AM8-21, AM10-03, AM11-06, AM12-02.
- **Changed:** AM12-02 added the whole tree: the proof's offline tests, re-run on an export of two folders, gave 31 errors from tests that read the contracts package and the workflow.
- **Home:** PF02, adding to the manager workflow, "Claims: a checklist" ("Check every count").

#### PF02-R54 — A session's claim stays the session's until checked

- **Rule:** Give an implementer's claim (a live result, a completeness claim, a statement about build output) as the session's until a review or the manager's own check confirms it, and name the view or check behind a live result cited as a decision's basis. A verification that meets "any", "every" or "all" tries at least two forms the session did not list, records each with its result, and still attributes the claim. A residual said to be reachable "only through" one route is tested against every input that reaches the check. No test over source proves "through any binding", so the manager never makes such a claim in its own words, and a brief asks for named forms and a stated guarantee with its limits.
- **Check:** the record attributes the claim and lists the manager's own forms with their results.
- **Sources:** AM3-13, AM5-06, AM8-21, AM9-03.
- **Home:** PF02, adding to the manager workflow, "Claims: a checklist" (DM-01 P8). The addition is AM9-03's, as DM-38 4.1 and 4.2 strengthen it.

#### PF02-R55 — Follow a stray read to every result

- **Rule (cited):** a read that can take in rows from outside what it measures is followed to every result computed from those rows and every record that reports one, and each is checked.
- **Check:** the list of results and records checked.
- **Sources:** AM5-16, AM5-17.
- **Home:** the manager workflow, step 5, "Follow a stray read to every result".

#### PF02-R56 — Compare two runs by what is the same

- **Rule:** A record that compares two runs of a timing-dependent suite says what is the same (the plan, the outcome) and gives each run's own counts; it does not call them "the same results".
- **Check:** each run's counts are stated.
- **Sources:** AM5-21.
- **Home:** PF02.

#### PF02-R57 — Write an ID or a result only after reading it

- **Rule:** An ID, a count or a result goes into any record, a PR description included, only after it is read; an item not yet checked stays unticked and says "pending". A merge commit's SHA comes from `git log --merges -1` after the merge, not from the batch's last commit.
- **Check:** each ID in the record matches the tool output it was read from.
- **Sources:** AM8-02, AM8-15.
- **Home:** PF02.

#### PF02-R58 — Route every item a session addresses

- **Rule:** The manager's verification lists every item a session's report addresses to the Dev Manager or to Nathan, and routes each in the same batch.
- **Check:** the verification's list, with each item's route.
- **Sources:** AM8-18.
- **Home:** PF02.

#### PF02-R59 — Check a decision message's facts against the cells

- **Rule:** Before a decision message goes to the Dev Manager, check each statement that cites a row or a design text against that row's own cells or that text's own words, not a summary of them. A paraphrase of a source is quoted or marked as a paraphrase.
- **Check:** each cited row was read; paraphrases are marked.
- **Sources:** AM10-10.
- **Home:** PF02.

#### PF02-R60 — Links resolve, and survive a prune

- **Rule:** Before each records commit, resolve every relative link added in it and confirm the target exists. A prune batch lists every link to the pruned files in the repository and in Notion (Implementation Control and the Work Register rows), pins each to a commit that holds the file, and reads Notion back before reporting the prune. A script that rewrites links resolves each target against its file's directory and matches the full path, and the manager reads the removed targets in the word diff before committing.
- **Check:** every added relative link resolves; no link to a pruned file is left on a branch.
- **Sources:** AM8-19, AM9-11, AM10-16, AM12-08.
- **Home:** PF02, adding to the manager workflow, step 5, "Batching records" (the receipt commit-pins the item's links into `docs/ephemeral/`), and step 7 (Notion links only to `main`, a commit ID or the manager branch).

### 4.10 Branches, merges, handovers and next actions

#### PF02-R61 — Report the branch state at each merge

- **Rule (cited):** at each merge, list every remote branch with what is merged and what is kept and why, read the branch cleanup's summary, and link Notion only to `main`, a commit ID or the manager branch.
- **Check:** the merge receipt's branch list against the remote.
- **Sources:** AM5-24.
- **Home:** the manager workflow, step 7, "Report the branch state" and "Link Notion only to `main`, a commit ID or the manager branch" (OD-09, OD-39, OD-58).

#### PF02-R62 — Record a promise when it is made

- **Rule:** A later action the manager promises, in a message or a record, goes into the handoff's next actions in the same batch.
- **Check:** each promise in a message has a matching next-actions line.
- **Sources:** AM2-07.
- **Home:** PF02.

#### PF02-R63 — Write next actions from the plan

- **Rule:** Before writing next actions, re-read PF01's sequence, the owner directions in force and the previous handoff's next actions, and quote the governing line in the handoff.
- **Check:** the handoff's next actions quote their governing line.
- **Sources:** AM2-08.
- **Changed:** AM2-08 named the initiation assignment, which M02 completed (the next-manager start procedure, step 3); the owner directions in force take its place (OD-49).
- **Home:** PF02.

#### PF02-R64 — Build the start procedure from the canon, and read it as the successor will

- **Rule:** A start prompt's reading list is built from the first paragraph of root `AGENTS.md` and PF00's "Start here". Before a handover commit, read the start procedure below the line as the successor will receive it, and check that every section of the mistakes log has its summary row.
- **Check:** the reading list covers both sources; a count of the log's sections against its rows.
- **Sources:** AM2-09, AM4-05.
- **Home:** PF02, adding to the manager workflow, "Handover checklist" ("brings the next-manager start prompt up to date").

#### PF02-R65 — At the start, read the open PR's threads

- **Rule (cited):** at the start, and before any message that says nothing else is open, list the open manager PR's review threads and Codex's latest summary, and check each unresolved thread against the records.
- **Check:** the thread listing in the first report's preparation.
- **Sources:** AM8-01.
- **Home:** the next-manager start procedure, step 2, "Your branch".

#### PF02-R66 — Change the environment only through a new session

- **Rule:** The manager never runs setup tooling or changes its own environment; an environment change takes effect through a new session.
- **Check:** no setup script or toolchain install runs in a manager session.
- **Sources:** AM2-10.
- **Home:** PF02.

### 4.11 TypeSafe readings

#### PF02-R67 — Keep readings out of briefs, handoffs and reports

- **Rule (cited):** the TypeSafe reading lives in the prompt's header and the Notion uses table only.
- **Check:** before a records commit that names a prompt, `grep -nE '(Fable|Opus|Sonnet|Haiku) [0-9.]+ at'` over the changed briefs, handoffs and reports finds no reading.
- **Sources:** AM8-14.
- **Changed:** AM8-14 let Nathan's pick stand in those files; his pick is no longer recorded (OD-53, D1).
- **Home:** the manager workflow, step 3 (DM-01 P8); PF02 holds the check.

#### PF02-R68 — Create a uses row from the printed row, whole

- **Rule (cited):** a uses-table row is the scoring skill's printed "Notion row" object, pasted whole and never retyped; the manager writes three fields by hand: *Nathan's pick* ("not recorded"), *PR* and *PR metrics*.
- **Check:** the row's read-back matches the printed row field by field, with the three hand-written fields filled.
- **Sources:** AM9-09, AM11-30.
- **Changed:** AM9-09 added the PR field to the printed properties; AM11-30 made the whole printed row the base, with the pick "not recorded" at creation and only *PR* and *PR metrics* added. The workflow's step 3 named the pick as the one hand-written field until DM-76 corrected it (the M08 record, conflict C1).
- **Home:** the manager workflow, step 3 (DM-34 D1.1; the scoring skill's step 4); PF02 holds the check.

## 5. Retired rules

These preventions no longer apply. Nothing is deleted from the log; each stays there as history.

| Entries | Prevention | Why retired | Superseding source |
|---|---|---|---|
| AM3-02 | Before recording a level, re-read what the manager promised; record a conditional level commitment in the brief's "Reasoning levels" | The manager makes no conditional commitment and puts no reading in a brief; a call it records for comparison goes only into the uses table before the run and is never put to Nathan, so there is no level promise to re-read | The manager workflow, step 3 (DM-01 P8; OD-34, OD-53 D1) |
| AM3-18 | When verifying a fix-reversal run, check each reversal's failure reason, not only the summary, "until the script itself rejects an edit that does not compile" | Its own end condition is met: the script now reports an edit that does not compile or import | P06.1-C3; `proofs/stream-chat/checks/fix_reversals.py` and its test `test_an_edit_that_does_not_compile_or_import_is_reported` |
| AM4-03 | A scoring request carries researched facts; any change is a new version with a rule saved before its first run; a model claim is written as judgement unless sourced | The manager no longer writes the request: the scoring skill carries the request and its rule, and the manager writes only the description, to the skill's template | OD-34, OD-42; the manager workflow, step 3, "Write the description to the skill's template" |

**Parts retired from entries that keep a rule.** These are stated in the rule's "Changed" line: AM2-06's "both reviews" (OD-41; PF02-R39); AM4-02's model-and-level choice (OD-34, OD-53 D1; PF02-R43); AM4-04's scorer-request prevention (OD-34, OD-42; PF02-R50); AM2-08's initiation assignment, completed by M02 (PF02-R63); AM5-02's pick column (OD-53 D1; PF02-R08); AM8-14's allowance for Nathan's pick (OD-53 D1; PF02-R67).

The log holds no entry about Google Drive or the historical App Builder or App Planner roles, so none is retired for them.

## 6. Recurring mechanisms

The mechanisms that recur across entries, with the rules that answer them. A count is the number of entries listed.

| Mechanism | Count | Entries | Rules |
|---|---|---|---|
| A time written before the clock was read, or not captured | 7 | AM2-05, AM9-04, AM10-17, AM10-18, AM11-03, AM11-07, AM11-25 | R01 |
| A supersession sweep that missed a home, a term or Notion | 15 | AM3-08, AM3-10, AM3-22, AM4-07, AM5-10, AM5-13, AM5-22, AM9-12, AM10-09, AM11-11, AM11-12, AM11-14, AM11-15, AM11-20, AM11-26 | R02 to R05 |
| A Notion status left stale in a property, body or row the update did not touch | 6 | AM3-23, AM5-02, AM5-03, AM5-07, AM5-09, AM8-07 | R08 to R10 |
| A Notion read-back that checked only the edited strings, leaving standing lines stale | 13 | AM3-09, AM8-11, AM8-13, AM8-22, AM9-01, AM9-07, AM10-05, AM10-08, AM10-20, AM10-21, AM10-22, AM11-02, AM11-08 | R11, R12 |
| An edit that replaced a list or an opening but left the sentence after it | 4 | AM10-07, AM11-02, AM11-08, AM11-19 | R06, R11, R16 |
| A later push that cancelled an earlier push's runs, a run of record among them | 6 | AM5-04, AM5-14, AM8-20, AM9-02, AM10-01, AM11-04 | R33, R35; R21 and R07 for the errors that forced a correcting push |
| A session's or a source's claim repeated without checking | 10 | AM3-13, AM3-16, AM3-18, AM5-06, AM5-12, AM7-01, AM7-08, AM8-21, AM9-03, AM10-14 | R17, R28, R29, R53, R54 |
| A count or figure not derived from its source | 8 | AM4-06, AM5-08, AM6-02, AM8-09, AM8-21, AM10-03, AM11-06, AM11-16 | R51 to R53 |
| A summary that said more than, or other than, its source | 9 | AM3-21, AM7-05, AM7-06, AM7-10, AM8-03, AM8-04, AM8-06, AM8-08, AM9-05 | R13, R46, R51, R52 |
| Something named in a brief, prompt or proposal without reading the code | 9 | AM5-18, AM6-03, AM10-02, AM10-11, AM10-12, AM10-15, AM10-19, AM11-09, AM11-23 | R14, R15, R23 to R25 |
| A prompt that could not work as written | 8 | AM2-02, AM5-15, AM8-17, AM9-06, AM10-13, AM11-21, AM11-22, AM11-24 | R20, R22, R25 to R27 |
| A Codex result not read, or not waited for, before the next step | 6 | AM2-06, AM7-13, AM8-01, AM11-17, AM11-28, AM11-29 | R39, R40, R65 |
| A turn ended with the manager's own step undone, or waiting on nothing | 4 | AM7-09, AM8-16, AM11-05, AM11-10 | R41, R42, R48 |
| A question or choice put to Nathan that was not his, or not explained | 6 | AM4-01, AM4-02, AM5-23, AM7-12, AM9-10, AM11-18 | R19, R43, R45, R47 |
| The handoff over its 5 KB limit | 3 | AM8-12, AM11-04, AM11-27 | R07 |
| The classifier given a symbolic or short SHA | 3 | AM3-03, AM3-14, AM5-01 | R38 |
| A logged prevention not run at its next use | 8 | AM8-13, AM8-22, AM10-17, AM10-18, AM11-03, AM11-07, AM11-27, AM11-29 | Each rule's check (section 2): R01, R07, R11, R40 |

## 7. Events with no standing rule

| Entry | Reason |
|---|---|
| AM5-20 | A scratch worktree restored with `git checkout -- .` kept staged reverted files; the unchanged control failed, the results were discarded and redone, and no record carried them. The entry's own control caught it, and it has no section or prevention (the log's rule for a slip its own tool caught). |
| AM11-13 | A count error in a review prompt, seen before the prompt was given and given as written by choice, with Nathan told. Its section's prevention answers AM11-14 and AM11-15 only; the count is the kind PF02-R53 and the claims checklist already check. |

## 8. Maintenance

- Each new mistakes-log entry names the PF02 rule it broke, or proposes a new or changed rule.
- The manager applies the change to PF02 with the next records batch.
- A PF02 change is governing Markdown: the Dev Manager reads it, at a named commit, before its pull request merges (the charter, "Read before it takes effect").
- PF02's revision history records each change.
- A batch that changes a passage a PF02 rule cites, in a governing home or in the next-manager start procedure, checks that rule's gist and "Home" line in the same batch, and corrects PF02 if they no longer hold; that correction, like any PF02 change, goes to the Dev Manager's read. The start procedure is not governing Markdown under the charter, so a change to a passage PF02 cites there reaches the Dev Manager only this way (DM-76).
- Entries added to the log after `553d9ed96bf3fb32e57e3ecf59d759eb3bcadf53` are folded in by the manager at integration, under this rule.
- **Folded in at integration** (App Manager 12, 17 November 2026): AM11-30 into PF02-R68 (DM-76, HH12); AM11-31 into R12; AM11-32 into R20; AM11-33 into R04; AM12-01 into R38; AM12-02 into R53; AM12-03 into R13; AM12-04 into R01; AM12-05 into R37; AM12-06 into R18; AM12-07 into R02; AM12-08 into R60. R13, R18, R37, R38 and R53 gain the addition each entry's prevention sets; the others are repeats of their rule as it stands. No entry is retired, and none is an event with no standing rule.

## 9. Revision history

1.0 — established from the mistakes log at `553d9ed96bf3fb32e57e3ecf59d759eb3bcadf53`, AM2-01 to AM11-29, 167 entries (M08; OD-66): 68 rules in 11 groups, 3 entries retired, 2 events with no standing rule; with the Dev Manager's read applied at integration (DM-76, a read of `9a90bd8`) and the log's later entries folded in (AM11-30, into PF02-R68; AM11-31 to AM12-08, each into the rule it broke, as section 8 lists).
