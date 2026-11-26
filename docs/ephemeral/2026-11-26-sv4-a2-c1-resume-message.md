# SV4 A2-C1 resume message — one more case named, and the session resumes

- **Owner:** App Manager 13. Nathan pastes this into A2-C1's own session (branch `claude/affectionate-sagan-r916ba`, local only, at `4a72036` with its changes uncommitted), which stopped at its stop rule and waits for the manager's decision.
- **Revision 1, 26 November 2026.**
- **Prompt:** [A2-C1's prompt](2026-11-26-sv4-a2-c1-correction-prompt.md), revision 1, from `4a72036`. **Brief:** [SV4](../planning/sv4-chat-notifications.md), revision 10; its owned paths already cover `chat_cases.py`, so no revision is needed.
- **Model and reasoning setting:** no new reading. This message continues the session A2-C1's prompt started (its reading: TypeSafe v8.2, Opus 5.5 at high); it starts no new session.
- **Environment:** the session's own, `Glow App - No Stream`.
- **The Dev Manager's read:** none before it runs. The decision changes one case so that it reads a value as every other case does; it changes no design, contract or assertion. It goes on the list for A2's pre-merge read.
- **Deletion condition:** prune with A2-C1's prompt, after A2's pull request (PR59) merges and its receipt is recorded.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**From App Manager 13 to the A2-C1 session: resume.** This message is at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2` (`docs/ephemeral/2026-11-26-sv4-a2-c1-resume-message.md`).

Your stop was right, and your diagnosis checks out:
- `transactions.non_atomic_requests` (`chat_cases.py`) builds its send's body with `ctx.message(one, match.id)` after it sets `ATOMIC_REQUESTS`;
- `message()` reads the version through `match_version`, that is, through SV3's match read;
- SV3's view refuses inside `ATOMIC_REQUESTS` (503, `transaction_open`), so the old fallback let the case send a guessed version 1. That is A2R-8's defect, which item 6 removes.

My prompt's item 6 took the fallback without a sweep of its callers; that miss is mine (AM13-07). The sweep since: in the chat suite, `match_version` is read only through `ChatContext.message` (when no `expected` is given) and by case 2. Your run shows only this case relied on the fallback.

**The decision.**
1. **`transactions.non_atomic_requests` joins item 6's list,** for one change only: the send's body is built before `ATOMIC_REQUESTS` is turned on, so its version comes from SV3's match read outside the block. Every expectation, the order of the requests inside the block, and the rest of the case stay as they are. Record it under the earlier cases changed, with its reason.
2. **Your own list case:** the own-account check's expected answer is `not_found` (404). The list refuses `account_not_active` through `error_for`, as A1's reads do, and item 4 named no code for that check. Correct your case's expectation. Record that this check is reached only by test data, since every writer that takes an account out of `active` also moves its epoch, so the session check refuses first.
3. **If another case fails on the removed fallback,** handle it the same way: read the version outside whatever state refuses the match read, with no expectation changed, and record it. Anything more is a stop, as the prompt says.

**Then finish as the prompt says,** in its order:
- the full API suite, with Ruff and format on every file you changed, the API test file among them, and mypy;
- the proof's offline tests, Ruff and mypy;
- the chat suite locally under D4 (iteration), every case passing;
- every reversal in section 3;
- the trusted classifier and the diff checks;
- then your code commit and push, the run of record, and your records commit with section "A2-C1". The record names this message, the stop and its cause, the decision, and the case's change with its reversal: put the body's build back inside the block, and the case fails as it did.

**On committing now:** you may commit locally at any time. Push only as the push rule says: your code commit once the checks pass, then nothing until its Foundation run has finished. That push also answers the stop hook. If the container is reclaimed before you push, say so in your report, with what was lost.

**Everything else in the prompt holds:** the owned paths, the stop rule, the push rule, the checks and the final report's form. Stop the Docker daemon you started when you have finished with it.
