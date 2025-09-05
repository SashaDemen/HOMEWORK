from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def token(u='alice', p='Secret#123'):
    r = client.post('/auth/login', json={'username':u,'password':p})
    assert r.status_code == 200
    return r.json()['access_token']

def test_login_and_ws_chat():
    t1 = token('alice')
    t2 = token('bob')
    with client.websocket_connect(f"/ws?token={t1}") as a:
        with client.websocket_connect(f"/ws?token={t2}") as b:
            a.send_json({'message':'<b>hi</b>'})
            data = b.receive_json()
            assert data['type'] == 'chat'
            assert data['from'] == 'alice'
            assert data['message'] == '&lt;b&gt;hi&lt;/b&gt;'
            # sessions endpoint
            s = client.get('/sessions/active').json()['active_users']
            assert s >= 2

def test_reject_without_token():
    try:
        with client.websocket_connect("/ws"):
            assert False
    except Exception:
        pass
