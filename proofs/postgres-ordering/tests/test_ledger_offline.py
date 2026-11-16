"""B-C1's ledger at the wrapper's level, offline (SV3 Stage B, correction B-C3's item 7; B-C2's
delta re-review, F6; DM-77).

``_as_a_client`` wraps every Stage B and B-C1 case so that ``_Ledger`` checks each command's
expected version. Its two wrappers, the routes' (``ctx.profiles.call``) and the direct one
(``glow_discovery.interactions``' four commands), check the version a command sent against the
versions served before it was sent, and only then record the command's own answer. So an answer
that echoes the version it was sent (an unmatch of a match already ``unmatched``, ``no_change``,
for one) never vouches for it.

No database and no Django: the routes are a stand-in ``call``, and ``glow_discovery.interactions``
is a stand-in module, put in ``sys.modules`` for the test only.
"""

from __future__ import annotations

import sys
import types
import unittest
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any
from unittest import mock
from uuid import uuid4

from glow_ordering_proof import interaction_cases
from glow_ordering_proof.identity_support import CaseFailed, Reply

UNSERVED = 7  # a version no answer or read gave: as if read from the database


def _member() -> Any:
    return SimpleNamespace(account_id=uuid4(), device=object())


def _match_body(match_id: str, version: int) -> dict[str, Any]:
    return {
        "meta": {"idempotency_key": str(uuid4()), "expected_version": version},
        "match_id": match_id,
    }


def _no_change(match_id: str, version: int) -> dict[str, Any]:
    """An unmatch's answer for a match already ``unmatched``: the match, at the version sent."""
    return {"kind": "match", "match_id": match_id, "state": "unmatched", "version": version}


class _Profiles:
    """The routes, stood in: each ``call`` answers with what ``answer`` gives for its path."""

    def __init__(self, answer: Callable[[str, Any], Reply]) -> None:
        self.answer = answer

    def call(self, member: Any, method: str, path: str, body: Any = None, **kwargs: Any) -> Reply:
        return self.answer(path, body)


def _interactions(unmatch: Callable[..., Any]) -> tuple[types.ModuleType, types.ModuleType]:
    """A stand-in ``glow_discovery`` package and its ``interactions`` module, whose ``unmatch``
    is ``unmatch`` and whose other commands are never called."""

    def never(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("not called")

    module = types.ModuleType("glow_discovery.interactions")
    module.interact = never  # type: ignore[attr-defined]
    module.undo = never  # type: ignore[attr-defined]
    module.block = never  # type: ignore[attr-defined]
    module.unmatch = unmatch  # type: ignore[attr-defined]
    package = types.ModuleType("glow_discovery")
    package.interactions = module  # type: ignore[attr-defined]
    return package, module


def _run(case: Callable[[Any], str], profiles: _Profiles, unmatch: Callable[..., Any]) -> str:
    """``case`` run under ``_as_a_client``, as the discovery suite runs a Stage B case."""
    package, module = _interactions(unmatch)
    ctx = SimpleNamespace(profiles=profiles)
    with mock.patch.dict(
        sys.modules, {"glow_discovery": package, "glow_discovery.interactions": module}
    ):
        return interaction_cases._as_a_client(case)(ctx)  # type: ignore[arg-type]


def _unused_direct(*args: Any, **kwargs: Any) -> Any:
    raise AssertionError("not called")


class LedgerWrapperTests(unittest.TestCase):
    """The ledger's two wrappers check a command's version before recording its answer."""

    def test_a_route_command_answering_with_an_unserved_version_it_sent_fails(self) -> None:
        member, match_id = _member(), str(uuid4())

        def answer(path: str, body: Any) -> Reply:
            version = body["meta"]["expected_version"]
            return Reply(200, {"data": _no_change(match_id, version)})

        def case(ctx: Any) -> str:
            """Sends an unmatch with a version no answer or read gave."""
            ctx.profiles.call(
                member, "POST", interaction_cases.UNMATCH, _match_body(match_id, UNSERVED)
            )
            return "sent"

        with self.assertRaises(CaseFailed) as raised:
            _run(case, _Profiles(answer), _unused_direct)
        self.assertIn("1 did not", str(raised.exception))
        self.assertIn(
            "match: a command sent a version no answer or read gave", str(raised.exception)
        )

    def test_a_direct_command_answering_with_an_unserved_version_it_sent_fails(self) -> None:
        member, match_id = _member(), str(uuid4())

        def unmatch(account_id: Any, intent: Any, **kwargs: Any) -> Any:
            version = intent["meta"]["expected_version"]
            return SimpleNamespace(ok=True, code="no_change", data=_no_change(match_id, version))

        def case(ctx: Any) -> str:
            """Calls the unmatch command directly with a version no answer or read gave."""
            from glow_discovery import interactions  # the stand-in

            interactions.unmatch(member.account_id, _match_body(match_id, UNSERVED))
            return "sent"

        with self.assertRaises(CaseFailed) as raised:
            _run(case, _Profiles(lambda path, body: Reply(404, None)), unmatch)
        self.assertIn("1 did not", str(raised.exception))

    def test_a_read_then_a_command_with_its_version_passes(self) -> None:
        member, match_id = _member(), str(uuid4())
        read_path = f"/api/v1/matches/{match_id}"

        def answer(path: str, body: Any) -> Reply:
            if path == read_path:
                return Reply(200, {"data": _no_change(match_id, 3)})
            version = body["meta"]["expected_version"]
            return Reply(200, {"data": _no_change(match_id, version)})

        def unmatch(account_id: Any, intent: Any, **kwargs: Any) -> Any:
            version = intent["meta"]["expected_version"]
            return SimpleNamespace(ok=True, code="no_change", data=_no_change(match_id, version))

        def case(ctx: Any) -> str:
            """Reads the match, then sends an unmatch, through the routes and directly, with the
            read's version."""
            from glow_discovery import interactions  # the stand-in

            ctx.profiles.call(member, "GET", read_path)
            ctx.profiles.call(member, "POST", interaction_cases.UNMATCH, _match_body(match_id, 3))
            interactions.unmatch(member.account_id, _match_body(match_id, 3))
            return "sent"

        detail = _run(case, _Profiles(answer), unmatch)
        self.assertTrue(detail.startswith("sent ["), detail)
        self.assertIn("2 expected versions sent", detail)

    def test_the_versions_checked_are_those_served_before_the_send(self) -> None:
        # S5's concurrent direct answer: a version served while the command is in flight (here,
        # by the command's own call, standing for another thread's answer) does not vouch for it.
        member, match_id = _member(), str(uuid4())
        ledger_holder: list[Any] = []

        def unmatch(account_id: Any, intent: Any, **kwargs: Any) -> Any:
            version = intent["meta"]["expected_version"]
            for ledger in ledger_holder:
                ledger.served_from(_no_change(match_id, version), "direct:other", str(account_id))
            return SimpleNamespace(ok=True, code="no_change", data=None)

        real = interaction_cases._Ledger

        def keep(*args: Any, **kwargs: Any) -> Any:
            ledger = real(*args, **kwargs)
            ledger_holder.append(ledger)
            return ledger

        def case(ctx: Any) -> str:
            """Calls the unmatch command directly with a version served only while it runs."""
            from glow_discovery import interactions  # the stand-in

            interactions.unmatch(member.account_id, _match_body(match_id, UNSERVED))
            return "sent"

        with mock.patch.object(interaction_cases, "_Ledger", keep):
            with self.assertRaises(CaseFailed):
                _run(case, _Profiles(lambda path, body: Reply(404, None)), unmatch)


if __name__ == "__main__":
    unittest.main()
