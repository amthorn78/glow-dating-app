"""The stress run's budget, fixed in code (item 6.3; the prompt, section 3 item 4).

Per race: up to MAX_ITERATIONS iterations or MAX_SECONDS of wall clock, whichever
comes first. A race that ends with fewer than MIN_ITERATIONS iterations or fewer than
MIN_OVERLAPS observed overlaps fails the job. The caps may change from measured CI
times, with the reason recorded; the floors do not.
"""

MAX_ITERATIONS = 200
MAX_SECONDS = 30.0
MIN_ITERATIONS = 50
MIN_OVERLAPS = 10
# A forced wait is awaited this long before the case fails as "wait not observed".
WAIT_OBSERVATION_SECONDS = 15.0
# A writer that holds its locks for the harness is released within this time, or its
# transaction aborts with an error instead of hanging the job.
HOLD_SECONDS = 60.0
# The default seed for the stress run; the CLI's --seed overrides it and the log
# records whichever was used.
DEFAULT_SEED = 20260929


def floors_met(iterations: int, overlaps: int) -> bool:
    return iterations >= MIN_ITERATIONS and overlaps >= MIN_OVERLAPS
