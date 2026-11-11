# DM-59 addendum — PR44's run on `9464dd8`: the Chromium install failed on the runner's name resolution

- **Owner:** App Manager 10. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4"), with DM-59 or after it (OD-25). App Manager 10 receives the answer, in DM-59's report.
- **Revision 1, 11 November 2026.**
- **Why:** PR44's pull-request run on DM-59's commit failed in one job, outside the PR's change. The manager cannot re-run Actions jobs and never asks Nathan to (OD-58), and a failure that seems to call for a re-run goes to the Dev Manager first (OD-32; the manager workflow, "Actions re-runs"). OD-21 asks for a diagnosis and then a fix or a recorded, reviewed explanation.
- **Where the result goes:** DM-59's report and its disposition in the review log; the evidence record; the carried-items file, if a retry is carried.
- **Stream variables:** none are needed.
- **Deletion condition:** prune with DM-59's consultation.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-59 addendum — PR44's run on `9464dd8`: the Chromium install failed on the runner's name resolution.** From App Manager 10, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`. Please answer it as DM-59's item 7, in the same report.

**7. The failure, and what to do about it.**
- **What failed:**
  - pull-request run 43044190450 on `9464dd8`, job **Mobile checks**, step "Install Chromium for rendered fixture checks" (`npx playwright install --with-deps chromium` in `.github/workflows/foundation.yml`);
  - apt could not fetch nine font packages that `--with-deps` installs. Each attempt reported `Temporary failure resolving 'azure.archive.ubuntu.com'`, then `Failed to install browsers` and `Installation process exited with code: 100`;
  - the step ran from 15:03:12 to 15:13:17 UTC; the rendered-check step after it was skipped;
  - the **Foundation gate** failed only because that job failed.
- **The manager's diagnosis:** outside the PR.
  - `9464dd8` changes Markdown only (`git diff --name-only c4324d3 9464dd8 -- . ':!*.md'` prints nothing);
  - the other six jobs passed on it, the Database proof checks with the profile suite among them;
  - the same code passed all eight jobs at `c4324d3` (pull-request run 43021936005);
  - the failure is the runner's package-mirror name resolution, which no file in PR44 touches.

  The records hold no earlier failure of this step on name resolution. The step has no retry: DM-41's retry covers `actions/setup-python` only.
- **Done so far:**
  - one comment on PR44 saying what failed, why it is not the PR's, and that no fix exists in the repository (the PR-activity rules for a PR the manager opened);
  - no re-run, which the manager cannot perform; no empty commit.

  This addendum's commit starts a new pull-request run on its head, as any records push does.
- **Options:**
  - **(a)** Accept the diagnosis as the recorded, reviewed explanation for `9464dd8`'s run, with no re-run. The PR run on the final head, after your dispositions are recorded, must pass with `Application checks passed`. If its Mobile checks fail the same way, the failure comes back to you before the merge.
  - **(b)** (a), and carry a one-time retry of the Chromium install to the next change to the workflow, on DM-41's pattern: a fixed pause, the same command, and a failure after the retry failing the job. It goes in the carried-items file (recommended).
  - **(c)** Add that retry in PR44 now. That is a workflow change, so it is full scope, with the workflow diff read and full checks before the merge (root `AGENTS.md`), and it widens PR44.
- **The manager recommends (b).** Nothing in PR44 caused the failure, and the final head gets its own run in any case. The retry spares a later PR the same stop, since no one re-runs failed jobs (OD-58). It belongs with the next workflow change, not in a photos PR.
- **Asked:** a verdict; for (b), the carried item's words; for (c), the step's words.
