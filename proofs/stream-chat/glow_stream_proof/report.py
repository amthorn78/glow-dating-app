"""Markdown tables for a run's results (redacted, with run identifiers generalized)."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


def _cell(value: Any) -> str:
    text = str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")
    return text.strip() or "-"


def table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_cell(v) for v in row) + " |")
    return "\n".join(lines)


def checks_table(checks: Sequence[Mapping[str, Any]]) -> str:
    return table(
        ("Check", "Description", "Result", "Evidence"),
        [(c["check_id"], c["description"], c["result"], c["evidence"]) for c in checks],
    )


def cases_table(cases: Sequence[Mapping[str, Any]]) -> str:
    return table(
        (
            "Case",
            "Actor",
            "Token",
            "Action",
            "Expected",
            "Request",
            "Observed",
            "Control",
            "Verdict",
        ),
        [
            (
                c["case_id"],
                c["actor"],
                c["token"],
                c["action"],
                c["expected"],
                c["request"],
                c["observed"],
                c["control"],
                f"{c['verdict']}: {c['reason']}",
            )
            for c in cases
        ],
    )


def verdict_counts(cases: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(str(c["verdict"]) for c in cases).items()))


def render(results: Mapping[str, Any]) -> str:
    parts = [
        f"Run `{results['prefix']}`",
        "",
        "Authorized path",
        "",
        checks_table(results["checks"]),
        "",
        "Bypass matrix",
        "",
        cases_table(results["cases"]),
        "",
        f"Verdicts: {verdict_counts(results['cases'])}",
    ]
    if results.get("notes"):
        parts += ["", "Notes:"] + [f"- {n}" for n in results["notes"]]
    return "\n".join(parts) + "\n"
