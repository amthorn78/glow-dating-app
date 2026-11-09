"""SV1's identity slice, the parts that need no database (its brief's D2, D3, D5, D7, D8, D9).

Each Django-dependent check runs in a fresh process under ``tests.identity_offline_settings``
(the identity fragment with Django's dummy backend and keys generated for that process). The
identity cases themselves (sign-up, verification, sessions, revocation, at both layers) run on
a disposable PostgreSQL in ``proofs/postgres-ordering``'s identity suite, through the HTTP
endpoints.
"""

import ast
import importlib.util
import json
import os
import subprocess
import sys
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from glow_domain.identity import (
    AccountId,
    AgeAssurance,
    AgeAssuranceMethod,
    AgeAssuranceState,
    unknown_age_assurance,
)
from glow_identity import access

API_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = API_ROOT.parents[1]
IDENTITY = API_ROOT / "glow_identity"


def contract_runtime():
    spec = importlib.util.spec_from_file_location(
        "glow_contract_runtime", REPO_ROOT / "packages" / "contracts" / "runtime.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def under_identity_settings(code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", "import django\ndjango.setup()\n" + code],
        cwd=API_ROOT,
        env={
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LANG": "C.UTF-8",
            "DJANGO_SETTINGS_MODULE": "tests.identity_offline_settings",
        },
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


class AccountAccessContractTests(unittest.TestCase):
    """Outcome 5: the builders the view serves validate with the contract's own validator."""

    def test_every_state_validates_as_the_contract_defines_it(self) -> None:
        runtime = contract_runtime()
        account_id = uuid4()
        for state in access.ACCOUNT_STATES:
            for session_state in access.SESSION_STATES:
                with self.subTest(state=state, session_state=session_state):
                    data = access.account_access(account_id, 3, state, session_state)
                    body = access.app_response(data, access.new_request_id())
                    self.assertTrue(runtime.valid("production", "AppResponse", body))
                    self.assertTrue(runtime.valid("production", "AccountAccess", data))
                    self.assertEqual(data["account_id"], str(account_id))

    def test_errors_validate_and_name_no_value(self) -> None:
        runtime = contract_runtime()
        for code in ("unauthenticated", "invalid_request"):
            with self.subTest(code=code):
                body = access.error(code, access.new_request_id())
                self.assertTrue(runtime.valid("production", "Error", body))
                self.assertEqual(set(body), {"contract_version", "request_id", "code", "retryable"})

    def test_a_state_the_contract_does_not_name_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            access.account_access(uuid4(), 1, "verified", "valid")
        with self.assertRaises(ValueError):
            access.account_access(uuid4(), 1, "active", "current")


class AgeAssuranceTests(unittest.TestCase):
    """D9: the age state's type; sign-up records unknown."""

    def test_unknown_has_no_method_and_no_policy_version(self) -> None:
        assurance = unknown_age_assurance(AccountId(str(uuid4())), datetime.now(UTC))
        self.assertIs(assurance.state, AgeAssuranceState.UNKNOWN)
        self.assertIs(assurance.method, AgeAssuranceMethod.NONE)
        self.assertIsNone(assurance.policy_version)

    def test_each_state_names_the_methods_that_may_set_it(self) -> None:
        now, account = datetime.now(UTC), AccountId(str(uuid4()))
        with self.assertRaises(ValueError):
            AgeAssurance(
                account, AgeAssuranceState.UNKNOWN, AgeAssuranceMethod.SELF_DECLARATION, now, None
            )
        with self.assertRaises(ValueError):
            AgeAssurance(
                account,
                AgeAssuranceState.SELF_DECLARED_ADULT,
                AgeAssuranceMethod.NONE,
                now,
                "policy-1",
            )
        with self.assertRaises(ValueError):
            AgeAssurance(
                account, AgeAssuranceState.UNKNOWN, AgeAssuranceMethod.NONE, now, "policy-1"
            )
        with self.assertRaises(ValueError):
            AgeAssurance(
                account,
                AgeAssuranceState.SELF_DECLARED_ADULT,
                AgeAssuranceMethod.SELF_DECLARATION,
                now,
                None,
            )
        with self.assertRaises(ValueError):
            AgeAssurance(
                account,
                AgeAssuranceState.UNKNOWN,
                AgeAssuranceMethod.NONE,
                datetime.now() + timedelta(0),  # naive
                None,
            )
        recorded = AgeAssurance(
            account,
            AgeAssuranceState.SELF_DECLARED_ADULT,
            AgeAssuranceMethod.SELF_DECLARATION,
            now,
            "policy-1",
        )
        self.assertEqual(recorded.policy_version, "policy-1")

    def test_the_type_holds_no_birth_date(self) -> None:
        self.assertEqual(
            set(AgeAssurance.__dataclass_fields__),
            {"account_id", "state", "method", "recorded_at", "policy_version"},
        )


class SettingsFragmentTests(unittest.TestCase):
    """D2, D3, D5 and D8: the fragment's values, as the brief states them."""

    def test_the_briefed_values(self) -> None:
        from glow_identity import conf

        settings = conf.settings()
        expected = {
            "ACCOUNT_LOGIN_METHODS": {"email"},
            "ACCOUNT_SIGNUP_FIELDS": ["email*", "password1*"],
            "ACCOUNT_UNIQUE_EMAIL": True,
            "ACCOUNT_EMAIL_VERIFICATION": "mandatory",
            "ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED": True,
            "ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED": True,
            "ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS": False,
            "ACCOUNT_PREVENT_ENUMERATION": True,
            "ACCOUNT_CHANGE_EMAIL": True,
            "ACCOUNT_REAUTHENTICATION_REQUIRED": True,
            "ACCOUNT_EMAIL_NOTIFICATIONS": True,
            "ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE": True,
            "ACCOUNT_LOGIN_BY_CODE_ENABLED": False,
            # D3 (correction C2, DM-48): the one rate limit SV1 changes.
            "ACCOUNT_RATE_LIMITS": {"change_password": "5/300s/user"},
            "HEADLESS_ONLY": True,
            "HEADLESS_CLIENTS": ("app",),
            "HEADLESS_SERVE_SPECIFICATION": False,
            "HEADLESS_TOKEN_STRATEGY": "glow_identity.strategy.GlowJWTTokenStrategy",
            "HEADLESS_JWT_ALGORITHM": "RS256",
            "HEADLESS_JWT_ACCESS_TOKEN_EXPIRES_IN": 300,
            "HEADLESS_JWT_REFRESH_TOKEN_EXPIRES_IN": 2_592_000,
            "HEADLESS_JWT_STATEFUL_VALIDATION_ENABLED": True,
            "HEADLESS_JWT_ROTATE_REFRESH_TOKEN": True,
            "USERSESSIONS_ADAPTER": "glow_identity.sessions.GlowUserSessionsAdapter",
            "USERSESSIONS_TRACK_ACTIVITY": False,
            "EMAIL_BACKEND": "glow_identity.mail.FixtureEmailBackend",
            "SESSION_ENGINE": "django.contrib.sessions.backends.db",
            "GLOW_IDENTITY_SESSION_LIFETIME": timedelta(days=30),
        }
        for name, value in expected.items():
            with self.subTest(setting=name):
                self.assertEqual(settings[name], value)
        validators = {
            entry["NAME"].rsplit(".", 1)[1] for entry in settings["AUTH_PASSWORD_VALIDATORS"]
        }
        self.assertEqual(
            validators,
            {
                "UserAttributeSimilarityValidator",
                "MinimumLengthValidator",
                "CommonPasswordValidator",
                "NumericPasswordValidator",
            },
        )
        minimum = settings["AUTH_PASSWORD_VALIDATORS"][1]
        self.assertEqual(minimum["OPTIONS"], {"min_length": 10})
        self.assertNotIn("PASSWORD_HASHERS", settings)  # Django's own list (D3)
        # D3 (correction C1): allauth's default window, 300 seconds, is not overridden.
        self.assertNotIn("ACCOUNT_REAUTHENTICATION_TIMEOUT", settings)

    def test_the_password_change_limit_merges_into_allauths_defaults(self) -> None:
        # D3 (correction C2, DM-48): allauth resolves change_password as 5 per 300 seconds per
        # account, and every other limit keeps allauth's own default, read from the installed
        # release with the override taken away.
        result = under_identity_settings(
            "from django.test import override_settings\n"
            "from allauth.account import app_settings as account\n"
            "from allauth.core.internal.ratelimit import parse_rates\n"
            "resolved = dict(account.RATE_LIMITS)\n"
            "with override_settings(ACCOUNT_RATE_LIMITS={}):\n"
            "    defaults = dict(account.RATE_LIMITS)\n"
            "assert defaults['change_password'] == '5/m/user', defaults['change_password']\n"
            "assert resolved['change_password'] == '5/300s/user', resolved['change_password']\n"
            "rate, = parse_rates(resolved['change_password'])\n"
            "assert (rate.amount, rate.duration, rate.per) == (5, 300, 'user'), rate\n"
            "assert set(resolved) == set(defaults), sorted(set(resolved) ^ set(defaults))\n"
            "changed = sorted(k for k in defaults if resolved[k] != defaults[k])\n"
            "assert changed == ['change_password'], changed\n"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_the_fragment_holds_no_key_password_connection_or_provider(self) -> None:
        from glow_identity import conf

        settings = conf.settings()
        for name in settings:
            with self.subTest(setting=name):
                self.assertNotIn(name, ("SECRET_KEY", "HEADLESS_JWT_PRIVATE_KEY", "DATABASES"))
                self.assertFalse(name.startswith("EMAIL_HOST"), name)
                self.assertNotIn("FRONTEND_URLS", name)
                self.assertFalse(name.startswith("SOCIALACCOUNT"), name)
                self.assertFalse(name.startswith("MFA_"), name)
        for app in ("allauth.socialaccount", "allauth.mfa"):
            self.assertNotIn(app, settings["INSTALLED_APPS"])

    def test_a_copy_is_independent(self) -> None:
        from glow_identity import conf

        copied = conf.settings()
        copied["INSTALLED_APPS"].append("not.an.app")
        self.assertNotIn("not.an.app", conf.settings()["INSTALLED_APPS"])


class IdentityUnderItsSettingsTests(unittest.TestCase):
    """The parts that need Django's registry, each in a fresh process."""

    def run_checks(self, code: str) -> None:
        result = under_identity_settings(code)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_the_routes_are_allauths_app_routes_and_one_glow_route(self) -> None:
        result = under_identity_settings(
            "import json\n"
            "from django.urls import get_resolver\n"
            "def walk(ps, prefix=''):\n"
            "    for p in ps:\n"
            "        if hasattr(p, 'url_patterns'):\n"
            "            yield from walk(p.url_patterns, prefix + str(p.pattern))\n"
            "        else:\n"
            "            yield prefix + str(p.pattern)\n"
            "print(json.dumps(sorted(walk(get_resolver().url_patterns))))\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        routes = json.loads(result.stdout.strip().splitlines()[-1])
        app = [r.removeprefix("_allauth/app/v1/") for r in routes if r.startswith("_allauth/")]
        self.assertTrue(all(r.startswith("_allauth/app/v1/") for r in routes if "allauth" in r))
        self.assertEqual(
            sorted(app),
            sorted(
                [
                    "account/email",
                    "account/password/change",
                    "account/phone",
                    "auth/code/confirm",
                    "auth/email/verify",
                    "auth/email/verify/resend",
                    "auth/login",
                    "auth/password/request",
                    "auth/password/reset",
                    "auth/phone/verify",
                    "auth/phone/verify/resend",
                    "auth/reauthenticate",
                    "auth/session",
                    "auth/sessions",
                    "auth/signup",
                    "config",
                    "tokens/refresh",
                ]
            ),
        )
        self.assertEqual(
            [r for r in routes if not r.startswith("_allauth/")], ["api/v1/account/access"]
        )

    def test_every_message_is_glows_plain_text_with_no_link(self) -> None:
        self.run_checks(
            "from glow_identity import messages\n"
            "context = {'code': 'BCDF-GHJK', 'timestamp': 'now', 'ip': '203.0.113.9',\n"
            "    'user_agent': 'agent/1', 'from_email': 'old@example.invalid',\n"
            "    'to_email': 'new@example.invalid', 'deleted_email': 'gone@example.invalid',\n"
            "    'signup_url': 'https://x.invalid/s', 'password_reset_url': 'https://x.invalid/r'}\n"
            "for prefix in sorted(messages.WORDED):\n"
            "    m = messages.render(prefix, context)\n"
            "    text = (m.subject + '\\n' + m.body)\n"
            "    low = text.lower()\n"
            "    assert '\\n' not in m.subject, prefix\n"
            "    assert 'glow' in low, prefix\n"
            "    for bad in ('http', '://', 'www.', 'href', '<', 'allauth', 'django',\n"
            "                'example.invalid', '203.0.113.9', 'agent/1'):\n"
            "        assert bad not in low, (prefix, bad)\n"
            "    if 'code' in prefix or 'confirmation' in prefix:\n"
            "        assert 'BCDF-GHJK' in m.body, prefix\n"
            "    else:\n"
            "        assert 'BCDF-GHJK' not in m.body, prefix\n"
            "verify = messages.render('account/email/email_confirmation', context)\n"
            "assert '15 minutes' in verify.body\n"
            "reset = messages.render('account/email/password_reset_code', context)\n"
            "assert '3 minutes' in reset.body\n"
            "for refused in ('account/email/unknown_account', 'account/email/password_reset_key',\n"
            "                'account/email/login_code', 'not/a/message'):\n"
            "    try:\n"
            "        messages.render(refused, context)\n"
            "    except messages.UnwordedMessage:\n"
            "        pass\n"
            "    else:\n"
            "        raise AssertionError(refused)\n"
            "try:\n"
            "    messages.render('account/email/password_reset_code', {})\n"
            "except messages.UnwordedMessage:\n"
            "    pass\n"
            "else:\n"
            "    raise AssertionError('a code message without its code')\n"
        )

    def test_glow_words_every_account_mail_sv1_can_send(self) -> None:
        # Each of allauth's account mails at the pinned release is worded by Glow, or is one SV1
        # cannot send: the unknown-account mail (off), the reset link (codes only), the login
        # code (off), the two base templates, and email_confirm, which no code path sends.
        self.run_checks(
            "from pathlib import Path\n"
            "import allauth\n"
            "from glow_identity import messages\n"
            "root = Path(allauth.__file__).parent / 'templates'\n"
            "allauths = {str(p.relative_to(root)).removesuffix('_subject.txt')\n"
            "    for p in (root / 'account' / 'email').glob('*_subject.txt')}\n"
            "assert messages.WORDED <= allauths, sorted(messages.WORDED - allauths)\n"
            "never = {'account/email/unknown_account', 'account/email/password_reset_key',\n"
            "    'account/email/login_code', 'account/email/base_message',\n"
            "    'account/email/base_notification', 'account/email/email_confirm'}\n"
            "unworded = allauths - messages.WORDED\n"
            "assert unworded <= never, sorted(unworded - never)\n"
        )

    def test_the_fixture_backend_records_and_opens_no_connection(self) -> None:
        self.run_checks(
            "import socket\n"
            "from unittest import mock\n"
            "from django.core import mail as django_mail\n"
            "from django.core.mail import EmailMessage, EmailMultiAlternatives\n"
            "from glow_identity import mail\n"
            "net = AssertionError('network')\n"
            "blocked = mock.patch.object(socket.socket, 'connect', side_effect=net)\n"
            "with blocked, mock.patch('socket.create_connection', side_effect=net):\n"
            "    sent = EmailMessage('s', 'b', 'Glow <no-reply@example.invalid>',\n"
            "        ['someone@example.invalid']).send()\n"
            "    assert sent == 1\n"
            "    assert mail.outbox()[-1].to == ('someone@example.invalid',)\n"
            "    for message in (\n"
            "        EmailMessage('s', 'b', 'f@example.invalid', ['a@example.invalid'],\n"
            "            cc=['c@example.invalid']),\n"
            "        EmailMultiAlternatives('s', 'b', 'f@example.invalid', ['a@example.invalid'],\n"
            "            alternatives=[('<p>b</p>', 'text/html')]),\n"
            "    ):\n"
            "        try:\n"
            "            message.send()\n"
            "        except mail.RefusedMessage:\n"
            "            pass\n"
            "        else:\n"
            "            raise AssertionError('not refused')\n"
            "    html = EmailMessage('s', '<p>b</p>', 'f@example.invalid', ['a@example.invalid'])\n"
            "    html.content_subtype = 'html'\n"
            "    try:\n"
            "        html.send()\n"
            "    except mail.RefusedMessage:\n"
            "        pass\n"
            "    else:\n"
            "        raise AssertionError('html not refused')\n"
            "assert len(mail.outbox()) == 1\n"
            "mail.clear()\n"
            "assert mail.outbox() == ()\n"
            "from django.conf import settings\n"
            "assert settings.EMAIL_BACKEND == 'glow_identity.mail.FixtureEmailBackend'\n"
        )

    def test_the_username_is_opaque(self) -> None:
        self.run_checks(
            "import re\n"
            "from django.contrib.auth.validators import UnicodeUsernameValidator\n"
            "from glow_identity.adapter import opaque_username\n"
            "names = {opaque_username() for _ in range(50)}\n"
            "assert len(names) == 50\n"
            "for name in names:\n"
            "    assert re.fullmatch(r'g[0-9a-f]{32}', name), name\n"
            "    UnicodeUsernameValidator()(name)\n"
            "    assert len(name) <= 150\n"
        )

    def test_the_replay_check_reads_no_session_before_allauths_own_checks(self) -> None:
        # D2 with DM-46's N2: a refresh token is a replay only after allauth's own checks, its
        # signature first. A forged, unsigned, expired or wrong-type token is refused before
        # any session is looked up (here, any database access fails the run); a validly signed
        # refresh token goes on to the session lookup.
        self.run_checks(
            "import time\n"
            "import jwt\n"
            "from cryptography.hazmat.primitives.asymmetric import rsa\n"
            "from allauth.headless.tokens.strategies.jwt import internal\n"
            "from glow_persistence.static_check import no_database_access\n"
            "from glow_identity.strategy import replayed_session_key\n"
            "sid = internal.session_key_to_sid('k' * 32)\n"
            "now = int(time.time())\n"
            "claims = {'iat': now, 'exp': now + 600, 'sid': sid, 'jti': 'j',\n"
            "    'token_use': 'refresh', 'sub': '1'}\n"
            "other = rsa.generate_private_key(public_exponent=65537, key_size=2048)\n"
            "forged = jwt.encode(claims, other, algorithm='RS256')\n"
            "unsigned = jwt.encode(claims, '', algorithm='none')\n"
            "expired, _ = internal.create_token('refresh', sub='1', sid=sid, expires_in=-60)\n"
            "access, _ = internal.create_token('access', sub='1', sid=sid, expires_in=600)\n"
            "with no_database_access():\n"
            "    for token in (forged, unsigned, expired, access, 'not-a-token'):\n"
            "        assert replayed_session_key(token) is None\n"
            "    valid, _ = internal.create_token('refresh', sub='1', sid=sid, expires_in=600)\n"
            "    try:\n"
            "        replayed_session_key(valid)\n"
            "    except Exception as exc:  # the dummy backend: the lookup reached the database\n"
            "        assert type(exc).__name__ in ('AssertionError', 'ImproperlyConfigured'), exc\n"
            "    else:\n"
            "        raise AssertionError('a valid token goes on to the session lookup')\n"
        )

    def test_the_strategy_and_adapters_are_allauths_own_with_glows_additions(self) -> None:
        self.run_checks(
            "from allauth.account.adapter import DefaultAccountAdapter\n"
            "from allauth.headless import app_settings as headless\n"
            "from allauth.headless.tokens.strategies.jwt import JWTTokenStrategy\n"
            "from allauth.usersessions.adapter import DefaultUserSessionsAdapter, get_adapter\n"
            "from allauth.account.adapter import get_adapter as get_account_adapter\n"
            "from glow_identity.adapter import GlowAccountAdapter\n"
            "from glow_identity.sessions import GlowUserSessionsAdapter\n"
            "from glow_identity.strategy import GlowJWTTokenStrategy\n"
            "assert isinstance(headless.TOKEN_STRATEGY, GlowJWTTokenStrategy)\n"
            "assert issubclass(GlowJWTTokenStrategy, JWTTokenStrategy)\n"
            "added = {name for name in vars(GlowJWTTokenStrategy) if not name.startswith('_')}\n"
            "assert added == {'refresh_token'}, added\n"
            "assert isinstance(get_adapter(), GlowUserSessionsAdapter)\n"
            "assert issubclass(GlowUserSessionsAdapter, DefaultUserSessionsAdapter)\n"
            "assert isinstance(get_account_adapter(), GlowAccountAdapter)\n"
            "assert issubclass(GlowAccountAdapter, DefaultAccountAdapter)\n"
            "assert not get_account_adapter()._has_phone_impl\n"
        )

    def test_an_address_change_needs_a_recent_reauthentication(self) -> None:
        # D3 (correction C1, DM-47): the setting is on, the window is allauth's 300 seconds, and
        # Glow's adapter leaves allauth's reauthentication and its password check alone, so a
        # wrong password at auth/reauthenticate consumes the sign-in form's login_failed limit.
        self.run_checks(
            "from allauth.account import app_settings as account\n"
            "from allauth.account.adapter import get_adapter\n"
            "from glow_identity.adapter import GlowAccountAdapter\n"
            "assert account.REAUTHENTICATION_REQUIRED is True\n"
            "assert account.REAUTHENTICATION_TIMEOUT == 300\n"
            "assert get_adapter().is_reauthentication_required(app='allauth.account') is True\n"
            "kept = ('reauthenticate', 'authenticate', 'pre_authenticate',\n"
            "        'is_reauthentication_required')\n"
            "overridden = [name for name in kept if name in vars(GlowAccountAdapter)]\n"
            "assert not overridden, overridden\n"
        )


class StaticGuardTests(unittest.TestCase):
    """Source checks behind D5, D6 and acceptance check 12; the proof shows the behavior."""

    def module(self, name: str) -> ast.Module:
        return ast.parse((IDENTITY / f"{name}.py").read_text(encoding="utf-8"))

    @staticmethod
    def code_of(path: Path) -> str:
        """A module's code with its docstrings and comments left out."""
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            body = getattr(node, "body", None)
            if (
                isinstance(body, list)
                and body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                body[0] = ast.Pass()
        return ast.unparse(tree)

    def test_the_actor_takes_the_session_from_the_tokens_own_sid(self) -> None:
        code = self.code_of(IDENTITY / "authentication.py")
        self.assertIn("session_key_from_sid", code)
        self.assertIn("JWTTokenAuthentication", code)
        for forbidden in (
            "session-token",
            "Session-Token",
            "SESSION_TOKEN",
            "get_session_token",
            "request.data",
            "request.headers",
            "request.META",
            # Correction C2 (F-5): the query, the form body, the cookies and the session key.
            "request.query_params",
            "request.GET",
            "request.POST",
            "request.COOKIES",
            "session_token",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, code)

    def test_the_actor_is_built_from_the_user_and_the_validated_payload_only(self) -> None:
        # Correction C2 (F-5): actor_for is called once, with exactly ``user, payload``.
        calls = [
            node
            for node in ast.walk(self.module("authentication"))
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "actor_for"
        ]
        self.assertEqual(len(calls), 1)
        self.assertEqual([ast.unparse(argument) for argument in calls[0].args], ["user", "payload"])
        self.assertEqual(calls[0].keywords, [])

    def test_the_request_reaches_only_allauths_authentication(self) -> None:
        # Correction C2 (DM-48 C2.7): on the module's syntax tree, authentication.py's code uses
        # ``request`` only as the parameter of ``authenticate`` and ``authenticate_header``, and
        # as the argument it passes to allauth's JWTTokenAuthentication methods of the same
        # names. Any other use (an attribute, getattr, another call, an alias) fails.
        tree = self.module("authentication")
        parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}

        def enclosing_function(node: ast.AST) -> str | None:
            while node in parents:
                node = parents[node]
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    return node.name
            return None

        def passed_to_allauth(name: ast.Name) -> bool:
            call = parents.get(name)
            if not (isinstance(call, ast.Call) and call.args == [name] and not call.keywords):
                return False
            method = call.func
            return (
                isinstance(method, ast.Attribute)
                and method.attr == enclosing_function(name)
                and isinstance(method.value, ast.Call)
                and ast.unparse(method.value) == "JWTTokenAuthentication()"
            )

        allowed = {"authenticate", "authenticate_header"}
        parameters: list[str] = []
        arguments: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.arg) and node.arg == "request":
                function = enclosing_function(node)
                with self.subTest(parameter_in=function, line=node.lineno):
                    self.assertIn(function, allowed)
                parameters.append(str(function))
            elif isinstance(node, ast.Name) and node.id == "request":
                with self.subTest(use=ast.unparse(parents.get(node, node)), line=node.lineno):
                    self.assertIsInstance(node.ctx, ast.Load)
                    self.assertTrue(passed_to_allauth(node))
                arguments.append(str(enclosing_function(node)))
            elif isinstance(node, ast.Attribute) and node.attr == "request":
                with self.subTest(attribute=ast.unparse(node), line=node.lineno):
                    self.fail("no attribute named request")
        self.assertEqual(sorted(parameters), sorted(allowed))
        self.assertEqual(sorted(arguments), sorted(allowed))

    def test_every_revocation_entry_refuses_an_open_transaction(self) -> None:
        guarded = {
            "mark_verified",
            "open_sign_in_session",
            "sign_out_current_session",
            "sign_out_account",
            "end_user_session",
            "end_replayed_session",
            "expire_found",
            "_revoke_account",
        }
        found = set()
        for node in self.module("revocation").body:
            if isinstance(node, ast.FunctionDef) and node.name in guarded:
                body = (
                    node.body[1:]
                    if isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    else node.body
                )
                first = body[0]
                with self.subTest(function=node.name):
                    self.assertIsInstance(first, ast.Expr)
                    self.assertIsInstance(first.value, ast.Call)
                    self.assertEqual(ast.unparse(first.value), "require_no_transaction()")
                found.add(node.name)
        self.assertEqual(found, guarded)

    def test_no_log_line_carries_a_value(self) -> None:
        # Acceptance check 12, at the source: a log call's arguments after its message are an
        # outcome or a reason code only, never a key, token, code, password or address.
        for path in sorted(IDENTITY.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "logger"
                ):
                    with self.subTest(module=path.name, line=node.lineno):
                        self.assertIsInstance(node.args[0], ast.Constant)
                        for argument in node.args[1:]:
                            self.assertIn(
                                ast.unparse(argument),
                                {"reason", "outcome.outcome", "retried.outcome", "result.reason"},
                            )
                        self.assertFalse(node.keywords)

    def test_no_atomic_requests(self) -> None:
        for path in sorted(IDENTITY.glob("*.py")):
            with self.subTest(module=path.name):
                self.assertNotIn("ATOMIC_REQUESTS", self.code_of(path))


if __name__ == "__main__":
    unittest.main()
