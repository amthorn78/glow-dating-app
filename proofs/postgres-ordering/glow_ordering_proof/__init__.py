"""P06.DB: the disposable-PostgreSQL proof of send-versus-revocation ordering.

Proof tooling, not application code. It imports ``glow_persistence`` from
``services/api`` unchanged and runs it against a database that exists only for the
proof (a CI job's container, or a session's throwaway cluster). The API's settings,
guards and dummy backend are never imported here.
"""
