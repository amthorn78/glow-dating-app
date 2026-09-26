"""The run's own stop conditions.

Kept apart from :mod:`glow_stream_proof.proof_run` so that the server client
(:mod:`glow_stream_proof.server_api`) can raise :class:`GuardRefused`, which
stops the run like any other stop condition (P06.1-I2a).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .proof_run import CaseResult


class RunStopped(RuntimeError):
    """The run stopped on a stop condition; the reason is reported.

    ``case_result`` holds what the case in progress had already observed, so
    that the matrix records it instead of losing it.
    """

    case_result: CaseResult | None = None


class GuardRefused(RunStopped):
    """The guard refused a server call before it was sent (:mod:`glow_stream_proof.guard`).

    Its message names the request's shape and the reason, never an identifier
    the run did not create.
    """
