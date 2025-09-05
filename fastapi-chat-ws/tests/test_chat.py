import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_token(u="alice", p="Secret#123"):
    r = client.post("/auth/login", json={"username":u,"password":p})
    assert r.status_code == 200
    return r.json()["access_token"]

def test_login_ok():
    t = get_token()
    assert t

def test_ws_requires_auth():
    try:
        with client.websocket_connect("/ws"):
            assert False, "should not connect without token"
    except Exception as e:
        # Expected close
        pass

def test_chat_send_receive():
    t1 = get_token("alice","Secret#123")
    t2 = get_token("bob","Secret#123")
    with client.websocket_connect(f"/ws?token={t1}") as ws1:
        with client.websocket_connect(f"/ws?token={t2}") as ws2:
            # alice sends, bob receives
            ws1.send_json({"message":"<b>Hello</b>"})
            data = ws2.receive_json()
            assert data["type"] == "chat"
            assert data["from"] == "alice"
            assert data["message"] == "&lt;b&gt;Hello&lt;/b&gt;"  # sanitized

def test_sessions_active_increment():
    before = client.get("/sessions/active").json()["active_users"]
    t = get_token("alice","Secret#123")
    with client.websocket_connect(f"/ws?token={t}") as ws:
        during = client.get("/sessions/active").json()["active_users"]
        assert during == before + 1
    after = client.get("/sessions/active").json()["active_users"]
    assert after == before
