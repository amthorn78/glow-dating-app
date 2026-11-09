"""The member's own ``AccountAccess`` (F01's response; the SV1 brief's Outcome 5), and the
contract's envelope and error, as plain values (``gapp-api-v1``).

Pure functions: the API tests validate their output with the contract's own validator
(``packages/contracts/runtime.py``), and the proof checks the served body against the same
schema. ``account_id`` is the app account's UUID, never the auth user's ID or email.
"""

from __future__ import annotations

import uuid
from typing import Any
from uuid import UUID

CONTRACT_VERSION = "gapp-api-v1"
ACCOUNT_STATES = ("unverified", "active", "suspended", "deletion_pending", "deleted")
SESSION_STATES = ("valid", "revoked", "expired")


def new_request_id() -> str:
    return str(uuid.uuid4())


def account_access(
    account_id: UUID, version: int, state: str, session_state: str
) -> dict[str, Any]:
    if state not in ACCOUNT_STATES or session_state not in SESSION_STATES:
        raise ValueError("not a contract state")
    return {
        "kind": "account_access",
        "account_id": str(account_id),
        "version": int(version),
        "state": state,
        "session_state": session_state,
    }


def app_response(data: dict[str, Any], request_id: str) -> dict[str, Any]:
    return {"contract_version": CONTRACT_VERSION, "request_id": request_id, "data": data}


def error(code: str, request_id: str, *, retryable: bool = False) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": request_id,
        "code": code,
        "retryable": retryable,
    }
