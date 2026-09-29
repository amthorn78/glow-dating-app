@AGENTS.md

# Claude sessions: manual relay

**Nathan runs a manual relay.**

- The manager gives Nathan prompts for implementers.
- Nathan runs each implementation session himself and relays its findings back.
- The manager follows up as needed.
- Nathan reinitiates managers manually, or directs the outgoing manager to create its successor (OD-31).

The full procedure is in `docs/planning/manager-workflow.md`.

- **Manager** (started by Nathan from a manager start prompt, or created by its predecessor at his direction, OD-31): begin with `docs/continuity/current-handoff.md` and follow the manager workflow. The manager never starts implementation or review work itself: no subagents or remote-session tools for that work. It writes the prompt and hands it to Nathan.
  - **Exception: the Dev Manager** (Nathan, 25 September 2026). The manager creates the Dev Manager session itself with the remote-session tools, and relays consultations to it and its reports back. See `docs/planning/dev-manager.md`.
- **Dev Manager** (created by the manager from the Dev Manager start prompt, or by its predecessor at Nathan's direction, OD-35): follow `docs/planning/dev-manager.md`. You review, challenge and approve decisions; you do not implement. Write only your report files and push only your own branch.
- **Implementation or review session** (started by Nathan from a prompt in `docs/ephemeral/`): follow that prompt and its linked brief.
  - You may use any tools, subagents, scheduled wake-ups or other capabilities the assignment needs.
  - Keep changes within the owned paths.
  - Push your own session branch and report as the prompt requires. The manager integrates branches, merges and syncs Notion.

**Environment.** App sessions run in the dedicated app cloud environment: no HDE variables, and the pinned toolchain from `scripts/bootstrap-toolchain.sh`. At session start, check variable names only. If `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is present, the session is in the HDE-shared environment:

- tell Nathan;
- never read, print or use those values;
- run app commands only in a clean process environment.

Create the API virtual environment with `python3.12`. Read the applicable nested `AGENTS.md` before touching a component. No external prompt library or Drive access is required.
