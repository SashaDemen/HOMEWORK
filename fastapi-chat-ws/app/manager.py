from typing import Dict, Set
from starlette.websockets import WebSocket
from .security import RateLimiter

class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}
        self.limiters: Dict[WebSocket, RateLimiter] = {}

    async def connect(self, user: str, ws: WebSocket):
        await ws.accept()
        self.connections.setdefault(user, set()).add(ws)
        self.limiters[ws] = RateLimiter()

    def _remove_ws(self, user: str, ws: WebSocket):
        try:
            self.connections[user].discard(ws)
            if not self.connections[user]:
                del self.connections[user]
        except KeyError:
            pass
        self.limiters.pop(ws, None)

    async def disconnect(self, user: str, ws: WebSocket):
        self._remove_ws(user, ws)
        try:
            await ws.close()
        except Exception:
            pass

    async def broadcast(self, sender: str, data: dict):
        for user, sockets in list(self.connections.items()):
            for ws in list(sockets):
                if ws.application_state.name != "CONNECTED":
                    self._remove_ws(user, ws)
                    continue
                if user == sender:
                    continue
                try:
                    await ws.send_json(data)
                except Exception:
                    self._remove_ws(user, ws)

    def active_users(self) -> int:
        return len(self.connections)

    def limiter_for(self, ws: WebSocket) -> RateLimiter:
        return self.limiters.setdefault(ws, RateLimiter())

manager = ConnectionManager()
