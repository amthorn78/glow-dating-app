# P02 domain and provider seam preparation

**Recorded:** 23 September 2026. **Work:** bounded local preparation for P02.1
and P02.3; not completion of either task or phase P02. This unit adds pure
Python application-domain code only. It does not alter the existing
development HTTP contract, API configuration, mobile scaffold or dependency locks.

## Scope and governing basis

GAPP-PF01 sections 5–7 require app/engine identity separation, versioned integration
provenance, conservative pair direction, and eligibility before compatibility
ranking. This unit prepares those primitives without claiming that an authenticated
request flow, ranking service, persistence adapter or HDE connection exists.

| New code | Implemented responsibility |
|---|---|
| `services/api/glow_domain/identity.py` | Distinct immutable `AccountId` and `EngineChartReference`; explicit pending/resolved mapping; birth-input and mapping revisions |
| `services/api/glow_domain/eligibility.py` | Immutable predicate snapshots and fail-closed pair eligibility; deterministic exclusion reasons and version provenance |
| `services/api/glow_domain/compatibility.py` | Internal `gapp-hde-port-v1` fixture states, synthetic provenance, ordered/versioned cache-key construction and explicit test-only symmetry declaration |
| `services/api/glow_domain/ports.py` | Narrow read-only eligibility/mapping repository protocols and a fixture compatibility provider protocol |
| `services/api/tests/test_domain.py` | Pure unit tests for exclusions, identity boundaries, direction/version invalidation, immutable DTOs and synthetic provider states |

These are application-owned internal interfaces. They are not the engine's final
wire schemas or endpoints. `FixtureCompatibilityPort` deliberately returns a
fixture-only type; a supported live result contract must be designed when A01/A07
are resolved. No numerical compatibility or harmony band is invented.

## Eligibility semantics

Every person snapshot explicitly supplies adult, consent, verified, active,
complete, visible and moderation outcomes: `PASS`, `FAIL`, or `UNKNOWN`. Both
preference directions and both block directions must also be explicit. A missing
typed decision is rejected; any `FAIL`, `UNKNOWN`, block or unknown block state
excludes the pair. Self-pairs are excluded. Multiple exclusions retain stable
order: self, viewer safety, candidate safety, preferences, then blocks.

The caller supplies evaluated policy predicates and their versions. This code
does not guess a launch geography, preference range, age calculation/timezone,
identity verification method, policy acceptance, moderation evidence or source
freshness. It has no client-input route. A future application service must obtain
trusted current snapshots, verify pair correspondence and recheck state before
privileged actions. A passing result is only eligibility under the supplied
snapshot; it is not a like, mutual match, messaging entitlement or authentication.

## Identity and fixture behavior

Application and engine wrappers remain distinct even if their underlying opaque
strings happen to match. Inputs are preserved exactly; no conversion from an app
ID to an engine ID occurs. A pending mapping has no resolved engine reference and
cannot form a cache key. Raw birth inputs are absent from these DTOs.

The immutable fixture provider requires an explicit `development` or `test`
environment and explicit case. With a resolved pair it returns one of pending,
unavailable, unsupported, or explicitly synthetic ready. An unresolved mapping
forces pending. Every result carries fixture provenance and a synthetic case;
none carries a score, band or genuine HD projection. The existing HTTP contract
remains pending-only; this unit adds no serialization or route for internal ready.

Fixture cache identities include both app IDs, both opaque engine references,
birth-input revisions, mapping revisions, fixture-set revision, adapter revision,
simulated engine/contract revisions and the internal port version. Pair order is
preserved by default. Normalization requires an explicit symmetry declaration
matching the exact simulated engine and contract revisions, with an evidence
reference. Tests use only a labeled synthetic declaration. No real HDE symmetry
guarantee has been obtained or asserted. There is no cache storage, TTL or live
cache-rights assumption in this unit.

## Verification

Commands run from `services/api/` using the existing pinned CPython 3.12.14
development environment:

| Command | Result |
|---|---|
| `.venv/bin/python -m unittest tests.test_domain -v` | Exit 0; 15 test methods passed, including parameterized cases for every safety predicate, both people and both preference/block directions |
| `.venv/bin/mypy glow_domain` | Exit 0; all 5 domain modules checked |
| `.venv/bin/ruff check glow_domain tests/test_domain.py` | Exit 0; all checks passed |
| `.venv/bin/ruff format --check glow_domain tests/test_domain.py` | Exit 0; all 6 files already formatted |

The tests run without Django setup and without any database or HDE access.
Provider-state tests replace network-socket creation with a failing stub. Typed
repository protocols have no implementation; these tests cannot establish SQL,
transaction, ORM, authentication or provider behavior.

The initial lint pass reported two local imported-name shadowing findings; the
loop-variable names were corrected. No external service, source of authority,
production record or protected HDE resource was touched.

## Remaining work

P02 still needs complete production contracts and state machines, trusted snapshot
acquisition, authenticated input/authorization, service orchestration that applies
eligibility before calling compatibility, full fixture-conformance coverage,
transaction/unit-of-work semantics, models/migrations, generated clients, and
the rest of the plan's flow acceptance map. These functions do not implement
cache invalidation delivery, atomic block/send behavior or mutual matching.
Production persistence and supported live HDE/provider validation remain P11 work.

## Internal fixture application service

`glow_domain/pair_evaluation.py` composes the read ports and eligibility primitives. It reads current supplied snapshots by application identity on every evaluation; missing or mismatched identities reject the operation. Failed/unknown eligibility returns exclusions before chart lookups or compatibility calls. Missing/mismatched chart mappings reject, and a present pending chart mapping returns `pending_identity` without a provider call. Eligible resolved mappings reach only the injected fixture-result port. The service requires explicit development/test mode and creates no HTTP route, rank, queue, like, match or authorization.

The policy predicates are trusted internal inputs. Fresh reads are neither atomic nor proof of freshness in a real repository; they do not establish concurrency, block/send linearization or database behavior. A typed provider-unavailable result is preserved. The current port defines no exception taxonomy, so unexpected adapter/programming exceptions propagate instead of being mislabeled as normal provider unavailability. No request or private output is logged.

Ten additional tests in `tests/test_pair_evaluation.py` passed, proving eligibility-before-provider, missing/mismatched identity handling, no provider call for unresolved mappings, rereads on repeated evaluations, fixture-mode refusal, typed unavailable propagation and visible undeclared errors. An independent review of the first 15 primitive tests found no actionable scoped defect; a subsequent independent internal-service review ran all 25 domain/service tests and found no actionable scoped defect.

Coordinator combined validation: `GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 1` passed **41 tests** (16 API/configuration, 15 domain primitives, 10 service tests); `ruff check .`, `ruff format --check .` (22 files), and `mypy glow_api glow_domain` (14 modules) passed. Six shared development-contract tests also passed. The default mypy configuration now includes both API and domain modules so hosted CI checks the new code. None of this establishes P02 completion.
