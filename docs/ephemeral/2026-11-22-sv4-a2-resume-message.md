# SV4 A2 resume message — option (a), and the scope it adds

- **Owner:** App Manager 13. Nathan pastes this into A2's own session (branch `claude/dazzling-hamilton-ocxuu3`, code head `e3f66a3`), which stopped on its run of record and waits for the manager's choice.
- **Revision 1, 22 November 2026.**
- **Brief:** [SV4](../planning/sv4-chat-notifications.md), revision 9.
- **Model and reasoning setting:** no new reading. This message continues the session A2's prompt started (its reading: TypeSafe v8.2, Opus 5.5 at extra high); it starts no new session.
- **Environment:** the session's own, `Glow App - No Stream`.
- **Deletion condition:** prune with A2's prompt, after A2's pull request merges and its receipt is recorded.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**From App Manager 13 to the A2 session: option (a). Resume.**

Your stop was right, and your report checked out: run 45018516461 failed only in Database proof checks (discovery), at SV3's `match.no_route_creates_a_match`, because `GET api/v1/matches` is a route the case did not list. My sweep for your prompt read the earlier tests, not the earlier suites' database cases; that miss is mine (AM13-04).

**The decision: (a).** The match list stays at `GET api/v1/matches`, beside the match read, as the brief's D9 puts it. The case's purpose, that no route creates a match, still holds with a read there. The brief's revision 9 (`git fetch origin claude/magical-wozniak-yfmmx2`; the brief at `<RECORDS_COMMIT>`) adds to your owned paths:

1. **`proofs/postgres-ordering/glow_ordering_proof/interaction_cases.py`, the case `match.no_route_creates_a_match` only:**
   - its `stage_b` set gains `("api/v1/matches", "MatchListView")`, or the view's name as you built it, with a comment naming SV4 A2 (D9);
   - its POST at the matches path now expects 405 where it expected 404, with the expectation's message saying the path takes no POST. Its "no match written" stays, and so does its check that no request DTO names a match. If that check fails with your view (a `definition` naming "match"), stop and report;
   - its docstring and its return line, only where they count or name the routes;
   - no other change to the file.
2. **`docs/operations/ci-and-branch-policy.md`, lines 5 and 23,** besides the paragraph you own: each count or list of the database jobs gains the chat job, and nothing else changes.

**Then:**
- **Sweep the database cases.** Search every earlier suite's cases for another pin of the routes, the URL configuration, the suites, the jobs or a count that A2 extends, and record what you find. Handle any hit the same way (only A2's entry added, every earlier assertion kept), or stop and report if it needs more.
- **Your new code commit's Foundation run is the run of record.** Run 45018516461 is superseded. Record it as the first run, failed, with its cause.
- **Then your records commit,** with section "A2" from your draft. Add what this message changed:
  - the stop and its cause;
  - the decision (a);
  - the case's change, with its reversal (remove `MatchListView` from the case's set and the case fails);
  - the database-case sweep;
  - the CI policy's lines.
- **Everything else in your prompt holds:** the stop rule, the push rule, the checks and the final report's form. Your final message names your new code head, the records head and the new run of record.

**Recorded for the exact-head review, not for you to change:**
- the duplicated list logic in `glow_chat/route_reads.py`, kept because `reads.py` stayed unchanged;
- no `TransactionTestCase` class for the views;
- the match list leaving out a match whose other member asked for deletion, while SV3's match read by ID still shows it `active`.

Name each again in your record's "Limits and deviations".
