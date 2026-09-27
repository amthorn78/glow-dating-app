# The reversal table quotes source lines exactly, so some exceed the line length.
# ruff: noqa: E501
"""P06.1-C1, P06.1-C2 and P06.1-C3: show that each fix is tested.

For each fix, a scratch copy of this directory (outside it, in a temporary
directory) gets that one fix reverted, and the fix's tests are run: they must
fail. The fix is then put back and the same tests must pass. Nothing in this
directory is changed. Run it with the harness's own Python after installing:

    .venv/bin/python checks/fix_reversals.py

It prints one line per reversal, with each failing test and the exception its
failure ended in, and exits non-zero if any reversal is not demonstrated. A
reversal whose tests abort the test process (for example an escaping
KeyboardInterrupt) counts as failing, and its line says so.

Since P06.1-C3 a reversal is "not demonstrated" unless each of its patterns
starts a line and occurs there exactly once (so a pattern with the wrong
indentation cannot land inside a longer line), and unless every file it edits
still compiles and imports (``.py``) or passes ``node --check`` (``.cjs``): a
reverted file that does not load makes its tests fail for the wrong reason.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
PY = str(SRC / ".venv" / "bin" / "python")
JWT_SHAPE = re.compile(r"eyJ[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]{2,}\.[A-Za-z0-9_-]*")
# No bytecode is written in the scratch copy, so a reverted or restored file is never
# shadowed by a cached copy of its other version (P06.1-C3).
ENV = {
    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    "HOME": os.environ.get("HOME", "/"),
    "LANG": "C.UTF-8",
    "PYTHONDONTWRITEBYTECODE": "1",
}
P = "glow_stream_proof/proof_run.py"
C = "glow_stream_proof/cli.py"
B = "glow_stream_proof/client_bridge.py"
S = "glow_stream_proof/server_api.py"
RD = "glow_stream_proof/redaction.py"
U = "glow_stream_proof/usage.py"
FR = "checks/fix_reversals.py"
TI = "tests.test_interruptions."
KEPT = TI + "ProceduresKeepWhatTheyObservedTest."
TA = "tests.test_answers."
TCC = "tests.test_cli.CommandTest."
SS = "tests.test_stop_signals."
# P06.1-I2a.
G = "glow_stream_proof/guard.py"
CF = "glow_stream_proof/configuration.py"
RP = "glow_stream_proof/report.py"
RL = "client/request-log.cjs"
RN = "client/runner.cjs"
TGU = "tests.test_guard."
TCS = "tests.test_client_session."
TRS = "tests.test_configuration.RecordedSettingsTest."
TCK = "tests.test_closing_checks.ClosingChecksTest."
# P06.1-I2a, step 2.
MX = "glow_stream_proof/mechanisms.py"
I2 = "glow_stream_proof/i2a.py"
AS = "glow_stream_proof/app_send.py"
TMX = "tests.test_mechanisms."
TI2 = "tests.test_i2a."
# P06.1-I2b.
MT = "glow_stream_proof/matrix.py"
TCE = "tests.test_credentials_and_client_env."
TCL = "tests.test_cleanup."
RT3_CONTROL_HOLDS = (
    "            elif (\n"
    '                control.outcome == "success" and _request_line(control.record, self.ctx) == request\n'
    "            ):\n"
)
# Updated in P06.1-I2a: the import also names mentions_billing.
SERVER_IMPORT = "from .usage import UsageLedger, charge_signal, is_rate_limit, mentions_billing\n"
SERVER_IMPORT_C2 = "from .usage import GuardrailStop, UsageLedger, charge_signal, is_rate_limit, mentions_billing\n"


def unobserved(context: str) -> tuple[str, str, str]:
    """Revert one place that keeps what a case observed: ``self._observe(`` becomes ``(``."""
    return (P, context, context.replace("self._observe(", "("))


R: list[tuple[str, list[tuple[str, str, str]], list[str]]] = [
    (
        "F1 request under test (generic)",
        [
            (
                P,
                "    return _answer_of(reply.last_request, reply)\n",
                "    status, code = reply.status, reply.code\n"
                "    if reply.ok:\n        return Answer('success', status, None, reply.last_request)\n"
                "    return Answer(matrix.classify(status, code), status, code, reply.last_request)\n",
            )
        ],
        [
            "tests.test_answers.AnswerTest.test_sdk_error_without_a_request_has_no_answer",
            "tests.test_answers.RequestUnderTestInCasesTest.test_generic_case_uses_the_record_not_the_sdk_error",
            "tests.test_answers.RequestUnderTestInCasesTest.test_generic_case_without_a_request_is_inconclusive",
        ],
    ),
    (
        "F1 G1",
        [
            (
                P,
                "            answer = _answer_of(post, reply)\n",
                "            answer = Answer(matrix.classify(reply.status, reply.code), reply.status, reply.code, post)\n",
            ),
            (
                P,
                '        if created_id is None and answer.outcome not in ("success", "no-response"):\n',
                '        if answer.outcome != "success":\n',
            ),
            (
                P,
                "        if created_id is not None:\n            verdict = matrix.Verdict(matrix.FAIL,",
                "        if False:\n            verdict = matrix.Verdict(matrix.FAIL,",
            ),
        ],
        [
            "tests.test_answers.RequestUnderTestInCasesTest.test_g1_fails_whenever_the_clients_post_guest_created_a_guest"
        ],
    ),
    (
        "F1 G3",
        [
            (
                P,
                '            else Answer("no-response", None, None, None, "the anonymous connect did not answer")\n        )\n        if connected.outcome != "success":\n',
                '            else Answer("no-response", None, None, None, "the anonymous connect did not answer")\n        )\n        if False:\n',
            ),
        ],
        [
            "tests.test_answers.RequestUnderTestInCasesTest.test_g3_is_inconclusive_unless_the_anonymous_connect_succeeded"
        ],
    ),
    (
        "F1 RT2/RT3",
        [
            (
                P,
                '        elif outcome == "no-response":\n            verdict = matrix.Verdict(matrix.INCONCLUSIVE, matrix.NO_RESPONSE_REASON)\n',
                "        elif False:\n            verdict = matrix.Verdict(matrix.INCONCLUSIVE, matrix.NO_RESPONSE_REASON)\n",
            )
        ],
        [
            "tests.test_answers.RequestUnderTestInCasesTest.test_rt2_local_throw_is_inconclusive",
            "tests.test_answers.RequestUnderTestInCasesTest.test_rt3_null_return_without_a_request_is_inconclusive",
        ],
    ),
    (
        "F2 RunStopped re-raised",
        [
            (
                P,
                "            except (GuardrailStop, RunStopped) as exc:\n                # Record the case, with what it had observed, then stop",
                "            except (GuardrailStop, ZeroDivisionError) as exc:\n                # Record the case, with what it had observed, then stop",
            ),
        ],
        ["tests.test_temporary_changes.TypeFeatureRestoreTest.test_failed_restore_stops_the_run"],
    ),
    (
        "F2 try before enabling (type/channel)",
        [
            (
                P,
                "            with self._temporary(change):\n                if case.feature_override:\n                    on = self._set_channel_override(change, override)\n                else:\n                    on = self._type_features_on(override)\n                result = self._evaluate_case(case)\n",
                "            if case.feature_override:\n                on = self._set_channel_override(change, override)\n            else:\n                on = self._type_features_on(override)\n            with self._temporary(change):\n                result = self._evaluate_case(case)\n",
            ),
        ],
        [
            "tests.test_temporary_changes.TypeFeatureRestoreTest.test_journal_entry_exists_before_the_enabling_request"
        ],
    ),
    (
        "F2 try before enabling (guest)",
        [
            (
                P,
                '                with self._temporary(change):\n                    on = self._set_guest_creation_disabled(False)\n                    time.sleep(TYPE_CHANGE_SETTLE_SECONDS)\n                    guest = self._session("guest", None, max_api_calls=30)\n                    creply = self._send(guest, "guest", max_calls=3, user=user)\n',
                '                on = self._set_guest_creation_disabled(False)\n                time.sleep(TYPE_CHANGE_SETTLE_SECONDS)\n                guest = self._session("guest", None, max_api_calls=30)\n                with self._temporary(change):\n                    creply = self._send(guest, "guest", max_calls=3, user=user)\n',
            ),
        ],
        [
            "tests.test_temporary_changes.TypeFeatureRestoreTest.test_guest_creation_is_restored_after_an_interrupt_before_the_control"
        ],
    ),
    (
        "F2 guardrail in flight kept",
        [
            (
                P,
                "                if isinstance(exc, GuardrailStop):\n                    raise exc from None\n",
                "",
            )
        ],
        [
            "tests.test_temporary_changes.TypeFeatureRestoreTest.test_restore_failure_does_not_hide_a_guardrail_stop_in_flight"
        ],
    ),
    (
        "F2 end of run: journal, cleanup, verify, exit",
        [
            # Repaired in P06.1-C3: the 8-space pattern matched inside the 12-space
            # line and made the file fail to compile.
            (
                C,
                "            problems = run.finish(cleanup=cleanup_needed)\n",
                "            problems: list[str] = []\n            run.cleanup() if cleanup_needed else run.close_sessions()\n",
            ),
        ],
        [
            "tests.test_cli.CommandTest.test_configuration_difference_after_the_run_exits_non_zero",
            "tests.test_cli.CommandTest.test_cleanup_problem_exits_non_zero",
            "tests.test_cli.CommandTest.test_ctrl_c_restores_cleans_up_writes_results_and_exits_non_zero",
        ],
    ),
    (
        "F2 Ctrl-C handled",
        [(C, '    except KeyboardInterrupt:\n        stop_reason = "interrupted (Ctrl-C)"\n', "")],
        [
            "tests.test_cli.CommandTest.test_ctrl_c_restores_cleans_up_writes_results_and_exits_non_zero"
        ],
    ),
    (
        "F3 exactly one",
        [(P, "        elif len(dashboard) != 1:\n", "        elif False:\n")],
        [
            "tests.test_preflight.PreflightTest.test_two_dashboard_users_stop_the_run",
            "tests.test_preflight.PreflightTest.test_no_dashboard_user_stops_the_run_when_one_is_expected",
        ],
    ),
    (
        "F3 created_at",
        [
            (
                P,
                '        elif _utc_minute(dashboard[0].get("created_at")) != DASHBOARD_USER_CREATED_MINUTE:\n',
                "        elif False:\n",
            )
        ],
        ["tests.test_preflight.PreflightTest.test_another_creation_time_stops_the_run"],
    ),
    (
        "F4 local events dropped",
        [
            (
                P,
                '        delivered = [e for e in events if e.get("type") not in matrix.LOCAL_EVENT_TYPES]\n',
                "        delivered = list(events)\n",
            )
        ],
        [
            "tests.test_events.MemberCustomEventsTest.test_local_query_event_is_not_counted_as_delivered",
            "tests.test_events.PayloadWindowsTest.test_marker_only_in_a_local_event_is_not_delivered",
        ],
    ),
    (
        "nit 1 every window",
        [
            (
                P,
                "        windows = after_request + after_probe\n",
                "        windows = after_request\n",
            )
        ],
        [
            "tests.test_events.PayloadWindowsTest.test_marker_in_another_event_type_in_the_second_window_fails"
        ],
    ),
    (
        "nit 1 every event type",
        [
            (
                P,
                '        carriers = sorted({str(e.get("type")) for e in windows if matrix.find_terms(e, [marker])})\n',
                '        carriers = sorted({str(e.get("type")) for e in events if matrix.find_terms(e, [marker])})\n',
            )
        ],
        [
            "tests.test_events.PayloadWindowsTest.test_marker_in_another_event_type_in_the_second_window_fails"
        ],
    ),
    (
        "F5 reply id checked",
        [(B, "        if reply_id != command_id:\n", "        if False:\n")],
        ["tests.test_client_session.ReplyMatchingTest.test_mismatched_reply_ends_the_session"],
    ),
    (
        "F5 timeout ends session",
        [
            (
                B,
                "            raise self._end(self._redactor.text(str(exc))) from None\n",
                "            raise RuntimeError(str(exc)) from None\n",
            )
        ],
        [
            "tests.test_client_session.ReplyMatchingTest.test_timeout_ends_the_session_and_releases_the_connection"
        ],
    ),
    (
        "F5 buffered line (select reader)",
        [
            (
                B,
                "        self._stdout_thread = threading.Thread(target=self._drain_stdout, daemon=True)\n",
                "        self._stdout_thread = threading.Thread(target=lambda: None, daemon=True)\n",
            ),
            (
                B,
                "        try:\n            line = self._lines.get(timeout=self._timeout)\n        except queue.Empty:\n"
                '            raise TimeoutError(f"no reply within {self._timeout}s") from None\n        if line is None:\n',
                "        import selectors\n        assert self._proc.stdout is not None\n"
                "        selector = selectors.DefaultSelector()\n"
                "        selector.register(self._proc.stdout, selectors.EVENT_READ)\n        try:\n"
                "            if not selector.select(self._timeout):\n"
                '                raise TimeoutError(f"no reply within {self._timeout}s")\n'
                "        finally:\n            selector.close()\n"
                "        line = self._proc.stdout.readline() or None\n        if line is None:\n",
            ),
        ],
        [
            "tests.test_client_session.ReplyMatchingTest.test_buffered_line_is_read_without_a_timeout"
        ],
    ),
    (
        "F6 simulation guest connect refused",
        [
            (
                "tests/fakes.py",
                '            guest_post = record(post_status, response, path="/guest")\n',
                '            guest_post = record(post_status, response, path="/guest")\n'
                "            if post_status == 201:\n"
                '                return Reply(True, {"me": {"id": stored, "role": "guest"}}, None, [guest_post])\n',
            )
        ],
        [
            # Renamed in P06.1-I2a, which sets G2 up server-side; it still checks that
            # G1's control's guest has no session because its connect is refused.
            "tests.test_run_simulation.SimulationTest.test_guest_reach_runs_on_a_guest_created_server_side"
        ],
    ),
    (
        "F7 leak terms",
        [
            (
                "glow_stream_proof/matrix.py",
                '        ("read-ab", "query channel AB", read_ab_terms),\n',
                '        ("read-ab", "query channel AB", ("{m_a_text}", "{m_b_text}")),\n',
            ),
            (
                "glow_stream_proof/matrix.py",
                '        ("message", "fetch XD\'s message by ID", ("{xd_text}", "{m_x}", "{X}", "{XD}")),\n',
                '        ("message", "fetch XD\'s message by ID", ("{xd_text}",)),\n',
            ),
        ],
        ["tests.test_procedures.LeakTermsTest"],
    ),
    (
        "nit 2 code 2",
        [
            (
                "glow_stream_proof/matrix.py",
                "AUTH_CODES = frozenset({5, 40, 41, 42, 43})",
                "AUTH_CODES = frozenset({2, 5, 40, 41, 42, 43})",
            )
        ],
        ["tests.test_matrix.ClassificationTest.test_api_key_error_is_not_a_token_refusal"],
    ),
    (
        "nit 3 user_id from params",
        [
            (
                P,
                "        return _request_line(record, self.ctx) + suffix\n",
                '        return _request_line(record, self.ctx) + " ?user_id={X}"\n',
            )
        ],
        ["tests.test_procedures.ClaimRequestLineTest.test_no_user_id_is_not_invented"],
    ),
    (
        "nit 4 undo checked",
        [
            (
                P,
                '        if not done.ok:\n            self._defer_stop(\n                f"{case_id}: undo',
                '        if False:\n            self._defer_stop(\n                f"{case_id}: undo',
            )
        ],
        [
            "tests.test_temporary_changes.UndoCheckTest.test_failed_undo_stops_the_run_after_its_case"
        ],
    ),
    (
        "nit 4 member field unset checked",
        [
            (
                P,
                '        if not undone.ok:\n            self._defer_stop(\n                f"S15: unsetting',
                '        if False:\n            self._defer_stop(\n                f"S15: unsetting',
            )
        ],
        ["tests.test_temporary_changes.UndoCheckTest.test_member_field_unset_is_checked"],
    ),
    (
        "nit 4 removal re-read",
        [
            (
                P,
                '            state = override_state(channel, key, value) if key in shown else "unknown"\n',
                '            state = "clear"\n',
            ),
        ],
        [
            "tests.test_temporary_changes.ChannelOverrideRemovalTest.test_removal_that_did_not_apply_stops_the_run"
        ],
    ),
    (
        "nit 4 removal status checked",
        [
            (
                P,
                "        if not off.ok:\n            raise RunStopped(\n                f\"removing AB's",
                "        if False:\n            raise RunStopped(\n                f\"removing AB's",
            )
        ],
        [
            "tests.test_temporary_changes.ChannelOverrideRemovalTest.test_removal_refused_stops_the_run"
        ],
    ),
    (
        "nit 5 cleanup steps guarded",
        [
            (
                P,
                "            try:\n                step()\n",
                "            step()\n            try:\n                pass\n",
            )
        ],
        ["tests.test_cleanup.GuardedCleanupTest.test_a_failing_step_does_not_stop_the_others"],
    ),
    (
        "nit 5 task status judged",
        [(P, '            if out.get(task) != "completed":\n', "            if False:\n")],
        ["tests.test_cleanup.GuardedCleanupTest.test_task_that_does_not_complete_is_a_problem"],
    ),
    (
        "nit 6 typed-call charge signal",
        [
            (
                "glow_stream_proof/server_api.py",
                '            event_hooks={"request": [self._before_request], "response": [self._after_response]},\n',
                '            event_hooks={"request": [self._before_request]},\n',
            )
        ],
        [
            "tests.test_server_api.TypedCallChargeSignalTest.test_typed_calls_stop_on_a_charge_signal"
        ],
    ),
    (
        "nit 7 request op removed",
        [
            (
                "client/runner.cjs",
                "    case 'events': {\n",
                "    case 'request': {\n      const url = BASE + cmd.path;\n      const m = String(cmd.method).toLowerCase();\n"
                "      if (m === 'get' || m === 'delete') await client[m](url, cmd.params || {});\n"
                "      else await client[m](url, cmd.body || {}, cmd.params ? { params: cmd.params } : undefined);\n"
                "      return {};\n    }\n    case 'events': {\n",
            )
        ],
        ["tests.test_runner.RunnerTest.test_unused_request_op_is_gone"],
    ),
    (
        "nit 8 baseline written without users",
        [
            (
                C,
                '    path = write_json(f"snapshot-{_stamp()}.json", public, ctx.secrets)',
                '    path = write_json(f"snapshot-{_stamp()}.json", snapshot, ctx.secrets)',
            )
        ],
        ["tests.test_cli.CommandTest.test_baseline_writes_no_other_users_identifier_or_name"],
    ),
    (
        "nit 8 redaction by pattern",
        [
            (
                "glow_stream_proof/redaction.py",
                "                if is_sensitive_key(key_text) and isinstance(item, str) and item:",
                "                if key_text.lower() in _SENSITIVE_KEYS and isinstance(item, str) and item:",
            ),
            (
                "glow_stream_proof/redaction.py",
                "                elif is_sensitive_key(key_text) and isinstance(item, Mapping | list) and item:",
                "                elif False:",
            ),
        ],
        ["tests.test_redaction.RedactionTest.test_sensitive_keys_are_matched_by_pattern"],
    ),
    (
        "nit 9 verify required settings",
        [
            (
                "glow_stream_proof/configuration.py",
                "    for key, want in REQUIRED_APP_SETTINGS.items():",
                "    for key, want in {}.items():",
            )
        ],
        [
            "tests.test_configuration.ConfigurationTest.test_verify_checks_permission_version_and_member_custom_settings"
        ],
    ),
    (
        "nit 10 restore verified",
        [
            (
                C,
                "    problems = configuration.verify_restored(after, record, match_type_deleted=delete_match_type)\n",
                "    problems: list[str] = []\n",
            )
        ],
        ["tests.test_cli.CommandTest.test_restore_apply_verifies_what_it_restored"],
    ),
    (
        "nit 11 isomorphic-ws check",
        [("client/runner.cjs", "    case 'selfcheck':", "    case 'selfcheck-removed':")],
        ["tests.test_runner.RunnerTest.test_stream_chat_uses_the_runners_websocket"],
    ),
    (
        "nit 12 cleanup reserve",
        [(P, "CLEANUP_RESERVE = 130\n", "CLEANUP_RESERVE = 60\n")],
        ["tests.test_cleanup.CleanupReserveTest.test_reserve_covers_the_worst_case_end_of_run"],
    ),
    (
        "nit 13 client-created data tracked",
        [(P, "            self._track_client_created(reply)\n", "            pass\n")],
        ["tests.test_cleanup.ClientCreatedDataTest.test_client_created_poll_and_group_are_deleted"],
    ),
    (
        "nit 13 verify-clean lists polls and groups",
        [
            (P, "            **self._new_polls_and_groups(),\n", ""),
        ],
        ["tests.test_cleanup.ClientCreatedDataTest.test_verify_clean_lists_polls_and_user_groups"],
    ),
    (
        "nit 15 check evidence redacted",
        [
            (
                P,
                "        text = self.redactor.text(_generic(evidence, self.ctx))\n",
                "        text = _generic(evidence, self.ctx)\n",
            )
        ],
        ["tests.test_procedures.CheckRedactionTest.test_check_evidence_is_redacted"],
    ),
    (
        "nit 16 E5 connection role",
        [
            (
                P,
                '        if connect_me_role not in (None, "user") and not stored_applied:\n',
                "        if False:\n",
            )
        ],
        ["tests.test_procedures.NotEffectiveTest.test_e5_role_carried_by_the_connection_fails"],
    ),
    (
        "nit 16 S14 connection profile",
        [(P, "        if me_applied and not stored_applied:\n", "        if False:\n")],
        ["tests.test_procedures.NotEffectiveTest.test_s14_profile_carried_by_the_connection_fails"],
    ),
    (
        "nit 16 T4-rest-unread controls",
        [
            (
                P,
                "            verdict = matrix.refused_verdict(outcome, controls_ok)\n",
                "            verdict = matrix.refused_verdict(outcome, True)\n",
            )
        ],
        [
            "tests.test_procedures.NotEffectiveTest.test_unread_refusal_without_its_controls_is_inconclusive"
        ],
    ),
    (
        "review 1: a re-read proves a removal only if it showed the override",
        [
            (
                P,
                '        shown = set(change.reread.get("shown_while_set") or [])\n',
                "        shown = set(override)\n",
            ),
        ],
        [
            "tests.test_temporary_changes.OverrideReReadShapeTest.test_re_read_that_never_shows_the_override_is_recorded_not_verified"
        ],
    ),
    (
        "review 1: an ended B session leaves the grant unverified",
        [
            (
                P,
                "        except ClientSessionEnded:\n            return None\n        return _http_answer(probe)\n",
                "        except ZeroDivisionError:\n            return None\n        return _http_answer(probe)\n",
            ),
        ],
        [
            "tests.test_temporary_changes.OverrideReReadShapeTest.test_grant_unverifiable_when_bs_session_has_ended"
        ],
    ),
    (
        "review 2: a failed restore keeps the observed row",
        [
            (
                P,
                '        if row is None:\n            return\n        row.detail["run_stopped"]',
                '        return\n        row.detail["run_stopped"]',
            ),
        ],
        [
            "tests.test_temporary_changes.KeptRowTest",
            "tests.test_temporary_changes.TypeFeatureRestoreTest.test_failed_restore_stops_the_run",
        ],
    ),
    (
        "review 3: S15's unset never hides a guardrail stop",
        [
            (
                P,
                "        except Exception as exc:\n            self._defer_stop(\n                f\"S15: unsetting A's member field raised",
                "        except ZeroDivisionError as exc:\n            self._defer_stop(\n                f\"S15: unsetting A's member field raised",
            ),
        ],
        ["tests.test_temporary_changes.GuardedUnsetTest"],
    ),
    (
        "review 4: polls and groups present at preflight are not leftovers",
        [
            (
                P,
                "            if now is not None and before is not None:\n",
                "            if False:\n",
            ),
        ],
        ["tests.test_cleanup.PreexistingPollsAndGroupsTest"],
    ),
    (
        "review 5: journalled restores are retried",
        [
            (P, "RESTORE_ATTEMPTS = 3\n", "RESTORE_ATTEMPTS = 1\n"),
        ],
        ["tests.test_temporary_changes.FinishRetryTest.test_restore_is_retried"],
    ),
    (
        "review nit: an unanswered anonymous connect is not a KeyError",
        [
            (
                P,
                '        connect_reply = self.connect_replies.get("anonymous")\n',
                '        connect_reply = self.connect_replies["anonymous"]\n',
            ),
        ],
        ["tests.test_answers.AnonymousConnectWithoutAnswerTest"],
    ),
    (
        "review nit: verify_restored checks automod and message length",
        [
            (
                "glow_stream_proof/configuration.py",
                '        for key in ("automod", "automod_behavior", "max_message_length"):\n',
                "        for key in ():\n",
            ),
        ],
        ["tests.test_configuration.ConfigurationTest.test_verify_restored"],
    ),
    (
        "review nit: runner reports ws-api only for Stream's frame",
        [
            (
                "client/error-info.cjs",
                "      info.kind = parsed.isWSFailure === false ? 'ws-api' : 'ws-failure';\n",
                "      info.kind = parsed.isWSFailure ? 'ws-failure' : 'ws-api';\n",
            ),
        ],
        ["tests.test_runner.ErrorInfoTest"],
    ),
    # -- P06.1-C2 ------------------------------------------------------------------
    (
        "C2 F1 an interrupted case keeps what it observed",
        [(P, "        row = self._partial\n", "        row = None\n")],
        [
            TI + "ReviewScenariosTest.test_s2_fail_survives_a_timeout_in_the_production_phase",
            TI + "ReviewScenariosTest.test_s15_leak_survives_bs_session_ending_during_the_control",
            TI + "ReviewScenariosTest.test_s3a_fail_is_recorded_when_the_replay_hits_a_rate_limit",
            TI + "ReviewScenariosTest.test_s3a_client_success_is_undone_after_a_replay_error",
            TI + "ReviewScenariosTest.test_s3a_undo_is_not_made_after_ctrl_c",
            TI
            + "EveryWayACaseEndsTest.test_an_observed_refusal_becomes_inconclusive_with_the_interruption_as_reason",
            TI + "ProceduresKeepWhatTheyObservedTest",
        ],
    ),
    (
        "C2 F1 a guardrail stop records the case",
        [
            (
                P,
                "            except (GuardrailStop, RunStopped) as exc:\n                # Record the case, with what it had observed, then stop",
                "            except GuardrailStop:\n                raise\n            except RunStopped as exc:\n                # Record the case, with what it had observed, then stop",
            )
        ],
        [
            TI
            + "EveryWayACaseEndsTest.test_guardrail_stop_with_nothing_observed_records_an_inconclusive_row",
            TI + "ReviewScenariosTest.test_s3a_fail_is_recorded_when_the_replay_hits_a_rate_limit",
            "tests.test_temporary_changes.GuardedUnsetTest",
        ],
    ),
    (
        "C2 F1 Ctrl-C records the case",
        [
            (
                P,
                "            except BaseException as exc:  # Ctrl-C: record the case, then stop\n                self.case_results.append(self._interrupted_row(case, exc))\n",
                "            except BaseException as exc:  # Ctrl-C: record the case, then stop\n",
            )
        ],
        [
            TI
            + "EveryWayACaseEndsTest.test_ctrl_c_with_nothing_observed_records_an_inconclusive_row",
            TI + "ReviewScenariosTest.test_s3a_undo_is_not_made_after_ctrl_c",
        ],
    ),
    (
        "C2 F1 the owed undo after an interrupted control",
        [
            (
                P,
                "            if undo_owed:\n                self._undo_after_interruption(case, exc, row)\n",
                "            pass\n",
            )
        ],
        [
            TI + "ReviewScenariosTest.test_s3a_fail_is_recorded_when_the_replay_hits_a_rate_limit",
            TI + "ReviewScenariosTest.test_s3a_client_success_is_undone_after_a_replay_error",
            TI + "ReviewScenariosTest.test_s3a_undo_is_not_made_after_ctrl_c",
        ],
    ),
    (
        "C2 F1 no undo after a guardrail stop",
        [
            (
                P,
                '        if isinstance(exc, GuardrailStop):\n            row.detail["client_success_undo"] = (',
                '        if False:\n            row.detail["client_success_undo"] = (',
            )
        ],
        [TI + "ReviewScenariosTest.test_s3a_fail_is_recorded_when_the_replay_hits_a_rate_limit"],
    ),
    (
        "C2 F1 the undo after a completed control is recorded",
        [
            (
                P,
                # Updated in P06.1-I2a: a phase's undo note is added to the earlier one.
                "        finally:\n"
                '            done = (f"{phase}: " if phase else "") + ", ".join(notes)\n'
                '            note = f"{earlier}; {done}" if earlier else done\n'
                '            row.detail["client_success_undo"] = self.redactor.text(note)\n',
                "        finally:\n            pass\n",
            )
        ],
        [TI + "ReviewScenariosTest.test_undo_after_a_completed_control_is_recorded"],
    ),
    (
        "C2 F1 kept: the client's request before its control",
        [unobserved("        row = self._observe(\n")],
        [
            TI + "ReviewScenariosTest.test_s3a_fail_is_recorded_when_the_replay_hits_a_rate_limit",
            TI
            + "EveryWayACaseEndsTest.test_an_observed_refusal_becomes_inconclusive_with_the_interruption_as_reason",
        ],
    ),
    (
        "C2 F1 kept: the feature-on phase (S2)",
        [unobserved("        result = self._observe(\n")],
        [TI + "ReviewScenariosTest.test_s2_fail_survives_a_timeout_in_the_production_phase"],
    ),
    (
        "C2 F1 kept: bad-token REST",
        [
            unobserved(
                '        detail = {"token_used": self._describe_bad(kind, token), "set_user": set_reply.ok}\n        self._observe('
            )
        ],
        [KEPT + "test_t2_rest_success_survives_as_controls_session_ending"],
    ),
    (
        "C2 F1 kept: bad-token WebSocket",
        [
            unobserved(
                "            # What the connect showed, kept if the disconnect is interrupted.\n            self._observe("
            )
        ],
        [KEPT + "test_t4_ws_connection_as_b_survives_a_failed_disconnect"],
    ),
    (
        "C2 F1 kept: T4-rest-xd",
        [
            unobserved(
                '                disclosed = matrix.Verdict(matrix.FAIL, "response disclosed XD\'s message")\n                self._observe('
            )
        ],
        [KEPT + "test_t4_rest_xd_success_survives_xs_session_ending"],
    ),
    (
        "C2 F1 kept: G1",
        [
            unobserved(
                "            # What the attempt showed, kept if a later step is interrupted.\n            self._observe("
            )
        ],
        [KEPT + "test_g1_created_guest_survives_a_failed_disconnect"],
    ),
    (
        "C2 F1 kept: guest and anonymous probes",
        [
            unobserved(
                '        self._observe(\n            self._result(\n                case,\n                _request_line(answer.record, self.ctx),\n                _observed(answer),\n                "control not completed",\n                matrix.no_leak_verdict(outcome, leaks, False, False),'
            )
        ],
        [KEPT + "test_g3_leak_survives_the_controls_session_ending"],
    ),
    (
        "C2 F1 kept: S10 with polls on",
        [unobserved("        voted = _http_answer(reply)\n        self._observe(")],
        [KEPT + "test_s10_vote_success_survives_an_error_in_the_server_replay"],
    ),
    (
        "C2 F1 kept: S10 before the production vote",
        [
            unobserved(
                "        # What the polls-on phase observed, kept if the production vote is interrupted.\n        self._observe("
            )
        ],
        [KEPT + "test_s10_polls_on_control_survives_the_production_vote_ending"],
    ),
    (
        "C2 F1 kept: S15 under production",
        [
            unobserved(
                "            seen = self._member_leaks(production)\n            self._observe("
            )
        ],
        [TI + "ReviewScenariosTest.test_s15_leak_survives_bs_session_ending_during_the_control"],
    ),
    (
        "C2 F1 kept: S14's connection",
        [
            unobserved(
                '            unjudged = matrix.Verdict(matrix.INCONCLUSIVE, "stored state not yet read")\n            self._observe('
            )
        ],
        [KEPT + "test_s14_profile_on_the_connection_survives_a_failed_disconnect"],
    ),
    (
        "C2 F1 kept: S14's stored state",
        [unobserved("        if stored_applied:\n            self._observe(")],
        [KEPT + "test_s14_stored_change_survives_an_error_in_the_control"],
    ),
    (
        "C2 F1 kept: E5's connection",
        [
            unobserved(
                '            connect_me_role = me.get("role") if isinstance(me, dict) else None\n            self._observe('
            )
        ],
        [KEPT + "test_e5_role_on_the_connection_survives_a_failed_disconnect"],
    ),
    (
        "C2 F1 kept: RT2/RT3 first window",
        [
            unobserved(
                '        self._observe(\n            self._result(\n                case,\n                _request_line(answer.record, self.ctx),\n                _observed(answer),\n                "B\'s listener not yet checked",'
            )
        ],
        [KEPT + "test_rt2_marker_in_the_first_window_survives_bs_session_ending"],
    ),
    (
        "C2 F1 kept: RT1",
        [
            unobserved(
                "        # A's events already decide a FAIL; keep it if X's events are interrupted.\n        self._observe("
            )
        ],
        [KEPT + "test_rt1_xd_event_survives_xs_session_ending"],
    ),
    (
        "C2 F2 T4-rest-unread needs both controls and all totals",
        [
            (
                P,
                '        elif outcome == "success" and (\n            not controls_ok or a_total is None or b_total is None or claim_total is None\n        ):',
                "        elif False:",
            )
        ],
        [
            "tests.test_procedures.UnreadControlsTest.test_as_own_control_refused_is_inconclusive",
            "tests.test_procedures.UnreadControlsTest.test_a_missing_total_is_inconclusive",
            "tests.test_procedures.UnreadControlsTest.test_b_count_with_as_control_failed_is_inconclusive",
        ],
    ),
    (
        "C2 F3 RT2/RT3 hold on attributable refusals only",
        [
            # Since P06.1-C3 the input, not-found and other refusals end in their own
            # branch; reverting C2's fix makes that branch HOLD again.
            (
                P,
                "            # A 400 input error, a 404 or an outage says nothing about what a\n"
                "            # well-formed event delivers to B (P06.1-C2).\n"
                "            verdict = matrix.Verdict(matrix.INCONCLUSIVE,",
                "            # A 400 input error, a 404 or an outage says nothing about what a\n"
                "            # well-formed event delivers to B (P06.1-C2).\n"
                "            verdict = matrix.Verdict(matrix.HOLDS,",
            )
        ],
        [
            "tests.test_answers.PayloadRefusalAttributionTest.test_input_not_found_and_other_refusals_are_inconclusive"
        ],
    ),
    (
        "C2 F3 named events count only after an accepted request",
        [(P, '        elif outcome == "success" and events:\n', "        elif events:\n")],
        [
            "tests.test_answers.PayloadRefusalAttributionTest.test_named_events_after_an_unattributable_refusal_are_inconclusive"
        ],
    ),
    (
        "C2 nit 4 only a rate limit is retried",
        [
            (
                P,
                "                    if not exc.rate_limited:\n",
                '                    if "stopping at once" not in str(exc):\n',
            )
        ],
        ["tests.test_temporary_changes.RateLimitRetryTest.test_a_charge_signal_is_not_retried"],
    ),
    (
        "C2 nit 4 what counts as a rate limit",
        [
            (
                U,
                "    return (status == 429 or code == 9) and status != 402 and code != 99\n",
                "    return status == 429 or code == 9\n",
            )
        ],
        [
            "tests.test_server_api.RateLimitFlagTest.test_charge_signals_are_not_rate_limits",
            "tests.test_client_session.ClientRateLimitFlagTest",
        ],
    ),
    (
        "C2 nit 4 flag on typed server calls",
        [
            (
                S,
                "                rate_limited=is_rate_limit(response.status_code, code),\n",
                "                rate_limited=False,\n",
            )
        ],
        ["tests.test_server_api.RateLimitFlagTest.test_rate_limits"],
    ),
    (
        "C2 nit 4 flag on raw server calls",
        [
            (
                S,
                "                rate_limited=is_rate_limit(result.status, result.code),\n",
                "                rate_limited=False,\n",
            )
        ],
        ["tests.test_server_api.RateLimitFlagTest.test_the_result_check_flags_a_rate_limit"],
    ),
    (
        "C2 nit 4 flag on client requests",
        [
            (
                B,
                # Updated in P06.1-I2a: the check records every signal in the reply.
                "                            rate_limited=is_rate_limit(status, stream_code),\n",
                "                            rate_limited=False,\n",
            )
        ],
        ["tests.test_client_session.ClientRateLimitFlagTest"],
    ),
    (
        "C2 nit 5 production phase needs an answer (feature-gated)",
        [
            (
                P,
                '        elif production.outcome == "no-response" and result.verdict not in NOT_A_PASS:\n',
                "        elif False:\n",
            )
        ],
        [
            "tests.test_answers.ProductionPhaseAnswerTest.test_feature_gated_case_without_a_production_answer_is_inconclusive"
        ],
    ),
    (
        "C2 nit 5 production phase needs an answer (S10)",
        [
            (
                P,
                '        elif production.outcome == "no-response" and verdict.label not in NOT_A_PASS:\n',
                "        elif False:\n",
            )
        ],
        [
            "tests.test_answers.ProductionPhaseAnswerTest.test_poll_vote_without_a_production_answer_is_inconclusive"
        ],
    ),
    (
        "C2 nit 6 exactly one request",
        [(P, "    if len(reply.requests) > 1:\n", "    if False:\n")],
        [
            "tests.test_answers.OneRequestTest.test_two_recorded_requests_have_no_answer",
            "tests.test_answers.OneRequestTest.test_generic_case_with_two_requests_is_inconclusive",
        ],
    ),
    (
        "C2 nit 6 G1's one POST /guest",
        [
            (
                P,
                '        if len(reply.requests) != 1 or reply.requests[0].get("path") != "/guest":\n            return None\n        return reply.requests[0]\n',
                '        return next((r for r in reply.requests if r.get("path") == "/guest"), None)\n',
            )
        ],
        ["tests.test_answers.OneRequestTest.test_guest_attempt_with_another_request_has_no_answer"],
    ),
    (
        "C2 nit 7 E5 with an unreadable stored user",
        [
            (
                P,
                '        if stored is None:\n            verdict = matrix.Verdict(matrix.INCONCLUSIVE, "A\'s stored user could not be read")\n',
                '        if False:\n            verdict = matrix.Verdict(matrix.INCONCLUSIVE, "A\'s stored user could not be read")\n',
            )
        ],
        [
            "tests.test_procedures.StoredUserUnreadableTest.test_e5_is_inconclusive_when_as_stored_user_cannot_be_read"
        ],
    ),
    (
        "C2 nit 7 S14 with an unreadable stored user",
        [(P, "        if read is None:\n", "        if False:\n")],
        [
            "tests.test_procedures.StoredUserUnreadableTest.test_s14_is_inconclusive_when_as_stored_user_cannot_be_read"
        ],
    ),
    (
        "C2 nit 7 the stored user is matched by ID",
        [
            (
                P,
                '        for user in users if result.ok and isinstance(users, list) else []:\n            if isinstance(user, dict) and user.get("id") == user_id:\n                return user\n        return None\n',
                "        return (users or [{}])[0]\n",
            )
        ],
        [
            "tests.test_procedures.StoredUserUnreadableTest.test_server_user_matches_the_id",
            "tests.test_procedures.StoredUserUnreadableTest.test_e5_is_inconclusive_when_as_stored_user_cannot_be_read",
        ],
    ),
    (
        "C2 nit 8 second Ctrl-C inside finish()",
        [
            (
                C,
                "            problems = run.finish(cleanup=cleanup_needed)\n        except KeyboardInterrupt:\n",
                "            problems = run.finish(cleanup=cleanup_needed)\n        except ZeroDivisionError:\n",
            )
        ],
        ["tests.test_cli.CommandTest.test_second_ctrl_c_inside_finish_keeps_the_results_file"],
    ),
    (
        "C2 nit 8 results written before the end of the run",
        [
            (
                C,
                '            write_json(f"run-{prefix}.json", early, ctx.secrets)\n',
                "            pass\n",
            )
        ],
        ["tests.test_cli.CommandTest.test_results_are_written_before_the_end_of_the_run"],
    ),
    (
        "C2 nit 9 accepted but unverified is not 'not restored'",
        [
            (
                P,
                "            if change.unverified is not None:\n                # The restore was made and accepted",
                "            if False:\n                # The restore was made and accepted",
            )
        ],
        ["tests.test_temporary_changes.UnverifiedRemovalTest"],
    ),
    (
        "C2 nit 9 B's probe stopped by a guardrail leaves the removal unverified",
        [
            (
                P,
                "                except GuardrailStop as exc:\n                    # The removal was accepted; only B's probe could not be made.\n",
                "                except ZeroDivisionError as exc:\n                    # The removal was accepted; only B's probe could not be made.\n",
            )
        ],
        ["tests.test_temporary_changes.UnverifiedRemovalTest"],
    ),
    (
        "C2 nit 10 credential key names",
        [(RD, '_SENSITIVE_SUFFIXES = ("_token", "_key")\n', '_SENSITIVE_SUFFIXES = ("_token",)\n')],
        [
            "tests.test_redaction.RedactionTest.test_credential_keys_of_the_app_settings_model_are_redacted"
        ],
    ),
    (
        "C2 review: E5 keeps a stored-role FAIL before its restore",
        [
            unobserved(
                '            self._observe(\n                self._result(\n                    case,\n                    request,\n                    _observed(answer),\n                    "control not judged",\n                    matrix.Verdict(matrix.FAIL, "the change reached Stream\'s stored state"),'
            )
        ],
        [
            TI + "ReviewOfC2Test.test_e5_stored_role_fail_survives_a_rate_limited_restore",
            TI + "ReviewOfC2Test.test_e5_failed_restore_stops_the_run_after_its_row",
        ],
    ),
    (
        "C2 review: E5's failed restore stops the run",
        [
            (
                P,
                "            except Exception as exc:\n                # Later cases must not run with A holding another role.\n",
                "            except ZeroDivisionError as exc:\n                # Later cases must not run with A holding another role.\n",
            )
        ],
        [TI + "ReviewOfC2Test.test_e5_failed_restore_stops_the_run_after_its_row"],
    ),
    (
        "C2 review: a failing progress write never replaces the stop",
        [
            (
                P,
                "        try:\n            progress()\n        except Exception as exc:\n",
                "        try:\n            progress()\n        except ZeroDivisionError as exc:\n",
            )
        ],
        [
            TI + "ReviewOfC2Test.test_a_failing_progress_write_never_replaces_a_guardrail_stop",
            TI + "ReviewOfC2Test.test_ctrl_c_is_kept_when_the_progress_write_fails",
        ],
    ),
    (
        "C2 review: a key still overridden keeps the change journalled",
        [
            (
                P,
                "                    probe_stop = exc\n                    continue\n",
                "                    change.unverified = 'probe stopped'\n                    raise\n",
            )
        ],
        [TI + "ReviewOfC2Test.test_a_key_still_overridden_keeps_the_change_journalled"],
    ),
    (
        "C2 review: finish keeps its problems as it finds them",
        [
            (
                P,
                "        problems: list[str] = []\n        self.post_run_problems = problems\n        for change in list(reversed(self.journal)):\n",
                "        problems: list[str] = []\n        for change in list(reversed(self.journal)):\n",
            )
        ],
        [TI + "ReviewOfC2Test.test_finish_keeps_the_problems_found_before_a_second_ctrl_c"],
    ),
    (
        "C2 review: results files are written atomically",
        [
            (
                "glow_stream_proof/workdir.py",
                '    partial = path.with_name(path.name + ".partial")\n    partial.write_text(text, encoding="utf-8")\n    partial.replace(path)\n',
                '    path.write_text("", encoding="utf-8")\n    partial = path.with_name(path.name + ".partial")\n    partial.write_text(text, encoding="utf-8")\n    partial.replace(path)\n',
            )
        ],
        ["tests.test_cli.AtomicWriteTest"],
    ),
    (
        "C2 review: a Ctrl-C during the early write still reaches the restores",
        [
            (
                C,
                "        except (Exception, KeyboardInterrupt) as exc:  # never in the way of the restores below\n",
                "        except Exception as exc:  # never in the way of the restores below\n",
            )
        ],
        ["tests.test_cli.CommandTest.test_ctrl_c_during_the_early_write_still_restores"],
    ),
    # -- P06.1-C3 ------------------------------------------------------------------
    (
        "C3 RT2/RT3 a feature refusal is REFUSED (feature off), not HOLDS",
        [(P, "                matrix.REFUSED_FEATURE,\n", "                matrix.HOLDS,\n")],
        [
            TA
            + "PayloadRefusalAttributionTest.test_feature_refusals_are_refused_feature_not_holds",
            TA
            + "RequestUnderTestInCasesTest.test_rt2_feature_refusal_is_refused_feature_not_holds",
        ],
    ),
    (
        "C3 RT2 an auth or permission refusal without a positive control is INCONCLUSIVE",
        [
            (
                P,
                "                verdict = matrix.Verdict(\n"
                "                    matrix.INCONCLUSIVE,\n"
                '                    f"{outcome} error, but no positive control:',
                "                verdict = matrix.Verdict(\n"
                "                    matrix.HOLDS,\n"
                '                    f"{outcome} error, but no positive control:',
            )
        ],
        [
            TA
            + "PayloadRefusalAttributionTest.test_rt2_auth_or_permission_refusal_has_no_positive_control"
        ],
    ),
    (
        "C3 RT3 an auth or permission refusal HOLDS only when B's own request succeeded",
        [(P, RT3_CONTROL_HOLDS, "            elif True:\n")],
        [
            TA
            + "PayloadRefusalAttributionTest.test_rt3_refusal_without_a_successful_control_is_inconclusive"
        ],
    ),
    (
        "C3 RT3 the control, B's own identical request, is made",
        [
            (
                P,
                '        if outcome in ("auth", "permission") and control_label is not None:\n',
                "        if False:\n",
            )
        ],
        [
            TA
            + "PayloadRefusalAttributionTest.test_rt3_auth_or_permission_refusal_holds_with_bs_own_request"
        ],
    ),
    (
        "C3 RT3 the matrix names B's session as RT3's control",
        [
            (
                "glow_stream_proof/matrix.py",
                '                session="B",\n                note="B connected and watching AB; B\'s own markRead with the same body",\n',
                '                note="B connected and watching AB; B\'s own markRead with the same body",\n',
            )
        ],
        [
            TA
            + "PayloadRefusalAttributionTest.test_rt3_auth_or_permission_refusal_holds_with_bs_own_request"
        ],
    ),
    (
        "C3 RT3 the control's own events are not searched for the marker",
        [
            (
                P,
                "        windows = after_request + after_probe\n",
                "        windows = after_request + after_probe + control_events\n",
            )
        ],
        [TA + "PayloadRefusalAttributionTest.test_rt3_controls_own_events_are_not_searched"],
    ),
    (
        "C3 F1 an observed FAIL survives a failed enabling request",
        [
            (
                P,
                "        if not on.ok and result.verdict != matrix.FAIL:\n",
                "        if not on.ok:\n",
            )
        ],
        [TA + "FeatureOnFailTest.test_fail_survives_a_failed_enabling_request"],
    ),
    (
        "C3 F2 a restore's charge or limit signal is recorded",
        [
            (
                P,
                "            self.record_signal(exc)\n            if change.unverified is not None:\n",
                "            if change.unverified is not None:\n",
            )
        ],
        [
            SS + "SignalRecordTest.test_a_signal_behind_another_stop_skips_the_cleanup",
            TCC + "test_a_signal_met_by_the_end_of_run_restore_skips_the_cleanup",
            TCC + "test_rate_limited_restores_at_the_end_skip_the_cleanup",
        ],
    ),
    (
        "C3 F2 finish() skips the cleanup after a recorded signal",
        [(P, "        elif self.stop_signals:\n", "        elif False:\n")],
        [
            SS + "SignalRecordTest.test_a_signal_behind_another_stop_skips_the_cleanup",
            TCC + "test_a_signal_met_by_the_end_of_run_restore_skips_the_cleanup",
            TCC + "test_a_signal_as_the_runs_own_stop_skips_the_cleanup",
            "tests.test_temporary_changes.FinishTest.test_finish_restores_the_journal_and_verifies_the_configuration",
        ],
    ),
    (
        "C3 F2 cmd_run adds its own stop to the run's record",
        [(C, "        run.record_signal(exc)\n", "        pass\n")],
        [TCC + "test_a_signal_as_the_runs_own_stop_skips_the_cleanup"],
    ),
    (
        "C3 F2 a signal met by the cleanup is recorded",
        [
            (
                P,
                "                self.record_signal(exc)\n                if exc.at_once:\n",
                "                if exc.at_once:\n",
            )
        ],
        [SS + "SignalRecordTest.test_a_signal_met_during_cleanup_ends_it_and_is_recorded"],
    ),
    (
        "C3 F2 a signal ends the cleanup at once (untested until C3)",
        [
            (
                P,
                "                if exc.at_once:\n                    break\n",
                "                if False:\n                    break\n",
            )
        ],
        [SS + "SignalRecordTest.test_a_signal_met_during_cleanup_ends_it_and_is_recorded"],
    ),
    (
        "C3 F2 a signal met by the final configuration read is recorded",
        [
            (
                P,
                '            self.record_signal(exc)\n            problems.append(f"configuration not verified',
                '            problems.append(f"configuration not verified',
            )
        ],
        [SS + "SignalRecordTest.test_a_signal_met_by_the_final_configuration_read_is_recorded"],
    ),
    (
        "C3 F2 a rate limit is a charge or limit signal",
        [
            (
                U,
                "        self.at_once = at_once or rate_limited\n",
                "        self.at_once = at_once\n",
            )
        ],
        [
            SS + "SignalRecordTest.test_a_signal_met_during_cleanup_ends_it_and_is_recorded",
            TCC + "test_rate_limited_restores_at_the_end_skip_the_cleanup",
        ],
    ),
    (
        "C3 F2 the server's response hook marks and records a signal",
        [
            (S, SERVER_IMPORT, SERVER_IMPORT_C2),
            (
                S,
                # Updated in P06.1-I2a: the message names a rate limit's reset.
                "            raise self._ledger.stop_at_once(\n"
                '                f"server {method} {path}: {signal}{_rate_limit_reset(response)}; stopping at once",\n'
                "                rate_limited=is_rate_limit(response.status_code, code),\n",
                "            raise GuardrailStop(\n"
                '                f"server {method} {path}: {signal}{_rate_limit_reset(response)}; stopping at once",\n'
                "                rate_limited=is_rate_limit(response.status_code, code),\n",
            ),
        ],
        ["tests.test_server_api.StopAtOnceFlagTest.test_typed_and_raw_calls_mark_the_signal"],
    ),
    (
        "C3 F2 the server's result check marks and records a signal",
        [
            (S, SERVER_IMPORT, SERVER_IMPORT_C2),
            (
                S,
                # Updated in P06.1-I2a: the message names a rate limit's reset.
                "            raise self._ledger.stop_at_once(\n"
                '                f"server {method} {path}: {signal}{_rate_limit_reset(response)}; stopping at once",\n'
                "                rate_limited=is_rate_limit(result.status, result.code),\n",
                "            raise GuardrailStop(\n"
                '                f"server {method} {path}: {signal}{_rate_limit_reset(response)}; stopping at once",\n'
                "                rate_limited=is_rate_limit(result.status, result.code),\n",
            ),
        ],
        ["tests.test_server_api.StopAtOnceFlagTest.test_the_result_check_marks_the_signal"],
    ),
    (
        "C3 F2 a client's recorded request marks and records a signal",
        [
            (
                B,
                # Updated in P06.1-I2a: the stop is collected, then raised.
                "                        self._ledger.stop_at_once(\n"
                '                            f"client {self.label}: {signal}; stopping at once",\n'
                "                            rate_limited=is_rate_limit(status, stream_code),\n",
                "                        GuardrailStop(\n"
                '                            f"client {self.label}: {signal}; stopping at once",\n'
                "                            rate_limited=is_rate_limit(status, stream_code),\n",
            )
        ],
        [
            "tests.test_client_session.ClientRateLimitFlagTest.test_every_client_signal_stops_at_once"
        ],
    ),
    (
        "C3 F2 a client's error marks and records a signal",
        [
            (
                B,
                # Updated in P06.1-I2a: the stop is collected, then raised.
                "                    self._ledger.stop_at_once(\n"
                '                        f"client {self.label}: {signal}; stopping at once",\n'
                "                        rate_limited=is_rate_limit(reply.status, reply.code),\n",
                "                    GuardrailStop(\n"
                '                        f"client {self.label}: {signal}; stopping at once",\n'
                "                        rate_limited=is_rate_limit(reply.status, reply.code),\n",
            )
        ],
        [
            "tests.test_client_session.ClientRateLimitFlagTest.test_every_client_signal_stops_at_once"
        ],
    ),
    (
        "C3 review: the ledger records a signal as its stop is raised",
        [(U, "        self.signals.append(stop)\n        return stop\n", "        return stop\n")],
        [
            SS + "SignalReplacedInFlightTest",
            TCC + "test_a_signal_whose_stop_a_ctrl_c_replaced_skips_the_cleanup",
            "tests.test_server_api.StopAtOnceFlagTest.test_typed_and_raw_calls_mark_the_signal",
            "tests.test_client_session.ClientRateLimitFlagTest.test_every_client_signal_stops_at_once",
        ],
    ),
    (
        "C3 review: a recorded signal stops the matrix after its case",
        [
            (
                P,
                "            if self.stop_signals:\n                # The signal's stop was replaced in flight",
                "            if False:\n                # The signal's stop was replaced in flight",
            )
        ],
        [
            SS
            + "SignalReplacedInFlightTest.test_an_error_that_replaces_the_stop_still_stops_the_run"
        ],
    ),
    (
        "C3 nit 3 a pattern counts only at a line start",
        [(FR, '        if i == 0 or text[i - 1] == "\\n":\n', "        if True:\n")],
        [
            "tests.test_fix_reversals.FixReversalsTest.test_a_pattern_matches_only_at_a_line_start",
            "tests.test_fix_reversals.FixReversalsTest.test_every_pattern_starts_a_line_once",
        ],
    ),
    (
        "C3 nit 3 an edited file that does not load is not demonstrated",
        [(FR, "    if done.returncode == 0:\n        return None\n", "    return None\n")],
        [
            "tests.test_fix_reversals.FixReversalsTest.test_an_edit_that_does_not_compile_or_import_is_reported"
        ],
    ),
    (
        "C3 nit 4 a feature-on FAIL stays FAIL without a production answer",
        [
            (
                P,
                '        elif production.outcome == "no-response" and result.verdict not in NOT_A_PASS:\n',
                '        elif production.outcome == "no-response":\n',
            )
        ],
        [
            TA
            + "ProductionPhaseAnswerTest.test_feature_on_fail_survives_a_production_request_without_an_answer"
        ],
    ),
    (
        "C3 nit 4 a polls-on FAIL stays FAIL without a production answer",
        [
            (
                P,
                '        elif production.outcome == "no-response" and verdict.label not in NOT_A_PASS:\n',
                '        elif production.outcome == "no-response":\n',
            )
        ],
        [
            TA
            + "ProductionPhaseAnswerTest.test_polls_on_fail_survives_a_production_vote_without_an_answer"
        ],
    ),
    (
        "C3 nit 4 a guardrail met by the undo after an interruption stops the run",
        [
            (
                P,
                '            raise\n        except Exception:  # recorded in the row as "not completed"; the interruption goes on\n',
                '            return\n        except Exception:  # recorded in the row as "not completed"; the interruption goes on\n',
            )
        ],
        [
            TI
            + "ReviewScenariosTest.test_a_guardrail_met_by_the_undo_after_an_interruption_stops_the_run"
        ],
    ),
    (
        "C3 nit 4 a second Ctrl-C keeps the problems finish() found",
        [(C, "                *run.post_run_problems,\n", "")],
        [TCC + "test_second_ctrl_c_keeps_the_problems_finish_found"],
    ),
    (
        "C3 nit 4 a second Ctrl-C closes the client processes",
        [(C, "            run.close_sessions()\n", "            pass\n")],
        [TCC + "test_second_ctrl_c_closes_the_client_sessions"],
    ),
    (
        "C3 nit 4 a client's error flags a rate limit",
        [
            (
                B,
                # Updated in P06.1-I2a: the check records every signal in the reply.
                "                        rate_limited=is_rate_limit(reply.status, reply.code),\n",
                "                        rate_limited=False,\n",
            )
        ],
        [
            "tests.test_client_session.ClientRateLimitFlagTest.test_the_error_only_check_flags_a_rate_limit"
        ],
    ),
    (
        "C3 nit 4 RT2/RT3 are INCONCLUSIVE unless B was listening",
        [(P, "        elif not listening:\n", "        elif False:\n")],
        [
            TA
            + "PayloadRefusalAttributionTest.test_a_refusal_while_b_is_not_listening_is_inconclusive"
        ],
    ),
    (
        "C3 nit 5 each request of a command is kept in the row",
        [
            (
                P,
                "        if self._multiple_requests:\n            # A command of this case recorded",
                "        if False:\n            # A command of this case recorded",
            )
        ],
        [TA + "OneRequestTest.test_each_request_of_a_command_is_kept_and_a_success_is_undone"],
    ),
    (
        "C3 nit 5 a 2xx among a command's requests is undone",
        [
            (
                P,
                "        succeeded = any(_succeeded(r) for r in reply.requests)\n",
                '        succeeded = outcome == "success"\n',
            )
        ],
        [TA + "OneRequestTest.test_each_request_of_a_command_is_kept_and_a_success_is_undone"],
    ),
    (
        "C3 nit 6 B's probe stop is kept in the stops",
        [
            (
                P,
                "                self.stops.append(\n"
                "                    f\"B's members query after AB's override removal: {self._text(probe_stop)}\"\n"
                "                )\n",
                "",
            )
        ],
        [SS + "ProbeStopKeptTest"],
    ),
    (
        "C3 nit 6 B's probe stop is recorded as a signal",
        [(P, "                self.record_signal(probe_stop)\n", "                pass\n")],
        [SS + "ProbeStopKeptTest"],
    ),
    (
        "C3 nit 7 no unset of A's member field after a guardrail stop",
        [
            (
                P,
                "        except GuardrailStop as exc:\n            self._member_field_kept(",
                "        except ZeroDivisionError as exc:\n            self._member_field_kept(",
            )
        ],
        [
            SS + "MemberFieldUnsetTest.test_no_unset_after_a_guardrail_stop_in_bs_reads",
            SS + "MemberFieldUnsetTest.test_no_unset_after_a_guardrail_stop_in_the_control",
        ],
    ),
    (
        "C3 nit 8 a failed read of A's stored user stops the run",
        [
            (
                P,
                "        except Exception as exc:  # Stream did not answer the listing with 2xx\n",
                "        except ZeroDivisionError as exc:  # Stream did not answer the listing with 2xx\n",
            )
        ],
        ["tests.test_procedures.StoredUserReadFailureTest"],
    ),
    (
        "C3 nit 8 a listing without A stops the run too",
        [
            (
                P,
                "        if stored is None:\n            self._defer_stop(\n",
                "        if False:\n            self._defer_stop(\n",
            )
        ],
        ["tests.test_procedures.StoredUserUnreadableTest"],
    ),
    (
        "C3 nit 9 the usage ledger is written through a temporary file",
        [
            (
                U,
                '        _replace(self.path, json.dumps({"session": asdict(self.session)}, indent=2) + "\\n")\n',
                '        self.path.write_text(json.dumps({"session": asdict(self.session)}, indent=2) + "\\n")\n',
            )
        ],
        [
            "tests.test_usage_and_report.UsageTest.test_an_interrupted_save_leaves_the_previous_ledger_whole"
        ],
    ),
    (
        "C3 nit 10 the early-write failure note is redacted",
        [
            (
                C,
                '                f"{type(exc).__name__}: {ctx.redactor.text(str(exc))}"\n',
                '                f"{type(exc).__name__}: {exc}"\n',
            )
        ],
        [TCC + "test_the_early_write_failure_note_is_redacted"],
    ),
    (
        "C3 nit 8 a guardrail stop on the read of A's stored user is not deferred",
        [
            (
                P,
                "        except GuardrailStop:\n            raise\n        except Exception as exc:  # Stream did not answer the listing with 2xx\n",
                "        except Exception as exc:  # Stream did not answer the listing with 2xx\n",
            )
        ],
        [
            "tests.test_procedures.StoredUserReadFailureTest.test_a_guardrail_stop_on_the_read_is_the_runs_stop"
        ],
    ),
    (
        "C3 RT3 kept: both windows before the control",
        [
            unobserved(
                '            self._observe(\n                self._result(\n                    case,\n                    request,\n                    _observed(answer),\n                    f"B listening (received a probe message): {listening}; control not completed",'
            )
        ],
        [KEPT + "test_rt3_marker_after_the_probe_survives_the_control_ending"],
    ),
    (
        "C3 F2 the client processes are closed when the cleanup is skipped",
        [
            (
                P,
                # Updated in P06.1-I2a: the sessions now close before the cleanup is decided.
                "        # signal among it skips the cleanup like any other (P06.1-I2a).\n        self.close_sessions()\n",
                "        # signal among it skips the cleanup like any other (P06.1-I2a).\n",
            )
        ],
        [
            TCC + "test_a_signal_met_by_the_end_of_run_restore_skips_the_cleanup",
            TCC + "test_rate_limited_restores_at_the_end_skip_the_cleanup",
            TCC + "test_a_signal_as_the_runs_own_stop_skips_the_cleanup",
        ],
    ),
    (
        "C3 nit 5 each case's row lists only its own commands",
        [
            (
                P,
                "            self._partial = None\n            self._multiple_requests = []\n",
                "            self._partial = None\n",
            )
        ],
        [TA + "OneRequestTest.test_each_request_of_a_command_is_kept_and_a_success_is_undone"],
    ),
    (
        "C3 review: the production command's requests are listed in the row",
        [
            (
                P,
                "        if self._multiple_requests:\n            # The row was built before the production phase;",
                "        if False:\n            # The row was built before the production phase;",
            )
        ],
        [TA + "ProductionPhaseAnswerTest.test_a_production_command_with_several_requests"],
    ),
    (
        "C3 review: a 2xx among the production command's requests is undone",
        [
            (
                P,
                # Updated in P06.1-I2a: the production phase's undo is labelled.
                '        if production_succeeded:\n            self._undo_client_success(case, result, "production")\n',
                '        if production.outcome == "success":\n            self._undo_client_success(case, result, "production")\n',
            )
        ],
        [TA + "ProductionPhaseAnswerTest.test_a_production_command_with_several_requests"],
    ),
    (
        "C3 review: RT3's control counts only as the same request",
        [(P, RT3_CONTROL_HOLDS, '            elif control.outcome == "success":\n')],
        [
            TA
            + "PayloadRefusalAttributionTest.test_rt3_control_that_was_another_request_is_inconclusive"
        ],
    ),
    (
        "C3 review: S15 sends no unset after a recorded signal, whatever is in flight",
        [
            (
                P,
                "            if self.stop_signals:\n                # A signal was met, though another exception is in flight (for example\n",
                "            if False:\n                # A signal was met, though another exception is in flight (for example\n",
            )
        ],
        [SS + "MemberFieldUnsetTest.test_no_unset_after_a_signal_whose_stop_is_not_in_flight"],
    ),
    (
        "C3 review: no undo after a recorded signal, whatever is in flight",
        [
            (
                P,
                "        if self.stop_signals:\n            # A signal was met, though another exception is in flight: nothing more is\n",
                "        if False:\n            # A signal was met, though another exception is in flight: nothing more is\n",
            )
        ],
        [TI + "ReviewScenariosTest.test_no_undo_after_a_signal_whose_stop_an_error_replaced"],
    ),
    (
        "C3 nit 5 a poll or group created among several requests is tracked",
        [
            (
                P,
                "        if succeeded:\n            self._track_client_created(reply)\n",
                '        if succeeded:\n            if outcome == "success":\n                self._track_client_created(reply)\n',
            )
        ],
        [TA + "OneRequestTest.test_a_poll_created_among_several_requests_is_deleted_at_cleanup"],
    ),
    # -- P06.1-I2a, step 1: the C3 review's items, the guard and the closing checks --
    (
        "I2a guard: a user the run did not create is refused",
        [(G, "    if any(not scope.owns_user(u) for u in users):\n", "    if False:\n")],
        [
            TGU + "RefusalTest.test_a_user_the_run_did_not_create_is_refused",
            TGU + "ServerHookTest.test_a_refused_request_is_neither_sent_nor_counted",
        ],
    ),
    (
        "I2a guard: a channel the run did not create is refused",
        [(G, "    if any(not scope.owns_channel(c) for c in channels):\n", "    if False:\n")],
        [
            TGU + "RefusalTest.test_a_channel_the_run_did_not_create_is_refused",
            TGU + "GuardedRunTest.test_a_refusal_in_a_case_stops_the_run_after_its_row",
        ],
    ),
    (
        "I2a guard: an application setting outside the journal is refused",
        [(G, "    if not keys <= scope.journalled_app_settings():\n", "    if False:\n")],
        [
            TGU + "RefusalTest.test_application_changes_outside_the_journal_are_refused",
            TGU + "GuardedRunTest.test_the_run_is_the_guards_scope",
        ],
    ),
    (
        "I2a guard: a match-type toggle outside the journal is refused",
        [
            (
                G,
                "    if not fixed_ok or not toggled <= scope.journalled_type_features():\n",
                "    if False:\n",
            )
        ],
        [TGU + "RefusalTest.test_match_type_changes_outside_the_journal_are_refused"],
    ),
    (
        "I2a guard: any other kind of change is refused",
        [(G, '    return "not a kind of request this proof makes"\n', "    return None\n")],
        [TGU + "RefusalTest.test_other_kinds_of_change_are_refused"],
    ),
    (
        "I2a guard: a message delete needs a message the run recorded",
        [
            (
                G,
                "        if len(parts) >= 2 and parts[1] not in _KEYWORDS and not scope.owns_message(parts[1]):\n",
                "        if False:\n",
            )
        ],
        [TGU + "RefusalTest.test_a_message_poll_or_group_must_be_the_runs"],
    ),
    (
        "I2a guard: the server client asks the guard before sending",
        [
            (
                S,
                "        if self.guard is not None:\n            # Before anything is counted or sent (DM-04 finding 1).\n",
                "        if False:\n            # Before anything is counted or sent (DM-04 finding 1).\n",
            )
        ],
        [TGU + "ServerHookTest.test_a_refused_request_is_neither_sent_nor_counted"],
    ),
    (
        "I2a guard: the run installs the guard with itself as the scope",
        [(P, "        self.api.guard = self._guard_refusal\n", "        pass\n")],
        [
            TGU + "GuardedRunTest.test_the_run_is_the_guards_scope",
            TGU + "GuardedRunTest.test_a_refusal_in_a_case_stops_the_run_after_its_row",
        ],
    ),
    (
        "I2a guard: cleanup --apply is guarded by the prefix",
        [
            (
                C,
                "    ctx.api.guard = lambda method, path, body, params: guard.refusal(\n"
                "        method, path, body, params, scope\n    )\n",
                "    pass\n",
            )
        ],
        [TGU + "CleanupCommandTest.test_cleanup_apply_is_guarded_by_the_prefix"],
    ),
    (
        "I2a guard: the deleted-user artifact the cleanup creates is recorded",
        [
            (
                P,
                "        self.artifacts.extend(a for a in artifacts if a not in self.artifacts)\n",
                "        pass\n",
            )
        ],
        [TGU + "GuardedRunTest.test_the_artifact_the_runs_cleanup_creates_may_be_deleted"],
    ),
    (
        "I2a closing checks: verify compares every recorded setting",
        [
            (
                CF,
                "    problems += recorded_differences(app, recorded_app_settings() if recorded is None else recorded)\n",
                "",
            )
        ],
        [
            TRS + "test_an_application_wide_token_revocation_is_a_difference",
            TRS + "test_every_hook_is_a_difference",
            TRS + "test_every_recorded_setting_is_compared_except_guest_creation",
            TCK + "test_preflight_sees_an_application_wide_token_revocation",
            TCK + "test_the_end_of_the_run_sees_a_hook",
            TCK + "test_the_dry_run_configure_sees_them",
        ],
    ),
    (
        "I2a closing checks: an unrecorded setting must be absent or empty",
        [(CF, "        elif have is not _ABSENT and not _empty(have):\n", "        elif False:\n")],
        [
            TRS + "test_a_setting_the_baseline_did_not_record_may_be_absent_or_empty",
            TRS + "test_every_hook_is_a_difference",
        ],
    ),
    (
        "I2a gap: the runner keeps a request sent outside a command",
        [
            (
                RL,
                "      this.kept.push(record);\n    }\n    return record;\n",
                "    }\n    return record;\n",
            )
        ],
        ["tests.test_runner.RequestLogTest.test_every_request_is_reported_once_answered"],
    ),
    (
        "I2a gap: the runner keeps a command's request answered after its reply",
        [
            (
                RL,
                "        record.late = true;\n        this.kept.push(record);\n",
                "        record.late = true;\n",
            )
        ],
        ["tests.test_runner.RequestLogTest.test_every_request_is_reported_once_answered"],
    ),
    (
        "I2a gap: a reply's requests outside its command are checked",
        [
            (
                B,
                # Updated after the independent review (point 3): every signal is recorded.
                "        stops += self._late_signals(reply.background_requests, self._redactor.value(raw_async))\n",
                "        stops += []\n",
            )
        ],
        [
            TCS + "LateRequestsTest.test_a_request_sent_between_commands",
            TCS + "LateRequestsTest.test_an_answer_that_came_after_its_command_replied",
            TCS + "LateRequestsTest.test_an_asynchronous_sdk_error",
        ],
    ),
    (
        "I2a gap: an asynchronous SDK error is checked",
        [(B, "        for error in async_errors:\n", "        for error in ():\n")],
        [
            TCS + "LateRequestsTest.test_an_asynchronous_sdk_error",
            TCS + "ClosingSignalTest.test_the_end_of_the_run_closes_without_raising",
        ],
    ),
    (
        "I2a gap: the runner's own refusal is not a signal",
        [(B, '    if error.get("kind") == "budget":\n        return None\n', "")],
        [TCS + "LateRequestsTest.test_a_request_the_runner_refused_is_not_a_signal"],
    ),
    (
        "I2a gap: calls sent between commands are counted",
        [
            (
                B,
                # Updated after the independent review (point 3): counted after the checks.
                "        if background_calls:\n"
                "            # Sent by the SDK between commands; counted like any client call (P06.1-I2a).\n"
                "            tally(background_calls)\n",
                "",
            )
        ],
        [TCS + "LateRequestsTest.test_a_request_sent_between_commands"],
    ),
    (
        "I2a gap: closing a session checks its exit reply",
        [(B, "        stop = self._exit_signal() if exited else None\n", "        stop = None\n")],
        [
            TCS
            + "ClosingSignalTest.test_a_signal_at_exit_is_raised_when_nothing_else_is_in_flight",
            TCS + "ClosingSignalTest.test_a_signal_at_exit_never_replaces_an_exception_in_flight",
            TCS + "ClosingSignalTest.test_the_end_of_the_run_closes_without_raising",
        ],
    ),
    (
        "I2a gap: a signal at exit is raised only when nothing else is in flight",
        [
            (
                B,
                "        if stop is not None and raise_signal and sys.exc_info()[1] is None:\n",
                "        if stop is not None and raise_signal:\n",
            )
        ],
        [TCS + "ClosingSignalTest.test_a_signal_at_exit_never_replaces_an_exception_in_flight"],
    ),
    (
        "I2a gap: the end of the run closes its sessions without raising",
        [(P, "            session.close(raise_signal=False)\n", "            session.close()\n")],
        [
            SS
            + "ClosingSessionSignalTest.test_a_signal_a_session_reports_as_it_closes_skips_the_cleanup"
        ],
    ),
    (
        "I2a gap: the sessions close before the cleanup is decided",
        [
            (
                P,
                "        # signal among it skips the cleanup like any other (P06.1-I2a).\n        self.close_sessions()\n",
                "        # signal among it skips the cleanup like any other (P06.1-I2a).\n",
            )
        ],
        [
            SS
            + "ClosingSessionSignalTest.test_a_signal_a_session_reports_as_it_closes_skips_the_cleanup"
        ],
    ),
    (
        "I2a gap: the cleanup checks again once the sessions are closed",
        [
            (
                P,
                "        if self.stop_signals:\n            # A session reported a charge or limit signal as it closed: nothing is\n",
                "        if False:\n            # A session reported a charge or limit signal as it closed: nothing is\n",
            )
        ],
        [
            SS
            + "ClosingSessionSignalTest.test_the_cleanup_checks_again_once_the_sessions_are_closed"
        ],
    ),
    (
        "I2a nit 1: RT3's control window is searched",
        [
            (
                P,
                "        searched = self._searched_control_events(control_events, control_label)\n",
                "        searched: list[dict[str, Any]] = []\n",
            )
        ],
        [
            TA
            + "PayloadRefusalAttributionTest.test_rt3_control_window_is_searched_but_for_bs_own_read_events"
        ],
    ),
    (
        "I2a nit 1: only read events are left out of the control window",
        [
            (
                P,
                '                e.get("type") in ("message.read", "notification.mark_read")\n'
                '                and _dig(e, "user.id") == own_id\n',
                '                _dig(e, "user.id") == own_id\n',
            )
        ],
        [
            TA
            + "PayloadRefusalAttributionTest.test_rt3_control_window_is_searched_but_for_bs_own_read_events"
        ],
    ),
    (
        "I2a nit 1: only the control member's own read events are left out",
        [(P, '                and _dig(e, "user.id") == own_id\n', "                and True\n")],
        [
            TA
            + "PayloadRefusalAttributionTest.test_rt3_control_window_is_searched_but_for_bs_own_read_events"
        ],
    ),
    (
        "I2a nit 2(a): a charge signal met by the cleanup ends it (402 and code 99)",
        [
            (
                P,
                "                if exc.at_once:\n                    break\n",
                "                if exc.rate_limited:\n                    break\n",
            )
        ],
        [SS + "SignalRecordTest.test_a_charge_signal_met_during_cleanup_ends_it_too"],
    ),
    (
        "I2a nit 2(b): S15 sends no unset after a budget stop",
        [
            (
                P,
                "        except GuardrailStop as exc:\n"
                '            self._member_field_kept(out, key, f"a guardrail stopped the run ({self._text(exc)})")\n'
                "            raise\n",
                "        except GuardrailStop as exc:\n"
                "            if exc.at_once:\n"
                '                self._member_field_kept(out, key, f"a guardrail stopped the run ({self._text(exc)})")\n'
                "            else:\n"
                "                out[key] = self._unset_member_note()\n"
                "            raise\n",
            )
        ],
        [SS + "MemberFieldUnsetTest.test_no_unset_after_a_budget_stop_in_bs_reads"],
    ),
    (
        "I2a nit 2(c): RT3's control only after an authentication or permission refusal",
        [
            (
                P,
                '        if outcome in ("auth", "permission") and control_label is not None:\n',
                "        if control_label is not None:\n",
            )
        ],
        [
            TA
            + "PayloadRefusalAttributionTest.test_rt3_control_is_sent_only_after_an_auth_or_permission_refusal"
        ],
    ),
    (
        "I2a nit 4: a phase's undo note is kept beside the earlier one",
        [
            (
                P,
                '            note = f"{earlier}; {done}" if earlier else done\n',
                "            note = done\n",
            )
        ],
        [TA + "ProductionPhaseAnswerTest.test_both_phases_undo_notes_are_kept"],
    ),
    (
        "I2a nit 5: the printed report lists the charge or limit signals",
        [(RP, '    if results.get("stop_signals"):\n', "    if False:\n")],
        [
            "tests.test_usage_and_report.ReportTest.test_the_report_lists_every_charge_or_limit_signal"
        ],
    ),
    (
        "I2a DM-04 9(c): the cleanup's prefix scan includes deactivated users",
        [
            (
                P,
                "        listed = self.api.get(\n"
                '            "/api/v2/users",\n'
                "            params={\n"
                '                "payload": json.dumps(\n'
                '                    {"filter_conditions": {}, "limit": 100, "include_deactivated_users": True}\n',
                "        listed = self.api.get(\n"
                '            "/api/v2/users",\n'
                "            params={\n"
                '                "payload": json.dumps(\n'
                '                    {"filter_conditions": {}, "limit": 100}\n',
            )
        ],
        [
            "tests.test_cleanup.GuardedCleanupTest.test_a_deactivated_user_with_the_prefix_is_found_and_deleted"
        ],
    ),
    (
        "I2a signals by kind: only a rate limit without billing wording is only a rate limit",
        [
            (
                P,
                "        if self.ledger.signals and all(s.only_rate_limit for s in self.ledger.signals):\n",
                "        if self.ledger.signals and all(s.rate_limited for s in self.ledger.signals):\n",
            )
        ],
        [SS + "SignalKindTest.test_anything_else_is_a_charge_signal"],
    ),
    (
        "I2a signals by kind: billing wording in the server's response hook",
        [
            (
                S,
                "                billing=mentions_billing(message),\n",
                "                billing=False,\n",
            )
        ],
        [
            "tests.test_server_api.SignalKindAtTheServerTest.test_a_rate_limit_with_quota_wording_is_a_charge_signal"
        ],
    ),
    (
        "I2a signals by kind: billing wording in the server's result check",
        [
            (
                S,
                "                billing=mentions_billing(result.message),\n",
                "                billing=False,\n",
            )
        ],
        [
            "tests.test_server_api.SignalKindAtTheServerTest.test_a_rate_limit_with_quota_wording_is_a_charge_signal"
        ],
    ),
    (
        "I2a signals by kind: billing wording in a client's recorded request",
        [
            (
                B,
                "                            billing=mentions_billing(message if isinstance(message, str) else None),\n",
                "                            billing=False,\n",
            )
        ],
        [TCS + "ClientSignalKindTest.test_record_and_error_sites"],
    ),
    (
        "I2a signals by kind: billing wording in a client's error",
        [
            (
                B,
                "                        billing=mentions_billing(reply.message),\n",
                "                        billing=False,\n",
            )
        ],
        [TCS + "ClientSignalKindTest.test_record_and_error_sites"],
    ),
    (
        "I2a signals by kind: billing wording in an asynchronous SDK error",
        [
            (
                B,
                "    return signal, is_rate_limit(status, code), mentions_billing(text)\n",
                "    return signal, is_rate_limit(status, code), False\n",
            )
        ],
        [TCS + "LateRequestsTest.test_an_asynchronous_sdk_error"],
    ),
    (
        "I2a signals by kind: a rate limit's stop names its reset",
        [(S, '    return f" (x-ratelimit-reset {reset})" if reset else ""\n', '    return ""\n')],
        ["tests.test_server_api.SignalKindAtTheServerTest.test_the_stop_names_the_reset"],
    ),
    # The independent review's point 3 (P06.1-I2a).
    (
        "I2a review 3: every signal in a reply is recorded",
        [
            (
                B,
                "        stops += self._late_signals(reply.background_requests, self._redactor.value(raw_async))\n",
                "        stops = stops or self._late_signals(reply.background_requests, self._redactor.value(raw_async))\n",
            )
        ],
        [TCS + "EverySignalTest.test_a_charge_behind_a_rate_limit_is_recorded"],
    ),
    (
        "I2a review 3: a signal is recorded before the calls are counted",
        [
            (
                B,
                "            if stops:\n                # Already sent: counted without a check that could raise over the signal.\n",
                "            if False:\n                # Already sent: counted without a check that could raise over the signal.\n",
            )
        ],
        [TCS + "EverySignalTest.test_a_signal_is_not_hidden_by_the_budget"],
    ),
    # P06.1-I2a, step 2: the new cases' safety rules.
    (
        "I2a step 2 guard: a member named in the path",
        [(G, "            users = [parts[4], *users]\n", "            pass\n")],
        [TGU + "RefusalTest.test_a_user_the_run_did_not_create_is_refused"],
    ),
    (
        "I2a step 2 outage: the app send path refuses an unreachable provider",
        [
            (
                AS,
                "        except ProviderUnavailable as exc:\n",
                "        except ArithmeticError as exc:\n",
            )
        ],
        [
            "tests.test_policy_and_send.AppSendTest.test_an_unreachable_provider_refuses_the_send_and_keeps_nothing",
            TI2 + "OutageTest.test_the_send_is_refused_and_nothing_is_kept",
        ],
    ),
    (
        "I2a step 2 outage: the server send turns a connection error into a refusal",
        [
            (
                P,
                "    except (StreamTransportException, httpx.TransportError) as exc:\n",
                "    except ArithmeticError as exc:\n",
            )
        ],
        [TI2 + "OutageTest.test_the_send_is_refused_and_nothing_is_kept"],
    ),
    (
        "I2a step 2 delete: the hard-deleted user is not named at cleanup",
        [
            (
                MX,
                "                run.users.remove(run.ctx[mech.affected])\n",
                "                pass\n",
            )
        ],
        [TMX + "FamiliesTest.test_deactivation_and_the_hard_delete"],
    ),
    (
        "I2a step 2 delete: the channel the delete removed is not named at cleanup",
        [(MX, "            run.channels.remove(self.cid)\n", "            pass\n")],
        [TMX + "FamiliesTest.test_deactivation_and_the_hard_delete"],
    ),
    (
        "I2a step 2 sessions: the I1 sessions close before the families",
        [(P, "                self._close_i1_sessions()\n", "                pass\n")],
        [TMX + "StopsTest.test_the_i1_sessions_close_before_the_families_only_when_one_runs"],
    ),
    (
        "I2a step 2 sessions: a family closes its own sessions",
        [(MX, "                close_session(self.run, label)\n", "                pass\n")],
        [TMX + "BudgetAndSessionsTest.test_a_familys_own_sessions_are_closed_at_its_end"],
    ),
    (
        "I2a step 2 budget: a case starts only with the calls it declared",
        [
            (
                P,
                "        margin = max(CASE_CALL_MARGIN, case.calls if case is not None else 0)\n",
                "        margin = CASE_CALL_MARGIN\n",
            )
        ],
        [TMX + "BudgetAndSessionsTest.test_a_family_starts_only_with_the_calls_it_declared"],
    ),
    (
        "I2a step 2 rules: a revocation dimension needs a successful control",
        [
            (
                MX,
                '    if before is None or before.outcome != "success":\n',
                "    if before is None:\n",
            )
        ],
        [TMX + "RulesTest.test_a_dimension_ends_only_on_an_attributable_refusal_after_a_control"],
    ),
    (
        "I2a step 2 rules: an ended subscription needs a listener that received the probe",
        [(MX, "    if not listener:\n", "    if False:\n")],
        [TMX + "RulesTest.test_the_subscription_ends_only_with_a_listener_that_received_it"],
    ),
    (
        "I2a step 2 oracle: a channel a probe created is counted",
        [(I2, '            run.ledger.reserve("channels")\n', "            pass\n")],
        [TI2 + "OracleTest.test_a_missing_channel_that_a_probe_created_is_counted_and_cleaned_up"],
    ),
    (
        "I2a step 2 S15 mapping: a member field not restored stops the run",
        [
            (
                I2,
                "    if differ:\n        run._defer_stop(\n",
                "    if False:\n        run._defer_stop(\n",
            )
        ],
        [TI2 + "S15MapTest.test_a_restore_that_fails_stops_the_run_after_the_case"],
    ),
    # The independent review's points 1 and 5 (P06.1-I2a).
    (
        "I2a review 1: a write is put back however the field ends",
        [
            (
                I2,
                '            else:\n                entry["restored"] = _restore_quietly(\n                    run, case, channel_id, user_id, fields, original\n                )\n',
                "            else:\n                pass\n",
            )
        ],
        [TI2 + "S15MapTest.test_a_field_the_control_set_is_restored_when_bs_session_ends"],
    ),
    (
        "I2a review 1: nothing is put back for a field that reads as it was",
        [(I2, "    if not changed:\n", "    if False:\n")],
        [TI2 + "S15MapTest.test_nothing_is_put_back_for_a_field_that_was_never_changed"],
    ),
    (
        "I2a review 1: nothing is sent to restore after a guardrail stop",
        [
            (
                I2,
                '    except GuardrailStop as exc:\n        if entry.get("written"):\n',
                '    except ArithmeticError as exc:\n        if entry.get("written"):\n',
            )
        ],
        [TI2 + "S15MapTest.test_nothing_is_sent_to_restore_after_a_guardrail_stop"],
    ),
    (
        "I2a review 1: a record that cannot be read after the restore stops the run",
        [(I2, "    if now is None:\n", "    if now is None and False:\n")],
        [TI2 + "S15MapTest.test_a_record_that_cannot_be_read_after_restoring_stops_the_run"],
    ),
    # The independent review's point 2 (P06.1-I2a): the open subscription's window.
    (
        "I2a review 2: the listeners are collected first",
        [
            (
                MX,
                "        return [lbl for lbl in self.labels if lbl not in judged] + [\n            lbl for lbl in self.labels if lbl in judged\n        ]\n",
                "        return list(self.labels)\n",
            )
        ],
        [TMX + "WindowTest.test_a_late_delivery_is_not_taken_for_an_ended_subscription"],
    ),
    (
        "I2a review 2: a member that missed the probe gets a second window",
        [(MX, "        if second:\n", "        if False:\n")],
        [TMX + "WindowTest.test_a_late_delivery_is_not_taken_for_an_ended_subscription"],
    ),
    (
        "I2a review 2: a closed or recovered connection leaves a miss not shown",
        [(MX, "    if dropped:\n", "    if False:\n")],
        [
            TMX + "RulesTest.test_the_subscription_ends_only_with_a_listener_that_received_it",
            TMX
            + "WindowTest.test_a_closed_or_recovered_connection_leaves_a_channel_level_miss_not_shown",
        ],
    ),
    (
        "I2a review 2: an account-level mechanism's close is not taken for a drop",
        [
            (
                MX,
                '        relevant = changes if self.mech.scope == "channel" else changes & {"recovered"}\n',
                "        relevant = changes\n",
            )
        ],
        [
            TMX
            + "WindowTest.test_an_account_level_close_may_end_the_subscription_a_recovery_may_not"
        ],
    ),
    (
        "I2a review 2: the mechanism's own window counts",
        [(MX, "            self.note_connection(label, window)\n", "            pass\n")],
        [TMX + "WindowTest.test_a_close_in_the_mechanisms_own_window_counts_too"],
    ),
    # The independent review's point 4 (P06.1-I2a): a token issued after the mechanism.
    (
        "I2a review 4: an account-level mechanism is judged on a token issued after it",
        [
            (
                MX,
                '        self.dimensions = ACCOUNT_DIMENSIONS if mech.scope == "account" else DIMENSIONS\n',
                "        self.dimensions = DIMENSIONS\n",
            )
        ],
        [TMX + "FamiliesTest.test_token_revocation_on_two_devices"],
    ),
    (
        "I2a review 4: the revocation's late token is the token issued after it",
        [(MX, '                if name == "late":\n', "                if False:\n")],
        [TMX + "FamiliesTest.test_token_revocation_on_two_devices"],
    ),
    (
        "I2a review 4: deactivation and deletion issue a token after the mechanism",
        [
            (
                MX,
                '            elif mech.scope == "account":\n                self.fresh_token()\n',
                "            elif False:\n                self.fresh_token()\n",
            )
        ],
        [TMX + "FamiliesTest.test_deactivation_and_the_hard_delete"],
    ),
    (
        "I2a review 4: the policy requires every dimension of the mechanism",
        [
            (
                MX,
                '        for dim in dimensions\n        if dims.get(dim, {}).get("status") not in (ENDED, NOT_ENDED)\n',
                '        for dim in DIMENSIONS\n        if dims.get(dim, {}).get("status") not in (ENDED, NOT_ENDED)\n',
            )
        ],
        [TMX + "FamiliesTest.test_the_policy_requires_every_dimension_of_the_mechanism"],
    ),
    (
        "I2a review nit: a connect after the hard delete names the user at cleanup again",
        [
            (
                MX,
                "                if uid not in self.run.users:\n                    self.run.users.append(uid)\n",
                "                if False:\n                    self.run.users.append(uid)\n",
            )
        ],
        [TMX + "FamiliesTest.test_a_connect_that_creates_the_deleted_user_again_is_cleaned_up"],
    ),
    # The independent review's point 6 (P06.1-I2a): the existence oracle's pairs.
    (
        "I2a review 6: a pair without a determinate answer is inconclusive",
        [
            (
                I2,
                "    if found.outcome not in DETERMINATE or absent.outcome not in DETERMINATE:\n",
                "    if False:\n",
            )
        ],
        [TI2 + "OracleTest.test_a_pair_without_an_answer_is_inconclusive"],
    ),
    (
        "I2a review 6: identical input or feature errors show nothing",
        [(I2, "    if found.outcome in NO_ORACLE_WHEN_IDENTICAL:\n", "    if True:\n")],
        [TI2 + "OracleTest.test_identical_input_errors_are_inconclusive"],
    ),
    (
        "I2a review 7: an oracle seen before an interruption stays a FAIL",
        [
            (
                I2,
                '                    pr._http_answer(_call(run, "A", "channel", method, args, missing)),\n                )\n            )\n            observe()\n',
                '                    pr._http_answer(_call(run, "A", "channel", method, args, missing)),\n                )\n            )\n            pass\n',
            )
        ],
        [TI2 + "OracleTest.test_an_oracle_seen_before_an_interruption_stays_a_fail"],
    ),
    # The independent review's point 8 (P06.1-I2a).
    (
        "I2a review 8: the delete's channel is checked at cleanup before the delete is sent",
        [
            (
                MX,
                '        if mech.key == "delete":\n            # The hard delete may remove the channel (a conversation of two or fewer\n',
                "        if False:\n            # The hard delete may remove the channel (a conversation of two or fewer\n",
            )
        ],
        [
            TMX
            + "FamiliesTest.test_a_stop_during_the_hard_deletes_task_leaves_the_channel_checked_first",
            TMX + "FamiliesTest.test_the_cleanup_names_no_user_or_channel_that_is_gone",
        ],
    ),
    # The independent review's nits (P06.1-I2a).
    (
        "I2a review nit: the guard reads a mute's target",
        [(G, '        "target_id",\n', "")],
        [TGU + "RefusalTest.test_a_user_the_run_did_not_create_is_refused"],
    ),
    (
        "I2a review nit: the guard reads a poll update's poll from its body",
        [(G, '        if len(parts) == 1 and verb in ("PUT", "PATCH"):\n', "        if False:\n")],
        [TGU + "RefusalTest.test_a_message_poll_or_group_must_be_the_runs"],
    ),
    (
        "I2a review nit: a show is sent only once the channel is hidden again",
        [
            (
                MX,
                '            if not again.ok or hidden["listed"] != "not listed":\n',
                "            if False:\n",
            )
        ],
        [TMX + "FamiliesTest.test_a_hide_that_is_not_made_again_leaves_the_undo_unjudged"],
    ),
    (
        "I2a review nit: a delete whose task did not complete is not judged",
        [(MX, "        if why is not None:\n", "        if False:\n")],
        [TMX + "FamiliesTest.test_the_cleanup_names_no_user_or_channel_that_is_gone"],
    ),
    (
        "I2a review nit: expiry controls count only well before the expiry",
        [(I2, "    elif exp - before_done < EXPIRY_MARGIN_SECONDS:\n", "    elif False:\n")],
        [
            TI2
            + "TokenExpiryTest.test_controls_that_finish_too_close_to_the_expiry_are_inconclusive"
        ],
    ),
    (
        "I2a review nit: G2's guest creation is tried again after any refusal",
        [
            (
                I2,
                "    if not created.ok:\n        change = run._guest_creation_change()\n",
                "    if created.status == 403:\n        change = run._guest_creation_change()\n",
            )
        ],
        [TI2 + "G2SetupTest.test_any_refusal_is_tried_again_with_guest_creation_enabled"],
    ),
    (
        "I2a review nit: the run plan counts what the session already used",
        [
            (
                "checks/run_plan.py",
                '        key: used[key] + complete[key] + reserve[key] <= caps[key] for key in ("users", "channels")\n',
                '        key: complete[key] + reserve[key] <= caps[key] for key in ("users", "channels")\n',
            )
        ],
        ["tests.test_run_plan.RunPlanTest.test_what_the_session_already_used_is_counted"],
    ),
    (
        "I2a review nit: a case runs only while the setup tokens are far from expiry",
        [
            (
                P,
                "            short = self._setup_tokens_expiring() if case.phase < FAMILY_PHASE else None\n",
                "            short = None\n",
            )
        ],
        [
            TMX
            + "TokenLifetimeTest.test_a_case_is_not_run_while_the_setup_tokens_are_close_to_expiry"
        ],
    ),
    (
        "I2a review nit: the reconnect check is not made near the tokens' expiry",
        [
            (
                P,
                "        short = self._setup_tokens_expiring()\n        if short:\n            # Not made: a refused reconnection could be the token's own expiry.\n",
                "        short = None\n        if short:\n            # Not made: a refused reconnection could be the token's own expiry.\n",
            )
        ],
        [
            TMX
            + "TokenLifetimeTest.test_a_case_is_not_run_while_the_setup_tokens_are_close_to_expiry"
        ],
    ),
    (
        "I2a review nit: a family runs only while the shared tokens are far from expiry",
        [
            (
                MX,
                "            if short:\n                return self.observe(\n",
                "            if False:\n                return self.observe(\n",
            )
        ],
        [
            TMX
            + "TokenLifetimeTest.test_a_family_is_not_run_while_the_shared_tokens_are_close_to_expiry"
        ],
    ),
    (
        "I2a review nit: no refusal near the member's own expiry is an ended dimension",
        [
            (
                MX,
                "            if left is not None and left < TOKEN_EXPIRY_MARGIN_SECONDS:\n",
                "            if False:\n",
            )
        ],
        [
            TMX
            + "TokenLifetimeTest.test_a_refusal_near_the_members_own_expiry_is_not_an_ended_dimension"
        ],
    ),
    # P06.1-I2a, before run 1: the poll listing's first live use got 400 code 4.
    (
        "I2a live: a listing not verified keeps Stream's message",
        [
            (
                P,
                '                f": {result.message}" if result.message else ""\n',
                '                ""\n',
            )
        ],
        ["tests.test_cleanup.ClientCreatedDataTest.test_verify_clean_lists_polls_and_user_groups"],
    ),
    # P06.1-I2a, run 1: C1's reply matching ended the session at the first live channel
    # command, whose channel ID had replaced the command's own ID.
    (
        "I2a live: a channel's ID never replaces the command's own ID",
        [
            (
                B,
                '        command = {**fields, "id": self._next_id, "op": op, "max_calls": max_calls}\n',
                '        command = {"id": self._next_id, "op": op, "max_calls": max_calls, **params}\n',
            )
        ],
        [
            "tests.test_runner.ChannelCommandSessionTest.test_a_channel_command_keeps_its_own_id_end_to_end"
        ],
    ),
    (
        "I2a live: the runner opens the channel named by channel_id",
        [
            (
                RN,
                "          : client.channel(cmd.type, cmd.channel_id);\n",
                "          : client.channel(cmd.type, cmd.id);\n",
            )
        ],
        [
            "tests.test_runner.RunnerTest.test_a_channel_command_names_its_channel_as_channel_id",
            "tests.test_runner.ChannelCommandSessionTest.test_a_channel_command_keeps_its_own_id_end_to_end",
        ],
    ),
    # The independent review's point 7 (P06.1-I2a): interruptions.
    (
        "I2a review 7: a family goes on when a member's session has ended",
        [
            (
                MX,
                '            if session is None or ended:\n                out[label] = {"collected": False, "why": str(ended or "no session")}\n',
                '            if session is None:\n                out[label] = {"collected": False, "why": str(ended or "no session")}\n',
            ),
            (
                MX,
                '            except ClientSessionEnded as exc:\n                out[label] = {"collected": False, "why": self.run._text(exc)}\n',
                '            except ArithmeticError as exc:\n                out[label] = {"collected": False, "why": self.run._text(exc)}\n',
            ),
        ],
        [TMX + "StopsTest.test_an_ended_client_session_ends_only_its_case"],
    ),
    (
        "I2a review 7: a session that ends at the S15 write leaves that dimension not shown",
        [
            (
                MX,
                '                except ClientSessionEnded as exc:\n                    self.after[label]["s15_error"] = run._text(exc)\n',
                '                except ArithmeticError as exc:\n                    self.after[label]["s15_error"] = run._text(exc)\n',
            )
        ],
        [TMX + "StopsTest.test_an_ended_client_session_ends_only_its_case"],
    ),
    (
        "I2a review 7: an interrupted family keeps DOES NOT MEET",
        [
            (
                P,
                "        if row.verdict not in matrix.KEPT_WHEN_INTERRUPTED:\n",
                "        if row.verdict != matrix.FAIL:\n",
            )
        ],
        [TMX + "StopsTest.test_an_interrupted_family_keeps_what_does_not_meet_the_policy"],
    ),
    (
        "I2a review 7: a family's row is kept after each step",
        [
            # Since P06.1-I2b every part of the step keeps the row (finding 1), so all
            # four blocks are reverted to show that none does.
            (
                MX,
                '        with self.stepping("REST reads and S15 writes made after the mechanism"):\n',
                "        if True:\n",
            ),
            (
                MX,
                '        with self.stepping("token reuse made after the mechanism"):\n',
                "        if True:\n",
            ),
            (
                MX,
                '        with self.stepping("tokens issued after the mechanism tried"):\n',
                "        if True:\n",
            ),
            (
                MX,
                '        with self.stepping("the probe after the mechanism collected"):\n',
                "        if True:\n",
            ),
        ],
        [
            TMX + "StopsTest.test_an_interrupted_family_keeps_what_does_not_meet_the_policy",
            TMX + "StopsTest.test_a_rate_limit_in_a_probe_keeps_what_was_observed",
        ],
    ),
    (
        "I2a review 7: an interrupted S15 mapping keeps the field in progress",
        [
            (
                I2,
                "            observe()  # with the field's restore, however the field ended\n",
                "            pass\n",
            )
        ],
        [TI2 + "S15MapTest.test_a_field_the_control_set_is_restored_when_bs_session_ends"],
    ),
    (
        "I2a review 7: an interrupted pin or archive keeps the restore's note",
        [
            (
                I2,
                "        observe()  # with the restore's note, however the case ended\n",
                "        pass\n",
            )
        ],
        [TI2 + "OwnMemberFlagTest.test_a_leak_stays_a_fail_when_the_control_is_interrupted"],
    ),
    (
        "I2a review 5: HOLDS (filtered) needs B's read to return A's member record",
        [
            (
                I2,
                '        elif b_answer.outcome == "success" and b_entries:\n',
                "        elif True:\n",
            )
        ],
        [
            TI2 + "OwnMemberFlagTest.test_a_b_read_without_as_member_record_is_inconclusive",
            TI2 + "OwnMemberFlagTest.test_a_refused_b_read_is_inconclusive",
        ],
    ),
    (
        "I2a review 5: HOLDS needs a readable stored record",
        [(I2, "        if stored is None:\n", "        if False:\n")],
        [TI2 + "OwnMemberFlagTest.test_a_stored_record_that_cannot_be_read_is_inconclusive"],
    ),
    (
        "I2a step 2 S10: the poll message is sent again until polls reach the channel",
        [
            (
                P,
                '            not_yet = msg.status == 403 and "polls not enabled" in (msg.message or "").lower()\n',
                "            not_yet = False\n",
            )
        ],
        [TI2 + "S10SetupTest.test_the_poll_message_is_retried_until_polls_reach_the_channel"],
    ),
    (
        "I2a step 2 G2: the guest is created server-side",
        [(P, "            _session, self.g2_setup = i2a.g2_session(self)\n", "            pass\n")],
        [
            "tests.test_run_simulation.SimulationTest.test_guest_reach_runs_on_a_guest_created_server_side"
        ],
    ),
    # P06.1-I2b: the I2a review's items, the two rules, the poll listing and the API key.
    (
        "I2b finding 1: a stop inside a step keeps the other members' observations",
        [
            (
                MX,
                '        with self.stepping("REST reads and S15 writes made after the mechanism"):\n',
                "        if True:\n",
            )
        ],
        [TMX + "KeptStepsTest.test_a_stop_inside_a_step_keeps_the_other_members_observation"],
    ),
    (
        "I2b finding 1: the row says applied once the mechanism's request is answered",
        [
            (
                MX,
                "        self.observe(\n"
                '            matrix.Verdict(matrix.INCONCLUSIVE, "applied; nothing observed after it yet"),\n'
                "            f\"applied: {self.detail['apply']['answer']}\",\n"
                "        )\n",
                "        pass\n",
            ),
            (
                MX,
                '        with self.stepping("applied; the events and the channel after it read"):\n',
                "        if True:\n",
            ),
        ],
        [TMX + "KeptStepsTest.test_a_stop_after_the_mechanisms_request_keeps_the_row_as_applied"],
    ),
    (
        "I2b finding 1: the retention read keeps the row",
        [
            (
                MX,
                '            with self.stepping("retention read; the undo not yet made"):\n',
                "            if True:\n",
            )
        ],
        [TMX + "KeptStepsTest.test_a_stop_in_the_retention_read_keeps_what_the_channel_showed"],
    ),
    (
        "I2b finding 2: two successes are compared by shape, not by size",
        [
            (
                I2,
                "        text = json.dumps(shape(response), sort_keys=True)\n",
                '        text = f"keys {sorted(response)}; size {len(json.dumps(response))}"\n',
            )
        ],
        [TI2 + "OracleTest.test_two_successes_are_compared_by_shape_never_by_size"],
    ),
    (
        "I2b finding 2: duration is left out of the shape",
        [
            (
                I2,
                '_VARYING_KEYS = frozenset({"duration"})\n',
                "_VARYING_KEYS: frozenset[str] = frozenset()\n",
            )
        ],
        [TI2 + "OracleTest.test_two_successes_are_compared_by_shape_never_by_size"],
    ),
    (
        "I2b: each oracle pair keeps both normalized answers",
        [
            (I2, '                "existing_normalized": normalized(found, ids),\n', ""),
            (I2, '                "missing_normalized": normalized(absent, ids),\n', ""),
        ],
        [TI2 + "OracleTest.test_a_refusals_normalized_messages_are_kept"],
    ),
    (
        "I2b: the existence oracle has a sync pair",
        [
            (
                I2,
                "        pairs.append(\n"
                "            (\n"
                '                "sync",\n'
                "                pr._http_answer(\n"
                '                    _call(run, "A", "client", "sync", [[f"{T}:{existing}"], run.ctx["run_start"]])\n'
                "                ),\n"
                "                pr._http_answer(\n"
                '                    _call(run, "A", "client", "sync", [[f"{T}:{missing}"], run.ctx["run_start"]])\n'
                "                ),\n"
                "            )\n"
                "        )\n"
                "        observe()\n",
                "        pass\n",
            )
        ],
        [TI2 + "OracleTest.test_the_channel_oracle_has_a_sync_pair"],
    ),
    (
        "I2b nit 3: the oracle needs a successful control",
        [(I2, '    elif control.outcome != "success":\n', "    elif False:\n")],
        [TI2 + "OracleTest.test_the_oracle_needs_a_successful_control"],
    ),
    (
        "I2b nit 3: a 5xx is not a determinate answer",
        [
            (
                I2,
                'DETERMINATE = ("success", "auth", "permission", "not-found", "input", "feature")\n',
                'DETERMINATE = ("success", "auth", "permission", "not-found", "input", "feature", "other")\n',
            )
        ],
        [TI2 + "OracleTest.test_two_different_5xx_answers_are_not_an_oracle"],
    ),
    (
        "I2b nit 3: a write with no answer or a 5xx counts as written",
        [
            (
                I2,
                '        entry["written"] = answer.outcome not in (*REFUSALS, "feature", "input", "not-found")\n',
                '        entry["written"] = answer.outcome == "success"\n',
            )
        ],
        [TI2 + "S15MapTest.test_a_write_answered_5xx_is_still_put_back"],
    ),
    (
        "I2b nit 3: OUT-send HOLDS with exactly one transport attempt",
        [
            (
                I2,
                "        and len(unreachable.attempts) == 1\n",
                "        and len(unreachable.attempts) >= 1\n",
            )
        ],
        [TI2 + "OutageTest.test_several_transport_attempts_are_inconclusive"],
    ),
    (
        "I2b nit 3: the type of a recorded setting is compared",
        [
            (
                CF,
                "            elif have != want or type(have) is not type(want):\n",
                "            elif have != want:\n",
            )
        ],
        [TRS + "test_a_value_of_another_type_is_a_difference"],
    ),
    (
        "I2b nit 3: the token margin applies to every dimension",
        [
            (
                MX,
                "                for dim in DIMENSIONS:\n",
                '                for dim in ("rest",):\n',
            )
        ],
        [TMX + "TokenLifetimeTest.test_the_margin_applies_to_every_dimension"],
    ),
    (
        "I2b nit 3: the subscription needs a listener that received the probe",
        [
            (
                MX,
                "        return any(bool(g) for g in got) if got else None\n",
                "        return True\n",
            )
        ],
        [
            TMX
            + "ListenerAndRetentionTest.test_a_probe_that_reaches_no_session_leaves_the_subscription_not_shown"
        ],
    ),
    (
        "I2b nit 3: retention needs the channel's first message",
        [
            (
                MX,
                "            self.retained = self.history_id in ids\n",
                "            self.retained = True\n",
            )
        ],
        [
            TMX
            + "ListenerAndRetentionTest.test_a_channel_whose_first_message_is_gone_does_not_meet_the_policy"
        ],
    ),
    (
        "I2b nit 4: the guard checks the message for every mutating request",
        [
            (
                G,
                "        if len(parts) >= 2 and parts[1] not in _KEYWORDS and not scope.owns_message(parts[1]):\n",
                '        if verb == "DELETE" and len(parts) == 2 and not scope.owns_message(parts[1]):\n',
            )
        ],
        [
            TGU + "RefusalTest.test_a_message_poll_or_group_must_be_the_runs",
            TGU + "ServerHookTest.test_the_message_rule_in_the_real_hook",
        ],
    ),
    (
        "I2b nit 4: the poll message is the run's own message",
        [(P, "                self.messages.add(message_id)\n", "                pass\n")],
        [
            TA
            + "ProductionPhaseAnswerTest.test_polls_on_fail_survives_a_production_vote_without_an_answer",
            TI
            + "ProceduresKeepWhatTheyObservedTest.test_s10_vote_success_survives_an_error_in_the_server_replay",
        ],
    ),
    (
        "I2b, the disclosure rule: a term the request carried is left out",
        [
            (
                P,
                "        scanned = [t for t in terms if t not in carried]\n",
                "        scanned = list(terms)\n",
            )
        ],
        [TA + "DisclosureRuleTest.test_a_term_the_request_carried_is_not_a_disclosure"],
    ),
    (
        "I2b, the disclosure rule: a carried term matches anywhere in the serialized request",
        [
            (
                MT,
                '    sent = "\\n".join(serialized_request(r) for r in records)\n',
                '    sent = "\\n".join(str(r.get("path")) for r in records)\n',
            )
        ],
        [
            TA + "DisclosureRuleTest.test_a_term_the_request_carried_is_not_a_disclosure",
            TA + "DisclosureRuleTest.test_the_helpers",
        ],
    ),
    (
        "I2b, the disclosure rule: where a term was found is kept",
        [
            (
                P,
                "            for term, paths in matrix.term_paths(answer, leaks).items():\n",
                "            for term, paths in {}.items():\n",
            )
        ],
        [
            TA
            + "DisclosureRuleTest.test_a_term_the_request_did_not_carry_is_a_disclosure_and_its_place_is_kept"
        ],
    ),
    (
        "I2b, 404 code 16: the other member's identical request must still succeed",
        [
            (
                MX,
                "    if not other_ok:\n        return None\n",
                "    if False:\n        return None\n",
            )
        ],
        [
            TMX + "Missing404Test.test_the_rule",
            TMX + "Missing404Test.test_a_404_without_the_other_members_success_stays_not_shown",
        ],
    ),
    (
        "I2b, 404 code 16: only where the mechanism removes what the request needs",
        [
            (
                MX,
                "    if missing is None:\n        return None\n",
                "    if False:\n        return None\n",
            )
        ],
        [
            TMX + "Missing404Test.test_the_rule",
            TMX + "Missing404Test.test_a_404_after_another_mechanism_stays_not_shown",
        ],
    ),
    (
        "I2b, 404 code 16: Stream's message must name the missing membership or user",
        [
            (
                MX,
                "    if not names_missing(message, missing, uid):\n        return None\n",
                "    if False:\n        return None\n",
            )
        ],
        [
            TMX + "Missing404Test.test_the_rule",
            TMX + "Missing404Test.test_a_404_whose_message_names_nothing_stays_not_shown",
        ],
    ),
    (
        "I2b, 404 code 16: the removal and the deactivation are the mechanisms it applies to",
        [
            (
                MX,
                'REMOVES: dict[str, str] = {"remove": "membership", "deactivate": "user"}\n',
                "REMOVES: dict[str, str] = {}\n",
            )
        ],
        [
            TMX + "Missing404Test.test_a_removed_members_own_write_404_ends_the_dimension",
            TMX + "Missing404Test.test_a_deactivated_users_404s_end_its_dimensions",
        ],
    ),
    (
        "I2b, 404 code 16: Stream's message is kept in the row",
        [
            (
                MX,
                '                "messages": self.refusal_messages(label),\n',
                '                "messages": {},\n',
            )
        ],
        [TMX + "Missing404Test.test_a_removed_members_own_write_404_ends_the_dimension"],
    ),
    (
        "I2b: a WebSocket refusal keeps Stream's message",
        [
            (
                P,
                '        note = message if isinstance(message, str) else ""\n',
                '        note = ""\n',
            )
        ],
        [TMX + "Missing404Test.test_a_deactivated_users_404s_end_its_dimensions"],
    ),
    (
        "I2b: the API key is removed from free text",
        [
            (
                RD,
                "        if self._api_key:\n            value = value.replace(self._api_key, REDACTED_API_KEY)\n",
                "        if False:\n            value = value.replace(self._api_key, REDACTED_API_KEY)\n",
            )
        ],
        [
            "tests.test_redaction.RedactionTest.test_the_api_key_is_removed_from_free_text_when_given",
            TCE
            + "ContextRedactionTest.test_the_commands_redactor_removes_the_api_key_from_free_text",
        ],
    ),
    (
        "I2b: the commands' redactor is given the API key",
        [
            (
                C,
                "        self.redactor = Redactor(self.secrets, api_key=self.credentials.api_key)\n",
                "        self.redactor = Redactor(self.secrets)\n",
            )
        ],
        [
            TCE
            + "ContextRedactionTest.test_the_commands_redactor_removes_the_api_key_from_free_text"
        ],
    ),
    (
        "I2b, the poll listing: polls are listed as each of the run's users",
        [(P, '            ("polls verified", lambda: self._verify_polls(out)),\n', "")],
        [TCL + "PollListingTest.test_polls_are_listed_as_each_run_user_and_read_by_id"],
    ),
    (
        "I2b, the poll listing: a recorded poll must be gone after its delete",
        [(P, '        if not str(status).startswith("404"):\n', "        if False:\n")],
        [TCL + "PollListingTest.test_a_poll_that_survives_its_delete_is_a_problem"],
    ),
    (
        "I2b, the poll listing: no listing as a deactivated user",
        [
            (
                P,
                "        users = sorted(set(self.users) - self.deactivated_users)\n",
                "        users = sorted(set(self.users))\n",
            )
        ],
        [TCL + "PollListingTest.test_no_listing_is_made_as_a_deactivated_user"],
    ),
    (
        "I2b, the poll listing: the listing as the run's users stands in for the standalone one",
        [
            (
                P,
                '        if listed.get("remaining_polls") is None and self.polls_as_users is not None:\n',
                "        if False:\n",
            )
        ],
        [TCL + "PollListingTest.test_polls_are_listed_as_each_run_user_and_read_by_id"],
    ),
]


def anchored(text: str, old: str) -> list[int]:
    """Where ``old`` occurs starting at the beginning of a line (P06.1-C3)."""
    found: list[int] = []
    start = 0
    while (i := text.find(old, start)) != -1:
        if i == 0 or text[i - 1] == "\n":
            found.append(i)
        start = i + 1
    return found


def loads(root: Path, path: str) -> str | None:
    """Why an edited file does not load, or ``None`` when it does (P06.1-C3).

    A ``.py`` file must compile and import; a ``.cjs`` file must pass ``node --check``.
    """
    if path.endswith(".py"):
        module = path.removesuffix(".py").replace("/", ".")
        code = (
            "import importlib, pathlib\n"
            f"compile(pathlib.Path({path!r}).read_text(), {path!r}, 'exec')\n"
            f"importlib.import_module({module!r})\n"
        )
        command = [PY, "-c", code]
    elif path.endswith(".cjs"):
        command = ["node", "--check", path]
    else:
        return None
    done = subprocess.run(command, cwd=root, env=ENV, capture_output=True, text=True, timeout=120)
    if done.returncode == 0:
        return None
    lines = [ln.strip() for ln in (done.stderr or done.stdout).splitlines() if ln.strip()]
    errors = [ln for ln in lines if re.match(r"[\w.]*(Error|Exception)\b", ln)]
    return (errors or lines or [f"exit code {done.returncode}"])[-1]


def failure_reasons(stderr: str) -> list[str]:
    """Each failing test and the exception its failure ended in (P06.1-C3), and why the
    test process stopped if it stopped before reporting (for example Ctrl-C).

    JWT-shaped text in a reason (the tests' synthetic tokens) is masked."""
    reasons: list[str] = []
    for block in re.split(r"^=+\n", stderr, flags=re.M):
        lines = block.splitlines()
        if not lines or not lines[0].startswith(("FAIL: ", "ERROR: ")):
            continue
        starts = [i for i, ln in enumerate(lines) if ln.startswith("Traceback")]
        after = lines[starts[-1] + 1 :] if starts else lines[1:]
        exception = next((ln for ln in after if ln.strip() and not ln.startswith((" ", "-"))), "?")
        reasons.append(f"{lines[0].split(' (', 1)[0]}: {exception}")
    if not re.search(r"^Ran \d+ tests? in ", stderr, flags=re.M):
        last = [ln.strip() for ln in stderr.splitlines() if ln.strip()]
        reasons.append("the test process stopped before reporting: " + (last[-1] if last else "?"))
    return [JWT_SHAPE.sub("<jwt>", r) for r in reasons]


def run_tests(root: Path, tests: list[str]) -> tuple[int, str, list[str]]:
    done = subprocess.run(
        [PY, "-m", "unittest", *tests],
        cwd=root,
        env=ENV,
        capture_output=True,
        text=True,
        timeout=300,
    )
    tail = [ln for ln in done.stderr.splitlines() if ln.startswith(("Ran ", "OK", "FAILED"))]
    return done.returncode, " ".join(tail), failure_reasons(done.stderr)


def main() -> int:
    work = Path(tempfile.mkdtemp(dir=sys.argv[1] if len(sys.argv) > 1 else None))
    root = work / "stream-chat"
    shutil.copytree(
        SRC, root, ignore=shutil.ignore_patterns(".venv", "node_modules", ".work", "__pycache__")
    )
    (root / "node_modules").symlink_to(SRC / "node_modules")
    bad = 0
    for name, edits, tests in R:
        originals: dict[str, str] = {}
        problem: str | None = None
        for path, old, new in edits:
            f = root / path
            current = f.read_text()
            originals.setdefault(path, current)
            where = anchored(current, old)
            if len(where) != 1:
                problem = f"pattern found {len(where)} times at a line start in {path}"
                break
            f.write_text(current[: where[0]] + new + current[where[0] + len(old) :])
        if problem is None:
            broken = [f"{p}: {why}" for p in originals if (why := loads(root, p)) is not None]
            if broken:
                problem = "the reverted file does not load: " + "; ".join(broken)
        if problem is None:
            code, tail, reasons = run_tests(root, tests)
        for path, text in originals.items():
            (root / path).write_text(text)
        if problem is not None:
            bad += 1
            print(f"BAD | {name} | not demonstrated: {problem}")
            continue
        with_fix, tail_ok, _ = run_tests(root, tests)
        ok = code != 0 and with_fix == 0
        bad += 0 if ok else 1
        print(f"{'OK ' if ok else 'BAD'} | {name} | reverted: {tail} | restored: {tail_ok}")
        for reason in reasons:
            print(f"      - {reason}")
    shutil.rmtree(work)
    print(f"reversals: {len(R)}, not demonstrated: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
