# Application contracts

This directory currently specifies **only the isolated development scaffold**. It is preparatory P02 work, not the public application API baseline or P02 completion. The architecture documents describe proposed future contracts explicitly.

## Implemented development surface

| File | Scope |
|---|---|
| `development/gapp-dev-v1.schema.json` | Closed JSON Schema 2020-12 definitions for synthetic recommendations, liveness and deliberately unsuccessful readiness |
| `development/openapi.json` | OpenAPI 3.1 description of the three implemented GET routes; external references resolve to the schema beside it |
| `tests/test_development_contract.py` | Schema and implementation response checks, with negative examples for leakage and false compatibility claims |

The version marker is `gapp-dev-v1`. The schema follows the mobile development decoder and API response shapes. It permits no unrecognized fields at any object boundary. Compatibility can only be `{ "status": "pending", "source": "fixture" }`. An empty list is valid; result order is fixture presentation order. Neither profile age nor inclusion in the fixture establishes a production eligibility decision.

The current mobile types/decoder are hand-written under `apps/mobile/src/contracts/`, not generated. Schema/client equivalence is not yet exhaustively established: the client additionally checks distinct profile identifiers, JavaScript string length counts UTF-16 code units while JSON Schema counts Unicode code points, and regex/whitespace behavior can vary between implementations. The present fixture strings are ASCII. Resolve the text-length convention and share a generated corpus before promoting this design to a production contract.

No public account/authentication endpoint, provider endpoint, HDE endpoint, authentication scheme or server URL is defined here. The framework may emit errors and support HEAD/OPTIONS in addition to the documented GET responses. That does not establish a production error convention.

## Check

After installing the API's locked development dependencies, run from the repository root:

```bash
PYTHONPATH=services/api services/api/.venv/bin/python -m unittest discover -s packages/contracts/tests -v
```

The checks use the API's test configuration, dummy database backend and `SimpleTestCase`, which disallows database access. They validate actual route responses against the referenced schemas and import no HDE adapter. This proves only the stated development response shapes and sampled rejection behavior. It does not establish persistence, allauth, native SDK or live-provider behavior.

## Proposed production contract work

The proposed flow/ownership and state inventory is in [domain and data boundaries](../../docs/architecture/domain-and-data-boundaries.md). HDE assumptions are in [provisional HDE seam](../../docs/architecture/provisional-hde-seam.md). P02 still needs reviewed production schemas, authorization/error/version conventions, generated clients, repository/unit-of-work ports, provider fixture conformance, model/migration definitions and the remaining acceptance cases. Do not point a production client at the development route or rebrand fixture schemas as that API.
