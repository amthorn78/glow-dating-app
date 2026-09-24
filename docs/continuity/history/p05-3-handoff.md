# Historical P05.3 handoff — superseded

Preserved from main ea394543533e99f611158b9026a2bd01de8d09b3. Relative links were adjusted for the archive location; commit-pinned links retain original recovery evidence. Drive links are historical provenance, not active prerequisites. Current assignment: ../current-handoff.md.

# App Builder 1 current handoff

## Assignment, authority and scope

**AP1-P05.3-001 revision 1.0 · 24 September 2026 UTC.** Implement
**P05.3 — likes, matches and unmatch** at fixture scope through meaningful tests,
review, checked publication/merge and actual-main verification. Nathan Amthor is
Product Owner; App Planner 1 coordinates; App Builder 1 implements. The task is
**In progress**. Its live state and final containing-commit/check/merge identities
belong to the existing Notion records below, not this source checkpoint.

Read [root instructions](../../../AGENTS.md), [mobile instructions](../../../apps/mobile/AGENTS.md),
[GAPP-PF00](../../pf-canon/GAPP-PF00-Canon-Index-and-Authority.md),
[GAPP-PF01](../../pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md), especially D08,
and [P05.3 evidence](../../testing/p05-3-checkpoint.md). Technical authority transferred
to this application repository at `ac38e58651e5578ee8503b6423e4884203b42278`.
Notion owns state/evidence pointers; Drive holds historical plans and session prompts.

D08 authorizes app-only branches, PRs, checked merges and project records. This
bounded assignment excludes database connections, SQL/applied migrations, live
HDE/provider calls, Railway/Cloudflare mutations, deployments, production/public
activation, paid resources, legacy retirement and person-directed messages.
HDE source, data, canon and shared resources remain protected by effect.

## Live records and baseline

- [Control](https://app.notion.com/p/3e44590a05eb8118bf02f0dc0c3ea57c),
  [Work Register](https://app.notion.com/p/71b769915b5b4e00830663770bc95f7e),
  [D08](https://app.notion.com/p/3e44590a05eb8106b26aea3147dc84bf).
- [P05.3](https://app.notion.com/p/3e44590a05eb81b4807fcb4f07692b7a),
  [shared reports](https://app.notion.com/p/3e44590a05eb81d58971ee4cd870774f).
  AB1-R011/AP1-ACK011 accept P05.2; expected P05.3 report is **AB1-R012**, if unused.
- [Full assignment](https://drive.google.com/file/d/19q4yMpZGYSVyLokTHqkqhNXKUhQMy_vI/view),
  [A05 unresolved policies](https://app.notion.com/p/3e44590a05eb81579ffdc11ee2336bcd),
  [later P06.1](https://app.notion.com/p/3e44590a05eb81c4a7c9fba6b4ae7091).

Private repository `amthorn78/glow-dating-app`, ID 1383293037, default branch main.
Verified starting main: `833408ab3e04ad4f649e71ca0483e606806dddbb`, tree
`5ec516752b591e6b9f558d7fa50241a08b31576f`. No open PR or prior P05.3 branch existed
at startup. Scoped branch: **app-builder-1/p05-3-interactions**, created with that
actual remote parent. [PR14](https://github.com/amthorn78/glow-dating-app/pull/14)
initial head is `c4209d4ab90320dded692f0b4da584bba31f8207`, verified tree
`5abeba974d8b82fb6e9b4afae612469d78cd556a`. Its initial runs failed one new browser
case (80/81; all 69 inherited passed), and code review found unrelated-pair safety
invalidation. The first correction is published at
`2b69e0805fe569745729f8028ab83b7e705df2bf`, tree
`9d775a72e885eec0eed97862fc6f656d7feb9408`; both runs passed all four jobs and
81/81 browser cases. Its code review found three further P2 edge cases, so it was
not merged. The next correction was published at
`4db111f0cf574bd998d451ae1fb75e1f15049aad`, tree
`fb7b474fef2e144fed2d7e68b1d6f2a2b8436c07`, and again passed both full runs/81
browser cases. Code review then found deleted-target match projections after
unmatch; that shared-projection correction was published at
`e3760963ed683db9b54ec6774715d79dfebe80dd`, tree
`a114a342324ebbb5eaa836136ed1d110912f1229`, and passed both full runs/81 cases.
Its code review found a stored canonical-match key replacement edge in Python.
That correction was published at
`8ccf35e23b5276d318fa9577d91b6e2385996d18`, tree
`07ee1dae4a1720e66983c08e60ed714feae0b1f9`, and passed both full runs/81 cases.
Its review found targeted-source scope and original-action projection gaps. Their
correction was published at `554fbd81cafb966cdc1564c3f9889baf2e486dcf`, tree
`72df178bea03722a195a91e8f0e63cf74da505d2`, and passed both full runs/81 cases.
Review then found retained Python policy/clock authority, mobile presentation
invalidation and private consumption freshness gaps. Their correction was published
at `0859fc4560088619b5d48eecbdbe3a3c3bb5a96e`, tree
`ed0f2eeaa6a106d76383d5bc4c16253ed10ed538`, and passed both full runs/81 cases.
Review then found cleanup denial after target-registry removal in Python and for
valid-session suspended/deletion-pending actors in mobile. Their correction was
published at `74fd2a87e453b32fdbac07e2aac0bd081da9c9b5`, tree
`9d6549ee527256d1be167bf9d00585421840dc0a`, and passed both full runs/83 cases.
Review then found Python aggregate projection and replay target-binding gaps.
Their bounded correction is prepared locally. See the checkpoint and read
actual current head, PR and newer external reports before recovery.

Terminal Git authentication was unavailable. All **231** baseline blobs/modes and
the complete tree were verified against pinned GitHub source. The local snapshot
has synthetic ancestry for diffing only: **never push it**. Publish a GitHub tree
and commit with verified real remote ancestry, then verify complete tree and modes.
Preserve unrelated work and inspect uncertain writes before retrying.

The accepted P05.2 [PR13](https://github.com/amthorn78/glow-dating-app/pull/13)
merged at 2026-09-24T04:06:58Z. All four jobs in
[final-main run 35954266272](https://github.com/amthorn78/glow-dating-app/actions/runs/35954266272)
passed, including 69/69 rendered cases. Those are baseline evidence only.
The [historical handoff](../history/p05-2-handoff.md) and
[P05.2 checkpoint](../../testing/p05-2-checkpoint.md) preserve failed-run/focus and
terminal-page freshness corrections; their old P05.2 next actions are superseded.
Preserve the earlier P05.1 failure/negative-control history and never merge its
unmerged birth-diagnostics branch. No retrospective certainty is added.

## Required behavior and recovery

Read [interaction semantics](../../architecture/interactions-fixtures.md),
[discovery](../../architecture/discovery-fixtures.md),
[trusted eligibility](../../architecture/trusted-eligibility.md),
[production contracts](../../architecture/production-contracts.md),
[contracts README](../../../packages/contracts/README.md), and actual current code.
The accepted P04/P05.1 source guards, private media, recovery/drafts and all
meaningful inherited browser behavior remain required.

P05.3 supplies trusted session/target/batch-bound like/pass, private unilateral
state, reciprocal canonical matches, immutable minimal idempotency receipts,
simulated atomic state/receipt/outbox and participant unmatch/block revocation.
Unknown pass reversal, rematch and history policies grant nothing. A match is
not a provider channel or send capability. Mobile is an explicitly fictional
presentation substitute checked against shared contracts/cases; Python owns the
domain boundary. Public write routes remain disabled, readiness remains 503 and
the API retains its dummy database and guarded startup.

## Validation and publication

See [P05.3 checkpoint](../../testing/p05-3-checkpoint.md) for actual observed commands,
results, defects, reviewed source and local/hosted limitations. Use fresh explicit
`services/api/.venv`, Python 3.12.14, Node 24.19.0, npm 11.9.0 and committed locks.
No test may connect a database or invoke a live provider. Local browser installation
failed with an invalid ZIP; Docker is absent. Required rendered/container results
must therefore come from existing hosted Foundation jobs.

Before merge verify actual final head/base/main, complete diff, mergeability,
review dispositions and all four **Foundation** jobs, including documentation:
API checks, Mobile checks, API mobile smoke and API artifact checks. Wait for
running reviews; preserve concrete failures/corrections and report unavailable
coverage honestly. After checked merge verify merge SHA/ordered parents,
candidate/main tree relationship and all four jobs on actual merged main.
An earlier candidate pass does not certify later source or merged main.

**Next action at this source checkpoint:** publish the narrow PR14 corrections as
an actual child of `74fd2a87e453b32fdbac07e2aac0bd081da9c9b5`, then satisfy new final-candidate checks
and review before checked merge and actual-main gates. Independent Python/mobile
and contract/static/documentation review covers the initial source; the narrow
correction has its own focused review. The checkpoint preserves the P2 and first
hosted failures. On recovery, reconcile live PR/checkpoint state before repeating
any action. Do not declare Done while publication, required checks, review, merge
or final-main evidence remains pending.

After every required gate, record/read back **Verified → Done at fixture scope**,
update Control and append **AB1-R012 — To App Planner 1** with exact external
identities and remaining limits. Nathan relays that saved report; saving is not
planner receipt, automatic dispatch or background monitoring. Propose separately
**P06.1 — Prove chat-provider permissions and economics**. P06 remains Planned
until assigned; no Stream SDK/account/channel/token or purchase is activated here.

## Deferred integration

[P11](../../testing/p11-deferred-acceptance.md) owns real auth/persistence, multi-process
ordering/constraints/outbox durability, provider rights and restore. A01/A07 own
supported HDE output/throughput; A05 owns launch/rematch/history/operating policies.
Native signed builds, device accessibility and release proof remain open.

The audited direction is clean app-owned storage in HDE's same logical PostgreSQL
database `railway`, dedicated app schema/restricted roles, in Railway project
`ample-illumination` (`ce01529f-679f-4f52-a979-23113299a59b`). Static models/unapplied
migrations are design, not applied physical tables. No HDE or legacy table reuse,
connection or retirement is introduced. Mobile/API/contracts stay in this monorepo;
future WordPress operations use scoped app APIs without privileged table access.
