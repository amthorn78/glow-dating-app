# Status report and State of the App

- **As of:** 26 October 2026. Prepared by App Manager 8 from the M05 whole-project review, for the Dev Manager's DM-31 and for any session that needs the whole picture.
- **Basis:** `main` at `5b9bcb1` (PR33). The manager branch adds Markdown records after it. The review read `f669f37`, and the manager integrated it at `e27f7c7`.
- **Claim levels:** "verified" means the M05 review or the manager checked it against the code, Git, CI or a tool, as the [M05 record](../testing/evidence/2026-10-25-m05-project-review.md) states. Anything else names its source.
- **Authority:** this is a snapshot, refreshed only for a periodic review. The [current handoff](current-handoff.md) routes sessions, [PF01](../pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md) governs the plan, and Notion holds live task state. The previous snapshot, as of 25 September 2026, is in [history](history/state-of-the-app-2026-09-25.md).

## 1. In one paragraph

Glow is a new iOS and Android dating app built around Glow-owned accounts, profiles, reciprocal eligibility, recommendations, mutual matches, safety and one-to-one chat. It will consume compatibility results from the separate, protected Glow HD Engine (HDE). In 33 days (23 September to 25 October 2026), phases P00 to P05 and the chat items P06.1, P06.DB and P06.2 merged, at fixture scope. The repository holds a pinned Expo app, a Django API, shared contracts and two proofs: Stream Chat's permissions, and send-versus-block ordering on a disposable PostgreSQL in CI. Every offline check passes. Nothing is served or deployed, and there is no production database, no HDE call and no client provider token. **The M05 review's verdict is "at risk"** (its section 2): what is built is sound, but the plan places the production server in no phase before P10 and P11, completion's external gates are open and undated, and the process's records cost is high.

## 2. Phase and item status (verified by M05, 26 October 2026)

| Phase or item | State | Evidence | What remains |
|---|---|---|---|
| P00 to P05 | Done, fixture scope | PR1 to PR14; the checkpoints in `docs/testing/` | Deferred cases in the [P11 plan](../testing/p11-deferred-acceptance.md); the production server has no phase (M05 finding 1) |
| M01, M02 | Done | PR15, PR16; PR18 | M02's hardening follow-ups ([its brief](../planning/claude-setup-optimization.md)) |
| M03 | Done (the Dev Manager's start and its first reviews, DM-01 and DM-02) | The [review log](dev-manager/README.md) | — |
| P06.1 | Done: PR27, `47db18d` (29 September) | [Evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md) | Items carried to P11 |
| P06.DB | Done: PR28, `3afffb3` (5 October) | [Evidence record](../testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md) | DB06 and DB09 on the real target (P11) |
| P06.2 | Done: PR29 to PR33, last `5b9bcb1` (25 October) | [Evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md) | The history read's provider half is unproven live; nothing is served; P11 entries |
| P06.3 | Planned; no brief; not resumed (OD-05) | — | Phase P06 is not complete (M05 finding 7) |
| P07 to P12 | Planned | — | All of it |
| M04 | Ready; waits for M05's close | OD-39 | Brief, the Dev Manager's read, implementation, review |
| M05 | In progress: report integrated; DM-31 next | The M05 record | The Dev Manager's read, then Nathan's decisions |

## 3. What exists (verified at `f669f37`)

| Component | Offline checks (M05, 26 October) |
|---|---|
| `apps/mobile` (Expo app) | 621 unit tests; 97 rendered tests in CI (run 40243775584) |
| `services/api` (Django API) | 366 tests; ruff, format and mypy clean |
| `packages/contracts` | 39 Python and 586 JavaScript tests; `generate` produces no diff |
| `proofs/stream-chat` | 648 tests |
| `proofs/postgres-ordering` | 160 unit tests; in CI, reference 56/56, adapter 115/115, delivery 13/13, reads 62/62, `VERDICT: PASS` |
| CI (`foundation.yml`, eight jobs) | `main`'s 15 most recent runs succeeded |

- **Boundaries that hold** (M05 section 2): no HDE call; no database connection outside CI's disposable proof; no token served (OD-45); no provider data in a render, a stored client state or a log.
- **Known gaps:** M05 findings 10 to 29, among them the API's narrow refusal list (22), the message spool's kept text (23), the dormant token code (24) and the mobile release guards' untested branches (17).

## 4. Dependencies (M05 finding 29)

`npm audit` at `f669f37`, reproduced by the manager from `apps/mobile`'s lock:

- `apps/mobile`: 1 critical, 6 high and 7 moderate, mostly development and build tooling. The fixes npm suggests imply an Expo SDK upgrade.
- `packages/contracts`: 1 moderate.
- `proofs/stream-chat`: 1 high (`follow-redirects`, recorded).

## 5. Open gates and decisions

- **With the Dev Manager first (DM-31), then Nathan:** N1 to N6 (the M05 record, section 7.2): where the production server is built, the budget, the store and legal requirements matrix, launch countries and age assurance, resuming feature work, and the process changes.
- **External:**
  - A01, HDE's contract: no date, in Nathan's own process (OD-23).
  - A04, the budget: $0, and the Stream Maker application pending since 25 September.
  - A05: launch geography, age assurance, retention and moderation operators.
  - Signing accounts and an EAS project: the mobile release block.

## 6. Risks (PF01 §11, as M05 reads them)

- **R01, late persistence defects:** raised; the persistence code outside chat has no phase before P11 (finding 1).
- **R02, the HDE contract:** open; no delivery date.
- **R03, shared infrastructure:** holding; no shared resource was changed.
- **R04, chat bypass or cost:** the client bypass is closed (OD-45); the cost is unknown until the production plan (A04).
- **R05, store, safety and operations:** open; the requirements matrix has not been built (finding 2).
- **R06, duplicate docs and misleading progress:** raised; Notion's stale status bullets (finding 30) and the records volume (finding 49).

## 7. The process as measured (the M05 record, section 6)

- Since 25 September, 39,250 Markdown lines were added against 10,564 lines of application code and tests, and 248 records commits against 58 code commits.
- 19 correction passes ran, of which 18 changed code. Of 24 exact-head reviews, 15 found code or test defects; Codex found 13 more after the reviews.
- 12 of the 31 days had commits. The two gaps, 4.9 and 16.0 days, have no recorded cause.
- Seven App Managers and three Dev Managers served in 32 days; the mistakes log holds 92 rows, 57 of them accuracy slips.
