# SV2 Stage B exact-head review prompt, after correction C1 — photos, the photo requirement and one pointer order, with a written threat model

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 11 November 2026.**
- **Durable brief:** [SV2 — The profiles and media slice](../planning/sv2-profiles-media.md), revision 8, "Review plan", "Stage B (revision 6)" and "Stage B, correction C1 (DM-58 item 9)".
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Exact-head review of Stage B", with a disposition for each finding (fix before the merge, or carry), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.94 (confidence 0.88); rung probabilities low 0.00, medium 0.00, high 0.12, extra high 0.82, max 0.06, ultracode 0.00. Model probabilities Fable 5.1 0.19, Opus 5.5 0.81, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.75). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.023, Fable 5.1 at extra high 0.156, Fable 5.1 at max 0.011, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.097, Opus 5.5 at extra high 0.664, Opus 5.5 at max 0.049, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-11T05:00:42Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs (the brief's "Review plan"; DM-58 section 7 set its scope). The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR44's head, which is this prompt's commit (manager workflow, step 6). A full review, not a delta review (DM-58 section 3).
- **Deletion condition:** prune after SV2 Stage B's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **exact-head code and security review of SV2's Stage B, after its correction C1**: photos, the photo requirement and one pointer order, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head in full, with a written threat model. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **Stage A merged** with PR43 at `4dc2061` (10 November 2026): the server's profile, its settings, consent, the adult check, the birth input and visibility, sealed until P11. Two exact-head reviews read it.
- **The brief,** `docs/planning/sv2-profiles-media.md`, revision 8. Its Stage B text applies the Dev Manager's conditions word for word:
  - DM-57's U1 to U11 (`docs/continuity/dev-manager/reviews/2026-11-11-dm-57-sv2-stage-b-brief.md`);
  - DM-58's J1 to J9 (`…/2026-11-11-dm-58-sv2-stage-b-decisions.md`);
  - Nathan's directions OD-61 (automated photo approval, no manual staff review) and OD-62 (photos in R2 object storage), in `docs/continuity/owner-directions.md`.

  In short, Stage B builds:
  - photos as objects in private R2 storage, behind storage, processing, detection, check and hold ports with **fixture adapters only**: no R2 call, credential, SDK or decoder (D10);
  - opaque object keys; upload grants under the media policy's own version; adoption of the first matching completion only; Glow's processing at the system review step; G-02's seam for every adopted upload, one with no variant included (rejected, `no_variant`); removal completing only on every object's acknowledgment;
  - the automated check's approval and rejection as `system` (F05's `approve` and `reject`, the only registry entries changed), and staff restriction on a report, which the check never clears;
  - the photo requirement, with D9's recompute and demotion;
  - one settings-pointer order in every transaction, with a check that raises an internal error on a lock out of order (D19), changing four of Stage A's transactions;
  - the media policy as a setting (migration 0009) and the media tables (migration 0008);
  - the profile suite's media cases.
- **The implementation** (branch `claude/sweet-ramanujan-wkn311`, code head `d8f1bad`, records `e7d6616`; the evidence record, "Stage B"): 42 reversals, sixteen decisions; run of record 42947095725, all eight jobs passed, the profile suite 64/64. The manager verified it ("Manager verification of Stage B").
- **DM-58** ruled on five of the decisions (J1 to J5: records only) and on Codex's P2 on PR44: `request_purge` and `acknowledge_deletion` refused an owner who is not `active`, so a photo removed before its owner was suspended or asked for deletion could never be purged (J6 to J9, and a correction).
- **Correction C1** (branch `claude/gracious-davinci-lpqt02`, code head `7538c76`, records `e30ef4a`; the record, "Stage B, correction C1"): the two writers lock the account row in any state through `lock_account_any_state`; every other step keeps its gate; three suite cases; run of record 42957799823, all eight jobs passed, the profile suite 67/67. The manager verified it ("Manager verification of Stage B's correction C1").

**The code head under review is `7538c76`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `7538c76` (the start gate checks this).

**Your scope:**
- **The code:** `git diff 4dc2061a33c6f63e2887b11aeb2fd32d6224e23e 7538c7642f38ac374f2a0f7ca22c8887a3a31922`, its 29 non-Markdown paths, read in full at `7538c76`:
  - `services/api/glow_profiles/` (11): `media.py` and `media_fixtures.py`, new, and Stage A's `settings_store.py`, `tx.py`, `staff.py`, `operations.py`, `requirements.py`, `contract.py`, `views.py`, `urls.py` and `events.py` as Stage B and C1 changed them;
  - `services/api/glow_domain/` (2): `media.py`, new, and `profile_settings.py`;
  - `glow_persistence/models.py` and migrations `0008` and `0009`;
  - `services/api/tests/` (8);
  - `packages/contracts/production/flows-v1.json` and `packages/contracts/tests/test_transition_contract.py`;
  - `proofs/postgres-ordering/` (3): `profile_cases.py`, `profile_support.py` and `tests/test_profile_offline.py`.
- **C1's own change,** `git diff ecad10c797b56d724c6039cc771717f6ccfad6e9 7538c7642f38ac374f2a0f7ca22c8887a3a31922` (6 non-Markdown paths), read with extra care, since no review has read it.
- **The records, as claims about the code:**
  - the evidence record's Stage B sections, whole: "Stage B", "Manager verification of Stage B", Codex on `82d246b`, "Stage B, correction C1" and its manager verification;
  - the data model's `MediaAsset`, `MediaObject` and grant rows, and its unit-of-work table's F05 row (J5);
  - the contract document's F05 index row and server mapping;
  - the media fixtures note's server section (`docs/architecture/private-media-fixtures.md`, J3);
  - the contracts README's Stage B bullet and the proof README's profile-suite paragraph;
  - the P11 plan's Stage B entries (PV04, DB07, DB08, DM-57's and DM-58's entries).
- **The runs:**
  - 42947095725 (Stage B's run of record) and 42957799823 (C1's);
  - the PR run on PR44's head (event `pull_request`), once it has finished.
- **Out of scope:**
  - code Stage B does not change (`glow_chat`, `glow_identity`, `glow_api` and the rest) and Stage A's code where Stage B left it unchanged. A finding there is reported as pre-existing, not as a defect of this item;
  - the items carried: P11's real adapters, delivery, worker and DB07 crash cases (DM-58 J2, J5), P07's restriction clearing and G-02's detection service (U7, J8), P08's account deletion (J9), G-05's hold record and the retention message. Report only where the code contradicts what the carry says.

**The threat model** (the brief's "Review plan"; DM-31 item 3: uploaded files are a security boundary). Write it in your report:
- **Assets:**
  - a member's photos: the uploaded originals, which keep their metadata, and the variants Glow delivers;
  - the object keys, the store's upload credentials and the grants;
  - the delivery references, and what a reference lets its holder reach;
  - the photo's states, its owner's removal record and staff's restriction record;
  - the hold, which must stop a purge and a delivery;
  - the collection's version, and the order of a member's photos;
  - the photo requirement, and whether a profile is `visible`;
  - the media policy and its fixed ceilings;
  - the settings pointers and their lock order;
  - the profile suite's `SECRET_KEY` and JWT key, and the run's database credentials.
- **Actors:**
  - an anonymous prober;
  - a holder of another member's stolen token (SV1's actor);
  - a signed-in member acting on another member's photo or collection;
  - a member who replays a grant, races two uploads, or uploads past the policy's limits or after the grant expires;
  - a forged, duplicated, late or out-of-order store event (completion or deletion), at the storage port;
  - a member who is suspended or asks for deletion with photos in flight;
  - a staff caller, in code until P07;
  - a console publication of the media policy that crosses a ceiling;
  - anyone who reads this public repository's CI logs and artifacts.
- **Entry points:**
  - F05's member routes under SV1's actor (`MediaIntent`, `OwnedObjectRequest`; `MediaLifecycle`, `MediaUploadGrant`, `MediaCollection`);
  - the store's events (`record_upload`, `acknowledge_deletion`) through the storage port;
  - the system steps (`review`, `run_check`, `request_purge`, `delivery_reference`);
  - staff's restriction (`staff.restrict_media`), with no route;
  - the settings publication of `media.policy`;
  - migrations 0008 and 0009;
  - the profile suite's job steps.

For each threat, give the code that stops it and the test that proves it. It covers the brief's "Review plan" focus list for Stage B: the media items, D19, and whatever Stage B changes in Stage A's code:
1. each F05 route's ownership and refusals;
2. **the media state machine, its seam and its provider events:** only an authenticated completion moves `upload_pending` → `quarantined`; only the system review moves `quarantined` → `review_pending`; only purge reaches `removed`;
3. **upload-grant replay and expiry:** one completion adopted, within its grant's time and its own policy version's byte limit; a later or mismatched completion changes nothing;
4. **the hold port's place in each path:** approval, delivery and a removed asset's purge each ask it first;
5. **the automated check never clears a staff restriction,** and an owner's removal is never undone;
6. **provider-event authenticity at the port,** and what the domain does with an event the port rejects;
7. **R2's shape (OD-62):** keys that reveal nothing; an original never delivered; a completion matched to its grant; processing on the adopted object; every adopted upload through the seam, one with no variant included; deletion acknowledged for every object;
8. **each F05 step's account-state rule after C1** (the record's list, "Each F05 step's account-state rule after C1"): the purge and the deletion acknowledgment in any state, under the account row's lock; every other photo command, staff operation, system step and read refusing an account that is not `active`;
9. **one pointer order (D19):** each transaction's pointers in name order, the publication's own lock recorded, and the check that enforces it, in every environment;
10. **D9's recompute** at each photo writer: the check's approval, the removal and the restriction of the last approved photo; no path makes a profile `visible` without an approved photo, or leaves it `visible` after the last one goes;
11. **the seeded requirements:** no runtime path writes an approved photo, and a test's seeded rows cannot reach the runtime;
12. **D17's rules** in every media response and error: no key, credential, original reference or byte in any body, log record, event or artifact;
13. **the outbox:** media events carry references, never values, and each reference names a record that still exists;
14. **the media policy's ceilings and audit,** including a ceiling crossed in two publications;
15. **the seal:** the served runtime imports none of Stage B's code;
16. **the proof's secret handling** in the profile suite's media cases.

**The focus:**
1. **The threat model above,** each threat with its stopping code and its test.
2. **The Dev Manager's conditions met in code:** DM-57's U1 to U5 and U8 to U10, DM-58's J6 and J7 and its section 3's correction. Name any condition the code does not meet.
3. **The sixteen decisions and DM-58's rulings,** against the code:
   - **item 1's premise:** no path changes an asset's projected fields without bumping its version, and no path deletes an asset row, so the derived collection version never goes back;
   - a removed photo outside the collection's 20 entries and its read, and still readable by its ID (J3, J4);
   - the store's upload time as the grant's clock (J2);
   - the ports called inside the transaction, with fixtures only (J2, J5): say whether any fixture call there has an effect outside the database;
   - the owner's reference during a hold: the reference cannot be an address, and only `delivery_reference` resolves a photo for delivery;
   - each other decision as the record states it, or a finding.
4. **C1:** the two writers, `lock_account_any_state` equal to `lock_account` without its state check, the three suite cases, and its deviation 1 (the pinned line at `media.py:128`).
5. **The coverage notes** (DM-58 section 5): say for each whether an offline test is needed before the merge, or the suite's case suffices:
   - **M2:** the seam skipped for an upload with no variant, caught only by the suite's `the seam was given the original` (`profile_cases.py:3119`);
   - **M3:** the approval's hold check removed, caught only by the suite's `the approval asked the hold port first` (`profile_cases.py:3074`);
   - **migration 0008's constraints** have no malformed-write case, where Stage A's 0005 has one for each (the P11 plan's DB04, partial): whether this waits for P11 or needs cases now.
6. **No test is weakened or vacuous:**
   - Stage A's cases that now need an approved photo, `CASE_COUNT` and the F05 registry test D11 names each assert what they asserted, or more;
   - each reversal the record names fails its case;
   - no case could pass while the behaviour it guards is wrong. Above all: the grant's adoption, the seam's inputs, the hold's order, the purge's completion, the restriction's survival, the pointer order and the account-state cases;
   - the static guards (`test_profiles_offline`'s `LockOrderTests` and logging checks, `test_profile_recompute`'s state-writer allowlist with its line pins, the D19 lock-site test and the sealed-runtime test) are not defeated by a plausible edit.
7. **The contract:**
   - every existing DTO is unchanged, and `MediaUploadGrant` is returned unchanged (U3);
   - the only registry change is F05's `approve` and `reject` to `system`, with an allowed and a forbidden example;
   - the generated outputs match the schemas when regenerated.
8. **The workflow and dependencies:** `foundation.yml` is unchanged from `4dc2061`, and so is every lock and requirement file. Read the Database proof checks job's steps and logs in the two runs: the profile suite runs Stage B's cases on its own database, as the CI policy's paragraph describes.
9. **The records:** every claim in the texts listed in the scope holds against the code and the runs.

**Re-run, at least,** in a scratch copy of `7538c76`:
- **The API's checks:** `manage.py check`, `manage.py test tests`, `ruff` and the configured `mypy`. The contract tests. The proof's offline tests, `ruff` and `mypy`.
- **The contract outputs:** `node scripts/generate.mjs --check` in `packages/contracts`, after `npm ci --ignore-scripts` there.
- **Four offline reversals:**
  - `settings_store._hold`'s raise removed: the D19 test of a lock out of order fails;
  - `lock_account` back in `request_purge`: `LockOrderTests` and `AccountStateTests` fail;
  - `lock_account_any_state` in `review`: the same tests fail for `review`;
  - the runtime's URL configuration importing `glow_domain.media`: the sealed-runtime test fails.
- **The profile suite, informational:** on a throwaway PostgreSQL under P06.DB's D4, if Docker allows. It is informational, and you name it so. If you can run it, add database reversals you doubt, such as:
  - a second completion for a used grant adopted;
  - the seam skipped for an upload with no variant (M2);
  - the approval's hold check removed (M3);
  - delivery of a held photo.

**What comes after this review: the correction classes.** Report every finding with its severity. A correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let an original, a variant, an object key, an upload credential or a photo's bytes reach a member who does not own it, a log, an error, a URL, an outbox event, a CI log or an artifact;
- let a member read, write, reorder or remove another member's photo, or act unauthenticated;
- let a completion be adopted twice, after its grant expires, past its policy version's byte limit, or for another grant's key;
- let a photo reach `review_pending`, `approved` or `removed` other than through its one path, or skip the seam;
- let the check approve a held photo or clear a staff restriction, or undo an owner's removal;
- let a held photo be delivered or purged, or a removed or restricted photo be delivered;
- leave a removal unable to complete, or complete before every object is acknowledged;
- let a profile be `visible` without an approved photo, or stay `visible` after the last one goes;
- let a transaction take settings pointers out of name order without the check stopping it;
- let a publication cross a media ceiling, or skip its audit;
- leave an outbox event naming a record that no longer exists;
- let the served runtime import Stage B's code, or add a package;
- let a test pass where it should fail, or fail where the code is right;
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
  - PyPI and the npm registry, for hash-locked installs in a scratch copy;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`);
  - GitHub, through your tools, to read runs.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from that image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.
- **Never:**
  - dump the environment, or print a credential, password, token, session key or key;
  - read, print or use the value of any `AWS_*` variable (section 1);
  - call any provider or HDE, R2 or Cloudflare included, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE` (DM-57 and DM-58). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values. If any other `AWS_*` name is present, stop and report.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`; Docker if present. Record their versions.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 4dc2061a33c6f63e2887b11aeb2fd32d6224e23e
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 7538c7642f38ac374f2a0f7ca22c8887a3a31922 HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "the code head under review"
git diff --quiet 7538c7642f38ac374f2a0f7ca22c8887a3a31922 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs ':!*.md' && echo "no code on the live branch after 7538c76"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-10-sv2-profiles-media.md | grep -c -E '^#+ Exact-head review of Stage B'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `7538c76`;
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
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`; `packages/contracts/README.md`;
- the brief, revision 8, and DM-57's and DM-58's reports;
- OD-61 and OD-62 in the owner-direction register;
- the evidence record's Stage B sections, whole;
- F05 in `packages/contracts/production/flows-v1.json`, and `MediaIntent`, `MediaLifecycle`, `MediaUploadGrant` and `MediaCollection` in `gapp-api-v1.schema.json`;
- `docs/architecture/private-media-fixtures.md` (P04.3's semantics and the server section) and `docs/architecture/media-provider-mapping.md`;
- the data model's media rows, unit-of-work table and outbox event table; the contract document's F05 sections;
- `glow_chat/contact.py`'s `suspend`, `delete` and `_revoke_account`, which C1 relies on (read only);
- every file in the code diff, whole: `glow_profiles/media.py`, `media_fixtures.py`, `settings_store.py`, `tx.py`, `staff.py` and `operations.py` above all, with `glow_domain/media.py`, the models, the migrations, `profile_cases.py` and `profile_support.py`.

**The runs,** with your GitHub tools:
- 42947095725 and 42957799823: every job's conclusion, the gate's line, the Database job's steps and its profile lines;
- the PR run on PR44's head, if it has finished.

## 3. What to do

1. Write the threat model, then review the code against the focus, item by item.
2. In a scratch copy of `7538c76`:
   - re-run the checks and the four offline reversals above, and any you doubt;
   - run the profile suite locally under D4 if you can, informational.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required;
- the threat model;
- the findings, in a table: number, severity, correction class or not, file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 9), one or two lines each, with each coverage note's ruling;
- the reversals you re-ran, with their results, the local database ones named informational;
- what you ran, and what you could not run or read.
