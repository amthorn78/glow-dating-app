"""SV3 Stage A, eligibility and discovery: who may see whom, on SV1's actor and SV2's profile (the
SV3 brief, revision 2, D1 to D8, D13 for Stage A's parts, D15 to D19; DM-60).

- ``policy``: what the selection reads (the settings, under their pointers' locks in name order,
  D19), the batch's policy version (Q3), the accepted age states (D3), and the bounds (D7);
- ``keys``: the cursor's binding to the viewer (D7); the tie-break has no key (D6; DM-61 K2);
- ``predicates``: the eligibility predicates of D3 to D5 and D7's consumption, as SQL, each for the
  viewer and for the candidate, the one source of every statement below;
- ``eligibility``: the trusted adapter behind ``glow_domain.trusted_eligibility``'s
  ``TrustedEligibilityService`` (D2): both members' authoritative rows, in one statement;
- ``pages``: recommendations first, then broader (D6), bounded batches and cursors (D7), with the
  compatibility port's fixture adapter only where the proof's settings select it;
- ``contract``, ``views`` and ``urls``: the page route, through SV1's actor, answering the card's
  additive DTOs (D13).

Sealed until P11 (PF01 section 8; D15): this package runs only under ``proofs/postgres-ordering``'s
discovery settings, on a disposable PostgreSQL. The served runtime (``glow_api``'s settings, URL
configuration and WSGI application) imports none of it and selects no compatibility provider
(``tests/test_discovery_sealed_runtime.py``). There is no provider, deployed URL, real member, HDE
call or stored credential. Stage B adds like, pass, the match, unmatch and block.
"""
