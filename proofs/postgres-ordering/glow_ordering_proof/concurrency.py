"""Two real connections: worker threads, each with its own Django connection, and the
hold points the forced interleavings use."""

from __future__ import annotations

import queue
import threading
from collections.abc import Callable
from concurrent.futures import Future
from typing import Any, TypeVar

from django.db import connection

from glow_ordering_proof import budget

T = TypeVar("T")


class HoldTimeout(RuntimeError):
    """The harness did not release a held writer in time; its transaction aborts."""


class Worker:
    """A thread that keeps one Django connection open across the tasks it runs."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._tasks: queue.Queue[tuple[Callable[[], Any], Future[Any]] | None] = queue.Queue()
        self._thread = threading.Thread(target=self._run, name=name, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        try:
            while True:
                item = self._tasks.get()
                if item is None:
                    return
                task, future = item
                try:
                    future.set_result(task())
                except BaseException as exc:  # noqa: BLE001 - the future carries it
                    future.set_exception(exc)
        finally:
            connection.close()

    def submit(self, task: Callable[[], T]) -> Future[T]:
        future: Future[T] = Future()
        self._tasks.put((task, future))
        return future

    def run(self, task: Callable[[], T], timeout: float = budget.HOLD_SECONDS) -> T:
        return self.submit(task).result(timeout=timeout)

    def close(self) -> None:
        self._tasks.put(None)
        self._thread.join(timeout=budget.HOLD_SECONDS)


class Hold:
    """A hold point: the writer signals that it holds its locks and waits for release."""

    def __init__(self) -> None:
        self.held = threading.Event()
        self.release = threading.Event()

    def point(self) -> None:
        self.held.set()
        if not self.release.wait(budget.HOLD_SECONDS):
            raise HoldTimeout("held writer was not released within the budget")

    def wait_held(self, timeout: float = budget.HOLD_SECONDS) -> bool:
        return self.held.wait(timeout)


class PidSlot:
    """Receives a writer's backend pid from its ``on_begin`` hook."""

    def __init__(self) -> None:
        self._ready = threading.Event()
        self.pid: int | None = None

    def set(self, pid: int) -> None:
        self.pid = pid
        self._ready.set()

    def wait(self, timeout: float = budget.HOLD_SECONDS) -> int:
        if not self._ready.wait(timeout) or self.pid is None:
            raise RuntimeError("the writer never reported its backend pid")
        return self.pid


class Barrier:
    """Starts writers together for the stress run; a thin wrapper for typing."""

    def __init__(self, parties: int) -> None:
        self._barrier = threading.Barrier(parties)

    def wait(self) -> None:
        self._barrier.wait(timeout=budget.HOLD_SECONDS)
