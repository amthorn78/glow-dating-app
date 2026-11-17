# SV3 Stage B, correction B-C5 prompt — B-C4's delta re-review: two limits under D14's freeze, the relations check's words narrowed, the record's `%()s` sentence (records only)

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 16 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 20, with its section "Stage B, correction B-C5 (B-C4's delta re-review; DM-79)".
- **Where the result goes:**
  - the session's changes in B-C5's owned paths, and its record, a new section `## Stage B, correction B-C5` at the end of `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at medium.** Effort score 1.13 (confidence 0.87); rung probabilities low 0.03, medium 0.82, high 0.14, extra high 0.01, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.95, Sonnet 5.5 0.04, Haiku 5.5 0.01 (confidence 0.93). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.028, Opus 5.5 at medium 0.779, Opus 5.5 at high 0.133, Opus 5.5 at extra high 0.009, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.001, Sonnet 5.5 at medium 0.033, Sonnet 5.5 at high 0.006, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.008, Haiku 5.5 at high 0.001, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-16T21:07:37Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs.
  - The brief's revision 20 applies DM-79's KK14 to KK16 as written, and the record holds KK12. DM-79 sets this prompt's place in the sequence (its sections 9 and 12) and needs no further read if its words are applied as written.
  - This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order:
  - the manager's verification, and PR47's run and Codex's review of its head;
  - a short bounded delta re-review of B-C5 against `07d8de3`, under class 5 and class 1 (DM-79 section 8);
  - Dev Manager 5's pre-merge read;
  - the merge.
- **Deletion condition:** prune after Stage B's PR (PR47) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are the **implementation session for SV3 Stage B's correction B-C5**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What B-C5 is.** A records correction after the bounded delta re-review of correction B-C4's code head `07d8de3`, the last review of D14 under all five classes. It changes no rule: D14's rules are frozen from `07d8de3` (DM-78). The review found:
- one class 5 finding that is record-only (F3, the record's sentence on `%()s`);
- two forms D14 does not see, recorded as limits under the freeze:
  - **F1:** an item after a `set` or `values` that the reading takes as the end of the `FROM` list;
  - **F2:** a placeholder followed by a string constant.

DM-79 gave the words. B-C5 applies them:
- to the proof README;
- to three docstrings in `row_locks.py`;
- to the record and the P11 plan.

B-C5 changes no code, test, model, migration, lock, version check, DTO, `glow_chat` writer, ledger, lock-scan rule or bound, contract package, workflow or dependency, and no line in `services/api`. In `row_locks.py` it changes three docstrings only: the module's, `judge`'s and `_relations`'s. Set the docstrings aside and the file is identical to `07d8de3`'s by AST. There is no provider, deployed URL, real member, HDE call or stored credential, and no local database run.

**The brief, `docs/planning/sv3-eligibility-discovery-interactions.md`, revision 20, is the specification:**
- its section "Stage B, correction B-C5", items 1 to 4, its stop rule, its run of record and "B-C5's review";
- D14's rule (KK14);
- B-C5's owned paths, "Correction B-C5 only" (KK16).

Its text is Dev Manager 5's words (DM-79). Follow them exactly. Where this prompt summarizes the brief, the brief wins.

**DM-79's given words that B-C5 applies.** DM-79's report (`docs/continuity/dev-manager/reviews/2026-11-16-dm-79-sv3-b-c4-delta-review-dispositions.md`) gives each exact old and new text, as a pair of quoted code blocks, in its section 11:
- **B-C5's twelve** (its section 12, "Who applies what"):
  - KK1 to KK5, the proof README;
  - KK6 to KK9, `row_locks.py`'s docstrings;
  - KK10 and KK11, the record;
  - KK13, the P11 plan.

  Each text is the content of its code block, without the `> ` quote markers.
- **Apply each as written, in that order.** Before the change, its old passage must be found exactly once; after it, its new text exactly once. The manager applied the twelve in that order to a scratch copy at `<START_SHA>`, and each held, as "Facts" below says.
- **Stop if a pair cannot be applied.** If an old passage is not found exactly once, report it; do not reword it.
- **Leave the manager's pairs alone.** KK12 (the record's "Manager verification of B-C4") and KK14 to KK16 (the brief) are already applied.
- **KK2's new text holds B-C5's own sentence** for the README's SV3 paragraph; write no other.

**What came before.**
- **SV3's Stage A** (PR45, `8d83474`) and **B0** (PR46, `947576d`) are merged.
- **Stage B and B-C1 to B-C4** are built, verified and integrated in PR47: code head `07d8de3`.
- **B-C4's run of record,** 43919688476, passed all eight jobs:
  - discovery 66/66 in a 175 s phase;
  - each suite's D14 record `PASS`, none refused, own objects 0, 0, 0;
  - account-table writer locks 44,841 (ordering), 127 (identity), 2,061 (profile) and 4,256 (discovery), all `FOR NO KEY UPDATE`.
- **B-C4's bounded delta re-review:** changes required by one class 5 finding that is record-only; no class 1, 3 or 4 finding. The evidence record's "Delta re-review of B-C4" holds its findings and planted examples.
- **DM-79** ruled on each finding and gave B-C5's words, section and owned paths. The brief is now at revision 20.

**Facts from the code** (the manager's reading at `<START_SHA>`, whose non-Markdown tree equals `07d8de3`'s):
- **Where the old passages are** (line numbers at `<START_SHA>`):
  - the proof README: KK1 and KK2 at line 19, KK3 at line 240, KK4 and KK5 at line 241;
  - `proofs/postgres-ordering/glow_ordering_proof/row_locks.py`: KK6 at line 70 (the module docstring's rule paragraph), KK7 at line 119 (its S4 clause), KK8 at line 641 (`judge`'s docstring) and KK9 at line 753 (`_relations`'s docstring);
  - the record: KK10 at line 2455, KK11 at line 2632;
  - `docs/testing/p11-deferred-acceptance.md`: KK13 at line 85.
- **The manager's scratch application** at `<START_SHA>` (Python 3.12 and the proof's hash-locked Ruff), with the twelve applied in order:
  - each old passage was found once before and each new text once after;
  - `row_locks.py` parses, and is identical to the start's by AST with docstrings set aside;
  - `ruff check` and `ruff format --check` pass on it.
- **No test reads these docstrings or Markdown files.** The manager's sweep found no `__doc__`, `getdoc` or `getsource` read of `row_locks.py`, and no test that opens the README, the record or the P11 plan.
- **The case count stays 66.** B-C5 adds no case and no test.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - **write only B-C5's owned paths** (the brief's "Correction B-C5 only", KK16):
    - in the proof: `row_locks.py`'s module docstring, `judge`'s docstring and `_relations`'s docstring, and nothing else in it;
    - the proof README's D14 entry, SV3 paragraph and "Limits";
    - the P11 plan's SV3 entry: B-C4's clause and its runs of record only;
    - the evidence record.

    Nothing else changes in B-C5.
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (the brief's "The stop rule (B-C5)"). Stop and report, with no further change, if any of these holds:
  - B-C5 needs a change outside its owned paths;
  - it needs a change to `row_locks.py` other than its three docstrings, or the file is not identical to `07d8de3`'s by AST with docstrings set aside;
  - it needs a text other than as DM-79 gives it, or one of the twelve pairs cannot be applied as written;
  - a local check fails, or the run of record differs from B-C4's in a case count, a D14 line, an own-objects count or an account-table lock count.

  Report it; do not narrow or reword a text to pass it.
- **The push rule** (AM5-04). After you push your code commit, push nothing more to your branch until that commit's Foundation run has finished; a newer push cancels the earlier run's application jobs. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.
- **Network:** PyPI only, for `pip install --require-hashes` from the proof's existing lock. No Docker, and no local database run: B-C5's code does not change (DM-79 section 12). A page you cannot reach is named as unread, never filled from memory.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, code, token, session key or signing key, in any form;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database, or start Docker;
  - run `migrate` or `makemigrations`, `playwright install`, `eas`, a native build or a package install script;
  - connect to HDE, Railway or any other external service;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE`. `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`. Record `python3.12 --version`.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"   # must print the line
git diff --quiet 07d8de3dc820e51623cb8529cac124054c0b8b2b HEAD -- . ':!*.md' && echo "B-C4's code"   # must print the line: the start's non-Markdown tree equals 07d8de3's
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering 'docs/testing/evidence/*sv3*' docs/testing/p11-deferred-acceptance.md   # must print nothing
grep -c -F 'Status: brief, revision 20,' docs/planning/sv3-eligibility-discovery-interactions.md   # must print 1
grep -c -E '^## Stage B, correction B-C5' docs/planning/sv3-eligibility-discovery-interactions.md   # must print 1
grep -c -E '^## Stage B, correction B-C5' docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md   # must print 0
test -f docs/continuity/dev-manager/reviews/2026-11-16-dm-79-sv3-b-c4-delta-review-dispositions.md && echo "DM-79's report"   # must print the line
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed an owned path since it;
- or the record already holds "Stage B, correction B-C5".

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`, and `proofs/postgres-ordering/README.md`: above all D14's entry, the SV3 paragraph, S4 and "Limits";
- the brief, revision 20: D14 and "Stage B, correction B-C5", whole;
- DM-79's report, whole: its rulings (sections 1 to 9) and its words (section 11);
- the evidence record: "Stage B, correction B-C4", "Manager verification of B-C4" and "Delta re-review of B-C4", whole;
- `row_locks.py`: its module docstring, `judge`, `_relations`, and `_bindings` with `_ENDS_FROM`, so that you know what each narrowed sentence describes;
- the P11 plan's SV3 entry.

## 3. What to do

1. **Apply the twelve pairs** (items 1 to 4), in the order KK1 to KK11, then KK13, each by a script. The script reads the old and new texts from DM-79's report at your start, or from a file you copy them to, never retyped. For each pair it checks the old passage once before the change and the new text once after, and prints both counts. Record the script and its output.
2. **The AST identity.** Confirm that `row_locks.py`'s code is `07d8de3`'s with docstrings set aside. Run from the repository root:

   ```bash
   d=$(mktemp -d)   # outside the repository
   git show 07d8de3dc820e51623cb8529cac124054c0b8b2b:proofs/postgres-ordering/glow_ordering_proof/row_locks.py > "$d/row_locks.07d8de3.py"
   python3.12 -I - "$d/row_locks.07d8de3.py" proofs/postgres-ordering/glow_ordering_proof/row_locks.py <<'EOF'
   import ast, sys
   def code(path):
       tree = ast.parse(open(path, encoding="utf-8").read())
       for node in ast.walk(tree):
           if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
               first = node.body[0]
               if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                   node.body = node.body[1:]
       return ast.dump(tree)
   print("identical by AST, docstrings aside:", code(sys.argv[1]) == code(sys.argv[2]))
   EOF
   ```

   It must print `True`. Also record `git diff --stat 07d8de3dc820e51623cb8529cac124054c0b8b2b HEAD -- . ':!*.md'`, which must list `row_locks.py` alone. Then, as the stop rule's evidence, a list of the docstrings that differ: the module's, `judge`'s and `_relations`'s, and no other.
3. **The local checks,** in `proofs/postgres-ordering`, each under `env -i`:
   - set up the proof's venv with `python3.12 -m venv` and its hash-locked install;
   - its offline tests, `ruff check .`, `ruff format --check .` and mypy, as its README gives them;
   - the lock scan, `python -m glow_ordering_proof.account_lock_scan`: its output unchanged (52 calls, 0 joining, 7 account locks).
4. **The run of record.** Commit and push your change: the README, the docstrings, KK10 and KK11 in the record, and KK13 in the P11 plan. Wait for the Foundation run on that commit to finish (the push rule). Then read it with your GitHub tools:
   - every job's conclusion, and the gate's line (`Application checks passed`);
   - each suite's result, D14's line (`ROW LOCKS (D14): PASS`, none refused) and its own-objects counts (0, 0, 0);
   - the account-table writer-lock counts in each suite, against B-C4's run of record (44,841; 127; 2,061; 4,256);
   - the discovery suite, 66/66, and its phase duration;
   - whether a toolchain retry fired.
5. **The P11 plan's run of record** (item 4): after the run, the P11 plan's SV3 entry gains B-C5's run of record, in the form of B-C4's sentence there: "Correction B-C5's (…; DM-79) is [<run ID>](<run URL>) (on `<code head>`), with every job passing, …; the evidence record's "Stage B, correction B-C5"." Its parenthesis names what B-C5 did, in the brief's words: two limits recorded under D14's freeze, the relations check's words narrowed to the positions its reading binds, the record corrected.

## 4. The record

Add a section `## Stage B, correction B-C5` at the end of `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, with:
- the start gate's results, the environment check (names only) and the toolchain version;
- **DM-79's twelve pairs:** a table with one row per pair, giving its target file, its old passage's count before and its new text's count after;
- **the AST identity:** the script's result, the non-Markdown diff stat, and the docstrings that differ;
- **commands:** every command you ran, with its result line;
- **the run of record:** its ID, each job's result, the gate's line, D14's line, the own-objects and account-table lock counts in each suite against B-C4's, the discovery phase's duration, and whether a retry fired;
- **B-C5's lines in `services/api`:** their count (expected zero);
- every deviation from the brief, and what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit (the record's section and the P11 plan's run of record) only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only these four paths:
- `proofs/postgres-ordering/README.md`;
- `proofs/postgres-ordering/glow_ordering_proof/row_locks.py`;
- `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`;
- `docs/testing/p11-deferred-acceptance.md`.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- DM-79's twelve pairs, each applied or not, with its counts;
- the AST identity's result, and the docstrings that differ;
- each local check's result;
- the run of record: its ID, every job, the gate's line, D14's line, the own-objects and account-table lock counts in each suite against B-C4's, the discovery phase's duration, and whether a retry fired;
- B-C5's lines in `services/api`;
- anything that met the stop rule, every deviation from the brief, and what you could not run.
