# SV3 Stage B, correction B-C6: short bounded delta re-review prompt (records only; class 5 and class 1)

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 17 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 21, "Stage B, correction B-C6 (B-C5's short review; DM-80)", its paragraph "B-C6's review".
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta re-review of B-C6", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.04 (confidence 0.81); rung probabilities low 0.00, medium 0.13, high 0.71, extra high 0.16, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.99, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.129, Opus 5.5 at high 0.703, Opus 5.5 at extra high 0.158, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.001, Sonnet 5.5 at high 0.007, Sonnet 5.5 at extra high 0.002, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-17T01:33:21Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 5's pre-merge read of PR47 follows it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR47's head, which is this prompt's commit (manager workflow, step 6).
- **Deletion condition:** prune after Stage B's PR (PR47) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **short bounded delta re-review of correction B-C6, in SV3's Stage B**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). B-C6 is a records correction: it changes two docstrings and Markdown, and no code. You review it against `07d8de3`, the code head the last review of code read, under class 5 and class 1 only (DM-80). This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`, the head of [PR47](https://github.com/amthorn78/glow-dating-app/pull/47).

**What came before.**
- **SV3's Stage A** (PR45, `8d83474`) and **B0** (PR46, `947576d`) are merged.
- **Stage B and B-C1 to B-C4** are built: code head `07d8de3`. D14's rules are frozen from `07d8de3` (DM-78 section 10).
- **B-C4's bounded delta re-review** found two forms D14 does not see, stated limits under the freeze: F1, an item after a word that ends the `FROM` list, and F2, a placeholder followed by a string constant. **B-C5** (code head `0d784d4`) recorded them in DM-79's words.
- **B-C5's short review** asked for one class 5 correction, R1: every word of `_ENDS_FROM`, written as a column's name after a dot, ends the `FROM` list, while four texts named only `set` and `values`. It also noted one record nit, N1, a sentence on Django's `ON` conditions. The evidence record, "Delta re-review of B-C5", holds them.
- **DM-80** (Dev Manager 5, `docs/continuity/dev-manager/reviews/2026-11-16-dm-80-sv3-b-c5-review-dispositions.md`) put the limit's detail in one home: the proof README's F1 limit states the mechanism, with R1's planted example, and the other texts point to it instead of listing exceptions. It narrowed N1's sentence to the ORM's joins, and ruled a records correction, B-C6, with this short review. Its eleven texts are LL1 to LL11 (its section 9): B-C6 applies LL1 to LL7; the manager applied LL8 to LL11 before B-C6.
- **B-C6** (branch `claude/intelligent-ride-t4vdpj`) applied them: code head `bf33fd0`, records `a965f3a` (the evidence record, "Stage B, correction B-C6").
- **Its run of record** is Foundation run 43983435571 on `bf33fd0` (push):
  - all eight jobs passed, and the gate printed `Application checks passed`; no DM-41 retry fired;
  - ordering 56/56, 115/115, 13/13 and 62/62; identity 49/49; profile 69/69; discovery 66/66, its phase 203 s (B-C5's: 135 s);
  - each suite's `ROW LOCKS (D14): PASS`, 0 refused, own objects 0, 0, 0; account-table writer locks 44,841, 127, 2,061 and 4,256, all `FOR NO KEY UPDATE`, equal to B-C5's run of record (43960479739).
- **The manager verified B-C6** (the evidence record, "Manager verification of B-C6") and merged it into the manager branch.
- **The session's departures,** all recorded: its venv outside the repository; its download of the Database job's log from the link the GitHub tools returned, as its prompt allowed; and its lock-scan comparison against `0d784d4`'s export, not `07d8de3`'s.

**The head under review.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `bf33fd0` (the start gate checks this). The baseline is `07d8de3`; `main` is at `947576d`.

**Your scope** (the brief's "B-C6's review"; nothing outside it):
- **Every path B-C6 touches,** as it stands at the head: `git diff 697072119cffab42997070c23160651b077c431b a965f3a7af70e7e328bb5d6b467fdbd957afe1b9`. These are the proof README, `row_locks.py` (two docstrings), the evidence record and the P11 plan.
- **The AST identity:** `row_locks.py`'s code at the head equals `07d8de3`'s with docstrings set aside.
- **DM-80's eleven texts,** each found once at the head, as given.
- **Every sentence that says what the relations check reads or where its reading stops,** outside the reviews' own sections, checked against the scan in `_bindings` (focus 3).
- **The run:** 43983435571, and PR47's pull-request run on this prompt's commit or its parent, if one has finished.
- **Out of scope:**
  - D14's rules themselves, which are frozen; a form they do not see is a stated limit, not a finding to correct;
  - code B-C6 does not change, among it everything in `services/api` and the ledger;
  - the earlier stages' and corrections' code and records outside B-C6's diff and outside focus 3's sentences, which the earlier reviews read;
  - #1's fix, which is SV4's, and the items carried to later phases.

**The size rule** (DM-80). This review is short because B-C6 changes no code: `row_locks.py` differs from `0d784d4` in two docstrings only, and from `07d8de3` in three. Check this yourself first, by AST. If any code changed (anything but those docstrings, in any non-Markdown file), say so first: a full exact-head review applies instead, and the manager takes it to the Dev Manager.

**How findings are judged** (the brief's "B-C6's review"):
- **Class 1 (blocking):** a lock of an `AppAccount` row at the reviewed head, in `services/api` or the reference design, or in a statement a suite sends that D14 passes, that is not `FOR NO KEY UPDATE`, however it is written.
- **Class 5:** a record (`row_locks.py`'s docstrings, the README, the evidence record, the P11 plan, the brief's D14 rule) that claims D14's rule refuses or sees more than it does.
- **Neither:** a record wrong about anything else is a record nit; a form D14 does not see is a stated limit under the freeze, with its planted example. With the code unchanged, no other class can arise.

Class 1 and class 5 lead to a correction. Name each finding's class, or say it is a record nit or a stated limit.

**The focus:**
1. **The AST identity.** Is `row_locks.py`'s code at the head `07d8de3`'s, with docstrings set aside? Do exactly two docstrings differ from `0d784d4`'s (the module's and `_relations`'s), and exactly three from `07d8de3`'s (the module's, `judge`'s and `_relations`'s)? Is `row_locks.py` the only non-Markdown path that differs from `07d8de3`?
2. **DM-80's texts.** Is each of LL1 to LL11 found once at the head, as given (each the content of its quoted code block in DM-80's section 9, without the `> ` markers)? LL1's, LL8's, LL10's and LL11's old passages stay present once, since each new text keeps its old passage and adds to it; every other old passage is gone.
3. **R1's kind of gap, closed rather than found one word at a time** (class 5). Find every sentence, outside the reviews' own sections ("Delta re-review of …" and the review prompts), that says what the relations check reads or where its reading stops: in the proof README (the D14 entry, the SV3 paragraph, "Limits"), `row_locks.py`'s module, `judge` and `_relations` docstrings, the evidence record, the P11 plan, and the brief's D14 rule. Read `_relations`, `_bindings` and `_ENDS_FROM` at the head. Then check each sentence against the scan in `_bindings`:
   - every word of `_ENDS_FROM`, in every position the tokenizer can give it: an item's name, an item's alias, a column's qualifier, a column's name after a dot, a function's name, and a bare word;
   - and the closing parenthesis.

   Does any sentence still claim the reading binds a position it does not, or name a narrower set of ends than the scan has? Plant each case through `row_locks.refusal` with the models' tables given, a statement taking `FOR UPDATE` that does not name the account table, with an unknown relation after the word, and with a control that is refused.
4. **F1's limit as it now stands** (LL4): its list of the sixteen words against `_ENDS_FROM`; its mechanism sentence; R1's planted example (passes) and its controls (refused); a statement naming the account table judged by the account rule as before; and N1's narrowed sentence on the ORM's joins, against Django 5.2.17's `Join.as_sql` (the proof's pinned version), from a hash-locked install.
5. **B-C6's own records:** LL1's B-C6 sentence in the README; every claim in the record's "Stage B, correction B-C6"; the P11 plan's B-C6 run-of-record sentence, against run 43983435571.
6. **Class 1.** With the code unchanged, does the run of record show any account-table lock that is not `FOR NO KEY UPDATE`, or any refused statement? Compare its D14 lines with 43960479739's.
7. **Nothing else changed:** only the four paths, and within them only B-C6's owned parts (the brief's "Correction B-C6 only", LL11): the README's D14 entry, SV3 paragraph and "Limits"; the P11 plan's SV3 entry, its runs of record only; the evidence record; no workflow, contract package, model, migration, lock file, dependency, test or `services/api` file.
8. **The session's departures:** does any affect the evidence?

**Re-run, at least,** in a scratch copy of the whole head (the proof's offline tests read `packages/contracts` and the workflow, so a partial export fails them):
- the proof's offline tests, Ruff, `ruff format --check` and mypy;
- the lock scan, its output compared byte for byte with `07d8de3`'s;
- the AST comparison, by your own script;
- the count of each of DM-80's eleven texts, by a script that reads them from the report, never retyped;
- focus 3's planted cases, by a script that builds them from `_ENDS_FROM` itself, and focus 4's examples, through `row_locks.refusal`, with one control of your own against a claim you doubt.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 12. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, thread resolutions, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
  - **GitHub is read through your GitHub tools.** If a sub-agent reads it another way, say so in the report.
- **Network:**
  - PyPI, for hash-locked installs in a scratch copy;
  - GitHub, through your tools, to read runs and PR47; and GitHub's Actions results host, only through a job-log download link those tools return, to read a whole log. Record no such link.

  No Docker and no local database run: the code is unchanged.
- **Never:**
  - dump the environment, or print a credential, password, token, session key or key;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or any other external service, or start Docker;
  - run `migrate`, `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE` (DM-57 and DM-58). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command. If any other `AWS_*` name is present, stop and report.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`. Record its version.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. No `AWS_*` name passes.

## 2. Start gate

If your checkout is shallow (`git rev-parse --is-shallow-repository` prints `true`), run `git fetch --unshallow origin` first: a shallow history gives a wrong merge base.

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 947576d98b7c3103455a670c20fdba2734ff5053
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet bf33fd097ef6012f3a07303be4a8c0a7aaeecc1d HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet bf33fd097ef6012f3a07303be4a8c0a7aaeecc1d origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after bf33fd0"
git diff --name-only 07d8de3dc820e51623cb8529cac124054c0b8b2b HEAD -- . ':!*.md'   # expected: proofs/postgres-ordering/glow_ordering_proof/row_locks.py alone
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Delta re-review of B-C6'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `bf33fd0`;
- this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree, run from the repository's root:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:**
- root `AGENTS.md` and `CLAUDE.md`; `proofs/postgres-ordering/README.md` (D14's entry, the SV3 paragraph, S4 and "Limits");
- the brief, revision 21: D14 and "Stage B, correction B-C6", whole;
- DM-80's report, whole;
- the evidence record: "Delta re-review of B-C5", "Stage B, correction B-C6" and "Manager verification of B-C6";
- the diff `git diff 697072119cffab42997070c23160651b077c431b a965f3a7af70e7e328bb5d6b467fdbd957afe1b9`, and, at `HEAD`, `row_locks.py`'s module docstring, `judge`, `_relations`, `_bindings`, `_ENDS_FROM` and `_read`, the tokenizer that feeds them.

**The run,** with your GitHub tools: 43983435571. Read every job's conclusion, the gate's line, and the Database proof checks job's suite, scan and D14 lines.

## 3. What to do

1. Review the delta against the focus, item by item.
2. In a scratch copy of the head, re-run the checks above, and any you doubt.
3. For each finding, give:
   - its severity (blocking, should fix, nit);
   - its file and line, and the evidence;
   - its class (1 or 5), or "record nit", or "stated limit" with its planted example.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the size rule's check, and whether a full review applies instead;
- **the verdict:** approve, approve with nits, or changes required. Changes are required only for a finding in class 1 or class 5;
- the findings, in a table: number, severity, class, "record nit" or "stated limit", file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 8), a few lines each, with focus 3's list of sentences and, for each, the positions and words planted and the result;
- what you re-ran, with results, and what you could not run or read.
