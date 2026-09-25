"""The ignored local work directory and leak-checked writes."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .redaction import find_leaks

PROOF_ROOT = Path(__file__).resolve().parent.parent
WORK_DIR = PROOF_ROOT / ".work"


class LeakRefused(RuntimeError):
    """Refused to write or print text that contains a secret or a token."""


def checked_text(text: str, secrets: Iterable[str]) -> str:
    reasons = find_leaks(text, secrets)
    if reasons:
        raise LeakRefused("refused output: " + "; ".join(reasons))
    return text


def write_json(name: str, data: Any, secrets: Iterable[str]) -> Path:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    text = checked_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n", secrets)
    path = WORK_DIR / name
    path.write_text(text, encoding="utf-8")
    return path


def write_text(name: str, text: str, secrets: Iterable[str]) -> Path:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    path = WORK_DIR / name
    path.write_text(checked_text(text, secrets), encoding="utf-8")
    return path
