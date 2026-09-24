# 🗂️ AB1-DBA-001 — Live Catalog Inventory and Query Record

Dated audit evidence migrated from [Notion](https://app.notion.com/p/3e44590a05eb8182afdaedeebc6796c6?pvs=204) on 2026-09-24. The observations below are from 2026-09-23, not a fresh database inspection. No connection, DDL or role change was performed for the migration. Physical integration remains P11. Future changes must reverify ownership and protect HDE.

## Machine-readable live inventory
Captured from the live `railway` database on 23 September 2026 inside an explicit read-only transaction.
```javascript
schema,relation,kind,owner,parent,total_bytes,disposition
hde,body_graphs,table,postgres,,81920,preserve
hde,body_graphs_current,view,postgres,,,preserve
hde,chart_snapshot,table,postgres,,24576,preserve
hde,meta,table,postgres,,32768,preserve
hde,pair_evaluation,partitioned_table,postgres,,,preserve
hde,pair_evaluation_pcur,partition,postgres,hde.pair_evaluation,49152,preserve
hde,public_results,partitioned_table,postgres,,,preserve
hde,public_results_pcur,partition,postgres,hde.public_results,81920,preserve
hde,schema_migrations,table,postgres,,32768,preserve
hde,test_bridge,table,postgres,,0,preserve_pending_proof
public,admin_action_log,table,postgres,,,retire_candidate
public,admin_action_log_id_seq,sequence,postgres,public.admin_action_log.id,,retire_with_owner
public,birth_data,table,postgres,,,retire_candidate
public,compatibility_matrix,table,postgres,,,retire_candidate
public,email_notifications,table,postgres,,,retire_candidate
public,email_notifications_id_seq,sequence,postgres,public.email_notifications.id,,retire_with_owner
public,hde_body_graphs_current,view,postgres,,,preserve_hde_dependency
public,human_design_data,table,postgres,,,retire_candidate
public,user_preferences,table,postgres,,,retire_candidate
public,user_priorities,table,postgres,,,retire_candidate
public,user_profiles,table,postgres,,,retire_candidate
public,user_profiles_id_seq,sequence,postgres,public.user_profiles.id,,retire_with_owner
public,user_resonance_prefs,table,postgres,,,retire_candidate
public,user_resonance_signals_private,table,postgres,,,retire_candidate
public,user_sessions,table,postgres,,,retire_candidate
public,user_sessions_id_seq,sequence,postgres,public.user_sessions.id,,retire_with_owner
public,users,table,postgres,,,retire_candidate
public,users_id_seq,sequence,postgres,public.users.id,,retire_with_owner
```
## Column inventory by relation
```plain text
hde.body_graphs:
  user_id uuid; vendor text; vendor_version int4; input_fingerprint char(64);
  payload jsonb; created_at timestamptz; refreshed_at timestamptz; ttl_at timestamptz

hde.body_graphs_current:
  user_id uuid; vendor text; vendor_version int4; input_fingerprint char(64);
  payload jsonb; created_at timestamptz; refreshed_at timestamptz; ttl_at timestamptz

hde.chart_snapshot:
  id uuid; user_id text; release_id text; chart_json jsonb; provider text;
  fingerprint text; computed_at timestamptz

hde.meta:
  id; engine_tag; build_commit; invocation_tag; emitter_sha256; created_at

hde.pair_evaluation and hde.pair_evaluation_pcur:
  id uuid; min_user text; max_user text; release_id text; bands_json jsonb;
  internal_json jsonb nullable; idempotence_hash text; evaluated_at timestamptz

hde.public_results and hde.public_results_pcur:
  id uuid; release_id text; payload jsonb; created_at timestamptz

hde.schema_migrations:
  migration; applied_at

hde.test_bridge:
  id int nullable

public.users:
  id int; email; password_hash; status; created_at; updated_at; is_admin; profile_version

public.user_profiles:
  id int; user_id int; first_name; last_name; display_name; avatar_url; bio; age;
  profile_completion; created_at; updated_at

public.user_sessions:
  id int; user_id int; session_token; created_at; expires_at; updated_at

public.birth_data:
  user_id int; birth date/time and location inputs; latitude; longitude; consent;
  location/timezone metadata; created_at; updated_at

public.human_design_data:
  user_id int; chart_data text; energy_type; strategy; authority; profile;
  api_response text; calculated_at

public.compatibility_matrix:
  user pair identifiers; overall and dimension scores; timestamps

public.user_priorities:
  user_id; score-priority fields; timestamps

public.user_preferences:
  user_id; preferences JSON; timestamps

public.user_resonance_prefs:
  user_id; version; weights/facets; timestamps

public.user_resonance_signals_private:
  user_id; private resonance-signal fields; timestamps

public.admin_action_log:
  administrative action/audit fields and timestamps

public.email_notifications:
  user/email notification fields and timestamps
```
The compact legacy column descriptions above intentionally avoid payload values. The reproducible catalog query below is the authoritative exact-column extraction and includes ordinal position, nullability, type, and default for every column.
## Constraints, indexes, views, roles, grants
```yaml
constraints:
  check: 13
  foreign_key: 13
  primary_key: 19
  unique: 5
foreign_keys:
  count: 13
  scope: public legacy tables -> public.users
  update_action: NO ACTION
  delete_action: NO ACTION
  validated: true
cross_schema_foreign_keys: 0
indexes:
  count: 43
  all_valid: true
views:
  - hde.body_graphs_current -> hde.body_graphs
  - public.hde_body_graphs_current -> hde.body_graphs_current
row_level_security_policies: 0
user_functions_in_hde_or_public: 0
non_internal_triggers: 0
extensions:
  - plpgsql
roles:
  - {name: postgres, login: true, superuser: true}
  - {name: hde_owner, login: false}
  - {name: hde_rw, login: false}
  - {name: hde_reader, login: false}
  - {name: hde_ops03_reader, login: false, member_of: hde_reader}
migration_ledgers:
  - {relation: hde.schema_migrations, rows: 1, latest: 011_body_graphs_durability.sql, applied_at: "2025-11-15 03:52:00.668498+00"}
```
## Reproducible read-only query record
Run only through the supported Railway connection and leave the transaction read-only:
```sql
BEGIN READ ONLY;
SET LOCAL statement_timeout = '5s';
SET LOCAL lock_timeout = '1s';

SELECT clock_timestamp(), current_database(), current_user, session_user,
       current_setting('search_path'),
       current_setting('transaction_read_only'),
       version();

SELECT n.nspname AS schema_name, c.relname, c.relkind,
       pg_get_userbyid(c.relowner) AS owner,
       pg_total_relation_size(c.oid) AS total_bytes,
       pg_get_expr(c.relpartbound, c.oid) AS partition_bound
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname IN ('hde','public')
  AND c.relkind IN ('r','p','v','m','S')
ORDER BY 1,2;

SELECT table_schema, table_name, ordinal_position, column_name,
       is_nullable, data_type, udt_name, column_default
FROM information_schema.columns
WHERE table_schema IN ('hde','public')
ORDER BY table_schema, table_name, ordinal_position;

SELECT n.nspname, c.relname, con.conname, con.contype,
       con.convalidated, pg_get_constraintdef(con.oid, true)
FROM pg_constraint con
JOIN pg_class c ON c.oid = con.conrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname IN ('hde','public')
ORDER BY 1,2,3;

SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname IN ('hde','public')
ORDER BY 1,2,3;

SELECT view_schema, view_name, table_schema, table_name
FROM information_schema.view_table_usage
WHERE view_schema IN ('hde','public')
ORDER BY 1,2,3,4;

SELECT grantee, table_schema, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema IN ('hde','public')
ORDER BY 1,2,3,4;

SELECT * FROM hde.schema_migrations ORDER BY applied_at;
ROLLBACK;
```
## Reproducible terminal record
```bash
source .venv/bin/activate
railway --version
psql --version
railway whoami
railway status
railway service status --all
railway connect Postgres
```
Sanitized service-binding probes were run with `railway run` for the HDE and legacy services and printed only host, port, database, role, and presence/absence of retired bridge keys. No secret values were printed or saved.
## Exact 32-model mapping
Source verified through the authorized GitHub connector at `bd701ebfede1630ba162862e053a0a55daea9c9b`. The model state and both unapplied migrations agree on 32 concrete models. No custom `db_table` is declared; the table names below are Django defaults. Schema `app` is the audit recommendation, not applied DDL.
```javascript
model,target_schema,target_table,disposition,live_relation_reuse
OutboxEvent,app,glow_persistence_outboxevent,new_app_owned,"none"
WebhookInbox,app,glow_persistence_webhookinbox,new_app_owned,"none"
AppAccount,app,glow_persistence_appaccount,new_app_owned,"public.users rejected"
PolicyRevision,app,glow_persistence_policyrevision,new_app_owned,"none"
AccountSession,app,glow_persistence_accountsession,new_app_owned,"public.user_sessions rejected"
ConsentDecision,app,glow_persistence_consentdecision,new_app_owned,"legacy consent fields insufficient"
Profile,app,glow_persistence_profile,new_app_owned,"public.user_profiles rejected"
Preferences,app,glow_persistence_preferences,new_app_owned,"public.user_preferences/user_priorities/user_resonance_prefs rejected"
BirthInput,app,glow_persistence_birthinput,new_app_owned,"public.birth_data rejected"
EngineIdentity,app,glow_persistence_engineidentity,new_app_owned,"public.human_design_data rejected; opaque HDE reference only"
MediaAsset,app,glow_persistence_mediaasset,new_app_owned,"none"
DirectionalInteraction,app,glow_persistence_directionalinteraction,new_app_owned,"none"
Block,app,glow_persistence_block,new_app_owned,"none"
Match,app,glow_persistence_match,new_app_owned,"none"
CompatibilitySnapshot,app,glow_persistence_compatibilitysnapshot,new_app_owned,"public.compatibility_matrix rejected; HDE result contract only"
RecommendationBatch,app,glow_persistence_recommendationbatch,new_app_owned,"none"
RecommendationEntry,app,glow_persistence_recommendationentry,new_app_owned,"none"
ChatBinding,app,glow_persistence_chatbinding,new_app_owned,"none"
MessageSubmission,app,glow_persistence_messagesubmission,new_app_owned,"none"
DeviceRegistration,app,glow_persistence_deviceregistration,new_app_owned,"none"
NotificationSettings,app,glow_persistence_notificationsettings,new_app_owned,"public.email_notifications is different semantics"
SafetyReport,app,glow_persistence_safetyreport,new_app_owned,"none"
ModerationCase,app,glow_persistence_moderationcase,new_app_owned,"none"
Appeal,app,glow_persistence_appeal,new_app_owned,"none"
StaffAudit,app,glow_persistence_staffaudit,new_app_owned,"public.admin_action_log rejected"
SupportRequest,app,glow_persistence_supportrequest,new_app_owned,"none"
ExportJob,app,glow_persistence_exportjob,new_app_owned,"none"
DeletionJob,app,glow_persistence_deletionjob,new_app_owned,"none"
ProviderLifecycleStep,app,glow_persistence_providerlifecyclestep,new_app_owned,"none"
DeletionTombstone,app,glow_persistence_deletiontombstone,new_app_owned,"none"
IdempotencyRecord,app,glow_persistence_idempotencyrecord,new_app_owned,"none"
Entitlement,app,glow_persistence_entitlement,new_app_owned,"none"
```
All 32 map to new app-owned relations if retained. `EngineIdentity` and `CompatibilitySnapshot` integrate with HDE by opaque identifier/provenance and supported contract, not by table ownership or FK. Maintained Django/allauth relations are additional P11 dependencies and are not part of the 32-model count.
## Coverage boundary
This appendix records catalog metadata and code-defined dependencies, not payload data. No legacy/application row values were read. The private app repository was read only through the GitHub connector; no repository content, branch, commit, issue, or PR was changed.
