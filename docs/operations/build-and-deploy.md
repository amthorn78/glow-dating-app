# API build and deployment preparation

P03 adds a Linux API image and a maintained Gunicorn WSGI process. This is an
isolated development artifact. Runtime still refuses staging/production, binds
only `127.0.0.1`, and reports readiness 503. It cannot be activated as a Railway
serving deployment. No app service, domain, image registry publication, live
provider, database connection, broker or migration is created by these files.

The eventual project is **ample-illumination**,
`ce01529f-679f-4f52-a979-23113299a59b`, as Nathan instructed on 23 September 2026.
App environment and service identities remain unselected/unprovisioned. See
[resource ownership](resource-ownership.md) and [environments](environments.md).
HDE, legacy services, project/environment-wide variables and shared persistence
remain protected. Being in the same project does not make shared credentials or
network connections app-owned.

## Reproducible inputs and executable scope

| Input | Committed selection and scope |
|---|---|
| Build | Repository-root `Dockerfile`, context `.`, allowlisted `.dockerignore` |
| Python base | `python:3.12.14-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e` |
| Linux amd64 member | Docker Hub reported `sha256:1aaa65a85fda306ffb8b910824d4e93bdce61e212c7e87168123ea3073b41a1a`; hosted build selects `linux/amd64` |
| Runtime packages | `services/api/requirements.lock`, hash-required binary installation; no unconstrained upgrade or compiler/build dependency resolution |
| WSGI server | Gunicorn 26.2.0, Python 3.10+; MIT wheel metadata recorded in the API dependency inventory |
| Start | Image entrypoint `python -m glow_api.runtime`, working directory `/opt/glow/api`, UID/GID `10001:10001` |
| Included code | `glow_api` and `glow_domain`; no `manage.py`, persistence models/migrations, Git history, local secrets, tests or mobile dependencies |
| Transport | Exactly `127.0.0.1:$PORT`; default 8000, ASCII decimal 1024–65535; no CLI arguments, `GUNICORN_*` overrides or foreign `DJANGO_SETTINGS_MODULE` |
| Process budgets | One sync worker, configured validated timeout, five-second graceful shutdown, 1,000-request worker recycle; no application restart loop |
| Signals and logs | Exec replaces the entrypoint with Gunicorn; SIGTERM is the image stop signal. Access logging disabled; structured allowlisted formatter discards arbitrary framework messages and exception text |
| Mobile | Existing Node 24.19.0/npm 11.9.0 pins and development guards preserved; native signing/distribution remains deferred |

The base digest was retrieved from the official
[Docker Hub tag API](https://hub.docker.com/v2/repositories/library/python/tags/3.12.14-slim-bookworm)
on 23 September 2026. This records an input digest, not an app-image build result.
Gunicorn's [release notes](https://gunicorn.org/news/) describe 26.2.2, but this
session's direct PyPI `gunicorn/26.2.2/json` request returned 404 and the available
[26.2.0 metadata](https://pypi.org/pypi/gunicorn/26.2.0/json) supplied the verified
wheel/sdist hashes. The lock resolver and installer accepted 26.2.0. Do not call
this pin the newest release. Reconcile the available patched release before
any non-loopback activation; P03 does not enable such activation. No optional
ASGI, HTTP/2, gevent or fast-parser extras are installed.

Hash-locked packages and a digest-pinned base make inputs reviewable. Builds
still download those exact packages, GitHub's runner image is managed, and
container metadata may differ between builds. This is not a claim of offline
or bit-for-bit image reproducibility. Dependency updates require new locks,
inventory review and the complete candidate checks.

## Build and inspect without exposing fixtures

From the repository root on a Linux workstation with Docker:

```bash
mkdir -p .work
docker build --platform linux/amd64 --tag glow-api:ci --iidfile .work/api-image-id .
python3 scripts/container_smoke.py glow-api:ci
```

The smoke runner inspects actual image identity/user/workdir/entrypoint, tests
missing/production/staging/database/HDE/broker configuration refusal, and starts
the image with `--network none`, no published port, read-only filesystem, a
bounded temporary `/tmp`, no Linux capabilities and no privilege escalation.
It uses `docker exec` to request container-local liveness 200, readiness 503 and
fixture recommendations; checks the listener is loopback-only, confirms absent
persistence/management source and the Python runtime; then requires clean
SIGTERM exit within a bounded deadline. It removes its container on exit. Its
reported image ID is only a runner-local build identity, not a registry digest.

Direct entrypoint tests use the installed locked runtime without Docker:

```bash
cd services/api
.venv/bin/python -m unittest tests.test_runtime -v
```

These tests execute real Gunicorn requests and shutdown, unsafe-environment
refusal and submitted sentinel redaction. They do not substitute for the
built-image check. This execution environment has no Docker/Podman daemon;
the hosted **API artifact checks** job is the required image validation path.
Check its actual outcome for the candidate before claiming a built image.

## CI and candidate operation

`Foundation` preserves **API checks**, **Mobile checks** and **API mobile smoke**
and adds **API artifact checks**. All four must pass on the actual proposed
candidate before merge under the [branch policy](ci-and-branch-policy.md).
API tests include runtime configuration, worker, webhook and telemetry cases;
P02 contract/model/static tests and deterministic contract generation remain.
The image job has a 15-minute limit and never authenticates to a registry or
publishes an image. CI has no Railway credentials or deployment action.

If a job fails, inspect that job's fixed diagnostics and reproduced failing
command, repair the cause, and rerun the changed candidate. Never turn readiness
green, weaken runtime guards or skip the artifact job to force a deployment.
P03 successful checks are no evidence of auth, persistence, native signing,
provider permission, durable outbox or restore acceptance.

## Future Railway service configuration, not an activation command

Current Railway legacy `railway.json`/`railway.toml` Config as Code is deprecated
and unavailable to new services. No such file is introduced. A whole-project
IaC apply could change omitted/shared resources and is not appropriate here.
Use app-service-specific supported configuration, after ownership and runtime
prerequisites are satisfied.

The following is a reviewed configuration draft matching the current
`update_service` tool fields. Strings beginning `REPLACE_` are explicit missing
identities, not resources, and must never be submitted. This draft does not
change the fact that the present runtime cannot serve Railway traffic:

```json
{
  "projectId": "ce01529f-679f-4f52-a979-23113299a59b",
  "environmentId": "REPLACE_WITH_VERIFIED_APP_ENVIRONMENT_ID",
  "serviceId": "REPLACE_WITH_VERIFIED_APP_SERVICE_ID",
  "rootDirectory": "/",
  "dockerfilePath": "Dockerfile",
  "startCommand": "python -m glow_api.runtime",
  "preDeployCommand": [],
  "healthcheckPath": "/health/ready",
  "healthcheckTimeout": 60,
  "restartPolicyType": "ON_FAILURE",
  "restartPolicyMaxRetries": 3,
  "watchPatterns": ["/services/api/**", "/Dockerfile", "/.dockerignore"]
}
```

Before executing later: re-list the project, select/verify the app environment,
verify an app-owned service and its consumers, and review the exact source
commit. Never duplicate the HDE production environment or inherit its services,
variables, volumes, credentials or broker. Creating a GitHub-backed service can
trigger its first deployment; source-less creation and source attachment are
separate actions with different effects. Include both service and environment
IDs on every update. Configure only service-scoped variables; review deploy
side effects before attaching source or applying variable writes.

The eventual serving implementation must separately establish its real
capabilities, safe binding, approved host/origin/healthcheck handling, secrets,
provider/persistence evidence and readiness. Do not simply edit `GLOW_ENV` or
publish the fixture port. No build/start/predeploy step may run migrations or
probe persistence. P11 owns those connections and the migration role.

The prepared deployment probe is `/health/ready`, not liveness. Railway's probe
accepts 2xx before activating a deployment and is not continuous uptime
monitoring. The present 503 deliberately prevents that acceptance. A liveness
200 only proves this process can respond. The proposed maximum three on-failure
restarts is a future service setting, not an observed Railway restart test.

## Rollback and later incident procedure

There is currently no app Railway deployment to roll back. A P03 source rollback
is a reviewed revert PR through all checks; no database rollback is implied.
For later activation, capture the exact app deployment, source commit, image
identity, service/environment IDs and last known compatible configuration
before each change. On a failed app rollout, stop the app's rollout or select
its verified previous compatible deployment only at those exact IDs. Do not
redeploy HDE or change project-wide settings. Recheck readiness and bounded
smoke after the app-only rollback. Once P11 migrations exist, follow the
[migration plan](migration-plan.md); reverting code does not undo data changes.

Gunicorn's [signal guide](https://gunicorn.org/signals/) defines graceful TERM.
Railway's [Dockerfile](https://docs.railway.com/builds/dockerfiles),
[Config as Code lifecycle](https://docs.railway.com/config-as-code/reference),
[healthcheck](https://docs.railway.com/deployments/healthchecks),
[restart policy](https://docs.railway.com/deployments/restart-policy), and
[teardown](https://docs.railway.com/deployments/deployment-teardown) references
were checked for this preparation on 23 September 2026. Local process/container
checks do not establish Railway rollout, continuous monitoring or recovery proof.
