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
RT3_CONTROL_HOLDS = (
    "            elif (\n"
    '                control.outcome == "success" and _request_line(control.record, self.ctx) == request\n'
    "            ):\n"
)
SERVER_IMPORT = "from .usage import UsageLedger, charge_signal, is_rate_limit\n"
SERVER_IMPORT_C2 = "from .usage import GuardrailStop, UsageLedger, charge_signal, is_rate_limit\n"


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
            "tests.test_run_simulation.SimulationTest.test_guest_reach_is_not_run_when_the_guest_connect_is_refused"
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
                '        finally:\n            row.detail["client_success_undo"] = self.redactor.text(", ".join(notes))\n',
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
                "                        rate_limited=is_rate_limit(status, stream_code),\n",
                "                        rate_limited=False,\n",
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
                "            raise self._ledger.stop_at_once(\n"
                '                f"server {method} {path}: {signal}; stopping at once",\n'
                "                rate_limited=is_rate_limit(response.status_code, code),\n",
                "            raise GuardrailStop(\n"
                '                f"server {method} {path}: {signal}; stopping at once",\n'
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
                "            raise self._ledger.stop_at_once(\n"
                '                f"server {method} {path}: {signal}; stopping at once",\n'
                "                rate_limited=is_rate_limit(result.status, result.code),\n",
                "            raise GuardrailStop(\n"
                '                f"server {method} {path}: {signal}; stopping at once",\n'
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
                "                    raise self._ledger.stop_at_once(\n"
                '                        f"client {self.label}: {signal}; stopping at once",\n'
                "                        rate_limited=is_rate_limit(status, stream_code),\n",
                "                    raise GuardrailStop(\n"
                '                        f"client {self.label}: {signal}; stopping at once",\n'
                "                        rate_limited=is_rate_limit(status, stream_code),\n",
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
                "                raise self._ledger.stop_at_once(\n"
                '                    f"client {self.label}: {signal}; stopping at once",\n'
                "                    rate_limited=is_rate_limit(reply.status, reply.code),\n",
                "                raise GuardrailStop(\n"
                '                    f"client {self.label}: {signal}; stopping at once",\n'
                "                    rate_limited=is_rate_limit(reply.status, reply.code),\n",
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
                "                    rate_limited=is_rate_limit(reply.status, reply.code),\n",
                "                    rate_limited=False,\n",
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
                "            # run's is deleted (P06.1-C3; until then only the run's own stop counted).\n            self.close_sessions()\n",
                "            # run's is deleted (P06.1-C3; until then only the run's own stop counted).\n",
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
                "        if production_succeeded:\n            self._undo_client_success(case, result)\n",
                '        if production.outcome == "success":\n            self._undo_client_success(case, result)\n',
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
