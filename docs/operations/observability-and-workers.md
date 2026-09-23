# Structured telemetry and bounded worker preparation

P03 preparation adds `glow_api.telemetry` and `glow_domain.worker_execution`.
There is no configured telemetry vendor, exported metric endpoint, live worker,
Celery broker, persisted queue or application database. The served routes remain
development fixtures. Liveness remains 200 and readiness remains 503 with the
existing response bodies. Neither telemetry nor worker simulations prove service
capacity, durable delivery or production readiness.

## Safe logging and correlation

`emit_event(Event, **fields)` validates a closed set of event and field names and
values before handing a record to logging. `SafeJsonFormatter` validates that
payload again at the output boundary. JSON lines go to stderr. Unknown/framework
logging becomes a fixed `framework_diagnostic` with severity. Message templates,
arguments, logger names, source paths, stack/exception text, arbitrary extras and
request objects are never formatted. A malformed custom record becomes a fixed
diagnostic rather than partially passing its fields through.

The settings loader installs this sink before configuration validation, then
Django installs the same logging configuration. Django request/security/server
and Gunicorn error logging use the safe sink; access-log output is disabled for
the managed Gunicorn entrypoint. Existing uncontrolled logger handlers are
disabled. New third-party libraries must be reviewed for their own handlers,
direct stdout/stderr writes and automatic payload capture before activation;
this is not a claim that any future SDK is automatically safe.

The loopback development WSGI server disables raw access logging. Its error
stream discards traceback fragments and reports one fixed server error. Its
server exception handler also emits only a fixed code. Parser rejections emit a
fixed rejection code. The `--ready-json` stdout handshake retains its original
event, pid, host and bound port fields for the development smoke harness. That
handshake describes bound loopback startup, never application readiness.

The first Django middleware accepts only one lowercase canonical 36-character
UUIDv4 in `X-Correlation-ID`. Missing, noncanonical, wrong-version, multiple,
overlong or malformed values get a newly generated UUIDv4. It returns the value
in the response header and uses a `ContextVar` that is reset after every request,
including errors. Correlation metadata is client-influenced tracing information,
not account identity, authentication, permission or a deduplication key. No
request body, query, header value, raw URL or remote address is logged. Only the
three exact served paths map to named routes; all other paths become `unmatched`.

Configuration rejection emits only the fixed `configuration_invalid` telemetry
code. The configuration exception retains its separately sanitized diagnostic.
Do not log environment mappings, provider exception strings, birth inputs,
private locations, contact/session/authorization tokens, provider credentials,
chat content, SQL parameters or arbitrary submitted text. No logging API accepts
an arbitrary `message`, `payload`, `request` or exception field.

## Event, error and metric vocabulary

| Event | Useful measurements and dimensions |
|---|---|
| `request_completed` | Count and `duration_ms`; route, method, status class, outcome and component |
| `request_failed` | Count of uncaught middleware failures with the fixed `unexpected_failure` code |
| `configuration_rejected` | Count with fixed rejection outcome and configuration code |
| `worker_attempt` | Count and attempt number |
| `worker_retry` | Count and bounded backoff delay; declared provider failure code |
| `worker_completed` | Count and elapsed milliseconds; terminal outcome, attempts and failure code |
| `framework_diagnostic`, `server_error` | Count/severity of framework or WSGI failures without the raw diagnostic |

Allowed methods and routes are finite. Status classes are `1xx` through `5xx` or
`unknown`; arbitrary codes are not labels. `metric_labels` returns only the
validated event/component/route/method/status/outcome/error dimensions and removes
correlation IDs, durations, delays and attempt counts. No account, work,
idempotency, chart, request or provider object ID is a metric label. Counts and
duration aggregation can later consume these events; no remote collector or
alerting installation is claimed. Request/worker durations are clipped to
300,000 ms and delays to 30,000 ms for bounded telemetry, not service objectives.

Provider failure codes reuse the P02 `FailureCode` enum. Only `timeout` and
`outage` are retryable. `unsupported`, `malformed_output`, `identity_mismatch`,
`stale`, `consent_required` and `idempotency_conflict` stop immediately. Executor
outcomes distinguish success, permanent failure, attempts exhausted, deadline
exceeded and cancellation. Unknown callback faults raise `WorkerExecutionError`
with fixed text, suppressed exception chaining and no retry. They do not become
an expected outage or successful fixture result. A separate sanitized error
workflow may be added later; do not enable automatic traceback/local-variable
capture as a debugging shortcut.

## Worker execution contract

Call `execute_with_retry(operation, idempotency_key=..., budget=...)` with an
explicit `RetryBudget`. Monotonic time, sleep, cancellation and observation are
injectable. `observe_worker` connects typed observations to safe telemetry. The
executor performs no I/O itself except the explicitly injected/default sleep.

The preparation bounds are 1–5 attempts, a total deadline of up to 300 seconds,
a per-attempt timeout of up to 60 seconds and positive exponential backoff capped
at 30 seconds. The per-attempt timeout cannot exceed the total deadline. NaN,
infinity, booleans, zero/negative and contradictory values reject. These are
interface guardrails for the substitute, not provider-approved retries, queue
budgets, capacity measurements or release policy. The eventual adapter must
apply the narrower supported provider and application configuration limits.

Every operation receives `AttemptContext` containing the attempt number, absolute
monotonic deadline, remaining timeout and unchanged opaque idempotency key. The
key is bounded to 128 printable ASCII characters and excluded from repr and all
telemetry. Each callback must acquire current consent/eligibility and other
required state before work, including repeated delivery; a previous success
never supplies new authorization. It must enforce the supplied timeout in its
actual provider transport. The executor does not wrap, replace or weaken P02's
pair/version checks or its nonpersistent fixture retry helper.

Cancellation is checked before work, after callbacks and during backoff in
intervals of at most 100 ms of requested sleep. Backoff does not schedule a retry
whose delay consumes the remaining deadline. A single captured remaining time
prevents negative sleep if the clock crosses the target while it is inspected.
Nonfinite or backward clocks fail loudly. A late success is discarded as a
deadline outcome and is not automatically retried.

These are **cooperative** limits: a blocking synchronous callback or scheduler
cannot be forcibly interrupted by this helper. An adapter must honor its timeout
and support its required cancellation mechanism. Cancellation or deadline after
a provider call can leave an uncertain external effect. Reconcile the stable
idempotency key and current state before any subsequent scheduling; do not infer
that a missing accepted result means nothing happened.

## Duplicate delivery and operational response

The executor deliberately has no result cache, work ledger, leases or fake
transaction machinery. Its tests use one small dictionary to show an explicitly
synthetic idempotent callback receiving duplicate work and checking current
authorization again. That dictionary disappears on process restart, is not
concurrent and proves no provider exactly-once guarantee. Durable payload-bound
deduplication and conflict detection belong to the P02 inbox/outbox/UOW design
and later provider contract.

For a repeated transient failure, inspect the bounded failure code and stop at
the recorded attempt/deadline result. For a permanent failure, resolve that
specific state or supported-contract issue before scheduling new work. For an
unknown failure, stop the affected path and reproduce using synthetic data;
do not turn on raw payload/exception logging. For cancellation or uncertain
completion, retain the future durable obligation for reconciliation rather than
declaring it finished. Actual queues/dead-letter operations cannot be performed
by this substitute.

The existing deferred cases remain unexecuted: **DB07** (transaction/outbox crash
recovery), **DB08** (duplicate/out-of-order durable inbox processing), **DB12**
(real timeout, contention and lease recovery), **DB13** (restore/tombstone replay)
and the applicable **PV01–PV08** provider cases. P03 does not mark them passed.

## Reproduce and evidence boundary

From `services/api/`, using the repository's hash-locked development environment:

```bash
GLOW_ENV=test .venv/bin/python manage.py test tests.test_worker_execution tests.test_telemetry --verbosity 2
.venv/bin/ruff check glow_api/telemetry.py glow_api/settings.py glow_api/devserver.py glow_domain/worker_execution.py tests/test_worker_execution.py tests/test_telemetry.py
.venv/bin/mypy glow_api/telemetry.py glow_api/settings.py glow_api/devserver.py glow_domain/worker_execution.py
```

When the environment is installed at repository root, substitute `../../.venv/`
for `.venv/` in these commands. New tests cover success/failure/configuration and
retry sentinels, Django 400/404/500 responses, actual loopback WSGI exception
handling, bounded/canonical correlations, ContextVar cleanup, metric label
exclusion, budgets, advancing/broken clocks, cancellation, late results and the
duplicate callback substitute. Network access is forbidden in worker unit tests;
the WSGI case uses an OS-assigned loopback port. Full publication and exact
candidate evidence belongs to the enclosing P03 checkpoint.

Sources inspected for framework behavior: [Django 5.2 logging](https://docs.djangoproject.com/en/5.2/ref/logging/)
and [Python 3.12 WSGI reference](https://docs.python.org/3.12/library/wsgiref.html).
Default framework request/exception capture and WSGI traceback output are the
reason the output sinks are replaced rather than only redacting selected fields
inside application calls.
