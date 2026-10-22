"""The app's persistence adapter as the suite's second subject (P06.2 Stage A, D3).

``AdapterSubject`` drives ``glow_chat.contact.OrmContactPersistence`` (the app code
under test, imported from ``services/api`` unchanged) through the suite's one
interface. It only translates: the suite's ``SendRequest`` into the domain's
``SendCommand``, the suite's ``Hooks`` into the adapter's ``TransactionProbe`` (whose
callables only signal and wait), and the adapter's results into the suite's ``Result``.
After each call, outside the adapter's transaction, it records the call's context
(``proof_adapter_call``); the oracle never takes a commit time from that row.

``AdapterFixtures`` creates accounts with the maintained authentication persistence,
a visible profile and an accepted onboarding consent (through the adapter's own consent
writer), and matches through the adapter's match activation, which commits the chat
binding, the random channel and provider user IDs, the identities' and the channel's
outbox events together (DM-13 9.4; B1, CX4). An identity is ``pending`` until the
delivery phase provisions it; the token cases need a provisioned identity before that
phase, so ``provision_identity`` marks one ``active`` by a fixture write (B1).
"""

from __future__ import annotations

import secrets
import uuid
from datetime import timedelta
from typing import Any
from uuid import UUID

from django.contrib.auth import get_user_model
from django.db import transaction
from glow_chat.contact import OrmContactPersistence
from glow_domain.chat import ContactResult, SendCommand, TransactionProbe
from glow_persistence.models import AppAccount, ChatIdentity, Profile

from glow_ordering_proof.interface import Hooks, Receipt, Result, SendRequest, Timing
from glow_ordering_proof.observe import ProofLog

PROVIDER = "fixture"
POLICY_VERSION = "proof-onboarding-1"


def _probe(hooks: Hooks | None) -> TransactionProbe | None:
    if hooks is None:
        return None
    return TransactionProbe(
        on_begin=hooks.on_begin,
        after_first_lock=hooks.after_first_lock,
        after_locks=hooks.after_locks,
        before_commit=hooks.before_commit,
    )


def to_result(result: ContactResult) -> Result:
    trace = result.trace
    receipt = result.receipt
    detail = dict(result.detail)
    if result.grant is not None:
        # The grant's times, from the database clock; never the opaque user ID.
        detail["issued_at"] = result.grant.issued_at
        detail["expires_at"] = result.grant.expires_at
    return Result(
        result.outcome,
        result.reason,
        receipt=(
            Receipt(receipt.submission_id, receipt.contact_version, receipt.request_digest)
            if receipt is not None
            else None
        ),
        timing=Timing(trace.backend_pid, trace.started_at, trace.ended_at) if trace else None,
        session_id=result.session_id,
        detail=detail,
    )


class AdapterSubject:
    """``OrderingSubject`` and ``ContactStateSubject`` over the app's adapter."""

    def __init__(self, adapter: OrmContactPersistence, log: ProofLog) -> None:
        self.adapter = adapter
        self.log = log

    def _done(self, kind: str, result: ContactResult, **ids: UUID | None) -> Result:
        trace = result.trace
        self.log.record_call(
            kind=kind,
            outcome=result.outcome if not result.reason else f"{result.outcome}:{result.reason}",
            submission_id=result.receipt.submission_id if result.receipt else None,
            backend_pid=trace.backend_pid if trace else None,
            started_at=trace.started_at if trace else None,
            ended_at=trace.ended_at if trace else None,
            event_ids=result.events,
            **ids,
        )
        return to_result(result)

    # -- the suite's interface --------------------------------------------------------

    def sign_in(
        self, account_id: UUID, *, ttl_seconds: float, hooks: Hooks | None = None
    ) -> Result:
        # A stand-in for the maintained adapter's non-secret session identifier (P06.DB
        # D2): generated here, in the proof; the app takes it as given.
        result = self.adapter.open_session(
            account_id,
            auth_session_ref=f"standin-{secrets.token_hex(16)}",
            lifetime=timedelta(seconds=ttl_seconds),
            probe=_probe(hooks),
        )
        return self._done("sign_in", result, actor_id=account_id, session_id=result.session_id)

    def sign_out(self, session_id: UUID, *, hooks: Hooks | None = None) -> Result:
        result = self.adapter.sign_out(session_id, probe=_probe(hooks))
        return self._done("sign_out", result, session_id=session_id)

    def expire_session(self, session_id: UUID, *, hooks: Hooks | None = None) -> Result:
        result = self.adapter.expire_session(session_id, probe=_probe(hooks))
        return self._done("expire", result, session_id=session_id)

    def send(self, request: SendRequest, *, hooks: Hooks | None = None) -> Result:
        command = SendCommand(
            session_id=request.session_id,
            match_id=request.match_id,
            contact_version=request.contact_version,
            idempotency_key=request.idempotency_key,
            text=request.text,
        )
        result = self.adapter.send(command, probe=_probe(hooks))
        return self._done("send", result, match_id=request.match_id, session_id=request.session_id)

    def block(self, actor_id: UUID, target_id: UUID, *, hooks: Hooks | None = None) -> Result:
        result = self.adapter.block(actor_id, target_id, probe=_probe(hooks))
        return self._done(
            "block", result, match_id=result.match_id, actor_id=actor_id, target_id=target_id
        )

    def unblock(self, actor_id: UUID, target_id: UUID, *, hooks: Hooks | None = None) -> Result:
        result = self.adapter.unblock(actor_id, target_id, probe=_probe(hooks))
        return self._done("unblock", result, actor_id=actor_id, target_id=target_id)

    def unmatch(self, actor_id: UUID, match_id: UUID, *, hooks: Hooks | None = None) -> Result:
        result = self.adapter.unmatch(actor_id, match_id, probe=_probe(hooks))
        return self._done("unmatch", result, match_id=match_id, actor_id=actor_id)

    def suspend(self, account_id: UUID, *, hooks: Hooks | None = None) -> Result:
        result = self.adapter.suspend(account_id, probe=_probe(hooks))
        return self._done("suspend", result, actor_id=account_id)

    def delete(self, account_id: UUID, *, hooks: Hooks | None = None) -> Result:
        result = self.adapter.delete(account_id, probe=_probe(hooks))
        return self._done("delete", result, actor_id=account_id)

    def pause_profile(self, account_id: UUID, *, hooks: Hooks | None = None) -> Result:
        result = self.adapter.pause_profile(account_id, probe=_probe(hooks))
        return self._done("pause", result, actor_id=account_id)

    def resume_profile(self, account_id: UUID, *, hooks: Hooks | None = None) -> Result:
        result = self.adapter.resume_profile(account_id, probe=_probe(hooks))
        return self._done("resume", result, actor_id=account_id)

    def restrict_profile(self, account_id: UUID, *, hooks: Hooks | None = None) -> Result:
        result = self.adapter.restrict_profile(account_id, probe=_probe(hooks))
        return self._done("restrict", result, actor_id=account_id)

    def withdraw_consent(self, account_id: UUID, *, hooks: Hooks | None = None) -> Result:
        result = self.adapter.withdraw_consent(account_id, probe=_probe(hooks))
        return self._done("withdraw", result, actor_id=account_id)

    def accept_consent(self, account_id: UUID, *, hooks: Hooks | None = None) -> Result:
        result = self.adapter.accept_consent(
            account_id, policy_version=POLICY_VERSION, probe=_probe(hooks)
        )
        return self._done("accept", result, actor_id=account_id)

    # -- P06.2 B1 --------------------------------------------------------------------

    def activate_match(self, first: UUID, second: UUID, *, hooks: Hooks | None = None) -> Result:
        result = self.adapter.activate_match(first, second, probe=_probe(hooks))
        return self._done(
            "activate", result, match_id=result.match_id, actor_id=first, target_id=second
        )

    def grant_token(self, session_id: UUID, *, hooks: Hooks | None = None) -> Result:
        result = self.adapter.grant_token(session_id, probe=_probe(hooks))
        return self._done("grant", result, session_id=session_id)


class AdapterFixtures:
    """``FixtureFactory`` for the adapter: accounts ready to send, matches activated
    through the adapter. Fixture writes record no call row; their own rows are their
    witnesses."""

    def __init__(self, adapter: OrmContactPersistence) -> None:
        self.adapter = adapter

    def create_account(self) -> UUID:
        with transaction.atomic():
            # No password and no email address: credentials are the maintained
            # library's, out of scope (P06.DB D2, D6).
            user = get_user_model().objects.create_user(username=f"proof-{uuid.uuid4().hex}")
            account: Any = AppAccount.objects.create(auth_user=user, state="active")
            # A synthetic display name; the provider never receives it (D3 of the brief).
            Profile.objects.create(account=account, display_name="Proof member", state="visible")
        consent = self.adapter.accept_consent(account.id, policy_version=POLICY_VERSION)
        if consent.outcome != "applied":
            raise RuntimeError(f"fixture consent failed: {consent.outcome}:{consent.reason}")
        assert isinstance(account.id, UUID)
        return account.id

    def create_match(self, first: UUID, second: UUID) -> UUID:
        activated = self.adapter.activate_match(first, second)
        if activated.outcome != "applied" or activated.match_id is None:
            raise RuntimeError(
                f"fixture match activation failed: {activated.outcome}:{activated.reason}"
            )
        match_id = activated.match_id
        assert isinstance(match_id, UUID)
        return match_id

    @staticmethod
    def provision_identity(account_id: UUID) -> None:
        """A fixture write (B1): the account's identity as the provider's receipt would
        leave it, ``active``, so a grant can be made before the delivery phase. The
        identity's own event is still delivered in that phase; the receipt then changes
        nothing."""
        ChatIdentity.objects.filter(account_id=account_id, provider=PROVIDER).update(state="active")
