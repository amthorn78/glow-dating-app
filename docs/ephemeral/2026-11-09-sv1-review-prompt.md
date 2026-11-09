# SV1 exact-head review prompt — the identity slice, with a written threat model

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 9 November 2026.**
- **Durable brief:** [SV1 — The identity slice](../planning/sv1-identity.md), revision 4, "Review plan" and "Correction C1".
- **Where the result goes:** the report Nathan relays. The manager records it in the SV1 record, "Exact-head review of SV1", with a disposition for each finding (fix before the merge, or carry), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Fable 5.1 at max.** Effort score 3.59 (confidence 0.71).
    - Rung probabilities: low 0.00, medium 0.01, high 0.07, extra high 0.25, max 0.66, ultracode 0.01.
    - Model probabilities: Fable 5.1 0.60, Opus 5.5 0.40, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.47).
    - Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.006, Fable 5.1 at high 0.042, Fable 5.1 at extra high 0.150, Fable 5.1 at max 0.396, Fable 5.1 at ultracode 0.006, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.004, Opus 5.5 at high 0.028, Opus 5.5 at extra high 0.100, Opus 5.5 at max 0.264, Opus 5.5 at ultracode 0.004, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000.
    - Flags: boundary between extra high and max; model near tie between Fable 5.1 and Opus 5.5.
    - Sent 2026-11-09T15:10:12Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs (DM-45 item 14). The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR42's head and of this prompt's commit (manager workflow, step 6).
- **Deletion condition:** prune after SV1's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **exact-head code and security review of SV1**, the identity slice, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head, with a written threat model. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **The brief,** `docs/planning/sv1-identity.md`, revision 4. Its Outcome items 1 to 10, D1 to D15, acceptance checks 1 to 13 and "Correction C1" apply the Dev Manager's conditions word for word: DM-45, DM-46 and DM-47, in `docs/continuity/dev-manager/reviews/` (`2026-11-09-dm-45-sv1-brief.md`, `…-dm-46-sv1-brief-revision-2.md` and `…-dm-47-sv1-email-change.md`). In short:
  - maintained sign-in on django-allauth 65.21.1 headless, the `app` client only, `HEADLESS_ONLY`, in the development scope only;
  - the JWT strategy with stateful validation and rotation, through a subclass that ends a session at both layers on a replayed refresh token, after allauth's own checks in allauth's order (N2);
  - `AppAccount` and `AccountSession` bound to the maintained user, `UserSession`'s primary key as the session reference (D5), and the Django session's expiry aligned to the `AccountSession`'s;
  - every session and account transition through `glow_chat`'s reviewed operations, outside any transaction, then allauth's layer; F01's `verified` transition in `glow_identity`;
  - one actor class, the `AccountAccess` route, the mail adapter with Glow's wording, the age-state seam;
  - the identity suite on a second disposable database in the Database proof checks job; the served runtime sealed.
- **The implementation** (branch `claude/hopeful-cerf-kc91xx`, code head `269ac3b`): 47 identity cases and 33 reversals, each failing its case. Run of record: push run 42578800951, all eight jobs passed. The manager verified it (the record, "Manager verification") and triaged its findings.
- **Codex's only finding on PR42** (P1, `services/api/glow_identity/conf.py:93-94`, on `6b8c958`): an email change needed no reauthentication. The implementation session had reported the same gap. The Dev Manager approved a correction (DM-47).
- **Correction C1** (branch `claude/stoic-franklin-ief71e`, code head `bda299e`; the record, "Correction C1"):
  - `ACCOUNT_REAUTHENTICATION_REQUIRED = True`, and a new case for acceptance check 13;
  - the job's secret check moved to `glow_ordering_proof/identity_scan.py`, scanning the results JSON too, with the upload gated on its pass;
  - the suite's own scan also covers the JSON.

  Run of record: push run 42634020622, all eight jobs passed, the identity suite 48/48. The manager verified it (the record, "Manager verification of correction C1").
- **F-M1, found by the manager:** `mail.no_link_no_stranger` forbids `http` in each lowercased message, and allauth's codes can spell `HTTP`. So the check can fail on a legal code, rarely. It is already dispositioned, fix before the merge, in the correction pass after this review. Confirm it, and say what its fix and test should cover.

**The code head under review is `bda299e`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `bda299e` (the start gate checks this).

**Your scope:**
- **The code:** `git diff 8d2de724091f2a7127d207fbc557ea1ced57f690 bda299e3034121b2cc20318024f35f5938f83b4c`, its 41 non-Markdown paths:
  - `services/api/glow_identity/` (14);
  - `services/api/glow_domain/identity.py`;
  - `glow_persistence/models.py` and migration `0004_account_age_state.py`;
  - `services/api/tests/` (5);
  - `services/api`'s `requirements-dev.in`, `requirements-dev.lock`, `dependency-inventory.json` and `pyproject.toml`;
  - `proofs/postgres-ordering/` (its identity modules, tests, settings, locks and `pyproject.toml`);
  - `.github/workflows/foundation.yml` (the Database proof checks job).
- **The records, as claims about the code:**
  - the SV1 record, whole, with both manager verification sections;
  - the data model's "Maintained authentication mapping";
  - the contract's "Maintained authentication reference and app mapping".
- **The runs:**
  - 42578800951 and 42634020622;
  - the PR run on PR42's head (event `pull_request`), once it has finished.
- **Out of scope:** code this item does not change (`glow_chat`, `glow_api` and the rest). A finding there is reported as pre-existing, not as a defect of this item.

**The threat model** (DM-31 item 3; the brief's review plan; DM-45 14.1). Write it in your report:
- **Assets:**
  - accounts and their addresses;
  - passwords;
  - session keys;
  - access and refresh tokens;
  - verification and reset codes;
  - the JWT signing key and the identity `SECRET_KEY`;
  - `UserSession`'s IP address and user agent.
- **Actors:**
  - an anonymous prober;
  - a holder of a stolen access token, refresh token or session key;
  - a member acting on another member's account;
  - anyone who reads this public repository's CI logs and artifacts.
- **Entry points:**
  - the 18 routes: allauth's 17 for the `app` client, and `GET /api/v1/account/access`;
  - the actor class;
  - the identity job's steps.

For each threat, give the code that stops it and the test that proves it. It covers:
1. **Every endpoint and its refusals,** unauthenticated and signed in, among them the routes 65.21.1 mounts whatever the configuration (`account/phone`, `auth/code/confirm`).
2. **Tokens:**
   - the signing key;
   - stateful validation;
   - rotation;
   - the replay subclass in allauth's check order (N2), with no action on an ended session;
   - each expiry, and the aligned expiry at both layers.
3. **The session reference and the session key:**
   - `UserSession`'s primary key, not derived (D5);
   - the key held in `UserSession` and `django_session`, and its reach at allauth's endpoints (N3);
   - the `sid`'s encryption under `SECRET_KEY`.
4. **Revocation at both layers** (D6), each step repeatable:
   - logout, password change and reset (`ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE`);
   - the session list through Glow's `USERSESSIONS_ADAPTER` (N1);
   - the replayed refresh token;
   - suspension and deletion;
   - a sign-in that fails closed.
5. **The actor class** (D7): the session from the token's own `sid`, never a header, and its use of allauth's internal `session_key_from_sid`.
6. **Enumeration and rate limits:** the taken-and-free pairs (acceptance check 3); `login_failed`; the 10-second `confirm_email` window (the record names what it reveals).
7. **The mail adapter and what a message reveals:**
   - no link;
   - no name but Glow's;
   - no address, IP address or device;
   - the two link-building mails replaced or off (D3, DM-45 7.1).
8. **Reauthentication for an address change** (C1; acceptance check 13):
   - a sign-in does not count;
   - the window, and the same session only;
   - the guessing budget being the sign-in form's;
   - no key change, no token pair and no `session_token`.
9. **The `verified` transition:** its account lock, its refusal unless `unverified`, its retry at the next sign-in, and no outer transaction anywhere a `glow_chat` call runs.
10. **The seal** (D11): the served runtime imports none of `glow_identity`, `allauth`, `jwt` or `cryptography`.
11. **G-13 and G-14:** a restored refresh token (D13); no review sign-in path.
12. **The proof's secret handling in a public repository:**
    - the keys generated to files of mode 0600, masked, never in a variable or the log;
    - the scan of the log and the JSON before anything is shown or uploaded (C1.4);
    - the suite's ledger;
    - the cleanup.

**The focus:**
1. **The threat model above,** each threat with its stopping code and its test.
2. **The Dev Manager's conditions met in code:**
   - DM-45's 2.1, 2.2, 3.1, 4.1, 4.2, 6.1 to 6.5, 7.1 to 7.3, 8.1, 9.1, 9.2, 11.1, 12.1 and 13.1;
   - DM-46's N1 to N3;
   - DM-47's C1.1, C1.2 and C1.4.

   Name any condition the code does not meet.
3. **allauth's behaviour that security rests on:** spot-check, in the installed 65.21.1, the record's "Facts read from the installed source" and C1's "What allauth 65.21.1 showed". Name any fact that does not hold, with file and line.
4. **No test is weakened or vacuous:**
   - each reversal the record names fails its case;
   - no case could pass while the behaviour it guards is wrong. Above all: the replay ordering, the actor's `sid`, the two-layer revocations, acceptance check 13 and the secret scan;
   - the static guards (`test_identity_offline`'s entry-point and no-header checks) are not defeated by a plausible edit;
   - no existing test was weakened.
5. **The known items:**
   - **F-M1:** confirm it. Say what the fix and its test should cover, and whether any other check in the suite has the same flaw (a forbidden string that a code, a token or an address can contain);
   - **the 10-second window:** is the record's account of it right?
   - **the reset code verifying the address** outside Glow's adapter;
   - **no `session_expired` on natural expiry** (carried to SV4, with C1.6);
   - **the phone refusal** (403);
   - **the suite's own JSON scan** (C1's addition).

   For each: right as dispositioned, or a finding.
6. **The workflow** (root `AGENTS.md`: CI routing is not a security boundary):
   - the complete diff of `foundation.yml` from `8d2de72` to `bda299e` is confined to the Database proof checks job;
   - no job, condition or gate elsewhere changed;
   - every SV1 step does what its name says.

   Read the actual job steps and logs of both runs.
7. **The dependency:**
   - `django-allauth[headless]` 65.21.1, `cryptography`, `cffi` and `pycparser`, hash-locked in the development scope only;
   - PyJWT unchanged at 2.15.0;
   - the runtime `requirements.in` and `requirements.lock` unchanged;
   - the proof's locks at the API's versions and hashes;
   - the licences recorded.
8. **The records:** every claim in the SV1 record, its two manager verification sections and the two mapping texts holds against the code and the runs.

**Re-run, at least,** in a scratch copy of `bda299e`:
- **The API's checks:** `manage.py check`, `manage.py test tests`, `ruff` and `mypy`. The proof's offline tests, `ruff` and `mypy`.
- **Four offline reversals:**
  - the setting off (C1-R1): the API's fragment test fails;
  - the scan ignoring the JSON (C1-R5): `IdentityScanTests` fail;
  - the actor reading the `X-Session-Token` header: the static no-header guard fails;
  - the replay check decoding without verifying the signature: the offline order test fails.
- **The identity suite, informational:** on a throwaway PostgreSQL under P06.DB's D4, if Docker allows. It is informational, and you name it so. If you can run it, add a database reversal you doubt, such as `D2-c` or `D6-h`.

**What comes after this review: the correction classes.** Report every finding with its severity. A correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let a credential, code, token, session key, key or secret reach a log, a message, a response, a CI log or an artifact;
- let a session or token act after its revocation, its expiry or its replay, or let one layer outlive the other beyond a repeatable step;
- let an account be taken over, or an address moved, without the member's password;
- let a prober tell a taken address from a free one beyond what the record states;
- let the actor take its session from anything but the token's own `sid`;
- let the served runtime import the identity slice, or add a package beyond the brief's set;
- let a test pass where it should fail, or fail where the code is right (F-M1's class);
- leave a Dev Manager condition unmet;
- make a record claim more than the code, the tests or the runs show.

Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:**
  - PyPI, for `pip install --require-hashes -r requirements-dev.lock` in a scratch copy, and for reading `django-allauth`'s release;
  - `docs.allauth.org`, for the pinned release's documentation;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`);
  - GitHub, through your tools, to read runs.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from that image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.
- **Never:**
  - dump the environment, or print a credential, password, code, token, session key or key;
  - call any provider, send any real email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
4. **The toolchain:** CPython 3.12.14 as `python3.12`, and Docker if present. Record their versions.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 8d2de724091f2a7127d207fbc557ea1ced57f690
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet bda299e3034121b2cc20318024f35f5938f83b4c HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "the code head under review"
git diff --quiet bda299e3034121b2cc20318024f35f5938f83b4c origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs ':!*.md' && echo "no code on the live branch after bda299e"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-09-sv1-identity.md | grep -c -E '^#+ Exact-head review of SV1'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `bda299e`;
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
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`;
- the brief, revision 4, and DM-45's, DM-46's and DM-47's reports;
- the SV1 record, whole;
- F01 and `AccountAccess` (`packages/contracts/production/flows-v1.json`, `gapp-api-v1.schema.json`);
- the data model's "Maintained authentication mapping" and outbox event table; the contract's "Maintained authentication reference and app mapping";
- `glow_chat/contact.py`'s `open_session`, `sign_out`, `expire_session`, `suspend`, `delete` and `_revoke_account`, which SV1 calls (read only);
- every file in the code diff, whole: `glow_identity/strategy.py`, `authentication.py`, `revocation.py`, `adapter.py`, `sessions.py` and `conf.py` above all, with `identity_cases.py`, `identity_scan.py` and the workflow's Database proof checks job.

**The runs,** with your GitHub tools:
- 42578800951 and 42634020622: every job's conclusion, the gate's line, the Database job's steps and its identity lines;
- the PR run on PR42's head, if it has finished.

## 3. What to do

1. Write the threat model, then review the diff against the focus, item by item.
2. In a scratch copy of `bda299e`:
   - re-run the checks and the four offline reversals above, and any you doubt;
   - run the identity suite locally under D4 if you can, informational.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required;
- the threat model;
- the findings, in a table: number, severity, correction class or not, file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 8), one or two lines each;
- the reversals you re-ran, with their results, the local database ones named informational;
- what you ran, and what you could not run or read.
