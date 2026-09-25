"""Offline tests. Importing this package disables outbound network connections."""

import socket
from typing import Any


def _refuse(*_args: Any, **_kwargs: Any) -> Any:
    raise OSError("network access is disabled in the offline tests")


socket.socket.connect = _refuse  # type: ignore[method-assign]
socket.socket.connect_ex = _refuse  # type: ignore[method-assign]
socket.create_connection = _refuse
