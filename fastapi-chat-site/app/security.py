import html, re, time
from collections import deque
from typing import Deque
from .settings import MAX_MESSAGE_LEN, RATE_LIMIT_COUNT, RATE_LIMIT_WINDOW_SEC

CTRL = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")

def sanitize_text(s: str) -> str:
    s = s if isinstance(s, str) else str(s)
    s = s[:MAX_MESSAGE_LEN]
    s = CTRL.sub("", s)
    return html.escape(s, quote=True)

class RateLimiter:
    def __init__(self):
        self.events: Deque[float] = deque()

    def allow(self) -> bool:
        now = time.time()
        self.events.append(now)
        start = now - RATE_LIMIT_WINDOW_SEC
        while self.events and self.events[0] < start:
            self.events.popleft()
        return len(self.events) <= RATE_LIMIT_COUNT
