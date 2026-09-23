# Glow API development foundation

This is a new Django/DRF API scaffold for the Glow dating application. It serves
synthetic presentation data only. There is no account authentication, persistent
storage, eligibility filtering, mutual matching, or real HDE result in this baseline.

## Reproduce locally

Use CPython **3.12.14**, the exact version in `.python-version`. From this directory:

```bash
python --version
python -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock
GLOW_ENV=test .venv/bin/python manage.py check
GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 2
GLOW_ENV=test .venv/bin/python smoke.py
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
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

| Name | Meaning |
|---|---|
| `GLOW_ENV` | Required; this baseline only permits exactly `development` or `test` |
| `GLOW_COMPATIBILITY_PROVIDER` | Optional in development/test; defaults to the sole supported value `fixture` |
| `DJANGO_SETTINGS_MODULE` | Entry points select `glow_api.settings` if not otherwise provided |

Missing or invalid environment fails startup. Staging/production always fail;
fixture providers are specifically rejected there. No partial production mode
or production-secret fallback is implemented. Configuration errors do not echo
supplied values. The development settings contain a public fixture-only Django
key, unused by any authentication/session feature.

Presence of `DATABASE_URL`, `GLOW_DATABASE_URL`, `HDE_API_URL`, or `HDE_API_TOKEN`
also fails startup. Do not copy inherited service configuration into this
process. Django uses its dummy database backend; SQLite, PostgreSQL, auth,
sessions, Celery and network HDE adapters are not installed or wired. Do not run
`migrate` or connect a database before the governed P11 stage.

`/health/live` proves only that this process can respond. `/health/ready` never
declares fixture behavior ready for real users. Real readiness, runtime/migration
roles, allauth, provider permissions, signed builds, deployment image digest,
and production connections remain unimplemented.

See `../../docs/testing/api-foundation.md` for observed test evidence, version
sources and limitations.
