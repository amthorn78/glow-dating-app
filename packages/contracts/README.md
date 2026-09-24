# Application contracts

Two contracts remain distinct:

| Contract | Current scope |
|---|---|
| `development/gapp-dev-v1.schema.json` and `development/openapi.json` | Three implemented, isolated development GET responses, plus an additive in-memory discovery page DTO. No new HTTP route. Compatibility stays pending/fixture; readiness stays 503. |
| `production/gapp-api-v1.schema.json`, `production/openapi.json` and `production/flows-v1.json` | P02 app-owned logical production contract/state baseline, with executable schema and transition-oracle checks. No production routes, auth wiring, persistence or providers are implemented by this package. |

[Production contracts](../../docs/architecture/production-contracts.md) defines every F01–F20 owner, projection, actor, state/error/version and pending-policy boundary. The JSON Schema files own payloads; flow registry owns transition tuples and projection scopes. `transition_contract.py` is test-only design validation, not runtime API authorization. HDE wire fields and credential APIs are not invented. F01 references maintained allauth; final HDE ready output remains unavailable pending A01/A07.

## Generate and check

Use repository Node 24.19.0/npm 11.9.0. From the repository root:

```bash
npm ci --ignore-scripts --prefix apps/mobile
npm ci --ignore-scripts --prefix packages/contracts
npm run generate --prefix packages/contracts
npm run check --prefix packages/contracts
PYTHONPATH=services/api services/api/.venv/bin/python -m unittest discover -s packages/contracts/tests -v
```

Generation uses exact-pinned `json-schema-to-typescript` for types and Ajv 2020-12 standalone for validators. Committed artifacts live in `apps/mobile/src/contracts/generated/`. `--check` regenerates in memory and compares bytes; generated code is not hand edited. Standalone validators need the pinned Ajv/ajv-formats runtime helpers, but do not compile schema or evaluate new code on the phone. Python uses the existing locked jsonschema dependency and a narrow standard-library UTC calendar checker because optional RFC3339 checking is not installed. All date/time spelling is restricted by the schema. Dependencies and license metadata are inventoried; this is not a legal clearance.

`corpus/shared-v1.json` runs unchanged through Python and the actual generated JavaScript validators. It includes every named DTO, rejection of extra/private fields, Unicode scalar length, combining marks, explicit whitespace, unpaired surrogates, regex end-anchor/newline cases, dates, duplicate candidate IDs/dimension keys and state-dependent projection leakage. Duplicate keys are enforced after shape validation in a small shared semantic rule; standard JSON Schema alone does not enforce key-level array uniqueness. TypeScript types alone never validate network JSON. The current development parser now uses these generated validators, replacing its former hand-written length/trim checks.

[Contract evidence](../../docs/testing/contract-baseline.md) records commands/results and limits. Database-dependent authentication, constraints, concurrency, outbox durability, provider enforcement and native/device acceptance remain unproved here.

## P05.1 raw-fact conformance

`fixtures/reciprocal-eligibility-v1.json` is a separate canonical development
truth table, consumed unchanged by API `tests/test_eligibility_facts.py` and mobile
`src/eligibility/facts.test.ts`. It specifies raw participant/policy/block/clock
inputs and independent expected predicates/directions/pair states; it is not a
client DTO or production authorization request. It also drives the bounded
provider batch's zero-call exclusions and ready positive controls. The existing
JSON Schema/generated candidate contract is unchanged. See
[source/policy mapping](../../docs/architecture/reciprocal-eligibility-fixtures.md)
and [actual P05.1 evidence](../../docs/testing/p05-1-checkpoint.md).

## P05.2 discovery composition

`DevelopmentDiscoveryPage` adds a closed development DTO without changing the
existing layout GET or production contract. The Python discovery composition and
explicitly fictional mobile in-memory adapter share this shape. The page contains
fixture viewer/session/request/queue correlation, mode, state, at most two
`DevelopmentDiscoveryProfile` projections and an optional continuation. This new
profile type preserves the existing fields and adds one to four unique simulated
approved-media delivery references; the original `DevelopmentProfile` is unchanged.
Only `fixture-approved-…` labels are accepted, with no real photo URL or claim of
provider delivery. All compatibility
remains `pending`/`fixture`, including synthetic provider success. There are no
numeric scores, bands, private birth facts, preferences, block details, mapping
references or provider payloads in the projection.

`ready` has one or two cards; `partial` permits zero to two cards and denotes
incomplete synthetic provider work. `empty`, `exhausted`, `reload_required` and
`error` have no cards or continuation. Normal queue outcomes require a queue
identity; errors before queue creation may use null. Identity and cursor fields
use bounded opaque strings. Shape validation does not establish the current
actor, source versions, queue freshness or authority: the adapters and mobile
adoption checks enforce those boundaries. Cursors are non-durable in-memory
handles, not production signing, encryption or access secrets.

`fixtures/discovery-v1.json` contains one shared fictional viewer and fourteen
independent candidate records: six eligible pairs plus exclusions and missing
facts. It provides full participant, approved-media, policy, directional-block and
mapping inputs, explicit synthetic provider states, limits and independent
expected decisions/order. Runtime adapters consume the raw inputs rather than
the expected results. Both modes use the same eligible population and retain
independent progress; recommended order uses synthetic priority followed by
profile ID, and broader order uses profile ID. Priority has no Human Design
meaning. See [discovery architecture](../../docs/architecture/discovery-fixtures.md)
and [P05.2 evidence](../../docs/testing/p05-2-checkpoint.md).

The shared schema corpus runs valid and invalid page states, identity constraints,
private/unknown fields, pending-only compatibility, cursor restrictions and
duplicate IDs through Python and generated JavaScript validators. The JavaScript
cases also exercise the actual page parser. Existing development and production
cases remain unchanged.
