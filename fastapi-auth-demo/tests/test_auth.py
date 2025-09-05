from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_basic_ok_and_fail():
    # ok
    r = client.get("/basic/secret", auth=("alice", "Secret#123"))
    assert r.status_code == 200
    assert r.json()["ok"] is True

    # fail
    r2 = client.get("/basic/secret", auth=("alice", "NOPE"))
    assert r2.status_code == 401

def test_oauth2_token_and_access():
    # get token
    r = client.post("/token", data={"username":"alice","password":"Secret#123"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    # use token
    headers = {"Authorization": f"Bearer {token}"}
    me = client.get("/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["user"] == "alice"
    data = client.get("/data", headers=headers)
    assert data.status_code == 200
    assert "numbers" in data.json()

def test_oauth2_bad_token():
    headers = {"Authorization": "Bearer BADTOKEN"}
    r = client.get("/me", headers=headers)
    assert r.status_code == 401
