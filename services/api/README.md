# Glow API development foundation

This Django/DRF scaffold serves synthetic presentation data only. Pure internal
eligibility/provider contracts and static data definitions support the P02 design.
There is no account authentication, persistent storage, production eligibility
route, mutual matching, or real HDE result in the served baseline.

P05.1 adds a development/test-only raw-fact `FixtureEligibilityRepository` behind
the existing trusted ordered-pair service. Its shared Python/mobile corpus is
`packages/contracts/fixtures/reciprocal-eligibility-v1.json` at repository root.
See [reciprocal eligibility](../../docs/architecture/reciprocal-eligibility-fixtures.md)
for policy, source/revision mapping and provider ordering, and
[P05.1 evidence](../../docs/testing/p05-1-checkpoint.md) for actual checks. This is
an internal fixture seam, not served authentication or a production eligibility
endpoint. GET smoke data and the guarded dummy-database runtime remain unchanged.

P05.2 adds an internal, development/test-only bounded discovery composition in
`glow_domain/discovery.py`, backed by the same eligibility/provider seams and
`packages/contracts/fixtures/discovery-v1.json`. It models per-candidate authority,
synthetic ordering, two-card pages, opaque ephemeral continuations and final
publication guards. The mobile journey uses a conformant in-memory substitute.
This module has no HTTP route: the anonymous GET below remains layout/smoke data,
not authenticated discovery. See [discovery semantics](../../docs/architecture/discovery-fixtures.md)
and [P05.2 evidence](../../docs/testing/p05-2-checkpoint.md).

P05.3 adds internal fixture commands in `glow_domain/interactions.py` and an
explicit two-session composition in `interaction_fixtures.py`. Both directions
must submit legitimate, current-batch likes before the system creates one
canonical account-UUID match. `page()` returns the unchanged discovery page plus
a composition-owned UUID batch binding; production profile UUIDs come from the
shared `interactions-v1.json` registry, never a client account assertion.

`FixtureInteractionService.command()` accepts closed production interaction,
unmatch and block intents. It derives the actor from its trusted fixture session,
stages directional/match/block state, SHA-256 payload-bound receipt and minimal
logical events, and replaces one owned state only after callback-free revision
checks. A lost response can recover its immutable receipt after batch consumption;
current projections are separately authorized. Both discovery modes exclude
consumed directions, either block and every existing match pair. Source/mapping
replacement or same-value restoration permanently restricts an active match on
the next authority read; unmatch works without discovery or provider eligibility.
`contact_decision()` always denies send, and `FixtureInteractionWorker` observes
controlled events without delivery. No authenticated HTTP mutation, SQL,
provider channel, chat token or live contact is enabled.

The substitute retains at most 200 receipts plus pending reservations together,
200 discretionary events, and up to 190 separately reserved source-revocation
events for its twenty-identity cap. Capacity refuses without evicting replay
evidence. Reset is explicit and nondurable. Tests exercise two sessions, shared
raw command traces, immutable replay, atomic abort/reentrant ordering, current
eligibility, canonical uniqueness, block/unmatch, source restoration, late
projection callbacks, capacity and stale fake-worker completion. These do not
prove database isolation, crash recovery or external exactly-once delivery.
See [interaction semantics](../../docs/architecture/interactions-fixtures.md),
[P05.3 evidence](../../docs/testing/p05-3-checkpoint.md) and the
[P11 obligations](../../docs/testing/p11-deferred-acceptance.md).

P06.2 Stage A adds the chat contact port (`glow_domain/chat.py`), the chat provider
port with an in-memory fixture adapter (`glow_domain/chat_provider*.py`), the token rules
(`glow_domain/chat_tokens.py`) and the `glow_chat` package: an ORM persistence adapter
that carries P06.DB's send-versus-revocation design onto `glow_persistence`'s models,
and the outbox delivery to the provider port. Migration `0003` adds `ChatIdentity` and
`ChatReadCursor`; it is applied only to the disposable proof database. `glow_chat` needs
a database and runs only under `proofs/postgres-ordering`'s settings, which test it on
PostgreSQL in CI; this runtime imports none of it and keeps the dummy backend
(`tests/test_chat_sealed_runtime.py`). No route, served feature or provider call is added.
See the [data model](../../docs/architecture/data-model.md), "Chat contact and the outbox".

## Reproduce locally

Use CPython **3.12.14**, the exact version in `.python-version`. From this directory:

```bash
python3.12 --version   # Python 3.12.14
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock
GLOW_ENV=test .venv/bin/python manage.py check
GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 2
GLOW_ENV=test .venv/bin/python smoke.py
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
GLOW_ENV=test .venv/bin/python -m glow_persistence.static_check
```

The hash-locked files contain all resolved runtime/development dependencies.
`requirements.in` and `requirements-dev.in` hold exact direct pins. Lock files
were generated with uv 0.12.17 for Python 3.12 on Linux; regenerate deliberately:

```bash
uv pip compile requirements.in --python-version 3.12 --generate-hashes --output-file requirements.lock --no-header
uv pip compile requirements-dev.in --python-version 3.12 --generate-hashes --output-file requirements-dev.lock --no-header
```

Do not automatically upgrade dependencies during startup. Other operating systems
need their own install verification; this checkpoint proves Linux only.

## Run the nonpersistent smoke flow

```bash
GLOW_ENV=development .venv/bin/python -m glow_api.devserver --port 8000
```

This standard-library WSGI development server binds only to `127.0.0.1`. It does
not run Django migration checks. It is not a production server or deployment
configuration. Use a simulator's host-loopback route where supported. Physical
device network access and signed native builds remain separate work.

| Request | Result |
|---|---|
| `GET /health/live` | HTTP 200, `{"status":"alive"}` |
| `GET /health/ready` | HTTP 503, `status: not_ready`, `mode: fixture` |
| `GET /api/v1/development/recommendations` | Deterministic `gapp-dev-v1` synthetic people; compatibility is always pending, with fixture provenance |

The development endpoint is intentionally unauthenticated and contains only
invented demo records. It is not the production recommendations contract. All
three endpoints reject mutation methods and send `Cache-Control: no-store`.
No login/token/session route exists. DRF defaults deny authentication-dependent
access; only these explicit smoke views allow public reads.

`smoke.py` starts a temporary WSGI server on an OS-assigned loopback port, checks
the three HTTP responses, and shuts it down. It bypasses external proxy routing
only for these local requests. It never calls HDE or a provider.

## Configuration and boundaries

The [P03 configuration catalog](../../docs/operations/configuration.md) owns the
complete typed variable matrix and future offline profile requirements. The
core development/runtime selectors are summarized below.

| Name | Meaning |
|---|---|
| `GLOW_ENV` | Required; this baseline only permits exactly `development` or `test` |
| `GLOW_COMPATIBILITY_PROVIDER` | Optional in development/test; defaults to the sole supported value `fixture` |
| `DJANGO_SETTINGS_MODULE` | Development entrypoints select `glow_api.settings`; the artifact entrypoint rejects any other module |
| `PORT` | Artifact entrypoint only: loopback port, default 8000, valid range 1024–65535 |

Missing or invalid environment fails startup. Staging/production always fail;
fixture providers are specifically rejected there. No partial production mode
or production-secret fallback is implemented. Configuration errors do not echo
supplied values. The development settings contain a public fixture-only Django
key, unused by any authentication/session feature.

Presence of `DATABASE_URL`, `GLOW_DATABASE_URL`, `HDE_API_URL`, or `HDE_API_TOKEN`
also fails startup. Do not copy inherited service configuration into this
process. The served API uses Django's dummy database backend; PostgreSQL drivers,
auth/session routes, Celery and network HDE adapters are not installed or wired.
The separate `glow_persistence.static_settings` registry loads maintained Django
auth/contenttypes model definitions and app-owned models only for static checks.
`static_check` compares migration state without a connection and rejects cursor,
connection and schema-editor access. It never applies migrations. Do not run
`migrate` or connect any database before the governed P11 stage.

`/health/live` proves only that this process can respond. `/health/ready` never
declares fixture behavior ready for real users. Real readiness, runtime/migration
roles, allauth, provider permissions, signed builds, deployed image identity,
and production connections remain unimplemented. P03 adds the image-building
and validation path below; a build is not a deployed service.

See `../../docs/testing/api-foundation.md` for observed test evidence, version
sources and limitations.

## P03 artifact preparation

The repository-root Dockerfile and `python -m glow_api.runtime` prepare a
hash-locked Gunicorn artifact. This process is still development/test-only and
loopback-only; production/staging refuse startup and readiness remains 503.
It performs no migrations or startup database checks. See
[`build-and-deploy.md`](../../docs/operations/build-and-deploy.md) for the exact
build, container-isolation checks, port/shutdown controls, planned same-project
Railway configuration and remaining activation work. The small standard-library
development server above remains available for the established mobile smoke.
