# P02.3 provider conformance evidence

Scope: app-owned provisional contracts and development/test adapters in
`glow_domain/provider_contracts.py` and `provider_fixtures.py`. Read alongside
[provider architecture](../architecture/provider-conformance.md) and
[trusted eligibility](../architecture/trusted-eligibility.md). No HDE wire schema,
database connection, engine call, protected mutation or live provider is involved.

Observed local commands from `services/api/`, using the freshly installed pinned
CPython 3.12.14/hash-locked development environment:

| Command | Result |
|---|---|
| `.venv/bin/python -m unittest tests.test_provider_conformance -v` | Exit 0; 29 tests pass. |
| `.venv/bin/ruff check glow_domain/provider_contracts.py glow_domain/provider_fixtures.py tests/test_provider_conformance.py` | Exit 0. |
| `.venv/bin/ruff format --check glow_domain/provider_contracts.py glow_domain/provider_fixtures.py tests/test_provider_conformance.py` | Exit 0; all three files already formatted. |
| `.venv/bin/mypy glow_domain/provider_contracts.py glow_domain/provider_fixtures.py` | Exit 0; both new modules pass strict type checking. |

All tests inherit a socket-creation prohibition and use synthetic, unrelated
birth/identity fixtures. They do not configure Django, import a database adapter
or require credentials. Prior domain tests and the new trusted evidence suite
remain separate evidence for both participant/direction predicate behavior.
Hosted candidate acceptance and combined API/mobile/contract checks are recorded
in the enclosing P02 checkpoint; these local results alone are not publication
or merge evidence.

| Case family | Executable evidence in `tests/test_provider_conformance.py` | Deferred live proof |
|---|---|---|
| Malformed private inputs | Civil date/time type checks; unknown/approximate/timezone-pair rules; whitespace, invalid Unicode and bool-vs-integer checks. Facts remain unconverted and excluded from repr. | Supported engine input/uncertainty semantics and real ownership/authentication. |
| Pending/ambiguous/resolved charts | Uncertainty cannot resolve; pending/unavailable/unsupported has no fabricated chart; resolved fixture must use explicit correct account/input mapping. | Actual chart operations, timezone resolution and completion signal. |
| Input/consent correction and idempotency | Same-input replay stable; changed payload conflicts; new current version or consent withdrawal invalidates replay. | Durable provider key semantics and transactional source acquisition. |
| Eligibility ordering and empty results | Empty/excluded candidates make zero mapping/provider calls. Missing/wrong/pending mapping makes zero provider calls. | Actual candidate query/index behavior and authorization. |
| Timeout/outage/unsupported/malformed output | Maximum one to three attempts; expected typed failures stay distinct; malformed adapter types and defects raise. | Real timeout deadlines, backoff, rate limits and supported error taxonomy. |
| Pair/version/provenance binding | Reversed pair, changed mapping/input and simulated contract mismatch reject; projection rechecks current identity; synthetic ready projects as pending with only status/source. | Supported live provenance/output/cache rights and directionality. |
| Partial batches | One successful pair retained while another exhausts retries; each candidate has its own outcome; duplicates/over-budget input reject before work. | Supported partial-response mapping, if an actual engine batch operation exists. No such endpoint is assumed. |
| Stale or revoked state during call/retry | Changed evidence version, visibility or mapping discards output; revocation during timeout prevents the retry; a later candidate's call revoking or changing an earlier candidate discards that earlier result in the final batch recheck. | Concurrent block/pause/consent/deletion ordering in the real P11 transaction boundary. |
| Deletion/shared chart | Unknown ownership, shared chart, zero references and absent mapping all yield an incomplete app obligation; wrong owner and conflicting replay reject. | Actual downstream deletion rights, shared ownership, retained records, tombstone replay and verifiable completion. |
| Mapping/outbox UOW | One logical event on replay; changed payload conflicts; stale account/input/mapping, withdrawal and deletion change neither mapping nor event; correspondence and types enforced. | PostgreSQL atomicity, crash recovery, constraints, outbox delivery/deduplication and rollback. |
| Fixture containment | Staging, production and unknown environment refuse construction; changing a mutable fixture's environment cannot bypass its invocation guard. | Actual deployment composition, credential isolation and live adapter activation. |

`CompatibilityConformanceCases` is a reusable factory-based test mixin for the
provisional adapter behavior. The current implementation uses synthetic scripts.
P11 must adapt authorized provider sandbox scenarios to that interface and expand
the cases to the actual supported contract; simply rerunning a fake is not live
conformance. No full authentication, SQL, cache, HDE deletion or release claim
is established here.

The first local lint pass found test-only loop binding and the UTC alias; these
were corrected. Parent review identified unvalidated mutable fixture-state
booleans/identity types; explicit runtime validation and negative cases now cover
that gap. Independent review reproduced a deterministic stale-batch window: a
later provider call could revoke an earlier candidate while its output remained
retained. The batch now captures evidence privately and rechecks all retained
outcomes after provider work; a regression covers revocation and mapping change.
The 29-test scoped run above includes that correction. Final independent-review
and combined candidate status are recorded by the enclosing checkpoint.
