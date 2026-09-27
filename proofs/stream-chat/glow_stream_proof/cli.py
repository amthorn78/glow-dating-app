"""Command line entry point: ``python -m glow_stream_proof <command>``.

Read-only: ``baseline``, ``verify-clean``, ``probe-products``, ``configure`` and
``restore`` without ``--apply`` (they print the plan). Mutating: ``configure --apply``,
``configure --products video,feeds --apply``, ``run``, ``cleanup --apply`` and
``restore --apply``. ``record-baseline`` and ``record-products-baseline`` write files
from a snapshot and call nothing.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import baseline, configuration, guard, products, report
from .credentials import EnvironmentRefused, ServerCredentials, load_server_credentials
from .proof_run import PREFIX_ROOT, ProofRun, RunStopped, lean_only, list_polls_and_groups
from .redaction import Redactor
from .server_api import ServerApi
from .stops import GuardRefused
from .usage import GuardrailStop, UsageLedger
from .workdir import PROOF_ROOT, WORK_DIR, checked_text, write_json, write_text

LEDGER = WORK_DIR / "usage-ledger.json"
BASELINE_RECORD = configuration.BASELINE_RECORD
BASELINE_DIR = BASELINE_RECORD.parent
EXIT_REFUSED = 2


def _stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


class Context:
    def __init__(self, environ: Mapping[str, str] | None = None) -> None:
        self.credentials: ServerCredentials = load_server_credentials(
            os.environ if environ is None else environ
        )
        self.secrets = [self.credentials.secret()]
        # The API key is removed from free text too (P06.1-I2b): Stream's code-43
        # message quotes it.
        self.redactor = Redactor(self.secrets, api_key=self.credentials.api_key)
        self.ledger = UsageLedger.load(LEDGER)
        self.api = ServerApi(self.credentials, self.ledger, self.redactor)

    def say(self, text: str) -> None:
        print(checked_text(self.redactor.text(text), self.secrets))

    def close(self) -> None:
        self.api.close()


def _print_plan(ctx: Context, plan: list[configuration.ApiRequest]) -> None:
    for step in plan:
        ctx.say(f"- {step.method} {step.path}: {step.purpose}")
        ctx.say("  body: " + json.dumps(step.body, sort_keys=True))


class StepRefused(RuntimeError):
    """Stream answered a configuration step with a status that is not 2xx and is no
    charge or limit signal; the apply stops there (P06.1-C4 names it so that a configure
    record can tell it from a stop that must reach ``main``)."""


def _apply(
    ctx: Context,
    plan: list[configuration.ApiRequest],
    applied: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Send the plan in order and stop at the first failure. Each answered step joins
    ``applied`` as it is answered, so a caller that keeps the list still has the steps
    applied so far when a later step fails or raises (P06.1-C4)."""
    applied = [] if applied is None else applied
    for step in plan:
        try:
            result = ctx.api.raw(step.method, step.path, body=step.body)
        except BaseException as exc:
            # The step was sent (or refused before it was sent) and raised: a charge or limit
            # signal's stop, the guard's refusal, a Ctrl-C. It joins the list with what
            # stopped it (C4's own review: the signalling step was missing from the record).
            applied.append(
                {
                    "method": step.method,
                    "path": step.path,
                    "status": None,
                    "stopped": ctx.redactor.text(f"{type(exc).__name__}: {exc}"),
                }
            )
            raise
        applied.append(
            {
                "method": step.method,
                "path": step.path,
                "status": result.status,
                "code": result.code,
                "message": result.message,
            }
        )
        ctx.say(
            f"{step.method} {step.path} -> {result.status}"
            + (f" code {result.code}: {result.message}" if not result.ok else "")
        )
        if not result.ok:
            raise StepRefused(f"{step.method} {step.path} failed; stopping")
    return applied


# What a configure record says when it does not re-read the application (P06.1-C4; the
# manager's addition to the I2b review's nit 8): a charge or limit signal stops at once
# and the ledger refuses no later request, so nothing more is sent.
AFTER_NOT_READ_SIGNAL = "after-state not read: a charge or limit signal was met"
AFTER_NOT_READ_INTERRUPTED = "after-state not read: the command was interrupted"


class _Applied:
    """The outcome of a configure plan's apply: the steps answered, the failure if one
    ended it, and whether a charge or limit signal was met (from the ledger's recorded
    signals, not only from the exception's type)."""

    def __init__(self) -> None:
        self.steps: list[dict[str, Any]] = []
        self.failure: BaseException | None = None
        # What the re-read raised when an earlier failure (a refused step) already ended the
        # apply: a signal's stop or a Ctrl-C here must still reach main (C4's own review).
        self.reread_failure: BaseException | None = None
        self.signal = False

    def failure_text(self, ctx: Context) -> str | None:
        if self.failure is None:
            return None
        return ctx.redactor.text(f"{type(self.failure).__name__}: {self.failure}")

    def may_read_after(self, ctx: Context) -> str | None:
        """``None`` when the re-read may be sent, or why it may not."""
        self.signal = self.signal or bool(ctx.ledger.signals)
        if self.signal:
            return AFTER_NOT_READ_SIGNAL
        if self.failure is not None and not isinstance(self.failure, Exception):
            return AFTER_NOT_READ_INTERRUPTED  # Ctrl-C: send nothing more
        return None

    def finish(self) -> int | None:
        """Re-raise what must reach ``main`` (a signal's stop, the guard's refusal, a
        Ctrl-C), after the record is written; 1 for a step Stream refused; ``None`` when
        every step succeeded."""
        later = self.reread_failure
        if later is not None and (
            isinstance(later, GuardrailStop) or not isinstance(later, Exception)
        ):
            raise later
        if self.failure is None:
            return None
        if isinstance(self.failure, StepRefused):
            return 1
        raise self.failure


def _apply_recorded(ctx: Context, plan: list[configuration.ApiRequest]) -> _Applied:
    """Apply the plan, keeping what happened even when a step fails or raises."""
    outcome = _Applied()
    try:
        _apply(ctx, plan, outcome.steps)
    except BaseException as exc:  # recorded, then re-raised by finish() after the record
        outcome.failure = exc
    return outcome


def _read_after(
    ctx: Context, outcome: _Applied, read: Any
) -> tuple[dict[str, Any] | None, str | None]:
    """The re-read after an apply, unless a charge or limit signal was met or the command
    was interrupted; a re-read that itself fails or meets a signal is recorded, not
    raised."""
    why = outcome.may_read_after(ctx)
    if why is not None:
        return None, why
    try:
        return read(ctx.api), None
    except BaseException as exc:  # recorded; finish() re-raises it after the record
        outcome.signal = outcome.signal or bool(ctx.ledger.signals)
        if outcome.failure is None:
            outcome.failure = exc
        else:
            outcome.reread_failure = exc
        if outcome.signal:
            return None, AFTER_NOT_READ_SIGNAL
        if not isinstance(exc, Exception):
            # A Ctrl-C during the re-read (C4's own review): the record is still written.
            return None, AFTER_NOT_READ_INTERRUPTED
        text = ctx.redactor.text(f"{type(exc).__name__}: {exc}")
        return None, f"after-state not read: the re-read failed: {text}"


def _settings_view(snapshot: dict[str, Any]) -> dict[str, Any]:
    app = snapshot["app"]["app"]
    return {
        "settings": {k: app.get(k) for k in configuration.APP_SETTING_KEYS if k in app},
        "app_grants": {r: app["grants"].get(r, []) for r in configuration.CLIENT_APP_ROLES},
        "types": sorted(snapshot["channel_types"]["channel_types"].keys()),
    }


def _say_products(ctx: Context, state: Mapping[str, Any]) -> None:
    for product in products.PRODUCTS:
        entry = state.get(product) or {}
        ctx.say(f"{product}: {entry.get('availability')}")
    ctx.say(f"video call types: {sorted(state['video']['call_types'])}")
    ctx.say(f"feed visibilities: {sorted(state['feeds']['feed_visibilities'])}")
    ctx.say(f"feed groups: {sorted(state['feeds']['feed_groups'])}")


def cmd_baseline(ctx: Context) -> int:
    snapshot = baseline.read_snapshot(ctx.api)
    # Written without other users' identifiers, names or custom fields.
    public = baseline.public_snapshot(snapshot, PREFIX_ROOT)
    path = write_json(f"snapshot-{_stamp()}.json", public, ctx.secrets)
    ctx.say(f"snapshot written to {path.relative_to(PROOF_ROOT)}")
    ctx.say("settings: " + json.dumps(_settings_view(snapshot)["settings"], sort_keys=True))
    ctx.say(
        f"configuration differences from the proof's target: {len(configuration.verify(snapshot))}"
    )
    # The Video and Feeds configuration is part of the snapshot (P06.1-I2b): settings and
    # grants only, no user and no data.
    _say_products(ctx, snapshot["products"])
    ctx.say(
        "video and feeds differences from the lockdown target: "
        f"{len(products.verify(snapshot['products']))}"
    )
    return 0


def cmd_record_products_baseline(ctx: Context, snapshot_path: Path) -> int:
    """Write the Video and Feeds baseline record from a ``baseline`` snapshot (P06.1-I2b):
    ``baseline/video-feeds-<app>-<date>.json``, settings and grants only. Calls nothing."""
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    state = snapshot.get("products")
    if not isinstance(state, dict):
        ctx.say("refused: the snapshot holds no products section")
        return EXIT_REFUSED
    record = products.baseline_record(state, ctx.credentials.app_id)
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    path = BASELINE_DIR / (
        f"video-feeds-{ctx.credentials.app_id}-{datetime.now(UTC).strftime('%Y-%m-%d')}.json"
    )
    text = checked_text(json.dumps(record, indent=2, sort_keys=True) + "\n", ctx.secrets)
    path.write_text(text, encoding="utf-8")
    shown = path.relative_to(PROOF_ROOT) if path.is_relative_to(PROOF_ROOT) else path
    ctx.say(f"video and feeds baseline record written to {shown}")
    return 0


def cmd_probe_products(ctx: Context) -> int:
    """The availability probe (the I2b prompt, section 5): one read-only server request
    per product, recorded; it decides whether that product's cases run at all."""
    probe = products.probe(ctx.api)
    path = write_json(f"probe-products-{_stamp()}.json", probe, ctx.secrets)
    ctx.say(f"probe written to {path.relative_to(PROOF_ROOT)}")
    for product in products.PRODUCTS:
        entry = probe[product]
        ctx.say(
            f"{product}: {entry['availability']} ({entry['request']} -> HTTP "
            f"{entry['answer']['status']} code {entry['answer']['code']})"
        )
    ctx.say(f"video call types: {probe['video']['call_types']}")
    ctx.say(f"feed visibilities: {probe['feeds']['feed_visibilities']}")
    ctx.say(f"feed groups: {probe['feeds']['feed_groups']}")
    return 0


def cmd_record_baseline(ctx: Context, snapshot_path: Path) -> int:
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    record = configuration.baseline_record(snapshot)
    BASELINE_RECORD.parent.mkdir(parents=True, exist_ok=True)
    text = checked_text(json.dumps(record, indent=2, sort_keys=True) + "\n", ctx.secrets)
    BASELINE_RECORD.write_text(text, encoding="utf-8")
    ctx.say(f"baseline record written to {BASELINE_RECORD.relative_to(PROOF_ROOT)}")
    return 0


def cmd_configure(ctx: Context, apply: bool, scope: list[str] | None = None) -> int:
    if scope is not None:
        unknown = sorted(set(scope) - set(products.PRODUCTS))
        if unknown or not scope:
            ctx.say(f"refused: --products names {unknown or 'nothing'}; only video and feeds")
            return EXIT_REFUSED
    before = baseline.read_snapshot(ctx.api)
    if scope is not None:
        return _configure_products(ctx, before, apply, scope)
    plan = configuration.apply_plan(before)
    ctx.say(f"differences before: {configuration.verify(before)}")
    if not apply:
        ctx.say("plan (dry run; pass --apply to change the application):")
        _print_plan(ctx, plan)
        return 0
    # The general apply re-sends the whole chat target (the application PATCH, the five
    # default types and glow-match); it is the operator command that reapplies the chat
    # configuration, outside the guard, and P06.1-I2b never runs it (DM-05 finding 1).
    # A step that fails, or a charge or limit signal, still leaves the record: the steps
    # applied so far, the failure and the after-state, which is re-read only when no
    # signal was met (P06.1-C4; the I2b review's nit 8, with the manager's addition).
    outcome = _apply_recorded(ctx, plan)
    after, not_read = _read_after(ctx, outcome, baseline.read_snapshot)
    record: dict[str, Any] = {
        "at": _stamp(),
        "before": _settings_view(before),
        "applied": outcome.steps,
    }
    if outcome.failure is not None:
        record["failure"] = outcome.failure_text(ctx)
    if outcome.reread_failure is not None:
        failed_reread = outcome.reread_failure
        record["reread_failure"] = ctx.redactor.text(
            f"{type(failed_reread).__name__}: {failed_reread}"
        )
    problems: list[str] | None = None
    if after is not None:
        problems = configuration.verify(after)
        record["after"] = _settings_view(after)
        record["after_match_type"] = after["channel_types"]["channel_types"].get(
            configuration.MATCH_TYPE
        )
        record["after_default_type_grants"] = {
            name: after["channel_types"]["channel_types"][name]["grants"]
            for name in configuration.DEFAULT_TYPES
        }
    else:
        record["after"] = not_read
    record["problems_after"] = problems
    path = write_json(f"configure-{record['at']}.json", record, ctx.secrets)
    ctx.say(f"configuration record written to {path.relative_to(PROOF_ROOT)}")
    if outcome.failure is not None:
        ctx.say(f"the apply did not complete: {record['failure']}")
    ctx.say(f"differences after: {problems if problems is not None else not_read}")
    failed = outcome.finish()
    if failed is not None:
        return failed
    return 0 if not problems else 1


def _configure_products(ctx: Context, before: dict[str, Any], apply: bool, scope: list[str]) -> int:
    """``configure --products video,feeds`` (P06.1-I2b; DM-05 finding 1): a scoped,
    differential plan of Video and Feeds configuration writes only. The dry run prints
    the plan and the chat verification. ``--apply`` refuses, in code, while the chat
    configuration does not verify, or if any planned request is outside the two
    configuration families; it then sends the plan through the guard's configure scope,
    re-reads and verifies chat and both products."""
    # The chat verification alone gates the apply: once the lockdown is recorded as
    # applied, verify() would name the products' own drift, which the apply is for (the
    # independent check of I2b, nit 5).
    chat_problems = [p for p in configuration.verify(before) if not p.startswith("video/feeds: ")]
    ctx.say(f"differences before: {chat_problems}")
    state = before["products"]
    _say_products(ctx, state)
    ctx.say(f"video and feeds differences before: {products.verify(state)}")
    # Each planned step names its product first in its purpose ("video: ...").
    plan = [step for step in products.lockdown_plan(state) if step.purpose.split(":")[0] in scope]
    if plan:
        ctx.say("video and feeds plan (a difference; dry run unless --apply):")
        _print_plan(ctx, plan)
    else:
        ctx.say("video and feeds plan: nothing to change")
    if not apply:
        return 0
    if chat_problems:
        ctx.say("refused: the chat configuration does not verify; nothing applied")
        return EXIT_REFUSED
    outside = [
        f"{step.method} {step.path}"
        for step in plan
        if not products.is_configuration_write(step.method, step.path)
    ]
    if outside:
        ctx.say(
            "refused: a planned request is outside the Video and Feeds configuration "
            f"families: {outside}; nothing applied"
        )
        return EXIT_REFUSED
    if not plan:
        ctx.say("nothing to apply")
        return 0
    # The guard's configure scope: only a call type's or a feed visibility's grants.
    configure_scope = guard.ConfigureScope(PREFIX_ROOT)
    ctx.api.guard = lambda method, path, body, params: guard.refusal(
        method, path, body, params, configure_scope
    )
    # A step that fails, or a charge or limit signal, still leaves the record (P06.1-C4;
    # the I2b review's nit 8, with the manager's addition): the re-read runs only when no
    # signal was met. The record keeps the full before- and after-state in
    # products.baseline_record's shape, every role and setting (the I2b review's
    # finding 2), and is scanned like every other record.
    outcome = _apply_recorded(ctx, plan)
    after, not_read = _read_after(ctx, outcome, baseline.read_configuration)
    record: dict[str, Any] = {
        "at": _stamp(),
        "scope": sorted(scope),
        "before": products.baseline_record(state, ctx.credentials.app_id),
        "applied": outcome.steps,
    }
    if outcome.failure is not None:
        record["failure"] = outcome.failure_text(ctx)
    if outcome.reread_failure is not None:
        failed_reread = outcome.reread_failure
        record["reread_failure"] = ctx.redactor.text(
            f"{type(failed_reread).__name__}: {failed_reread}"
        )
    problems: list[str] | None = None
    if after is not None:
        problems = configuration.verify(after)
        if products.LOCKDOWN_APPLIED is None:
            # Until the commit that records the apply, verify() leaves the products out.
            problems += configuration.product_differences(after, locked=True)
        record["after"] = products.baseline_record(after["products"], ctx.credentials.app_id)
    else:
        record["after"] = not_read
    record["problems_after"] = problems
    path = write_json(f"configure-products-{record['at']}.json", record, ctx.secrets)
    ctx.say(f"configuration record written to {path.relative_to(PROOF_ROOT)}")
    if outcome.failure is not None:
        ctx.say(f"the apply did not complete: {record['failure']}")
    ctx.say(f"differences after: {problems if problems is not None else not_read}")
    failed = outcome.finish()
    if failed is not None:
        return failed
    return 0 if not problems else 1


EXIT_STOPPED = 2
EXIT_AFTER_RUN_PROBLEMS = 4


def cmd_run(ctx: Context, accept_dashboard_user: bool, only: set[str] | None) -> int:
    """One run. Exit 0 only if it completed, was cleaned up and the configuration
    verifies; 2 if it stopped; 4 if it completed but a check after it failed."""
    prefix = f"{PREFIX_ROOT}{datetime.now(UTC).strftime('%m%d%H%M%S')}"
    lean = lean_only(only)
    run = ProofRun(
        ctx.credentials,
        ctx.api,
        ctx.ledger,
        ctx.redactor,
        os.environ,
        prefix=prefix,
        accept_dashboard_user=accept_dashboard_user,
        lean=lean,
    )
    started = datetime.now(UTC).isoformat(timespec="seconds")
    ctx.say(f"run {prefix} started {started}")
    if lean:
        ctx.say("a Video and Feeds run: lean setup (users A and B, no channel)")
    stop_reason = None
    cleanup_needed = False

    def progress() -> None:
        write_json(f"run-{prefix}-progress.json", run.results(), ctx.secrets)

    try:
        preflight = run.preflight()
        ctx.say(f"preflight: {preflight}")
        cleanup_needed = True
        run.setup()
        run.authorized_path()
        progress()
        run.run_matrix(only, progress)
    except RunStopped as exc:
        stop_reason = f"stopped: {ctx.redactor.text(str(exc))}"
    except GuardrailStop as exc:
        stop_reason = f"guardrail: {ctx.redactor.text(str(exc))}"
        # A charge or limit signal joins the run's record; finish() skips the
        # cleanup after any signal in it, wherever it was met (P06.1-C3: until then
        # only this stop's own type counted).
        run.record_signal(exc)
    except KeyboardInterrupt:
        stop_reason = "interrupted (Ctrl-C)"
    except Exception as exc:  # recorded, never hidden; cleanup still runs
        stop_reason = f"harness error: {type(exc).__name__}: {ctx.redactor.text(str(exc))}"
    finally:
        # The results so far are written first, so that nothing observed is lost
        # if the end of the run is interrupted (P06.1-C2); they are rewritten below.
        try:
            early = run.results()
            early.update(
                {
                    "started": started,
                    "stop_reason": stop_reason,
                    "end_of_run": "not finished: restores, cleanup and the configuration "
                    "check had not completed when this was written",
                }
            )
            write_json(f"run-{prefix}.json", early, ctx.secrets)
        except (Exception, KeyboardInterrupt) as exc:  # never in the way of the restores below
            run.notes.append(
                "results not written before the end of the run: "
                f"{type(exc).__name__}: {ctx.redactor.text(str(exc))}"
            )
        # Every run ends here: journalled temporary changes are restored and
        # verified, the run's data is cleaned up (not after a charge or limit
        # signal), and the configuration is verified, whatever stopped the run.
        try:
            problems = run.finish(cleanup=cleanup_needed)
        except KeyboardInterrupt:
            # A second Ctrl-C: the end of the run stops here, except closing the
            # client processes; what is known is written below.
            stop_reason = stop_reason or "interrupted (Ctrl-C)"
            problems = [
                "the end of the run was interrupted (Ctrl-C): restores, cleanup and the "
                "configuration check may be incomplete; run configure (a dry run) and "
                "verify-clean",
                *run.post_run_problems,
            ]
            run.post_run_problems = problems
            run.close_sessions()
    ctx.say(f"cleanup: {run.cleanup_result}")
    for stop in run.stops:
        ctx.say(f"stop recorded: {stop}")
    for problem in problems:
        ctx.say(f"after the run: {problem}")
    ended = datetime.now(UTC).isoformat(timespec="seconds")
    results = run.results()
    results.update({"started": started, "ended": ended, "stop_reason": stop_reason})
    write_json(f"run-{prefix}.json", results, ctx.secrets)
    markdown = report.render(results)
    write_text(f"run-{prefix}.md", markdown, ctx.secrets)
    ctx.say(markdown)
    ctx.say(f"usage: {json.dumps(ctx.ledger.summary())}")
    ctx.say(f"run {prefix} ended {ended}" + (f"; {stop_reason}" if stop_reason else ""))
    if stop_reason is not None:
        return EXIT_STOPPED
    return EXIT_AFTER_RUN_PROBLEMS if problems else 0


def cmd_verify_clean(ctx: Context) -> int:
    snapshot = baseline.read_snapshot(ctx.api)
    users = [str(u.get("id")) for u in snapshot["users"].get("users", [])]
    # Stream prefixes guest IDs ("guest-<uuid>-<requested id>"), so match anywhere.
    proof_users = [u for u in users if PREFIX_ROOT in u]
    channels = [str(c["channel"]["cid"]) for c in snapshot["channels"].get("channels", [])]
    listed = {
        **list_polls_and_groups(ctx.api),
        **products.list_objects(ctx.api, snapshot.get("products")),
    }
    ctx.say(f"proof users remaining: {proof_users}")
    ctx.say(f"channels remaining: {channels}")
    ctx.say(f"other users present: {len(users) - len(proof_users)}")
    for key in ("polls", "user_groups", *products.OBJECT_KINDS):
        remaining = listed[f"remaining_{key}"]
        shown = remaining if remaining is not None else listed[f"{key}_listing"]
        ctx.say(f"{key} remaining: {shown}")
    if listed["remaining_polls"] is None:
        # Stream's server-side Query Polls needs a user, and the proof never uses the
        # dashboard user; a run's cleanup lists polls as each of its own users before
        # their delete and reads each recorded poll by ID (P06.1-I2b).
        ctx.say(
            "polls: the standalone listing needs a user; a run's cleanup lists polls as each "
            "of its own users before their delete and reads each recorded poll by ID"
        )
    clean = not proof_users and not channels
    clean = clean and listed["remaining_polls"] == [] and listed["remaining_user_groups"] == []
    for kind in products.OBJECT_KINDS:
        # A product that is not available can hold no object (P06.1-I2b).
        if listed[f"remaining_{kind}"] is None:
            clean = clean and str(listed[f"{kind}_listing"]).startswith("not available")
        else:
            clean = clean and listed[f"remaining_{kind}"] == []
    return 0 if clean else 1


def cmd_cleanup(ctx: Context, apply: bool) -> int:
    snapshot = baseline.read_snapshot(ctx.api)
    users = [
        str(u["id"]) for u in snapshot["users"].get("users", []) if PREFIX_ROOT in str(u["id"])
    ]
    cids = [
        str(c["channel"]["cid"])
        for c in snapshot["channels"].get("channels", [])
        if PREFIX_ROOT in str(c["channel"]["cid"])
    ]
    ctx.say(f"proof users: {users}; proof channels: {cids}")
    # The products' objects whose IDs carry the prefix (P06.1-I2b); an activity has a
    # server ID, so the run users' Feeds data delete removes theirs.
    objects = products.list_objects(ctx.api, snapshot.get("products"))
    calls = [c for c in objects.get("remaining_calls") or [] if PREFIX_ROOT in c]
    feeds = [f for f in objects.get("remaining_feeds") or [] if PREFIX_ROOT in f]
    activities = objects.get("remaining_activities")
    ctx.say(
        f"proof calls: {calls}; proof feeds: {feeds}; activities present: "
        f"{len(activities) if activities is not None else objects.get('activities_listing')}"
    )
    if not apply:
        ctx.say("dry run; pass --apply to hard-delete them")
        return 0
    # Only what carries the proof's prefix may be deleted (P06.1-I2a; DM-04 finding 1).
    scope = guard.PrefixScope(PREFIX_ROOT)
    ctx.api.guard = lambda method, path, body, params: guard.refusal(
        method, path, body, params, scope
    )
    for cid in calls:
        call_type, _, call_id = cid.partition(":")
        res = ctx.api.raw(
            "POST", f"/api/v2/video/call/{call_type}/{call_id}/delete", body={"hard": True}
        )
        ctx.say(f"call delete -> {res.status}")
    for fid in feeds:
        group, _, feed_id = fid.partition(":")
        res = ctx.api.raw(
            "DELETE",
            f"/api/v2/feeds/feed_groups/{group}/feeds/{feed_id}",
            params={"hard_delete": "true"},
        )
        ctx.say(f"feed delete -> {res.status}")
    if feeds or (activities and users):
        for user_id in users:
            res = ctx.api.raw("POST", f"/api/v2/feeds/users/{user_id}/delete", body={})
            ctx.say(f"feeds user data delete -> {res.status}")
    if cids:
        res = ctx.api.raw(
            "POST", "/api/v2/chat/channels/delete", body={"cids": cids, "hard_delete": True}
        )
        ctx.say(f"channels delete -> {res.status}")
    if users:
        res = ctx.api.raw(
            "POST",
            "/api/v2/users/delete",
            body={"user_ids": users, "user": "hard", "messages": "hard", "conversations": "hard"},
        )
        ctx.say(f"users delete -> {res.status}")
    return 0


def cmd_restore(ctx: Context, apply: bool, delete_match_type: bool) -> int:
    record = json.loads(BASELINE_RECORD.read_text(encoding="utf-8"))
    plan = configuration.restore_plan(record, delete_match_type=delete_match_type)
    if not apply:
        ctx.say("restore plan (dry run; pass --apply to change the application):")
        _print_plan(ctx, plan)
        return 0
    _apply(ctx, plan)
    after = baseline.read_configuration(ctx.api)
    problems = configuration.verify_restored(after, record, match_type_deleted=delete_match_type)
    ctx.say(f"differences from the recorded baseline after restore: {problems}")
    return 0 if not problems else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="glow_stream_proof")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("baseline", help="read-only snapshot of settings, types, roles and data")
    rec = sub.add_parser("record-baseline", help="write the restore record from a snapshot")
    rec.add_argument("--snapshot", type=Path, required=True)
    conf = sub.add_parser("configure", help="plan (or --apply) the proof's configuration")
    conf.add_argument("--apply", action="store_true")
    conf.add_argument(
        "--products",
        default=None,
        help="scoped, differential: only Video and Feeds configuration writes (video,feeds)",
    )
    sub.add_parser("probe-products", help="read-only: is each of Video and Feeds available?")
    prec = sub.add_parser(
        "record-products-baseline", help="write the Video and Feeds baseline from a snapshot"
    )
    prec.add_argument("--snapshot", type=Path, required=True)
    run = sub.add_parser("run", help="one live proof run with cleanup")
    run.add_argument("--accept-dashboard-user", action="store_true")
    run.add_argument("--only", default="", help="comma-separated case ids (development)")
    sub.add_parser("verify-clean", help="confirm no proof users or channels remain")
    clean = sub.add_parser("cleanup", help="hard-delete leftover proof users and channels")
    clean.add_argument("--apply", action="store_true")
    restore = sub.add_parser("restore", help="plan (or --apply) restoring the recorded baseline")
    restore.add_argument("--apply", action="store_true")
    restore.add_argument("--delete-match-type", action="store_true")
    args = parser.parse_args(argv)
    try:
        ctx = Context()
    except EnvironmentRefused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    try:
        if args.command == "baseline":
            return cmd_baseline(ctx)
        if args.command == "record-baseline":
            return cmd_record_baseline(ctx, args.snapshot)
        if args.command == "configure":
            scope = None
            if args.products is not None:
                scope = [s for s in args.products.split(",") if s]
            return cmd_configure(ctx, args.apply, scope)
        if args.command == "probe-products":
            return cmd_probe_products(ctx)
        if args.command == "record-products-baseline":
            return cmd_record_products_baseline(ctx, args.snapshot)
        if args.command == "run":
            only = {s for s in args.only.split(",") if s} or None
            return cmd_run(ctx, args.accept_dashboard_user, only)
        if args.command == "verify-clean":
            return cmd_verify_clean(ctx)
        if args.command == "cleanup":
            return cmd_cleanup(ctx, args.apply)
        if args.command == "restore":
            return cmd_restore(ctx, args.apply, args.delete_match_type)
    except GuardrailStop as exc:
        print(f"guardrail stop: {exc}", file=sys.stderr)
        return 3
    except GuardRefused as exc:  # outside a run: cleanup --apply (P06.1-I2a)
        print(f"stopped: {exc}", file=sys.stderr)
        return 2
    finally:
        ctx.close()
    return 1
