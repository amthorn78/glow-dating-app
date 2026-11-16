# M08 evidence — the manager practice canon (GAPP-PF02)

- **Work item:** M08, the manager practice canon (OD-66, 16 November 2026).
- **Prompt:** revision 1, from commit `553d9ed96bf3fb32e57e3ecf59d759eb3bcadf53` of the manager branch `claude/magical-wozniak-yfmmx2` (`docs/ephemeral/2026-11-16-m08-manager-practice-canon-prompt.md`).
- **Session:** the documentation session for M08, started by Nathan in `Glow App - No Stream`. It is neither the manager nor a reviewer.
- **Branch:** `claude/beautiful-pascal-7n0o9n`, from `553d9ed96bf3fb32e57e3ecf59d759eb3bcadf53`. Its final head is named in the report Nathan relays (a record cannot name the commit that contains it).
- **Changed paths:** `docs/pf-canon/GAPP-PF02-Manager-Practice-Rules.md` (new); `docs/pf-canon/GAPP-PF00-Canon-Index-and-Authority.md` (registry row, authority-map row, header revision and date, revision history 1.12); `docs/README.md` (the `docs/pf-canon/` row and one new "One home per fact" row); this record (new).
- **Next:** Dev Manager 5's read of PF00 and PF02 at this branch's head (governing Markdown), with the design choices below; then the manager's integration, after PR47 merges, in its own pull request.

## 1. Environment check (names only)

- `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`: none present.
- `STREAM_*` and `PG*` names: none present.
- `AWS_*` names present: `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE`, `AWS_SECRET_ACCESS_KEY`. Their values were never read, printed or used.
- GitHub token names present: `GH_TOKEN`, `GITHUB_TOKEN`. Their values were never read, printed or used.
- No provider, HDE, database, Railway or other external service was called. GitHub was used read-only (fetch and `ls-remote`), and Notion was not touched.

## 2. Start gate

All checks passed, on 16 November 2026, after the prompt's commit (01:36:28 UTC by its commit time); the clock was not read at the gate:

| Check | Result |
|---|---|
| `git switch -C claude/beautiful-pascal-7n0o9n 553d9ed…`, then `git rev-parse HEAD` | `553d9ed96bf3fb32e57e3ecf59d759eb3bcadf53` |
| `553d9ed…` an ancestor of `origin/claude/magical-wozniak-yfmmx2` | "this prompt's commit is on the live branch"; the live branch's head was `553d9ed…` itself |
| `git diff --name-only 553d9ed… origin/claude/magical-wozniak-yfmmx2 -- docs/pf-canon docs/README.md` | empty |
| `ls docs/pf-canon/` | PF00 and PF01 only |
| `grep -c -F '**Revision:** 1.11'` in PF00 | 1 |
| Entry count, `grep -o -E '^\| AM[0-9]+-[0-9]+ '` over the log, `wc -l` | 167 |
| Last entry in row order | AM11-29 |

`origin/main` was `947576d98b7c3103455a670c20fdba2734ff5053`.

## 3. What was read

Read completely at `553d9ed…`: root `AGENTS.md` and `CLAUDE.md`; `docs/README.md`; PF00 whole and PF01's D08 to D10 (section 10, lines 444 to 478, with the decisions table); the manager workflow whole; the Dev Manager charter whole; the CI policy whole; the next-manager start procedure whole; the owner-direction register whole (OD-01 to OD-66).

**The mistakes log, whole** (1,492 lines, 218,162 bytes), by line range, in this order: 1–105 (header, the adding rules and the summary rows AM2-01 to AM7-14); 105–192 (rows AM7-14 to AM11-29); 192–391 (App Manager 2; App Manager 3 to AM3-12); 392–591 (AM3-12 to AM5-08); 592–781 (AM5-09 to AM7-05); 782–961 (AM7-05 to AM8-12); 962–1136 (AM8-12 to AM9-12); 1137–1316 (App Manager 11, AM11-23 down to AM11-01); 1317–1492 (AM11-01, the AM10-20 to AM10-22 section, and App Manager 10, AM10-19 down to AM10-01). Every row and every section was read.

The log's structure, from a scratch script (`sections.py`, below): 167 rows, all IDs unique; 160 entries have a section (two shared sections: AM10-20 to AM10-22, and AM11-13 to AM11-16); 9 have only a row: AM3-14, AM3-17, AM5-04, AM5-20, AM9-02, AM11-03, AM11-04, AM11-06, AM11-07. App Manager 11's sections come before App Manager 10's, and both run in reverse order. Kinds beyond the four the log defines appear in rows: scope (AM6-03), records (AM8-14, AM8-19, AM11-19, AM11-20, AM11-27), prompt (AM8-20, AM10-01, AM10-13, AM11-22 to AM11-24) and communication (AM11-18).

## 4. Method

1. The session read every governing home and the whole log itself (section 3), and drafted the rule set from that reading.
2. **Extraction.** A read-only workflow of nine subagents, one per block of entries, returned for every entry its ID, date, kind, mechanism, prevention, the prevention's source (section, row or a later entry), and a check of the prevention against the six governing homes (stated, partly, not stated, contradicted or moot, with the home's section and a verbatim quote). All 167 entries came back, none duplicated. The session compared each result with its draft and changed the draft where they differed (section 8).
3. **Verification.** A second read-only workflow of four subagents checked the written PF02 adversarially: the cited rules against their homes; the PF02-held rules against their source entries, in two halves; and completeness, conflicts and the mechanism index. Its findings and their dispositions are in section 9.
4. **Scripts,** run from the session's scratch directory outside the checkout, with `python3 -I`, over the log as `git show 553d9ed…:docs/continuity/manager-mistakes.md` writes it: `sections.py` (rows to sections), `coverage.py` (section 6) and `mech.py` (section 6). None is in the repository.

## 5. Counts

- **Log entries read:** 167, AM2-01 to AM11-29.
- **Rules:** 68, in **11 groups**: times and clocks (1); standing lines, revision numbers and supersession sweeps (6); Notion syncs and read-backs (6); briefs, proposals and the Dev Manager's reports (6); prompts (15); runs, pushes and commands (4); Codex and the waits (4); messages to Nathan and turn endings (8); records, claims and verification (10); branches, merges, handovers and next actions (6); TypeSafe readings (2).
- **By home:** 17 rules are cited only (a governing home states them; PF02 gives the gist and the section): R02, R08, R10, R19, R32, R34, R36, R38, R39, R43, R44, R45, R51, R55, R61, R65, R67. 17 cite a home for the core and hold an addition ("PF02, adding to …" and similar): R03, R06, R07, R11, R12, R17, R22, R33, R35, R37, R46, R47, R52, R53, R54, R60, R64. 34 are held by PF02 alone: R01, R04, R05, R09, R13 to R16, R18, R20, R21, R23 to R31, R40 to R42, R48 to R50, R56 to R59, R62, R63, R66, R68.
- **Retired:** 3 entries (AM3-02, AM3-18, AM4-03), and five parts of entries that keep a rule, each named in its rule's "Changed" line.
- **Events with no standing rule:** 2 (AM5-20, AM11-13).
- **Recurring mechanisms:** 17 rows.

## 6. Coverage

Every entry ID at `553d9ed…` must appear in exactly one of: at least one rule's sources; the retired list; the events with no standing rule. `coverage.py` parses PF02 itself (each rule's "Sources" line, the retired table, the no-rule table) and compares the IDs with the log's rows. Its output on the final PF02:

```
log entries: 167 | first AM2-01 | last by row order AM11-29
rules: 68
IDs in rule sources: 162
IDs retired: 3
IDs with no standing rule: 2
IDs in no place: 0 []
IDs in more than one place: 0 []
IDs cited that are not log entries: []
COVERAGE COMPLETE

-- rule sources --
PF02-R01 AM2-05, AM9-04, AM10-17, AM10-18, AM11-03, AM11-07, AM11-25
PF02-R02 AM3-08, AM3-10, AM3-22, AM5-10, AM5-13, AM5-22, AM11-11
PF02-R03 AM3-22, AM9-12, AM10-09, AM11-14
PF02-R04 AM4-07, AM11-15, AM11-26
PF02-R05 AM3-15, AM7-07, AM11-12, AM11-20
PF02-R06 AM11-19
PF02-R07 AM8-12, AM11-04, AM11-27
PF02-R08 AM2-11, AM3-01, AM3-04, AM5-02, AM5-03, AM5-07, AM5-11
PF02-R09 AM2-11, AM3-23
PF02-R10 AM5-09, AM8-07
PF02-R11 AM8-11, AM8-13, AM8-22, AM9-01, AM9-07, AM10-08, AM10-20, AM10-21, AM10-22, AM11-02, AM11-08
PF02-R12 AM3-09, AM10-05
PF02-R13 AM3-21, AM9-05
PF02-R14 AM10-02, AM10-11, AM10-15
PF02-R15 AM5-18
PF02-R16 AM8-05, AM9-08, AM10-07
PF02-R17 AM10-06, AM10-14
PF02-R18 AM3-06, AM3-07
PF02-R19 AM7-12, AM10-04
PF02-R20 AM2-01, AM2-02, AM2-03, AM8-17
PF02-R21 AM2-04, AM7-03, AM10-01
PF02-R22 AM5-15, AM10-13, AM11-21
PF02-R23 AM3-08, AM6-03, AM10-12, AM11-09
PF02-R24 AM10-19
PF02-R25 AM11-22, AM11-23
PF02-R26 AM5-05, AM11-24
PF02-R27 AM9-06
PF02-R28 AM5-19, AM7-01, AM7-04
PF02-R29 AM3-16
PF02-R30 AM7-11
PF02-R31 AM11-01
PF02-R32 AM3-17, AM3-19
PF02-R33 AM5-14, AM7-02, AM8-20
PF02-R34 AM3-05
PF02-R35 AM5-04, AM9-02
PF02-R36 AM6-01
PF02-R37 AM8-10
PF02-R38 AM3-03, AM3-14, AM5-01
PF02-R39 AM2-06, AM7-13
PF02-R40 AM11-17, AM11-28, AM11-29
PF02-R41 AM11-10
PF02-R42 AM11-05
PF02-R43 AM4-01, AM4-02, AM5-23
PF02-R44 AM3-11, AM3-12
PF02-R45 AM9-10
PF02-R46 AM7-05
PF02-R47 AM11-18
PF02-R48 AM7-09, AM8-16
PF02-R49 AM3-20
PF02-R50 AM4-04, AM7-14
PF02-R51 AM5-08, AM7-06, AM7-08, AM7-10, AM8-03, AM8-04, AM8-06, AM8-08, AM11-16
PF02-R52 AM5-08, AM8-06
PF02-R53 AM4-06, AM5-12, AM6-02, AM8-09, AM8-21, AM10-03, AM11-06
PF02-R54 AM3-13, AM5-06, AM8-21, AM9-03
PF02-R55 AM5-16, AM5-17
PF02-R56 AM5-21
PF02-R57 AM8-02, AM8-15
PF02-R58 AM8-18
PF02-R59 AM10-10
PF02-R60 AM8-19, AM9-11, AM10-16
PF02-R61 AM5-24
PF02-R62 AM2-07
PF02-R63 AM2-08
PF02-R64 AM2-09, AM4-05
PF02-R65 AM8-01
PF02-R66 AM2-10
PF02-R67 AM8-14
PF02-R68 AM9-09

-- in rules --
AM2-01, AM2-02, AM2-03, AM2-04, AM2-05, AM2-06, AM2-07, AM2-08, AM2-09, AM2-10, AM2-11, AM3-01, AM3-03, AM3-04, AM3-05, AM3-06, AM3-07, AM3-08, AM3-09, AM3-10, AM3-11, AM3-12, AM3-13, AM3-14, AM3-15, AM3-16, AM3-17, AM3-19, AM3-20, AM3-21, AM3-22, AM3-23, AM4-01, AM4-02, AM4-04, AM4-05, AM4-06, AM4-07, AM5-01, AM5-02, AM5-03, AM5-04, AM5-05, AM5-06, AM5-07, AM5-08, AM5-09, AM5-10, AM5-11, AM5-12, AM5-13, AM5-14, AM5-15, AM5-16, AM5-17, AM5-18, AM5-19, AM5-21, AM5-22, AM5-23, AM5-24, AM6-01, AM6-02, AM6-03, AM7-01, AM7-02, AM7-03, AM7-04, AM7-05, AM7-06, AM7-07, AM7-08, AM7-09, AM7-10, AM7-11, AM7-12, AM7-13, AM7-14, AM8-01, AM8-02, AM8-03, AM8-04, AM8-05, AM8-06, AM8-07, AM8-08, AM8-09, AM8-10, AM8-11, AM8-12, AM8-13, AM8-14, AM8-15, AM8-16, AM8-17, AM8-18, AM8-19, AM8-20, AM8-21, AM8-22, AM9-01, AM9-02, AM9-03, AM9-04, AM9-05, AM9-06, AM9-07, AM9-08, AM9-09, AM9-10, AM9-11, AM9-12, AM10-01, AM10-02, AM10-03, AM10-04, AM10-05, AM10-06, AM10-07, AM10-08, AM10-09, AM10-10, AM10-11, AM10-12, AM10-13, AM10-14, AM10-15, AM10-16, AM10-17, AM10-18, AM10-19, AM10-20, AM10-21, AM10-22, AM11-01, AM11-02, AM11-03, AM11-04, AM11-05, AM11-06, AM11-07, AM11-08, AM11-09, AM11-10, AM11-11, AM11-12, AM11-14, AM11-15, AM11-16, AM11-17, AM11-18, AM11-19, AM11-20, AM11-21, AM11-22, AM11-23, AM11-24, AM11-25, AM11-26, AM11-27, AM11-28, AM11-29

-- retired --
AM3-02, AM3-18, AM4-03

-- no standing rule --
AM5-20, AM11-13
```

`mech.py` checks that each recurring-mechanism row's count equals the entries it lists, without duplicates, and that every rule it names exists:

```
  7 vs   7  A time written before the clock was read, or not captured []
 15 vs  15  A supersession sweep that missed a home, a term or Notion []
  6 vs   6  A Notion status left stale in a property, body or row the up []
 13 vs  13  A Notion read-back that checked only the edited strings, lea []
  4 vs   4  An edit that replaced a list or an opening but left the sent []
  6 vs   6  A later push that cancelled an earlier push's runs, a run of []
 10 vs  10  A session's or a source's claim repeated without checking []
  8 vs   8  A count or figure not derived from its source []
  9 vs   9  A summary that said more than, or other than, its source []
  9 vs   9  Something named in a brief, prompt or proposal without readi []
  8 vs   8  A prompt that could not work as written []
  6 vs   6  A Codex result not read, or not waited for, before the next  []
  4 vs   4  A turn ended with the manager's own step undone, or waiting  []
  6 vs   6  A question or choice put to Nathan that was not his, or not  []
  3 vs   3  The handoff over its 5 KB limit []
  3 vs   3  The classifier given a symbolic or short SHA []
  8 vs   8  A logged prevention not run at its next use []
ALL COUNTS MATCH
```

## 7. Conflicts, for the Dev Manager

| # | Entry | Home | The two texts | Recommendation |
|---|---|---|---|---|
| C1 | AM9-09 (PF02-R68) | The manager workflow, step 3 | AM9-09: "before creating a uses row, add the PR field (the PR, its scope and the code head) to the skill's printed properties." Step 3: "The uses-table row is the skill's printed row, except that the manager sets *Nathan's pick* to "not recorded" in place of the "pending" the skill prints; that is the one field the manager writes by hand (DM-34 D1.1)." | AM9-09 came later (8 November, from DM-40 section 8) and the managers' rows carry the PR field. Amend step 3 to name both hand-written fields, or drop the PR field; PF02-R68 holds AM9-09's form, marked as in conflict, and the workflow wins until the Dev Manager rules. |
| C2 | AM11-10 against AM11-28 and AM11-29 (PF02-R40, PF02-R41) | None settles it; the manager workflow, step 6, sets the Codex wait for review and correction prompts only | AM11-10: "a consultation goes to Nathan as soon as its commit is pushed. A later Codex finding on the same code goes to the Dev Manager as an addition, without holding the message." AM11-28: "after any push to PR47's head, the manager waits for Codex's pass on it and reads PR47's comments before writing or giving the next prompt or consultation." | PF02 reads them together: a consultation is not held for the pass on its own commit (R41), and the next prompt or consultation after any push waits for that push's pass and a read of the PR's new comments (R40). Confirm this reading, or choose one, and consider moving the result into step 6, since the mechanism recurred four times (AM11-10, AM11-17, AM11-28, AM11-29). |
| C3 | AM3-02 (retired) | The manager workflow, step 3 (DM-01 P8) | AM3-02: "Record a conditional level commitment in the brief's 'Reasoning levels' when it is made." Step 3: "Make no conditional commitments, such as "ultracode if the scorer flags it" (DM-01 P8)", and readings live "in the prompt's header and in the Notion uses table only, not in briefs". | Plainly superseded: retired (PF02, section 5). |
| C4 | AM2-06, AM4-02, AM4-04, AM5-02, AM8-14 (rules kept) | OD-41; OD-34; OD-53, D1; OD-42 | Each entry's prevention carries a part a later direction replaced: Codex's "both reviews" (OD-41); a choice between the manager's call and TypeSafe put to Nathan (OD-34, OD-53 D1); the manager's own scorer requests and their reachability test (OD-34, OD-42); a pick status in the uses table (OD-53 D1); Nathan's pick allowed in a brief (OD-53 D1). | Plainly superseded in part: each rule states the later form, and its "Changed" line names the retired part (PF02, section 5, last paragraph). |

**Log entries that claim a home that does not hold the rule.** Not conflicts with a home, but a reader of the log would be misled:

- AM11-05 says its rule is "now a checklist step"; no governing home states it. PF02-R42 holds it.
- AM11-20 says the workflow's supersession sweep "already names … every record that names a branch's head"; the sweep's text (manager workflow, step 5) names a brief's previous revision number and links to the old home, not branch heads. PF02-R05 holds the branch-head rule.
- AM11-25 says AM11-07's clock rule "extends to Notion writes"; no governing home holds a clock rule. PF02-R01 holds it.
- The manager workflow cites AM5-04 in step 3's session rule ("Say when a session may push again"), while AM5-04's own mechanism was the manager's records pushes; its "Batching records" bullet is conditioned on "While a code PR is under review". PF02-R35 keeps that condition (both entries' pushes were to a code PR under review) and adds that a mistake entry or a stop hook's request waits for the next batch.

## 8. Design choices, for the Dev Manager's read

1. **Grouping.** The prompt's ten suggested groups, adapted: "briefs, proposals and the Dev Manager's reports" added (six rules about reading code and reports before proposing, which fit none of the ten); "branches, pull requests and merges" joined with handovers and next actions, since only one rule (R61) is about branches alone; "records and evidence" named "records, claims and verification", which is what its entries are about. Rule IDs run in group order.
2. **Cited, not held.** A rule a governing home states is cited by section with a one-line gist marked "(cited)" and a check, and is not restated (17 rules). Where a home states the core and an entry adds a check or a case, PF02 holds only the addition and says "PF02, adding to …" (17 rules). This keeps every rule findable by its ID without a second copy of a home's text.
3. **The next-manager start procedure as a cited home.** The prompt lists six governing homes; the start procedure is not one of them, but it already holds AM8-01's rule (step 2) and every manager runs it. PF02-R65 cites it rather than restating it. If the Dev Manager prefers the six alone, R65 becomes PF02-held.
4. **Retired.** AM3-02 (contradicted by step 3, DM-01 P8); AM4-03 (the manager no longer writes scorer requests: OD-34, OD-42); AM3-18 (its own end condition met: P06.1-C3's `fix_reversals.py` reports an edit that does not compile or import, with the test `test_an_edit_that_does_not_compile_or_import_is_reported`, both read at `553d9ed…`). The prompt's examples, Google Drive and the historical App Builder role, have no entries in the log, so nothing was retired for them.
5. **Kept in a rule though partly superseded.** AM2-06, AM4-02, AM4-04, AM5-02 and AM8-14 stay among their rules' sources, because the workflow itself cites AM4-02 and AM5-02 for rules in force, and the other three each carry a part still in force. Each rule's "Changed" line names the superseded part.
6. **Events with no standing rule.** AM5-20 (caught by its own control, no section, no record carried it; the log's rule for such slips) and AM11-13 (a count seen before the prompt was given and given as written by choice; its shared section's prevention answers AM11-14 and AM11-15 only).
7. **AM11-06** has no prevention of its own (a count in a scorer's action text, caught before use). It is a source of PF02-R53, whose rule on figures covers text sent to the scorer.
8. **Rules that generalize a single incident's words.** Where an entry's prevention names one file or tool (PR47, `Stack.Protected`, `# via` lines), the rule keeps the example and states the general case the entry's own words support; it adds no case the entries do not name.
9. **PF02-R42 (a watch before a wait ends)** applies to the manager's own pushes. It does not conflict with the workflow's rule that the manager does not watch a session's run of record (step 5; PF02-R36), and it is not implementation or review work, so `CLAUDE.md`'s rule against the manager starting such work does not reach it.
10. **Not changed, outside M08's paths.** `docs/README.md`'s "Governing rules" row, PF00's "Start here" and "Current session authority", and root `AGENTS.md`'s reading list do not name PF02. PF02's section 2 has a manager read it at its start, and PF02-R64 builds a start prompt's reading list from `AGENTS.md`'s first paragraph and PF00's "Start here", so until one of those names PF02 the route runs only through the start procedure's list. Recommended at integration: add PF02 to the next-manager start procedure's step 3, between the handoff and the mistakes log (the prompt already assigns that pointer to the manager), and consider adding it to PF00's "Start here" or the `AGENTS.md` reading list; section 2 says the pointers come at integration.

**What I was unsure of:**

- Whether the next-manager start procedure should count as a governing home (choice 3).
- Whether AM2-05 (print the UTC time with every scorer request) is moot: the scoring skill prints a send time in the reading it returns (this prompt's header shows "Sent 2026-11-16T01:35:06Z"). It stays a source of PF02-R01, whose clock rule covers any time the manager writes.
- C2's reading.

## 9. Verification findings and dispositions

Four read-only verifiers read PF02 as committed at `bd5bb11` (after the AM3-18 retirement and the renumbering). They returned 26 findings, some overlapping. All 26 were accepted and applied in one commit; the rule IDs below are the final ones.

| # | Verifier | Rule | Finding | Disposition |
|---|---|---|---|---|
| 1 | cited | R19 | The gist widened the home's exemption from consultation and dropped some of its triggers | Accepted: the gist now uses the home's words, including "is fixed before the merge" |
| 2, 20 | cited, completeness | R33 | Marked cited, but AM8-20's alternative (one push for code and records) and its wider trigger are in no home | Accepted: now "PF02, adding to" step 3 and step 5, with both stated |
| 3 | cited | R37 | Marked cited, but "never by which jobs it skipped" is AM8-10's, not the checklist's | Accepted: now "PF02, adding to" step 7 |
| 4 | cited | R34 | The gist's second clause was not in the home; it dropped the report's prompt-commit statement | Accepted: the gist now uses step 6's words; step 5 dropped from the Home |
| 5 | cited | R35 | The cited clause left out the home's condition, "While a code PR is under review" | Accepted: the condition is kept (both sources were pushes to a code PR under review); section 7's note corrected |
| 6 | cited | R18 | The Home gave the Dev Manager a check its charter does not define | Accepted: the manager checks it; the Dev Manager's read may catch a mismatch |
| 7 | cited | R54 | DM-38 was placed as if the home cited it | Accepted: the Home cites DM-01 P8, and attributes the addition to AM9-03 and DM-38 |
| 8 | cited | R51 | "a message" widened the home's "a message to Nathan" | Accepted |
| 9 | cited | R32 | "none added" made universal; the home limits it to a session started while the Stream variables were set | Accepted |
| 10 | cited | section 2 | Nothing routes a manager to PF02 before integration | Accepted in part: section 2 now says the pointers come at integration; the pointers are outside M08's paths (section 8, choice 10) |
| 11 | fidelity-a | R01 | AM2-05's "print the UTC time with every scorer request" was lost | Accepted: stated in the rule |
| 12 | fidelity-a | R04 | "Notion's standing lines" and "a branch count" came from no source of R04 | Accepted: both removed |
| 13 | fidelity-a | R05 | A Notion edit cannot be "in the same commit" | Accepted: the handoff in the commit, Notion in the batch's sync, before the push |
| 14, 26 | fidelity-a, completeness | R23 | AM11-09's "and the reading list" dropped | Accepted |
| 15 | fidelity-b | Section 5 | AM3-02's reason said the manager records no level of its own; step 3 lets it record a call for comparison | Accepted: reason reworded |
| 16, 25 | fidelity-b, completeness | R63 | The initiation assignment swapped for the owner directions with no "Changed" line; "Propose; do not dispatch" restated the start procedure | Accepted: a "Changed" line added, the sentence removed, and the dropped part listed in section 5 |
| 17 | fidelity-b | R53 | Some sources' scoped requirements were applied to every figure | Accepted: reworded to the sources' scopes |
| 18 | completeness | Section 6 | The cancelled-run row included AM10-01, whose cancelled run was not a run of record | Accepted: the row now covers "an earlier push's runs, a run of record among them", with AM11-04 added (6 entries) and R21 and R07 named |
| 19 | completeness | Section 6 | "A logged prevention not run" pointed at "Maintenance", which does not answer it, and missed AM10-17 and AM11-03 | Accepted: it now points to each rule's check (R01, R07, R11, R40), with 8 entries |
| 21 | completeness | R45 | AM9-10's "any question about how to verify a head" and "a written procedure … reported as a conflict" were missing | Accepted: both added, with OD-58 and the start procedure cited |
| 22 | completeness | R50 and section 5 | AM4-04's judgement prevention was listed as retired, though step 3 still states it | Accepted: only its scorer-request part is retired; R50 cites step 3 for the judgement part |
| 23 | completeness | R41 | The rule's lead and check were unconditional, against R40's comment listing | Accepted: the listing is read before a consultation; only the pass on its own commit is not awaited; a "Changed" line added |
| 24 | completeness | R17 | An item not carried went only to the Dev Manager; the charter also sends an item accepted with changes to Nathan | Accepted: added, with the charter's "The relay", step 4, cited |

After the fixes, `coverage.py` and `mech.py` were run again (section 6). The verifiers also confirmed as clean: every named home section exists under the name PF02 gives it; the OD and DM numbers; the remaining "Changed" lines; the retirement of AM3-18 (its `fix_reversals.py` and test); and sections 1, 3 and 8 against PF00 and the charter.

## 10. Classification

CLASSIFICATION

## 11. Deviations and limits

- **Subagents and workflows.** The extraction and verification used read-only subagents in two workflows; the prompt allows any tools. No subagent wrote a file.
- **Suggested groups** were adapted (section 8, choice 1).
- **The prompt's retirement examples** (Google Drive, App Builder) had no entries to retire.
- **Times** in this record are UTC, from tool output. The start gate's time is not recorded: the clock was not read then (PF02-R01).
- **Not done, by design:** no change to the mistakes log, the manager workflow, `AGENTS.md`, `CLAUDE.md`, the start procedures, the charter, the CI policy, the register, any brief or Notion; no pull request, comment or other GitHub write.
- **Limit:** the check of each rule against the governing homes was made at `553d9ed…`. A governing change on the manager branch after that commit is not reflected.

Status: draft (verification findings, coverage output and classification pending)
