# Application contracts

Two contracts remain distinct:

| Contract | Current scope |
|---|---|
| `development/gapp-dev-v1.schema.json` and `development/openapi.json` | Three implemented, isolated development GET responses. Compatibility stays pending/fixture; readiness stays 503. |
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
