import html, re, time
from collections import deque
from typing import Deque
from .settings import MAX_MESSAGE_LEN, RATE_LIMIT_COUNT, RATE_LIMIT_WINDOW_SEC

CONTROL_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")

def sanitize_text(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    s = s[:MAX_MESSAGE_LEN]
    s = CONTROL_RE.sub("", s)
    s = html.escape(s, quote=True)
    return s

class RateLimiter:
    def __init__(self):
        self.events: Deque[float] = deque()

    def allow(self) -> bool:
        now = time.time()
        self.events.append(now)
        window_start = now - RATE_LIMIT_WINDOW_SEC
        while self.events and self.events[0] < window_start:
            self.events.popleft()
        return len(self.events) <= RATE_LIMIT_COUNT
