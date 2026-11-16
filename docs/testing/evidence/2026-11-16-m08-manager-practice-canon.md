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
- **By home:** 19 rules are cited only (a governing home states them; PF02 gives the gist and the section); 15 cite a home for the core and hold an addition ("PF02, adding to …" and similar); 34 are held by PF02 alone.
- **Retired:** 3 entries (AM3-02, AM3-18, AM4-03), and five parts of entries that keep a rule, each named in its rule's "Changed" line.
- **Events with no standing rule:** 2 (AM5-20, AM11-13).
- **Recurring mechanisms:** 17 rows.

## 6. Coverage

Every entry ID at `553d9ed…` must appear in exactly one of: at least one rule's sources; the retired list; the events with no standing rule. `coverage.py` parses PF02 itself (each rule's "Sources" line, the retired table, the no-rule table) and compares the IDs with the log's rows. Its output on the final PF02:

```
COVERAGE_OUTPUT
```

`mech.py` checks that each recurring-mechanism row's count equals the entries it lists, without duplicates, and that every rule it names exists:

```
MECH_OUTPUT
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
- The manager workflow cites AM5-04 in step 3's session rule ("Say when a session may push again"), while AM5-04's own mechanism was the manager's records pushes; its "Batching records" bullet is conditioned on "While a code PR is under review". PF02-R35 states the manager's rule without that condition, from AM5-04 and AM9-02.

## 8. Design choices, for the Dev Manager's read

1. **Grouping.** The prompt's ten suggested groups, adapted: "briefs, proposals and the Dev Manager's reports" added (six rules about reading code and reports before proposing, which fit none of the ten); "branches, pull requests and merges" joined with handovers and next actions, since only one rule (R61) is about branches alone; "records and evidence" named "records, claims and verification", which is what its entries are about. Rule IDs run in group order.
2. **Cited, not held.** A rule a governing home states is cited by section with a one-line gist marked "(cited)" and a check, and is not restated (19 rules). Where a home states the core and an entry adds a check or a case, PF02 holds only the addition and says "PF02, adding to …" (15 rules). This keeps every rule findable by its ID without a second copy of a home's text.
3. **The next-manager start procedure as a cited home.** The prompt lists six governing homes; the start procedure is not one of them, but it already holds AM8-01's rule (step 2) and every manager runs it. PF02-R65 cites it rather than restating it. If the Dev Manager prefers the six alone, R65 becomes PF02-held.
4. **Retired.** AM3-02 (contradicted by step 3, DM-01 P8); AM4-03 (the manager no longer writes scorer requests: OD-34, OD-42); AM3-18 (its own end condition met: P06.1-C3's `fix_reversals.py` reports an edit that does not compile or import, with the test `test_an_edit_that_does_not_compile_or_import_is_reported`, both read at `553d9ed…`). The prompt's examples, Google Drive and the historical App Builder role, have no entries in the log, so nothing was retired for them.
5. **Kept in a rule though partly superseded.** AM2-06, AM4-02, AM4-04, AM5-02 and AM8-14 stay among their rules' sources, because the workflow itself cites AM4-02 and AM5-02 for rules in force, and the other three each carry a part still in force. Each rule's "Changed" line names the superseded part.
6. **Events with no standing rule.** AM5-20 (caught by its own control, no section, no record carried it; the log's rule for such slips) and AM11-13 (a count seen before the prompt was given and given as written by choice; its shared section's prevention answers AM11-14 and AM11-15 only).
7. **AM11-06** has no prevention of its own (a count in a scorer's action text, caught before use). It is a source of PF02-R53, whose rule on figures covers text sent to the scorer.
8. **Rules that generalize a single incident's words.** Where an entry's prevention names one file or tool (PR47, `Stack.Protected`, `# via` lines), the rule keeps the example and states the general case the entry's own words support; it adds no case the entries do not name.
9. **PF02-R42 (a watch before a wait ends)** applies to the manager's own pushes. It does not conflict with the workflow's rule that the manager does not watch a session's run of record (step 5; PF02-R36), and it is not implementation or review work, so `CLAUDE.md`'s rule against the manager starting such work does not reach it.
10. **Not changed, outside M08's paths.** `docs/README.md`'s "Governing rules" row and PF00's "Current session authority" paragraph do not name PF02; the manager may add it at integration, with the pointers from the manager workflow, the next-manager start procedure and the mistakes log that the prompt assigns to integration.

**What I was unsure of:**

- Whether the next-manager start procedure should count as a governing home (choice 3).
- Whether AM2-05 (print the UTC time with every scorer request) is moot: the scoring skill prints a send time in the reading it returns (this prompt's header shows "Sent 2026-11-16T01:35:06Z"). It stays a source of PF02-R01, whose clock rule covers any time the manager writes.
- C2's reading.

## 9. Verification findings and dispositions

VERIFICATION

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
