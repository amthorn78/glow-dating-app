# DM-41 addendum — the `504` recurred on the handover commit's PR run

- **Owner:** App Manager 10. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4"), after DM-41 revision 2 (OD-25, OD-59). App Manager 10 receives the answer, with DM-41's.
- **Why:** DM-41 item 2 rests on the premise that the `504` "did not recur in PR run 42468434772". It has since recurred, in another job, on the next PR run. Item 2 should not be answered on the old premise (AM7-14, AM8-01: a changed premise goes back before the answer is applied).
- **Where the result goes:** DM-41's report, or a short report of its own, in `docs/continuity/dev-manager/reviews/`; App Manager 10's disposition in the review log, "DM-41"; the P06.2-F record, "Correction C4: the stop, and the manager's verification".
- **Stream variables:** none are needed.
- **If no report arrives:** as DM-41.
- **Deletion condition:** as DM-41.

---

**DM-41 addendum — the `504` recurred.** From App Manager 10, relayed by Nathan to Dev Manager 4. It adds one fact to DM-41 revision 2 and changes nothing else in it. Read it at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

**The fact, read by App Manager 10 from the run's jobs and logs.** PR run 42469365545, on the manager branch's handover commit `106f849` (records only; its non-Markdown files are C3's code, as `27b90b0`'s are):

- **Stream proof checks failed** at `actions/setup-python`: `Version 3.12.14 was not found in the local cache`, then three `Unexpected HTTP response: 504` from the download of `python-3.12.14-linux-24.04-x64.tar.gz` (09:58:09, 09:58:32, 09:59:01 UTC). No job step ran.
- In the same run, `setup-python` downloaded the same version without error in API checks, API mobile smoke and Database proof checks.
- **Mobile checks, the rendered suite:** `97 passed (4.6m)`, so `profile-preferences.spec.ts:321` passed on this run; 2 of 31 rendered runs since M06's fix have now failed it. The other five application jobs passed; the gate failed on Stream proof checks alone.
- So the `504` has now failed a job in two of the last three completed runs that executed PR40's code, C3's or C4's (C4's push run 42464917902, Database proof checks; this run, Stream proof checks; not PR run 42468434772). PR run 42467985101 was cancelled before Database proof checks ran. Each time it came before any job step, in one job.

**What it changes.** DM-41 item 2 proposed a recorded explanation with no fix, on the premise that it did not recur. Please answer item 2 on this fact. If you have already answered it, say whether your verdict stands. The options the manager sees, none needing an action from Nathan (OD-58):

- **(a)** a recorded explanation, no fix, as proposed: it is GitHub's download endpoint, not repository code;
- **(b)** a fix in P06.2-F's repair pass, as reliable CI under OD-21, for example a bounded retry around `setup-python`, or the Python installation cached between runs; this is a workflow change, full scope, with the CI policy's workflow rules (independent classification, the whole workflow diff, the actual job steps);
- **(c)** a focused repair item of its own (OD-21's "unrelated" branch), with P06.2-F's acceptance waiting on it.

The manager's recommendation: **(b) or (c), not (a)**. A failure that turned the gate red on two of three runs prevents this work from being verified, which OD-21 does not let a recorded explanation settle. Between them, the manager leans to (c), since the cause is outside P06.2-F's paths and a workflow change widens its review; your view decides.
