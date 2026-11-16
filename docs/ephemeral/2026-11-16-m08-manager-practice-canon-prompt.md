# M08 prompt — the manager practice canon: GAPP-PF02, from the managers' mistakes log

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 16 November 2026.**
- **Why:** Nathan, 16 November 2026 (OD-66): *"I want to create a new session to turn the mistake logs into some sort of canonical (PFxx) docs. Create a scored prompt for a new session to do that work."*
- **Durable brief:** none. This prompt is the specification. The session's evidence record holds what it decided, and the manager promotes anything else worth keeping before the prompt is pruned.
- **Where the result goes:**
  - the session's branch: a new canon document, `docs/pf-canon/GAPP-PF02-Manager-Practice-Rules.md`; GAPP-PF00's registry, authority map and revision history; one row of `docs/README.md`; and its record, `docs/testing/evidence/2026-11-16-m08-manager-practice-canon.md`;
  - then Dev Manager 5's read of PF00 and PF02 at the session's commit (governing Markdown; `docs/planning/dev-manager.md`), with the design choices the record lists;
  - then the manager integrates it, after SV3 Stage B's PR (PR47) merges, in its own pull request, adding pointers to PF02 from the manager workflow, the next-manager start procedure and the mistakes log.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.19 (confidence 0.76); rung probabilities low 0.00, medium 0.09, high 0.65, extra high 0.25, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.77, Sonnet 5.5 0.22, Haiku 5.5 0.00 (confidence 0.69). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.007, Fable 5.1 at extra high 0.003, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.069, Opus 5.5 at high 0.501, Opus 5.5 at extra high 0.193, Opus 5.5 at max 0.008, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.020, Sonnet 5.5 at high 0.143, Sonnet 5.5 at extra high 0.055, Sonnet 5.5 at max 0.002, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-16T01:35:06Z. Nathan picks the cell.
- **The Dev Manager's read:** after the session, before integration, as above. This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **Running beside SV3:** this session writes no path SV3's work writes. Running it while SV3 Stage B's review is open is two sessions at once and a second work item, which OD-29 and the one-item rule (Nathan, 24 September 2026) do not allow without Nathan's direction. Whether it runs now is Nathan's choice, recorded with OD-66.
- **Deletion condition:** prune after M08's pull request merges and its receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **documentation session for M08, the manager practice canon**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What M08 is.**
- **The source:** since 25 September 2026 every manager has logged its own mistakes in `docs/continuity/manager-mistakes.md` (OD-11). Each entry has a table row (ID, date, kind, what happened, found by) and, for most, a section with "What happened", "Caught by", "Effect", "Correction" and **"Prevention"**. At `<START_SHA>` the log runs from AM2-01 to AM11-29, about 167 entries in some 218 KB.
- **The problem:** the prevention rules are scattered through that dated history. Some were later promoted into the manager workflow, some tightened by later entries, some made moot by later directions. A new manager must read the whole log to learn them.
- **The task:** distil the log into one canonical document of standing rules, **GAPP-PF02, "Manager Practice Rules"**. Each rule is stated once, traced to the entries that set it, and either holds the rule or points to the home that already holds it.
- **What stays:** the log stays as the dated record of what happened. It is evidence, not authority, and the manager keeps writing to it.

**Why one document, and why in the canon.**
- GAPP-PF00 says additional GAPP-PF documents are created "only when a specific concept requires its own canonical home". The managers' standing practice rules are such a concept. Today they have no single home: the log holds them as history, and the governing documents hold only some.
- PF00 also says: "Never create a second editable authority by copying a document." So PF02 must not restate a rule that `AGENTS.md`, `CLAUDE.md`, the manager workflow, the Dev Manager charter, the CI policy or an owner direction already states. It cites that home by section instead.
- Everything in `docs/pf-canon/` is governing Markdown. It skips code review as ordinary documentation, but the Dev Manager reads it at a named commit before its pull request merges.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - **write only these paths:**
    - `docs/pf-canon/GAPP-PF02-Manager-Practice-Rules.md` (new);
    - `docs/pf-canon/GAPP-PF00-Canon-Index-and-Authority.md`: its canon registry (one row), its authority map (one row), its header's revision and date, and its revision history (one entry, 1.12), and nothing else;
    - `docs/README.md`: the `docs/pf-canon/` row of its location table and the "Managers' mistakes" row of "One home per fact" (or one new row beside it), and nothing else;
    - `docs/testing/evidence/2026-11-16-m08-manager-practice-canon.md` (new): your record.

    Nothing else changes in M08. In particular, change nothing in the mistakes log, the manager workflow, `AGENTS.md`, `CLAUDE.md`, the next-manager start procedure, the Dev Manager charter, the CI policy, the owner-direction register, any brief, or Notion. The manager adds the pointers to PF02 at integration, after the Dev Manager's read.
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting.
- **All of it is Markdown.** Write no script, code or configuration into the repository. Scripts you use to check coverage run from a scratch directory outside the checkout, and their output goes in your record.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - the work needs a change outside the paths above;
  - the log cannot be read whole at `<START_SHA>`;
  - your branch's diff does not classify as ordinary documentation (section 3, step 7).

  A prevention that contradicts a governing home is **not** a stop. List it in the record and the report as a conflict for the Dev Manager, and do not resolve it by changing that home.
- **Never:** dump the environment, or print a credential, token or key; read, print or use the value of any `AWS_*` variable; call any provider or HDE; connect to any database, HDE, Railway or other external service.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **AWS and GitHub token names** may be present. Record which `AWS_*` names are present, by name only; never read or use their values, or the token values.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"   # must print the line
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- docs/pf-canon docs/README.md   # must print nothing
ls docs/pf-canon/                                   # must list PF00 and PF01 only
grep -c -F '**Revision:** 1.11' docs/pf-canon/GAPP-PF00-Canon-Index-and-Authority.md   # must print 1
grep -o -E '^\| AM[0-9]+-[0-9]+ ' docs/continuity/manager-mistakes.md | wc -l   # the entry count; record it
grep -o -E '^\| AM[0-9]+-[0-9]+ ' docs/continuity/manager-mistakes.md | tail -1  # the last entry at <START_SHA>; record it
```

If a check fails, stop and report. The prompt is stale if `<START_SHA>` is not on the live manager branch, or the live branch has changed PF00, PF01's folder or `docs/README.md` since it.

**The log after `<START_SHA>`.** The manager may add entries to the live branch while you work. Work from the log as it stands at `<START_SHA>`, and name its last entry in PF02's header. Entries added later are the manager's to fold in at integration, under PF02's maintenance rule.

**Then read, completely, at `<START_SHA>`:**
- root `AGENTS.md` and `CLAUDE.md`; `docs/README.md`;
- `docs/pf-canon/GAPP-PF00-Canon-Index-and-Authority.md`, whole, and `GAPP-PF01-A-to-Z-Implementation-Plan.md`'s D08 to D10;
- `docs/planning/manager-workflow.md`, whole;
- `docs/planning/dev-manager.md`, whole;
- `docs/operations/ci-and-branch-policy.md`, whole;
- `docs/planning/start-prompts/next-manager.md`, whole;
- `docs/continuity/owner-directions.md`, whole;
- `docs/continuity/manager-mistakes.md`, **whole**: every table row and every section. It is long; read it in parts, and record that you read all of it.

## 3. What to do

1. **Extract.** For every entry at `<START_SHA>`, from its table row and its section, take its ID, date, kind, mechanism (what went wrong, in a few words) and its prevention. Where an entry has no section, take the prevention from its row or from a later entry that names it.
2. **Group and merge.**
   - Group the preventions by what they guard. Suggested groups; use, merge or split them as the entries warrant:
     - times and clocks;
     - standing lines, revision numbers and supersession sweeps;
     - Notion syncs and read-backs;
     - prompts: start gates, owned paths, stop clauses, the earlier tests a stage changes, and sweeps before a prompt;
     - runs, pushes and the push rule;
     - Codex and the waits before a prompt;
     - messages to Nathan;
     - records and evidence;
     - branches, pull requests and merges;
     - TypeSafe readings.
   - Where several entries set the same or overlapping preventions, write **one rule** with all their IDs as sources.
   - Where a later entry tightened or replaced an earlier rule, state the later form, list both sources, and say what changed.
3. **Check each rule against the governing homes.**
   - For each rule, search `AGENTS.md`, `CLAUDE.md`, the manager workflow, the Dev Manager charter, the CI policy and the owner-direction register.
   - **Already stated there:** PF02 gives the rule's one-line gist and cites that home by section and, where one applies, its OD. It does not restate the rule's text.
   - **Stated nowhere else:** PF02 holds it.
   - **Contradicted by a governing home, or by a later owner direction:** list it as a conflict in the record. If the rule is plainly superseded, retire it (step 5); otherwise leave it for the Dev Manager.
4. **Write each rule** with:
   - a stable ID, `PF02-R01` onward, in group order;
   - the rule, in one or two imperative sentences, specific enough to check;
   - **the check:** what shows it was followed (a command, a field, a read-back);
   - **sources:** the entry IDs;
   - **home:** "PF02", or the governing section it points to.
5. **Retire what no longer applies.** List preventions that a later direction or process change has made moot (for example, those about Google Drive or the historical App Builder role), each with its entry IDs, the reason and the superseding source. Nothing is deleted silently.
6. **Coverage.** Every entry ID at `<START_SHA>` must appear in exactly one of three places:
   - in at least one rule's sources;
   - in the retired list;
   - in a short list of **events with no standing rule** (a one-off with nothing to prevent, or a prevention another entry already covers), each with its reason.

   Check this with a script run from scratch, outside the checkout. Put its output in your record: the counts, and every ID in each place.
7. **Classify your diff** as root `AGENTS.md` requires, with the trusted base policy outside the checkout:

   ```bash
   base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)   # the trusted policy comes from main
   policy_dir=$(mktemp -d)
   git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
   python3 -I "$policy_dir/change_scope.py" --base <START_SHA> --head "$head" --merge-base   # the base is this prompt's commit, so only your change is classified
   ```

   Expected: `"full": false`, `ordinary-docs-only`. Anything else is a stop. No application CI runs for this change.

## 4. What PF02 holds

Write `docs/pf-canon/GAPP-PF02-Manager-Practice-Rules.md` in the canon's style (PF00's header form and plain, dated statements):

1. **Header:** `**Identity:** GAPP-PF02 · **Revision:** 1.0 · **Recorded:** <date>`, and a scope line: the managers' practice in this application's manual relay; it does not govern the Glow HD engine or its canon. Also the source: the mistakes log at `<START_SHA>`, from AM2-01 to its last entry, with the entry count.
2. **Purpose and authority:**
   - PF02 is the canonical home of the managers' standing practice rules that the mistakes log's preventions set;
   - the log stays the dated record of what happened (OD-11), evidence and not authority;
   - a rule another governing home already states is cited there, not restated;
   - where PF02 and a governing home differ, the governing home wins until the Dev Manager rules and the difference is corrected.
3. **How to use it:** a manager reads PF02 at its start, after the handoff and before the log; a prompt or message may cite a rule by its ID.
4. **The rules,** by group, as section 3 describes.
5. **Retired rules,** with reasons.
6. **Recurring mechanisms:** a short index of the mechanisms that recur across entries (for example, a time written before the clock was read; an edit that replaced a list but left the sentence after it; a sweep that searched the repository and not Notion), each with its count and the rules that answer it.
7. **Events with no standing rule,** with reasons.
8. **Maintenance:**
   - each new log entry names the PF02 rule it broke, or proposes a new or changed rule;
   - the manager applies the change to PF02 with the next records batch;
   - a PF02 change is governing Markdown, read by the Dev Manager before its pull request merges;
   - PF02's revision history records each change.
9. **Revision history:** 1.0 — established from the mistakes log at `<START_SHA>` (M08; OD-66).

Write plainly: one rule, one idea; no rule that only restates a principle without a check.

## 5. PF00 and the documentation map

- **PF00:**
  - the canon registry gains GAPP-PF02, "Manager Practice Rules", its home, and its state: "Established on merge; read by the Dev Manager";
  - the authority map gains a row: the managers' standing practice rules belong to GAPP-PF02, and the dated record of mistakes to the mistakes log;
  - the header's revision becomes 1.12, with the date;
  - the revision history gains 1.12: GAPP-PF02 created for the managers' practice rules (M08; OD-66), as a specific concept needing its own canonical home; no other change to authority.
- **`docs/README.md`:**
  - the `docs/pf-canon/` row names GAPP-PF02;
  - "One home per fact" gives the managers' practice rules their home in PF02, beside the mistakes log's row.

## 6. The record

Write `docs/testing/evidence/2026-11-16-m08-manager-practice-canon.md`:
- the start gate's results, the environment check (names only), `<START_SHA>`, the entry count and the log's last entry;
- that you read every part of the log, and how (the parts, by line range);
- the counts: entries, rules, groups, retired, events with no standing rule; and the coverage script's output;
- **each conflict** between a prevention and a governing home or an owner direction: the entry, the home, the two texts, and your recommendation, for the Dev Manager;
- **the design choices** for the Dev Manager's read: the grouping; where you cited rather than held a rule; what you retired and why; anything you were unsure of;
- the classification's output;
- every deviation from this prompt, and what you could not do.

Commit each logical step with a clear message ending in the session's attribution lines. Push your branch when done. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only the four paths in "How you work".

## 7. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch and its head;
- the start gate's and the environment check's results;
- the counts: entries read, rules, groups, retired, events with no standing rule; and whether coverage is complete;
- the conflicts found, each in one line;
- the design choices for the Dev Manager, each in one line;
- the classification's result;
- anything that met the stop rule, every deviation, and what you could not do.
