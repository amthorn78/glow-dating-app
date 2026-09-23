"""Structural P02 regression cases; every registry is an isolated process.

These cases test the declared migration/field design, never SQL enforcement.
The fixture API's installed apps and test runner remain database-independent.
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]


class StaticModelDefinitionTests(unittest.TestCase):
    def check_script(self, assertions):
        prelude = """
from glow_persistence.static_check import no_database_access, setup_static_registry
from django.db import models, connections
from django.db.migrations.loader import MigrationLoader
from django.apps import apps
with no_database_access():
    setup_static_registry()
    from glow_persistence import models as m
"""
        body = "\n".join("    " + line for line in assertions.splitlines())
        result = subprocess.run(
            [sys.executable, "-c", prelude + body],
            cwd=API_ROOT,
            env={**os.environ, "GLOW_ENV": "test"},
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_model_and_migration_state_have_no_drift_without_a_database(self):
        self.check_script("""
from glow_persistence.static_check import inspect_definitions
loader, state = inspect_definitions()
assert loader.connection is None
assert not loader.applied_migrations
assert len([key for key in state.models if key[0] == 'glow_persistence']) == 32
assert connections['default'].connection is None
""")

    def test_outbox_is_dependency_before_every_app_domain_table(self):
        self.check_script("""
loader = MigrationLoader(None)
from django.db.migrations.operations.models import CreateModel
infra = loader.disk_migrations[('glow_persistence', '0001_event_infrastructure')]
domain = loader.disk_migrations[('glow_persistence', '0002_app_domain')]
assert ('glow_persistence', '0001_event_infrastructure') in domain.dependencies
assert {op.name for op in infra.operations if isinstance(op, CreateModel)} == {
    'OutboxEvent', 'WebhookInbox'}
assert all(type(op).__name__ in {'CreateModel', 'AddField', 'AddIndex', 'AddConstraint'}
    for migration in (infra, domain) for op in migration.operations)
assert m.OutboxEvent._meta.get_field('dedup_key').unique
assert any(c.name == 'inbox_event' for c in m.WebhookInbox._meta.constraints)
""")

    def test_auth_is_maintained_and_app_identity_is_separate(self):
        self.check_script("""
from django.contrib.auth.models import User
assert m.AppAccount._meta.get_field('auth_user').remote_field.model is User
assert m.AppAccount._meta.get_field('auth_user').one_to_one
assert isinstance(m.AppAccount._meta.pk, models.UUIDField)
assert m.AppAccount._meta.get_field('auth_user').remote_field.on_delete is models.PROTECT
assert not {'password', 'email', 'access_token', 'refresh_token'} & {
    f.name for f in m.AppAccount._meta.fields}
assert 'auth_session_ref' in {f.name for f in m.AccountSession._meta.fields}
assert m.Entitlement._meta.get_field('state').choices == [('disabled', 'disabled')]
""")

    def test_deletion_tombstones_and_safety_do_not_cascade_with_account(self):
        self.check_script("""
assert not any(f.is_relation and f.remote_field.model is m.AppAccount
    for f in m.DeletionTombstone._meta.fields)
assert m.DeletionTombstone._meta.get_field('subject_id').unique
assert m.DeletionTombstone._meta.get_field('deletion').remote_field.on_delete is models.PROTECT
assert m.DeletionJob._meta.get_field('account').remote_field.on_delete is models.SET_NULL
assert m.SafetyReport._meta.get_field('subject').remote_field.on_delete is models.SET_NULL
assert m.SafetyReport._meta.get_field('reporter').remote_field.on_delete is models.SET_NULL
assert m.ProviderLifecycleStep._meta.get_field('deletion').remote_field.on_delete is models.PROTECT
assert any(c.name == 'provider_step_evidence' for c in m.ProviderLifecycleStep._meta.constraints)
assert any(c.name == 'provider_step_one_job' for c in m.ProviderLifecycleStep._meta.constraints)
""")

    def test_pair_uniqueness_direction_and_version_counters_are_explicit(self):
        self.check_script("""
def constraint(model, name):
    return next(c for c in model._meta.constraints if c.name == name)
assert constraint(m.Match, 'match_pair').fields == ('account_low', 'account_high')
assert constraint(m.Match, 'match_order').condition.children == [
    ('account_low__lt', models.F('account_high'))]
assert constraint(m.Block, 'directional_block_pair').fields == ('actor', 'target')
assert constraint(m.DirectionalInteraction, 'directional_interaction_pair').fields == (
    'actor', 'target')
fields = constraint(m.CompatibilitySnapshot, 'snapshot_directional_revision').fields
assert fields[:2] == ('viewer', 'candidate')
assert 'viewer_mapping_version' in fields and 'candidate_mapping_version' in fields
for role in ('viewer', 'candidate'):
    for key in ('eligibility_version', 'preferences_version', 'blocks_version'):
        assert role + '_' + key in fields
for name in ('eligibility_version', 'preferences_version', 'blocks_version', 'session_epoch'):
    assert m.AppAccount._meta.get_field(name).default == 1
assert m.PolicyRevision._meta.get_field('name').unique
""")

    def test_missing_birth_time_and_bounded_candidates_use_field_validation(self):
        self.check_script("""
from django.core.exceptions import ValidationError
def rejected(field, value):
    try:
        field.clean(value, None)
    except ValidationError:
        return True
    return False
assert m.BirthInput._meta.get_field('local_time').null
assert m.BirthInput._meta.get_field('timezone_name').null
assert not m.BirthInput._meta.get_field('birth_date').null
assert m.EngineIdentity._meta.get_field('engine_reference').null
assert not m.EngineIdentity._meta.get_field('engine_reference').unique
assert rejected(m.RecommendationBatch._meta.get_field('limit'), 0)
assert rejected(m.RecommendationBatch._meta.get_field('limit'), 101)
assert not rejected(m.RecommendationBatch._meta.get_field('limit'), 100)
assert rejected(m.RecommendationEntry._meta.get_field('position'), 100)
assert rejected(m.Entitlement._meta.get_field('state'), 'active')
""")

    def test_model_registry_does_not_leak_into_fixture_runtime(self):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import django; django.setup(); "
                "from django.apps import apps; from django.db import connections; "
                "assert not apps.is_installed('glow_persistence'); "
                "assert connections['default'].connection is None",
            ],
            cwd=API_ROOT,
            env={**os.environ, "GLOW_ENV": "test", "DJANGO_SETTINGS_MODULE": "glow_api.settings"},
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_valid_wire_text_bounds_fit_storage_definitions(self):
        self.check_script("""
import json
from pathlib import Path
defs = json.loads((Path.cwd().parents[1] / 'packages/contracts/production/'
    'gapp-api-v1.schema.json').read_text())['$defs']
def text_bound(schema):
    if '$ref' in schema:
        assert schema['$ref'].startswith('#/$defs/')
        return text_bound(defs[schema['$ref'].removeprefix('#/$defs/')])
    if 'anyOf' in schema:
        return max(text_bound(branch) for branch in schema['anyOf'])
    if 'const' in schema:
        assert isinstance(schema['const'], str)
        return len(schema['const'])
    assert schema.get('type') == 'string', 'Unexpected non-text storage contract'
    assert 'maxLength' in schema, 'Unbounded text cannot fit a bounded storage field'
    return schema['maxLength']
for model, field, contract, property_name in (
    (m.ConsentDecision, 'policy_version', 'ConsentIntent', 'policy_version'),
    (m.Preferences, 'policy_version', 'PreferencesIntent', 'policy_version'),
    (m.Profile, 'display_name', 'ProfileIntent', 'display_name'),
    (m.Profile, 'bio', 'ProfileIntent', 'summary'),
    (m.BirthInput, 'place_label', 'BirthInput', 'place_label'),
    (m.SafetyReport, 'reason_code', 'ReportSubmission', 'reason_code'),
    (m.SafetyReport, 'description', 'ReportSubmission', 'description'),
    (m.Appeal, 'description', 'AppealSubmission', 'description'),
    (m.SupportRequest, 'subject', 'SupportRequest', 'subject'),
    (m.SupportRequest, 'description', 'SupportRequest', 'description'),
    (m.MessageSubmission, 'text', 'MessageIntent', 'text'),
):
    assert model._meta.get_field(field).max_length >= text_bound(
        defs[contract]['properties'][property_name])
""")


if __name__ == "__main__":
    unittest.main()
