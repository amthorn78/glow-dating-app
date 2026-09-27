"""P06.1-I2b: the Video and Feeds cases, against the fake products (tests/fake_products.py).

Before the lockdown a capability is a FAIL; after it every case HOLDS with the server's
control; a product that is not available is that product's finding, not a charge; every
object a case creates is the run's own, recorded, and deleted at cleanup; a Video and
Feeds run gets the lean setup. The fake's grants are a model, not Stream's behaviour.
"""

import unittest
from collections import Counter
from typing import Any

import tests  # noqa: F401
from glow_stream_proof import matrix, proof_run
from glow_stream_proof.client_bridge import Reply
from glow_stream_proof.proof_run import ProofRun, RunStopped, cleanup_problems
from glow_stream_proof.usage import GuardrailStop, UsageLedger
from tests.fake_products import ProductBehaviour
from tests.fakes import PREFIX, FakeServer, FakeSession, NoSettle, make_run
from tests.test_preflight import dashboard_user

PRODUCT_CASES = set(matrix.product_case_ids())
VIDEO_CASES = set(matrix.product_case_ids("video"))
FEEDS_CASES = set(matrix.product_case_ids("feeds"))


def product_run(
    knobs: dict[str, Any] | None = None,
    *,
    only: set[str] | None = None,
    lean: bool = True,
    behaviour: Any = None,
) -> tuple[ProofRun, FakeServer]:
    server = FakeServer(UsageLedger())
    for key, value in (knobs or {}).items():
        setattr(server.products, key, value)
    run, server = make_run(
        server=server, default_behaviour=behaviour or ProductBehaviour(server.products)
    )
    run.lean = lean
    with NoSettle():
        run.setup()
        run.authorized_path()
        run.run_matrix(only if only is not None else PRODUCT_CASES)
    return run, server


def verdicts(run: ProofRun) -> dict[str, str]:
    return {c.case_id: c.verdict for c in run.case_results}


def row(run: ProofRun, case_id: str) -> proof_run.CaseResult:
    return next(c for c in run.case_results if c.case_id == case_id)


class BeforeTheLockdownTest(unittest.TestCase):
    """Every capability the fake grants the user role shows as a FAIL: the client's
    request succeeded, or the other member read what it should not."""

    proof: ProofRun
    server: FakeServer

    @classmethod
    def setUpClass(cls) -> None:
        cls.proof, cls.server = product_run()

    def test_every_capability_is_recorded(self) -> None:
        got = verdicts(self.proof)
        expected = dict.fromkeys(PRODUCT_CASES, matrix.FAIL)
        # The fake lets only a feed's owner post into it, so A's post into B's feed is
        # refused; the server's replay of the same request is its control.
        expected["FD-other-feed"] = matrix.HOLDS
        self.assertEqual(got, expected)
        self.assertEqual(row(self.proof, "VD-create").reason, "the client action succeeded")
        self.assertIn(self.proof.ctx["vd_text"], row(self.proof, "VD-read-other").reason)
        self.assertIn(self.proof.ctx["CALL_x"], row(self.proof, "VD-query").reason)
        self.assertIn(self.proof.ctx["fd_text"], row(self.proof, "FD-read").reason)

    def test_the_request_under_test_is_the_clients_own(self) -> None:
        self.assertEqual(
            row(self.proof, "VD-create").request, "POST /api/v2/video/call/default/{CALL_a}"
        )
        self.assertEqual(row(self.proof, "FD-follow").request, "POST /api/v2/feeds/follows")
        self.assertEqual(
            row(self.proof, "FD-reaction").request, "POST /api/v2/feeds/activities/{ACT}/reactions"
        )
        # The client's requests were made as the session's own user.
        clients = {actor for _m, _p, actor in self.server.products.seen if actor is not None}
        self.assertEqual(clients, {self.proof.ctx["A"], self.proof.ctx["B"]})

    def test_client_successes_are_undone_once_where_an_undo_is_defined(self) -> None:
        # The control's replay succeeded on the same object and made the undo; a second
        # delete would get 404.
        once = "made once, by the control's replay's undo"
        for case_id in (
            "VD-create",
            "VD-create-dev",
            "VD-members",
            "FD-feed",
            "FD-follow",
            "FD-reaction",
        ):
            self.assertEqual(row(self.proof, case_id).detail["client_success_undo"], once, case_id)
            self.assertIn("undo", row(self.proof, case_id).control)
        # An object with a server-assigned ID is recorded for cleanup instead.
        self.assertEqual(
            row(self.proof, "FD-activity").detail["client_success_undo"], "none defined"
        )
        self.assertEqual(
            row(self.proof, "FD-comment").detail["client_success_undo"], "none defined"
        )

    def test_every_object_is_recorded_and_the_cleanup_removes_it(self) -> None:
        run, server = product_run()
        self.assertTrue(run.calls and run.feeds and run.activities and run.comments)
        with NoSettle():
            problems = run.finish(cleanup=True)
        self.assertEqual(problems, [])
        state = server.products
        self.assertEqual(
            (
                state.calls,
                state.feeds,
                state.activities,
                state.comments,
                state.reactions,
                state.follows,
            ),
            ({}, {}, {}, {}, set(), set()),
        )
        kinds = {d["kind"] for d in run.cleanup_result["product_deletes"]}
        self.assertEqual(
            kinds, {"call", "feed", "activity", "comment", "reaction", "follow", "feeds user data"}
        )
        # Each object is recorded from the answer that created it, whoever sent the
        # request: the client's activity and comment, the replays' two activities (A's
        # feed, B's feed) and comment, and the fixture's activity.
        counted = Counter(d["kind"] for d in run.cleanup_result["product_deletes"])
        self.assertEqual((counted["activity"], counted["comment"]), (4, 2))
        for entry in run.cleanup_result["product_deletes"]:
            # 404: the case's undo had already removed it (a reaction, a follow).
            self.assertIn(entry["status"], (200, 404), entry)
        self.assertEqual(run.cleanup_result["remaining_calls"], [])
        self.assertEqual(run.cleanup_result["remaining_feeds"], [])
        self.assertEqual(run.cleanup_result["remaining_activities"], [])
        self.assertEqual(sorted(state.user_data_deleted), sorted(run.users))

    def test_fixtures_are_sent_once_and_what_they_create_is_the_runs(self) -> None:
        run, server = product_run(
            only={"VD-read", "VD-update", "VD-event", "FD-comment", "FD-reaction"}
        )
        call_creates = [
            (m, p)
            for m, p, actor in server.products.seen
            if actor is None and m == "POST" and p.endswith(run.ctx["CALL"])
        ]
        self.assertEqual(len(call_creates), 1)
        activity_creates = [
            (m, p)
            for m, p, actor in server.products.seen
            if actor is None and p == "/api/v2/feeds/activities"
        ]
        self.assertEqual(len(activity_creates), 1)
        self.assertIn(run.ctx["ACT"], run.activities)
        self.assertTrue(run.owns_activity(run.ctx["ACT"]))
        self.assertIn(("default", run.ctx["CALL"]), run.calls)


class AfterTheLockdownTest(unittest.TestCase):
    def test_every_case_of_the_user_role_holds_with_the_servers_control(self) -> None:
        """With the user role's grants gone, what remains is what a call's member and a
        feed's owner may do through the resource roles the lockdown does not touch: those
        cases stay FAIL, recorded plainly as capabilities configuration did not remove."""
        run, server = product_run({"allowed": set()})
        expected = dict.fromkeys(PRODUCT_CASES, matrix.HOLDS)
        for case_id in ("VD-read", "FD-activity", "FD-update", "FD-feed-custom"):
            expected[case_id] = matrix.FAIL
        self.assertEqual(verdicts(run), expected)
        for case in run.case_results:
            if case.verdict == matrix.HOLDS:
                self.assertIn("control succeeded", case.reason, case.case_id)
                self.assertIn("403 / code 17", case.observed, case.case_id)
        with NoSettle():
            problems = run.finish(cleanup=True)
        self.assertEqual(problems, [])
        state = server.products
        self.assertEqual((state.calls, state.feeds, state.activities), ({}, {}, {}))

    def test_a_read_that_returns_nothing_of_the_other_member_holds_filtered(self) -> None:
        # B may read, but sees only its own objects: no leak, and the control found the data.
        run, _server = product_run({"others_readable": False}, only={"VD-query", "FD-query"})
        self.assertEqual(
            verdicts(run), {"VD-query": matrix.HOLDS_FILTERED, "FD-query": matrix.HOLDS_FILTERED}
        )


class ProductNotAvailableTest(unittest.TestCase):
    def test_an_answer_that_the_product_is_not_enabled_is_its_finding_not_a_charge(self) -> None:
        run, server = product_run({"available": {"video": False, "feeds": True}})
        got = verdicts(run)
        self.assertEqual({got[c] for c in VIDEO_CASES}, {matrix.NOT_AVAILABLE})
        first = row(run, "VD-create")
        self.assertIn("Video is not enabled for this application. Upgrade your plan", first.reason)
        self.assertEqual(first.observed, "403 / code 17")
        self.assertEqual(first.request, "POST /api/v2/video/call/default/{CALL_a}")
        later = row(run, "VD-read")
        self.assertEqual(later.observed, "not run: video is not available to the application")
        # The "Upgrade" wording is not a charge signal: nothing stopped, feeds ran, and the
        # cleanup proceeds.
        self.assertEqual(run.stop_signals, [])
        self.assertEqual({got[c] for c in FEEDS_CASES} - {matrix.FAIL, matrix.HOLDS}, set())
        self.assertEqual(run.results()["unavailable_products"], {"video": first.reason})
        with NoSettle():
            problems = run.finish(cleanup=True)
        self.assertEqual(problems, [])

    def test_a_fixture_answered_not_available_ends_the_products_cases_too(self) -> None:
        run, _server = product_run(
            {"available": {"video": False, "feeds": True}}, only={"VD-read", "VD-update"}
        )
        first, second = row(run, "VD-read"), row(run, "VD-update")
        self.assertEqual(first.verdict, matrix.NOT_AVAILABLE)
        self.assertTrue(
            first.observed.startswith("fixture POST /api/v2/video/call/default/{CALL} got 403")
        )
        self.assertEqual(second.verdict, matrix.NOT_AVAILABLE)
        self.assertTrue(second.observed.startswith("not run"))

    def test_a_fixture_stream_refuses_otherwise_leaves_the_case_inconclusive(self) -> None:
        server = FakeServer(UsageLedger())
        del server.products.call_type_grants["default"]  # "call type does not exist"
        run, _ = make_run(server=server, default_behaviour=ProductBehaviour(server.products))
        run.lean = True
        with NoSettle():
            run.setup()
            run.run_matrix({"VD-read"})
        case = row(run, "VD-read")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertTrue(case.reason.startswith("fixture not in place: fixture POST"), case.reason)
        self.assertIn("404 / code 16", case.reason)
        self.assertEqual(run.results()["unavailable_products"], {})
        # No step was sent: nothing reached the client's session.
        self.assertEqual([actor for _m, _p, actor in server.products.seen if actor], [])

    def test_a_charge_signal_on_a_product_request_still_stops_the_run(self) -> None:
        """A 402 to a product request is a charge signal whatever its wording: the client
        session records it and raises its stop, as ClientSession does."""
        server = FakeServer(UsageLedger())

        def charged(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "product":
                raise server.ledger.stop_at_once(
                    f"client {session.label}: HTTP 402; stopping at once",
                    rate_limited=False,
                    billing=True,
                )
            return None

        run, server = make_run(server=server, default_behaviour=charged)
        run.lean = True
        with NoSettle():
            run.setup()
            with self.assertRaises(GuardrailStop):
                run.run_matrix({"VD-create"})
        self.assertTrue(run.stop_signals)
        self.assertEqual(row(run, "VD-create").verdict, matrix.INCONCLUSIVE)
        with NoSettle():
            problems = run.finish(cleanup=True)
        self.assertTrue(any(p.startswith("cleanup skipped") for p in problems), problems)


class LeanSetupTest(unittest.TestCase):
    def test_a_video_and_feeds_run_creates_two_users_and_no_channel(self) -> None:
        run, _server = product_run(only={"VD-create"})
        self.assertEqual(run.users, [run.ctx["A"], run.ctx["B"]])
        self.assertEqual(run.channels, [])
        self.assertEqual(sorted(run.sessions), ["A", "B"])
        self.assertEqual([c.check_id for c in run.checks], ["AP1", "AP4-A", "AP4-B"])
        self.assertTrue(all(c.result == "PASS" for c in run.checks))
        self.assertEqual(
            (run.ledger.run.users, run.ledger.run.channels, run.ledger.run.peak_connections),
            (2, 0, 2),
        )
        self.assertIn("lean setup", run.notes[0])
        self.assertTrue(run.results()["lean"])
        self.assertNotIn("AP11", {c.check_id for c in run.checks})  # no reconnect check

    def test_lean_only(self) -> None:
        self.assertTrue(proof_run.lean_only({"VD-create", "FD-feed"}))
        self.assertTrue(proof_run.lean_only(PRODUCT_CASES))
        self.assertFalse(proof_run.lean_only({"VD-create", "S1"}))
        self.assertFalse(proof_run.lean_only({"S1"}))
        self.assertFalse(proof_run.lean_only({"no-such-case"}))
        self.assertFalse(proof_run.lean_only(None))
        self.assertFalse(proof_run.lean_only(set()))

    def test_the_full_setup_runs_the_product_cases_too(self) -> None:
        run, _server = product_run(only={"VD-create", "FD-feed"}, lean=False)
        self.assertEqual(len(run.users), 4)
        self.assertEqual(verdicts(run), {"VD-create": matrix.FAIL, "FD-feed": matrix.FAIL})


class PreflightObjectsTest(unittest.TestCase):
    def preflight(self, prepare: Any) -> Any:
        run, server = make_run()
        server.users["owner"] = dashboard_user("owner")
        prepare(server.products)
        return run, run.preflight()

    def test_a_call_feed_or_activity_the_run_did_not_create_stops_the_run(self) -> None:
        for prepare, expected in (
            (
                lambda s: s.calls.update(
                    {
                        "default:someone": {
                            "id": "someone",
                            "type": "default",
                            "custom": {},
                            "members": [],
                            "created_by": "x",
                        }
                    }
                ),
                "call default:someone",
            ),
            (
                lambda s: s.feeds.update({"user:someone": {"user_id": "someone", "custom": {}}}),
                "feed user:someone",
            ),
            (
                lambda s: s.activities.update(
                    {
                        "a-9": {
                            "type": "post",
                            "text": "t",
                            "feeds": [],
                            "user_id": "x",
                            "custom": {},
                        }
                    }
                ),
                "activity a-9",
            ),
        ):
            with self.assertRaises(RunStopped) as stopped:
                self.preflight(prepare)
            self.assertEqual(
                str(stopped.exception),
                f"application holds data this run did not create: {expected}",
            )

    def test_a_product_that_is_not_available_is_recorded_and_stops_nothing(self) -> None:
        def unavailable(state: Any) -> None:
            state.available["feeds"] = False

        run, result = self.preflight(unavailable)
        self.assertEqual(result["calls_before_run"], 0)
        self.assertTrue(
            str(result["feeds_before_run"]).startswith("not available: HTTP 403 code 17")
        )
        self.assertTrue(str(result["activities_before_run"]).startswith("not available"))
        self.assertIsNone(run.preexisting["remaining_feeds"])

    def test_the_end_of_the_run_tells_new_objects_from_preexisting_ones(self) -> None:
        run, server = make_run()
        server.users["owner"] = dashboard_user("owner")
        server.products.available["video"] = False  # its listing stays not available
        run.preflight()
        server.products.feeds["user:left"] = {"user_id": "left", "custom": {}}
        out = run.verify_clean()
        self.assertEqual(out["remaining_feeds"], ["user:left"])
        self.assertIsNone(out["remaining_calls"])
        problems = cleanup_problems({**run.cleanup_result, **out, "errors": []})
        self.assertIn("remaining_feeds: ['user:left']", problems)
        self.assertFalse(any(p.startswith("remaining_calls") for p in problems), problems)


class VerdictLabelTest(unittest.TestCase):
    def test_not_available_is_neither_kept_when_interrupted_nor_a_pass(self) -> None:
        self.assertNotIn(matrix.NOT_AVAILABLE, matrix.KEPT_WHEN_INTERRUPTED)
        self.assertNotEqual(matrix.NOT_AVAILABLE, matrix.HOLDS)
        self.assertIn(PREFIX, PREFIX)


if __name__ == "__main__":
    unittest.main()
