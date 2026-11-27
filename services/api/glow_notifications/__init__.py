"""SV4 B1, F12's surface: devices and notification settings, stored and served, on SV1's actor (the
SV4 brief, revision 12, D16 to D20, with DM-101's AM1 to AM7).

- ``persistence``: the ORM adapter behind ``glow_domain.notifications.NotificationPersistence``
  (D18), whose in-memory fixture is the domain's ``NotificationService``: one row per account and
  installation, the locks, the keyed idempotency and the token's custody;
- ``providers``: the token store's and the push transport's factory hooks (D16; AM1), which only
  the disposable-database proof's chat settings name, with the in-memory fixtures;
- ``contract``, ``views`` and ``urls``: F12's three routes (D19), with the installation from the
  ``Glow-Installation-Id`` header and every refusal the contract's ``Error``.

Sealed until integration (PF01 1.20, stage 2): this package runs only under
``proofs/postgres-ordering``'s chat settings, on a disposable PostgreSQL. The served runtime
(``glow_api``'s settings, URL configuration and WSGI application) imports none of it and names no
factory (``tests/test_notifications_sealed_runtime.py``). There is no provider, deployed URL, real
member, real token, HDE call or stored credential. SV4 B2 adds the triggers, the deliverer and the
sweeps.
"""
