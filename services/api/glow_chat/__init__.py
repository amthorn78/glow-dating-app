"""P06.2 chat integration: the persistence adapter behind ``glow_domain.chat``'s port,
and the outbox delivery to a chat provider (Stage A: the fixture provider only).

This package needs a database. It is imported only by the disposable-database proof
(``proofs/postgres-ordering``) under that proof's settings; the API's runtime settings,
URL configuration and dummy backend never import it (D2; the API's sealed-runtime
test). P11 wires it into the runtime.
"""
