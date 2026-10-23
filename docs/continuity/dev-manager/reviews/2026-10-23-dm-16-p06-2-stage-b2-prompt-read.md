# DM-16 — Stage B2's prompt, brief revision 4 and the governing changes since DM-14

- **Consultation:** DM-16, revision 1, from App Manager 6, relayed by Nathan (OD-25). The consultation names the path `2026-10-22-dm-16-…`; this file is dated the day I wrote it, 23 October, as the consultation asks.
- **Reviewer:** Dev Manager 2, `session_015DxVkL8PXn2YaauE6RdSWN`, branch `claude/dev-manager`.
- **Commit read:** `2f62b1eeddb1457654f969bc222bf99a627f1b78`, the head of `claude/magical-wozniak-yfmmx2` when I fetched it (no PR yet). The code is read at `main`, `3272eed3d6b07d3215c6c667000082b6254eea69`. **This read covers `2f62b1e`** (DM-03 G2).
- **Environment (names only):** `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` are present, never read or used. No HDE name is present. I called no provider, database, HDE or Railway, and ran no code.

## 1. What I read

**At `2f62b1e`:**

- the brief's diff since `3272eed`, whole: the Status line, "B2's design points" a to h, and "The database job's time margin";
- Stage B2's prompt, revision 1, all 130 lines;
- the governing diff `da9fac6..2f62b1e` over `AGENTS.md`, `CLAUDE.md`, `docs/pf-canon`, the manager workflow, the charter and the CI policy. Only the manager workflow and the CI policy changed. I also read the diff of `docs/planning/start-prompts/next-manager.md` since `3272eed`;
- OD-41 in the register; OD-34's row; AM6-02, both its row and its section, in the mistakes log;
- the evidence record's "Manager verification of Stage B1-C1", "Exact-head review of Stage B1-C1" and "Stage B1's merge receipt";
- the DM-16 consultation, the review log's DM-15 and DM-16 rows, and the handoff's "Now", checkpoint and next actions.

**At `3272eed`:**

- `services/api/glow_domain/chat_provider.py` (the port and `error_code`), `chat_provider_fixtures.py` (the six operations) and `chat_tokens.py`, whole;
- `services/api/requirements.in`, `requirements-dev.in` and the head of `dependency-inventory.json`;
- `proofs/stream-chat/glow_stream_proof/server_api.py`, whole;
- `guard.py`: its docstring, `refusal` and `_reason`, and the ownership scopes;
- `cli.py`: `cmd_baseline`, `cmd_run` and the command list;
- `stops.py`, and the stop types in `usage.py`;
- `app_send.py`;
- the harness's `requirements.lock`, for the resolved set;
- `PREFIX_ROOT`;
- the workflow's job timeouts.

**For DM-14's words:** DM-14's report, items 1 and 2, compared with the manager workflow at `9f6f6ab` and `3272eed`.

**Notion, read-only, 23 October:**

- *Implementation Control*, including its operating procedure;
- the Work Register's P06.2 row;
- the owner-direction register copy;
- *Dev Manager — reviews and approvals*.

## 2. Summary verdict

| Item | Verdict |
|---|---|
| 1 The prompt's authority and safety | **Approved with conditions 1.1 to 1.5.** Nothing too wide. Four guards are missing: a configuration check in code, a final `baseline`, a rerun rule, and `.env` files. One condition goes to B2's review prompt |
| 2 The dependency and the seal | **Approved with conditions 2.1 to 2.4.** Pin `getstream` in the development scope, not the runtime lock, until P11 wires it |
| 3 What the adapter sends, and the signer | **Approved with conditions 3.1 to 3.4.** `iat` is never later than the truncated issue time. A hand-signed token is **pre-approved** as a fallback, so the session need not stop on it |
| 4 The contract suite and the conformance rows | **Approved with conditions 4.1 to 4.7.** Most important: the adapter must not turn the harness's stop exceptions into a Glow code, and a repeated operation must not undo a removal, a deactivation or a revocation. The run's IDs are right |
| 5 F3 and CX6's database half | **(i), with conditions 5.1 to 5.3** |
| 6 The database job's time margin | **Raise `timeout-minutes` from 20 to 30 in B2's PR**, budgets unchanged, with the CI policy's words in 6.1 |
| 7 The governing changes | **OD-41's sentences: approved.** DM-14's words: **confirmed** as applied word for word. **Step 3's TypeSafe sentence: approved with conditions 7.1 and 7.2** (record Nathan's direction as an OD row; the outside reference) |
| 8 Notion | **Matches `2f62b1e`, apart from three items**: the Work Register row and the operating procedure still name TypeSafe v6; the DM page drops part of DM-15's verdict |

**Revision 1 does not run as it is.** A revision 2 of the prompt and brief revision 4 that apply sections 3 to 5's conditions as written need no further read (G2). The same holds for the governing words in item 7. No item is Nathan's.

## 3. Findings

### Item 1 — The prompt's authority and safety: approved with conditions

The prompt does several things right:

- It authorizes exactly what B2 needs: the three names in `Glow app`, read only by the harness's credential loader; Chat on application 1729640; no configuration change at Stream; `baseline` first; `verify-clean` before and after; cleanup of the run's own data.
- Its "never" list, start gate (AM5-15), clean environment, push rule (AM5-14), stop on a departure and fix-here classes are the ones earlier live prompts used, with DM-04's and DM-05's lessons.
- Nothing in it is too wide.

Four things are missing, and one belongs to the review that follows:

- **1.1 The configuration check in code, not only in the session's reading.** `cmd_baseline` prints the two difference counts and always exits 0 (`cli.py:278-295`). The stop on a non-zero count therefore rests on the session reading a line. Before its first changing request, `conformance` itself runs `configuration.verify` and `products.verify` on a fresh snapshot, and refuses to start unless both are 0. An offline test covers each refusal.
- **1.2 A closing `baseline`.** After `cleanup --apply` (if needed) and `verify-clean`, `baseline` runs again, and both counts are 0. Item 4 sends requests no earlier run made, so the run must show the application's configuration is unchanged at its end too.
- **1.3 A rerun rule.** The prompt says "`conformance`, once", but the run plan keeps a budget for one rerun. One rerun is allowed only when all of these hold:
  - the first run stopped on something other than a charge or limit signal;
  - its cleanup and `verify-clean` passed;
  - the cause is recorded;
  - the fix, if any, is offline and its checks pass.

  Otherwise, and after a second stop, the session stops and reports.
- **1.4 No `.env` file.** `getstream` 6.1.0 brings `python-dotenv` and `pydantic-settings` (the harness's lock). Either can read an environment file. The start check confirms that no `.env` exists in the checkout root, `services/api` or `proofs/stream-chat`, and reports any that does, without reading it. The session records, from the SDK's source at 6.1.0, whether importing `getstream` or constructing `Stream` reads the environment or a `.env` file.
- **1.5 For B2's exact-head review prompt (the manager's).** Codex's security review is gone (OD-41). The exact-head session is now the only security reading of B2, the first stage to add a credentialed dependency and live code. Its prompt names these as explicit security focus areas:
  - the new resolved set and its hashes;
  - every path the secret takes, the signer included;
  - the adapter's exception boundary (4.1);
  - the recorded transport's contents (4.2);
  - the guard's coverage of each new request (4.3).

### Item 2 — The dependency and the seal: approved with conditions

**The pin belongs in development scope until P11.**

- `services/api/requirements.in` is the runtime set (Django, DRF, gunicorn). `requirements.lock` is what a deployed API installs.
- `getstream` 6.1.0 resolves to about 28 packages in the harness, including `requests`, `urllib3`, `protobuf`, `twirp`, `pyee`, `structlog`, `pydantic`, `pydantic-settings` and `python-dotenv`. Most are new to the API.
- B2 uses the adapter only in tests and in the conformance run. The prompt itself says "No app runtime gains … a live provider."
- Putting the pin in the runtime lock would ship that whole set in every runtime image for nothing, before P11 decides how the runtime builds a client.

The conditions:

- **2.1 Scope.** The exact pin goes in `services/api/requirements-dev.in`, and so into `requirements-dev.lock`. `requirements.in` and `requirements.lock` stay unchanged. `dependency-inventory.json` marks the new packages `"scope": "development"`, with their licences as the inventory records them. P11 moves the pin to runtime when it wires the client. The prompt's item 1 and its owned paths change to match, and the brief's point b says so. DM-13 9.1's "the API's lock" meant the API's own lock, as against the harness's; the development lock is that lock.
- **2.2 One SDK under test.** A pin test fails unless `getstream` and `httpx` have the same version and the same set of hashes in the API's development lock as in the harness's `requirements.lock`. If the signer uses `pyjwt` directly (3.3), the test covers it too. The conformance run executes the adapter on the harness's installed SDK, so this is what lets the run vouch for the API's pin. The session reports any other shared package whose version differs.
- **2.3 The seal.** The sealed-runtime test, as the prompt extends it, fails if the runtime settings or URL configuration import the adapter or `getstream`. Add: the adapter module imports nothing from Django, `glow_persistence` or `glow_chat`, only the port, the token module and the SDK. That keeps it outside every runtime import path by construction, and lets the harness import it (4.6).
- **2.4 No client, no loader.** The adapter never calls `Stream(...)`, `Stream.from_env()` or any settings loader, and reads no environment variable. It holds only the client it is given. The API's tests build their client with explicit dummy values under `env -i`.

### Item 3 — What the adapter sends, and the signer: approved with conditions

Point d is right. Item 4 adds tests that make it checkable. On the signer:

- **3.1 `iat` is never later than the truncated issue time.** The rule that matters for F1 is one-sided. A token issued before a bump stays revocable only if its `iat` is below the cut-off sent, so `iat` may never be later than `floor(issued_at)`. An earlier `iat` only revokes more, at the cost of a client refetching a token. So:
  - `iat` is the grant's `issued_at` truncated to the second;
  - if Stream refuses a token whose `iat` is the current second (clock skew between the issuing host and Stream), the signer may subtract a fixed, recorded number of whole seconds, never more than 5, as the harness's own tokens do (`iat: now - 5`). The session records which, with the live evidence.
- **3.2 `exp`.** `exp` is the grant's `expires_at` truncated to the second, never later. It is derived from the grant, not from the SDK's own clock. Today `ServerApi.user_token` passes `expiration=ttl_seconds`, which counts from the SDK's clock.
- **3.3 The fallback is pre-approved.** If `getstream` 6.1.0 cannot set `iat` (or `exp`) from the grant, the session does not stop. The signer signs the token itself, under these conditions:
  - claims exactly `user_id`, `iat` and `exp`, with the header `{"alg": "HS256", "typ": "JWT"}`;
  - `pyjwt` at the version `getstream` resolves, added to `requirements-dev.in` as the one other pin, under 2.2's test;
  - the key taken only from the injected client's own secret, or from an injected signing function. Never from the environment, a file or a field the adapter stores. Never logged;
  - an offline test decodes the signer's token and the SDK's token for the same user, and shows the same header and the same claim names;
  - a token with a wrong key fails verification;
  - the live row "a token from the signer is accepted" shows Stream accepts it.

  This is no new trust. The harness already signs its expired and wrong-key tokens this way (`server_api.py:250-265`). A stop here would cost a full consultation round on a likely outcome.
- **3.4 The cut-off value.** The revocation row, and the adapter, send `glow_domain.chat_tokens.revocation_cutoff_sent(cutoff)` as delivery gives it. Neither reimplements it. The row "a cut-off at an exact second is sent one second later" uses that function's output.

### Item 4 — The contract suite and the conformance rows: approved with conditions

**The run's IDs are right.** The run's prefix plus `secrets.token_hex(16)` contains the prefix, so `RunScope` and `PrefixScope` own it. The guard, `verify-clean` and `cleanup --apply` stay unchanged.

- The prefix is `p061i1-` plus ten digits, 17 characters. With 32 hexadecimal characters, the IDs come to 49, under Stream's 64-character limit for a channel ID.
- **The adapter must enforce no ID shape** (for example "exactly 32 hexadecimal characters"). A shape check would force a test-only branch for these IDs, which DM-13 2.1 forbids.

**The rows cover the port contract, the token rules and the provider halves of F3 and CX6.** Seven conditions make them sufficient:

- **4.1 The exception boundary.** This is the most important one.
  - The harness raises `GuardRefused`, `RunStopped` and `GuardrailStop`, all subclasses of `RuntimeError`, from inside the HTTP client's hooks (`server_api.py:127-151`; `stops.py`), so they surface through the adapter's SDK calls.
  - An adapter that maps "every Stream error" with a broad `except` would turn a guard refusal or a charge signal into `provider_unavailable`, which delivery retries.
  - So the adapter maps only the SDK's own API error and `httpx`'s transport errors and timeouts to Glow codes. Every other exception propagates unchanged.
  - Offline tests: a client whose hook raises each of the three stop types, and an unrelated `RuntimeError`, for each of the six operations. Each propagates unchanged.
- **4.2 What is sent, in code.**
  - An offline test asserts each operation's method, path and exact JSON keys on the recorded transport:
    - provisioning: `id` only, no `role`;
    - creation: type `glow-match`, `members` only;
    - send: the message's `id`, `text` and its sender;
    - removal: the two members;
    - deactivation and revocation: the user and the cut-off.
  - Any `name`, `image`, `role`, custom or `data` key fails it.
  - The recordings hold no `api_key` query parameter and no `Authorization` or `stream-auth-type` header. A test fails if one does.
  - The recordings are written by hand from Stream's documented responses, or from P06.1's redacted results. They are not captured with the credentials.
- **4.3 Every request passes the guard.** An offline test installs a guard that refuses everything. Each of the six operations must raise `GuardRefused` before the transport sees a request. This shows that every call the adapter makes goes through the one hooked client, including SDK calls P06.1 never used.
- **4.4 A repeat never undoes a revocation.** These are the rows the fixture cannot show:
  - **Provisioning never changes an existing user.** It never resets fields, never reactivates and never clears a token cut-off. Live: provision, revoke, provision again, and the revoked token is still refused. Deactivate, provision again, and the user is still deactivated. Stream's user upsert replaces the user object, so if it would undo either, the adapter uses a create-only path, or reads first and creates only when absent. The session records which.
  - **Deactivation and revocation never create a user**, never through an upsert. On a user Stream does not have, they give `member_unavailable` (the F3 and CX6 rows).
  - **Channel creation repeated after the removal does not re-add the members.** Live, then read back. If Stream would re-add them, the adapter must not send the members on an existing channel, and the session reports it. A P11 reconciliation that re-runs creation must never undo a block.
- **4.5 Codes from status and number.**
  - Each mapping to `ERROR_CODES` is decided by HTTP status and Stream's numeric `code`.
  - Where Stream uses one number for several causes, the adapter may test the message's text in memory, never storing, returning or logging it.
  - The record lists each mapping with the live row that shows it.
- **4.6 The import route.** The harness has never imported the API's code. `conformance` adds `services/api` to the import path for that command only, and imports the adapter and `glow_domain`'s port and token modules. Under 2.3 these load without Django. A harness test shows the import in the harness's own environment.
- **4.7 One more contract row.** A send whose sender is no longer a member, after the removal. The fixture gives `member_unavailable` (`chat_provider_fixtures.py`, `send_message`). Stream's server-side send may not check membership. Record what Stream answers. If it accepts, that is a reported difference, not a failure: Glow's own send checks refuse it first (D5). P11's worker must know.

### Item 5 — F3 and CX6's database half: (i), with conditions

**I choose (i).** B1's database job shows the mark on the fixture. B2 shows live that Stream gives the fixture's codes for the causes delivery acts on, and that removal works on a channel whose creation succeeded at Stream.

**Why not (ii).** It would put the Stream secret and a database connection in one session. Every prompt so far has kept them apart, and the proof's marker and used-database guard were built for sessions with no credentials. It would also compose delivery with a harness whose stop exceptions are `RuntimeError`s: delivery's `except Exception` (`glow_chat/delivery.py`, `_deliver`) maps anything to `provider_unavailable` and retries, so a guard refusal or a charge signal would become a retry loop inside the live run. (ii) proves little beyond what the composition does. Delivery's marking was shown on the codes in B1; B2 shows the adapter returns those codes.

Conditions:

- **5.1** Brief revision 4 records that DM-16 replaces DM-14 item 4's "the conformance run shows that state after an injected terminal failure" with (i), and why.
- **5.2** The composition holds only if the codes match. The live rows show:
  - `channel_unavailable` for removal from a channel Stream does not have;
  - `member_unavailable` for deactivation, revocation and channel creation naming a user Stream does not have.

  Offline, a transport failure and a timeout give `provider_unavailable`. If Stream gives a different code for any of these causes, that difference blocks B2's merge until it is dispositioned. It is not merely reported.
- **5.3** The P11 plan's DB06 provider half names the residual: delivery composed with the Stream adapter, against a database, under the deployed worker. P11 also checks delivery's exception handling against the adapter's errors.

### Item 6 — The database job's time margin: raise to 30 minutes in B2's PR

**Why 30 minutes:**

- The race budgets (`budget.MAX_SECONDS` = 30 per race) define what the races prove. The slowest race used 29.7 s of its 30, so lowering the budget would change the evidence and likely fail it.
- Leaving the timeout as it is risks a timed-out run on a PR that did not cause it, and OD-21 makes that a failure to diagnose, not a rerun.
- At about 18.5 to 19.5 minutes in the worst case, 20 leaves no margin; 30 leaves a third.
- A runaway job costs at most 10 more minutes.

**6.1 The words.**

- **The prompt's `<WORKFLOW_LINE>`:** "`.github/workflows/foundation.yml`: the `database` job's `timeout-minutes` only, from 20 to 30".
- **The CI policy:** in the sentence that begins "The one database is P06.DB's", after "checks no proof container remains" and before its full stop, add:

  > "; the job's timeout is 30 minutes (DM-16), and its race budgets, which define the evidence, are unchanged: a run of record that takes more than 24 minutes is a finding to diagnose before acceptance (OD-21)".
- **The brief's "time margin" paragraph:** "if a later run nears the timeout" becomes "more than 24 minutes".

This is a workflow change, so the manager reads the whole workflow diff and runs full checks (the CI policy's workflow rule). Each later run of record records the database job's duration.

### Item 7 — The governing changes

**DM-14's words: confirmed.** Step 3's OD-40 bullet ends with DM-14 item 1's clause, and step 5's AM6-01 bullet is DM-14 item 2's text. Both are word for word at `9f6f6ab` and at `3272eed`.

**OD-41's sentences: approved as written.** Step 7's checklist line, its "Wait for Codex" bullet and the CI policy's sentence say the same thing, in Nathan's terms:

- Codex's code review, completed on the final head, is the Codex check;
- the exact-head code and security review sessions are unchanged.

*Consider,* in step 7's "Wait for Codex" bullet, after "unchanged": "; the exact-head review prompt for a full-scope PR names its security focus areas explicitly, since it is now the only security reading". 1.5 applies this to B2.

**Step 3's TypeSafe sentence: approved with conditions.** The update to request v8.2 and four models is right, and the start procedure's line matches it. Two things:

- **7.1 Record Nathan's direction.**
  - Nathan's words, *"you can fix the typesafe skill version in the workflow"* (22 October, in App Manager 6's session), are recorded only in the DM-16 consultation, an ephemeral file.
  - They change what OD-33 and OD-34 set: request v6, and two models.
  - Add a register row, OD-42, with his words. It records the skill's move to request v8.2 with four models, and marks OD-34's "request v6" as updated by OD-42.
  - In the sentence, replace "and Nathan corrected this sentence on 22 October" with "at Nathan's direction (22 October 2026, OD-42)". He directed the fix; the manager wrote it.
- **7.2 The outside reference.** "v8.2's rule and acceptance are recorded in the Glow HD engine repository (`docs/ephemeral/typesafe-ladder/four-model-20261016/`)" points a governing sentence at a folder that repository's own rules may prune. Do one of these:
  - name that repository and a commit SHA;
  - or say that the installed skill carries v8.2's request and rule, and give the HD engine record as history.

  I cannot read that repository from here (section 7).

### Item 8 — Notion: matches `2f62b1e`, apart from three items

- ***Implementation Control*:**
  - It is matched to `2f62b1e`: B2's prompt, revision 1 (Fable 5.1 at max), brief revision 4, DM-16, and B1's merge receipt.
  - The operating procedure's pre-merge bullet takes OD-41's words.
  - **Mismatch:** the procedure's "Model and reasoning setting" bullet still says "(request v6): a model (Opus 5.5 or Fable 5.1)". The workflow at `2f62b1e` says v8.2 with four models.
  - Its status's "(Nathan's correction, 22 October)" changes with 7.1.
- **The Work Register's P06.2 row** is "In progress" and matches through B1's merge and OD-41. **Mismatch:** it says DM-16 reads "step 3's TypeSafe v6 sentence", which at `2f62b1e` names v8.2.
- **The register copy** is matched to `3120904`. `owner-directions.md` is unchanged from `3120904` to `2f62b1e`, so it matches. OD-41's row is word for word.
- ***Dev Manager — reviews and approvals*:**
  - DM-16's row is pending, as in the review log.
  - The session row reaches DM-15 (`c748c64`, integrated at `e7cddd4`) and DM-16, "given to Nathan".
  - **Mismatch:** DM-15's verdict drops the review log's "(`iat` truncated, strict next second)" after "5.1 and 5.2".

## 4. Verdicts

| Item | Verdict |
|---|---|
| 1 | Approved with conditions 1.1 to 1.5 |
| 2 | Approved with conditions 2.1 to 2.4; the pin in development scope |
| 3 | Approved with conditions 3.1 to 3.4; the hand-signed fallback pre-approved |
| 4 | Approved with conditions 4.1 to 4.7; the IDs right |
| 5 | (i), with conditions 5.1 to 5.3 |
| 6 | 30 minutes in B2's PR, with 6.1's words |
| 7 | DM-14's words confirmed; OD-41's sentences approved; step 3's approved with 7.1 and 7.2 |
| 8 | Matches `2f62b1e`, apart from three items |

## 5. Questions for Nathan

None. 7.1 records his own direction; it asks him nothing.

## 6. Documentation to update

- **B2's prompt, revision 2:** items 1 to 4's conditions; 6.1's workflow line; 5's choice. Then score it again.
- **Brief revision 4:** points b, e, f, g and h as above; the time-margin paragraph (6.1).
- **The CI policy:** 6.1's words, at B2's integration.
- **The register:** OD-42 (7.1).
- **The manager workflow:** step 3 (7.1, 7.2); step 7's *consider*.
- **B2's exact-head review prompt:** 1.5.
- **Notion:** the three mismatches in item 8.
- **The review log:** DM-16's disposition.

## 7. Limits

- **The SDK.** `getstream` 6.1.0's source is not installed in this container, and I did not install it. Several points come from the harness's lock and code and from Stream's documented behaviour, and the session confirms them at 6.1.0:
  - whether `create_token` can take `iat`;
  - whether a user upsert replaces fields;
  - whether a channel creation on an existing channel adds members;
  - whether construction reads the environment.
- **The harness.** `proof_run.py`'s preflight, `credentials.py`, `usage.py` beyond its stop types, and `client/runner.cjs` were not read in this read.
- **The HD engine repository** (7.2) is not reachable from here.
- **Nothing was run.**
- **Notion:** the four pages in section 1 only.
- **No scoring** (OD-15).

## 8. Relay message for Nathan to paste into App Manager 6's session

> **From Dev Manager 2 to App Manager 6 (relayed by Nathan, 23 October 2026)**
>
> DM-16 is answered on `claude/dev-manager`, in `docs/continuity/dev-manager/reviews/2026-10-23-dm-16-p06-2-stage-b2-prompt-read.md` (dated the day I wrote it). My read covers `2f62b1e`, with the code at `3272eed`. No item is Nathan's.
>
> **Revision 1 does not run as it is.** A revision 2, with brief revision 4, that applies my conditions as written needs no further read. Score it again.
>
> 1. **Authority and safety: approved with conditions.**
>    - `conformance` itself refuses to start unless `configuration.verify` and `products.verify` are both 0 (`baseline` always exits 0).
>    - A closing `baseline`, both counts 0.
>    - One rerun only after a stop that is not a charge or limit signal, with cleanup and `verify-clean` passed.
>    - No `.env` file present, and the SDK's environment reading recorded.
>    - B2's exact-head review prompt names its security focus areas, since Codex's security review is gone.
> 2. **The dependency: approved with conditions.**
>    - Pin `getstream` in `requirements-dev.in` (development scope), not the runtime lock: about 28 packages, none needed at runtime before P11.
>    - A pin test: `getstream` and `httpx` identical in version and hashes to the harness's lock.
>    - The adapter imports nothing from Django, `glow_persistence` or `glow_chat`, and constructs no client or loader.
> 3. **The signer: approved with conditions.**
>    - `iat` is never later than the truncated issue time; a fixed backdate of at most 5 s is allowed if Stream needs it, recorded.
>    - `exp` comes from the grant, not the SDK's clock.
>    - If the SDK cannot set them, a hand-signed HS256 token is pre-approved (no stop): claims `user_id`, `iat` and `exp` only; `pyjwt` pinned as the one other pin; the key only from the injected client; tests against the SDK's token; live acceptance.
>    - The revocation row uses `revocation_cutoff_sent`.
> 4. **Contract and rows: approved with conditions; the IDs are right** (49 characters; no ID-shape check).
>    - The adapter maps only SDK and `httpx` errors to codes; the harness's `GuardRefused`, `RunStopped` and `GuardrailStop` propagate. Test each.
>    - The exact request keys are tested; recordings hold no `api_key` or auth header.
>    - A refuse-all guard stops all six operations before the transport sees a request.
>    - Live: re-provisioning keeps a revocation and a deactivation; deactivation and revocation never create a user; a repeated creation after removal does not re-add the members.
>    - Codes from status and number.
>    - The harness imports the adapter by path for `conformance` only.
>    - A new row: a send by a removed member; record Stream's answer.
> 5. **F3 and CX6's database half: (i).** (ii) would put the secret and a database in one session, and delivery's `except Exception` would turn a harness stop into a retry.
>    - The brief records that this replaces DM-14 item 4.
>    - A code that differs from the fixture's for those causes blocks the merge until dispositioned.
>    - P11's DB06 names the composed residual.
> 6. **Time margin: 30 minutes in B2's PR**, budgets unchanged.
>    - `<WORKFLOW_LINE>`: "`.github/workflows/foundation.yml`: the `database` job's `timeout-minutes` only, from 20 to 30".
>    - CI policy, after "checks no proof container remains" and before its full stop: "; the job's timeout is 30 minutes (DM-16), and its race budgets, which define the evidence, are unchanged: a run of record that takes more than 24 minutes is a finding to diagnose before acceptance (OD-21)".
> 7. **Governing changes.** DM-14's words confirmed word for word. OD-41's sentences approved (*consider* naming security focus in step 7). Step 3's TypeSafe sentence approved with conditions:
>    - record Nathan's "you can fix the typesafe skill version in the workflow" as OD-42, updating OD-34's v6, and write "at Nathan's direction (22 October 2026, OD-42)" in place of "Nathan corrected this sentence";
>    - pin the HD engine reference to a commit, or name the skill as the authority.
> 8. **Notion matches `2f62b1e` apart from three items:**
>    - the Work Register row says "TypeSafe v6 sentence";
>    - Implementation Control's procedure still says "request v6 … Opus 5.5 or Fable 5.1";
>    - the DM page's DM-15 verdict drops "(`iat` truncated, strict next second)".

Status: complete
