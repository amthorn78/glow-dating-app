"""P06.1-I2a's run plan: count the complete set offline, before any live call.

The I2a prompt, section 5, and DM-04 finding 5: the complete set (the I1 matrix and
every I2a case) is run against the fakes, whose reservations go through the same
usage ledger a live run uses, and so is each case family on its own after the base
setup, as a rerun (``run --only``) would be. Run 1 may use the complete set's count
only if what is left of the session's caps still covers one rerun: the base setup
plus the largest single case family. Otherwise there is no live run.

A case family is a group of the matrix (``Case.group``). The fakes answer as the
live lockdown is expected to; a case that fails in a way that creates data can
reserve more, and ``CONDITIONAL`` lists those.

The caps are per session, and this checkout's usage ledger (the ignored
``.work/usage-ledger.json``) holds what earlier live commands of the session used:
the plan adds it (read only; zero when there is no ledger).

Usage, offline and without any ``STREAM_*`` variable::

    python checks/run_plan.py

It prints the count and exits 0 when the plan fits, 1 when it does not.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROOF_ROOT = Path(__file__).resolve().parent.parent
if str(PROOF_ROOT) not in sys.path:
    sys.path.insert(0, str(PROOF_ROOT))

from glow_stream_proof import matrix  # noqa: E402
from glow_stream_proof.usage import Limits  # noqa: E402
from tests.fake_world import family_run  # noqa: E402
from tests.fakes import NoSettle  # noqa: E402

RESOURCES = ("users", "channels", "peak_connections")
LEDGER = PROOF_ROOT / ".work" / "usage-ledger.json"
# What a case can reserve beyond the count, only when it fails in a way that creates
# data (the fakes do not).
CONDITIONAL = {
    "EO-channel": "+1 channel, if a probe of the missing channel created it",
}


def measure(only: set[str] | None) -> dict[str, Any]:
    """One run against the fakes: setup, the authorized path and ``only`` (every case
    when ``None``), then the end of the run; what the ledger counted."""
    run, _server, _world, clock = family_run()
    with NoSettle(), clock:
        run.setup()
        run.authorized_path()
        run.run_matrix(only)
        problems = run.finish(cleanup=True)
    counted = run.ledger.summary()["run"]
    return {
        **{key: counted[key] for key in RESOURCES},
        "api_calls": counted["api_calls"],
        "cases": len(run.case_results),
        "problems": problems,
        "harness_errors": [c.case_id for c in run.case_results if "harness error" in c.observed],
    }


def session_used(ledger: Path | None) -> dict[str, int]:
    """What earlier live commands of this checkout used of the session's caps, from its
    usage ledger (never written here); zero when there is none."""
    stored: dict[str, Any] = {}
    if ledger is not None and ledger.exists():
        stored = json.loads(ledger.read_text(encoding="utf-8")).get("session", {})
    return {key: int(stored.get(key, 0)) for key in ("users", "channels", "api_calls")}


def plan(ledger: Path | None = LEDGER) -> dict[str, Any]:
    cases = matrix.all_cases()
    used = session_used(ledger)
    complete = measure(None)
    # No case: an empty set would mean every case to run_matrix.
    base = measure({"(no case)"})
    families: dict[str, dict[str, Any]] = {}
    for group in sorted({c.group for c in cases}):
        families[group] = measure({c.id for c in cases if c.group == group})
    reserve = {key: max(f[key] for f in families.values()) for key in RESOURCES}
    largest = {
        key: sorted(g for g, f in families.items() if f[key] == reserve[key]) for key in RESOURCES
    }
    limits = Limits()
    caps = {"users": limits.users, "channels": limits.channels}
    fits = {
        key: used[key] + complete[key] + reserve[key] <= caps[key] for key in ("users", "channels")
    }
    fits["peak_connections"] = max(complete["peak_connections"], reserve["peak_connections"]) <= (
        limits.connections
    )
    fits["api_calls"] = (
        used["api_calls"] + complete["api_calls"] + max(f["api_calls"] for f in families.values())
        <= limits.api_calls
    )
    return {
        "complete_set": complete,
        "base_setup": base,
        "families": families,
        "reserve": reserve,
        "largest_family": largest,
        "caps": {**caps, "connections": limits.connections, "api_calls": limits.api_calls},
        "session_used_before": used,
        "fits": fits,
        "conditional": CONDITIONAL,
        "all_fit": all(fits.values()),
        "note": "API calls: the fakes count the server's calls and one per recorded client "
        "request; the live count differs",
    }


def main() -> int:
    # Each measure uses a fresh ledger with no file: nothing is loaded or written.
    result = plan()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("run plan: fits" if result["all_fit"] else "run plan: DOES NOT FIT: no live run")
    return 0 if result["all_fit"] else 1


if __name__ == "__main__":
    sys.exit(main())
