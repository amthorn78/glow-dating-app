"""P06.1-I2a, DM-04 finding 2: the closing checks see application-wide settings.

``configuration.verify`` compares every setting the committed baseline records, so
preflight, the end of a run and the dry-run ``configure`` each see an
application-wide token revocation or a hook (``tests/test_configuration.py`` checks
the comparison itself).
"""

import unittest

import tests  # noqa: F401
from glow_stream_proof import cli
from glow_stream_proof.proof_run import RunStopped
from glow_stream_proof.redaction import Redactor
from glow_stream_proof.usage import UsageLedger
from tests.fakes import FakeServer, NoSettle, make_run, set_up
from tests.test_preflight import dashboard_user

REVOKE_ALL = "2026-09-26T12:00:00Z"


class ClosingChecksTest(unittest.TestCase):
    def test_preflight_sees_an_application_wide_token_revocation(self) -> None:
        run, server = make_run()
        server.users["owner"] = dashboard_user("owner")
        server.app["revoke_tokens_issued_before"] = REVOKE_ALL
        with self.assertRaises(RunStopped) as stopped:
            run.preflight()
        self.assertIn(
            f"revoke_tokens_issued_before is '{REVOKE_ALL}', recorded None",
            str(stopped.exception),
        )

    def test_the_end_of_the_run_sees_a_hook(self) -> None:
        run, server = make_run()
        with NoSettle():
            set_up(run)
            server.app["webhook_url"] = "https://hooks.invalid/w"
            problems = run.finish(cleanup=True)
        self.assertIn(
            "configuration differs after the run: webhook_url is 'https://hooks.invalid/w', "
            "recorded ''",
            problems,
        )

    def test_the_dry_run_configure_sees_them(self) -> None:
        server = FakeServer(UsageLedger())
        server.app["event_hooks"] = [{"url": "https://hooks.invalid/e"}]
        server.app["revoke_tokens_issued_before"] = REVOKE_ALL

        class Context:
            api = server
            redactor = Redactor()
            lines: list[str] = []

            def say(self, text: str) -> None:
                self.lines.append(text)

        ctx = Context()
        self.assertEqual(cli.cmd_configure(ctx, apply=False), 0)  # type: ignore[arg-type]
        before = next(line for line in ctx.lines if line.startswith("differences before:"))
        self.assertIn("event_hooks is [{'url': 'https://hooks.invalid/e'}], recorded []", before)
        self.assertIn(f"revoke_tokens_issued_before is '{REVOKE_ALL}', recorded None", before)


if __name__ == "__main__":
    unittest.main()


class ProductDriftTest(unittest.TestCase):
    """P06.1-I2b: once the lockdown is recorded as applied, preflight, the end of the run
    and the dry-run ``configure`` see a client role's grant in Video or Feeds as drift."""

    def test_preflight_and_the_end_of_the_run_see_it(self) -> None:
        from unittest import mock

        from glow_stream_proof import products

        run, server = make_run()
        server.users["owner"] = dashboard_user("owner")
        server.products.grant_before_lockdown()
        drift = "video/feeds: video call type default: grants for user not empty: "
        with mock.patch.object(products, "LOCKDOWN_APPLIED", "2026-09-27T00:00:00Z"):
            with self.assertRaises(RunStopped) as stopped:
                run.preflight()
            self.assertIn(drift, str(stopped.exception))
            # Locked: the run may start.
            for grants in server.products.call_type_grants.values():
                for role in products.CLIENT_ROLES:
                    grants[role] = []
            for grants in server.products.visibility_grants.values():
                for role in products.CLIENT_ROLES:
                    grants[role] = []
            run.preflight()
            with NoSettle():
                set_up(run)
                server.products.call_type_grants["default"]["user"] = ["create-call"]
                problems = run.finish(cleanup=True)
        self.assertIn("configuration differs after the run: " + drift + "['create-call']", problems)

    def test_the_dry_run_configure_sees_it(self) -> None:
        from unittest import mock

        from glow_stream_proof import products

        server = FakeServer(UsageLedger())
        server.products.grant_before_lockdown()

        class Context:
            api = server
            redactor = Redactor()
            lines: list[str] = []

            def say(self, text: str) -> None:
                self.lines.append(text)

        ctx = Context()
        with mock.patch.object(products, "LOCKDOWN_APPLIED", "2026-09-27T00:00:00Z"):
            self.assertEqual(cli.cmd_configure(ctx, apply=False), 0)  # type: ignore[arg-type]
        before = next(line for line in ctx.lines if line.startswith("differences before:"))
        self.assertIn("video/feeds: video call type default: grants for user not empty", before)
