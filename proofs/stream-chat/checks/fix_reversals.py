# The reversal table quotes source lines exactly, so some exceed the line length.
# ruff: noqa: E501
"""P06.1-C1: show that each fix is tested.

For each fix, a scratch copy of this directory (outside it, in a temporary
directory) gets that one fix reverted, and the fix's tests are run: they must
fail. The fix is then put back and the same tests must pass. Nothing in this
directory is changed. Run it with the harness's own Python after installing:

    .venv/bin/python checks/fix_reversals.py

It prints one line per reversal and exits non-zero if any reversal is not
demonstrated. A reversal whose tests abort the test process (for example an
escaping KeyboardInterrupt) counts as failing.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
PY = str(SRC / ".venv" / "bin" / "python")
P = "glow_stream_proof/proof_run.py"
C = "glow_stream_proof/cli.py"
B = "glow_stream_proof/client_bridge.py"

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
                "        answer = _answer_of(post, reply)\n",
                "        answer = Answer(matrix.classify(reply.status, reply.code), reply.status, reply.code, post)\n",
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
                '        connected = _ws_answer(self.connect_replies["anonymous"])\n        if connected.outcome != "success":\n',
                '        connected = _ws_answer(self.connect_replies["anonymous"])\n        if False:\n',
            )
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
                "            except RunStopped as exc:\n                # Record the case, then stop",
                "            except ZeroDivisionError as exc:\n                # Record the case, then stop",
            )
        ],
        ["tests.test_temporary_changes.TypeFeatureRestoreTest.test_failed_restore_stops_the_run"],
    ),
    (
        "F2 try before enabling (type/channel)",
        [
            (
                P,
                "        with self._temporary(change):\n            if case.feature_override:\n"
                '                on = self.api.raw("PATCH", path, body={"set": {"config_overrides": override}})\n'
                "            else:\n                on = self._type_features_on(override)\n"
                "            result = self._evaluate_case(case)\n",
                "        if case.feature_override:\n"
                '            on = self.api.raw("PATCH", path, body={"set": {"config_overrides": override}})\n'
                "        else:\n            on = self._type_features_on(override)\n"
                "        with self._temporary(change):\n            result = self._evaluate_case(case)\n",
            )
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
                "            with self._temporary(change):\n                on = self._set_guest_creation_disabled(False)\n"
                "                time.sleep(TYPE_CHANGE_SETTLE_SECONDS)\n"
                '                guest = self._session("guest", None, max_api_calls=30)\n'
                '                creply = self._send(guest, "guest", max_calls=3, user=user)\n',
                "            on = self._set_guest_creation_disabled(False)\n"
                "            time.sleep(TYPE_CHANGE_SETTLE_SECONDS)\n"
                '            guest = self._session("guest", None, max_api_calls=30)\n'
                "            with self._temporary(change):\n"
                '                creply = self._send(guest, "guest", max_calls=3, user=user)\n',
            )
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
            (
                C,
                "        problems = run.finish(cleanup=cleanup_needed)\n",
                "        problems: list[str] = []\n        run.cleanup() if cleanup_needed else run.close_sessions()\n",
            )
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
                '("{xd_text}", "{m_x}", "{X}", "{XD}")',
                '("{xd_text}",)',
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
                '        problems, unreadable = override_removal_problems(\n            self._server_channel(self.ctx["AB_cid"]), override\n        )\n',
                "        problems: list[str] = []\n        unreadable: list[str] = []\n",
            )
        ],
        [
            "tests.test_temporary_changes.ChannelOverrideRemovalTest.test_removal_that_did_not_apply_stops_the_run",
            "tests.test_temporary_changes.ChannelOverrideRemovalTest.test_removal_is_re_read",
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
                'event_hooks={"request": [self._before_request], "response": [self._after_response]},',
                'event_hooks={"request": [self._before_request]},',
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
        [(P, "            **list_polls_and_groups(self.api),\n", "")],
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
]


def run_tests(root: Path, tests: list[str]) -> tuple[int, str]:
    env = {"PATH": os.environ["PATH"], "HOME": os.environ["HOME"], "LANG": "C.UTF-8"}
    done = subprocess.run(
        [PY, "-m", "unittest", *tests],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    tail = [ln for ln in done.stderr.splitlines() if ln.startswith(("Ran ", "OK", "FAILED"))]
    return done.returncode, " ".join(tail)


def main() -> int:
    work = Path(tempfile.mkdtemp(dir=sys.argv[1] if len(sys.argv) > 1 else None))
    root = work / "stream-chat"
    shutil.copytree(
        SRC, root, ignore=shutil.ignore_patterns(".venv", "node_modules", ".work", "__pycache__")
    )
    (root / "node_modules").symlink_to(SRC / "node_modules")
    bad = 0
    for name, edits, tests in R:
        originals = {}
        for path, old, new in edits:
            f = root / path
            text = originals.setdefault(path, f.read_text())
            current = f.read_text()
            if current.count(old) != 1:
                print(f"SETUP ERROR {name}: pattern found {current.count(old)} times in {path}")
                bad += 1
                break
            f.write_text(current.replace(old, new))
        else:
            with_fix = None
            code, tail = run_tests(root, tests)
            for path, text in originals.items():
                (root / path).write_text(text)
            with_fix, tail_ok = run_tests(root, tests)
            ok = code != 0 and with_fix == 0
            bad += 0 if ok else 1
            print(f"{'OK ' if ok else 'BAD'} | {name} | reverted: {tail} | restored: {tail_ok}")
            continue
        for path, text in originals.items():
            (root / path).write_text(text)
    shutil.rmtree(work)
    print(f"reversals: {len(R)}, not demonstrated: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
