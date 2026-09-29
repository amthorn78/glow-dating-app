"""The reference design's switches (D5), importable without Django.

The reference is ``Design()``. Each negative control flips exactly one switch, so a
control breaks one guarantee and the suite must see it fail (item 6.3).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TimeSource = Literal["clock_timestamp", "transaction_start"]


@dataclass(frozen=True)
class Design:
    """The reference design and its switches. Defaults are the design; a control flips
    one switch."""

    lock_accounts: bool = True
    lock_match: bool = True
    lock_session: bool = True
    check_contact_version: bool = True
    time_source: TimeSource = "clock_timestamp"
    authorize_before_dedup: bool = True
    # 5.5: filter on state inside the locked read and treat an absent row as nothing to
    # refuse. The design locks by primary key and checks state in code.
    filter_state_in_lock: bool = False
    # 5.3: a block locks the lower account first whoever acts. The control locks the
    # actor's own account first.
    canonical_order: bool = True

    def describe(self) -> str:
        changed = [
            name
            for name, default in (
                ("lock_accounts", True),
                ("lock_match", True),
                ("lock_session", True),
                ("check_contact_version", True),
                ("time_source", "clock_timestamp"),
                ("authorize_before_dedup", True),
                ("filter_state_in_lock", False),
                ("canonical_order", True),
            )
            if getattr(self, name) != default
        ]
        return "reference" if not changed else "broken:" + ",".join(changed)


REFERENCE = Design()
