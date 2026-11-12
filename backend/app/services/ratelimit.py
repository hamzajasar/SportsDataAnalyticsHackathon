"""Tiny in-memory sliding-window limiter for endpoints that cost money per call.

Per process and per key (client address), so it resets on restart and is not shared between
workers: enough to stop one visitor running up the bill, not a replacement for a gateway.
Behind a proxy every visitor shares the proxy's address, which makes the limit global: also fine.
"""

import time
from collections import defaultdict, deque
from collections.abc import Callable


class RateLimiter:
    def __init__(self, max_calls: Callable[[], int], window_seconds: float = 3600.0):
        self._max_calls = max_calls  # read at call time, so settings changes apply
        self._window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        hits = self._hits[key]
        while hits and now - hits[0] >= self._window:
            hits.popleft()
        if len(hits) >= self._max_calls():
            return False
        hits.append(now)
        return True

    def retry_after(self, key: str, now: float | None = None) -> int:
        now = time.monotonic() if now is None else now
        hits = self._hits[key]
        return max(1, int(self._window - (now - hits[0]))) if hits else 1
