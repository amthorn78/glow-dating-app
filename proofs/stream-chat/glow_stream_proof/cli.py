"""Command line entry point: ``python -m glow_stream_proof <command>``.

Read-only: ``baseline``, ``verify-clean``, ``configure`` and ``restore`` without
``--apply`` (they print the plan). Mutating: ``configure --apply``, ``run``,
``cleanup --apply`` and ``restore --apply``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import baseline, configuration, report
from .credentials import EnvironmentRefused, ServerCredentials, load_server_credentials
from .proof_run import PREFIX_ROOT, ProofRun, RunStopped
from .redaction import Redactor
from .server_api import ServerApi
from .usage import GuardrailStop, UsageLedger
from .workdir import PROOF_ROOT, WORK_DIR, checked_text, write_json, write_text

LEDGER = WORK_DIR / "usage-ledger.json"
BASELINE_RECORD = PROOF_ROOT / "baseline" / "application-1729640-2026-09-25.json"


def _stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


class Context:
    def __init__(self) -> None:
        self.credentials: ServerCredentials = load_server_credentials(os.environ)
        self.secrets = [self.credentials.secret()]
        self.redactor = Redactor(self.secrets)
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


def _apply(ctx: Context, plan: list[configuration.ApiRequest]) -> list[dict[str, Any]]:
    applied = []
    for step in plan:
        result = ctx.api.raw(step.method, step.path, body=step.body)
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
            raise RuntimeError(f"{step.method} {step.path} failed; stopping")
    return applied


def _settings_view(snapshot: dict[str, Any]) -> dict[str, Any]:
    app = snapshot["app"]["app"]
    return {
        "settings": {k: app.get(k) for k in configuration.APP_SETTING_KEYS if k in app},
        "app_grants": {r: app["grants"].get(r, []) for r in configuration.CLIENT_APP_ROLES},
        "types": sorted(snapshot["channel_types"]["channel_types"].keys()),
    }


def cmd_baseline(ctx: Context) -> int:
    snapshot = baseline.read_snapshot(ctx.api)
    path = write_json(f"snapshot-{_stamp()}.json", snapshot, ctx.secrets)
    ctx.say(f"snapshot written to {path.relative_to(PROOF_ROOT)}")
    ctx.say("settings: " + json.dumps(_settings_view(snapshot)["settings"], sort_keys=True))
    ctx.say(
        f"configuration differences from the proof's target: {len(configuration.verify(snapshot))}"
    )
    return 0


def cmd_record_baseline(ctx: Context, snapshot_path: Path) -> int:
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    record = configuration.baseline_record(snapshot)
    BASELINE_RECORD.parent.mkdir(parents=True, exist_ok=True)
    text = checked_text(json.dumps(record, indent=2, sort_keys=True) + "\n", ctx.secrets)
    BASELINE_RECORD.write_text(text, encoding="utf-8")
    ctx.say(f"baseline record written to {BASELINE_RECORD.relative_to(PROOF_ROOT)}")
    return 0


def cmd_configure(ctx: Context, apply: bool) -> int:
    before = baseline.read_snapshot(ctx.api)
    plan = configuration.apply_plan(before)
    ctx.say(f"differences before: {configuration.verify(before)}")
    if not apply:
        ctx.say("plan (dry run; pass --apply to change the application):")
        _print_plan(ctx, plan)
        return 0
    applied = _apply(ctx, plan)
    after = baseline.read_snapshot(ctx.api)
    problems = configuration.verify(after)
    record = {
        "at": _stamp(),
        "before": _settings_view(before),
        "applied": applied,
        "after": _settings_view(after),
        "after_match_type": after["channel_types"]["channel_types"].get(configuration.MATCH_TYPE),
        "after_default_type_grants": {
            name: after["channel_types"]["channel_types"][name]["grants"]
            for name in configuration.DEFAULT_TYPES
        },
        "problems_after": problems,
    }
    path = write_json(f"configure-{record['at']}.json", record, ctx.secrets)
    ctx.say(f"configuration record written to {path.relative_to(PROOF_ROOT)}")
    ctx.say(f"differences after: {problems}")
    return 0 if not problems else 1


def cmd_run(ctx: Context, accept_dashboard_user: bool, only: set[str] | None) -> int:
    prefix = f"{PREFIX_ROOT}{datetime.now(UTC).strftime('%m%d%H%M%S')}"
    run = ProofRun(
        ctx.credentials,
        ctx.api,
        ctx.ledger,
        ctx.redactor,
        os.environ,
        prefix=prefix,
        accept_dashboard_user=accept_dashboard_user,
    )
    started = datetime.now(UTC).isoformat(timespec="seconds")
    ctx.say(f"run {prefix} started {started}")
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
        stop_reason = f"stopped: {exc}"
    except GuardrailStop as exc:
        stop_reason = f"guardrail: {exc}"
        cleanup_needed = "stopping at once" not in str(exc)
    except Exception as exc:  # recorded, never hidden; cleanup still runs
        stop_reason = f"harness error: {type(exc).__name__}: {ctx.redactor.text(str(exc))}"
    finally:
        if cleanup_needed:
            try:
                result = run.cleanup()
                ctx.say(f"cleanup: {result}")
            except Exception as exc:  # reported, never hidden
                ctx.say(f"cleanup failed: {type(exc).__name__}: {exc}")
        else:
            run.close_sessions()
    ended = datetime.now(UTC).isoformat(timespec="seconds")
    results = run.results()
    results.update({"started": started, "ended": ended, "stop_reason": stop_reason})
    write_json(f"run-{prefix}.json", results, ctx.secrets)
    markdown = report.render(results)
    write_text(f"run-{prefix}.md", markdown, ctx.secrets)
    ctx.say(markdown)
    ctx.say(f"usage: {json.dumps(ctx.ledger.summary())}")
    ctx.say(f"run {prefix} ended {ended}" + (f"; {stop_reason}" if stop_reason else ""))
    return 0 if stop_reason is None else 2


def cmd_verify_clean(ctx: Context) -> int:
    snapshot = baseline.read_snapshot(ctx.api)
    users = [str(u.get("id")) for u in snapshot["users"].get("users", [])]
    proof_users = [u for u in users if u.startswith(PREFIX_ROOT)]
    channels = [str(c["channel"]["cid"]) for c in snapshot["channels"].get("channels", [])]
    ctx.say(f"proof users remaining: {proof_users}")
    ctx.say(f"channels remaining: {channels}")
    ctx.say(f"other users present: {len(users) - len(proof_users)}")
    return 0 if not proof_users and not channels else 1


def cmd_cleanup(ctx: Context, apply: bool) -> int:
    snapshot = baseline.read_snapshot(ctx.api)
    users = [
        str(u["id"])
        for u in snapshot["users"].get("users", [])
        if str(u["id"]).startswith(PREFIX_ROOT)
    ]
    cids = [
        str(c["channel"]["cid"])
        for c in snapshot["channels"].get("channels", [])
        if PREFIX_ROOT in str(c["channel"]["cid"])
    ]
    ctx.say(f"proof users: {users}; proof channels: {cids}")
    if not apply:
        ctx.say("dry run; pass --apply to hard-delete them")
        return 0
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
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="glow_stream_proof")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("baseline", help="read-only snapshot of settings, types, roles and data")
    rec = sub.add_parser("record-baseline", help="write the restore record from a snapshot")
    rec.add_argument("--snapshot", type=Path, required=True)
    conf = sub.add_parser("configure", help="plan (or --apply) the proof's configuration")
    conf.add_argument("--apply", action="store_true")
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
            return cmd_configure(ctx, args.apply)
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
    finally:
        ctx.close()
    return 1
