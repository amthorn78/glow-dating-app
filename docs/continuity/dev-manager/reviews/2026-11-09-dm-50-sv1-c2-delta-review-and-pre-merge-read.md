# DM-50 — C2's delta review (N-1, C2.5's words) and SV1's pre-merge read

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 10, relayed by Nathan (OD-25).
- **Read at:** `ffcdd41af2a03b5f3b0b320ac11db66b0fd559dd` of `claude/magical-wozniak-yfmmx2`, with SV1's code head `6da8061`. From `6da8061` to `ffcdd41` only regular Markdown files changed (no mode change, no `.claude/` path). The manager branch was still at `ffcdd41` at 22:25 UTC (`git ls-remote`).
- **Written:** 9 November 2026, finished at 22:29 UTC by the clock.
- **Boundaries kept:**
  - I checked environment variable names only; none of the six names is present.
  - I called no provider, database, HDE, Railway or TypeSafe service, ran no application test, and wrote only this file.
  - I read GitHub's runs and jobs with GitHub's tools, read-only.
  - For allauth I read the 65.21.1 wheel I downloaded and checked for DM-45 (SHA-256 `7bdf018c…`). I installed nothing and ran none of its code.
  - Notion was read, not edited.

## 1. What I read

- **The consultation** at `ffcdd41`, and the record's "Delta review of correction C2", with its findings and dispositions.
- **For item 1, at `6da8061`:**
  - `identity_support.py`: `MAIL_FORBIDDEN`, `CODE_GENERATORS`, `Context.record_issued_code`, `mail_forbidden_found` and `recording_issued_codes`;
  - `identity_cases.py`: `mail.no_link_no_stranger` and where the recorder is entered.
- **allauth 65.21.1:** the adapter's code generators and `core/internal/cryptokit.py`'s `generate_user_code`. Glow's `conf.py` and `adapter.py`, for any override.
- **For item 2:**
  - the CI policy's paragraphs on Database proof checks (lines 5 and 20 at `ffcdd41`);
  - the data model's "Maintained authentication mapping" and the contract's "Maintained authentication reference and app mapping", whole;
  - the workflow's SV1 steps at `6da8061`, with `git diff bda299e 6da8061` on the workflow, and `identity_scan.py` whole;
  - the brief, revision 5, against my C2.1 to C2.8, by script;
  - `conf.py`, the API's guard test and the new identity case;
  - the spec builder's settings, in the wheel;
  - a sweep of the living documents for the states C1 and C2 replaced.
- **CI:**
  - the PR run on `ffcdd41`, 42709897206: its job list and conclusion;
  - the run list since `cf03cde`.
- **Notion,** read-only (section 7).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. N-1 | **(a) approved, with conditions** 1.1 (the reading's words) and 1.2 (a carry). The run-wide removal meets C2.5. No code can hold a vowel, `:`, `/`, `.` or `<`, so removing any issued code, the message's own or another's, can hide nothing outside a code. No code change and no C3. N-1 becomes a records item, and the delta review's verdict becomes approve with nits |
| 2. The pre-merge read | **SV1 may merge, with conditions** 2.1 to 2.3 applied as written. 2.1 is the one that matters: P11's plan still says an email change "needs none" (no reauthentication), which C1 made false. 2.2 corrects three "revision 3" citations. 2.3 puts C2.6's counts-only rule into the CI policy. Everything else I read holds: the CI paragraph, both mapping texts with C2.8's sentence, C1.4's and C2.6's workflow changes, and **C2.1 to C2.8 as applied, which I confirm** (DM-48's deferred row). Since there is no C3, there is no read after one |
| Notion | **Matches** `ffcdd41` in every place I read, the Branches bullet included |

**How to apply:**
- Every condition is Markdown, in given words; line breaks may move.
- Applied as written, they need no read from me before the merge. My next consultation confirms them.
- The merge still needs step 7: a complete PR run on the final head, and Codex's read of that head.

## 3. Item 1 — N-1: does the run-wide removal meet C2.5?

**Yes.**

**What the code does** (read at `6da8061`):
- **Recording:** `recording_issued_codes` patches only `GlowAccountAdapter`'s two generators, `generate_email_verification_code` and `generate_password_reset_code` (`CODE_GENERATORS`). Each code they return goes, unchanged, to `ctx.issued_codes` and the secret ledger (`record_issued_code`, which keeps only non-empty strings).
- **The check:** `mail.no_link_no_stranger` runs last, over the whole outbox. For each message, `mail_forbidden_found` removes every recorded code by `str.replace`: exact, case-sensitive, every occurrence, no pattern. Only then does it lower-case the text and look for `MAIL_FORBIDDEN`: `http`, `://`, `www.`, `href`, `<a`, `allauth`, `django` and `example.com`.
- **The codes** (65.21.1, read in the wheel): Glow overrides neither the generators nor the format. `generate_user_code` draws eight characters from `BCDFGHJKLMNPQRSTVWXZ`, consonants only, and joins two groups of four with a hyphen (`core/internal/cryptokit.py:16-39`).

**Why that meets C2.5:**
- C2.5's protective words are "exact", "every occurrence", "removes nothing else", "uses no pattern", and "a link anywhere else in the message still fails it". The run-wide set keeps every one of them: each string removed is an exact code that Glow's adapter issued.
- A code holds no vowel and none of `:`, `/`, `.` or `<`. So no code can hold `://`, `www.`, `href`, `<a`, `allauth`, `django` or `example.com`.
- Removing a code can hide only an `http`, or a `www.`, made with that code's own letters. It can never hide a forbidden string outside a code. At worst, it joins the text on either side into a forbidden string, and that fails the check, which is the safe direction.
- A message that held another case's code would be a different defect, a code reaching the wrong inbox. The no-link check was never the guard for that, and the same case checks each message's recipient separately.

**Why not (b) or (c):**
- (c) strengthens nothing the check looks for, at the cost of a harness change and a review.
- (b) is a new code head, which needs exact-head review evidence under `AGENTS.md`. That is a full cycle for a docstring and a test pin.
- 1.2 carries both to the next item that changes the file, where they ride that item's own review.

**1.1 — The reading, for the record** (with N-1's disposition):

> **C2.5's reading** (DM-50): "the exact code the case issued" covers every code the run's cases issued: each code Glow's account adapter generated during the run, recorded where it was generated (`generate_email_verification_code`, `generate_password_reset_code`) in `ctx.issued_codes`. The check removes each of them from each message, by exact, case-sensitive replacement, wherever it occurs, before it looks for `MAIL_FORBIDDEN`; it removes nothing else and uses no pattern. In 65.21.1 a code is eight letters from `BCDFGHJKLMNPQRSTVWXZ`, in two groups of four joined by a hyphen, so no code can hold `://`, `www.`, `href`, `<a`, `allauth`, `django` or `example.com`. Removing a code can hide only an `http` or a `www.` made with that code's own letters, never a forbidden string outside a code; at worst it joins the text on either side into one, which fails the check. A link anywhere in a message outside a code still fails it, so C2.5 is met. `mail_forbidden_found`'s docstring repeats C2.5 and is read the same way.

**1.2 — The carry.** In the carried-items file, under "Carried to SV2", add:

> - **From SV1's C2 delta review** (DM-50; N-1, N-2), for the first of SV2 to SV4 whose work changes `proofs/postgres-ordering/glow_ordering_proof/identity_support.py` (if SV2's does not, this entry moves to the next item's section): reword `mail_forbidden_found`'s docstring to say that the check removes every code the run's cases issued, and add a test that pins the removal as exact, case-sensitive and of every occurrence. Until then, the SV1 record's reading of C2.5 (DM-50) governs the docstring's words.

## 4. Item 2 — SV1's pre-merge read (DM-45 14.1), at `ffcdd41`

**The CI policy's Database proof checks paragraphs: accurate.**
- **Checked against the workflow at `6da8061`:**
  - the second database, `glow_identity_proof`, with its own marker and the same non-superuser role;
  - the ordering database's marker refused there;
  - the migrations from zero, and `makemigrations --check --dry-run`;
  - the suite through Django's test client;
  - the job's check (`identity_scan`) before any output is shown;
  - the second run's refusal with the counts unchanged;
  - the upload only after the check has passed (`if: ${{ always() && steps.identity.outputs.scan == 'passed' }}`, 14 days), and none after a failure;
  - the identity phase's duration.
- **The keys** (line 20), checked the same way:
  - the `SECRET_KEY` is masked and written to a file;
  - the RSA key, 2048 bits, is written by Python with `os.O_EXCL` and mode `0o600`, never put in a variable or printed;
  - both are in the protected directory and removed with it.
- **One gap,** filled by 2.3: the policy does not yet say what the log shows after a failed check. Since C2 it shows counts only, and the governing text should say so.

**The two mapping texts: accurate, with C2.8's sentence in both** ("passes allauth's own checks, its signature first, but carries"). Also checked:
- the data model carries C1.3's email-change sentence;
- every statement on identities, sign-up, verification, sessions, tokens, revocation and personal data matches the brief and the code at `6da8061`;
- the pinned specification's hashes still hold. allauth's spec builder varies only on the clients, the sign-up fields and the routes (`headless/spec/internal/schema.py`), not on the rate limits or the reauthentication setting.
- **Each cites "the SV1 brief, revision 3",** although each carries words from revisions 4 and 5. 2.2 corrects this.

**The workflow changes: as described, inside the Database proof checks job.**
- **C1.4:**
  - `identity_scan.py` reads the job's values from its protected directory: the identity `SECRET_KEY`, both markers, the superuser's password, the passfile's passwords and each line of the signing key;
  - it looks for the same values in the log and in the results JSON, the JSON's decoded strings included;
  - it requires the suite's own clean scan;
  - on a refusal it removes the JSON;
  - it prints counts and file names only, and imports only the standard library.
- **C2.6:**
  - after a failed check the step prints a line count and pass/fail counts, never a line of the output;
  - the step still exits 1, and `scan` stays unset, so nothing uploads.
- **The gate:** it fails closed on anything but a successful classification (DM-49).

**C2.1 to C2.8 as applied: confirmed** (DM-48's deferred row can close).
- **Word for word**, checked by script:
  - C2.1, C2.2, C2.3 and C2.6 in the brief's D3, acceptance check 11 and D10;
  - C2.4 in the record's C2 section;
  - C2.5 in `mail_forbidden_found`'s docstring;
  - C2.7 in the brief, and as `test_the_request_reaches_only_allauths_authentication` (`test_identity_offline.py:545`);
  - C2.8's six replacements, in the brief, `strategy.py`, the data model, the contract, the record and the API test's comment.
- **The replaced texts are gone.** Each remaining "in allauth's order" is a quotation inside a correction's instructions or notes.
- **In the code:**
  - `"ACCOUNT_RATE_LIMITS": {"change_password": "5/300s/user"}` (`conf.py:78`);
  - `ratelimit.password_change` (`identity_cases.py:1507`), using the limiter's moved clock;
  - the record's D3 facts row is corrected (N-6).
- **CI:** the PR run on `ffcdd41`, 42709897206, has all eight jobs `success` and the gate `success`. The gate succeeds only when every application job matches a full classification, so this is a full-scope pass.

**What the sweep found, and 2.1.** `docs/testing/p11-deferred-acceptance.md`, in SV1's entry, lists under "Limits":

> **No reauthentication:** an email change needs none (`ACCOUNT_REAUTHENTICATION_REQUIRED` keeps its default, off).

- **Since C1 this is false:** `conf.py` sets the setting on, and acceptance check 13 proves it.
- **The line dates from SV1's records** (`157c1f6`). C1's integration added C1.5 to the same plan but left this line.
- **The effect:** P11 might wire the app without allauth's `reauthenticate` flow. The server still refuses the change, so the cost is a broken screen, not a weaker boundary.
- **The same entry's list of what SV1 proves** names neither C1's reauthentication case nor C2's password-change limit.

**2.1 — P11's plan** (`docs/testing/p11-deferred-acceptance.md`, SV1's entry):
- Replace "  - the failed-sign-in rate limit;" with:

  > ```
  >   - the rate limits: the failed-sign-in limit, and the password change's own, 5 per 300 seconds (acceptance check 11; correction C2);
  >   - reauthentication before an address is added, removed or made primary: the password again within 300 seconds, in the same session (acceptance check 13; correction C1). The app answers allauth's `reauthenticate` flow there (P11's client wiring);
  > ```

- Delete the line "  - **No reauthentication:** an email change needs none (`ACCOUNT_REAUTHENTICATION_REQUIRED` keeps its default, off)."

**2.2 — The citations:**
- In `docs/architecture/data-model.md`, `docs/architecture/production-contracts.md` and `docs/testing/p11-deferred-acceptance.md`, replace "the [SV1 brief](../planning/sv1-identity.md), revision 3" with "the [SV1 brief](../planning/sv1-identity.md), revision 5".
- If the brief's revision changes before the final head, all three follow it.

**2.3 — The CI policy** (`docs/operations/ci-and-branch-policy.md`). Replace "that none of its secrets is in the suite's output or its results JSON before that output is shown, and a second identity run's refusal" with:

> that none of its secrets is in the suite's output or its results JSON before that output is shown (after a failed check the log shows counts only, never a line of that output; SV1's correction C2, DM-48 C2.6), and a second identity run's refusal

**The answer:** SV1's PR may merge on these texts, given item 1's answer, once:
- 1.1 and 2.1 to 2.3 are applied as written, with 1.2's carry recorded;
- step 7 holds: the PR run on the final head has passed all eight jobs with `Application checks passed`, and Codex has read that head.

## 5. One of my own misses

- **What I missed:** in DM-48 section 6 I confirmed C1.1 to C1.6 as applied. I checked that their words were present, but I did not sweep the living documents for the state C1 replaced, and P11's plan still said that no reauthentication is needed.
- **Who else missed it:** the manager's supersession sweep at C1's integration missed it too.
- **Prevention:** when I confirm a correction as applied, I also `git grep` the living documents for the replaced state, here the setting's old value and "no reauthentication".

## 6. The notes (no verdict asked)

- **N-2:** it rides 1.2's carry.
- **N-3:** agreed as a claim limit. The guard catches plausible forms, not code written to evade it.
- **N-5:** agreed. The branch has no pipe, and the review also ran it under the job's shell.
- **N-4 and N-6:** both corrected in place. I read both corrections: 7 subtests and one plain assertion; the facts row noting that C1 turns reauthentication on.
- **AM10-08:** its prevention worked. The Branches bullet names `ffcdd41`, the commit the status names.

## 7. Notion (read-only, at about 22:25 UTC; the pages as of 22:13 UTC)

What I read: the parts named here, not the whole of either large page.

- **Implementation Control:**
  - **The status** says the page was last matched at `ffcdd41`, with its message.
  - **The Branches bullet** lists six branches, from a 22:12 UTC listing, and gives the manager branch as "`ffcdd41` at this sync". Every hash matches my `git ls-remote` at 22:25 UTC:
    - `main` (`da92f1f`);
    - the manager branch (`ffcdd41`);
    - `claude/dev-manager` (`21882dd`);
    - `claude/hopeful-cerf-kc91xx` (`157c1f6`);
    - `claude/stoic-franklin-ief71e` (`96dc3e2`);
    - `claude/trusting-goldberg-e4ogat` (`080c9a9`).
- **The Dev Manager page:** both rows match the review log:
  - DM-49's row: the report pinned at `cf03cde`, answered at `21882dd`, merged at `e438c8f`, 1.1 applied at `cf03cde`;
  - DM-50's row: the consultation at `ffcdd41`, "Awaited".
- **The Work Register:** SV1 is In progress. Its Next Action describes DM-50 as the consultation does, and its Evidence link is pinned at `ffcdd41`.
  - Its "CI green on its head" was written while the PR run on `ffcdd41` was running. That run has since passed all eight jobs, so the words now hold.
- The repository wins (OD-27).

## 8. Where each item goes

| Item | Goes to |
|---|---|
| 1.1 | The SV1 record, "Delta review of correction C2", N-1's disposition |
| 1.2 | The carried-items file, "Carried to SV2" |
| 2.1 | P11's plan, SV1's entry |
| 2.2 | The data model, the contract and P11's plan |
| 2.3 | The CI policy |
| C2.1 to C2.8 | DM-48's deferred row closes |
| The merge | Step 7: a complete PR run on the final head, and Codex's read of it |
| Confirming 1.1 and 2.1 to 2.3 as applied | My next consultation |

Status: complete
