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
from pathlib import Path
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
assert len([key for key in state.models if key[0] == 'glow_persistence']) == 34
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

    def test_receipt_is_minimal_complete_and_target_is_not_a_dedup_scope(self):
        self.check_script("""
fields = {field.name: field for field in m.IdempotencyRecord._meta.fields}
assert not any(isinstance(field, models.JSONField) for field in fields.values())
assert isinstance(fields['result_ref'], models.UUIDField)
assert isinstance(fields['result_version'], models.PositiveBigIntegerField)
codes = {value for value, _ in fields['outcome_code'].choices}
assert {'liked', 'passed', 'unmatched', 'blocked', 'unblocked'} <= codes
dedup = next(c for c in m.IdempotencyRecord._meta.constraints if c.name == 'intent_dedup')
assert dedup.fields == ('actor_id', 'operation', 'key')
receipt = next(c for c in m.IdempotencyRecord._meta.constraints if c.name == 'intent_result')
assert receipt.condition.connector == 'OR'
completed, pending = (dict(branch.children) for branch in receipt.condition.children)
assert completed['state'] == 'completed' and pending['state'] == 'pending'
for field in ('result_ref', 'result_version', 'outcome_code'):
    assert completed[field + '__isnull'] is False
    assert pending[field + '__isnull'] is True
assert completed['result_version__gte'] == 1
assert completed['result_version__lte'] == 9007199254740991
assert set(completed['outcome_code__in']) == codes
""")

    def test_migration_0003_is_additive_and_0001_0002_are_unchanged(self):
        # P06.2 D7 (DM-13 item 6): 0003 adds the two new models and, since Stage B1 (DM-15
        # 4.1 to 4.3), the outbox's order column and the binding's reconciliation mark as
        # AddField operations; the reviewed migrations stay byte-identical to P02's.
        import hashlib

        migrations = API_ROOT / "glow_persistence" / "migrations"
        pinned = {
            "0001_event_infrastructure.py": (
                "817c1c763b53f9af8e5291c7c511d73e9684b9665b9efac4dde7ce3c1a434d58"
            ),
            "0002_app_domain.py": (
                "862bac8b81aa76f74fd88743a36ab5a4b2e9261651251b94398c274350a31335"
            ),
        }
        for name, digest in pinned.items():
            with self.subTest(migration=name):
                content = (migrations / name).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), digest)
        self.check_script("""
from django.db.migrations.operations.models import CreateModel
from glow_persistence.fields import SequenceField
loader = MigrationLoader(None)
added = loader.disk_migrations[('glow_persistence', '0003_chat_identity_read_cursor')]
assert added.dependencies == [('glow_persistence', '0002_app_domain')]
# The exact operation list (DM-15 4.3), as the pinned autodetector wrote it.
assert [(type(op).__name__, getattr(op, 'name', None), getattr(op, 'model_name', None))
    for op in added.operations] == [
    ('AddField', 'reconcile_code', 'chatbinding'),
    ('AddField', 'sequence', 'outboxevent'),
    ('CreateModel', 'ChatIdentity', None),
    ('CreateModel', 'ChatReadCursor', None),
], [type(op).__name__ for op in added.operations]
assert isinstance(added.operations[1].field, SequenceField)
assert added.operations[1].preserve_default is True
assert added.operations[0].field.max_length == 32 and added.operations[0].field.null
identity_op = added.operations[2]
assert dict(identity_op.fields)['state'].default == 'pending'
assert sorted(dict(identity_op.fields)) == sorted(['id', 'created_at', 'updated_at', 'version',
    'provider', 'user_ref', 'state', 'tokens_revoked_before', 'reconcile_code', 'account'])
leaves = loader.graph.leaf_nodes('glow_persistence')
assert leaves == [('glow_persistence', '0003_chat_identity_read_cursor')], leaves
source = (Path.cwd() / 'glow_persistence' / 'migrations' /
    '0003_chat_identity_read_cursor.py').read_text()
assert 'RunSQL' not in source and 'RunPython' not in source
identity = m.ChatIdentity._meta
names = {c.name for c in identity.constraints}
assert {'chat_identity_account', 'chat_identity_ref'} <= names
assert identity.get_field('account').remote_field.on_delete is models.PROTECT
assert identity.get_field('user_ref').max_length == 64
assert {f.name for f in identity.get_fields()} >= {'account', 'provider', 'user_ref', 'state',
    'tokens_revoked_before', 'reconcile_code'}
assert [v for v, _ in identity.get_field('state').choices] == ['pending', 'active', 'deactivated']
assert identity.get_field('state').default == 'pending'
mark = identity.get_field('reconcile_code')
assert mark.null and mark.blank and mark.max_length == 32
assert not {f.name for f in identity.get_fields()} & {'name', 'image', 'email', 'display_name'}
binding = m.ChatBinding._meta
mark = binding.get_field('reconcile_code')
assert mark.null and mark.blank and mark.max_length == 32
cursor = m.ChatReadCursor._meta
assert 'chat_read_cursor_member' in {c.name for c in cursor.constraints}
assert cursor.get_field('last_read').remote_field.model is m.MessageSubmission
""")

    def test_the_outbox_order_column_is_a_database_assigned_identity_beside_the_key(self):
        # P06.2 B1 (DM-15 3.1): the delivery order key is assigned by the database in
        # insertion order; the UUID stays the primary key, and the app never writes it.
        self.check_script("""
from glow_persistence.fields import DatabaseAssigned, SequenceField
meta = m.OutboxEvent._meta
field = meta.get_field('sequence')
assert isinstance(field, SequenceField) and isinstance(field, models.BigAutoField)
assert not field.primary_key and meta.pk.name == 'id' and isinstance(meta.pk, models.UUIDField)
assert meta.auto_field is None, meta.auto_field
assert field.db_returning is True
assert field.get_internal_type() == 'BigAutoField'
assert field.check(databases=[]) == [], field.check(databases=[])
assert field.deconstruct()[1:] == ('glow_persistence.fields.SequenceField', [], {})
event = m.OutboxEvent()
assert event.sequence is None
assigned = field.pre_save(event, add=True)
assert isinstance(assigned, DatabaseAssigned)
assert assigned.as_sql(None, None) == ('DEFAULT', [])
event.sequence = 7
assert field.pre_save(event, add=True) == 7 and field.pre_save(event, add=False) == 7
unset = m.OutboxEvent()
assert field.pre_save(unset, add=False) is None  # an update never asks for a new value
assert field in meta.db_returning_fields
""")

    def test_makemigrations_check_passes_without_a_database(self):
        # P06.2 D7: makemigrations --check --dry-run under the static registry, with the
        # same guard that rejects every connection, cursor and schema editor.
        self.check_script("""
from django.core.management import call_command
call_command('makemigrations', '--check', '--dry-run', verbosity=1)
assert connections['default'].connection is None
""")

    def test_the_chat_adapter_loads_without_a_connection_and_has_no_switch(self):
        # P06.2 D2 and DM-13 2.1: the adapter imports the models; its only constructor
        # input is the provider's name, and nothing in it is a test-only switch.
        self.check_script("""
import inspect
from glow_chat import contact, delivery, events
parameters = list(inspect.signature(contact.OrmContactPersistence.__init__).parameters)
assert parameters == ['self', 'provider'], parameters
adapter = contact.OrmContactPersistence(provider='fixture')
assert vars(adapter) == {'provider': 'fixture'}, vars(adapter)
source = inspect.getsource(contact)
for word in ('Design(', 'design.', 'lock_accounts', 'check_contact_version', 'filter_state'):
    assert word not in source, word
ref = contact.new_provider_ref()
assert len(ref) == 32 and int(ref, 16) >= 0 and ref != contact.new_provider_ref()
assert set(events.DELIVERED.values()) == {'provision_user', 'create_channel', 'send_message',
    'remove_members', 'deactivate_user', 'revoke_user_tokens'}
assert list(events.DELIVERED)[0] == 'identity_created'
assert events.CHAT_SCHEMA_VERSION == 'glow-chat-1'
assert delivery.MAX_ATTEMPTS == 5
assert connections['default'].connection is None
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
