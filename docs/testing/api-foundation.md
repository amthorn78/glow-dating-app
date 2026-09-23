# API foundation evidence

**Work item:** P01.3 API portion; includes narrow configuration and readiness
preparation for P03. **Observed date:** 23 September 2026.

This is new local application code under `services/api/`. It does not reuse or
execute legacy code. Repository publication and governing authority-transfer
evidence are recorded by App Builder 1 separately. This document does not mark
all of P01.3, P02, or P03 complete.

## Version basis

| Component | Selected exact version | Observed source/basis |
|---|---|---|
| CPython | 3.12.14 | Available runtime; [official release](https://www.python.org/downloads/release/python-31214/) identifies a 12 August 2026 security release; `.python-version` records the pin |
| Django | 5.2.17 | [Official supported releases](https://www.djangoproject.com/download/) lists this 5.2 LTS patch and extended support to April 2028; [5.2 compatibility](https://docs.djangoproject.com/en/5.2/releases/5.2/) includes Python 3.12 |
| Django REST framework | 3.18.1 | [Official release notes](https://www.django-rest-framework.org/community/release-notes/) date it 7 September 2026; 3.18 removes older Django 4.2/5.0/5.1 support; 5.2 remains supported |
| Ruff | 0.16.8 | Package index and installed wheel metadata; lint/format actually executed |
| mypy | 2.3.1 | Package index and installed wheel metadata; application type check actually executed |
| jsonschema | 4.26.0 | [Official stable documentation](https://python-jsonschema.readthedocs.io/en/stable/) and package index; development-only shared contract checker dependency |
| uv lock generator | 0.12.17 | Installed tool version; used for Python 3.12 hash lock generation |

Python 3.12 is in security maintenance, not the newest feature series. The exact
available supported runtime was selected to make this initial check reproducible.
The framework pins were verified against both official guidance and package-index
availability. No preview versions or unconstrained runtime dependencies are used.

Runtime dependencies are Django, DRF, asgiref 3.12.1 and sqlparse 0.6.0. Exact
transitive development pins and artifact hashes are in the lock files. Installed
wheel license metadata is captured in
`services/api/dependency-inventory.json`: Django/DRF/asgiref report BSD-3-Clause;
sqlparse reports the BSD license classifier; Ruff/mypy/mypy-extensions/librt/
ast-serialize report MIT; typing-extensions reports PSF-2.0; pathspec reports
MPL-2.0. jsonschema and its added attrs, jsonschema-specifications, referencing
and rpds-py dependencies report MIT. Missing exact license-expression metadata is preserved as missing, not
filled by inference. This is a dependency inventory, not a legal assessment or
complete container/native SBOM.

## Implemented and verified boundary

- Explicit `GLOW_ENV=development` or `test` is required. Missing, blank, unknown,
  staging and production configurations fail startup. Fake-provider production
  rejection is tested independently of live-provider production refusal.
- Connection variable presence is refused without echoing values. No database
  driver, real provider, auth/session app, HDE URL or HDE calculation is wired.
- Django's dummy backend is configured. All endpoint tests use `SimpleTestCase`
  with no permitted databases. The test runner reported that default database
  setup was skipped. Endpoint tests also deny network sockets.
- Liveness returns HTTP 200 `alive`. Readiness returns HTTP 503 `not_ready` with
  `mode: fixture`; it never certifies real-user readiness.
- The read-only development route returns synthetic demo people and the
  `gapp-dev-v1` envelope. Compatibility is always pending with fixture provenance;
  there is no numerical score, harmony band, eligibility or match claim.
- Mutation methods return HTTP 405, unknown hosts return HTTP 400, response
  caching is disabled, and there is no login, admin or production recommendations
  route. A per-request guard also rejects fixture access outside dev/test even
  if URL configuration was loaded earlier.

## Executed checks

Working directory: `services/api/`; Linux x86_64; CPython 3.12.14.

| Command | Actual result |
|---|---|
| `python -m venv .venv` | Exit 0; newly created isolated virtual environment |
| `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock` | Exit 0; hashes enforced; final lock has 16 packages including jsonschema |
| `.venv/bin/python -m pip check` | Exit 0; no broken requirements |
| `GLOW_ENV=test .venv/bin/python manage.py check` | Exit 0; no issues, none silenced |
| `GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 2` | Exit 0; 15 tests passed; database setup skipped |
| `.venv/bin/ruff check .` | Exit 0; all checks passed |
| `.venv/bin/ruff format --check .` | Exit 0; formatting checked |
| `.venv/bin/mypy` | Exit 0; 8 application source files checked |
| `GLOW_ENV=test .venv/bin/python smoke.py` | Exit 0; 200 live, 503 readiness, 200 fixture recommendations; temporary loopback server shut down |

After jsonschema was added for the shared contract checks, the final 16-package
lock was also installed with `--require-hashes` into a second fresh virtual
environment, `.venv-repro`, with exit 0. Django checks, all 15 tests, pip check,
Ruff lint/format, mypy and the HTTP smoke were repeated with that environment
and passed. Runtime transitive versions are constrained to `requirements.lock`
when compiling the development lock. Both virtual environments are ignored.

An additional isolated subprocess run of `glow_api.devserver --port 8123` and
loopback HTTP requests observed 200 live, 503 readiness, and 200 development
recommendations. The server was terminated afterwards. An initial attempt across
separate execution calls received connection refused; the same-execution run
then passed. No application defect or external reachability claim is inferred
from the isolated execution-tool networking behavior.

The first type-check run found three local typing problems, corrected before
the passing run: typed-dictionary construction, environment literal narrowing,
and the untyped DRF framework inheritance boundary. mypy checks app annotations;
Django/DRF imports lack installed type stubs, and the single `APIView` inheritance
exception is explicit. These checks do not certify third-party framework internals.

## Limits and next evidence

No package-install network block was encountered. Successful installation here
does not prove another platform's install, native builds, or container deployment.
This checkpoint has no verified container image digest or deployment artifact.

The fixture API proves routing, deterministic DTO presentation and configuration
boundaries. It does not prove authentication, data persistence, SQL migrations,
PostgreSQL concurrency, real HDE compatibility, eligibility rules, chat/media
permissions, provider behavior, or production readiness. Allauth and real adapters
remain later work. Database-dependent integration stays in P11. No shared Railway
resource, database, protected HDE source, secret or engine endpoint was changed
or contacted by this API work.

Next: bind shared contract validation to this narrow smoke DTO, develop the
separate production contracts and domain seams under P02, and maintain explicit
fixture-only operation until the real integrations exist.

## Foundation review correction

The development server now supports an OS-assigned port and a bounded JSON startup handshake for its parent smoke process. The explicit Android emulator host alias `10.0.2.2` is allowed; neighboring and spoofed hosts are rejected. After correction, 16 configuration/endpoint tests, Ruff lint/format, and mypy passed. Root smoke and its occupied-old-port/startup-failure regression passed; the latter proves an unrelated matching server cannot supply acceptance evidence. No native emulator run is claimed.
