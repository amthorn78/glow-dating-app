"""The identity cases (SV1; its brief's acceptance checks 1 to 13, with D2 to D9), each run
through the HTTP endpoints with Django's test client on the disposable identity database.

Every case makes its own synthetic members, so no case depends on another. Each declares the
acceptance checks it covers. A case returns a short detail line, or raises ``CaseFailed``.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from unittest import mock
from uuid import UUID

from glow_ordering_proof.identity_support import (
    ACCOUNT_ACCESS,
    APP,
    CaseFailed,
    Context,
    Device,
    clock_ahead,
    expect,
    mail_forbidden_found,
    recording_issued_codes,
)


@dataclass(frozen=True)
class Case:
    case_id: str
    checks: tuple[str, ...]
    run: Callable[[Context], str]


CASES: list[Case] = []


def case(
    case_id: str, *checks: str
) -> Callable[[Callable[[Context], str]], Callable[[Context], str]]:
    def register(function: Callable[[Context], str]) -> Callable[[Context], str]:
        CASES.append(Case(case_id, checks, function))
        return function

    return register


def _actor(device: Device, bearer: str | None) -> int:
    return device.account_access(bearer).status


def _valid_body(reply: Any) -> list[str]:
    from glow_ordering_proof.schema_check import check

    return check("AppResponse", reply.body)


def _error_body(reply: Any, code: str) -> bool:
    from glow_ordering_proof.schema_check import check

    return not check("Error", reply.body) and (reply.body or {}).get("code") == code


def _account(account_id: UUID) -> Any:
    from glow_persistence.models import AppAccount

    return AppAccount.objects.get(pk=account_id)


def _sessions(account_id: UUID) -> list[Any]:
    from glow_persistence.models import AccountSession

    return list(AccountSession.objects.filter(account_id=account_id).order_by("created_at"))


def _user_sessions(user_id: int) -> int:
    from allauth.usersessions.models import UserSession

    return int(UserSession.objects.filter(user_id=user_id).count())


def _xmin(table: str, column: str, value: Any) -> int:
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT xmin::text::bigint FROM {table} WHERE {column} = %s", [value])
        row = cursor.fetchone()
    expect(row is not None, f"the {table} row exists")
    return int(row[0])


# =============================================================================================
# Configuration and routes (D2, D3, D5, D8)
# =============================================================================================


@case("config.settings_as_briefed", "D2", "D3", "D5", "D8")
def config_settings(ctx: Context) -> str:
    from allauth import app_settings as allauth_settings
    from allauth.account import app_settings as account
    from allauth.headless import app_settings as headless
    from allauth.headless.tokens.strategies.jwt import JWTTokenStrategy, internal
    from allauth.usersessions import app_settings as usersessions
    from cryptography.hazmat.primitives.asymmetric import rsa
    from django.apps import apps
    from django.conf import settings
    from django.test import override_settings
    from glow_identity.sessions import GlowUserSessionsAdapter
    from glow_identity.strategy import GlowJWTTokenStrategy

    strategy = headless.TOKEN_STRATEGY
    expect(isinstance(strategy, GlowJWTTokenStrategy), "the token strategy is Glow's")
    expect(isinstance(strategy, JWTTokenStrategy), "Glow's strategy is allauth's JWT strategy")
    expect(headless.CLIENTS == ("app",), "the app client only")
    expect(allauth_settings.HEADLESS_ONLY, "HEADLESS_ONLY")
    expect(not headless.SERVE_SPECIFICATION, "the specification is not served")
    expect(headless.FRONTEND_URLS == {}, "no frontend URL is set")
    expect(headless.JWT_ALGORITHM == "RS256", "RS256")
    config = internal._get_jwt_config()
    key = config.signing_key
    expect(
        isinstance(key, rsa.RSAPrivateKey) and key.key_size >= 2048,
        "an RSA key of 2048 bits or more",
    )
    expect(headless.JWT_ACCESS_TOKEN_EXPIRES_IN == 300, "access tokens live 300 seconds")
    expect(headless.JWT_REFRESH_TOKEN_EXPIRES_IN == 30 * 86400, "refresh tokens live 30 days")
    expect(headless.JWT_STATEFUL_VALIDATION_ENABLED, "stateful validation is on")
    expect(headless.JWT_ROTATE_REFRESH_TOKEN, "refresh rotation is on")
    expect(account.LOGIN_METHODS == {account.LoginMethod.EMAIL}, "email login only")
    expect(
        account.SIGNUP_FIELDS == {"email": {"required": True}, "password1": {"required": True}},
        "sign-up takes email and password only",
    )
    expect(account.UNIQUE_EMAIL, "unique email")
    expect(account.EMAIL_VERIFICATION == account.EmailVerificationMethod.MANDATORY, "mandatory")
    expect(account.EMAIL_VERIFICATION_BY_CODE_ENABLED, "verification by code")
    expect(account.EMAIL_VERIFICATION_BY_CODE_MAX_ATTEMPTS == 3, "three attempts per code")
    expect(
        account.EMAIL_VERIFICATION_BY_CODE_TIMEOUT == 900, "a verification code lives 15 minutes"
    )
    expect(account.PASSWORD_RESET_BY_CODE_ENABLED, "reset by code")
    expect(account.PASSWORD_RESET_BY_CODE_MAX_ATTEMPTS == 3, "three attempts per reset code")
    expect(account.PASSWORD_RESET_BY_CODE_TIMEOUT == 180, "a reset code lives 3 minutes")
    expect(account.EMAIL_UNKNOWN_ACCOUNTS is False, "no mail to an unknown address")
    expect(account.PREVENT_ENUMERATION is True, "enumeration prevention (not strict)")
    expect(account.CHANGE_EMAIL, "one address, replaced after verification")
    expect(account.REAUTHENTICATION_REQUIRED is True, "an address change needs reauthentication")
    expect(account.REAUTHENTICATION_TIMEOUT == 300, "within the last 300 seconds")
    expect(account.RATE_LIMITS["reauthenticate"] == "10/m/user", "allauth's reauthenticate limit")
    expect(account.EMAIL_NOTIFICATIONS, "the account-change notices")
    expect(account.LOGOUT_ON_PASSWORD_CHANGE, "a password change ends every session")
    expect(not account.LOGIN_BY_CODE_ENABLED, "no login by code")
    expect(
        account.RATE_LIMITS["login_failed"] == "10/m/ip,5/300s/key", "allauth's failed-login limit"
    )
    # D3 (correction C2, DM-48): change_password at 5 per 300 seconds per account, merged into
    # allauth's defaults, which every other limit keeps.
    resolved = dict(account.RATE_LIMITS)
    with override_settings(ACCOUNT_RATE_LIMITS={}):
        defaults = dict(account.RATE_LIMITS)
    expect(resolved["change_password"] == "5/300s/user", "the password change's limit")
    expect(defaults["change_password"] == "5/m/user", "in place of allauth's default 5/m/user")
    expect(
        set(resolved) == set(defaults)
        and [name for name in defaults if resolved[name] != defaults[name]] == ["change_password"],
        "every other rate limit keeps allauth's default",
    )
    # F-7 (correction C2): a pending verification can neither change its address nor resend its
    # code, so it answers alike whoever holds the address.
    # 65.21.1 resolves the two settings as counts (account/app_settings.py:121-140).
    for name in ("SUPPORTS_CHANGE", "SUPPORTS_RESEND"):
        expect(
            getattr(settings, f"ACCOUNT_EMAIL_VERIFICATION_{name}", False) is False,
            f"ACCOUNT_EMAIL_VERIFICATION_{name} is off",
        )
    expect(account.EMAIL_VERIFICATION_MAX_CHANGE_COUNT == 0, "no address change while pending")
    expect(account.EMAIL_VERIFICATION_MAX_RESEND_COUNT == 0, "no code resend while pending")
    expect(not apps.is_installed("allauth.mfa"), "no multi-factor authentication")
    expect(not apps.is_installed("allauth.socialaccount"), "no social login")
    expect(
        usersessions.ADAPTER == "glow_identity.sessions.GlowUserSessionsAdapter", "Glow's adapter"
    )
    expect(issubclass(GlowUserSessionsAdapter, object), "the adapter loads")
    expect(not usersessions.TRACK_ACTIVITY, "no activity tracking")
    expect(settings.DATABASES["default"].get("ATOMIC_REQUESTS") is False, "no ATOMIC_REQUESTS")
    expect(
        settings.EMAIL_BACKEND == "glow_identity.mail.FixtureEmailBackend", "the fixture backend"
    )
    expect(not settings.EMAIL_HOST_USER and not settings.EMAIL_HOST_PASSWORD, "no SMTP credential")
    expect(settings.SESSION_ENGINE == "django.contrib.sessions.backends.db", "the database store")
    expect(settings.GLOW_IDENTITY_SESSION_LIFETIME == timedelta(days=30), "30-day sessions")
    expect(len(settings.SECRET_KEY) >= 50, "a generated SECRET_KEY")
    minimum = [v for v in settings.AUTH_PASSWORD_VALIDATORS if "MinimumLength" in v["NAME"]]
    expect(minimum and minimum[0]["OPTIONS"]["min_length"] == 10, "passwords of 10 or more")
    return "every briefed value holds at the installed release"


EXPECTED_ROUTES = frozenset(
    {
        "_allauth/app/v1/account/email",
        "_allauth/app/v1/account/password/change",
        "_allauth/app/v1/account/phone",
        "_allauth/app/v1/auth/code/confirm",
        "_allauth/app/v1/auth/email/verify",
        "_allauth/app/v1/auth/email/verify/resend",
        "_allauth/app/v1/auth/login",
        "_allauth/app/v1/auth/password/request",
        "_allauth/app/v1/auth/password/reset",
        "_allauth/app/v1/auth/phone/verify",
        "_allauth/app/v1/auth/phone/verify/resend",
        "_allauth/app/v1/auth/reauthenticate",
        "_allauth/app/v1/auth/session",
        "_allauth/app/v1/auth/sessions",
        "_allauth/app/v1/auth/signup",
        "_allauth/app/v1/config",
        "_allauth/app/v1/tokens/refresh",
        "api/v1/account/access",
    }
)


def served_routes() -> frozenset[str]:
    from django.urls import get_resolver

    def walk(patterns: Any, prefix: str = "") -> Any:
        for pattern in patterns:
            if hasattr(pattern, "url_patterns"):
                yield from walk(pattern.url_patterns, prefix + str(pattern.pattern))
            else:
                yield prefix + str(pattern.pattern)

    return frozenset(walk(get_resolver().url_patterns))


@case("config.routes", "D3", "Outcome 5")
def config_routes(ctx: Context) -> str:
    routes = served_routes()
    expect(
        routes == EXPECTED_ROUTES, "the served routes are allauth's app routes and one Glow route"
    )
    return f"{len(routes)} routes: 17 of allauth's app client, 1 Glow route"


# Each endpoint, with no credential: (method, path, body, expected status).
UNAUTHENTICATED: tuple[tuple[str, str, dict[str, Any] | None, int], ...] = (
    ("GET", APP + "config", None, 200),
    ("GET", APP + "auth/session", None, 401),
    ("DELETE", APP + "auth/session", None, 401),
    ("POST", APP + "auth/reauthenticate", {"password": "Synthetic-not-a-password"}, 401),
    ("POST", APP + "auth/code/confirm", {"code": "BCDF-GHJK"}, 409),
    ("POST", APP + "account/password/change", {"new_password": "Synthetic-x1"}, 401),
    ("GET", APP + "account/email", None, 401),
    ("POST", APP + "account/email", {"email": "nobody@example.invalid"}, 409),
    ("PUT", APP + "account/email", {"email": "nobody@example.invalid"}, 401),
    ("PATCH", APP + "account/email", {"email": "nobody@example.invalid"}, 401),
    ("DELETE", APP + "account/email", {"email": "nobody@example.invalid"}, 401),
    ("GET", APP + "account/phone", None, 401),
    ("POST", APP + "account/phone", {"phone": "+15555550100"}, 409),
    ("POST", APP + "auth/password/request", {}, 400),
    ("GET", APP + "auth/password/reset", None, 409),
    ("POST", APP + "auth/password/reset", {"key": "x", "password": "y"}, 409),
    ("POST", APP + "auth/login", {}, 400),
    ("POST", APP + "auth/signup", {}, 400),
    ("GET", APP + "auth/email/verify", None, 409),
    ("POST", APP + "auth/email/verify", {"key": "BCDF-GHJK"}, 409),
    ("POST", APP + "auth/email/verify/resend", None, 409),
    ("POST", APP + "auth/phone/verify", {"code": "123456"}, 409),
    ("POST", APP + "auth/phone/verify/resend", None, 409),
    ("POST", APP + "tokens/refresh", {}, 400),
    ("POST", APP + "tokens/refresh", {"refresh_token": "not-a-token"}, 400),
    ("GET", APP + "auth/sessions", None, 401),
    ("DELETE", APP + "auth/sessions", {"sessions": [1]}, 401),
    ("GET", ACCOUNT_ACCESS, None, 401),
    ("POST", ACCOUNT_ACCESS, None, 401),
)


@case("endpoints.refusals", "3", "4", "threat model")
def endpoint_refusals(ctx: Context) -> str:
    device = ctx.device()
    seen: list[str] = []
    for method, path, body, expected in UNAUTHENTICATED:
        reply = device.call(method, path, body)
        expect(reply.status == expected, f"{method} {path} with no credential answers {expected}")
        expect(not reply.tokens() & {"access_token", "refresh_token"}, f"{method} {path}: no token")
        seen.append(f"{method} {path.removeprefix(APP)} {reply.status}")
    refused = device.account_access(None)
    expect(
        _error_body(refused, "unauthenticated"), "the Glow route's refusal is the contract's Error"
    )
    member = ctx.member()
    signed_in = member.device
    for method, path, expected in (
        ("GET", APP + "account/phone", 403),
        ("POST", APP + "account/phone", 403),
        ("POST", APP + "auth/code/confirm", 409),
        ("POST", ACCOUNT_ACCESS, 405),
    ):
        reply = signed_in.call(
            method,
            path,
            {"phone": "+15555550100"} if "phone" in path else None,
            bearer=signed_in.access,
        )
        expect(reply.status == expected, f"{method} {path} signed in answers {expected}")
        expect(reply.status < 500, f"{method} {path} signed in is not a server error")
    other = signed_in.call("POST", ACCOUNT_ACCESS, bearer=signed_in.access)
    expect(
        _error_body(other, "invalid_request"), "another method is the contract's invalid_request"
    )
    return f"{len(seen)} unauthenticated requests refused as expected; 4 signed-in refusals"


# =============================================================================================
# Acceptance check 1: sign-up (D4, D9)
# =============================================================================================


@case("signup.records_unverified_account", "1")
def signup_records(ctx: Context) -> str:
    import re

    from allauth.account.models import EmailAddress
    from django.contrib.auth import get_user_model
    from glow_persistence.models import AccountAgeState, AccountSession, AppAccount

    device = ctx.device()
    email, password = ctx.email(), ctx.password()
    mark = ctx.mail_mark()
    reply = ctx.sign_up(device, email, password)
    expect(reply.status == 401, "sign-up answers 401")
    expect(reply.pending() == {"verify_email"}, "email verification is pending")
    expect(
        "access_token" not in reply.tokens() and "refresh_token" not in reply.tokens(),
        "no token pair",
    )
    users = get_user_model().objects.filter(email=email)
    expect(users.count() == 1, "one auth user")
    user = users.get()
    addresses = EmailAddress.objects.filter(user=user)
    expect(addresses.count() == 1 and not addresses.get().verified, "one unverified address")
    account = AppAccount.objects.get(auth_user=user)
    expect(account.state == "unverified" and account.version == 1, "one unverified AppAccount")
    age = AccountAgeState.objects.get(account=account)
    expect(
        age.state == "unknown" and age.method == "none" and age.policy_version is None,
        "unknown age",
    )
    expect(not AccountSession.objects.filter(account=account).exists(), "no AccountSession")
    expect(_user_sessions(user.pk) == 0, "no allauth session")
    local = email.split("@")[0]
    expect(re.fullmatch(r"g[0-9a-f]{32}", user.username) is not None, "the username is opaque")
    expect(local not in user.username, "the username copies nothing of the email")
    expect(len(ctx.mail_since(mark, email)) == 1, "one verification message")
    return "one user, one unverified address, one unverified account, one unknown age state"


@case("signup.one_transaction", "1", "D4")
def signup_one_transaction(ctx: Context) -> str:
    from django.contrib.auth import get_user_model
    from glow_persistence.models import AppAccount

    device = ctx.device()
    email = ctx.email()
    expect(ctx.sign_up(device, email, ctx.password()).status == 401, "sign-up answers 401")
    user = get_user_model().objects.get(email=email)
    account = AppAccount.objects.get(auth_user=user)
    user_tx = _xmin("auth_user", "id", user.pk)
    account_tx = _xmin("glow_persistence_appaccount", "id", account.pk)
    age_tx = _xmin("glow_persistence_accountagestate", "account_id", account.pk)
    expect(
        user_tx == account_tx == age_tx,
        "the user, its account and its age state share a transaction",
    )
    return "the three rows carry one xmin"


@case("signup.failure_leaves_no_user", "1", "D4")
def signup_failure(ctx: Context) -> str:
    from django.contrib.auth import get_user_model
    from glow_identity import age

    device = ctx.device()
    email = ctx.email()
    with mock.patch.object(age.OrmAgeAssurance, "record", side_effect=RuntimeError("injected")):
        reply = ctx.sign_up(device, email, ctx.password())
    expect(reply.status == 500, "the injected failure answers 500")
    expect(
        not get_user_model().objects.filter(email=email).exists(),
        "no auth user without its account",
    )
    return "an age-state write failure rolls back the user and its account"


# =============================================================================================
# Acceptance check 2: verification by code (D3, D6)
# =============================================================================================


@case("verify.activates_and_issues_pair", "2", "D6")
def verify_activates(ctx: Context) -> str:
    device = ctx.device()
    email = ctx.email()
    mark = ctx.mail_mark()
    ctx.sign_up(device, email, ctx.password())
    reply = ctx.verify(device, ctx.code_since(mark, email))
    expect(reply.status == 200, "the right code answers 200")
    expect({"access_token", "refresh_token"} <= reply.tokens(), "the token pair is returned")
    _, account_id = ctx.ids(email)
    account = _account(account_id)
    expect(account.state == "active", "the account is active")
    expect(
        account.version == 2 and account.eligibility_version == 2, "version and eligibility bumped"
    )
    sessions = _sessions(account_id)
    expect(len(sessions) == 1 and sessions[0].state == "valid", "one valid AccountSession")
    expect(_actor(device, device.access) == 200, "the actor accepts the new access token")
    return "unverified to active (version 2, eligibility 2); one valid session"


@case("verify.wrong_code_refused", "2")
def verify_wrong(ctx: Context) -> str:
    device = ctx.device()
    email = ctx.email()
    mark = ctx.mail_mark()
    ctx.sign_up(device, email, ctx.password())
    code = ctx.code_since(mark, email)
    wrong = "BCDF-GHJK" if code != "BCDF-GHJK" else "CDFG-HJKL"
    reply = ctx.verify(device, wrong)
    expect(reply.status == 400, "a wrong code answers 400")
    expect(not reply.tokens() & {"access_token", "refresh_token"}, "no token pair")
    _, account_id = ctx.ids(email)
    expect(_account(account_id).state == "unverified", "the account stays unverified")
    expect(ctx.verify(device, code).status == 200, "the right code still works within the limit")
    return "refused; the attempt counted; the right code then worked"


@case("verify.expired_code_refused", "2")
def verify_expired(ctx: Context) -> str:
    from allauth.account.internal.flows import code_verification

    results = []
    for seconds, expected in ((895, 200), (905, 409)):
        device = ctx.device()
        email = ctx.email()
        mark = ctx.mail_mark()
        ctx.sign_up(device, email, ctx.password())
        code = ctx.code_since(mark, email)
        with clock_ahead(code_verification, seconds):
            reply = ctx.verify(device, code)
        expect(reply.status == expected, f"the code {seconds} s later answers {expected}")
        _, account_id = ctx.ids(email)
        state = _account(account_id).state
        expect(
            state == ("active" if expected == 200 else "unverified"), "the account state follows"
        )
        results.append(f"{seconds}s:{reply.status}")
    return "15-minute limit: " + ", ".join(results)


@case("verify.used_code_refused", "2")
def verify_used(ctx: Context) -> str:
    device = ctx.device()
    email = ctx.email()
    mark = ctx.mail_mark()
    ctx.sign_up(device, email, ctx.password())
    pending_token = device.session_token
    code = ctx.code_since(mark, email)
    expect(ctx.verify(device, code).status == 200, "the code works once")
    again_old = device.app("POST", "auth/email/verify", {"key": code}, session_token=pending_token)
    expect(again_old.status == 410, "the used code with the old session token: 410 (session gone)")
    again = device.app("POST", "auth/email/verify", {"key": code}, bearer=device.access)
    expect(again.status == 409, "the used code signed in: 409 (no pending verification)")
    _, account_id = ctx.ids(email)
    expect(len(_sessions(account_id)) == 1, "no second session")
    return "a used code is refused (410 on the old session, 409 signed in)"


@case("verify.attempt_limit", "2")
def verify_attempt_limit(ctx: Context) -> str:
    device = ctx.device()
    email, password = ctx.email(), ctx.password()
    mark = ctx.mail_mark()
    ctx.sign_up(device, email, password)
    code = ctx.code_since(mark, email)
    wrong = "BCDF-GHJK" if code != "BCDF-GHJK" else "CDFG-HJKL"
    statuses = [ctx.verify(device, wrong).status for _ in range(3)]
    expect(statuses == [400, 400, 400], "three wrong codes are refused")
    reply = ctx.verify(device, code)
    expect(reply.status == 409, "after three attempts the right code is refused (409)")
    _, account_id = ctx.ids(email)
    expect(_account(account_id).state == "unverified", "the account stays unverified")
    ctx.clear_rate_limits()
    mark = ctx.mail_mark()
    again = device.app("POST", "auth/login", {"email": email, "password": password})
    expect(
        again.status == 401 and again.pending() == {"verify_email"}, "signing in starts a new code"
    )
    expect(ctx.verify(device, ctx.code_since(mark, email)).status == 200, "the new code works")
    return "three attempts, then the process ends; a new sign-in sends a new code"


@case("verify.transition_retried_at_sign_in", "2", "4", "D6")
def verify_retried(ctx: Context) -> str:
    from allauth.account.models import EmailAddress
    from glow_identity import revocation

    device = ctx.device()
    email, password = ctx.email(), ctx.password()
    mark = ctx.mail_mark()
    ctx.sign_up(device, email, password)
    code = ctx.code_since(mark, email)
    refused = revocation.Outcome("refused", "injected")
    with mock.patch.object(revocation, "mark_verified", return_value=refused):
        reply = ctx.verify(device, code)
    expect(
        reply.status == 401 and not reply.tokens() & {"access_token"}, "the sign-in fails closed"
    )
    user_id, account_id = ctx.ids(email)
    expect(
        EmailAddress.objects.get(user_id=user_id).verified, "allauth marked the address verified"
    )
    expect(_account(account_id).state == "unverified", "the transition did not apply")
    expect(not _sessions(account_id), "no AccountSession")
    retry = ctx.device()
    signed_in = retry.app("POST", "auth/login", {"email": email, "password": password})
    expect(signed_in.status == 200, "the next sign-in succeeds")
    expect(_account(account_id).state == "active", "the next sign-in took the transition")
    expect(_actor(retry, retry.access) == 200, "and its session serves the actor")
    return "a verified address never leaves its account unverified"


@case("verified.waits_on_account_lock", "D6")
def verified_waits(ctx: Context) -> str:
    from glow_domain.chat import TransactionProbe
    from glow_identity import revocation

    from glow_ordering_proof.concurrency import Hold, PidSlot, Worker
    from glow_ordering_proof.observe import observe_lock_wait

    device = ctx.device()
    email = ctx.email()
    ctx.sign_up(device, email, ctx.password())
    _, account_id = ctx.ids(email)
    holder, arriver = Worker("identity-holder"), Worker("identity-arriver")
    try:
        hold, slot = Hold(), PidSlot()
        probe = TransactionProbe(on_begin=slot.set, before_commit=hold.point)
        suspending = holder.submit(lambda: revocation.contact().suspend(account_id, probe=probe))
        expect(hold.wait_held(), "the suspension holds the account lock")
        arriver_pid = arriver.run(_backend_pid)
        verifying = arriver.submit(lambda: revocation.mark_verified(account_id))
        wait = observe_lock_wait(arriver_pid, holder_pid=slot.wait(), finished=verifying.done)
        hold.release.set()
        suspended = suspending.result(timeout=30)
        outcome = verifying.result(timeout=30)
    finally:
        hold.release.set()
        holder.close()
        arriver.close()
    expect(wait.observed, "the verified transition waited on the suspension's account lock")
    expect(suspended.outcome == "applied", "the suspension applied")
    expect(outcome.outcome == "refused", "the transition refused after the suspension committed")
    expect(_account(account_id).state == "suspended", "the account stays suspended")
    return wait.summary()


def _backend_pid() -> int:
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_backend_pid()")
        return int(cursor.fetchone()[0])


@case("verified.refuses_unless_unverified", "D6")
def verified_refuses(ctx: Context) -> str:
    from glow_identity import revocation

    member = ctx.member()
    before = _account(member.account_id)
    again = revocation.mark_verified(member.account_id)
    after = _account(member.account_id)
    expect(again.outcome == "no_change" and after.version == before.version, "active: no change")
    for operation, state in (("suspend", "suspended"), ("delete", "deletion_pending")):
        device = ctx.device()
        email = ctx.email()
        ctx.sign_up(device, email, ctx.password())
        _, account_id = ctx.ids(email)
        getattr(revocation.contact(), operation)(account_id)
        outcome = revocation.mark_verified(account_id)
        expect(outcome.outcome == "refused", f"a {state} account is refused")
        expect(_account(account_id).state == state, f"the account stays {state}")
    return "active is no change; suspended and deletion_pending are refused"


# =============================================================================================
# Acceptance check 3: enumeration and wrong-account linking (D3)
# =============================================================================================


@case("enum.signup_taken_and_new_alike", "3")
def enum_signup(ctx: Context) -> str:
    from django.contrib.auth import get_user_model

    member = ctx.member()
    # Outside allauth's 10-second window since the owner's own code; within it, the taken
    # address answers 429 (recorded in the threat model).
    ctx.clear_rate_limits()
    taken, fresh = ctx.device(), ctx.device()
    fresh_email = ctx.email()
    mark = ctx.mail_mark()
    taken_reply = ctx.sign_up(taken, member.email, ctx.password())
    fresh_reply = ctx.sign_up(fresh, fresh_email, ctx.password())
    expect(taken_reply.status < 500 and fresh_reply.status < 500, "neither raises")
    expect(taken_reply.shape() == fresh_reply.shape(), "a taken and a new address answer alike")
    expect(get_user_model().objects.filter(email=member.email).count() == 1, "no second account")
    to_member = ctx.mail_since(mark, member.email)
    expect(len(to_member) == 1 and to_member[0].subject == "Your Glow account", "the owner is told")
    expect("code is" not in to_member[0].body, "the owner's notice holds no code")
    expect(len(ctx.mail_since(mark, fresh_email)) == 1, "the new address gets its code")
    return f"both answer {taken_reply.status} with the same shape; the owner gets Glow's notice"


@case("enum.reset_unknown_and_known_alike", "3")
def enum_reset(ctx: Context) -> str:
    member = ctx.member()
    unknown = ctx.email()
    ctx.unknown_addresses.add(unknown)
    known_device, unknown_device = ctx.device(), ctx.device()
    mark = ctx.mail_mark()
    known_reply = known_device.app("POST", "auth/password/request", {"email": member.email})
    unknown_reply = unknown_device.app("POST", "auth/password/request", {"email": unknown})
    expect(known_reply.status < 500 and unknown_reply.status < 500, "neither raises")
    expect(
        known_reply.shape() == unknown_reply.shape(), "an unknown and a known address answer alike"
    )
    expect(len(ctx.mail_since(mark, member.email)) == 1, "the known address gets a reset code")
    expect(not ctx.mail_since(mark, unknown), "the unknown address gets nothing")
    return f"both answer {known_reply.status} with the same shape; no mail to the unknown address"


@case("enum.email_change_taken_and_free_alike", "3")
def enum_email_change(ctx: Context) -> str:
    a, b = ctx.member(), ctx.member()
    ctx.clear_rate_limits()
    free = ctx.email()
    ctx.asked_addresses.update({b.email, free})
    # Correction C1: an address change needs a reauthentication in the same session first.
    expect(ctx.reauthenticate(a.device, a.password).status == 200, "A reauthenticates")
    mark = ctx.mail_mark()
    to_taken = a.device.app("POST", "account/email", {"email": b.email}, bearer=a.device.access)
    a2 = ctx.sign_in(a)
    expect(ctx.reauthenticate(a2, a.password).status == 200, "A reauthenticates on its device")
    to_free = a2.app("POST", "account/email", {"email": free}, bearer=a2.access)
    expect(to_taken.status < 500 and to_free.status < 500, "neither raises")
    expect(to_taken.shape() == to_free.shape(), "a taken and a free address answer alike")
    listed_taken = sorted(entry["email"] for entry in to_taken.data())
    listed_free = sorted(entry["email"] for entry in to_free.data())
    expect(listed_taken == sorted([a.email, b.email]), "the pending address is listed (taken)")
    expect(listed_free == sorted([a.email, free]), "the pending address is listed (free)")
    to_b = ctx.mail_since(mark, b.email)
    expect(len(to_b) == 1, "the installed release sends the code to the address asked for (taken)")
    expect(len(ctx.mail_since(mark, free)) == 1, "and to the free address")
    stolen = ctx.code_since(mark, b.email)
    linked = a.device.app("POST", "auth/email/verify", {"key": stolen}, bearer=a.device.access)
    from allauth.account.models import EmailAddress

    # allauth refuses at validation: the address cannot be verified while another account
    # holds it verified (headless/account/inputs.py, VerifyEmailInput.clean_key).
    codes = [e.get("code") for e in (linked.body or {}).get("errors", [])]
    expect(linked.status == 400 and "email_taken" in codes, "even with B's own code, refused")
    expect(
        sorted(EmailAddress.objects.filter(user_id=a.user_id).values_list("email", flat=True))
        == [a.email],
        "A's address is unchanged",
    )
    expect(EmailAddress.objects.get(email=b.email).user_id == b.user_id, "B keeps its address")
    return "taken and free answer alike; wrong-account linking refused with B's own code"


# =============================================================================================
# Acceptance check 4: sign-in (D4, D5, D6, D7)
# =============================================================================================


@case("signin.records_account_session", "4", "D2", "D5")
def signin_records(ctx: Context) -> str:
    from allauth.usersessions.models import UserSession
    from django.contrib.sessions.models import Session

    from glow_ordering_proof.schema_check import check

    member = ctx.member()
    device = ctx.sign_in(member)
    row = ctx.account_session_of(device.access or "")
    key = ctx.session_key_of(device.access or "")
    account = _account(member.account_id)
    user_session = UserSession.objects.get(session_key=key)
    expect(
        row.state == "valid" and row.epoch == account.session_epoch, "valid, at the current epoch"
    )
    expect(
        row.auth_session_ref == str(user_session.pk), "the reference is UserSession's primary key"
    )
    # A BigAutoField row ID (allauth's migration), not the key or anything derived from it.
    expect(
        row.auth_session_ref.isdigit() and row.auth_session_ref != key,
        "the reference is a row ID, not the key",
    )
    lifetime = row.expires_at - row.created_at
    expect(abs(lifetime - timedelta(days=30)) < timedelta(seconds=5), "30 days from sign-in")
    expire_date = Session.objects.get(session_key=key).expire_date
    expect(expire_date == row.expires_at, "allauth's session expires at the same instant")
    reply = device.account_access(device.access)
    expect(reply.status == 200, "the actor accepts the access token")
    expect(not check("AppResponse", reply.body), "AccountAccess validates against the contract")
    data = reply.data()
    expect(
        data
        == {
            "kind": "account_access",
            "account_id": str(member.account_id),
            "version": account.version,
            "state": "active",
            "session_state": "valid",
        },
        "AccountAccess is the owner's state",
    )
    return "valid at epoch, UserSession reference, 30 days, aligned expiry, AccountAccess valid"


@case("signin.reference_not_derived", "4", "D5")
def signin_reference(ctx: Context) -> str:
    member = ctx.member()
    device = member.device
    first = device.access or ""
    expect(
        device.app("POST", "tokens/refresh", {"refresh_token": device.refresh}).status == 200,
        "refresh",
    )
    second = device.access or ""
    from allauth.headless.tokens.strategies.jwt import internal

    sid_one = str(internal.decode_token(first, "access")["sid"])
    sid_two = str(internal.decode_token(second, "access")["sid"])
    key = ctx.session_key_of(first)
    expect(sid_one != sid_two, "two tokens of one session carry different sids (a fresh IV each)")
    expect(ctx.session_key_of(second) == key, "both decrypt to the one session key")
    expect(key not in (sid_one, sid_two), "the sid is not the key in clear")
    reference = ctx.user_session_ref(key)
    expect(
        reference is not None and reference.isdigit() and reference not in (sid_one, sid_two),
        "the reference is a row ID, not a sid",
    )
    return "the sid is the encrypted key, fresh per token; the reference is a row ID"


@case("signin.unverified_gets_no_session", "4")
def signin_unverified(ctx: Context) -> str:
    device = ctx.device()
    email, password = ctx.email(), ctx.password()
    ctx.sign_up(device, email, password)
    ctx.clear_rate_limits()
    other = ctx.device()
    reply = other.app("POST", "auth/login", {"email": email, "password": password})
    expect(reply.status == 401 and reply.pending() == {"verify_email"}, "verification is pending")
    expect(not reply.tokens() & {"access_token", "refresh_token"}, "no token pair")
    user_id, account_id = ctx.ids(email)
    expect(not _sessions(account_id) and _user_sessions(user_id) == 0, "no session at either layer")
    return "an unverified account gets a code, not a session"


@case("signin.fails_closed", "4", "D6")
def signin_fails_closed(ctx: Context) -> str:
    from django.contrib.sessions.models import Session
    from glow_identity import revocation

    member = ctx.member()
    # Glow's layer only: the account is suspended, its auth user still active, so allauth
    # completes the sign-in and only open_session refuses it.
    expect(revocation.contact().suspend(member.account_id).outcome == "applied", "suspended")
    sessions_before = len(_sessions(member.account_id))
    user_sessions_before = _user_sessions(member.user_id)
    django_sessions_before = Session.objects.count()
    device = ctx.device()
    reply = device.app("POST", "auth/login", {"email": member.email, "password": member.password})
    expect(reply.status == 401, "the sign-in answers 401")
    expect(not reply.tokens(), "no session token and no token pair")
    expect(
        Session.objects.count() == django_sessions_before, "no Django session survives the sign-in"
    )
    expect(_user_sessions(member.user_id) == user_sessions_before, "no UserSession survives it")
    expect(len(_sessions(member.account_id)) == sessions_before, "no AccountSession is opened")
    return "open_session refused, so allauth's session ended in the same request"


# =============================================================================================
# The actor (D5, D7)
# =============================================================================================


@case("actor.uses_token_sid_not_header", "4", "D5", "D7")
def actor_sid(ctx: Context) -> str:
    a, b = ctx.member(), ctx.member()
    a2 = ctx.sign_in(a)
    b_key = ctx.session_key_of(b.device.access or "")
    a2_key = ctx.session_key_of(a2.access or "")
    crossed = a.device.account_access(a.device.access, session_token=b_key)
    expect(crossed.status == 200, "another member's session key in the header is ignored")
    expect(crossed.data()["account_id"] == str(a.account_id), "the actor is the token's own")
    expect(
        a2.app("DELETE", "auth/session", bearer=a2.access).status == 401, "A's second device out"
    )
    stale = a.device.account_access(a.device.access, session_token=a2_key)
    expect(stale.status == 200, "a revoked session's key in the header does not refuse the token")
    return "the actor takes the session from the token's sid only"


@case("actor.refuses_inactive_account", "D7")
def actor_inactive(ctx: Context) -> str:
    from django.db import connection
    from glow_identity import revocation

    # As the app makes it: a suspension at Glow's layer only, its auth user still active.
    member = ctx.member()
    revocation.contact().suspend(member.account_id)
    token = member.device.access or ""
    expect(ctx.allauth_accepts(token), "allauth's layer still accepts the token")
    expect(_actor(member.device, token) == 401, "the actor refuses a suspended account")
    # Every app writer that takes an account out of active also bumps its epoch, so the epoch
    # check would refuse first. A harness write no app writer makes moves the state alone,
    # so the account check is the deciding refusal.
    other = ctx.member()
    row = ctx.account_session_of(other.device.access or "")
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE glow_persistence_appaccount SET state = 'suspended' WHERE id = %s",
            [other.account_id],
        )
    account = _account(other.account_id)
    expect(row.epoch == account.session_epoch, "the session is at the current epoch")
    expect(ctx.allauth_accepts(other.device.access or ""), "allauth's layer still accepts it")
    expect(_actor(other.device, other.device.access) == 401, "the account check refuses it")
    return "account not active: refused whatever the token's remaining life (the deciding check)"


@case("actor.refuses_stale_epoch", "D7")
def actor_epoch(ctx: Context) -> str:
    from django.db import connection

    member = ctx.member()
    with connection.cursor() as cursor:
        # A harness write no app writer makes: the epoch moves while the account stays active,
        # so the epoch check is the deciding refusal.
        cursor.execute(
            "UPDATE glow_persistence_appaccount SET session_epoch = session_epoch + 1"
            " WHERE id = %s",
            [member.account_id],
        )
    token = member.device.access or ""
    expect(_account(member.account_id).state == "active", "the account is still active")
    expect(ctx.allauth_accepts(token), "allauth's layer still accepts the token")
    expect(_actor(member.device, token) == 401, "the actor refuses a session at an old epoch")
    return "the epoch check is the deciding refusal"


@case("actor.refuses_revoked_session_between_layers", "D6", "D7")
def actor_between(ctx: Context) -> str:
    from glow_identity import revocation

    member = ctx.member()
    row = ctx.account_session_of(member.device.access or "")
    expect(revocation.contact().sign_out(row.pk).outcome == "applied", "Glow's layer only")
    token = member.device.access or ""
    expect(ctx.allauth_accepts(token), "allauth's layer has not ended yet")
    expect(_actor(member.device, token) == 401, "the actor already refuses")
    return "between the two commits, Glow's refusal does not wait on allauth's"


# =============================================================================================
# Acceptance check 5: refresh (D2)
# =============================================================================================


@case("refresh.rotates", "5")
def refresh_rotates(ctx: Context) -> str:
    member = ctx.member()
    device = member.device
    old_access, old_refresh = device.access, device.refresh
    reply = device.app("POST", "tokens/refresh", {"refresh_token": old_refresh})
    expect(reply.status == 200, "refresh answers 200")
    expect(device.access != old_access and device.refresh != old_refresh, "a new pair")
    expect(_actor(device, device.access) == 200, "the new access token is accepted")
    return "rotation issues a new pair"


@case("refresh.replay_ends_session", "5", "D2")
def refresh_replay(ctx: Context) -> str:
    member = ctx.member()
    other = ctx.sign_in(member)
    device = member.device
    old_refresh = device.refresh
    row = ctx.account_session_of(device.access or "")
    key = ctx.session_key_of(device.access or "")
    expect(
        device.app("POST", "tokens/refresh", {"refresh_token": old_refresh}).status == 200,
        "rotated",
    )
    current_access, current_refresh = device.access or "", device.refresh
    replay = ctx.device().app("POST", "tokens/refresh", {"refresh_token": old_refresh})
    expect(replay.status == 400, "the replayed refresh token is refused")
    row.refresh_from_db()
    expect(row.state == "revoked", "the session is revoked at Glow's layer")
    expect(ctx.events(row.pk, "session_revoked") == 1, "with its session_revoked event")
    expect(
        ctx.user_session_ref(key) is None and not ctx.django_session_exists(key), "and at allauth's"
    )
    expect(
        _actor(device, current_access) == 401 and not ctx.allauth_accepts(current_access),
        "the current access stops",
    )
    refused = device.app("POST", "tokens/refresh", {"refresh_token": current_refresh})
    expect(refused.status == 400, "the current refresh token stops")
    expect(_actor(other, other.access) == 200, "the member's other device is untouched")
    return "the replay ended its session at both layers; the current pair stopped"


@case("refresh.ended_session_refused_nothing_else", "5")
def refresh_ended(ctx: Context) -> str:
    member = ctx.member()
    other = ctx.sign_in(member)
    device = member.device
    refresh = device.refresh
    expect(device.app("DELETE", "auth/session", bearer=device.access).status == 401, "logged out")
    events = ctx.event_count()
    reply = ctx.device().app("POST", "tokens/refresh", {"refresh_token": refresh})
    expect(reply.status == 400, "a refresh token of an ended session is refused")
    expect(ctx.event_count() == events, "nothing else changes")
    expect(_actor(other, other.access) == 200, "the other session stays valid")
    return "refused, and no further event"


@case("refresh.bad_tokens_refused_without_ending", "5", "D2")
def refresh_bad(ctx: Context) -> str:
    import jwt
    from allauth.headless.tokens.strategies.jwt import internal
    from cryptography.hazmat.primitives.asymmetric import rsa

    member = ctx.member()
    device = member.device
    access, refresh = device.access or "", device.refresh or ""
    claims = internal.decode_token(access, "access")
    assert claims is not None
    head, body, signature = refresh.split(".")
    middle = len(signature) // 2
    swapped = "A" if signature[middle] != "A" else "B"
    tampered = f"{head}.{body}.{signature[:middle]}{swapped}{signature[middle + 1 :]}"
    other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    forged_claims = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "sid": claims["sid"],
        "jti": "11111111-2222-4333-8444-555555555555",
        "token_use": "refresh",
        "sub": claims["sub"],
    }
    forged = jwt.encode(forged_claims, other_key, algorithm="RS256")
    unsigned = jwt.encode(forged_claims, "", algorithm="none")
    expired, _ = internal.create_token(
        "refresh", sub=claims["sub"], sid=claims["sid"], expires_in=-120
    )
    for token in (tampered, forged, unsigned, expired):
        ctx.ledger.add(token)
    row = ctx.account_session_of(access)
    for label, token in (
        ("a bad signature", tampered),
        ("another key's signature", forged),
        ("no signature", unsigned),
        ("a past expiry", expired),
        ("the wrong type (an access token)", access),
    ):
        reply = ctx.device().app("POST", "tokens/refresh", {"refresh_token": token})
        expect(reply.status == 400, f"{label} is refused")
        row.refresh_from_db()
        expect(row.state == "valid", f"{label} ends no session")
    expect(_actor(device, access) == 200, "the member's session is untouched")
    expect(
        device.app("POST", "tokens/refresh", {"refresh_token": refresh}).status == 200,
        "its refresh works",
    )
    return "five bad tokens refused; no session ended"


# =============================================================================================
# Acceptance check 6: expiry (D2, D6)
# =============================================================================================


@case("expiry.access_token", "6")
def expiry_access(ctx: Context) -> str:
    from django.test import override_settings

    with override_settings(HEADLESS_JWT_ACCESS_TOKEN_EXPIRES_IN=2):
        member = ctx.member()
        token = member.device.access or ""
        time.sleep(3.5)
        expect(_actor(member.device, token) == 401, "the actor refuses an expired access token")
        expect(not ctx.allauth_accepts(token), "allauth's layer refuses it")
        expect(
            member.device.app("GET", "auth/session", bearer=token).status == 401,
            "allauth's endpoint too",
        )
    expect(
        member.device.app("POST", "tokens/refresh", {"refresh_token": member.device.refresh}).status
        == 200,
        "refresh",
    )
    expect(_actor(member.device, member.device.access) == 200, "a fresh access token works")
    return "expired access refused; the session lives on"


@case("expiry.refresh_token", "6")
def expiry_refresh(ctx: Context) -> str:
    from django.test import override_settings

    with override_settings(HEADLESS_JWT_REFRESH_TOKEN_EXPIRES_IN=2):
        member = ctx.member()
    refresh = member.device.refresh
    time.sleep(3.5)
    row = ctx.account_session_of(member.device.access or "")
    reply = ctx.device().app("POST", "tokens/refresh", {"refresh_token": refresh})
    expect(reply.status == 400, "an expired refresh token is refused")
    row.refresh_from_db()
    expect(row.state == "valid", "and ends no session")
    return "expired refresh refused without ending its session"


@case("expiry.account_session", "6", "D2", "D6")
def expiry_session(ctx: Context) -> str:
    from django.contrib.sessions.models import Session
    from django.db import connection
    from django.test import override_settings

    with override_settings(GLOW_IDENTITY_SESSION_LIFETIME=timedelta(seconds=3)):
        member = ctx.member()
    device = member.device
    access, refresh = device.access or "", device.refresh
    key = ctx.session_key_of(access)
    row = ctx.account_session_of(access)
    expect(Session.objects.get(session_key=key).expire_date == row.expires_at, "aligned expiry")
    time.sleep(4.0)
    expect(_actor(device, access) == 401, "the actor refuses a session past expires_at")
    expect(not ctx.allauth_accepts(access), "allauth's session ended at the same instant")
    expect(
        ctx.device().app("POST", "tokens/refresh", {"refresh_token": refresh}).status == 400,
        "allauth's refresh refuses",
    )
    expect(
        device.app("GET", "account/email", bearer=access).status == 401,
        "allauth's account endpoint refuses",
    )
    expect(
        device.app("GET", "account/email", session_token=key).status == 410,
        "even with the session key",
    )
    # Glow's own check, which decides when allauth's session has not ended: a harness write
    # (no app writer makes it) moves another member's expires_at into the past.
    other = ctx.member()
    other_row = ctx.account_session_of(other.device.access or "")
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE glow_persistence_accountsession SET expires_at = clock_timestamp()"
            " - interval '1 second' WHERE id = %s",
            [other_row.pk],
        )
    expect(ctx.allauth_accepts(other.device.access or ""), "allauth's layer still accepts it")
    expect(_actor(other.device, other.device.access) == 401, "the actor refuses it")
    other_row.refresh_from_db()
    expect(other_row.state == "expired", "expire_session marked the row when found")
    expect(ctx.events(other_row.pk, "session_expired") == 1, "with its session_expired event")
    return "aligned: both layers stop at expires_at; Glow's own check refuses and marks the row"


# =============================================================================================
# Acceptance check 7: logout (D6)
# =============================================================================================


@case("logout.ends_at_once", "7")
def logout_ends(ctx: Context) -> str:
    member = ctx.member()
    device = member.device
    access, refresh = device.access or "", device.refresh
    row = ctx.account_session_of(access)
    key = ctx.session_key_of(access)
    expect(device.app("DELETE", "auth/session", bearer=access).status == 401, "logout answers 401")
    row.refresh_from_db()
    expect(
        row.state == "revoked" and ctx.events(row.pk, "session_revoked") == 1,
        "the session is revoked",
    )
    expect(_actor(device, access) == 401, "Glow's layer refuses the access token")
    expect(not ctx.allauth_accepts(access), "allauth's layer refuses it (stateful validation)")
    expect(
        ctx.device().app("POST", "tokens/refresh", {"refresh_token": refresh}).status == 400,
        "refresh refused",
    )
    expect(
        device.app("GET", "auth/session", session_token=key).status == 410,
        "the session key is gone",
    )
    return "access, refresh and the session key all refused at once"


@case("logout.second_layer_fails_then_repeat", "7", "D6")
def logout_repeat(ctx: Context) -> str:
    from allauth.account.adapter import DefaultAccountAdapter

    member = ctx.member()
    device = member.device
    access = device.access or ""
    row = ctx.account_session_of(access)
    real_logout = DefaultAccountAdapter.logout
    calls = {"n": 0}

    def failing_once(self: Any, request: Any) -> None:
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("injected")
        real_logout(self, request)

    with mock.patch.object(DefaultAccountAdapter, "logout", failing_once):
        first = device.app("DELETE", "auth/session", bearer=access)
        expect(first.status == 500, "the failed second step answers an error")
        row.refresh_from_db()
        expect(row.state == "revoked", "Glow's layer committed first")
        expect(ctx.allauth_accepts(access), "allauth's session is still there")
        expect(_actor(device, access) == 401, "the actor already refuses")
        repeat = device.app("DELETE", "auth/session", bearer=access)
    expect(repeat.status == 401, "the repeat completes the logout")
    expect(not ctx.allauth_accepts(access), "allauth's layer has ended")
    expect(ctx.events(row.pk, "session_revoked") == 1, "one session_revoked event")
    return "error, then the repeat completed both layers"


# =============================================================================================
# Acceptance check 8: two devices (D6; DM-46's N1)
# =============================================================================================


@case("devices.logout_one_leaves_other", "8")
def devices_logout(ctx: Context) -> str:
    member = ctx.member()
    other = ctx.sign_in(member)
    expect(
        member.device.app("DELETE", "auth/session", bearer=member.device.access).status == 401,
        "out",
    )
    expect(_actor(other, other.access) == 200, "the other device stays signed in")
    return "one logout, one session"


@case("devices.session_list_ends_other", "8", "D6")
def devices_list(ctx: Context) -> str:
    member = ctx.member()
    other = ctx.sign_in(member)
    device = member.device
    listed = device.app("GET", "auth/sessions", bearer=device.access)
    expect(listed.status == 200 and len(listed.data()) == 2, "the list shows both sessions")
    other_ref = ctx.user_session_ref(ctx.session_key_of(other.access or ""))
    other_row = ctx.account_session_of(other.access or "")
    ended = device.app(
        "DELETE", "auth/sessions", {"sessions": [int(other_ref or 0)]}, bearer=device.access
    )
    expect(ended.status == 200 and len(ended.data()) == 1, "the other session is ended")
    other_row.refresh_from_db()
    expect(other_row.state == "revoked", "its AccountSession is revoked")
    expect(ctx.events(other_row.pk, "session_revoked") == 1, "with its session_revoked event")
    expect(
        _actor(other, other.access) == 401 and not ctx.allauth_accepts(other.access or ""),
        "its token stops",
    )
    expect(_actor(device, device.access) == 200, "this device stays signed in")
    return "the list's DELETE ended the other device at both layers"


@case("devices.session_list_current_logs_out", "8", "D6")
def devices_list_current(ctx: Context) -> str:
    member = ctx.member()
    other = ctx.sign_in(member)
    device = member.device
    own_ref = ctx.user_session_ref(ctx.session_key_of(device.access or ""))
    row = ctx.account_session_of(device.access or "")
    reply = device.app(
        "DELETE", "auth/sessions", {"sessions": [int(own_ref or 0)]}, bearer=device.access
    )
    expect(reply.status == 401, "ending the current session logs out")
    row.refresh_from_db()
    expect(row.state == "revoked" and ctx.events(row.pk, "session_revoked") == 1, "revoked once")
    expect(_actor(other, other.access) == 200, "the other device stays signed in")
    return "the current session chosen: allauth logs out; Glow's row revoked once"


@case("devices.password_change_ends_both", "8", "10", "D5", "D6")
def devices_password_change(ctx: Context) -> str:
    member = ctx.member()
    other = ctx.sign_in(member)
    device = member.device
    rows = [ctx.account_session_of(d.access or "") for d in (device, other)]
    old_key = ctx.session_key_of(device.access or "")
    new_password = ctx.password()
    mark = ctx.mail_mark()
    reply = device.app(
        "POST",
        "account/password/change",
        {"current_password": member.password, "new_password": new_password},
        bearer=device.access,
    )
    expect(reply.status == 401, "the password change signs this device out")
    expect("session_token" not in reply.tokens(), "no new session key is handed out")
    for row in rows:
        row.refresh_from_db()
        expect(
            row.state == "revoked" and ctx.events(row.pk, "session_revoked") == 1, "both revoked"
        )
    for d in (device, other):
        expect(
            _actor(d, d.access) == 401 and not ctx.allauth_accepts(d.access or ""),
            "both tokens stop",
        )
        expect(
            ctx.device().app("POST", "tokens/refresh", {"refresh_token": d.refresh}).status == 400,
            "refresh stops",
        )
    expect(
        device.app("GET", "auth/session", session_token=old_key).status == 410,
        "the old key is gone",
    )
    notices = [
        m
        for m in ctx.mail_since(mark, member.email)
        if m.subject == "Your Glow password was changed"
    ]
    expect(len(notices) == 1, "one password-changed notice")
    member.password = new_password
    again = ctx.sign_in(member)
    expect(_actor(again, again.access) == 200, "the member signs in again with the new password")
    return "both sessions ended; one notice; signed in again"


@case("devices.password_reset_ends_both", "8", "10", "D6")
def devices_password_reset(ctx: Context) -> str:
    member = ctx.member()
    other = ctx.sign_in(member)
    rows = [ctx.account_session_of(d.access or "") for d in (member.device, other)]
    recovering = ctx.device()
    mark = ctx.mail_mark()
    requested = recovering.app("POST", "auth/password/request", {"email": member.email})
    expect(requested.status == 401, "the reset is requested")
    code = ctx.code_since(mark, member.email)
    confirmed = recovering.app(
        "GET",
        "auth/password/reset",
        headers={"X-Password-Reset-Key": code},
        session_token=recovering.session_token,
    )
    expect(confirmed.status == 200, "the reset code is confirmed")
    new_password = ctx.password()
    reset = recovering.app(
        "POST",
        "auth/password/reset",
        {"key": code, "password": new_password},
        session_token=recovering.session_token,
    )
    expect(reset.status == 401, "the reset answers 401 (no sign-in on reset)")
    for row in rows:
        row.refresh_from_db()
        expect(row.state == "revoked", "every session is revoked")
    for d in (member.device, other):
        expect(
            _actor(d, d.access) == 401 and not ctx.allauth_accepts(d.access or ""),
            "every token stops",
        )
    notices = [
        m for m in ctx.mail_since(mark, member.email) if m.subject == "Your Glow password was reset"
    ]
    expect(len(notices) == 1, "one password-reset notice")
    member.password = new_password
    again = ctx.sign_in(member)
    expect(_actor(again, again.access) == 200, "the member signs in with the new password")
    return "lost-device recovery ended both sessions; one notice"


# =============================================================================================
# Acceptance check 9: suspension and deletion (D6)
# =============================================================================================


def _revocation_case(ctx: Context, operation: str, state: str) -> str:
    from django.contrib.auth import get_user_model
    from glow_identity import revocation
    from glow_persistence.models import DeletionJob, DeletionTombstone

    member = ctx.member()
    other = ctx.sign_in(member)
    devices = (member.device, other)
    epoch = _account(member.account_id).session_epoch
    outcome = getattr(revocation, f"{operation}_account")(member.account_id)
    expect(outcome.outcome == "applied", f"{operation} applied")
    account = _account(member.account_id)
    expect(account.state == state and account.session_epoch == epoch + 1, "the epoch is bumped")
    for row in _sessions(member.account_id):
        expect(row.epoch < account.session_epoch, "every AccountSession is at an old epoch")
    expect(_user_sessions(member.user_id) == 0, "every allauth session has ended")
    expect(ctx.events(member.account_id, "access_revoked") == 1, "access_revoked")
    expect(ctx.events(member.account_id, "session_epoch_bumped") == 1, "session_epoch_bumped")
    for d in devices:
        expect(
            _actor(d, d.access) == 401 and not ctx.allauth_accepts(d.access or ""),
            "every access stops",
        )
        expect(
            ctx.device().app("POST", "tokens/refresh", {"refresh_token": d.refresh}).status == 400,
            "every refresh stops",
        )
    expect(
        not get_user_model().objects.get(pk=member.user_id).is_active, "the auth user is inactive"
    )
    retry = ctx.device().app(
        "POST", "auth/login", {"email": member.email, "password": member.password}
    )
    expect(
        retry.status in (400, 401) and not retry.tokens() & {"access_token"},
        "a new sign-in is refused",
    )
    if operation == "delete":
        expect(
            DeletionJob.objects.filter(subject_id=member.account_id).exists(), "the deletion job"
        )
        expect(
            DeletionTombstone.objects.filter(subject_id=member.account_id).exists(), "the tombstone"
        )
    return f"{state}: epoch bumped, both layers ended, events written, sign-in refused"


@case("revoke.suspend", "9")
def revoke_suspend(ctx: Context) -> str:
    return _revocation_case(ctx, "suspend", "suspended")


@case("revoke.delete", "9")
def revoke_delete(ctx: Context) -> str:
    return _revocation_case(ctx, "delete", "deletion_pending")


@case("revoke.inside_transaction_refused", "9", "D6")
def revoke_in_transaction(ctx: Context) -> str:
    from django.db import transaction
    from glow_identity import revocation

    member = ctx.member()
    for label, enter in (
        ("an atomic block", lambda: transaction.atomic()),
        ("autocommit off", _autocommit_off),
    ):
        refused = False
        try:
            with enter():
                revocation.suspend_account(member.account_id)
        except revocation.TransactionOpen:
            refused = True
        expect(refused, f"the revocation service refuses inside {label}")
        expect(_account(member.account_id).state == "active", f"nothing ran inside {label}")
        expect(ctx.events(member.account_id, "access_revoked") == 0, "no event")
    expect(_actor(member.device, member.device.access) == 200, "the member's session is untouched")
    return "refused inside an atomic block and with autocommit off; nothing ran"


class _autocommit_off:
    def __enter__(self) -> None:
        from django.db import transaction

        transaction.set_autocommit(False)

    def __exit__(self, *exc: object) -> None:
        from django.db import transaction

        transaction.rollback()
        transaction.set_autocommit(True)


@case("revoke.second_layer_fails_then_repeat", "9", "D6")
def revoke_repeat(ctx: Context) -> str:
    from allauth.usersessions.models import UserSession
    from glow_identity import revocation

    member = ctx.member()
    real_end = UserSession.end
    calls = {"n": 0}

    def failing_once(self: Any) -> None:
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("injected")
        real_end(self)

    failed = False
    with mock.patch.object(UserSession, "end", failing_once):
        try:
            revocation.suspend_account(member.account_id)
        except RuntimeError:
            failed = True
    expect(failed, "the failed second step is an error")
    expect(_account(member.account_id).state == "suspended", "Glow's layer committed first")
    expect(_user_sessions(member.user_id) == 1, "allauth's session is still there")
    expect(_actor(member.device, member.device.access) == 401, "the actor already refuses")
    repeat = revocation.suspend_account(member.account_id)
    expect(repeat.outcome == "no_change", "the repeat is no change at Glow's layer")
    expect(_user_sessions(member.user_id) == 0, "and completes allauth's")
    expect(not ctx.allauth_accepts(member.device.access or ""), "every token stops")
    expect(ctx.events(member.account_id, "access_revoked") == 1, "one access_revoked event")
    return "error, then the repeat completed both layers"


@case("revoke.suspend_after_delete_refused", "9")
def revoke_after_delete(ctx: Context) -> str:
    from glow_identity import revocation

    member = ctx.member()
    expect(revocation.delete_account(member.account_id).outcome == "applied", "deleted")
    events = ctx.event_count()
    outcome = revocation.suspend_account(member.account_id)
    expect(outcome.outcome == "refused", "a deleting account cannot be suspended")
    expect(ctx.event_count() == events, "and nothing more is written")
    return "suspension of a deleting account refused, as reviewed"


# =============================================================================================
# Acceptance check 10: the account-change notices (D8)
# =============================================================================================


@case("notice.email_change", "10", "3")
def notice_email_change(ctx: Context) -> str:
    from allauth.account.models import EmailAddress

    member = ctx.member()
    device = member.device
    new_email = ctx.email()
    ctx.asked_addresses.add(new_email)
    # Correction C1: an address change needs a reauthentication in the same session first.
    expect(ctx.reauthenticate(device, member.password).status == 200, "the member reauthenticates")
    mark = ctx.mail_mark()
    asked = device.app("POST", "account/email", {"email": new_email}, bearer=device.access)
    expect(asked.status == 200, "the change is asked for")
    code = ctx.code_since(mark, new_email)
    verified = device.app("POST", "auth/email/verify", {"key": code}, bearer=device.access)
    expect(verified.status == 200, "the new address is verified by code")
    addresses = list(
        EmailAddress.objects.filter(user_id=member.user_id).values_list(
            "email", "verified", "primary"
        )
    )
    expect(addresses == [(new_email, True, True)], "one address: the new one, verified and primary")
    notices = [
        m
        for m in ctx.mail_since(mark, member.email)
        if m.subject == "Your Glow email address was changed"
    ]
    expect(len(notices) == 1, "one email-changed notice, to the old address")
    expect(new_email not in notices[0].body, "the notice does not name the new address")
    member.email = new_email
    again = ctx.sign_in(member)
    expect(_actor(again, again.access) == 200, "the member signs in with the new address")
    return "verified by code before it replaced the old; the old address told once"


# =============================================================================================
# Acceptance check 11: the rate limits, on failed sign-ins and at the password change (D3)
# =============================================================================================


@case("ratelimit.failed_sign_ins", "11")
def ratelimit_failed(ctx: Context) -> str:
    member = ctx.member()
    device = ctx.device()
    wrong = ctx.password()
    statuses = [
        device.app("POST", "auth/login", {"email": member.email, "password": wrong}).status
        for _ in range(5)
    ]
    expect(statuses == [400] * 5, "five wrong passwords are refused")
    limited = device.app("POST", "auth/login", {"email": member.email, "password": member.password})
    expect(
        limited.status == 400 and not limited.tokens() & {"access_token"}, "the sixth is refused"
    )
    codes = [e.get("code") for e in (limited.body or {}).get("errors", [])]
    expect("too_many_login_attempts" in codes, "by the failed-login limit")
    return "five failures, then refused even with the right password"


@case("ratelimit.password_change", "11", "D3")
def ratelimit_password_change(ctx: Context) -> str:
    """Acceptance check 11's second sentence (correction C2, DM-48 C2.3): five wrong current
    passwords at ``account/password/change``, then the right one, sent more than 60 and less than
    300 seconds after the first of the five by the limiter's clock, is refused as too many, and
    the password is unchanged. allauth's default, 5/m/user, would accept it."""
    from allauth.core.internal import ratelimit

    member = ctx.member()
    device = member.device
    wrong = ctx.password()
    new_password = ctx.password()
    mark = ctx.mail_mark()

    def change(current: str) -> Any:
        return device.app(
            "POST",
            "account/password/change",
            {"current_password": current, "new_password": new_password},
            bearer=device.access,
        )

    started = time.time()  # the limiter's clock: allauth's module reads time.time()
    for attempt in range(1, 6):
        refused = change(wrong)
        expect(
            refused.status == 400 and "enter_current_password" in refused.error_codes(),
            f"wrong current password {attempt} is refused",
        )
        expect(not refused.tokens(), "and carries no credential")
    fifth_done = time.time()
    # The sixth, with the limiter's clock 120 seconds ahead: at least 120 seconds after the
    # first of the five, and the elapsed time is checked to keep it under 300.
    ahead = 120
    before_sixth = time.time()
    with clock_ahead(ratelimit, ahead):
        limited = change(member.password)
    after_sixth = time.time()
    earliest_gap = before_sixth + ahead - fifth_done
    latest_gap = after_sixth + ahead - started
    expect(earliest_gap > 60 and latest_gap < 300, "the sixth is 60 to 300 seconds after the first")
    expect(
        limited.status == 429,
        f"the sixth, with the right password, is refused as too many (answered {limited.status})",
    )
    expect(not limited.error_codes() and not limited.tokens(), "with no error code or credential")
    # The password is unchanged: no notice, the session still valid, the old password signs in.
    expect(
        not [
            m
            for m in ctx.mail_since(mark, member.email)
            if m.subject == "Your Glow password was changed"
        ],
        "no password-changed notice",
    )
    expect(_actor(device, device.access) == 200, "the device's session is not ended")
    again = ctx.sign_in(member)
    expect(_actor(again, again.access) == 200, "the old password still signs in")
    return (
        f"five wrong current passwords refused (400 enter_current_password); the sixth, right,"
        f" {earliest_gap:.0f} to {latest_gap:.0f} s after the first: 429 with no error code;"
        " the old password still signs in"
    )


# =============================================================================================
# Acceptance check 13: reauthentication before an address change (D3; correction C1, DM-47)
# =============================================================================================


@case("reauth.email_change_needs_recent_reauthentication", "13", "10", "D3", "D5")
def reauth_email_change(ctx: Context) -> str:
    from allauth.account.internal.flows import reauthentication
    from allauth.account.models import EmailAddress
    from allauth.usersessions.models import UserSession
    from django.contrib.sessions.models import Session

    member = ctx.member()
    device = ctx.sign_in(member)  # a password sign-in: its own record must not count
    other = ctx.sign_in(member)  # another session of the same account
    new_email = ctx.email()
    ctx.asked_addresses.add(new_email)

    def addresses() -> list[tuple[str, bool, bool]]:
        return sorted(
            EmailAddress.objects.filter(user_id=member.user_id).values_list(
                "email", "verified", "primary"
            )
        )

    start = addresses()
    expect(start == [(member.email, True, True)], "one verified address to start")

    def refused(on: Device, when: str) -> None:
        mark = ctx.mail_mark()
        reply = on.app("POST", "account/email", {"email": new_email}, bearer=on.access)
        expect(reply.status == 401, f"{when}: the change answers 401")
        # allauth's 401 lists the reauthenticate flow, and password_reset_by_code not pending.
        expect("reauthenticate" in reply.flow_ids(), f"{when}: with the reauthenticate flow")
        expect(not reply.pending(), f"{when}: and no pending flow")
        expect(not reply.tokens(), f"{when}: and no credential")
        expect(not ctx.mail_since(mark), f"{when}: no mail is sent")
        expect(addresses() == start, f"{when}: no address changes")
        expect(not EmailAddress.objects.filter(email=new_email).exists(), f"{when}: none is added")

    # Right after sign-in, with no reauthentication.
    refused(device, "right after sign-in")

    # The reauthentication: recorded in the Django session only (D3, D5).
    key = ctx.session_key_of(device.access or "")
    user_session = UserSession.objects.get(session_key=key)
    row = ctx.account_session_of(device.access or "")
    written = (
        _xmin("usersessions_usersession", "id", user_session.pk),
        _xmin("glow_persistence_accountsession", "id", row.pk),
    )
    django_sessions = Session.objects.count()
    pair = (device.access, device.refresh, device.session_token)
    reply = ctx.reauthenticate(device, member.password)
    expect(reply.status == 200, "the right password reauthenticates")
    expect(not reply.tokens(), "no token pair and no session_token")
    expect(set(reply.meta()) == {"is_authenticated"}, "the reply's meta holds no credential")
    expect(
        (device.access, device.refresh, device.session_token) == pair, "the device's tokens stay"
    )
    records = [m for m in (reply.data() or {}).get("methods", []) if m.get("reauthenticated")]
    expect(len(records) == 1, "one reauthentication recorded in the session")
    expect(ctx.session_key_of(device.access or "") == key, "the token names the same key")
    expect(ctx.django_session_exists(key), "the session key is unchanged")
    expect(Session.objects.count() == django_sessions, "no Django session is made or ended")
    expect(ctx.user_session_ref(key) == str(user_session.pk), "the same UserSession row")
    expect(
        (
            _xmin("usersessions_usersession", "id", user_session.pk),
            _xmin("glow_persistence_accountsession", "id", row.pk),
        )
        == written,
        "neither the UserSession row nor the AccountSession is written",
    )
    row.refresh_from_db()
    expect(
        row.state == "valid" and row.auth_session_ref == str(user_session.pk),
        "the AccountSession is unchanged",
    )
    expect(
        _actor(device, device.access) == 200 and ctx.allauth_accepts(device.access or ""),
        "the token still works at both layers",
    )

    # More than 300 seconds after the reauthentication (allauth's clock, moved for its module).
    with clock_ahead(reauthentication, 301):
        refused(device, "301 seconds after the reauthentication")

    # In another session of the same account than the one that reauthenticated.
    refused(other, "in another session")

    # Wrong passwords: refused; the sixth within 300 seconds as too many attempts. The limit is
    # the sign-in form's (login_failed, keyed by the address), so sign-in is held too.
    wrong = ctx.password()
    for attempt in range(1, 6):
        failed = ctx.reauthenticate(other, wrong)
        expect(
            failed.status == 400 and "incorrect_password" in failed.error_codes(),
            f"wrong password {attempt} is refused",
        )
        expect(not failed.tokens(), "and carries no credential")
    sixth = ctx.reauthenticate(other, wrong)
    expect(
        sixth.status == 400 and "too_many_login_attempts" in sixth.error_codes(),
        "the sixth wrong password is refused as too many attempts",
    )
    held = ctx.reauthenticate(other, member.password)
    expect(
        held.status == 400 and "too_many_login_attempts" in held.error_codes(),
        "then the right password is held too",
    )
    signing_in = ctx.device().app(
        "POST", "auth/login", {"email": member.email, "password": member.password}
    )
    expect(
        signing_in.status == 400 and "too_many_login_attempts" in signing_in.error_codes(),
        "and so is the sign-in form: the same login_failed limit",
    )
    refused(other, "after the refused reauthentications")

    # With the right password, the change goes ahead, as acceptance check 10's notice shows.
    ctx.clear_rate_limits()  # as if the limits' window had passed
    expect(ctx.reauthenticate(device, member.password).status == 200, "reauthenticated again")
    mark = ctx.mail_mark()
    asked = device.app("POST", "account/email", {"email": new_email}, bearer=device.access)
    expect(asked.status == 200, "the change goes ahead")
    code = ctx.code_since(mark, new_email)
    verified = device.app("POST", "auth/email/verify", {"key": code}, bearer=device.access)
    expect(verified.status == 200, "the new address is verified by code")
    expect(addresses() == [(new_email, True, True)], "one address: the new one")
    notices = [
        m
        for m in ctx.mail_since(mark, member.email)
        if m.subject == "Your Glow email address was changed"
    ]
    expect(len(notices) == 1, "one email-changed notice, to the old address")
    return (
        "refused with the reauthenticate flow after sign-in, after 301 s and in another session;"
        " wrong passwords refused, the sixth as too many; the key, UserSession and AccountSession"
        " unchanged, no credential returned; then the change went ahead"
    )


# =============================================================================================
# Acceptance checks 3 and 12: the mail and the output (run last)
# =============================================================================================


@case("mail.no_link_no_stranger", "3", "D8")
def mail_check(ctx: Context) -> str:
    from allauth.account.models import EmailAddress
    from glow_identity import mail

    messages = mail.outbox()
    expect(messages, "the run sent mail")
    owners = set(EmailAddress.objects.values_list("email", flat=True)) | ctx.account_addresses
    expect(ctx.issued_codes, "the run recorded the codes it issued")
    for message in messages:
        text = message.subject + "\n" + message.body
        # Correction C2 (DM-48 C2.5): the exact codes issued are removed first, and only they.
        found = mail_forbidden_found(text, ctx.issued_codes)
        expect(not found, "no link and no name but Glow's")
        expect("glow" in text.lower(), "Glow's name")
        expect(len(message.to) == 1, "one recipient")
        recipient = message.to[0]
        expect(recipient not in ctx.unknown_addresses, "no mail to an address with no account")
        expect(recipient in owners or recipient in ctx.asked_addresses, "no mail to a stranger")
    return f"{len(messages)} messages: no link, Glow's name only, each to its owner"


def run_case(ctx: Context, entry: Case) -> tuple[bool, str]:
    from django.core.cache import cache

    cache.clear()
    ctx.case_id = entry.case_id
    try:
        # Correction C2: each code is recorded where allauth's adapter issues it, for the
        # no-link check, and joins the ledger.
        with recording_issued_codes(ctx):
            return True, entry.run(ctx)
    except CaseFailed as failed:
        return False, f"FAILED: {failed}"
    except BaseException as exc:  # noqa: BLE001 - recorded by type only; never a value
        return False, f"ERROR: {type(exc).__name__}"


def plan() -> tuple[str, ...]:
    return tuple(entry.case_id for entry in CASES)


_ = threading  # the lock case's workers are threads (concurrency.Worker)
