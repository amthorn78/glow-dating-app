# SV3 Stage A, correction C3: delta re-review prompt

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 13 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 9, "Stage A, correction C3" and its paragraph "C3's review" (DM-67's GD1).
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta re-review of C3", with a disposition for each finding (fix before the merge, or carry), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.25 (confidence 0.81); rung probabilities low 0.00, medium 0.02, high 0.72, extra high 0.25, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.02, Opus 5.5 0.98, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.97). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.014, Fable 5.1 at extra high 0.005, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.020, Opus 5.5 at high 0.706, Opus 5.5 at extra high 0.245, Opus 5.5 at max 0.010, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-13T07:53:59Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 5's pre-merge read follows it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR45's head, which is this prompt's commit (manager workflow, step 6).
- **Deletion condition:** prune after SV3 Stage A's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **delta code and security re-review of correction C3 to SV3's Stage A** (eligibility and discovery) for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one correction's changes against the head the previous re-review read, with two checks read as security boundaries. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **C2's delta re-review** read code head `303fdcc` (the evidence record, "Delta re-review of C2"): changes required, narrowly. No blocking finding and no app change, but two of C2's guards could pass while what they guard is wrong:
  - **L1, L2:** the lock scan (`account_lock_scan.py`) passed a generic lock with a join and `of=`, and did not see several join forms;
  - **S1, S2:** `pages.one_snapshot_statements` accepted any account-table read with the viewer's ID before the probe point, and checked a cursor page's writes in its transaction only.

  Also **R1:** the README stated T3's rule too narrowly; and **N2:** T5's list left out two case-level texts. Codex found L1, L2's `Q` variable, S1 and S2 too, on PR45 (`3000014`).
- **The Dev Manager disposed of them** (DM-67, GD1 to GD14, in `docs/continuity/dev-manager/reviews/`). It approved each fix, made L2's and S1's rules exact (GD1, now the brief's "Stage A, correction C3"), and gave the record texts (GD3 to GD10). N1 and N3 are carried to Stage B.
- **C3** (branch `claude/glow-discovery-c3-ir9mnd`) built them: code head `72ace21`, records `8189b31` (the evidence record, "Stage A, correction C3").
- **Its run of record** is Foundation run 43369448338 on `72ace21` (push). All eight jobs passed, and the gate printed `Application checks passed`. Every suite passed (ordering 56/56, 115/115 and 62/62; identity 49/49; profile 69/69; discovery 40/40), and every scan was clean.
- **The manager verified C3** (the evidence record, "Manager verification of C3"): the diff within C3's owned paths, the given words, the run of record, the offline tests, its L1 and L2 probes now refused, and two reversals of its own. It integrated C3 by the merge `f9a8621`.
- **The session's observation, not changed:** the scan does not read `dates()`, `datetimes()`, `complex_filter()` or `in_bulk(field_name=)` as path or lookup methods, and its SQL rule accepts a view's name after `FROM`. None occurs in a locked queryset today. GD7's limits do not name them.
- **Dev Manager 5** has succeeded Dev Manager 4 (OD-65); its pre-merge read comes after this review.

**The code head under review is `72ace21`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `72ace21` (the start gate checks this). The baseline is `303fdcc`, which C2's delta re-review read.

**Your scope:**
- **The code:** `git diff 303fdcca30788bf88a65f65e50d532971ab435a4 72ace2179a7dff74fecf6b7f06de30b7a1454dcb`, its three non-Markdown paths, each read in full at `72ace21`:
  - `proofs/postgres-ordering/glow_ordering_proof/account_lock_scan.py`: its docstring, `read_models` and the reverse names, the argument, method and variable rules, the generic branch, and the SQL rule;
  - `proofs/postgres-ordering/glow_ordering_proof/discovery_cases.py`: `listed`, `OWN_ACCOUNT_READ`, `_Statements`' phases and `pages.one_snapshot_statements`;
  - `proofs/postgres-ordering/tests/test_discovery_offline.py`: the lock scan's and the pre-probe list's tests.
- **The records, as claims about the code:**
  - the evidence record's "Stage A, correction C3" and "Manager verification of C3", and GD8's and GD9's lines;
  - the proof README's SV3 paragraph and heading, the lock scan's row in the file table, T3's rule and limit, and the lock scan's "Limits" entry (GD3 to GD7);
  - the P11 plan's SV3 entry's runs-of-record sentence (GD10).
- **The runs:** 43369448338, the run of record; and PR45's pull-request run on this prompt's commit or its parent, if one has finished.
- **Out of scope:**
  - code C3 does not change. Stage A, C1 and C2 were read at `b44e6f7` and `303fdcc`; report a finding there only where C3's change reaches it;
  - Stage B, OD-64's limits, and the items carried to later phases (N1 and N3 among them).

**The focus** (the brief's "C3's review"):
1. **L1, as a security boundary:** a generic lock with a join passes only with `no_key=True`. Plant the review's helper, `model.objects.select_related("account").select_for_update(of=("self",))`, and see it refused; with `no_key=True`, see it pass.
2. **L2, as a security boundary:**
   - **Each rule** of the brief's item 2: the arguments (a keyword's value judged only when it is, or names, a `Q` or an `F`), the methods (`latest`, `earliest`, `extra()`), the variables (every plain assignment, before and after the lock, transitively), the reverse relations (the names read from `models.py`), and the SQL rule (only complete literal text naming its tables passes a `FOR UPDATE`). Plant each of the brief's forms and see each refused.
   - **The session's stricter readings** (its section's deviations): a positional `Q(…) | Q(…)` as a join; a `Q` or `F` anywhere inside a keyword's value; a conditional assignment followed; an `of=` entry ending in the reverse name refused; a related name that is not a literal failing closed. Is each within the brief's rule, and does any refuse what the rule passes?
   - **What stays unseen:** do the docstring, the README and the record state exactly what the scan cannot see (GD7)? Judge the session's observation (`dates()`, `datetimes()`, `complex_filter()`, `in_bulk(field_name=)`, a view's name after `FROM`): for each, a gap to fix in this item, or a limit to state, and the words.
   - **The tree:** the scan still reads 52 `select_for_update` calls, none locking a queryset that joins, and the seven explicit account locks; no existing lock is refused.
3. **S1, as a security boundary:**
   - **The list:** `predicates.VIEWER` with the viewer's ID as its `viewer` parameter, and `OWN_ACCOUNT_READ`'s shape with the viewer's ID as its only parameter. The session allowed column aliases in that shape (`AS "eligibility_version"`), since the versions read uses them. Can any statement that reads another row, or another table, pass the shape?
   - **The phases:** the check reads the phase before the transaction and the transaction.
   - **The pages:** the statements each page makes before the probe point are those the record lists (2, 3 and 2), and each is on the list.
   - **The matcher's tests:** each failing form (another ID, an `IN` list, a join, a subquery, `VIEWER` for another member) fails for the reason the rule gives.
4. **S2:** the write check reads every phase the probe records for a page by cursor, and the case requires the photo reads to be recorded after the commit. Could a write escape it?
5. **The records:** GD3 to GD10 as applied; the README's sentence on C3; and every claim in the record's C3 sections holds against the code and the run.
6. **Nothing else changed:** from the diff, no path outside C3's owned paths, and no app code, workflow, contract, model, migration, lock file or dependency.

**Re-run, at least,** in a scratch copy of `72ace21`:
- **The checks:** the proof's offline tests, `ruff`, `ruff format --check` and `mypy`; the lock scan over the tree, with its counts.
- **Offline reversals, at least five:**
  - L1's generic branch accepting `of=` again, against its test;
  - two of L2's rules undone (for example `latest` removed from the path methods, and the variables rule cut to one hop), against their tests;
  - `listed` accepting `VIEWER` for any member, against the matcher's tests;
  - one of your own choosing, against a claim you doubt.
- **The discovery suite, informational:** on a throwaway PostgreSQL under P06.DB's D4, if Docker allows. If you can run it, run the database reversals the record names: D (a pre-probe read of other members' accounts), `VIEWER` run for another member, and E (a write after the cursor page's transaction), each failing the case; and any you doubt.

**What comes after this review: the correction classes.** Report every finding with its severity. A correction takes every blocking finding, and any should-fix finding that could do any of these:
- let the lock scan miss a lock that takes an account row `FOR UPDATE`, beyond a limit the README states;
- let a statement that reads another member's row, or a write, pass `pages.one_snapshot_statements`;
- let a test pass where it should fail, or fail where the code is right;
- change app behaviour, a lock, a predicate, the selection, the recheck or a writer;
- leave a Dev Manager condition unmet (DM-67 GD1 to GD10);
- make a record claim more than the code, the tests or the runs show.

Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:**
  - PyPI, for hash-locked installs in a scratch copy;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`);
  - GitHub, through your tools, to read runs.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from that image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.
- **Never:**
  - dump the environment, or print a credential, password, token, session key or key;
  - read, print or use the value of any `AWS_*` variable (section 1);
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE` (DM-57 and DM-58). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values. If any other `AWS_*` name is present, stop and report.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Docker if present. Record their versions.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 3240ef0acca7983e5b60b9a111be371ed5a16b74
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 72ace2179a7dff74fecf6b7f06de30b7a1454dcb HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "the code head under review"
git diff --quiet 72ace2179a7dff74fecf6b7f06de30b7a1454dcb origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs ':!*.md' && echo "no code on the live branch after 72ace21"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Delta re-review of C3'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `72ace21`;
- this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:**
- root `AGENTS.md` and `CLAUDE.md`; `proofs/postgres-ordering/README.md`;
- the brief, revision 9: D2, D14, the owned paths, "Stage A, correction C2" (its items 1 and 3) and "Stage A, correction C3";
- DM-67's report, whole, above all sections 3.3 to 3.10;
- the evidence record's "Delta re-review of C2", "Stage A, correction C3" and "Manager verification of C3";
- every file in the code diff, whole; and, for the pre-probe list, read only: `glow_discovery/pages.py` (`create`, `continue_page`, `_with_photos`), `glow_profiles/tx.py` (`run`, `lock_account`, `read_account_shared`), `glow_profiles/media.py` (`delivery_reference`, `_owner`), `glow_discovery/predicates.py` (`VIEWER`) and `glow_persistence/models.py`.

**The run,** with your GitHub tools: 43369448338, every job's conclusion, the gate's line, and the Database proof checks job's suite lines.

## 3. What to do

1. Review the code delta against the focus, item by item, with focus 1 to 3 as security boundaries: for each, what the rule stops, what it cannot see, and the test that proves it.
2. In a scratch copy of `72ace21`:
   - re-run the checks and the offline reversals above, and any you doubt;
   - run the discovery suite locally under D4 if you can, informational, with the database reversals.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required;
- the findings, in a table: number, severity, correction class or not, file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 6), a few lines each, with a disposition and words for each form in the session's observation;
- the reversals you re-ran, with their results, the local database ones named informational;
- what you ran, and what you could not run or read.
