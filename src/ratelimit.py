"""レート制限。一定時間内の回数を数えるだけ（Discord に依存しない）。"""
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_events, window_seconds, clock=time.monotonic):
        self._max = max_events
        self._window = window_seconds
        self._clock = clock
        self._events = {}  # key -> deque[発生時刻]

    def allow(self, key):
        """回数内なら記録して True。超えていれば記録せず False。"""
        now = self._clock()
        q = self._events.setdefault(key, deque())
        while q and q[0] <= now - self._window:
            q.popleft()
        if len(q) >= self._max:
            return False
        q.append(now)
        return True
