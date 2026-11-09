"""SV1, the identity slice: maintained sign-in bound to Glow's account and session rows.

django-allauth headless (the ``app`` client only, the JWT strategy with stateful validation and
refresh rotation) is configured by ``conf``; ``adapter``, ``strategy`` and ``sessions`` bind its
flows to ``glow_persistence``'s ``AppAccount`` and ``AccountSession`` through ``glow_chat``'s
reviewed operations (``revocation``); ``authentication`` is the one actor class every later slice
uses; ``views`` serves the member's own ``AccountAccess``; ``mail`` is the fixture mail backend;
``age`` is the age state's port adapter.

Sealed until P11 (PF01 section 8): this package runs only under
``proofs/postgres-ordering``'s identity settings, on a disposable PostgreSQL. The served runtime
(``glow_api``'s settings, URL configuration and WSGI application) imports none of it, nor
allauth, ``jwt`` or ``cryptography`` (``tests/test_identity_sealed_runtime.py``). P11 wires the
routes, the settings, the keys and the mail provider.
"""
