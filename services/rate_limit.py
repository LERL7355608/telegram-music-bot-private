from __future__ import annotations

import time
from collections import defaultdict, deque


def consume(bot_data: dict, user_id: int) -> bool:
    """Cobra una descarga al presupuesto del usuario. True si puede seguir."""
    limiter = bot_data.get("rate_limiter")
    if limiter is None:
        return True
    return limiter.allow(user_id)


def limit_message(bot_data: dict) -> str:
    limiter = bot_data.get("rate_limiter")
    cuantas = limiter.max_events if limiter is not None else 0
    return (
        f"🚫 Limite alcanzado: {cuantas} descargas por hora.\n"
        "Espera un rato y vuelve a intentar."
    )


class InMemoryRateLimiter:
    def __init__(self, max_events: int, window_seconds: int = 3600):
        self.max_events = max_events
        self.window_seconds = window_seconds
        self._events: dict[int, deque[float]] = defaultdict(deque)

    def allow(self, user_id: int) -> bool:
        now = time.time()
        events = self._events[user_id]

        while events and now - events[0] >= self.window_seconds:
            events.popleft()

        if len(events) >= self.max_events:
            return False

        events.append(now)
        return True

    def remaining(self, user_id: int) -> int:
        now = time.time()
        events = self._events[user_id]
        while events and now - events[0] >= self.window_seconds:
            events.popleft()
        return max(0, self.max_events - len(events))
