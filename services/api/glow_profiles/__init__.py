"""SV2 Stage A, the profiles slice: the server's profile on SV1's actor (the SV2 brief, D1 to D9,
D11 to D18).

- ``settings_store``: the versioned, audited settings store (D2), with ``glow_domain``'s closed
  schemas and fixed limits;
- ``operations``: the member's domain operations (D3 to D9), each one transaction that takes the
  account row lock first and nests ``glow_chat``'s reviewed writers where they apply;
- ``staff``: the staff operations (D2's publication, D9's restriction, D18's approval without
  identity verification and its revocation), each with a staff subject and a reason, written to
  ``StaffAudit``; no member route reaches them, and P07's console calls them later;
- ``requirements``: completion's requirements (D9) and the owner's completion read;
- ``identity_verification``: D18's port adapter; ``areas``: the area table and the nearest-area
  query (D5); ``contract``: the closed request checks and the response projections (D11, D17);
- ``views`` and ``urls``: the member's routes, through SV1's actor (``GlowActorAuthentication``).

Sealed until P11 (PF01 section 8): this package runs only under ``proofs/postgres-ordering``'s
profile settings, on a disposable PostgreSQL. The served runtime (``glow_api``'s settings, URL
configuration and WSGI application) imports none of it (``tests/test_profiles_sealed_runtime.py``).
There is no provider, no deployed URL, no real member, no HDE call and no stored credential.
"""
